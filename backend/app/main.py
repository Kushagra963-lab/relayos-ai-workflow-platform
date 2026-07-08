from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.agents import AgentRuntime
from app.database import get_db, init_db
from app.models import AgentConfig, Document, WorkflowLog
from app.schemas import (
    AgentConfigCreate,
    AgentConfigOut,
    AgentConfigUpdate,
    DashboardOut,
    DocumentOut,
    WorkflowLogOut,
)
from app.services.extraction import extract_text_from_upload
from app.services.notifications import dispatch_notification
from app.services.vector_store import VectorStore


app = FastAPI(
    title="AI Agent Workflow Automation Platform",
    version="1.0.0",
    description="Document extraction, classification, summarization, routing, notifications, logs, and retries.",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = AgentRuntime()
vector_store = VectorStore()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with next(get_db()) as db:
        seed_agent_configs(db)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "ai-agent-workflow-automation",
        "vector_store": "enabled" if vector_store.enabled else "disabled",
    }


@app.get("/api/dashboard", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardOut:
    documents = db.scalars(select(Document).order_by(desc(Document.created_at)).limit(12)).all()
    logs = db.scalars(select(WorkflowLog).order_by(desc(WorkflowLog.created_at)).limit(30)).all()
    agents = db.scalars(select(AgentConfig).order_by(AgentConfig.name)).all()

    total = db.scalar(select(func.count(Document.id))) or 0
    completed = db.scalar(select(func.count(Document.id)).where(Document.status == "completed")) or 0
    failed = db.scalar(select(func.count(Document.id)).where(Document.status == "failed")) or 0
    retries = db.scalar(select(func.coalesce(func.sum(Document.retry_count), 0))) or 0
    avg_confidence = db.scalar(select(func.coalesce(func.avg(Document.confidence), 0))) or 0

    return DashboardOut(
        metrics={
            "total_documents": total,
            "completed": completed,
            "failed": failed,
            "retries": retries,
            "avg_confidence": round(float(avg_confidence), 2),
            "active_agents": sum(1 for agent in agents if agent.is_active),
        },
        documents=documents,
        logs=logs,
        agents=agents,
    )


@app.post("/api/documents/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    agent_config_id: int | None = Form(None),
    db: Session = Depends(get_db),
) -> Document:
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    agent = get_agent(db, agent_config_id)
    text = extract_text_from_upload(contents, file.filename or "document", file.content_type)
    document = Document(
        filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        status="processing",
        extracted_text=text,
        agent_config_id=agent.id if agent else None,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    write_log(
        db,
        event="document.uploaded",
        message=f"{document.filename} uploaded",
        document=document,
        agent=agent,
        payload={"size_bytes": len(contents), "content_type": document.content_type},
    )
    process_document(db, document, agent)
    return document


@app.get("/api/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).order_by(desc(Document.created_at)).limit(50)).all())


@app.get("/api/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.post("/api/documents/{document_id}/retry", response_model=DocumentOut)
def retry_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    agent = db.get(AgentConfig, document.agent_config_id) if document.agent_config_id else get_agent(db, None)
    document.retry_count += 1
    document.status = "processing"
    document.notification_status = "pending"
    db.commit()
    db.refresh(document)

    write_log(
        db,
        event="document.retry",
        message=f"Retry started for {document.filename}",
        document=document,
        agent=agent,
        level="warning",
        payload={"retry_count": document.retry_count},
    )
    process_document(db, document, agent)
    return document


@app.get("/api/documents/{document_id}/logs", response_model=list[WorkflowLogOut])
def document_logs(document_id: int, db: Session = Depends(get_db)) -> list[WorkflowLog]:
    return list(
        db.scalars(
            select(WorkflowLog)
            .where(WorkflowLog.document_id == document_id)
            .order_by(desc(WorkflowLog.created_at))
        ).all()
    )


@app.get("/api/logs", response_model=list[WorkflowLogOut])
def list_logs(db: Session = Depends(get_db)) -> list[WorkflowLog]:
    return list(db.scalars(select(WorkflowLog).order_by(desc(WorkflowLog.created_at)).limit(100)).all())


@app.get("/api/agents", response_model=list[AgentConfigOut])
def list_agents(db: Session = Depends(get_db)) -> list[AgentConfig]:
    return list(db.scalars(select(AgentConfig).order_by(AgentConfig.name)).all())


@app.post("/api/agents", response_model=AgentConfigOut)
def create_agent(payload: AgentConfigCreate, db: Session = Depends(get_db)) -> AgentConfig:
    existing = db.scalar(select(AgentConfig).where(AgentConfig.key == payload.key))
    if existing:
        raise HTTPException(status_code=409, detail="Agent key already exists")
    agent = AgentConfig(**payload.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    write_log(db, event="agent.created", message=f"{agent.name} created", agent=agent)
    return agent


@app.put("/api/agents/{agent_id}", response_model=AgentConfigOut)
def update_agent(agent_id: int, payload: AgentConfigUpdate, db: Session = Depends(get_db)) -> AgentConfig:
    agent = db.get(AgentConfig, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    db.commit()
    db.refresh(agent)
    write_log(db, event="agent.updated", message=f"{agent.name} updated", agent=agent)
    return agent


@app.post("/api/webhooks/test")
def test_webhook(payload: dict[str, Any]) -> dict[str, str]:
    status = dispatch_notification(
        payload.get("channels", ["slack"]),
        {"event": "webhook.test", "payload": payload},
        payload.get("webhook_url"),
    )
    return {"status": status}


def process_document(db: Session, document: Document, agent: AgentConfig | None) -> None:
    try:
        agent_payload = agent_to_payload(agent)
        result = runtime.run(document.filename, document.extracted_text, agent_payload)

        document.doc_type = result.get("doc_type", "unknown")
        document.confidence = float(result.get("confidence", 0))
        document.extracted_fields = result.get("extracted_fields", {})
        document.summary = result.get("summary", "")
        document.action_items = result.get("action_items", [])
        document.assigned_queue = result.get("assigned_queue", "operations-triage")

        vector_status = vector_store.add_document(
            str(document.id),
            document.extracted_text,
            {
                "filename": document.filename,
                "doc_type": document.doc_type,
                "assigned_queue": document.assigned_queue,
            },
        )
        write_log(
            db,
            event="document.indexed",
            message=vector_status,
            document=document,
            agent=agent,
            payload={"vector_store": vector_status},
        )

        notification_payload = {
            "document_id": document.id,
            "filename": document.filename,
            "doc_type": document.doc_type,
            "confidence": document.confidence,
            "assigned_queue": document.assigned_queue,
            "action_items": document.action_items,
        }
        document.notification_status = dispatch_notification(
            agent.notification_channels if agent else ["slack"],
            notification_payload,
            agent.webhook_url if agent else None,
        )
        document.status = "completed"
        db.commit()
        db.refresh(document)

        write_log(
            db,
            event="document.completed",
            message=f"{document.filename} routed to {document.assigned_queue}",
            document=document,
            agent=agent,
            payload=notification_payload | {"notification_status": document.notification_status},
        )
    except Exception as exc:
        document.status = "failed"
        document.notification_status = "notification:skipped"
        db.commit()
        write_log(
            db,
            event="document.failed",
            message=str(exc),
            document=document,
            agent=agent,
            level="error",
            payload={"error_type": type(exc).__name__},
        )


def seed_agent_configs(db: Session) -> None:
    if db.scalar(select(func.count(AgentConfig.id))) or 0:
        return

    agents = [
        AgentConfig(
            key="hr-onboarding",
            name="HR Onboarding Agent",
            use_case="HR document intake",
            prompt="Extract employee data, classify HR document type, summarize onboarding risks, and notify people ops.",
            classifier_labels=["offer_letter", "payroll", "onboarding", "policy"],
            notification_channels=["email", "slack"],
            confidence_threshold=0.74,
            is_active=True,
        ),
        AgentConfig(
            key="finance-invoice",
            name="Finance Invoice Agent",
            use_case="Invoice and expense routing",
            prompt="Extract invoice fields, validate vendor and amount, summarize payment action, and notify finance ops.",
            classifier_labels=["invoice", "receipt", "purchase_order", "expense"],
            notification_channels=["slack", "webhook"],
            confidence_threshold=0.78,
            is_active=True,
        ),
        AgentConfig(
            key="legal-review",
            name="Legal Review Agent",
            use_case="Contract and NDA review",
            prompt="Identify parties, dates, key clauses, risk notes, and route to legal review.",
            classifier_labels=["contract", "nda", "agreement", "policy"],
            notification_channels=["email"],
            confidence_threshold=0.8,
            is_active=True,
        ),
    ]
    db.add_all(agents)
    db.commit()


def get_agent(db: Session, agent_config_id: int | None) -> AgentConfig | None:
    if agent_config_id:
        agent = db.get(AgentConfig, agent_config_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent config not found")
        return agent
    return db.scalar(select(AgentConfig).where(AgentConfig.is_active.is_(True)).order_by(AgentConfig.id))


def agent_to_payload(agent: AgentConfig | None) -> dict[str, Any]:
    if not agent:
        return {}
    return {
        "id": agent.id,
        "key": agent.key,
        "name": agent.name,
        "use_case": agent.use_case,
        "prompt": agent.prompt,
        "classifier_labels": agent.classifier_labels,
        "notification_channels": agent.notification_channels,
        "confidence_threshold": agent.confidence_threshold,
    }


def write_log(
    db: Session,
    event: str,
    message: str,
    document: Document | None = None,
    agent: AgentConfig | None = None,
    level: str = "info",
    payload: dict[str, Any] | None = None,
) -> WorkflowLog:
    log = WorkflowLog(
        document_id=document.id if document else None,
        agent_config_id=agent.id if agent else None,
        level=level,
        event=event,
        message=message,
        payload=payload or {},
        attempt=(document.retry_count + 1) if document else 1,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
