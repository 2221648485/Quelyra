from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=300)


class QuestionRequest(BaseModel):
    datasource_id: uuid.UUID
    question: str = Field(min_length=1, max_length=10_000)
