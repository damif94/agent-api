from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class InvokeRequest(BaseModel):
    user_input: str


class FieldError(BaseModel):
    field: str
    message: str


class InvokeResponse(BaseModel):
    status: Literal["complete", "invalid"]
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
