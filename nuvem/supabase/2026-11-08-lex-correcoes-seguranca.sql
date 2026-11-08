-- =====================================================================================
-- 2026-11-08-lex-correcoes-seguranca.sql  —  projeto solverone-app (Supabase)
-- RADAR JUDICIAL: correções de segurança e robustez do que foi aplicado em 08/Nov/2026 de manhã
-- (lex-licencas.sql, lex-admin.sql). Revisão em documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md.
--
-- O QUE FAZ (e só isto):
--   1. lex_criar_conta com search_path = '' e nomes qualificados (regra C10). Mesmo comportamento.
--   2. lex_contas.max_computadores (padrão 20) + trigger que recusa instalação além de max_computadores + 5.
--   3. Trigger que recusa lex_registros quando já houver 600 na última hora (freio de emergência).
--   4. Índices para os limites por chamada.
--   5. Job do pg_cron: apaga lex_registros com mais de 90 dias (só erros técnicos).
--   6. Conferência no fim.
-- O QUE NÃO FAZ: não mexe em dado, não altera a função lex-conta, não cria acesso novo, não toca spatial_ref_sys.
--
-- COMO APLICAR (só depois de o dono revisar): supabase.com → projeto solverone-app → SQL Editor → New query →
-- colar este arquivo inteiro → Run. Pode rodar de novo sem estragar nada. Nenhuma chave, senha ou dado de pessoa aqui.
-- Cada bloco tem o comando que DESFAZ, em comentário logo abaixo.
-- =====================================================================================

-- ---------------------------------------------------------------------
-- 1. lex_criar_conta: mesma lógica, search_path fixo e nomes qualificados
-- ---------------------------------------------------------------------
create or replace function public.lex_criar_conta(p_escritorio text, p_validade date default null)
returns text language plpgsql security definer set search_path = '' as $$
declare
  alfabeto constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  bytes bytea; corpo text; novo text;
begin
  if coalesce(pg_catalog.btrim(p_escritorio), '') = '' then
    raise exception 'Informe o nome do escritório';
  end if;
  loop
    bytes := extensions.gen_random_bytes(8);
    corpo := '';
    for i in 0..7 loop
      corpo := corpo || pg_catalog.substr(alfabeto, 1 + (pg_catalog.get_byte(bytes, i) % 32), 1);
    end loop;
    novo := 'LEX-' || pg_catalog.substr(corpo, 1, 4) || '-' || pg_catalog.substr(corpo, 5, 4);
    begin
      insert into public.lex_contas (codigo, escritorio, validade) values (novo, pg_catalog.btrim(p_escritorio), p_validade);
      return novo;
    exception when unique_violation then
      -- código repetido (raríssimo): tenta outro
    end;
  end loop;
end $$;
revoke all on function public.lex_criar_conta(text, date) from public, anon, authenticated;
grant execute on function public.lex_criar_conta(text, date) to service_role;   -- só a equipe, via admin_lex_criar; o verificador exige um GRANT explícito
-- DESFAZER: reaplicar o bloco "lex_criar_conta" de nuvem/supabase/lex-licencas.sql (versão com search_path = public, extensions).

-- ---------------------------------------------------------------------
-- 2. Teto de instalações por licença
--    max_computadores: quantos computadores a equipe espera naquela licença (ajustável na ficha, 0.8).
--    O trigger recusa a linha quando já há max_computadores + 5 (folga para reinstalação).
-- ---------------------------------------------------------------------
alter table public.lex_contas
  add column if not exists max_computadores smallint not null default 20
  check (max_computadores between 1 and 500);
comment on column public.lex_contas.max_computadores is 'Computadores esperados nesta licença. O banco recusa instalação nova a partir de max_computadores + 5.';
-- DESFAZER: alter table public.lex_contas drop column max_computadores;

create or replace function public.lex_teto_instalacoes()
returns trigger language plpgsql security definer set search_path = '' as $$
declare v_max smallint; v_qtd integer;
begin
  select c.max_computadores into v_max from public.lex_contas c where c.codigo = new.codigo;
  if v_max is null then
    raise exception 'Licença desconhecida' using errcode = '23503';
  end if;
  select count(*) into v_qtd from public.lex_instalacoes i where i.codigo = new.codigo;
  if v_qtd >= v_max + 5 then
    raise exception 'Esta licença já tem o máximo de computadores (%). Fale com judicial@solverone.com.br.', v_max
      using errcode = 'P0001';
  end if;
  return new;
end $$;
revoke all on function public.lex_teto_instalacoes() from public, anon, authenticated;
grant execute on function public.lex_teto_instalacoes() to service_role;   -- função de trigger: ninguém chama direto
drop trigger if exists lex_instalacoes_teto on public.lex_instalacoes;
create trigger lex_instalacoes_teto before insert on public.lex_instalacoes
  for each row execute function public.lex_teto_instalacoes();
-- DESFAZER: drop trigger if exists lex_instalacoes_teto on public.lex_instalacoes; drop function if exists public.lex_teto_instalacoes();

-- ---------------------------------------------------------------------
-- 3. Freio de emergência em lex_registros: no máximo 600 linhas por hora no total
--    (a função lex-conta já limita 30 por hora por instalação; isto segura o caso de muitas instalações inventadas).
-- ---------------------------------------------------------------------
create or replace function public.lex_freio_registros()
returns trigger language plpgsql security definer set search_path = '' as $$
declare v_qtd integer;
begin
  select count(*) into v_qtd from public.lex_registros r where r.criado_em > pg_catalog.now() - interval '1 hour';
  if v_qtd >= 600 then
    raise exception 'Muitos registros na última hora; tente mais tarde.' using errcode = 'P0001';
  end if;
  return new;
end $$;
revoke all on function public.lex_freio_registros() from public, anon, authenticated;
grant execute on function public.lex_freio_registros() to service_role;   -- função de trigger: ninguém chama direto
drop trigger if exists lex_registros_freio on public.lex_registros;
create trigger lex_registros_freio before insert on public.lex_registros
  for each row execute function public.lex_freio_registros();
-- DESFAZER: drop trigger if exists lex_registros_freio on public.lex_registros; drop function if exists public.lex_freio_registros();

-- ---------------------------------------------------------------------
-- 4. Índices para os limites por chamada (lex-conta v4) e para os triggers acima
-- ---------------------------------------------------------------------
create index if not exists lex_instalacoes_codigo on public.lex_instalacoes (codigo);
create index if not exists lex_eventos_instalacao_criado on public.lex_eventos (instalacao, criado_em desc);
create index if not exists lex_registros_instalacao_criado on public.lex_registros (instalacao, criado_em desc);
-- DESFAZER: drop index if exists public.lex_instalacoes_codigo, public.lex_eventos_instalacao_criado, public.lex_registros_instalacao_criado;

-- ---------------------------------------------------------------------
-- 5. Retenção dos erros técnicos: 90 dias, todo dia às 07:10 UTC (04:10 em Brasília).
--    Só roda onde o pg_cron existe (no Supabase existe; num Postgres de teste, pula).
-- ---------------------------------------------------------------------
do $$
begin
  if exists (select 1 from pg_catalog.pg_extension where extname = 'pg_cron') then
    perform cron.unschedule(jobid) from cron.job where jobname = 'lex-registros-retencao-90d';
    perform cron.schedule('lex-registros-retencao-90d', '10 7 * * *',
      $job$ delete from public.lex_registros where criado_em < now() - interval '90 days' $job$);
  end if;
end $$;
-- DESFAZER: select cron.unschedule(jobid) from cron.job where jobname = 'lex-registros-retencao-90d';

-- ---------------------------------------------------------------------
-- 6. Conferência (só leitura): tudo deve vir "true"
-- ---------------------------------------------------------------------
select
  (select pg_catalog.array_to_string(p.proconfig, ',') in ('search_path=', 'search_path=""') from pg_catalog.pg_proc p
     join pg_catalog.pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public' and p.proname = 'lex_criar_conta')                                   as criar_conta_search_path_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public'
            and table_name = 'lex_contas' and column_name = 'max_computadores')                     as max_computadores_ok,
  exists (select 1 from pg_catalog.pg_trigger where tgname = 'lex_instalacoes_teto' and not tgisinternal) as teto_instalacoes_ok,
  exists (select 1 from pg_catalog.pg_trigger where tgname = 'lex_registros_freio' and not tgisinternal)   as freio_registros_ok,
  (select count(*) = 3 from pg_catalog.pg_indexes where schemaname = 'public'
     and indexname in ('lex_instalacoes_codigo', 'lex_eventos_instalacao_criado', 'lex_registros_instalacao_criado')) as indices_ok,
  (not exists (select 1 from pg_catalog.pg_extension where extname = 'pg_cron')
     or exists (select 1 from pg_catalog.pg_class c join pg_catalog.pg_namespace n on n.oid = c.relnamespace
                 where n.nspname = 'cron' and c.relname = 'job'))                                   as retencao_ok,   -- no Supabase: confira também "select jobname from cron.job" (deve listar lex-registros-retencao-90d)
  not exists (select 1 from information_schema.role_table_grants
               where table_schema = 'public' and table_name like 'lex\_%' and grantee in ('anon', 'authenticated')) as sem_acesso_direto_ok;
