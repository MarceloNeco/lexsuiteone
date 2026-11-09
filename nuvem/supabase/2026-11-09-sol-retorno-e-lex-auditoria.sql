-- =====================================================================================
-- 2026-11-09-sol-retorno-e-lex-auditoria.sql  —  projeto solverone-app (Supabase)
-- Desenho: documentacao/DESENHO-RETORNO-E-ROOTIFY.md (decisões do dono de 09/Nov).
-- PRÉ-REQUISITO: 2026-11-08b e 2026-11-08c aplicados. APLICADO em 09/Nov/2026 pelo conector (prefixo em sol_apps sem "_").
-- da Arquitetura (não tem DROP; não pede confirmação). Cada bloco tem o DESFAZER em comentário.
--
-- O QUE FAZ:
--   1. sol_apps ganha suite e acesso (web | instalado | nuvem) e a linha do RADAR JUDICIAL (código radar-judicial).
--   2. sol_retorno_diario: totais por situação que os produtos mandam à SolverONE. Agnóstico: app, licença, data,
--      até três dimensões (dim1..dim3, nomeadas por app em sol_apps.retorno_dimensoes), situação e quantidade.
--      SEM dado pessoal, SEM nome de empresa, SEM número de processo: só contagens.
--   3. Auditoria da ficha: lex_eventos ganha quem e motivo; admin_lex_ativar (ativar/pausar com motivo) e
--      admin_lex_salvar registram quem (equipe:<uuid>) e motivo.
--   4. lex_contas.email_responsavel (quem responde pela licença no escritório); o e-mail de boas-vindas segue em
--      email_boas_vindas (padrão: o mesmo).
--   5. admin_lex_convidar_lote(codigo, emails[]) → devolve válidos, inválidos e repetidos; grava os válidos como
--      pessoas aprovadas pela equipe (sem computador ainda).
--   6. Funções de leitura para o RootifyONE: admin_sol_retorno (totais por período e dimensão, qualquer app) e
--      sol_retorno_gravar (usada pela lex-conta via service_role).
-- =====================================================================================

-- 1. sol_apps: suíte e tipo de acesso; RADAR JUDICIAL
alter table public.sol_apps add column if not exists suite text;
alter table public.sol_apps add column if not exists acesso text not null default 'web' check (acesso in ('web', 'instalado', 'nuvem'));
alter table public.sol_apps add column if not exists retorno_dimensoes jsonb not null default '[]';
comment on column public.sol_apps.suite is 'Linha de negócio / suíte (ex.: lexsuiteone). Vazio = app da plataforma de consumo.';
comment on column public.sol_apps.acesso is 'web: app no navegador; instalado: programa no computador do cliente; nuvem: roda em servidor da SolverONE.';
comment on column public.sol_apps.retorno_dimensoes is 'Nomes das dimensões dim1..dim3 de sol_retorno_diario para este app (ex.: ["tribunal","frente","faixa_valor"]).';
insert into public.sol_apps (codigo, nome, prefixo, ativo, suite, acesso, retorno_dimensoes)
values ('radar-judicial', 'RADAR JUDICIAL (LexSuiteONE)', 'lex', true, 'lexsuiteone', 'instalado', '["tribunal","frente","faixa_valor"]'::jsonb)
on conflict (codigo) do update set suite = excluded.suite, acesso = excluded.acesso, retorno_dimensoes = excluded.retorno_dimensoes;
-- DESFAZER: delete from public.sol_apps where codigo = 'radar-judicial'; alter table public.sol_apps drop column suite, drop column acesso, drop column retorno_dimensoes;

-- 2. sol_retorno_diario (agnóstico)
create table if not exists public.sol_retorno_diario (
  app        text not null references public.sol_apps(codigo),
  licenca    text not null,                     -- código da licença no produto (no RADAR, LEX-XXXX-XXXX)
  data       date not null,
  dim1       text not null default '',
  dim2       text not null default '',
  dim3       text not null default '',
  situacao   text not null check (length(situacao) between 1 and 40),
  qtd        integer not null check (qtd >= 0),
  atualizado_em timestamptz not null default now(),
  primary key (app, licenca, data, dim1, dim2, dim3, situacao)
);
comment on table public.sol_retorno_diario is 'Totais por situação que cada produto manda à SolverONE (só contagens; nenhum dado pessoal, nome de empresa ou número de processo). Nunca apagado.';
create index if not exists sol_retorno_diario_app_data on public.sol_retorno_diario (app, data desc);
alter table public.sol_retorno_diario enable row level security;
revoke all on public.sol_retorno_diario from public, anon, authenticated;
grant select, insert, update on public.sol_retorno_diario to service_role;
-- DESFAZER: drop table if exists public.sol_retorno_diario;

create or replace function public.sol_retorno_gravar(p_app text, p_licenca text, p_linhas jsonb)
returns integer language plpgsql security definer set search_path = '' as $$
declare l jsonb; n integer := 0;
begin
  if not exists (select 1 from public.sol_apps a where a.codigo = p_app and a.ativo) then raise exception 'App desconhecido'; end if;
  if p_licenca is null or length(p_licenca) > 40 then raise exception 'Licença inválida'; end if;
  if jsonb_typeof(p_linhas) <> 'array' or jsonb_array_length(p_linhas) > 2000 then raise exception 'Linhas inválidas'; end if;
  for l in select * from jsonb_array_elements(p_linhas) loop
    insert into public.sol_retorno_diario (app, licenca, data, dim1, dim2, dim3, situacao, qtd, atualizado_em)
    values (p_app, p_licenca, (l->>'data')::date,
            pg_catalog.left(coalesce(l->>'dim1', ''), 40), pg_catalog.left(coalesce(l->>'dim2', ''), 40), pg_catalog.left(coalesce(l->>'dim3', ''), 40),
            pg_catalog.left(l->>'situacao', 40), greatest(0, (l->>'qtd')::integer), pg_catalog.now())
    on conflict (app, licenca, data, dim1, dim2, dim3, situacao) do update set qtd = excluded.qtd, atualizado_em = pg_catalog.now();
    n := n + 1;
  end loop;
  return n;
end $$;
revoke all on function public.sol_retorno_gravar(text, text, jsonb) from public, anon, authenticated;
grant execute on function public.sol_retorno_gravar(text, text, jsonb) to service_role;
-- DESFAZER: drop function if exists public.sol_retorno_gravar(text, text, jsonb);

create or replace function public.admin_sol_retorno(p_app text, p_licenca text default null, p_de date default null, p_ate date default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return jsonb_build_object(
    'dimensoes', (select a.retorno_dimensoes from public.sol_apps a where a.codigo = p_app),
    'por_situacao', coalesce((select jsonb_agg(jsonb_build_object('situacao', s.situacao, 'qtd', s.qtd) order by s.qtd desc)
      from (select situacao, sum(qtd) as qtd from public.sol_retorno_diario r
             where r.app = p_app and (p_licenca is null or r.licenca = p_licenca) and (p_de is null or r.data >= p_de) and (p_ate is null or r.data <= p_ate)
             group by situacao) s), '[]'::jsonb),
    'por_dia', coalesce((select jsonb_agg(jsonb_build_object('data', d.data, 'situacao', d.situacao, 'qtd', d.qtd) order by d.data)
      from (select data, situacao, sum(qtd) as qtd from public.sol_retorno_diario r
             where r.app = p_app and (p_licenca is null or r.licenca = p_licenca) and (p_de is null or r.data >= p_de) and (p_ate is null or r.data <= p_ate)
             group by data, situacao) d), '[]'::jsonb),
    'por_dimensao', coalesce((select jsonb_agg(jsonb_build_object('dim1', x.dim1, 'dim2', x.dim2, 'dim3', x.dim3, 'situacao', x.situacao, 'qtd', x.qtd) order by x.qtd desc)
      from (select dim1, dim2, dim3, situacao, sum(qtd) as qtd from public.sol_retorno_diario r
             where r.app = p_app and (p_licenca is null or r.licenca = p_licenca) and (p_de is null or r.data >= p_de) and (p_ate is null or r.data <= p_ate)
             group by dim1, dim2, dim3, situacao) x), '[]'::jsonb));
end $$;
revoke all on function public.admin_sol_retorno(text, text, date, date) from public, anon;
grant execute on function public.admin_sol_retorno(text, text, date, date) to authenticated;
-- DESFAZER: drop function if exists public.admin_sol_retorno(text, text, date, date);

-- 3. Auditoria: quem e motivo em lex_eventos; ativar/pausar com motivo
alter table public.lex_eventos add column if not exists quem text;
alter table public.lex_eventos add column if not exists motivo text;
-- DESFAZER: alter table public.lex_eventos drop column quem, drop column motivo;

create or replace function public.admin_lex_ativar(p_codigo text, p_ativo boolean, p_motivo text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if coalesce(pg_catalog.btrim(p_motivo), '') = '' then raise exception 'Escreva o motivo'; end if;
  select to_jsonb(c) into antes from public.lex_contas c where c.codigo = p_codigo;
  if antes is null then raise exception 'Licença não encontrada'; end if;
  update public.lex_contas set ativo = p_ativo where codigo = p_codigo;
  select to_jsonb(c) into depois from public.lex_contas c where c.codigo = p_codigo;
  insert into public.lex_eventos (codigo, tipo, detalhe, quem, motivo)
  values (p_codigo, 'licenca_alterada', case when p_ativo then 'licença ativada' else 'licença pausada' end, 'equipe:' || coalesce(auth.uid()::text, '?'), pg_catalog.left(pg_catalog.btrim(p_motivo), 300));
  perform public.lab_registrar_log(case when p_ativo then 'lex_ativar_licenca' else 'lex_pausar_licenca' end, null, depois, antes);
  return depois;
end $$;
revoke all on function public.admin_lex_ativar(text, boolean, text) from public, anon;
grant execute on function public.admin_lex_ativar(text, boolean, text) to authenticated;
-- DESFAZER: drop function if exists public.admin_lex_ativar(text, boolean, text);

-- 4. E-mail do responsável
alter table public.lex_contas add column if not exists email_responsavel text check (email_responsavel is null or (email_responsavel = lower(email_responsavel) and email_responsavel like '%_@_%._%'));
comment on column public.lex_contas.email_responsavel is 'Quem responde pela licença no escritório (recebe avisos e o e-mail de boas-vindas, salvo se email_boas_vindas disser outro).';
update public.lex_contas set email_responsavel = email_boas_vindas where email_responsavel is null and email_boas_vindas is not null;
-- DESFAZER: alter table public.lex_contas drop column email_responsavel;

-- admin_lex_salvar: aceita email_responsavel e motivo; registra quem
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
-- DESFAZER: reaplicar o bloco admin_lex_salvar de 2026-11-08c-lex-modalidade.sql.

-- 5. Cadastro de e-mails em lote (válidos viram pessoas aprovadas pela equipe; sem computador ainda)
create or replace function public.admin_lex_convidar_lote(p_codigo text, p_emails text[])
returns jsonb language plpgsql security definer set search_path = '' as $$
declare e text; v text; validos text[] := '{}'; invalidos text[] := '{}'; repetidos text[] := '{}'; outra text[] := '{}'; v_doms text[];
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select dominios into v_doms from public.lex_contas where codigo = p_codigo;
  if v_doms is null then raise exception 'Licença não encontrada'; end if;
  if p_emails is null or array_length(p_emails, 1) > 200 then raise exception 'Mande até 200 e-mails'; end if;
  foreach e in array p_emails loop
    v := pg_catalog.lower(pg_catalog.btrim(e));
    if v = '' then continue; end if;
    if v !~ '^[^@[:space:]]{1,64}@[^@[:space:]]+\.[^@[:space:]]{2,}$' then invalidos := invalidos || v; continue; end if;
    if exists (select 1 from public.lex_usuarios u where u.email = v and u.codigo <> p_codigo) then outra := outra || v; continue; end if;
    if exists (select 1 from public.lex_usuarios u where u.email = v and u.codigo = p_codigo) then repetidos := repetidos || v; continue; end if;
    insert into public.lex_usuarios (email, codigo, nome, papel, aprovacao, aprovado_por, aprovado_em)
    values (v, p_codigo, pg_catalog.split_part(v, '@', 1), '', 'aprovado', 'equipe:' || coalesce(auth.uid()::text, '?'), pg_catalog.now());
    insert into public.lex_eventos (codigo, email, tipo, detalhe, quem) values (p_codigo, v, 'cadastro', 'cadastrado em lote pela equipe', 'equipe:' || coalesce(auth.uid()::text, '?'));
    validos := validos || v;
  end loop;
  perform public.lab_registrar_log('lex_convidar_lote', null, jsonb_build_object('codigo', p_codigo, 'validos', array_length(validos, 1)), null);
  return jsonb_build_object('validos', to_jsonb(validos), 'invalidos', to_jsonb(invalidos), 'repetidos', to_jsonb(repetidos), 'em_outra_licenca', to_jsonb(outra),
                            'fora_do_dominio', (select to_jsonb(array_agg(x)) from unnest(validos) x where cardinality(v_doms) > 0 and not (pg_catalog.split_part(x, '@', 2) = any(v_doms))));
end $$;
revoke all on function public.admin_lex_convidar_lote(text, text[]) from public, anon;
grant execute on function public.admin_lex_convidar_lote(text, text[]) to authenticated;
-- DESFAZER: drop function if exists public.admin_lex_convidar_lote(text, text[]);

-- Conferência (só leitura): tudo "true"
select
  exists (select 1 from public.sol_apps where codigo = 'radar-judicial' and acesso = 'instalado') as app_ok,
  exists (select 1 from information_schema.tables where table_schema = 'public' and table_name = 'sol_retorno_diario') as retorno_ok,
  (select count(*) = 4 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public'
     and p.proname in ('sol_retorno_gravar', 'admin_sol_retorno', 'admin_lex_ativar', 'admin_lex_convidar_lote')) as funcoes_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_eventos' and column_name = 'motivo') as auditoria_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_contas' and column_name = 'email_responsavel') as responsavel_ok,
  not exists (select 1 from information_schema.role_table_grants where table_schema = 'public' and (table_name like 'lex\_%' or table_name = 'sol_retorno_diario') and grantee in ('anon', 'authenticated')) as sem_acesso_direto_ok;
