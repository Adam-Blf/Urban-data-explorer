"""Urban Data Explorer · FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .routers import auth, datamarts, geo
from .schemas import HealthResponse

app = FastAPI(
    title="Urban Data Explorer · API",
    description=(
        "API REST sécurisée (JWT) sur le datamart Gold du logement parisien. "
        "Utilise `/auth/login` pour récupérer un token, puis appelle les "
        "endpoints `/datamarts/*` et `/geo/*`."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(datamarts.router)
app.include_router(geo.router)


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)
