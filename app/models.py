from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class InvokeStatus(str, Enum):
    complete = "complete"
    partial = "partial"
    invalid = "invalid"


class InvokeRequest(BaseModel):
    user_input: str


class FieldError(BaseModel):
    field: str
    message: str


class InvokeResponse(BaseModel):
    status: InvokeStatus
    result: dict[str, Any] | None = None
    errors: list[FieldError] | None = None
    extracted: dict[str, Any] | None = None


class SkillField(BaseModel):
    name: str
    required: bool
    type: str


class SkillResponseItem(BaseModel):
    name: str
    description: str
    fields: list[SkillField]
