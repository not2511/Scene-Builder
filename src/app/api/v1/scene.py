"""
scene.py

API endpoint definitions for the Scene Builder Agent (v1)
Defines the POST /v1/agent/scene endpoint and connects it with the real pipeline
Validates incoming requests and returns the generated plan and Scene JSON
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.app.core.schema import SceneSchema, SceneInputConstraints
from src.app.agents.pipeline import run_pipeline

router = APIRouter()


class SceneRequest(BaseModel):
    prompt: str = Field(..., description="Natural language prompt describing the desired scene(s)")
    constraints: Optional[SceneInputConstraints] = Field(
        default_factory=SceneInputConstraints,
        description="Optional generation constraints such as duration, fps, aspect ratio, deterministic flag"
    )


class SceneResponse(BaseModel):
    plan: Dict[str, Any]
    scene: SceneSchema


@router.post("/scene", response_model=SceneResponse)
async def generate_scene(request: SceneRequest):
    """
    POST /v1/agent/scene
    Accepts a natural language prompt and optional constraints
    Runs the full scene-building pipeline and returns plan + scene JSON
    """
    try:
        result = run_pipeline(request.prompt, request.constraints)
        scene_obj = SceneSchema.parse_obj(result["scene"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=422, detail=[str(e)])

    response = {"plan": result["plan"], "scene": scene_obj}
    return response
