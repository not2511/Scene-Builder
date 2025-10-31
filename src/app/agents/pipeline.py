"""
pipeline.py

Gemini-backed cinematic scene builder pipeline and stable fallback.
Generates realistic video skits (titles, script lines, effects, transitions).
Cleans Markdown code fences (```json ... ```) from Gemini output before parsing.
"""

import os
import json
import uuid
from typing import Any, Dict, List, Optional
from src.app.core.schema import SceneSchema, SceneInputConstraints


def _get_gemini():
    try:
        import google.generativeai as genai  # type: ignore
        return genai
    except Exception:
        return None


def _clean_gemini_json(text: str) -> str:
    """Remove Markdown code fences or extraneous text from Gemini output."""
    if not text:
        return text
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.replace("```", "")
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return text.strip()


def _normalize_to_scene_schema(raw_scene: Dict[str, Any], *_, **__) -> SceneSchema:
    """
    Normalize raw LLM JSON output into SceneSchema-compatible format.
    Fixes missing fields, wraps dicts in lists, and ensures consistent structure.
    """

    plan = raw_scene.get("plan", {})
    scenes = []
    for idx, sc in enumerate(raw_scene.get("scenes", []), 1):
        rows = []
        assets = sc.get("assets", [])

        # Scene-level normalization
        scene_effects = sc.get("effects", [])
        if isinstance(scene_effects, dict):
            scene_effects = [scene_effects]

        scene_transitions = sc.get("transitions", [])
        if isinstance(scene_transitions, dict):
            scene_transitions = [scene_transitions]

        # Normalize transitions to include 'name'
        for t in scene_transitions:
            if "name" not in t or not t["name"]:
                t["name"] = t.get("type", "unknown")

        duration = sc.get("durationSec", 3)

        # Build a single row for simplicity (can expand later)
        row_actions = []
        for aidx, asset in enumerate(assets, 1):
            effects = asset.get("effects", [])
            if isinstance(effects, dict):
                effects = [effects]
            elif effects is None:
                effects = []

            asset_type = asset.get("type", "video").lower()
            if asset_type == "music":
                asset_type = "audio"

            action = {
                "id": asset.get("id", f"action-{idx}-{aidx}"),
                "type": asset_type,
                "startSec": float(asset.get("startSec", 0)),
                "durationSec": float(asset.get("durationSec", duration)),
                "props": asset.get("props", {**asset, "src": asset.get("src", "")}),
                "effects": effects
            }
            row_actions.append(action)

        # Normalize row-level transitions too
        for t in scene_transitions:
            if "name" not in t or not t["name"]:
                t["name"] = t.get("type", "unknown")

        row = {
            "id": f"row-{idx}-1",
            "kind": "video",
            "actions": row_actions,
            "transitions": scene_transitions
        }
        rows.append(row)

        scene_obj = {
            "id": sc.get("id", f"scene_{idx}"),
            "title": sc.get("title", f"Scene {idx}"),
            "description": sc.get("description", ""),
            "rows": rows,
            "durationSec": duration
        }
        scenes.append(scene_obj)

    meta = raw_scene.get("meta", {})
    return SceneSchema(
        plan={
            "scenesCount": len(scenes),
            "notes": plan.get("summary", plan.get("notes", "")),
            "prompt": plan.get("prompt", ""),
        },
        scenes=scenes,
        meta=meta
    )

def _make_plan(prompt: str, normalized_scene: Dict[str, Any]) -> Dict[str, Any]:
    scenes_count = len(normalized_scene.get("scenes", []))
    notes = f"Generated {scenes_count} scene(s) from prompt"
    return {"scenesCount": scenes_count, "notes": notes, "prompt": prompt}


def run_pipeline(prompt: str, constraints: Optional[SceneInputConstraints] = None) -> Dict[str, Any]:
    """Main entry for cinematic scene generation."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    raw_output = None

    if gemini_key:
        genai = _get_gemini()
        if genai:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                system_prompt = (
    "You are a Cinematic Scene Builder AI Assistant.\n"
    "Your task is to create a realistic cinematic storyboard in structured JSON format based on the user's idea or theme.\n\n"

    "The goal is to simulate a short video or film concept, written like a visual script with camera directions, scene titles, dialogues, and transitions.\n"
    "The result must be emotionally coherent, cinematic, and ready for production planning.\n\n"

    "Output only valid JSON — no markdown, no commentary, no text outside JSON.\n\n"

    "Your JSON structure must look exactly like this:\n"
    "{\n"
    "  'processId': 'unique_identifier_for_video',\n"
    "  'plan': {\n"
    "    'title': 'Short descriptive title of the full video',\n"
    "    'summary': '2-3 line story summary of the full video',\n"
    "    'themes': ['teamwork', 'resilience', 'hope']\n"
    "  },\n"
    "  'scenes': [\n"
    "    {\n"
    "      'id': 'scene_01',\n"
    "      'title': 'Short scene title',\n"
    "      'description': 'One-line cinematic summary of what happens',\n"
    "      'script': [\n"
    "         'Camera pans across a dark office. The hum of computers fills the air.',\n"
    "         'SARAH: We’re not done yet. Not tonight.',\n"
    "         'Mark looks up, determination in his eyes.'\n"
    "      ],\n"
    "      'assets': [\n"
    "         {'type': 'video', 'src': 'office_nightwide.mp4', 'description': 'Wide shot of office at night'},\n"
    "         {'type': 'audio', 'src': 'ambient_keyboard_typing.mp3', 'description': 'Subtle background typing and clicking'},\n"
    "         {'type': 'text', 'src': '02:47 AM', 'description': 'Overlay timestamp in bottom-right corner'}\n"
    "      ],\n"
    "      'effects': [\n"
    "         {'type': 'camera', 'name': 'slow_zoom_in'},\n"
    "         {'type': 'color', 'name': 'blue_tint', 'intensity': 0.3}\n"
    "      ],\n"
    "      'transitions': [\n"
    "         {'type': 'fade', 'direction': 'out', 'durationSec': 1.2}\n"
    "      ],\n"
    "      'durationSec': 4.0\n"
    "    }\n"
    "  ],\n"
    "  'meta': {\n"
    "    'totalDurationSec': <total_duration>,\n"
    "    'aspectRatio': '<aspect_ratio>',\n"
    "    'fps': <fps>,\n"
    "    'language': '<language>',\n"
    "    'deterministic': <deterministic_flag>,\n"
    "    'tone': 'cinematic / motivational / dramatic'\n"
    "  }\n"
    "}\n\n"

    "Guidelines:\n"
    "- Every scene should have a unique and meaningful title.\n"
    "- The 'script' array should describe visual camera actions and short dialogue lines.\n"
    "- Include transitions and effects where natural.\n"
    "- Keep tone consistent with the theme and duration constraints.\n"
    "- Ensure the total duration roughly matches the constraint.\n"
)
                full_prompt = f"{system_prompt}\nUser Prompt: {prompt}\nConstraints: {json.dumps((constraints.model_dump() if hasattr(constraints, 'model_dump') else dict(constraints)) if constraints else {})}"
                response = model.generate_content(full_prompt)

                if hasattr(response, "text") and response.text:
                    raw_output = response.text.strip()
                elif hasattr(response, "candidates") and len(response.candidates) > 0:
                    raw_output = response.candidates[0].content.parts[0].text.strip()
            except Exception as e:
                print("Gemini API call failed:", str(e))
                raw_output = ""

    # Fallback mock output if no Gemini response
    if not raw_output or not raw_output.strip():
        mock_scene = {
            "processId": f"proc-{uuid.uuid4().hex[:8]}",
            "plan": {
                "title": "Mock Plan",
                "summary": "Fallback mock plan if LLM unavailable.",
                "themes": ["mock"]
            },
            "scenes": [
                {
                    "id": "1",
                    "title": "Intro",
                    "description": prompt,
                    "assets": [
                        {"type": "video", "src": "placeholder_intro.mp4"},
                        {"type": "text", "src": prompt}
                    ],
                    "effects": [{"type": "transition", "name": "fadeIn"}],
                    "durationSec": (constraints.totalDurationSec if constraints and getattr(constraints, "totalDurationSec", None) else 10)
                }
            ],
            "meta": {
                "totalDurationSec": (constraints.totalDurationSec if constraints and getattr(constraints, "totalDurationSec", None) else 10),
                "aspectRatio": (constraints.aspectRatio if constraints and getattr(constraints, "aspectRatio", None) else "16:9"),
                "fps": (constraints.fps if constraints and getattr(constraints, "fps", None) else 30),
                "language": "en"
            }
        }
        raw_output = json.dumps(mock_scene)

    try:
        cleaned_output = _clean_gemini_json(raw_output)
        parsed = json.loads(cleaned_output)
    except Exception as e:
        raise ValueError(f"Failed to parse LLM output as JSON: {e}")

    normalized = _normalize_to_scene_schema(
    parsed, prompt,
    (constraints.model_dump() if hasattr(constraints, "model_dump") else (dict(constraints) if isinstance(constraints, dict) else None))
)
    plan = _make_plan(prompt, normalized.model_dump())
    return {"plan": plan, "scene": normalized.model_dump()}

