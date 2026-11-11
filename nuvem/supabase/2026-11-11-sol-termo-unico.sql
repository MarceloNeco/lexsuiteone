-- =====================================================================================
-- 2026-11-11-sol-termo-unico.sql  —  projeto solverone-app (Supabase)
-- Decisão do dono (11/Nov): UM texto só de termos; o escritório aceita pelo link (registrado com o e-mail de quem aceitou)
-- e cada pessoa aceita o MESMO texto no cadastro do programa. Desenho: documentacao/DESENHO-TERMOS-UNICO-2026-11-11.md.
-- Também: trava do aceite LIGADA nas duas licenças (pedido do dono, 11/Nov: "pode já deixar ligada").
--
-- O QUE FAZ:
--   1. sol_termos.ativo; o termo 'lexsuiteone-uso' fica inativo (histórico). 'lexsuiteone-termos' passa à versão 1.2
--      (seção 2 reescrita; ninguém tinha aceitado a 1.1), sem reaceite obrigatório; hash do texto publicado.
--   2. sol_aceite_registrar: aceite vindo do programa (origem 'programa') exige só o nome (o cadastro do programa pede o
--      nome como a pessoa escreveu); pelo link e pelo site continua nome e sobrenome.
--   3. lex_contas.exigir_aceite = true nas licenças existentes (KR Law e teste do dono), com evento e log.
-- APLICADO em 11/Nov/2026 pelo conector.
-- =====================================================================================
alter table public.sol_termos add column if not exists ativo boolean not null default true;
update public.sol_termos set ativo = false, atualizado_em = now() where termo = 'lexsuiteone-uso';
update public.sol_termos set versao = '1.2', vigente_desde = now(), atualizado_em = now(), reaceite_obrigatorio = false,
       hash_texto = 'fa21688a79ae66ecdad1396b4cd5aec0a16683fc17f8ca15370b5bd2fa89d6e4', titulo = 'Termos do produto: contrato de licença, termos de uso, privacidade e tratamento de dados (escritório e cada pessoa)'
 where termo = 'lexsuiteone-termos';
-- DESFAZER: update public.sol_termos set ativo = true where termo = 'lexsuiteone-uso'; update public.sol_termos set versao = '1.1' where termo = 'lexsuiteone-termos';

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
  v_origem text := case when p->>'origem' in ('site', 'programa') then p->>'origem' else 'email' end;
  v_ip text := pg_catalog.btrim(pg_catalog.split_part(coalesce(p->>'ip', ''), ',', 1));
  v_id bigint; v_quando timestamptz; v_conhecidos text[]; v_escritorio text; t record;
begin
  if not exists (select 1 from public.sol_apps a where a.codigo = v_app and a.ativo) then raise exception 'App desconhecido' using errcode = 'P0001'; end if;
  if v_termo !~ '^[a-z0-9-]{3,60}$' or v_versao = '' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  select * into t from public.sol_termos where termo = v_termo;
  if t.termo is not null and not t.ativo then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  if t.termo is not null and t.versao <> v_versao then raise exception 'Os termos mudaram de versão: recarregue a página e leia a versão atual' using errcode = 'P0001'; end if;
  if v_hash = '' then v_hash := coalesce(t.hash_texto, pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(v_termo || '|' || v_versao, 'UTF8')), 'hex')); end if;
  if v_hash !~ '^[0-9a-f]{64}$' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  if v_origem = 'programa' then
    if length(v_nome) < 2 then raise exception 'Escreva o nome' using errcode = 'P0001'; end if;
  elsif length(v_nome) < 5 or v_nome !~ '\s' then raise exception 'Escreva o nome completo (nome e sobrenome)' using errcode = 'P0001'; end if;
  if v_email !~ '^[^@[:space:]]{1,64}@[^@[:space:]]+\.[^@[:space:]]{2,}$' then raise exception 'Confira o e-mail' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:email:' || v_email, 5, 3600) then raise exception 'Muitas tentativas; tente mais tarde' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:lic:' || v_lic, 60, 86400) then raise exception 'Muitas tentativas para esta licença hoje' using errcode = 'P0001'; end if;
  if v_app = 'radar-judicial' then
    select c.escritorio, array_remove(array[c.email_responsavel, c.email_boas_vindas] || coalesce((select array_agg(u.email) from public.lex_usuarios u where u.codigo = c.codigo), '{}'), null)
      into v_escritorio, v_conhecidos from public.lex_contas c where c.codigo = v_lic;
    if v_escritorio is null then raise exception 'Código de cliente desconhecido' using errcode = 'P0001'; end if;
    if pg_catalog.cardinality(v_conhecidos) > 0 and not (v_email = any (v_conhecidos)) then
      raise exception 'Use o link do e-mail de boas-vindas: o aceite é feito com o e-mail do responsável pela licença' using errcode = 'P0001';
    end if;
  end if;
  if v_ip ~ '^\d{1,3}(\.\d{1,3}){3}$' then v_ip := pg_catalog.regexp_replace(v_ip, '\.\d+$', '.x');
  elsif v_ip like '%:%' then v_ip := pg_catalog.array_to_string((pg_catalog.string_to_array(v_ip, ':'))[1:4], ':') || ':…';
  else v_ip := null; end if;
  insert into public.sol_aceites (app, licenca, termo, versao, hash, nome, email, ip_resumo, navegador, origem, fuso)
  values (v_app, v_lic, v_termo, v_versao, v_hash, pg_catalog.left(v_nome, 120), v_email, v_ip, nullif(v_nav, ''), v_origem, v_fuso)
  returning id, aceito_em into v_id, v_quando;
  return jsonb_build_object('ok', true, 'protocolo', 'ACE-' || pg_catalog.lpad(v_id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(v_hash, 6)),
                            'aceito_em', v_quando, 'fuso', v_fuso, 'escritorio', v_escritorio, 'nome', pg_catalog.left(v_nome, 120), 'email', v_email, 'versao', v_versao, 'termo', v_termo);
end $$;
revoke all on function public.sol_aceite_registrar(jsonb) from public, anon, authenticated;
grant execute on function public.sol_aceite_registrar(jsonb) to service_role;
-- DESFAZER: reaplicar o bloco sol_aceite_registrar de 2026-11-09f.

-- 3. Trava do aceite ligada (pedido do dono, 11/Nov), com registro
update public.lex_contas set exigir_aceite = true where exigir_aceite = false;
insert into public.lex_eventos (codigo, tipo, detalhe, quem, motivo)
select codigo, 'licenca_alterada', 'aceite dos termos exigido: trava ligada (uso só depois do aceite do responsável)', 'arquitetura', 'pedido do dono em 11/Nov: "pode já deixar ligada"'
  from public.lex_contas;
-- DESFAZER: update public.lex_contas set exigir_aceite = false;
