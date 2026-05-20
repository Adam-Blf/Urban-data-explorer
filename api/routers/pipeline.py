from __future__ import annotations

from fastapi import APIRouter, Depends

from ..db import pg_fetch_all
from ..schemas import PipelineRun
from ..security import require_api_key

router = APIRouter(prefix="/pipeline", tags=["pipeline"], dependencies=[Depends(require_api_key)])


@router.get("/latest", response_model=PipelineRun | None)
def latest_run():
    """Return the most recent pipeline execution status."""

    rows = pg_fetch_all(
        """
        SELECT run_date, stage, status, row_count, updated_at
        FROM pipeline_runs
        ORDER BY updated_at DESC
        LIMIT 1
        """
    )
    return PipelineRun(**rows[0]) if rows else None
