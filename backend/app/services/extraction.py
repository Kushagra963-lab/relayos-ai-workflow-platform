import re
from io import BytesIO


def extract_text_from_upload(contents: bytes, filename: str, content_type: str | None = None) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf") or content_type == "application/pdf":
        return _extract_pdf_text(contents)

    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return contents.decode(encoding).strip()
        except UnicodeDecodeError:
            continue

    return ""


def extract_business_fields(text: str, doc_type: str) -> dict[str, str | float]:
    compact = " ".join(text.split())
    fields: dict[str, str | float] = {}

    amount = _first_match(r"(?:total|amount|invoice value|payable)\s*[:\-]?\s*(?:rs\.?|inr|usd|\$)?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", compact)
    if amount:
        fields["amount"] = float(amount.replace(",", ""))

    invoice_number = _first_match(r"(?:invoice|bill)\s*(?:no\.?|number|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)", compact, flags=re.I)
    if invoice_number:
        fields["invoice_number"] = invoice_number

    vendor = _first_match(r"(?:vendor|supplier|from)\s*[:\-]\s*([A-Z][A-Za-z0-9 &.,-]{2,80})", compact)
    if vendor:
        fields["vendor"] = vendor.strip(" .,")

    employee = _first_match(r"(?:employee|candidate|staff)\s*(?:name)?\s*[:\-]\s*([A-Z][A-Za-z .'-]{2,80})", compact)
    if employee:
        fields["employee"] = employee.strip(" .,")

    contract_id = _first_match(r"(?:contract|agreement|nda)\s*(?:id|no\.?|number|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)", compact, flags=re.I)
    if contract_id:
        fields["contract_id"] = contract_id

    ticket_id = _first_match(r"(?:ticket|incident|case)\s*(?:id|no\.?|number|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)", compact, flags=re.I)
    if ticket_id:
        fields["ticket_id"] = ticket_id

    date_value = _first_match(r"(\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b|\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b)", compact)
    if date_value:
        fields["document_date"] = date_value

    if doc_type == "legal":
        party = _first_match(r"(?:between|party)\s*[:\-]?\s*([A-Z][A-Za-z0-9 &.,-]{2,90})", compact)
        if party:
            fields["primary_party"] = party.strip(" .,")

    if doc_type == "hr":
        department = _first_match(r"(?:department|team)\s*[:\-]\s*([A-Z][A-Za-z &-]{2,60})", compact)
        if department:
            fields["department"] = department.strip(" .,")

    return fields


def _extract_pdf_text(contents: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(contents))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(page.strip() for page in pages if page.strip())
    except Exception:
        return ""


def _first_match(pattern: str, text: str, flags: int = 0) -> str | None:
    match = re.search(pattern, text, flags)
    if not match:
        return None
    return match.group(1).strip()
