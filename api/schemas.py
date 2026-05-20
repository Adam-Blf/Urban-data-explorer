from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SourceInfo(BaseModel):
    source_id: str
    title: str
    provider: str
    family: str
    catalog_url: str
    metadata_only: bool = False


class ArrondissementDashboard(BaseModel):
    arrondissement_code: str
    green_space_count: int
    mobility_count: int
    public_service_count: int
    education_count: int
    culture_count: int
    health_count: int
    housing_count: int
    pressure_count: int
    accessibility_index: float
    pressure_index: float
    attractiveness_index: float


class TimelinePoint(BaseModel):
    arrondissement_code: str
    year: int
    month: int
    record_count: int
    accessibility_index: float
    pressure_index: float
    attractiveness_index: float


class EventRow(BaseModel):
    event_id: str
    event_type: str
    source_id: str
    arrondissement_code: str | None = None
    payload: dict[str, Any]
    event_time: datetime


class PipelineRun(BaseModel):
    run_date: str
    stage: str
    status: str
    row_count: int
    updated_at: datetime
