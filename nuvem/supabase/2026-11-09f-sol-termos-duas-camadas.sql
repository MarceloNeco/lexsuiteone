-- =====================================================================================
-- 2026-11-09f-sol-termos-duas-camadas.sql  —  projeto solverone-app (Supabase)
-- Decisão do dono (09/Nov, noite): termos em DUAS CAMADAS.
--   (1) Escritório: o responsável aceita uma vez o contrato + termo de tratamento de dados (termo 'lexsuiteone-termos');
--       libera a licença (já existia).
--   (2) Pessoa: cada pessoa que usa o programa aceita os termos de uso (termo 'lexsuiteone-uso') no cadastro, com versão,
--       data/hora com fuso e e-mail; versão nova = aceita de novo; sem aceite da pessoa ela não lê, mesmo com a licença liberada.
-- Desenho: documentacao/DECISAO-B2B-QUEM-FAZ-O-QUE-2026-11-09.md, seção 5c. PRÉ-REQUISITO: 2026-11-09e.
--
-- O QUE FAZ:
--   1. sol_termos: registro das versões vigentes (termo, alcance escritorio|pessoa, versão, desde, link, hash do texto).
--      Quem muda a versão: admin_sol_termo_publicar (equipe, com motivo, registrado). Leitura pública: sol_termo_vigente.
--   2. sol_aceites.fuso (fuso horário informado por quem aceitou; a hora fica em timestamptz, UTC, e sai com o fuso).
--   3. sol_aceite_registrar: confere a versão contra a vigente ("recarregue a página" se mudou); exige sobrenome só para o
--      termo do escritório; para termo de pessoa, o e-mail tem de ser de pessoa cadastrada na licença; hash opcional para
--      aceite feito no programa (usa o hash do texto publicado ou sha256(termo|versão)).
--   4. sol_aceite_situacao(app, licenca, termo, email): o que a lex-conta devolve ao programa e ao RootifyONE
--      ({aceito, versao, aceito_em, fuso, nome, email, protocolo, versao_vigente, link, precisa_aceitar}).
--   5. admin_sol_termos(): lista das versões para o RootifyONE.
-- APLICADO em 09/Nov/2026 pelo conector.
-- =====================================================================================

create table if not exists public.sol_termos (
  termo          text primary key check (termo ~ '^[a-z0-9-]{3,60}$'),
  suite          text not null,
  alcance        text not null check (alcance in ('escritorio', 'pessoa')),
  titulo         text not null,
  versao         text not null check (length(versao) between 1 and 20),
  vigente_desde  timestamptz not null default now(),
  link           text not null,
  hash_texto     text check (hash_texto is null or hash_texto ~ '^[0-9a-f]{64}$'),
  atualizado_em  timestamptz not null default now()
);
comment on table public.sol_termos is 'Versão vigente de cada termo (por suíte): escritório aceita o contrato uma vez; cada pessoa aceita os termos de uso por versão.';
alter table public.sol_termos enable row level security;
revoke all on public.sol_termos from public, anon, authenticated;
grant select, insert, update on public.sol_termos to service_role;
insert into public.sol_termos (termo, suite, alcance, titulo, versao, vigente_desde, link) values
  ('lexsuiteone-termos', 'lexsuiteone', 'escritorio', 'Contrato de licença, política de privacidade e termo de tratamento de dados', '1.0', '2026-11-09', 'https://judicial.solverone.com.br/aceite.html'),
  ('lexsuiteone-uso',    'lexsuiteone', 'pessoa',     'Termos de uso do programa (cada pessoa que usa)',                                  '1.0', '2026-11-09', 'https://judicial.solverone.com.br/aceite.html?ler=uso')
on conflict (termo) do nothing;
-- DESFAZER: drop table if exists public.sol_termos;

alter table public.sol_aceites add column if not exists fuso text check (fuso is null or length(fuso) <= 60);
-- DESFAZER: alter table public.sol_aceites drop column fuso;

create or replace function public.sol_termo_vigente(p_termo text)
returns jsonb language sql security definer set search_path = '' stable as $$
  select coalesce((select jsonb_build_object('termo', t.termo, 'alcance', t.alcance, 'titulo', t.titulo, 'versao', t.versao, 'vigente_desde', t.vigente_desde, 'link', t.link)
                     from public.sol_termos t where t.termo = p_termo), jsonb_build_object('ok', false));
$$;
revoke all on function public.sol_termo_vigente(text) from public;
grant execute on function public.sol_termo_vigente(text) to anon, authenticated, service_role;   -- pública, só leitura: versão e link do termo
-- DESFAZER: drop function if exists public.sol_termo_vigente(text);

create or replace function public.admin_sol_termos()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((select jsonb_agg(to_jsonb(t) order by t.suite, t.alcance) from public.sol_termos t), '[]'::jsonb);
end $$;
revoke all on function public.admin_sol_termos() from public, anon;
grant execute on function public.admin_sol_termos() to authenticated;
-- DESFAZER: drop function if exists public.admin_sol_termos();

create or replace function public.admin_sol_termo_publicar(p_termo text, p_versao text, p_link text, p_hash_texto text, p_motivo text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if length(coalesce(pg_catalog.btrim(p_motivo), '')) < 5 then raise exception 'Escreva o motivo (pelo menos 5 letras)'; end if;
  if coalesce(pg_catalog.btrim(p_versao), '') = '' or length(p_versao) > 20 then raise exception 'Versão inválida'; end if;
  select to_jsonb(t) into antes from public.sol_termos t where t.termo = p_termo;
  if antes is null then raise exception 'Termo não encontrado'; end if;
  update public.sol_termos set versao = pg_catalog.btrim(p_versao), vigente_desde = pg_catalog.now(), link = coalesce(nullif(pg_catalog.btrim(p_link), ''), link),
         hash_texto = coalesce(nullif(pg_catalog.lower(pg_catalog.btrim(p_hash_texto)), ''), hash_texto), atualizado_em = pg_catalog.now()
   where termo = p_termo;
  select to_jsonb(t) into depois from public.sol_termos t where t.termo = p_termo;
  perform public.lab_registrar_log('sol_termo_publicar', null, depois || jsonb_build_object('motivo', pg_catalog.left(pg_catalog.btrim(p_motivo), 300)), antes);
  return depois;
end $$;
revoke all on function public.admin_sol_termo_publicar(text, text, text, text, text) from public, anon;
grant execute on function public.admin_sol_termo_publicar(text, text, text, text, text) to authenticated;
-- DESFAZER: drop function if exists public.admin_sol_termo_publicar(text, text, text, text, text);

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
  v_fuso text := nullif(pg_catalog.left(pg_catalog.btrim(coalesce(p->>'fuso', '')), 60), '');
  v_ip text := pg_catalog.btrim(pg_catalog.split_part(coalesce(p->>'ip', ''), ',', 1));
  v_id bigint; v_quando timestamptz; v_conhecidos text[]; v_escritorio text; t record;
begin
  if not exists (select 1 from public.sol_apps a where a.codigo = v_app and a.ativo) then raise exception 'App desconhecido' using errcode = 'P0001'; end if;
  if v_termo !~ '^[a-z0-9-]{3,60}$' or v_versao = '' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  select * into t from public.sol_termos where termo = v_termo;
  if t.termo is not null and t.versao <> v_versao then raise exception 'Os termos mudaram de versão: recarregue a página e leia a versão atual' using errcode = 'P0001'; end if;
  if v_hash = '' then v_hash := coalesce(t.hash_texto, pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(v_termo || '|' || v_versao, 'UTF8')), 'hex')); end if;
  if v_hash !~ '^[0-9a-f]{64}$' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  if coalesce(t.alcance, 'escritorio') = 'escritorio' then
    if length(v_nome) < 5 or v_nome !~ '\s' then raise exception 'Escreva o nome completo (nome e sobrenome)' using errcode = 'P0001'; end if;
  elsif length(v_nome) < 2 then raise exception 'Escreva o nome' using errcode = 'P0001'; end if;
  if v_email !~ '^[^@[:space:]]{1,64}@[^@[:space:]]+\.[^@[:space:]]{2,}$' then raise exception 'Confira o e-mail' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:email:' || v_email, 5, 3600) then raise exception 'Muitas tentativas; tente mais tarde' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:lic:' || v_lic, 60, 86400) then raise exception 'Muitas tentativas para esta licença hoje' using errcode = 'P0001'; end if;
  if v_app = 'radar-judicial' then
    select c.escritorio, array_remove(array[c.email_responsavel, c.email_boas_vindas] || coalesce((select array_agg(u.email) from public.lex_usuarios u where u.codigo = c.codigo), '{}'), null)
      into v_escritorio, v_conhecidos from public.lex_contas c where c.codigo = v_lic;
    if v_escritorio is null then raise exception 'Código de cliente desconhecido' using errcode = 'P0001'; end if;
    if coalesce(t.alcance, 'escritorio') = 'pessoa' then
      if not exists (select 1 from public.lex_usuarios u where u.codigo = v_lic and u.email = v_email) then
        raise exception 'Pessoa não cadastrada nesta licença' using errcode = 'P0001';
      end if;
    elsif pg_catalog.cardinality(v_conhecidos) > 0 and not (v_email = any (v_conhecidos)) then
      raise exception 'Use o link do e-mail de boas-vindas: o aceite é feito com o e-mail do responsável pela licença' using errcode = 'P0001';
    end if;
  end if;
  if v_ip ~ '^\d{1,3}(\.\d{1,3}){3}$' then v_ip := pg_catalog.regexp_replace(v_ip, '\.\d+$', '.x');
  elsif v_ip like '%:%' then v_ip := pg_catalog.array_to_string((pg_catalog.string_to_array(v_ip, ':'))[1:4], ':') || ':…';
  else v_ip := null; end if;
  insert into public.sol_aceites (app, licenca, termo, versao, hash, nome, email, ip_resumo, navegador, origem, fuso)
  values (v_app, v_lic, v_termo, v_versao, v_hash, pg_catalog.left(v_nome, 120), v_email, v_ip, nullif(v_nav, ''),
          case when p->>'origem' in ('site', 'programa') then p->>'origem' else 'email' end, v_fuso)
  returning id, aceito_em into v_id, v_quando;
  return jsonb_build_object('ok', true, 'protocolo', 'ACE-' || pg_catalog.lpad(v_id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(v_hash, 6)),
                            'aceito_em', v_quando, 'fuso', v_fuso, 'escritorio', v_escritorio, 'nome', pg_catalog.left(v_nome, 120), 'email', v_email, 'versao', v_versao, 'termo', v_termo);
end $$;
revoke all on function public.sol_aceite_registrar(jsonb) from public, anon, authenticated;
grant execute on function public.sol_aceite_registrar(jsonb) to service_role;   -- só a lex-conta grava
-- DESFAZER: reaplicar o bloco sol_aceite_registrar de 2026-11-09e-lex-aceite-seguranca.sql.

create or replace function public.sol_aceite_situacao(p_app text, p_licenca text, p_termo text, p_email text default null)
returns jsonb language sql security definer set search_path = '' stable as $$
  with t as (select versao, link, alcance, titulo from public.sol_termos where termo = p_termo),
       a as (select a.versao, a.aceito_em, a.fuso, a.nome, a.email, 'ACE-' || pg_catalog.lpad(a.id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(a.hash, 6)) as protocolo
               from public.sol_aceites a
              where a.app = p_app and a.licenca = p_licenca and a.termo = p_termo and (p_email is null or a.email = pg_catalog.lower(p_email))
              order by a.aceito_em desc limit 1)
  select jsonb_build_object(
    'termo', p_termo, 'alcance', (select alcance from t), 'titulo', (select titulo from t),
    'versao_vigente', (select versao from t), 'link', (select link from t),
    'aceito', exists (select 1 from a),
    'versao', (select versao from a), 'aceito_em', (select aceito_em from a), 'fuso', (select fuso from a),
    'nome', (select nome from a), 'email', (select email from a), 'protocolo', (select protocolo from a),
    'precisa_aceitar', not exists (select 1 from a where a.versao = (select versao from t)));
$$;
revoke all on function public.sol_aceite_situacao(text, text, text, text) from public, anon;
grant execute on function public.sol_aceite_situacao(text, text, text, text) to authenticated, service_role;   -- equipe (RootifyONE) e lex-conta
-- DESFAZER: drop function if exists public.sol_aceite_situacao(text, text, text, text);

-- Conferência (só leitura): tudo "true"
select
  (select count(*) = 2 from public.sol_termos where suite = 'lexsuiteone') as termos_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'sol_aceites' and column_name = 'fuso') as fuso_ok,
  (select count(*) = 4 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public'
     and p.proname in ('sol_termo_vigente', 'admin_sol_termos', 'admin_sol_termo_publicar', 'sol_aceite_situacao')) as funcoes_ok,
  (select prosrc like '%alcance%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'sol_aceite_registrar') as registrar_ok,
  (public.sol_aceite_situacao('radar-judicial', 'LEX-0000-0000', 'lexsuiteone-uso', 'x@y.zz')->>'precisa_aceitar')::boolean as situacao_ok;
