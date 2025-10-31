"""
schema.py

Pydantic models that represent the Scene JSON schema.

Responsibilities:
- Define Pydantic models for Scene JSON (SceneSchema, SceneItem, Row, Action, Effect, Meta)
- Provide lightweight validation (types, optional constraints)
- Act as the single source of truth for the shape returned by the API
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Any, Dict

class LicenseBlock(BaseModel):
    source: str
    author: Optional[str] = ""
    url: Optional[str] = ""
    license: Optional[str] = ""

class Effect(BaseModel):
    name: str
    props: Dict[str, Any] = Field(default_factory=dict)

class Action(BaseModel):
    id: str
    type: Literal["video", "image", "audio", "text"]
    startSec: float
    durationSec: float
    props: Dict[str, Any]
    effects: Optional[List[Effect]] = Field(default_factory=list)

class Row(BaseModel):
    id: str
    kind: Literal["video", "image", "audio", "text", "captions"]
    actions: List[Action]
    transitions: Optional[List[Effect]] = Field(default_factory=list)

class SceneItem(BaseModel):
    id: str
    title: Optional[str] = ""
    durationSec: float
    rows: List[Row]

class Meta(BaseModel):
    aspectRatio: Optional[str] = "16:9"
    fps: Optional[int] = 30
    totalDurationSec: float
    generator: Optional[str] = "scene-builder-agent"
    version: Optional[str] = "1.0.0"

class SceneSchema(BaseModel):
    scenes: List[SceneItem]
    meta: Meta

#  constraints model used by the API
class SceneInputConstraints(BaseModel):
    totalDurationSec: Optional[int] = None
    aspectRatio: Optional[str] = "16:9"
    fps: Optional[int] = 30
    language: Optional[str] = "en"  
    deterministic: Optional[bool] = False

