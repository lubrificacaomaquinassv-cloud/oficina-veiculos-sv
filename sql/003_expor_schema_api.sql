-- Expor schema oficina_veiculos no PostgREST (Supabase API)
ALTER ROLE authenticator SET pgrst.db_schemas = 'public, graphql_public, oficina_veiculos';
NOTIFY pgrst, 'reload config';
NOTIFY pgrst, 'reload schema';
