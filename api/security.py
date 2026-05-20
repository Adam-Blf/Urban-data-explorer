from __future__ import annotations

import os

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Enforce an optional shared API token when API_TOKEN is set."""

    token = os.getenv("API_TOKEN", "")
    if not token:
        return
    if x_api_key != token:
        raise HTTPException(status_code=401, detail="Invalid API key")
