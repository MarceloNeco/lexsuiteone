-- =====================================================================================
-- 2026-11-12-sol-termos-versoes.sql  —  projeto solverone-app (Supabase)
-- Pedido da Produto "Aceite dos termos e e-mail de boas-vindas" (12/Nov) + diretriz do dono (12/Nov, ponto 4 da definição
-- de pronto): guardar cada versão do texto dos termos; novo aceite só em mudança material; mostrar a versão aceita e as
-- anteriores com link para o texto de cada uma. Desenho: documentacao/DESENHO-TERMOS-UNICO-2026-11-11.md, seção 5e.
--
-- O QUE FAZ:
--   1. sol_termos_versoes: histórico imutável (termo, versão, desde, link do texto, hash, material, motivo). Preenchida com a
--      versão vigente de hoje (1.0, texto em judicial.solverone.com.br/termos/v1.0.html, cópia estática da página).
--   2. admin_sol_termo_publicar (6 parâmetros) passa a gravar a versão nova no histórico; p_reaceite = "mudança material".
--   3. sol_aceite_situacao: precisa_aceitar só quando a versão vigente é material (reaceite_obrigatorio) e o aceite é de
--      versão anterior, ou quando nunca houve aceite. Mudança editorial (material: não) não pede novo aceite a ninguém.
--   4. sol_termos_versoes_lista(p_termo): lista para o programa (via lex-conta) e para o RootifyONE.
-- Retenção (pesquisa da Produto, 12/Nov): versões e aceites ficam pelo contrato + 5 anos; nada se apaga por rotina.
-- APLICADO em 12/Nov/2026 pelo conector.
-- =====================================================================================
create table if not exists public.sol_termos_versoes (
  id            bigint generated always as identity primary key,
  termo         text not null references public.sol_termos(termo),
  versao        text not null check (length(versao) between 1 and 20),
  vigente_desde timestamptz not null default now(),
  link          text not null,
  hash_texto    text check (hash_texto is null or hash_texto ~ '^[0-9a-f]{64}$'),
  material      boolean not null default true,
  motivo        text,
  publicado_por text,
  unique (termo, versao)
);
comment on table public.sol_termos_versoes is 'Histórico imutável das versões de cada termo: texto (link), hash, se a mudança foi material (pede novo aceite) e motivo. Guardado pelo contrato + 5 anos.';
alter table public.sol_termos_versoes enable row level security;
revoke all on public.sol_termos_versoes from public, anon, authenticated;
grant select, insert on public.sol_termos_versoes to service_role;
insert into public.sol_termos_versoes (termo, versao, vigente_desde, link, hash_texto, material, motivo, publicado_por)
select termo, versao, vigente_desde, 'https://judicial.solverone.com.br/termos/v' || versao || '.html', hash_texto, true,
       'Primeira versão publicada (aprovada pelo dono e pelo Leandro em 11/Nov)', 'arquitetura'
  from public.sol_termos where termo = 'lexsuiteone-termos'
on conflict (termo, versao) do nothing;
-- DESFAZER: drop table if exists public.sol_termos_versoes;

create or replace function public.sol_termos_versoes_imutavel()
returns trigger language plpgsql security definer set search_path = '' as $$
begin raise exception 'Versão de termo não se altera nem se apaga' using errcode = 'P0001'; end $$;
revoke all on function public.sol_termos_versoes_imutavel() from public, anon, authenticated;
grant execute on function public.sol_termos_versoes_imutavel() to service_role;
do $$ begin
  if not exists (select 1 from pg_trigger where tgname = 'sol_termos_versoes_sem_update_delete') then
    create trigger sol_termos_versoes_sem_update_delete before update or delete on public.sol_termos_versoes
      for each row execute function public.sol_termos_versoes_imutavel();
  end if;
end $$;

create or replace function public.admin_sol_termo_publicar(p_termo text, p_versao text, p_link text, p_hash_texto text, p_motivo text, p_reaceite boolean)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb; v_link text;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if length(coalesce(pg_catalog.btrim(p_motivo), '')) < 5 then raise exception 'Escreva o motivo (pelo menos 5 letras)'; end if;
  if coalesce(pg_catalog.btrim(p_versao), '') = '' or length(p_versao) > 20 then raise exception 'Versão inválida'; end if;
  select to_jsonb(t) into antes from public.sol_termos t where t.termo = p_termo;
  if antes is null then raise exception 'Termo não encontrado'; end if;
  if antes->>'versao' = pg_catalog.btrim(p_versao) then raise exception 'Essa já é a versão vigente'; end if;
  v_link := coalesce(nullif(pg_catalog.btrim(p_link), ''), 'https://judicial.solverone.com.br/termos/v' || pg_catalog.btrim(p_versao) || '.html');
  update public.sol_termos set versao = pg_catalog.btrim(p_versao), vigente_desde = pg_catalog.now(),
         hash_texto = coalesce(nullif(pg_catalog.lower(pg_catalog.btrim(p_hash_texto)), ''), hash_texto),
         reaceite_obrigatorio = coalesce(p_reaceite, false), atualizado_em = pg_catalog.now()
   where termo = p_termo;
  insert into public.sol_termos_versoes (termo, versao, link, hash_texto, material, motivo, publicado_por)
  values (p_termo, pg_catalog.btrim(p_versao), v_link, nullif(pg_catalog.lower(pg_catalog.btrim(p_hash_texto)), ''), coalesce(p_reaceite, false),
          pg_catalog.left(pg_catalog.btrim(p_motivo), 300), 'equipe:' || coalesce(auth.uid()::text, '?'));
  select to_jsonb(t) into depois from public.sol_termos t where t.termo = p_termo;
  perform public.lab_registrar_log('sol_termo_publicar', null, depois || jsonb_build_object('motivo', pg_catalog.left(pg_catalog.btrim(p_motivo), 300)), antes);
  return depois;
end $$;
revoke all on function public.admin_sol_termo_publicar(text, text, text, text, text, boolean) from public, anon;
grant execute on function public.admin_sol_termo_publicar(text, text, text, text, text, boolean) to authenticated;
-- DESFAZER: reaplicar o bloco de 2026-11-09g.

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
    -- precisa aceitar: nunca aceitou; ou a versão vigente é material (reaceite_obrigatorio) e o aceite é de versão anterior
    'precisa_aceitar', (not exists (select 1 from a))
                       or (coalesce((select reaceite_obrigatorio from t), false) and not exists (select 1 from a where a.versao = (select versao from t))));
$$;
revoke all on function public.sol_aceite_situacao(text, text, text, text) from public, anon;
grant execute on function public.sol_aceite_situacao(text, text, text, text) to authenticated, service_role;
-- DESFAZER: reaplicar o bloco de 2026-11-09g.

create or replace function public.sol_termos_versoes_lista(p_termo text)
returns jsonb language sql security definer set search_path = '' stable as $$
  select coalesce((select jsonb_agg(jsonb_build_object('versao', v.versao, 'vigente_desde', v.vigente_desde, 'link', v.link, 'material', v.material, 'motivo', v.motivo) order by v.vigente_desde desc)
                     from public.sol_termos_versoes v where v.termo = p_termo), '[]'::jsonb);
$$;
revoke all on function public.sol_termos_versoes_lista(text) from public, anon;
grant execute on function public.sol_termos_versoes_lista(text) to authenticated, service_role;
-- DESFAZER: drop function if exists public.sol_termos_versoes_lista(text);

-- Conferência (só leitura): tudo "true"
select
  (select count(*) = 1 from public.sol_termos_versoes where termo = 'lexsuiteone-termos') as historico_ok,
  exists (select 1 from pg_trigger where tgname = 'sol_termos_versoes_sem_update_delete') as imutavel_ok,
  (select prosrc like '%sol_termos_versoes%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_sol_termo_publicar' and pg_catalog.pg_get_function_arguments(p.oid) like '%p_reaceite%') as publicar_ok,
  (public.sol_aceite_situacao('radar-judicial', 'LEX-0000-0000', 'lexsuiteone-termos')->>'precisa_aceitar')::boolean as situacao_ok,
  (public.sol_termos_versoes_lista('lexsuiteone-termos')->0->>'versao') = '1.0' as lista_ok;
