from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import datamarts, events, health

app = FastAPI(
    title="Urban Data Explorer v2",
    description="FastAPI access to Postgres (gold) and Cassandra (events).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(datamarts.router)
app.include_router(events.router)
