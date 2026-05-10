from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.skills.base import BaseSkill


class TaskStatus(str, Enum):
    needs_action = "needsAction"
    completed = "completed"


class UpdateGoogleTaskForm(BaseModel):
    task_id: str = Field(description="ID of the task to update")
    title: str | None = Field(None, description="New title for the task")
    due_date: str | None = Field(None, description="New due date in ISO 8601 format")
    notes: str | None = Field(None, description="New notes or description")
    status: TaskStatus | None = Field(None, description="Task status: needsAction or completed")


class UpdateGoogleTask(BaseSkill):
    name = "update_google_task"
    description = "Update an existing task in Google Tasks"
    form_model = UpdateGoogleTaskForm

    async def execute(self, form: UpdateGoogleTaskForm) -> dict[str, Any]:
        # TODO: Google Tasks API call
        return {"status": "updated", "task_id": form.task_id}
