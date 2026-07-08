import os
from typing import Any

import httpx


def dispatch_notification(
    channels: list[str],
    payload: dict[str, Any],
    webhook_url: str | None = None,
) -> str:
    statuses: list[str] = []
    timeout = float(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "5"))

    if webhook_url:
        try:
            response = httpx.post(webhook_url, json=payload, timeout=timeout)
            response.raise_for_status()
            statuses.append("webhook:delivered")
        except Exception as exc:
            statuses.append(f"webhook:failed:{type(exc).__name__}")

    for channel in channels:
        normalized = channel.strip().lower()
        if normalized in {"email", "slack", "teams"}:
            statuses.append(f"{normalized}:queued")
        elif normalized:
            statuses.append(f"{normalized}:simulated")

    return ", ".join(statuses) if statuses else "notification:skipped"
