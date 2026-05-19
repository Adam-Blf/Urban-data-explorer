from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from ..db import cassandra_session
from ..schemas import EventRow

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/recent", response_model=list[EventRow])
def recent_events(limit: int = 100):
    sql = """
        SELECT event_id, event_type, payload, event_time
        FROM events_by_type
        WHERE event_type = 'transaction'
        LIMIT %s
    """
    session = cassandra_session()
    try:
        rows = session.execute(sql, [limit])
        return [
            EventRow(
                event_id=str(r.event_id),
                event_type=r.event_type,
                payload=json.loads(r.payload),
                event_time=r.event_time,
            )
            for r in rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        session.cluster.shutdown()
