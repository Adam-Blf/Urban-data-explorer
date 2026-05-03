"""Exporte la spec OpenAPI de l'API + une collection Postman prête à importer.

Sortie ·
    docs/openapi.json
    docs/postman_collection.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT))

# Set demo env so the app can boot without .env
os.environ.setdefault("JWT_SECRET", "export-only-secret-thirty-two-chars")
os.environ.setdefault("DEMO_USER", "admin")
os.environ.setdefault("DEMO_PASSWORD", "admin")
os.environ.setdefault("GOLD_DUCKDB_PATH", str(ROOT / "data" / "demo" / "urban.duckdb"))

from api.main import app  # noqa: E402


def export_openapi() -> Path:
    spec = app.openapi()
    out = DOCS / "openapi.json"
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"openapi · wrote {out} ({out.stat().st_size // 1024} KB)")
    return out


def to_postman(spec: dict) -> dict:
    """Conversion minimale OpenAPI → Postman v2.1 (suffit pour l'import GUI)."""
    items = []
    base_url = "{{baseUrl}}"

    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method.upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            req = {
                "name": op.get("summary") or f"{method.upper()} {path}",
                "request": {
                    "method": method.upper(),
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{accessToken}}"},
                        {"key": "Content-Type",  "value": "application/json"},
                    ],
                    "url": {
                        "raw": f"{base_url}{path}",
                        "host": [base_url],
                        "path": [p for p in path.split("/") if p],
                    },
                },
            }
            if method.upper() in {"POST", "PUT", "PATCH"}:
                example = {"username": "admin", "password": "admin"} if path.endswith("/login") else {}
                req["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(example, indent=2),
                    "options": {"raw": {"language": "json"}},
                }
            items.append(req)

    return {
        "info": {
            "name": "Urban Data Explorer · API",
            "_postman_id": "urban-data-explorer-1",
            "description": (spec.get("info", {}).get("description") or "")
                           + "\n\nDefine `baseUrl` (e.g. http://localhost:8000) and "
                             "`accessToken` (returned by /auth/login) as Postman variables.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
        "variable": [
            {"key": "baseUrl",     "value": "http://localhost:8000"},
            {"key": "accessToken", "value": ""},
        ],
    }


def export_postman(spec: dict) -> Path:
    out = DOCS / "postman_collection.json"
    out.write_text(json.dumps(to_postman(spec), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"postman · wrote {out} ({out.stat().st_size // 1024} KB · {len(to_postman(spec)['item'])} requests)")
    return out


def main():
    spec_path = export_openapi()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    export_postman(spec)


if __name__ == "__main__":
    main()
