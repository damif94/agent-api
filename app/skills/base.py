from __future__ import annotations

import types as builtin_types
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, Type, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo


def field_to_schema(field: FieldInfo) -> dict:
    annotation = field.annotation
    description = field.description or ""

    # Unwrap Optional / union-with-None (both `Optional[X]` and `X | None`)
    origin = get_origin(annotation)
    if origin is Union or isinstance(annotation, builtin_types.UnionType):
        args = [a for a in get_args(annotation) if a is not type(None)]
        if args:
            annotation = args[0]

    # Enum → string with values list
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        schema: dict[str, Any] = {"type": "string", "enum": [e.value for e in annotation]}
        if description:
            schema["description"] = description
        return schema

    type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
    schema = {"type": type_map.get(annotation, "string")}
    if description:
        schema["description"] = description
    return schema


class BaseSkill(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    form_model: ClassVar[Type[BaseModel]]

    @abstractmethod
    async def execute(self, form: BaseModel) -> dict[str, Any]: ...


class NoOpSkill(BaseSkill):
    async def execute(self, form: BaseModel) -> dict[str, Any]:
        return {}
