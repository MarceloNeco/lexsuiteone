-- =====================================================================================
-- 2026-11-09d-lex-exigir-aceite.sql  —  projeto solverone-app (Supabase)
-- Decisão do dono (09/Nov, noite): a licença fica ATIVA desde o e-mail de boas-vindas (o código pode ir no e-mail),
-- mas o USO fica travado até o responsável aceitar os termos. A trava é por licença (exigir_aceite) e é aplicada pela
-- função da nuvem lex-conta (resposta ok:false, motivo 'aceite_pendente', com o link da página de aceite).
-- PRÉ-REQUISITO: 2026-11-09b-sol-aceites.sql e 2026-11-09c-lex-listar-responsavel-aceite.sql.
--
-- O QUE FAZ:
--   1. lex_contas.exigir_aceite (padrão true para licença nova). As licenças que JÁ existem ficam false neste momento,
--      porque a página de aceite ainda não está publicada (ninguém conseguiria aceitar): quando a página for ao ar,
--      a Arquitetura liga a trava da KR Law (update abaixo, em comentário) com o "pode" do dono.
--   2. admin_lex_salvar aceita exigir_aceite; admin_lex_listar devolve exigir_aceite.
--   3. sol_aceite_registrar, para o RADAR: o e-mail do aceite tem de ser um e-mail conhecido da licença (responsável,
--      boas-vindas ou pessoa cadastrada), quando a licença tiver algum; assim o campo fixo da página vale de verdade.
--   4. sol_aceite_contexto devolve também o e-mail do responsável (para a página preencher quando o link não trouxer).
-- APLICADO em 09/Nov/2026 pelo conector (pedido direto do dono nesta rotina).
-- =====================================================================================
alter table public.lex_contas add column if not exists exigir_aceite boolean not null default true;
comment on column public.lex_contas.exigir_aceite is 'true = o programa só libera o uso depois que o responsável aceita os termos (sol_aceites). A licença continua ativa.';
update public.lex_contas set exigir_aceite = false where criado_em < '2026-11-10';   -- licenças de antes da página de aceite existir
-- Quando a página estiver publicada (com o "pode" do dono): update public.lex_contas set exigir_aceite = true where escritorio ilike 'KR Law%';
-- DESFAZER: alter table public.lex_contas drop column exigir_aceite;  (antes, reaplicar admin_lex_salvar/listar de 2026-11-09 e 2026-11-09c)

create or replace function public.admin_lex_salvar(p jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb; v_mod_antes text; v_mod_depois text; v_quem text := 'equipe:' || coalesce(auth.uid()::text, '?');
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select to_jsonb(c), c.modalidade into antes, v_mod_antes from public.lex_contas c where c.codigo = p->>'codigo';
  if antes is null then raise exception 'Licença não encontrada'; end if;
  if p ? 'modalidade' and p->>'modalidade' not in ('instalado', 'nuvem') then raise exception 'Modalidade inválida'; end if;
  update public.lex_contas set
    escritorio        = coalesce(nullif(pg_catalog.btrim(p->>'escritorio'), ''), escritorio),
    ativo             = coalesce((p->>'ativo')::boolean, ativo),
    validade          = case when p ? 'validade' then nullif(p->>'validade', '')::date else validade end,
    max_pessoas       = case when p ? 'max_pessoas' then nullif(p->>'max_pessoas', '')::integer else max_pessoas end,
    max_computadores  = case when p ? 'max_computadores' then coalesce(nullif(p->>'max_computadores', '')::smallint, max_computadores) else max_computadores end,
    mensagem          = case when p ? 'mensagem' then coalesce(p->>'mensagem', '') else mensagem end,
    email_boas_vindas = case when p ? 'email_boas_vindas' then nullif(pg_catalog.lower(pg_catalog.btrim(p->>'email_boas_vindas')), '') else email_boas_vindas end,
    email_responsavel = case when p ? 'email_responsavel' then nullif(pg_catalog.lower(pg_catalog.btrim(p->>'email_responsavel')), '') else email_responsavel end,
    exigir_aprovacao  = coalesce((p->>'exigir_aprovacao')::boolean, exigir_aprovacao),
    exigir_aceite     = coalesce((p->>'exigir_aceite')::boolean, exigir_aceite),
    dominios          = case when p ? 'dominios' then coalesce((select array_agg(pg_catalog.lower(pg_catalog.btrim(d))) from jsonb_array_elements_text(p->'dominios') d where pg_catalog.btrim(d) <> ''), '{}') else dominios end,
    modalidade        = coalesce(p->>'modalidade', modalidade),
    modalidade_desde  = case when p ? 'modalidade' and p->>'modalidade' <> modalidade then pg_catalog.now() else modalidade_desde end
  where codigo = p->>'codigo';
  select to_jsonb(c), c.modalidade into depois, v_mod_depois from public.lex_contas c where c.codigo = p->>'codigo';
  insert into public.lex_eventos (codigo, tipo, detalhe, quem, motivo)
  values (p->>'codigo', 'licenca_alterada', case when v_mod_depois <> v_mod_antes then 'modalidade: ' || v_mod_antes || ' -> ' || v_mod_depois else 'ficha alterada' end,
          v_quem, pg_catalog.left(coalesce(p->>'motivo', ''), 300));
  perform public.lab_registrar_log('lex_salvar_licenca', null, depois, antes);
  return depois;
end $$;
revoke all on function public.admin_lex_salvar(jsonb) from public, anon;
grant execute on function public.admin_lex_salvar(jsonb) to authenticated;
-- DESFAZER: reaplicar o bloco admin_lex_salvar de 2026-11-09-sol-retorno-e-lex-auditoria.sql.

create or replace function public.admin_lex_listar()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'codigo', c.codigo, 'escritorio', c.escritorio, 'doc_tipo', c.doc_tipo, 'documento', c.documento,
      'ativo', c.ativo, 'validade', c.validade, 'max_pessoas', c.max_pessoas, 'max_computadores', c.max_computadores,
      'mensagem', c.mensagem, 'criado_em', c.criado_em, 'dominios', c.dominios, 'email_boas_vindas', c.email_boas_vindas,
      'email_responsavel', c.email_responsavel, 'exigir_aceite', c.exigir_aceite,
      'boas_vindas', (select jsonb_build_object('ok', e.tipo = 'aviso_enviado', 'para', e.email, 'em', e.criado_em)
                        from public.lex_eventos e
                       where e.codigo = c.codigo and e.tipo in ('aviso_enviado', 'aviso_falhou') and e.detalhe like 'boas-vindas%'
                       order by e.criado_em desc limit 1),
      'aceite', coalesce((select jsonb_build_object('aceito', true, 'versao', a.versao, 'aceito_em', a.aceito_em, 'nome', a.nome, 'email', a.email,
                                                    'protocolo', 'ACE-' || pg_catalog.lpad(a.id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(a.hash, 6)))
                            from public.sol_aceites a
                           where a.app = 'radar-judicial' and a.licenca = c.codigo and a.termo = 'lexsuiteone-termos'
                           order by a.aceito_em desc limit 1), jsonb_build_object('aceito', false)),
      'exigir_aprovacao', c.exigir_aprovacao, 'modalidade', c.modalidade, 'modalidade_desde', c.modalidade_desde,
      'dominios_pessoas', coalesce((select jsonb_agg(distinct pg_catalog.split_part(u.email, '@', 2)) from public.lex_usuarios u where u.codigo = c.codigo), '[]'::jsonb),
      'pessoas_ativas', (select count(*) from public.lex_pessoas p where p.codigo = c.codigo and p.ativa and p.aprovacao = 'aprovado'),
      'pessoas_total', (select count(*) from public.lex_usuarios u where u.codigo = c.codigo),
      'pessoas_aguardando', (select count(*) from public.lex_usuarios u where u.codigo = c.codigo and u.aprovacao = 'aguardando'),
      'computadores', (select count(*) from public.lex_computadores i where i.codigo = c.codigo and i.esquecida_em is null),
      'computadores_ativos', (select count(*) from public.lex_computadores i where i.codigo = c.codigo and i.ativo),
      'ultima_vez', (select max(i.ultima_vez) from public.lex_instalacoes i where i.codigo = c.codigo),
      'erros_7d', (select count(*) from public.lex_registros r where r.codigo = c.codigo and r.criado_em > pg_catalog.now() - interval '7 days'),
      'avisos_falhos', (select count(*) from public.lex_avisos a where a.codigo = c.codigo and a.estado = 'falhou')
    ) order by c.criado_em desc)
    from public.lex_contas c), '[]'::jsonb);
end $$;
revoke all on function public.admin_lex_listar() from public, anon;
grant execute on function public.admin_lex_listar() to authenticated;
-- DESFAZER: reaplicar o bloco admin_lex_listar de 2026-11-09c-lex-listar-responsavel-aceite.sql.

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
  v_ip text; v_id bigint; v_quando timestamptz; v_conhecidos text[];
begin
  if not exists (select 1 from public.sol_apps a where a.codigo = v_app and a.ativo) then raise exception 'App desconhecido' using errcode = 'P0001'; end if;
  if v_termo !~ '^[a-z0-9-]{3,60}$' or v_versao = '' or v_hash !~ '^[0-9a-f]{64}$' then raise exception 'Dados do termo inválidos' using errcode = 'P0001'; end if;
  if length(v_nome) < 5 or v_nome !~ '\s' then raise exception 'Escreva o nome completo (nome e sobrenome)' using errcode = 'P0001'; end if;
  if v_email !~ '^[^@[:space:]]{1,64}@[^@[:space:]]+\.[^@[:space:]]{2,}$' then raise exception 'Confira o e-mail' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:email:' || v_email, 5, 3600) then raise exception 'Muitas tentativas; tente mais tarde' using errcode = 'P0001'; end if;
  if not public.lex_contar_chamada('aceite:lic:' || v_lic, 30, 86400) then raise exception 'Muitas tentativas para esta licença hoje' using errcode = 'P0001'; end if;
  if v_app = 'radar-judicial' then
    if not exists (select 1 from public.lex_contas c where c.codigo = v_lic) then raise exception 'Código de cliente desconhecido' using errcode = 'P0001'; end if;
    -- O e-mail do aceite tem de ser um e-mail da licença (responsável, boas-vindas ou pessoa cadastrada), se houver algum.
    select array_remove(array[c.email_responsavel, c.email_boas_vindas] || coalesce((select array_agg(u.email) from public.lex_usuarios u where u.codigo = c.codigo), '{}'), null)
      into v_conhecidos from public.lex_contas c where c.codigo = v_lic;
    if pg_catalog.cardinality(v_conhecidos) > 0 and not (v_email = any (v_conhecidos)) then
      raise exception 'Use o link do e-mail de boas-vindas: o aceite é feito com o e-mail do responsável pela licença' using errcode = 'P0001';
    end if;
  end if;
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
grant execute on function public.sol_aceite_registrar(jsonb) to anon, authenticated, service_role;   -- anon de propósito (página pública), com limites
-- DESFAZER: reaplicar o bloco sol_aceite_registrar de 2026-11-09b-sol-aceites.sql.

create or replace function public.sol_aceite_contexto(p_app text, p_licenca text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_lic text := pg_catalog.upper(pg_catalog.btrim(coalesce(p_licenca, ''))); v_nome text; v_email text;
begin
  if not public.lex_contar_chamada('aceite:ctx:' || v_lic, 30, 3600) then return jsonb_build_object('ok', false); end if;
  if p_app = 'radar-judicial' then select c.escritorio, coalesce(c.email_responsavel, c.email_boas_vindas) into v_nome, v_email from public.lex_contas c where c.codigo = v_lic; end if;
  if v_nome is null then return jsonb_build_object('ok', false); end if;
  return jsonb_build_object('ok', true, 'escritorio', v_nome, 'email', v_email,
    'ja_aceito', exists (select 1 from public.sol_aceites a where a.app = p_app and a.licenca = v_lic and a.termo = 'lexsuiteone-termos'));
end $$;
revoke all on function public.sol_aceite_contexto(text, text) from public;
grant execute on function public.sol_aceite_contexto(text, text) to anon, authenticated, service_role;   -- anon de propósito: nome do escritório e e-mail do responsável, para quem tem o código
-- DESFAZER: reaplicar o bloco sol_aceite_contexto de 2026-11-09b-sol-aceites.sql.

-- Conferência (só leitura): tudo "true"
select
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_contas' and column_name = 'exigir_aceite') as coluna_ok,
  (select count(*) = count(*) filter (where not exigir_aceite) from public.lex_contas where criado_em < '2026-11-10') as antigas_sem_trava_ok,
  (select prosrc like '%exigir_aceite%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_lex_salvar') as salvar_ok,
  (select prosrc like '%exigir_aceite%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_lex_listar') as listar_ok,
  (select prosrc like '%v_conhecidos%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'sol_aceite_registrar') as registrar_ok;
