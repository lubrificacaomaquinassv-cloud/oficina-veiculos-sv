-- OFICINA VEÍCULOS — Schema Supabase (Postgres)
-- Projeto: azhpxhrwhegfysoeqmft (dados_controladoria_sv)
-- Rodar no SQL Editor do Supabase
-- Depois: Settings > API > Exposed schemas → adicionar "oficina_veiculos"

CREATE SCHEMA IF NOT EXISTS oficina_veiculos;

-- ── Prestadores de serviço (terceiros) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS oficina_veiculos.prestadores (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nome        TEXT NOT NULL UNIQUE,
  ativo       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Mecânicos (custo/hora para financeiro futuro) ───────────────────────────
CREATE TABLE IF NOT EXISTS oficina_veiculos.mecanicos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nome        TEXT NOT NULL UNIQUE,
  custo_hora  NUMERIC(10, 2),
  responsavel BOOLEAN NOT NULL DEFAULT FALSE,
  ativo       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Veículos (leve, pesado, moto) ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS oficina_veiculos.veiculos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  placa       TEXT NOT NULL,
  modelo      TEXT NOT NULL,
  categoria   TEXT NOT NULL CHECK (categoria IN ('LEVE', 'PESADO', 'MOTO')),
  ativo       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (placa)
);

CREATE INDEX IF NOT EXISTS idx_veiculos_categoria ON oficina_veiculos.veiculos (categoria);
CREATE INDEX IF NOT EXISTS idx_veiculos_ativo ON oficina_veiculos.veiculos (ativo) WHERE ativo = TRUE;

-- ── Ordens de serviço ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS oficina_veiculos.ordens_servico (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_os                 TEXT NOT NULL UNIQUE,
  categoria_veiculo         TEXT NOT NULL CHECK (categoria_veiculo IN ('LEVE', 'PESADO', 'MOTO')),
  veiculo_id                UUID REFERENCES oficina_veiculos.veiculos(id),
  placa                     TEXT NOT NULL,
  modelo                    TEXT,
  horimetro_km              NUMERIC(14, 1),
  mecanico                  TEXT NOT NULL,
  prestador_id              UUID REFERENCES oficina_veiculos.prestadores(id),
  prestador_nome            TEXT,
  tipo_servico              TEXT NOT NULL CHECK (tipo_servico IN (
    'ELETRICO', 'HIDRAULICO', 'SUSPENSAO', 'FREIO',
    'CARDAN', 'REVISAO GERAL', 'TROCA DE OLEO'
  )),
  hora_entrada              TEXT,
  hora_saida                TEXT,
  tempo_min                 INTEGER,
  operador                  TEXT,
  status                    TEXT NOT NULL DEFAULT 'PENDENTE'
                            CHECK (status IN ('PENDENTE', 'FINALIZADO')),
  descricao                 TEXT,
  observacao                TEXT,
  odometro_ultima_troca     NUMERIC(14, 1),
  created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_os_status ON oficina_veiculos.ordens_servico (status);
CREATE INDEX IF NOT EXISTS idx_os_categoria ON oficina_veiculos.ordens_servico (categoria_veiculo);
CREATE INDEX IF NOT EXISTS idx_os_created ON oficina_veiculos.ordens_servico (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_os_prestador ON oficina_veiculos.ordens_servico (prestador_id);
CREATE INDEX IF NOT EXISTS idx_os_tipo_servico ON oficina_veiculos.ordens_servico (tipo_servico);

-- ── Views para painel ───────────────────────────────────────────────────────
CREATE OR REPLACE VIEW oficina_veiculos.v_painel_resumo AS
SELECT
  count(*)::int AS total_os,
  count(*) FILTER (WHERE status = 'PENDENTE')::int AS pendentes,
  count(*) FILTER (WHERE status = 'FINALIZADO')::int AS finalizadas,
  count(*) FILTER (WHERE categoria_veiculo = 'LEVE')::int AS os_leve,
  count(*) FILTER (WHERE categoria_veiculo = 'PESADO')::int AS os_pesado,
  count(*) FILTER (WHERE categoria_veiculo = 'MOTO')::int AS os_moto
FROM oficina_veiculos.ordens_servico;

CREATE OR REPLACE VIEW oficina_veiculos.v_prestadores_ranking AS
SELECT
  coalesce(prestador_nome, 'OFICINA INTERNA — SV') AS prestador,
  count(*)::int AS qtd_os
FROM oficina_veiculos.ordens_servico
GROUP BY coalesce(prestador_nome, 'OFICINA INTERNA — SV')
ORDER BY count(*) DESC;

CREATE OR REPLACE VIEW oficina_veiculos.v_tipos_servico_ranking AS
SELECT
  tipo_servico,
  count(*)::int AS qtd_os
FROM oficina_veiculos.ordens_servico
GROUP BY tipo_servico
ORDER BY count(*) DESC;

-- ── Dados iniciais: prestadores ─────────────────────────────────────────────
INSERT INTO oficina_veiculos.prestadores (nome) VALUES
  ('L R BRAGA ME'),
  ('OSMAR BORGES JUNIOR'),
  ('MARCELO CHIYOJI SAITO'),
  ('ROCHA AUTO ELETRICA E BORRACHARIA LTDA'),
  ('ANDREIA DA ROCHA SILVA'),
  ('ALEXSANDRO TEIXEIRA DA PAZ EIRELI - ME'),
  ('INJETORA DIESEL BATAGUASSU LTDA'),
  ('ROMERA E SANTANA SERVICOS LTDA'),
  ('SAN JOSE EQUIPAMENTOS PARA AUTOS LTDA - ME'),
  ('SILVA & CIA LTDA'),
  ('VANUZA CORREA DOS SANTOS PEREIRA'),
  ('RITA DE CASSIA MARQUES DE SOUZA PAIAO'),
  ('SMS ELETRO DIESEL E ELETRICA LTDA'),
  ('JOAO PAULO DA SILVA LIMA')
ON CONFLICT (nome) DO NOTHING;

-- ── Mecânico responsável ────────────────────────────────────────────────────
INSERT INTO oficina_veiculos.mecanicos (nome, responsavel, custo_hora) VALUES
  ('Andre Luis Brito Gomes', TRUE, NULL)
ON CONFLICT (nome) DO UPDATE SET responsavel = TRUE;

-- ── Veículos leves (frota atual) ─────────────────────────────────────────────
INSERT INTO oficina_veiculos.veiculos (placa, modelo, categoria) VALUES
  ('SMC7D44', 'KWID', 'LEVE'),
  ('SLZ8I55', 'KWID', 'LEVE'),
  ('SMA6B13', 'KWID', 'LEVE'),
  ('AGH7924', 'KWID', 'LEVE'),
  ('OOH4A79', 'KWID', 'LEVE'),
  ('TMH8J55', 'KWID', 'LEVE')
ON CONFLICT (placa) DO NOTHING;

-- ── Frota pesada (linha pesada / terceiros) ─────────────────────────────────
INSERT INTO oficina_veiculos.veiculos (placa, modelo, categoria) VALUES
  ('3385', 'COMBOIO', 'PESADO'),
  ('3315', 'MB 2426', 'PESADO'),
  ('3355', 'MB 2638 | MBN3J38', 'PESADO'),
  ('3383', 'MB 2638 | MBL7G35', 'PESADO'),
  ('3267', 'MB 2831', 'PESADO'),
  ('3381', 'MB 3340', 'PESADO'),
  ('3316', 'MB 1016', 'PESADO'),
  ('3349', 'MB 1620', 'PESADO'),
  ('3404', 'MB 1719', 'PESADO')
ON CONFLICT (placa) DO UPDATE SET
  modelo = EXCLUDED.modelo,
  categoria = EXCLUDED.categoria,
  ativo = TRUE;

-- ── RLS ─────────────────────────────────────────────────────────────────────
ALTER TABLE oficina_veiculos.prestadores ENABLE ROW LEVEL SECURITY;
ALTER TABLE oficina_veiculos.mecanicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE oficina_veiculos.veiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE oficina_veiculos.ordens_servico ENABLE ROW LEVEL SECURITY;

DO $$ DECLARE t TEXT; BEGIN
  FOREACH t IN ARRAY ARRAY['prestadores', 'mecanicos', 'veiculos', 'ordens_servico'] LOOP
    EXECUTE format('DROP POLICY IF EXISTS ov_%s_all ON oficina_veiculos.%s', t, t);
    EXECUTE format(
      'CREATE POLICY ov_%s_all ON oficina_veiculos.%s FOR ALL TO anon, authenticated USING (true) WITH CHECK (true)',
      t, t
    );
  END LOOP;
END $$;

GRANT USAGE ON SCHEMA oficina_veiculos TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA oficina_veiculos TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA oficina_veiculos TO anon, authenticated, service_role;
GRANT SELECT ON oficina_veiculos.v_painel_resumo TO anon, authenticated, service_role;
GRANT SELECT ON oficina_veiculos.v_prestadores_ranking TO anon, authenticated, service_role;
GRANT SELECT ON oficina_veiculos.v_tipos_servico_ranking TO anon, authenticated, service_role;
