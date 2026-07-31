# Oficina Veículos SV

App Streamlit para lançamento de Ordens de Serviço — veículos leves, pesados e motos.

## Início rápido

```bash
pip install -r requirements.txt
streamlit run oficina_veiculos_app.py
```

1. Aplique `sql/001_oficina_veiculos_schema.sql` no Supabase
2. Exponha o schema `oficina_veiculos` em Settings → API
3. Configure Secrets (`SUPABASE_URL`, `SUPABASE_KEY`, `APP_PIN`)

Detalhes em [LEIA-ME.txt](LEIA-ME.txt) e [DEPLOY_STREAMLIT.txt](DEPLOY_STREAMLIT.txt).
