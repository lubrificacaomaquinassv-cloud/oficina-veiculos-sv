#!/usr/bin/env python3
"""Expoe schema oficina_veiculos na API PostgREST."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

import psycopg2

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "sql" / "003_expor_schema_api.sql"
SECRETS_LOCAL = ROOT / ".streamlit" / "secrets.toml"


def main():
    if not SECRETS_LOCAL.is_file():
        print("secrets.toml nao encontrado")
        sys.exit(1)
    with open(SECRETS_LOCAL, "rb") as f:
        data = tomllib.load(f)
    cfg = data["connections"]["supabase"]
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["username"],
        password=cfg["password"],
        sslmode="require",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(SQL_FILE.read_text(encoding="utf-8"))
    cur.close()
    conn.close()
    print("OK — schema oficina_veiculos exposto na API.")


if __name__ == "__main__":
    main()
