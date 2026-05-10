from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.skills.base import BaseSkill


class CreateGoogleTaskForm(BaseModel):
    title: str = Field(description="Title of the task")
    due_date: str | None = Field(None, description="Due date in ISO 8601 format, e.g. 2025-06-01")
    notes: str | None = Field(None, description="Additional notes or description")


class CreateGoogleTask(BaseSkill):
    name = "create_google_task"
    description = "Create a new task in Google Tasks"
    form_model = CreateGoogleTaskForm

    async def execute(self, form: CreateGoogleTaskForm) -> dict[str, Any]:
        # TODO: Google Tasks API call
        return {"status": "created", "title": form.title, "due_date": form.due_date}
