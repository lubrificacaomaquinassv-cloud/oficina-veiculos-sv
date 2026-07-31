-- Financeiro — custos de OS veículos (peças, óleo, M.O. mecânico)
-- Sem hora parada de operador/motorista (leves e motos ficam na adm)

CREATE TABLE IF NOT EXISTS oficina_veiculos.financeiro_custos (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  os_id               UUID REFERENCES oficina_veiculos.ordens_servico(id) ON DELETE SET NULL,
  numero_os           TEXT NOT NULL,
  data                DATE NOT NULL DEFAULT CURRENT_DATE,
  categoria_veiculo   TEXT NOT NULL CHECK (categoria_veiculo IN ('LEVE', 'PESADO', 'MOTO')),
  placa               TEXT NOT NULL,
  mecanico            TEXT,
  item                TEXT NOT NULL CHECK (item IN (
    'PECAS', 'TROCA DE OLEO', 'M.O. MECANICO', 'OUTROS'
  )),
  tipo_manutencao     TEXT,
  descricao_peca      TEXT,
  nfe                 TEXT,
  id_fornecedor_sap   TEXT,
  quantidade          NUMERIC(10, 2) NOT NULL DEFAULT 1 CHECK (quantidade > 0),
  valor_unitario      NUMERIC(14, 2),
  valor               NUMERIC(14, 2) NOT NULL CHECK (valor >= 0),
  tempo_min_mecanico  INTEGER,
  custo_hora_mecanico NUMERIC(10, 2),
  custo_mo_mecanico   NUMERIC(14, 2),
  observacao          TEXT,
  criado_em           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fin_os ON oficina_veiculos.financeiro_custos (numero_os);
CREATE INDEX IF NOT EXISTS idx_fin_data ON oficina_veiculos.financeiro_custos (data DESC);
CREATE INDEX IF NOT EXISTS idx_fin_placa ON oficina_veiculos.financeiro_custos (placa);
CREATE INDEX IF NOT EXISTS idx_fin_categoria ON oficina_veiculos.financeiro_custos (categoria_veiculo);

CREATE OR REPLACE VIEW oficina_veiculos.v_custo_os_resumo AS
SELECT
  numero_os,
  categoria_veiculo,
  placa,
  max(mecanico) AS mecanico,
  count(*)::int AS qtd_lancamentos,
  coalesce(sum(valor) FILTER (WHERE item = 'PECAS'), 0)::numeric(14, 2) AS custo_pecas,
  coalesce(sum(valor) FILTER (WHERE item = 'TROCA DE OLEO'), 0)::numeric(14, 2) AS custo_oleo,
  coalesce(sum(valor) FILTER (WHERE item = 'M.O. MECANICO'), 0)::numeric(14, 2) AS custo_mo_mecanico,
  coalesce(sum(valor) FILTER (WHERE item = 'OUTROS'), 0)::numeric(14, 2) AS custo_outros,
  coalesce(sum(valor), 0)::numeric(14, 2) AS custo_total
FROM oficina_veiculos.financeiro_custos
GROUP BY numero_os, categoria_veiculo, placa;

CREATE OR REPLACE VIEW oficina_veiculos.v_custo_veiculo_mes AS
SELECT
  placa,
  categoria_veiculo,
  to_char(data, 'YYYY-MM') AS mes,
  count(*)::int AS qtd_lancamentos,
  coalesce(sum(valor), 0)::numeric(14, 2) AS custo_total
FROM oficina_veiculos.financeiro_custos
GROUP BY placa, categoria_veiculo, to_char(data, 'YYYY-MM');

ALTER TABLE oficina_veiculos.financeiro_custos ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS ov_fin_custos_all ON oficina_veiculos.financeiro_custos;
CREATE POLICY ov_fin_custos_all ON oficina_veiculos.financeiro_custos
  FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

GRANT ALL ON oficina_veiculos.financeiro_custos TO anon, authenticated, service_role;
GRANT SELECT ON oficina_veiculos.v_custo_os_resumo TO anon, authenticated, service_role;
GRANT SELECT ON oficina_veiculos.v_custo_veiculo_mes TO anon, authenticated, service_role;
