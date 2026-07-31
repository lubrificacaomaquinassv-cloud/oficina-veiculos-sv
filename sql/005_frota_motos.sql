-- Motocicletas e quadriciclos — cadastro inicial
INSERT INTO oficina_veiculos.veiculos (placa, modelo, categoria) VALUES
  ('3347', 'CRF', 'MOTO'),
  ('3353', 'CRF', 'MOTO'),
  ('3373', 'CRF', 'MOTO'),
  ('3392', 'XRE 300', 'MOTO'),
  ('3401', 'XRE 160', 'MOTO'),
  ('3379', 'XRE 190', 'MOTO'),
  ('3391', 'QUADRICICLO', 'MOTO'),
  ('3367', 'XRE 300', 'MOTO'),
  ('3407', 'QUADRICICLO', 'MOTO'),
  ('3408', 'QUADRICICLO', 'MOTO')
ON CONFLICT (placa) DO UPDATE SET
  modelo = EXCLUDED.modelo,
  categoria = EXCLUDED.categoria,
  ativo = TRUE;
