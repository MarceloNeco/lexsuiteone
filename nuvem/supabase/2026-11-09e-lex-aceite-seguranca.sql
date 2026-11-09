-- =====================================================================================
-- 2026-11-09e-lex-aceite-seguranca.sql  —  projeto solverone-app (Supabase)
-- Pedido do dono (09/Nov, noite): (a) a equipe pode LIBERAR O USO antes do aceite (risco assumido pela SolverONE), com
-- registro de quem, quando e motivo; (b) fechar a segurança do caminho do aceite.
--
-- O QUE FAZ:
--   1. admin_lex_dispensar_aceite(codigo, dispensar, motivo): liga/desliga exigir_aceite com motivo obrigatório; grava em
--      lex_eventos (quem = equipe:<uuid>, motivo) e no log da plataforma. É o único jeito "oficial" de liberar sem aceite.
--   2. sol_aceite_registrar deixa de ser pública: só a função da nuvem lex-conta (service_role) grava, depois de validar e
--      limitar. Nenhuma função que ESCREVE fica executável pela chave publicável. A função aceita o IP que a lex-conta lê
--      do pedido (resumido na hora) e devolve também o escritório, para o e-mail de confirmação.
--   3. sol_aceite_contexto (pública, só leitura) passa a devolver o e-mail do responsável MASCARADO (l***@krlaw.com.br):
--      quem tem só o código não descobre o e-mail inteiro; o aceite exige o e-mail certo, que veio no e-mail de boas-vindas.
-- Evento de aceite e de dispensa usam tipo 'licenca_alterada' com detalhe próprio (ampliar o check de lex_eventos pede
-- DROP CONSTRAINT, que o conector só confirma no desktop; fica para a próxima sessão no desktop: 'termos_aceitos',
-- 'aceite_dispensado', 'aceite_exigido').
-- APLICADO em 09/Nov/2026 pelo conector.
-- =====================================================================================

create or replace function public.admin_lex_dispensar_aceite(p_codigo text, p_dispensar boolean, p_motivo text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if length(coalesce(pg_catalog.btrim(p_motivo), '')) < 5 then raise exception 'Escreva o motivo (pelo menos 5 letras)'; end if;
  select to_jsonb(c) into antes from public.lex_contas c where c.codigo = p_codigo;
  if antes is null then raise exception 'Licença não encontrada'; end if;
  update public.lex_contas set exigir_aceite = not p_dispensar where codigo = p_codigo;
  select to_jsonb(c) into depois from public.lex_contas c where c.codigo = p_codigo;
  insert into public.lex_eventos (codigo, tipo, detalhe, quem, motivo)
  values (p_codigo, 'licenca_alterada',
          case when p_dispensar then 'aceite dos termos dispensado pela equipe: uso liberado sem aceite (risco da SolverONE)' else 'aceite dos termos exigido de novo: uso travado até o aceite' end,
          'equipe:' || coalesce(auth.uid()::text, '?'), pg_catalog.left(pg_catalog.btrim(p_motivo), 300));
  perform public.lab_registrar_log(case when p_dispensar then 'lex_dispensar_aceite' else 'lex_exigir_aceite' end, null, depois, antes);
  return depois;
end $$;
revoke all on function public.admin_lex_dispensar_aceite(text, boolean, text) from public, anon;
grant execute on function public.admin_lex_dispensar_aceite(text, boolean, text) to authenticated;
-- DESFAZER: drop function if exists public.admin_lex_dispensar_aceite(text, boolean, text);

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
  v_ip text := pg_catalog.btrim(pg_catalog.split_part(coalesce(p->>'ip', ''), ',', 1));
  v_id bigint; v_quando timestamptz; v_conhecidos text[]; v_escritorio text;
begin
  if not exists (select 1 from public.sol_apps a where a.codigo = v_app and a.ativo) then raise exception 'App desconhecido' using errcode = 'P0001'; end if;
  if v_termo !~ '^[a-z0-9-]{3,60}$' or v_versao = '' or v_hash !~ '^[0-9a-f]{64}$' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  if length(v_nome) < 5 or v_nome !~ '\s' then raise exception 'Escreva o nome completo (nome e sobrenome)' using errcode = 'P0001'; end if;
  if v_email !~ '^[^@[:space:]]{1,64}@[^@[:space:]]+\.[^@[:space:]]{2,}$' then raise exception 'Confira o e-mail' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:email:' || v_email, 5, 3600) then raise exception 'Muitas tentativas; tente mais tarde' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:lic:' || v_lic, 30, 86400) then raise exception 'Muitas tentativas para esta licença hoje' using errcode = 'P0001'; end if;
  if v_app = 'radar-judicial' then
    select c.escritorio, array_remove(array[c.email_responsavel, c.email_boas_vindas] || coalesce((select array_agg(u.email) from public.lex_usuarios u where u.codigo = c.codigo), '{}'), null)
      into v_escritorio, v_conhecidos from public.lex_contas c where c.codigo = v_lic;
    if v_escritorio is null then raise exception 'Código de cliente desconhecido' using errcode = 'P0001'; end if;
    if pg_catalog.cardinality(v_conhecidos) > 0 and not (v_email = any (v_conhecidos)) then
      raise exception 'Use o link do e-mail de boas-vindas: o aceite é feito com o e-mail do responsável pela licença' using errcode = 'P0001';
    end if;
  end if;
  -- IP resumido (prova sem identificar o aparelho): 3 blocos do IPv4 ou 4 do IPv6.
  if v_ip ~ '^\d{1,3}(\.\d{1,3}){3}$' then v_ip := pg_catalog.regexp_replace(v_ip, '\.\d+$', '.x');
  elsif v_ip like '%:%' then v_ip := pg_catalog.array_to_string((pg_catalog.string_to_array(v_ip, ':'))[1:4], ':') || ':…';
  else v_ip := null; end if;
  insert into public.sol_aceites (app, licenca, termo, versao, hash, nome, email, ip_resumo, navegador, origem)
  values (v_app, v_lic, v_termo, v_versao, v_hash, pg_catalog.left(v_nome, 120), v_email, v_ip, nullif(v_nav, ''),
          case when p->>'origem' in ('site', 'programa') then p->>'origem' else 'email' end)
  returning id, aceito_em into v_id, v_quando;
  return jsonb_build_object('ok', true, 'protocolo', 'ACE-' || pg_catalog.lpad(v_id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(v_hash, 6)),
                            'aceito_em', v_quando, 'escritorio', v_escritorio, 'nome', pg_catalog.left(v_nome, 120), 'email', v_email, 'versao', v_versao);
end $$;
revoke all on function public.sol_aceite_registrar(jsonb) from public, anon, authenticated;
grant execute on function public.sol_aceite_registrar(jsonb) to service_role;   -- só a lex-conta grava
-- DESFAZER: reaplicar o bloco sol_aceite_registrar de 2026-11-09d-lex-exigir-aceite.sql.

create or replace function public.sol_aceite_contexto(p_app text, p_licenca text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_lic text := pg_catalog.upper(pg_catalog.btrim(coalesce(p_licenca, ''))); v_nome text; v_email text;
begin
  if not public.lex_contar_chamada('aceite:ctx:' || v_lic, 30, 3600) then return jsonb_build_object('ok', false); end if;
  if p_app = 'radar-judicial' then select c.escritorio, coalesce(c.email_responsavel, c.email_boas_vindas) into v_nome, v_email from public.lex_contas c where c.codigo = v_lic; end if;
  if v_nome is null then return jsonb_build_object('ok', false); end if;
  return jsonb_build_object('ok', true, 'escritorio', v_nome,
    'email_mascarado', case when v_email is null then null else pg_catalog.left(v_email, 1) || '***@' || pg_catalog.split_part(v_email, '@', 2) end,
    'ja_aceito', exists (select 1 from public.sol_aceites a where a.app = p_app and a.licenca = v_lic and a.termo = 'lexsuiteone-termos'));
end $$;
revoke all on function public.sol_aceite_contexto(text, text) from public;
grant execute on function public.sol_aceite_contexto(text, text) to anon, authenticated, service_role;   -- pública, só leitura, e-mail mascarado
-- DESFAZER: reaplicar o bloco sol_aceite_contexto de 2026-11-09d-lex-exigir-aceite.sql.

-- Conferência (só leitura): tudo "true"
select
  exists (select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_lex_dispensar_aceite') as dispensar_ok,
  not exists (select 1 from information_schema.routine_privileges where routine_schema = 'public' and routine_name = 'sol_aceite_registrar' and grantee in ('anon', 'authenticated')) as registrar_so_servico_ok,
  (select prosrc like '%email_mascarado%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'sol_aceite_contexto') as contexto_ok;
