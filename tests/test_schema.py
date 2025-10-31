"""
Tests for validating SceneSchema structure and basic rules
Ensures that generated scene JSON objects comply with Pydantic validation
"""
import pytest
from src.app.core.schema import SceneSchema

def test_valid_scene_schema():
    valid_scene = {
        "scenes": [
            {
                "id": "scene-1",
                "title": "Sample Scene",
                "durationSec": 10,
                "rows": [
                    {
                        "id": "row-1",
                        "kind": "video",
                        "actions": [
                            {
                                "id": "action-1",
                                "type": "video",
                                "startSec": 0,
                                "durationSec": 10,
                                "props": {
                                    "src": "placeholder:test",
                                    "width": 1920,
                                    "height": 1080,
                                    "license": {
                                        "source": "placeholder",
                                        "author": "",
                                        "url": "",
                                        "license": "free"
                                    }
                                },
                                "effects": []
                            }
                        ],
                        "transitions": []
                    }
                ]
            }
        ],
        "meta": {
            "aspectRatio": "16:9",
            "fps": 30,
            "totalDurationSec": 10,
            "generator": "scene-builder-agent",
            "version": "1.0.0"
        }
    }

    schema_obj = SceneSchema.parse_obj(valid_scene)
    assert schema_obj.meta.totalDurationSec == 10
    assert schema_obj.meta.aspectRatio == "16:9"
