-- =====================================================================================
-- 2026-11-09b-sol-aceites.sql  —  projeto solverone-app (Supabase)
-- Aceite eletrônico dos termos (LexSuiteONE e qualquer produto da SolverONE), pedido do dono em 09/Nov/2026.
-- Desenho: documentacao/DESENHO-ACEITE-TERMOS.md. PRÉ-REQUISITO: 2026-11-09-sol-retorno-e-lex-auditoria.sql.
--
-- O QUE FAZ:
--   1. sol_aceites: um registro por aceite (app, licença, documento e versão aceitos, hash do texto mostrado, nome
--      completo, e-mail, data e hora, resumo do IP e do navegador). Nunca apagado nem editado (trigger).
--   2. sol_aceite_registrar(p): chamada pela página pública de aceite com a chave publicável (anon, DE PROPÓSITO):
--      valida app, licença, nome, e-mail, versão e hash; limita 5 por hora por e-mail e 30 por dia por licença;
--      grava e devolve o protocolo.
--   3. admin_sol_aceites(app, licenca): a equipe vê os aceites (RootifyONE).
--   4. sol_tem_aceite(app, licenca, termo): usada pela lex-conta (service_role) para dizer ao programa se há aceite.
--   5. sol_aceite_contexto(app, licenca): a página mostra o nome do escritório da licença ("em nome de KR Law…"),
--      para o aceite dizer por quem é dado. Anon, só o nome, com limite de 30 consultas por hora por licença.
-- APLICADO em 09/Nov/2026 pelo conector, com o "pode aplicar" do dono (conferência toda "true"). O advisor do Supabase
-- avisa "anon pode executar função security definer" para sol_aceite_registrar e sol_aceite_contexto: é por desenho
-- (página pública), com validação de licença e limite de chamadas dentro da função. Cada bloco tem o DESFAZER em comentário.
-- =====================================================================================

create table if not exists public.sol_aceites (
  id         bigint generated always as identity primary key,
  app        text not null references public.sol_apps(codigo),
  licenca    text not null check (length(licenca) between 3 and 40),
  termo      text not null check (termo ~ '^[a-z0-9-]{3,60}$'),
  versao     text not null check (length(versao) between 1 and 20),
  hash       text not null check (hash ~ '^[0-9a-f]{64}$'),
  nome       text not null check (length(nome) between 5 and 120),
  email      text not null check (email = lower(email) and email like '%_@_%._%'),
  aceito_em  timestamptz not null default now(),
  ip_resumo  text,
  navegador  text,
  origem     text not null default 'email' check (origem in ('email', 'site', 'programa'))
);
comment on table public.sol_aceites is 'Aceite eletrônico de termos (assinatura eletrônica simples): quem aceitou, o quê (documento, versão e hash do texto), quando, de onde (IP resumido). Nunca apagado nem editado.';
create index if not exists sol_aceites_app_licenca on public.sol_aceites (app, licenca, aceito_em desc);
alter table public.sol_aceites enable row level security;
revoke all on public.sol_aceites from public, anon, authenticated;
grant select, insert on public.sol_aceites to service_role;
-- DESFAZER: drop table if exists public.sol_aceites;

create or replace function public.sol_aceites_imutavel()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  raise exception 'Registro de aceite não se altera nem se apaga' using errcode = 'P0001';
end $$;
revoke all on function public.sol_aceites_imutavel() from public, anon, authenticated;
grant execute on function public.sol_aceites_imutavel() to service_role;
do $$ begin
  if not exists (select 1 from pg_trigger where tgname = 'sol_aceites_sem_update_delete') then
    create trigger sol_aceites_sem_update_delete before update or delete on public.sol_aceites
      for each row execute function public.sol_aceites_imutavel();
  end if;
end $$;
-- DESFAZER: drop trigger if exists sol_aceites_sem_update_delete on public.sol_aceites; drop function if exists public.sol_aceites_imutavel();

create or replace function public.sol_aceite_registrar(p jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  v_app text := pg_catalog.left(coalesce(p->>'app', ''), 40);
  v_lic text := pg_catalog.upper(pg_catalog.btrim(coalesce(p->>'licenca', '')));
  v_termo text := pg_catalog.left(coalesce(p->>'termo', ''), 60);
  v_versao text := pg_catalog.left(coalesce(p->>'versao', ''), 20);
  v_hash text := pg_catalog.lower(pg_catalog.left(coalesce(p->>'hash', ''), 64));
  v_nome text := pg_catalog.regexp_replace(pg_catalog.btrim(coalesce(p->>'nome', '')), '\s+', ' ', 'g');
  v_email text := pg_catalog.lower(pg_catalog.btrim(coalesce(p->>'email', '')));
  v_nav text := pg_catalog.left(coalesce(p->>'navegador', ''), 120);
  v_ip text; v_id bigint; v_quando timestamptz;
begin
  if not exists (select 1 from public.sol_apps a where a.codigo = v_app and a.ativo) then raise exception 'App desconhecido' using errcode = 'P0001'; end if;
  if v_app = 'radar-judicial' and not exists (select 1 from public.lex_contas c where c.codigo = v_lic) then raise exception 'Código de cliente desconhecido' using errcode = 'P0001'; end if;
  if v_termo !~ '^[a-z0-9-]{3,60}$' or v_versao = '' or v_hash !~ '^[0-9a-f]{64}$' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  if length(v_nome) < 5 or v_nome !~ '\s' then raise exception 'Escreva o nome completo (nome e sobrenome)' using errcode = 'P0001'; end if;
  if v_email !~ '^[^@[:space:]]{1,64}@[^@[:space:]]+\.[^@[:space:]]{2,}$' then raise exception 'Confira o e-mail' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:email:' || v_email, 5, 3600) then raise exception 'Muitas tentativas; tente mais tarde' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:lic:' || v_lic, 30, 86400) then raise exception 'Muitas tentativas para esta licença hoje' using errcode = 'P0001'; end if;
  -- IP resumido: só o começo (3 blocos do IPv4 ou 4 do IPv6), suficiente para prova e sem identificar o aparelho.
  begin
    v_ip := pg_catalog.split_part(coalesce(pg_catalog.current_setting('request.headers', true)::jsonb->>'x-forwarded-for', ''), ',', 1);
    v_ip := pg_catalog.btrim(v_ip);
    if v_ip like '%.%' then v_ip := pg_catalog.regexp_replace(v_ip, '\.\d+$', '.x');
    elsif v_ip like '%:%' then v_ip := pg_catalog.array_to_string((pg_catalog.string_to_array(v_ip, ':'))[1:4], ':') || ':…';
    else v_ip := null; end if;
  exception when others then v_ip := null; end;
  insert into public.sol_aceites (app, licenca, termo, versao, hash, nome, email, ip_resumo, navegador, origem)
  values (v_app, v_lic, v_termo, v_versao, v_hash, pg_catalog.left(v_nome, 120), v_email, v_ip, nullif(v_nav, ''),
          case when p->>'origem' in ('site', 'programa') then p->>'origem' else 'email' end)
  returning id, aceito_em into v_id, v_quando;
  return jsonb_build_object('ok', true, 'protocolo', 'ACE-' || pg_catalog.lpad(v_id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(v_hash, 6)), 'aceito_em', v_quando);
end $$;
revoke all on function public.sol_aceite_registrar(jsonb) from public;
grant execute on function public.sol_aceite_registrar(jsonb) to anon, authenticated, service_role;   -- anon de propósito: página pública de aceite, com limites
-- DESFAZER: drop function if exists public.sol_aceite_registrar(jsonb);

create or replace function public.sol_aceite_contexto(p_app text, p_licenca text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_lic text := pg_catalog.upper(pg_catalog.btrim(coalesce(p_licenca, ''))); v_nome text;
begin
  if not public.lex_contar_chamada('aceite:ctx:' || v_lic, 30, 3600) then return jsonb_build_object('ok', false); end if;
  if p_app = 'radar-judicial' then select c.escritorio into v_nome from public.lex_contas c where c.codigo = v_lic; end if;
  if v_nome is null then return jsonb_build_object('ok', false); end if;
  return jsonb_build_object('ok', true, 'escritorio', v_nome,
    'ja_aceito', exists (select 1 from public.sol_aceites a where a.app = p_app and a.licenca = v_lic and a.termo = 'lexsuiteone-termos'));
end $$;
revoke all on function public.sol_aceite_contexto(text, text) from public;
grant execute on function public.sol_aceite_contexto(text, text) to anon, authenticated, service_role;   -- anon de propósito: só devolve o nome do escritório
-- DESFAZER: drop function if exists public.sol_aceite_contexto(text, text);

create or replace function public.sol_tem_aceite(p_app text, p_licenca text, p_termo text)
returns jsonb language sql security definer set search_path = '' stable as $$
  select coalesce((select jsonb_build_object('aceito', true, 'versao', a.versao, 'aceito_em', a.aceito_em, 'nome', a.nome)
                     from public.sol_aceites a where a.app = p_app and a.licenca = p_licenca and a.termo = p_termo
                    order by a.aceito_em desc limit 1), jsonb_build_object('aceito', false));
$$;
revoke all on function public.sol_tem_aceite(text, text, text) from public, anon, authenticated;
grant execute on function public.sol_tem_aceite(text, text, text) to service_role;
-- DESFAZER: drop function if exists public.sol_tem_aceite(text, text, text);

create or replace function public.admin_sol_aceites(p_app text, p_licenca text default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((select jsonb_agg(to_jsonb(a) order by a.aceito_em desc)
                     from (select id, app, licenca, termo, versao, hash, nome, email, aceito_em, ip_resumo, navegador, origem
                             from public.sol_aceites where app = p_app and (p_licenca is null or licenca = p_licenca) order by aceito_em desc limit 200) a), '[]'::jsonb);
end $$;
revoke all on function public.admin_sol_aceites(text, text) from public, anon;
grant execute on function public.admin_sol_aceites(text, text) to authenticated;
-- DESFAZER: drop function if exists public.admin_sol_aceites(text, text);

-- Conferência (só leitura): tudo "true"
select
  exists (select 1 from information_schema.tables where table_schema = 'public' and table_name = 'sol_aceites') as tabela_ok,
  exists (select 1 from pg_trigger where tgname = 'sol_aceites_sem_update_delete') as imutavel_ok,
  (select count(*) = 4 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public'
     and p.proname in ('sol_aceite_registrar', 'sol_aceite_contexto', 'sol_tem_aceite', 'admin_sol_aceites')) as funcoes_ok,
  not exists (select 1 from information_schema.role_table_grants where table_schema = 'public' and table_name = 'sol_aceites' and grantee in ('anon', 'authenticated')) as sem_acesso_direto_ok;
