from __future__ import annotations

import types as builtin_types
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, Type, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo


class GeminiPropertySchema(BaseModel):
    type: str
    description: str = ""
    enum: list[str] | None = None


class GeminiFunctionParameters(BaseModel):
    type: str = "object"
    properties: dict[str, GeminiPropertySchema]
    required: list[str] = []


class GeminiFunctionDeclaration(BaseModel):
    name: str
    description: str
    parameters: GeminiFunctionParameters


def field_to_gemini_schema(field: FieldInfo) -> GeminiPropertySchema:
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
        return GeminiPropertySchema(
            type="string",
            description=description,
            enum=[e.value for e in annotation],
        )

    type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
    return GeminiPropertySchema(type=type_map.get(annotation, "string"), description=description)


class BaseSkill(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    form_model: ClassVar[Type[BaseModel]]

    @classmethod
    def function_declaration(cls) -> GeminiFunctionDeclaration:
        """Gemini function declaration with all fields optional (partial extraction)."""
        return GeminiFunctionDeclaration(
            name=cls.name,
            description=cls.description,
            parameters=GeminiFunctionParameters(
                properties={
                    name: field_to_gemini_schema(field)
                    for name, field in cls.form_model.model_fields.items()
                }
            ),
        )

    @abstractmethod
    async def execute(self, form: BaseModel) -> dict[str, Any]: ...
