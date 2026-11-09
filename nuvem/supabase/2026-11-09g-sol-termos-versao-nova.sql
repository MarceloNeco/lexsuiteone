-- =====================================================================================
-- 2026-11-09g-sol-termos-versao-nova.sql  —  projeto solverone-app (Supabase)
-- Pedido nº 2 da conversa do RootifyONE (versão nova dos termos, administrada pelo RootifyONE). Desenho:
-- documentacao/DECISAO-B2B-QUEM-FAZ-O-QUE-2026-11-09.md, seção 5d. PRÉ-REQUISITO: 2026-11-09f.
--
-- O QUE FAZ:
--   1. sol_termos.reaceite_obrigatorio: quando a equipe publica versão nova, decide se os escritórios que aceitaram a
--      versão antiga precisam aceitar de novo (true = o programa volta a travar até o responsável aceitar a nova).
--      Para o termo de PESSOA a regra é fixa (decisão do dono): versão nova = aceita de novo, sempre.
--   2. admin_sol_termo_publicar com 6 parâmetros (os 5 de antes + p_reaceite boolean). A de 5 continua (reaceite = false).
--   3. sol_aceite_situacao devolve também reaceite_obrigatorio e vigente_desde.
-- APLICADO em 09/Nov/2026 pelo conector.
-- =====================================================================================
alter table public.sol_termos add column if not exists reaceite_obrigatorio boolean not null default false;
comment on column public.sol_termos.reaceite_obrigatorio is 'Escritórios que aceitaram versão anterior precisam aceitar a vigente de novo (trava do programa). Pessoa: sempre.';
-- DESFAZER: alter table public.sol_termos drop column reaceite_obrigatorio;

create or replace function public.admin_sol_termo_publicar(p_termo text, p_versao text, p_link text, p_hash_texto text, p_motivo text, p_reaceite boolean)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if length(coalesce(pg_catalog.btrim(p_motivo), '')) < 5 then raise exception 'Escreva o motivo (pelo menos 5 letras)'; end if;
  if coalesce(pg_catalog.btrim(p_versao), '') = '' or length(p_versao) > 20 then raise exception 'Versão inválida'; end if;
  select to_jsonb(t) into antes from public.sol_termos t where t.termo = p_termo;
  if antes is null then raise exception 'Termo não encontrado'; end if;
  if antes->>'versao' = pg_catalog.btrim(p_versao) then raise exception 'Essa já é a versão vigente'; end if;
  update public.sol_termos set versao = pg_catalog.btrim(p_versao), vigente_desde = pg_catalog.now(), link = coalesce(nullif(pg_catalog.btrim(p_link), ''), link),
         hash_texto = coalesce(nullif(pg_catalog.lower(pg_catalog.btrim(p_hash_texto)), ''), hash_texto),
         reaceite_obrigatorio = coalesce(p_reaceite, false), atualizado_em = pg_catalog.now()
   where termo = p_termo;
  select to_jsonb(t) into depois from public.sol_termos t where t.termo = p_termo;
  perform public.lab_registrar_log('sol_termo_publicar', null, depois || jsonb_build_object('motivo', pg_catalog.left(pg_catalog.btrim(p_motivo), 300)), antes);
  return depois;
end $$;
revoke all on function public.admin_sol_termo_publicar(text, text, text, text, text, boolean) from public, anon;
grant execute on function public.admin_sol_termo_publicar(text, text, text, text, text, boolean) to authenticated;
-- A versão de 5 parâmetros passa a chamar esta, com reaceite = false.
create or replace function public.admin_sol_termo_publicar(p_termo text, p_versao text, p_link text, p_hash_texto text, p_motivo text)
returns jsonb language sql security definer set search_path = '' as $$
  select public.admin_sol_termo_publicar(p_termo, p_versao, p_link, p_hash_texto, p_motivo, false);
$$;
revoke all on function public.admin_sol_termo_publicar(text, text, text, text, text) from public, anon;
grant execute on function public.admin_sol_termo_publicar(text, text, text, text, text) to authenticated;
-- DESFAZER: drop function if exists public.admin_sol_termo_publicar(text, text, text, text, text, boolean); reaplicar a de 5 de 2026-11-09f.

create or replace function public.sol_aceite_situacao(p_app text, p_licenca text, p_termo text, p_email text default null)
returns jsonb language sql security definer set search_path = '' stable as $$
  with t as (select versao, link, alcance, titulo, vigente_desde, reaceite_obrigatorio from public.sol_termos where termo = p_termo),
       a as (select a.versao, a.aceito_em, a.fuso, a.nome, a.email, 'ACE-' || pg_catalog.lpad(a.id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(a.hash, 6)) as protocolo
               from public.sol_aceites a
              where a.app = p_app and a.licenca = p_licenca and a.termo = p_termo and (p_email is null or a.email = pg_catalog.lower(p_email))
              order by a.aceito_em desc limit 1)
  select jsonb_build_object(
    'termo', p_termo, 'alcance', (select alcance from t), 'titulo', (select titulo from t),
    'versao_vigente', (select versao from t), 'vigente_desde', (select vigente_desde from t), 'link', (select link from t),
    'reaceite_obrigatorio', coalesce((select reaceite_obrigatorio from t), false),
    'aceito', exists (select 1 from a),
    'versao', (select versao from a), 'aceito_em', (select aceito_em from a), 'fuso', (select fuso from a),
    'nome', (select nome from a), 'email', (select email from a), 'protocolo', (select protocolo from a),
    'precisa_aceitar', not exists (select 1 from a where a.versao = (select versao from t)));
$$;
revoke all on function public.sol_aceite_situacao(text, text, text, text) from public, anon;
grant execute on function public.sol_aceite_situacao(text, text, text, text) to authenticated, service_role;
-- DESFAZER: reaplicar o bloco sol_aceite_situacao de 2026-11-09f.

-- Conferência (só leitura): tudo "true"
select
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'sol_termos' and column_name = 'reaceite_obrigatorio') as coluna_ok,
  (select count(*) = 2 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_sol_termo_publicar') as publicar_ok,
  (public.sol_aceite_situacao('radar-judicial', 'LEX-0000-0000', 'lexsuiteone-termos') ? 'reaceite_obrigatorio') as situacao_ok;
