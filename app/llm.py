from __future__ import annotations

import asyncio
import os

from google import genai
from google.genai import types

from app.skills.base import BaseSkill

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _extract_sync(skill: BaseSkill, user_input: str) -> dict:
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input,
        config=types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=[skill.function_declaration()])],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.function_call:
            return {k: v for k, v in dict(part.function_call.args).items() if v is not None}
    return {}


async def extract_fields(skill: BaseSkill, user_input: str) -> dict:
    return await asyncio.to_thread(_extract_sync, skill, user_input)
