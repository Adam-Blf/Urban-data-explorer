from __future__ import annotations

from fastapi import APIRouter, Depends

from etl.catalog import ALL_SOURCES

from ..schemas import SourceInfo
from ..security import require_api_key

router = APIRouter(prefix="/catalog", tags=["catalog"], dependencies=[Depends(require_api_key)])


@router.get("/sources", response_model=list[SourceInfo])
def list_sources():
    """Expose the integrated source catalog for the frontend."""

    return [
        SourceInfo(
            source_id=spec.source_id,
            title=spec.title,
            provider=spec.provider,
            family=spec.family,
            catalog_url=spec.catalog_url,
            metadata_only=spec.metadata_only,
        )
        for spec in ALL_SOURCES
    ]
