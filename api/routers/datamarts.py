from __future__ import annotations

from fastapi import APIRouter, Depends

from ..db import pg_fetch_all
from ..schemas import ArrondissementDashboard, TimelinePoint
from ..security import require_api_key

router = APIRouter(prefix="/datamarts", tags=["datamarts"], dependencies=[Depends(require_api_key)])


@router.get("/dashboard", response_model=list[ArrondissementDashboard])
def dashboard():
    """Return the current arrondissement KPI dashboard."""

    rows = pg_fetch_all(
        """
        SELECT
            arrondissement_code,
            green_space_count,
            mobility_count,
            public_service_count,
            education_count,
            culture_count,
            health_count,
            housing_count,
            pressure_count,
            accessibility_index,
            pressure_index,
            attractiveness_index
        FROM fact_arrondissement_dashboard
        ORDER BY arrondissement_code
        """
    )
    return [ArrondissementDashboard(**row) for row in rows]


@router.get("/timeline", response_model=list[TimelinePoint])
def timeline():
    """Return the monthly Gold trend mart."""

    rows = pg_fetch_all(
        """
        SELECT
            arrondissement_code,
            year,
            month,
            record_count,
            accessibility_index,
            pressure_index,
            attractiveness_index
        FROM fact_arrondissement_timeline
        ORDER BY arrondissement_code, year, month
        """
    )
    return [TimelinePoint(**row) for row in rows]
