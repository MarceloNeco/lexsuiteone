-- =====================================================================================
-- 2026-11-08c-lex-modalidade.sql  —  projeto solverone-app (Supabase)
-- RADAR JUDICIAL: item F da licença em uso (documentacao/DESENHO-LICENCA-EM-USO.md): tipo de acesso do cliente.
-- PRÉ-REQUISITO: 2026-11-08b-lex-licenca-em-uso.sql aplicado.
--
-- O QUE FAZ (tudo opcional; nenhum programa instalado é bloqueado):
--   1. lex_contas.modalidade ('instalado' | 'nuvem'), padrão 'instalado' para todas as licenças de hoje, e modalidade_desde.
--   2. admin_lex_salvar aceita "modalidade" e grava a troca em lex_eventos (tipo licenca_alterada, detalhe
--      "modalidade: instalado -> nuvem", com a hora; quem mudou fica em acesso_log, como as outras ações da equipe).
--   3. admin_lex_listar devolve modalidade, modalidade_desde e dominios_pessoas (domínios dos e-mails cadastrados, sem
--      os e-mails) para a busca por domínio no RootifyONE; admin_lex_detalhe idem.
-- APLICADO em 08/Nov/2026 à noite pelo conector (Arquitetura). Cada bloco tem o DESFAZER em comentário.
-- =====================================================================================

alter table public.lex_contas add column if not exists modalidade text not null default 'instalado' check (modalidade in ('instalado', 'nuvem'));
alter table public.lex_contas add column if not exists modalidade_desde timestamptz not null default now();
comment on column public.lex_contas.modalidade is 'instalado: o programa roda no computador do escritório (hoje). nuvem: o RADAR roda em servidor da SolverONE (ainda não vendido; fica no cadastro como oportunidade).';
-- DESFAZER: alter table public.lex_contas drop column modalidade, drop column modalidade_desde;

create or replace function public.admin_lex_salvar(p jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb; v_mod_antes text; v_mod_depois text;
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
    exigir_aprovacao  = coalesce((p->>'exigir_aprovacao')::boolean, exigir_aprovacao),
    dominios          = case when p ? 'dominios' then coalesce((select array_agg(pg_catalog.lower(pg_catalog.btrim(d))) from jsonb_array_elements_text(p->'dominios') d where pg_catalog.btrim(d) <> ''), '{}') else dominios end,
    modalidade        = coalesce(p->>'modalidade', modalidade),
    modalidade_desde  = case when p ? 'modalidade' and p->>'modalidade' <> modalidade then pg_catalog.now() else modalidade_desde end
  where codigo = p->>'codigo';
  select to_jsonb(c), c.modalidade into depois, v_mod_depois from public.lex_contas c where c.codigo = p->>'codigo';
  if v_mod_depois <> v_mod_antes then
    insert into public.lex_eventos (codigo, tipo, detalhe) values (p->>'codigo', 'licenca_alterada', 'modalidade: ' || v_mod_antes || ' -> ' || v_mod_depois);
  end if;
  perform public.lab_registrar_log('lex_salvar_licenca', null, depois, antes);
  return depois;
end $$;
revoke all on function public.admin_lex_salvar(jsonb) from public, anon;
grant execute on function public.admin_lex_salvar(jsonb) to authenticated;
-- DESFAZER: reaplicar o bloco admin_lex_salvar de 2026-11-08b-lex-licenca-em-uso.sql.

create or replace function public.admin_lex_listar()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'codigo', c.codigo, 'escritorio', c.escritorio, 'doc_tipo', c.doc_tipo, 'documento', c.documento,
      'ativo', c.ativo, 'validade', c.validade, 'max_pessoas', c.max_pessoas, 'max_computadores', c.max_computadores,
      'mensagem', c.mensagem, 'criado_em', c.criado_em, 'dominios', c.dominios, 'email_boas_vindas', c.email_boas_vindas,
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
-- DESFAZER: reaplicar o bloco admin_lex_listar de 2026-11-08b-lex-licenca-em-uso.sql.

-- Conferência (só leitura): tudo "true"
select
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_contas' and column_name = 'modalidade') as modalidade_ok,
  (select count(*) = count(*) filter (where modalidade = 'instalado') from public.lex_contas) as todas_instaladas_ok,
  (select prosrc like '%dominios_pessoas%' from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_lex_listar') as listar_ok;
