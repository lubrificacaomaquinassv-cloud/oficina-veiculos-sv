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
veiculos = sb.schema("oficina_veiculos").from_("veiculos").select("placa,modelo").limit(6).execute()
prest = sb.schema("oficina_veiculos").from_("prestadores").select("nome").execute()
mec = sb.schema("oficina_veiculos").from_("mecanicos").select("nome,responsavel").execute()
print(f"OK — {len(veiculos.data)} veiculos, {len(prest.data)} prestadores, {len(mec.data)} mecanicos")
