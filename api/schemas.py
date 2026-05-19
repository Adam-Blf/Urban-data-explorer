from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ArrondissementKpi(BaseModel):
    code_arrondissement: str
    label: str
    prix_m2: float | None = None
    idx_accessibilite: float | None = None
    idx_tension: float | None = None
    idx_effort_social: float | None = None
    idx_attractivite: float | None = None


class TimelinePoint(BaseModel):
    code_arrondissement: str
    year: int
    month: int
    prix_m2_median: float | None = None


class EventRow(BaseModel):
    event_id: str
    event_type: str
    payload: dict[str, Any]
    event_time: datetime

