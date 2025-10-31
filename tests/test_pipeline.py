"""
End to end tests for the full scene builder pipeline
Checks for deterministic output, duration and license
"""
from src.app.agents.pipeline import run_pipeline
from src.app.core.schema import SceneInputConstraints

def test_pipeline_deterministic():
    constraints = SceneInputConstraints(totalDurationSec=10, deterministic=True)
    result1 = run_pipeline("Create a 10s motivational video", constraints)
    result2 = run_pipeline("Create a 10s motivational video", constraints) 
    plan1 = result1["plan"]["plan"]
    plan2 = result2["plan"]["plan"]

    assert plan1["scenesCount"] == plan2["scenesCount"]
    assert plan1["durationPerSceneSec"] == plan2["durationPerSceneSec"]


def test_duration_budget():
    constraints = SceneInputConstraints(totalDurationSec=15, deterministic=True)
    result = run_pipeline("Create a short intro video", constraints)
    meta_dur = result["scene"]["meta"]["totalDurationSec"]
    total_scene_dur = sum(s["durationSec"] for s in result["scene"]["scenes"])
    assert round(meta_dur, 2) == round(total_scene_dur, 2)

def test_license_presence():
    constraints = SceneInputConstraints(totalDurationSec=8, deterministic=True)
    result = run_pipeline("Simple text and video", constraints)
    for scene in result["scene"]["scenes"]:
        for row in scene["rows"]:
            for action in row["actions"]:
                license_info = action["props"].get("license", {})
                assert "license" in license_info
                assert license_info.get("license") == "free"
