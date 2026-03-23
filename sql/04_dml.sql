INSERT INTO users (login, hashed_password, created_at) VALUES
    ('alexandra', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT),
    ('testuser',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT),
    ('ivan',      '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT),
    ('maria',     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT);


DO $$
DECLARE
  r record;
BEGIN
  FOR r IN
    SELECT
      c.relname AS table_name,
      a.attname AS column_name,
      pg_get_serial_sequence(format('%I.%I', n.nspname, c.relname), a.attname) AS seq_name
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    JOIN pg_attribute a ON a.attrelid = c.oid
    JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
    WHERE c.relkind = 'r'
      AND n.nspname = 'public'
      AND pg_get_serial_sequence(format('%I.%I', n.nspname, c.relname), a.attname) IS NOT NULL
  LOOP
    EXECUTE format(
      'SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %I.%I), 1), true)',
      r.seq_name, r.column_name, 'public', r.table_name
    );
  END LOOP;
END $$;