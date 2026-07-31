#!/usr/bin/env python3
"""Aplica sql/001_oficina_veiculos_schema.sql no Supabase (uma vez)."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

import psycopg2

ROOT = Path(__file__).resolve().parent
SQL_FILES = [
    ROOT / "sql" / "001_oficina_veiculos_schema.sql",
    ROOT / "sql" / "002_reload_postgrest_schema.sql",
]
SECRETS_LOCAL = ROOT / ".streamlit" / "secrets.toml"
SECRETS_SIGALMOX = ROOT.parent / "SIGALMOX" / ".streamlit" / "secrets.toml"


def load_db_cfg():
    for path in (SECRETS_LOCAL, SECRETS_SIGALMOX):
        if path.is_file():
            with open(path, "rb") as f:
                data = tomllib.load(f)
            if "connections" in data and "supabase" in data["connections"]:
                return data["connections"]["supabase"]
    print("Secrets não encontrado. Cole sql/001_oficina_veiculos_schema.sql no Supabase SQL Editor.")
    sys.exit(1)


def main():
    cfg = load_db_cfg()
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
    for sql_file in SQL_FILES:
        if not sql_file.is_file():
            print(f"SQL não encontrado: {sql_file}")
            sys.exit(1)
        print(f"Aplicando {sql_file.name}...")
        cur.execute(sql_file.read_text(encoding="utf-8"))
    cur.close()
    conn.close()
    print("OK — schema oficina_veiculos aplicado.")
    print("Lembre: Settings > API > Exposed schemas > adicionar 'oficina_veiculos'")


if __name__ == "__main__":
    main()
