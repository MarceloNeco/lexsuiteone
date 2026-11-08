-- RADAR JUDICIAL: funções da tela "Licenças do RADAR" no RootifyONE. Só dono ou admin da equipe
-- (public.eh_admin_equipe()); cada alteração vai para o registro de acessos (public.lab_registrar_log).

create or replace function public.admin_lex_listar()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'codigo', c.codigo, 'escritorio', c.escritorio, 'doc_tipo', c.doc_tipo, 'documento', c.documento,
      'ativo', c.ativo, 'validade', c.validade, 'max_pessoas', c.max_pessoas, 'mensagem', c.mensagem, 'criado_em', c.criado_em,
      'pessoas_ativas', (select count(*) from public.lex_pessoas p where p.codigo = c.codigo and p.ativa),
      'pessoas_total', (select count(*) from public.lex_usuarios u where u.codigo = c.codigo),
      'computadores', (select count(*) from public.lex_instalacoes i where i.codigo = c.codigo),
      'ultima_vez', (select max(i.ultima_vez) from public.lex_instalacoes i where i.codigo = c.codigo),
      'erros_7d', (select count(*) from public.lex_registros r where r.codigo = c.codigo and r.criado_em > now() - interval '7 days')
    ) order by c.criado_em desc)
    from public.lex_contas c), '[]'::jsonb);
end $$;

create or replace function public.admin_lex_detalhe(p_codigo text)
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return jsonb_build_object(
    'pessoas', coalesce((select jsonb_agg(to_jsonb(p) order by p.ativa desc, p.ultima_vez desc nulls last) from public.lex_pessoas p where p.codigo = p_codigo), '[]'::jsonb),
    'computadores', coalesce((select jsonb_agg(jsonb_build_object('instalacao', i.instalacao, 'email', i.email, 'versao', i.versao,
                      'primeira_vez', i.primeira_vez, 'ultima_vez', i.ultima_vez) order by i.ultima_vez desc) from public.lex_instalacoes i where i.codigo = p_codigo), '[]'::jsonb),
    'eventos', coalesce((select jsonb_agg(to_jsonb(e) order by e.criado_em desc) from (select * from public.lex_eventos where codigo = p_codigo order by criado_em desc limit 100) e), '[]'::jsonb),
    'erros', coalesce((select jsonb_agg(to_jsonb(r) order by r.criado_em desc) from (select * from public.lex_registros where codigo = p_codigo order by criado_em desc limit 50) r), '[]'::jsonb));
end $$;

-- Erros do instalador que chegaram sem código (falhas antes de digitar o código).
create or replace function public.admin_lex_erros_sem_codigo()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((select jsonb_agg(to_jsonb(r) order by r.criado_em desc)
                   from (select * from public.lex_registros where codigo is null order by criado_em desc limit 50) r), '[]'::jsonb);
end $$;

create or replace function public.admin_lex_salvar(p jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select to_jsonb(c) into antes from public.lex_contas c where c.codigo = p->>'codigo';
  if antes is null then raise exception 'Licença não encontrada'; end if;
  update public.lex_contas set
    escritorio  = coalesce(nullif(trim(p->>'escritorio'), ''), escritorio),
    ativo       = coalesce((p->>'ativo')::boolean, ativo),
    validade    = case when p ? 'validade' then nullif(p->>'validade', '')::date else validade end,
    max_pessoas = case when p ? 'max_pessoas' then nullif(p->>'max_pessoas', '')::integer else max_pessoas end,
    mensagem    = case when p ? 'mensagem' then coalesce(p->>'mensagem', '') else mensagem end
  where codigo = p->>'codigo';
  select to_jsonb(c) into depois from public.lex_contas c where c.codigo = p->>'codigo';
  perform public.lab_registrar_log('lex_salvar_licenca', null, depois, antes);
  return depois;
end $$;

create or replace function public.admin_lex_criar(p_escritorio text, p_validade date default null, p_max_pessoas integer default null)
returns text language plpgsql security definer set search_path = '' as $$
declare novo text;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if coalesce(trim(p_escritorio), '') = '' then raise exception 'Informe o nome do escritório'; end if;
  novo := public.lex_criar_conta(p_escritorio, p_validade);
  if p_max_pessoas is not null then update public.lex_contas set max_pessoas = p_max_pessoas where codigo = novo; end if;
  perform public.lab_registrar_log('lex_criar_licenca', null, jsonb_build_object('codigo', novo, 'escritorio', p_escritorio), null);
  return novo;
end $$;

revoke all on function public.admin_lex_listar(), public.admin_lex_detalhe(text), public.admin_lex_erros_sem_codigo(),
  public.admin_lex_salvar(jsonb), public.admin_lex_criar(text, date, integer) from public, anon;
grant execute on function public.admin_lex_listar(), public.admin_lex_detalhe(text), public.admin_lex_erros_sem_codigo(),
  public.admin_lex_salvar(jsonb), public.admin_lex_criar(text, date, integer) to authenticated;
