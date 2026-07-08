import os
import re
from typing import Any, TypedDict

from app.services.extraction import extract_business_fields


class WorkflowState(TypedDict, total=False):
    filename: str
    text: str
    doc_type: str
    confidence: float
    extracted_fields: dict[str, Any]
    summary: str
    action_items: list[str]
    assigned_queue: str


class AgentRuntime:
    def __init__(self) -> None:
        self.graph = self._build_graph()

    def run(self, filename: str, text: str, agent_config: dict[str, Any]) -> WorkflowState:
        state: WorkflowState = {"filename": filename, "text": text}
        if self.graph is not None:
            return self.graph.invoke(state | {"agent_config": agent_config})

        state = self._classify_node(state | {"agent_config": agent_config})
        state = self._extract_node(state)
        state = self._summarize_node(state)
        state = self._route_node(state)
        return state

    def _build_graph(self):
        try:
            from langgraph.graph import END, StateGraph

            workflow = StateGraph(dict)
            workflow.add_node("classify", self._classify_node)
            workflow.add_node("extract", self._extract_node)
            workflow.add_node("summarize", self._summarize_node)
            workflow.add_node("route", self._route_node)
            workflow.set_entry_point("classify")
            workflow.add_edge("classify", "extract")
            workflow.add_edge("extract", "summarize")
            workflow.add_edge("summarize", "route")
            workflow.add_edge("route", END)
            return workflow.compile()
        except Exception:
            return None

    def _classify_node(self, state: dict[str, Any]) -> dict[str, Any]:
        doc_type, confidence = classify_document(state.get("text", ""))
        return state | {"doc_type": doc_type, "confidence": confidence}

    def _extract_node(self, state: dict[str, Any]) -> dict[str, Any]:
        fields = extract_business_fields(state.get("text", ""), state.get("doc_type", "unknown"))
        return state | {"extracted_fields": fields}

    def _summarize_node(self, state: dict[str, Any]) -> dict[str, Any]:
        text = state.get("text", "")
        doc_type = state.get("doc_type", "unknown")
        summary = summarize_with_llm(text, doc_type) or summarize_text(text, doc_type)
        actions = action_items_for(doc_type, state.get("extracted_fields", {}))
        return state | {"summary": summary, "action_items": actions}

    def _route_node(self, state: dict[str, Any]) -> dict[str, Any]:
        doc_type = state.get("doc_type", "unknown")
        queue_by_type = {
            "hr": "people-ops",
            "finance": "finance-ops",
            "legal": "legal-review",
            "support": "customer-operations",
            "unknown": "operations-triage",
        }
        return state | {"assigned_queue": queue_by_type.get(doc_type, "operations-triage")}


def classify_document(text: str) -> tuple[str, float]:
    normalized = text.lower()
    vocab = {
        "hr": ["employee", "candidate", "payroll", "offer", "salary", "leave", "onboarding", "benefits", "resume"],
        "finance": ["invoice", "payment", "amount", "gst", "tax", "expense", "purchase", "vendor", "receipt"],
        "legal": ["contract", "agreement", "nda", "clause", "party", "jurisdiction", "terms", "liability"],
        "support": ["ticket", "incident", "customer", "priority", "sla", "bug", "request", "escalation"],
    }

    scores = {
        doc_type: sum(1 for token in tokens if re.search(rf"\b{re.escape(token)}\b", normalized))
        for doc_type, tokens in vocab.items()
    }
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    total_score = sum(scores.values()) or 1

    if best_score == 0:
        return "unknown", 0.38

    confidence = min(0.97, 0.55 + (best_score / total_score) * 0.42)
    return best_type, round(confidence, 2)


def summarize_text(text: str, doc_type: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    usable = [sentence for sentence in sentences if len(sentence) > 24]
    head = " ".join(usable[:2]) if usable else text[:260]
    if not head:
        head = "No extractable text was found. Manual review is required."
    return f"{doc_type.upper()} document summary: {head[:520]}"


def summarize_with_llm(text: str, doc_type: str) -> str | None:
    if not os.getenv("OPENAI_API_KEY") or not text.strip():
        return None
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.1)
        response = llm.invoke(
            "Summarize this business document in two concise sentences. "
            f"Document type: {doc_type}\n\n{text[:5000]}"
        )
        return str(response.content).strip()
    except Exception:
        return None


def action_items_for(doc_type: str, fields: dict[str, Any]) -> list[str]:
    if doc_type == "finance":
        return [
            "Validate invoice amount and vendor ownership",
            "Route to finance approver",
            "Schedule payment or flag exception",
        ]
    if doc_type == "legal":
        return [
            "Assign legal reviewer",
            "Check dates, liability, and termination clauses",
            "Send redlines or approval decision",
        ]
    if doc_type == "hr":
        return [
            "Verify employee or candidate record",
            "Update HRIS checklist",
            "Notify people ops owner",
        ]
    if doc_type == "support":
        return [
            "Confirm ticket priority and SLA",
            "Route to owning operations queue",
            "Send status notification",
        ]

    if fields:
        return ["Review extracted fields", "Assign manual owner", "Update workflow status"]
    return ["Perform manual review", "Capture missing fields", "Re-run workflow after correction"]
