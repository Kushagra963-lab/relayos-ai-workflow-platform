from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentConfigBase(BaseModel):
    key: str = Field(min_length=2, max_length=80)
    name: str
    use_case: str
    prompt: str
    classifier_labels: list[str] = Field(default_factory=list)
    notification_channels: list[str] = Field(default_factory=list)
    webhook_url: str | None = None
    confidence_threshold: float = 0.72
    is_active: bool = True


class AgentConfigCreate(AgentConfigBase):
    pass


class AgentConfigUpdate(BaseModel):
    name: str | None = None
    use_case: str | None = None
    prompt: str | None = None
    classifier_labels: list[str] | None = None
    notification_channels: list[str] | None = None
    webhook_url: str | None = None
    confidence_threshold: float | None = None
    is_active: bool | None = None


class AgentConfigOut(AgentConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class WorkflowLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int | None
    agent_config_id: int | None
    level: str
    event: str
    message: str
    payload: dict[str, Any]
    attempt: int
    created_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    status: str
    doc_type: str
    confidence: float
    extracted_fields: dict[str, Any]
    summary: str
    action_items: list[str]
    assigned_queue: str
    retry_count: int
    notification_status: str
    agent_config_id: int | None
    created_at: datetime
    updated_at: datetime


class DashboardOut(BaseModel):
    metrics: dict[str, int | float]
    documents: list[DocumentOut]
    logs: list[WorkflowLogOut]
    agents: list[AgentConfigOut]
