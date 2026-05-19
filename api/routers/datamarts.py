from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..db import pg_conn
from ..schemas import ArrondissementKpi, TimelinePoint

router = APIRouter(prefix="/datamarts", tags=["datamarts"])


@router.get("/arrondissements", response_model=list[ArrondissementKpi])
def list_arrondissements():
    sql = """
        SELECT
            code_arrondissement,
            label,
            prix_m2,
            idx_accessibilite,
            idx_tension,
            idx_effort_social,
            idx_attractivite
        FROM datamart_kpi
        ORDER BY code_arrondissement
    """
    with pg_conn() as conn:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    return [
        ArrondissementKpi(
            code_arrondissement=r[0],
            label=r[1],
            prix_m2=r[2],
            idx_accessibilite=r[3],
            idx_tension=r[4],
            idx_effort_social=r[5],
            idx_attractivite=r[6],
        )
        for r in rows
    ]


@router.get("/timeline", response_model=list[TimelinePoint])
def timeline():
    sql = """
        SELECT code_arrondissement, year, month, prix_m2_median
        FROM datamart_timeline
        ORDER BY code_arrondissement, year, month
    """
    with pg_conn() as conn:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    return [
        TimelinePoint(
            code_arrondissement=r[0],
            year=r[1],
            month=r[2],
            prix_m2_median=r[3],
        )
        for r in rows
    ]

