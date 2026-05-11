from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

import app.registry as registry
from app.llm import extract_fields
from app.models import FieldError, InvokeRequest, InvokeResponse, SkillField, SkillResponseItem
from app.skills.base import field_to_gemini_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.load()
    yield


app = FastAPI(title="Agent API", version="0.1.0", lifespan=lifespan)


@app.get("/skills", response_model=list[SkillResponseItem])
def list_skills() -> list[SkillResponseItem]:
    result = []
    for skill in registry.all_skills():
        required = {
            name
            for name, field in skill.form_model.model_fields.items()
            if field.is_required()
        }
        fields = [
            SkillField(
                name=name,
                required=name in required,
                type=field_to_gemini_schema(field).get("type", "string"),
            )
            for name, field in skill.form_model.model_fields.items()
        ]
        result.append(SkillResponseItem(name=skill.name, description=skill.description, fields=fields))
    return result


@app.post("/skills/{skill_name}/invoke", response_model=InvokeResponse)
async def invoke_skill(skill_name: str, body: InvokeRequest) -> InvokeResponse:
    skill = registry.get(skill_name)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    extracted = await extract_fields(skill, body.user_input)

    try:
        form = skill.form_model.model_validate(extracted)
    except ValidationError as exc:
        errors = [
            FieldError(field=str(e["loc"][0]), message=e["msg"])
            for e in exc.errors()
        ]
        return InvokeResponse(status="invalid", errors=errors, extracted=extracted)

    result = await skill.execute(form)
    return InvokeResponse(status="complete", result=result, extracted=extracted)
