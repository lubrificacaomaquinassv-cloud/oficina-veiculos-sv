-- Frota pesada (linha pesada) — cadastro inicial
-- Rodar no Supabase SQL Editor ou: python aplicar_migracao.py 004

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
