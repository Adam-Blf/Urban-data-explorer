"""Endpoints datamarts · arrondissements, timeline, indicateurs."""

from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, Query

from pipeline.config import get_settings

from ..db import gold_connection
from ..schemas import (
    ArrondissementKpi,
    IndicatorRow,
    Page,
    TimelinePoint,
)
from ..security import get_current_user

router = APIRouter(prefix="/datamarts", tags=["datamarts"])


def _paginate(items, page: int, page_size: int, total: int):
    pages = math.ceil(total / page_size) if total else 0
    return Page(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
        next_page=page + 1 if page < pages else None,
        prev_page=page - 1 if page > 1 else None,
    )


def _bound_page_size(ps: int) -> int:
    s = get_settings()
    return max(1, min(ps, s.max_page_size))


@router.get("/arrondissements", response_model=Page[ArrondissementKpi])
def list_arrondissements(
    user: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1),
    code_arrondissement: str | None = Query(
        None, description="Filtre code (75101..75120)"
    ),
    min_attractivite: float | None = Query(None),
    max_prix_m2: float | None = Query(None),
    order_by: str = Query(
        "code_arrondissement",
        pattern="^(code_arrondissement|prix_m2|idx_attractivite|idx_accessibilite|idx_tension)$",
    ),
    desc: bool = Query(False),
) -> Page[ArrondissementKpi]:
    settings = get_settings()
    page_size = _bound_page_size(page_size or settings.default_page_size)

    where: list[str] = []
    params: list = []
    if code_arrondissement:
        where.append("code_arrondissement = ?")
        params.append(code_arrondissement)
    if min_attractivite is not None:
        where.append("idx_attractivite >= ?")
        params.append(min_attractivite)
    if max_prix_m2 is not None:
        where.append("prix_m2 <= ?")
        params.append(max_prix_m2)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    direction = "DESC" if desc else "ASC"
    offset = (page - 1) * page_size

    with gold_connection() as con:
        try:
            total = con.execute(
                f"SELECT COUNT(*) FROM kpi_arrondissement {where_sql}", params
            ).fetchone()[0]
            rows = con.execute(
                f"""
                SELECT *
                FROM kpi_arrondissement
                {where_sql}
                ORDER BY {order_by} {direction}
                LIMIT ? OFFSET ?
                """,
                [*params, page_size, offset],
            ).fetch_arrow_table().to_pylist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    items = [ArrondissementKpi(**_safe(r)) for r in rows]
    return _paginate(items, page, page_size, int(total))


@router.get("/timeline", response_model=Page[TimelinePoint])
def get_timeline(
    user: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1),
    code_arrondissement: str | None = Query(None),
    year_from: int | None = Query(None, ge=2010, le=2030),
    year_to: int | None = Query(None, ge=2010, le=2030),
) -> Page[TimelinePoint]:
    settings = get_settings()
    page_size = _bound_page_size(page_size or settings.default_page_size)

    where: list[str] = []
    params: list = []
    if code_arrondissement:
        where.append("code_arrondissement = ?")
        params.append(code_arrondissement)
    if year_from is not None:
        where.append("year >= ?")
        params.append(year_from)
    if year_to is not None:
        where.append("year <= ?")
        params.append(year_to)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    offset = (page - 1) * page_size

    with gold_connection() as con:
        try:
            total = con.execute(
                f"SELECT COUNT(*) FROM timeline_arrondissement {where_sql}", params
            ).fetchone()[0]
            rows = con.execute(
                f"""
                SELECT *
                FROM timeline_arrondissement
                {where_sql}
                ORDER BY code_arrondissement, year, month
                LIMIT ? OFFSET ?
                """,
                [*params, page_size, offset],
            ).fetch_arrow_table().to_pylist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    items = [TimelinePoint(**_safe(r)) for r in rows]
    return _paginate(items, page, page_size, int(total))


@router.get("/indicators", response_model=Page[IndicatorRow])
def get_indicators(
    user: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1),
    indicator: str | None = Query(
        None,
        pattern="^(idx_accessibilite|idx_tension|idx_effort_social|idx_attractivite)$",
    ),
) -> Page[IndicatorRow]:
    settings = get_settings()
    page_size = _bound_page_size(page_size or settings.default_page_size)

    indicators = (
        ["idx_accessibilite", "idx_tension", "idx_effort_social", "idx_attractivite"]
        if indicator is None
        else [indicator]
    )
    union = " UNION ALL ".join(
        f"SELECT code_arrondissement, label, '{i}' AS indicator, {i} AS value FROM kpi_arrondissement"
        for i in indicators
    )

    offset = (page - 1) * page_size
    with gold_connection() as con:
        total = con.execute(f"SELECT COUNT(*) FROM ({union}) t").fetchone()[0]
        rows = con.execute(
            f"""
            SELECT * FROM ({union}) t
            ORDER BY indicator, code_arrondissement
            LIMIT ? OFFSET ?
            """,
            [page_size, offset],
        ).fetch_arrow_table().to_pylist()

    items = [IndicatorRow(**r) for r in rows]
    return _paginate(items, page, page_size, int(total))


def _safe(row: dict) -> dict:
    """DuckDB renvoie parfois Decimal/None proches · normalise pour Pydantic."""
    out = {}
    for k, v in row.items():
        if isinstance(v, (int, float, str)) or v is None:
            out[k] = v
        else:
            out[k] = float(v)
    return out
