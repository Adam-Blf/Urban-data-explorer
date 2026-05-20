from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from ..db import cassandra_session
from ..schemas import EventRow
from ..security import require_api_key

router = APIRouter(prefix="/events", tags=["events"], dependencies=[Depends(require_api_key)])


@router.get("/recent", response_model=list[EventRow])
def recent_events(limit: int = 50, event_type: str = "service_snapshot"):
    """Return the latest streaming events stored in Cassandra."""

    query = """
        SELECT event_id, event_type, source_id, arrondissement_code, payload, event_time
        FROM events_by_type
        WHERE event_type = %s
        LIMIT %s
    """
    session = cassandra_session()
    try:
        rows = session.execute(query, [event_type, limit])
        return [
            EventRow(
                event_id=str(row.event_id),
                event_type=row.event_type,
                source_id=str(row.source_id),
                arrondissement_code=row.arrondissement_code,
                payload=json.loads(row.payload),
                event_time=row.event_time,
            )
            for row in rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        session.cluster.shutdown()
