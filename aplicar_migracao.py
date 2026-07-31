#!/usr/bin/env python3
"""Aplica um arquivo SQL de migracao (ex: 004_frota_pesada.sql)."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

import psycopg2

ROOT = Path(__file__).resolve().parent
SECRETS_LOCAL = ROOT / ".streamlit" / "secrets.toml"


def main():
    if len(sys.argv) < 2:
        print("Uso: python aplicar_migracao.py 004")
        sys.exit(1)
    num = sys.argv[1].zfill(3)
    sql_file = ROOT / "sql" / f"{num}_*.sql"
    matches = sorted(ROOT.glob(f"sql/{num}_*.sql"))
    if not matches:
        print(f"SQL nao encontrado: sql/{num}_*.sql")
        sys.exit(1)
    sql_file = matches[0]

    with open(SECRETS_LOCAL, "rb") as f:
        cfg = tomllib.load(f)["connections"]["supabase"]

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
    print(f"Aplicando {sql_file.name}...")
    cur.execute(sql_file.read_text(encoding="utf-8"))
    cur.close()
    conn.close()
    print("OK — migracao aplicada.")


if __name__ == "__main__":
    main()
