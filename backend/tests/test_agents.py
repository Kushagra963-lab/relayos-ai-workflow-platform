from app.agents import action_items_for, classify_document


def test_classifies_finance_invoice() -> None:
    doc_type, confidence = classify_document("Invoice number INV-42 from vendor Acme. Total amount INR 9000.")
    assert doc_type == "finance"
    assert confidence > 0.7


def test_classifies_legal_agreement() -> None:
    doc_type, confidence = classify_document("This agreement includes liability, jurisdiction, and termination clauses.")
    assert doc_type == "legal"
    assert confidence > 0.7


def test_action_items_for_unknown_fields() -> None:
    actions = action_items_for("unknown", {"document_date": "2026-06-09"})
    assert "Review extracted fields" in actions
