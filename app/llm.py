from __future__ import annotations

import asyncio
import os
import types as builtin_types
from typing import Optional, Type, Union, get_args, get_origin

import instructor
from google import genai
from pydantic import BaseModel, Field, create_model

from app.skills.base import BaseSkill

_client = instructor.from_genai(genai.Client(api_key=os.environ["GEMINI_API_KEY"]), use_async=False)


def _make_partial(model: Type[BaseModel]) -> Type[BaseModel]:
    """Return a copy of model with every field made Optional[T] = None.

    This mirrors the old 'required: []' trick — we extract only what the LLM
    provides; required-field validation happens later in Pydantic.
    """
    fields: dict = {}
    for name, field_info in model.model_fields.items():
        annotation = field_info.annotation
        # Unwrap existing Optional/union-with-None before re-wrapping
        origin = get_origin(annotation)
        if origin is Union or isinstance(annotation, builtin_types.UnionType):
            inner = [a for a in get_args(annotation) if a is not type(None)]
            if inner:
                annotation = inner[0]
        fields[name] = (Optional[annotation], Field(None, description=field_info.description))
    return create_model(f"_Partial{model.__name__}", **fields)


def _extract_sync(skill: BaseSkill, user_input: str) -> dict:
    partial_model = _make_partial(skill.form_model)
    result = _client.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": user_input}],
        response_model=partial_model,
    )
    return result.model_dump(exclude_none=True)


async def extract_fields(skill: BaseSkill, user_input: str) -> dict:
    return await asyncio.to_thread(_extract_sync, skill, user_input)
