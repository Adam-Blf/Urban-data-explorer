from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import catalog, datamarts, events, health, pipeline

tags_metadata = [
    # The tags improve the Swagger UI grouping and make the API easier to demo.
    {"name": "health", "description": "Checks and readiness status."},
    {"name": "catalog", "description": "Catalog of integrated data sources."},
    {"name": "pipeline", "description": "Pipeline execution monitoring."},
    {"name": "datamarts", "description": "Gold-level analytical views."},
    {"name": "events", "description": "Recent streaming events from Cassandra."},
]

app = FastAPI(
    title="Urban Data Explorer v2",
    description="FastAPI access to catalog, gold datamarts, pipeline status and streaming events.",
    version="2.0.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(pipeline.router)
app.include_router(datamarts.router)
app.include_router(events.router)


@app.get("/", tags=["health"])
def root():
    """Return the most useful links for local and demo usage."""

    return {
        "name": "Urban Data Explorer",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }
