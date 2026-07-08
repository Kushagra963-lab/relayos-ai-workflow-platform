from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    use_case: Mapped[str] = mapped_column(String(120), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    classifier_labels: Mapped[list[str]] = mapped_column(JSON, default=list)
    notification_channels: Mapped[list[str]] = mapped_column(JSON, default=list)
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.72)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    documents: Mapped[list["Document"]] = relationship(back_populates="agent_config")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)
    content_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    status: Mapped[str] = mapped_column(String(40), default="queued", index=True)
    doc_type: Mapped[str] = mapped_column(String(80), default="unknown", index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    extracted_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    summary: Mapped[str] = mapped_column(Text, default="")
    action_items: Mapped[list[str]] = mapped_column(JSON, default=list)
    assigned_queue: Mapped[str] = mapped_column(String(100), default="operations")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    notification_status: Mapped[str] = mapped_column(String(160), default="pending")
    agent_config_id: Mapped[int | None] = mapped_column(ForeignKey("agent_configs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    agent_config: Mapped[AgentConfig | None] = relationship(back_populates="documents")
    logs: Mapped[list["WorkflowLog"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="WorkflowLog.created_at",
    )


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    agent_config_id: Mapped[int | None] = mapped_column(ForeignKey("agent_configs.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(20), default="info", index=True)
    event: Mapped[str] = mapped_column(String(120), index=True)
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped[Document | None] = relationship(back_populates="logs")
