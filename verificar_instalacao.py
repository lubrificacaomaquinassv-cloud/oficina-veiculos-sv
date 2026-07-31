"""Verifica conexao com schema oficina_veiculos (secrets local)."""
from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from supabase import create_client

ROOT = Path(__file__).resolve().parent
with open(ROOT / ".streamlit" / "secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

sb = create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_KEY"])
veiculos = sb.schema("oficina_veiculos").from_("veiculos").select("placa,modelo,categoria").eq("ativo", True).order("categoria").order("placa").execute()
prest = sb.schema("oficina_veiculos").from_("prestadores").select("nome").execute()
mec = sb.schema("oficina_veiculos").from_("mecanicos").select("nome,responsavel").execute()
leves = [v for v in veiculos.data if v["categoria"] == "LEVE"]
pesados = [v for v in veiculos.data if v["categoria"] == "PESADO"]
print(f"OK — {len(leves)} leves, {len(pesados)} pesados, {len(prest.data)} prestadores, {len(mec.data)} mecanicos")
