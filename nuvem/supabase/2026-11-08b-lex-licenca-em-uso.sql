-- =====================================================================================
-- 2026-11-08b-lex-licenca-em-uso.sql  —  projeto solverone-app (Supabase)
-- RADAR JUDICIAL: "licença em uso" (desenho em documentacao/DESENHO-LICENCA-EM-USO.md, aprovado pelo dono em 08/Nov).
-- PRÉ-REQUISITO: rodar antes 2026-11-08-lex-correcoes-seguranca.sql (cria lex_contas.max_computadores e os índices).
--
-- O QUE FAZ (tudo opcional: nenhum programa já instalado é bloqueado):
--   1. lex_contas: dominios (domínios de e-mail do escritório), email_boas_vindas, exigir_aprovacao (padrão desligado).
--   2. lex_usuarios: aprovacao ('aprovado' | 'aguardando' | 'recusado'), aprovado_por, aprovado_em. Linhas existentes: 'aprovado'.
--   3. lex_instalacoes: nome_pc, esquecida_em. Visão lex_computadores (ativo = visto nos últimos 30 dias e não esquecido).
--   4. lex_eventos aceita os tipos novos. Visão lex_pessoas ganha a coluna aprovacao.
--   5. lex_avisos: caixa de saída dos e-mails de aviso (pessoa nova, computador novo), com estado e erro.
--   6. lex_chamadas + lex_contar_chamada(): contador para os limites por chamada da função lex-conta.
--   7. Funções da equipe: admin_lex_aprovar_pessoa, admin_lex_esquecer_instalacao; admin_lex_criar (versão de 5 parâmetros,
--      ao lado da antiga), admin_lex_salvar, admin_lex_listar e admin_lex_detalhe ampliadas. Só dono/admin da equipe.
--   APLICADO em 08/Nov/2026 à noite pelo conector (Arquitetura); o bloco 4a (regra de lex_eventos) em seguida, com a confirmação do dono no computador.
--   8. Retenção: lex_avisos 90 dias e lex_chamadas 2 dias (pg_cron).
--   9. Conferência no fim.
-- COMO APLICAR (só depois de o dono revisar): SQL Editor → New query → colar inteiro → Run. Pode rodar de novo.
-- Nenhuma chave, senha ou dado de pessoa neste arquivo. Cada bloco tem o DESFAZER em comentário.
-- =====================================================================================

-- ---------------------------------------------------------------------
-- 1. lex_contas
-- ---------------------------------------------------------------------
alter table public.lex_contas add column if not exists max_computadores smallint not null default 20 check (max_computadores between 1 and 500);
alter table public.lex_contas add column if not exists dominios text[] not null default '{}';
alter table public.lex_contas add column if not exists email_boas_vindas text check (email_boas_vindas is null or (email_boas_vindas = lower(email_boas_vindas) and email_boas_vindas like '%_@_%._%'));
alter table public.lex_contas add column if not exists exigir_aprovacao boolean not null default false;
comment on column public.lex_contas.dominios is 'Domínios de e-mail do escritório (ex.: {krlaw.com.br}). E-mail desses domínios é aprovado na hora; outros ficam aguardando.';
comment on column public.lex_contas.email_boas_vindas is 'Para quem o e-mail de boas-vindas foi enviado. Devolvido ao programa só enquanto a licença não tem pessoa aprovada.';
comment on column public.lex_contas.exigir_aprovacao is 'Ligado: pessoa aguardando não lê. Desligado (padrão): lê normalmente e vê o aviso.';
-- DESFAZER: alter table public.lex_contas drop column dominios, drop column email_boas_vindas, drop column exigir_aprovacao;

-- ---------------------------------------------------------------------
-- 2. lex_usuarios: aprovação
-- ---------------------------------------------------------------------
alter table public.lex_usuarios add column if not exists aprovacao text not null default 'aprovado' check (aprovacao in ('aprovado', 'aguardando', 'recusado'));
alter table public.lex_usuarios add column if not exists aprovado_por text;
alter table public.lex_usuarios add column if not exists aprovado_em timestamptz;
comment on column public.lex_usuarios.aprovacao is 'aprovado: e-mail do domínio do escritório ou aprovado pela equipe. aguardando: fora do domínio, esperando a equipe. recusado: a tela pede outro e-mail.';
-- DESFAZER: alter table public.lex_usuarios drop column aprovacao, drop column aprovado_por, drop column aprovado_em;

-- ---------------------------------------------------------------------
-- 3. lex_instalacoes: nome do computador e "esquecer"
-- ---------------------------------------------------------------------
alter table public.lex_instalacoes add column if not exists nome_pc text check (nome_pc is null or length(nome_pc) <= 60);
alter table public.lex_instalacoes add column if not exists esquecida_em timestamptz;
comment on column public.lex_instalacoes.esquecida_em is 'Marcada pela equipe ("Esquecer computador"). Se o mesmo id voltar a chamar, a função limpa e registra o evento computador_voltou.';
-- DESFAZER: alter table public.lex_instalacoes drop column nome_pc, drop column esquecida_em;

create or replace view public.lex_computadores as
select i.instalacao, i.codigo, i.email, i.nome_pc, i.versao, i.primeira_vez, i.ultima_vez, i.esquecida_em,
       (i.esquecida_em is null and i.ultima_vez >= now() - interval '30 days') as ativo
from public.lex_instalacoes i;
alter view public.lex_computadores set (security_invoker = true);
revoke all on public.lex_computadores from public, anon, authenticated;
grant select on public.lex_computadores to service_role;
-- DESFAZER: drop view if exists public.lex_computadores;

-- ---------------------------------------------------------------------
-- 4. lex_eventos: tipos novos; lex_pessoas com aprovacao
-- ---------------------------------------------------------------------
-- Bloco 4a: o único com DROP (o conector pede confirmação, que só aparece num computador). APLICADO em 08/Nov à noite.
alter table public.lex_eventos drop constraint if exists lex_eventos_tipo_check;
alter table public.lex_eventos add constraint lex_eventos_tipo_check check (tipo in (
  'cadastro', 'troca_de_pessoa', 'alteracao_de_dados', 'acesso',
  'pessoa_aguardando', 'pessoa_aprovada', 'pessoa_recusada', 'computador_esquecido', 'computador_voltou',
  'aviso_enviado', 'aviso_falhou', 'licenca_alterada', 'limite'));
-- DESFAZER: recriar a restrição só com os 4 tipos originais (cadastro, troca_de_pessoa, alteracao_de_dados, acesso).

create or replace view public.lex_pessoas as
select u.email, u.codigo, u.nome, u.papel, u.criado_em, u.ultima_vez,
       exists (select 1 from public.lex_instalacoes i where i.email = u.email) as em_computador,
       (exists (select 1 from public.lex_instalacoes i where i.email = u.email)
        and coalesce(u.ultima_vez, u.criado_em) >= now() - interval '30 days') as ativa,
       u.aprovacao, u.aprovado_em
from public.lex_usuarios u;
alter view public.lex_pessoas set (security_invoker = true);
revoke all on public.lex_pessoas from public, anon, authenticated;
grant select on public.lex_pessoas to service_role;
-- DESFAZER: reaplicar o bloco "create or replace view public.lex_pessoas" de lex-licencas.sql (sem as duas colunas finais).

-- ---------------------------------------------------------------------
-- 5. lex_avisos: caixa de saída dos e-mails de aviso
--    "para" guarda o destinatário (responsável do escritório ou judicial@); "ref" guarda só o necessário para o
--    texto (nome da pessoa, domínio do e-mail, nome do computador). Nunca o conteúdo de listas.
-- ---------------------------------------------------------------------
create table if not exists public.lex_avisos (
  id          bigint generated always as identity primary key,
  criado_em   timestamptz not null default now(),
  codigo      text not null references public.lex_contas(codigo) on update cascade,
  tipo        text not null check (tipo in ('pessoa_nova', 'computador_novo')),
  para        text not null check (para = lower(para) and para like '%_@_%._%'),
  assunto     text not null default '',
  ref         jsonb not null default '{}',
  estado      text not null default 'pendente' check (estado in ('pendente', 'enviado', 'falhou')),
  tentativas  smallint not null default 0,
  erro        text not null default '',
  enviado_em  timestamptz
);
comment on table public.lex_avisos is 'RADAR JUDICIAL: e-mails de aviso (pessoa nova, computador novo) enviados pela função lex-conta via Resend. Estado e erro ficam aqui para a equipe ver.';
create index if not exists lex_avisos_codigo_criado on public.lex_avisos (codigo, criado_em desc);
alter table public.lex_avisos enable row level security;
revoke all on public.lex_avisos from public, anon, authenticated;
grant select, insert, update on public.lex_avisos to service_role;
-- DESFAZER: drop table if exists public.lex_avisos;

-- ---------------------------------------------------------------------
-- 6. Limites por chamada: lex_chamadas + lex_contar_chamada(chave, limite, segundos) → true quando pode seguir
--    Janela deslizante simples: uma linha por chave; zera quando a janela passa. Só a chave de serviço usa.
-- ---------------------------------------------------------------------
create table if not exists public.lex_chamadas (
  chave   text primary key check (length(chave) <= 120),
  janela  timestamptz not null default now(),
  qtd     integer not null default 0
);
comment on table public.lex_chamadas is 'RADAR JUDICIAL: contadores dos limites por chamada da função lex-conta (chave = instalação ou licença + ação). Sem dado pessoal.';
alter table public.lex_chamadas enable row level security;
revoke all on public.lex_chamadas from public, anon, authenticated;
grant select, insert, update, delete on public.lex_chamadas to service_role;
-- DESFAZER: drop table if exists public.lex_chamadas;

create or replace function public.lex_contar_chamada(p_chave text, p_limite integer, p_segundos integer)
returns boolean language plpgsql security definer set search_path = '' as $$
declare v_qtd integer;
begin
  if p_chave is null or p_limite is null or p_segundos is null or p_limite < 1 or p_segundos < 1 then
    return false;
  end if;
  insert into public.lex_chamadas (chave, janela, qtd) values (pg_catalog.left(p_chave, 120), pg_catalog.now(), 1)
  on conflict (chave) do update
    set qtd    = case when public.lex_chamadas.janela < pg_catalog.now() - make_interval(secs => p_segundos) then 1 else public.lex_chamadas.qtd + 1 end,
        janela = case when public.lex_chamadas.janela < pg_catalog.now() - make_interval(secs => p_segundos) then pg_catalog.now() else public.lex_chamadas.janela end
  returning qtd into v_qtd;
  return v_qtd <= p_limite;
end $$;
revoke all on function public.lex_contar_chamada(text, integer, integer) from public, anon, authenticated;
grant execute on function public.lex_contar_chamada(text, integer, integer) to service_role;
-- DESFAZER: drop function if exists public.lex_contar_chamada(text, integer, integer);

-- ---------------------------------------------------------------------
-- 7. Funções da equipe (só dono/admin: public.eh_admin_equipe(); log em acesso_log por public.lab_registrar_log)
-- ---------------------------------------------------------------------
create or replace function public.admin_lex_aprovar_pessoa(p_email text, p_decisao text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb; v_codigo text;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if p_decisao not in ('aprovado', 'recusado', 'aguardando') then raise exception 'Decisão inválida'; end if;
  select to_jsonb(u) into antes from public.lex_usuarios u where u.email = pg_catalog.lower(p_email);
  if antes is null then raise exception 'Pessoa não encontrada'; end if;
  update public.lex_usuarios
     set aprovacao = p_decisao, aprovado_por = 'equipe:' || coalesce(auth.uid()::text, '?'), aprovado_em = pg_catalog.now(), atualizado_em = pg_catalog.now()
   where email = pg_catalog.lower(p_email)
  returning to_jsonb(lex_usuarios.*), codigo into depois, v_codigo;
  insert into public.lex_eventos (codigo, email, tipo, detalhe)
  values (v_codigo, pg_catalog.lower(p_email), case p_decisao when 'aprovado' then 'pessoa_aprovada' when 'recusado' then 'pessoa_recusada' else 'pessoa_aguardando' end, 'pela equipe');
  perform public.lab_registrar_log('lex_aprovar_pessoa', null, depois, antes);
  return depois;
end $$;

create or replace function public.admin_lex_esquecer_instalacao(p_instalacao text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb; v_codigo text;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select to_jsonb(i) into antes from public.lex_instalacoes i where i.instalacao = p_instalacao;
  if antes is null then raise exception 'Computador não encontrado'; end if;
  update public.lex_instalacoes set esquecida_em = pg_catalog.now() where instalacao = p_instalacao
  returning to_jsonb(lex_instalacoes.*), codigo into depois, v_codigo;
  insert into public.lex_eventos (codigo, instalacao, tipo, detalhe) values (v_codigo, p_instalacao, 'computador_esquecido', 'pela equipe');
  perform public.lab_registrar_log('lex_esquecer_instalacao', null, depois, antes);
  return depois;
end $$;

-- admin_lex_criar ganha e-mail de boas-vindas e domínios. A função com 3 parâmetros (lex-admin.sql) CONTINUA existindo,
-- e esta, com 5 parâmetros SEM valores padrão, fica ao lado dela (assim não há ambiguidade e nada precisa ser apagado;
-- o conector do Supabase pede confirmação para qualquer DROP, e o dono não consegue confirmar pelo celular).
create or replace function public.admin_lex_criar(p_escritorio text, p_validade date, p_max_pessoas integer, p_email_boas_vindas text, p_dominios text[])
returns text language plpgsql security definer set search_path = '' as $$
declare novo text;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  if coalesce(pg_catalog.btrim(p_escritorio), '') = '' then raise exception 'Informe o nome do escritório'; end if;
  novo := public.lex_criar_conta(p_escritorio, p_validade);
  update public.lex_contas
     set max_pessoas = coalesce(p_max_pessoas, max_pessoas),
         email_boas_vindas = nullif(pg_catalog.lower(pg_catalog.btrim(coalesce(p_email_boas_vindas, ''))), ''),
         dominios = coalesce((select array_agg(pg_catalog.lower(pg_catalog.btrim(d))) from unnest(p_dominios) d where pg_catalog.btrim(d) <> ''), '{}')
   where codigo = novo;
  perform public.lab_registrar_log('lex_criar_licenca', null, jsonb_build_object('codigo', novo, 'escritorio', p_escritorio), null);
  return novo;
end $$;
-- DESFAZER: drop function public.admin_lex_criar(text, date, integer, text, text[]);

create or replace function public.admin_lex_salvar(p jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare antes jsonb; depois jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select to_jsonb(c) into antes from public.lex_contas c where c.codigo = p->>'codigo';
  if antes is null then raise exception 'Licença não encontrada'; end if;
  update public.lex_contas set
    escritorio        = coalesce(nullif(pg_catalog.btrim(p->>'escritorio'), ''), escritorio),
    ativo             = coalesce((p->>'ativo')::boolean, ativo),
    validade          = case when p ? 'validade' then nullif(p->>'validade', '')::date else validade end,
    max_pessoas       = case when p ? 'max_pessoas' then nullif(p->>'max_pessoas', '')::integer else max_pessoas end,
    max_computadores  = case when p ? 'max_computadores' then coalesce(nullif(p->>'max_computadores', '')::smallint, max_computadores) else max_computadores end,
    mensagem          = case when p ? 'mensagem' then coalesce(p->>'mensagem', '') else mensagem end,
    email_boas_vindas = case when p ? 'email_boas_vindas' then nullif(pg_catalog.lower(pg_catalog.btrim(p->>'email_boas_vindas')), '') else email_boas_vindas end,
    exigir_aprovacao  = coalesce((p->>'exigir_aprovacao')::boolean, exigir_aprovacao),
    dominios          = case when p ? 'dominios' then coalesce((select array_agg(pg_catalog.lower(pg_catalog.btrim(d))) from jsonb_array_elements_text(p->'dominios') d where pg_catalog.btrim(d) <> ''), '{}') else dominios end
  where codigo = p->>'codigo';
  select to_jsonb(c) into depois from public.lex_contas c where c.codigo = p->>'codigo';
  perform public.lab_registrar_log('lex_salvar_licenca', null, depois, antes);
  return depois;
end $$;

create or replace function public.admin_lex_listar()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'codigo', c.codigo, 'escritorio', c.escritorio, 'doc_tipo', c.doc_tipo, 'documento', c.documento,
      'ativo', c.ativo, 'validade', c.validade, 'max_pessoas', c.max_pessoas, 'max_computadores', c.max_computadores,
      'mensagem', c.mensagem, 'criado_em', c.criado_em, 'dominios', c.dominios, 'email_boas_vindas', c.email_boas_vindas,
      'exigir_aprovacao', c.exigir_aprovacao,
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

create or replace function public.admin_lex_detalhe(p_codigo text)
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return jsonb_build_object(
    'pessoas', coalesce((select jsonb_agg(to_jsonb(p) order by (p.aprovacao = 'aguardando') desc, p.ativa desc, p.ultima_vez desc nulls last) from public.lex_pessoas p where p.codigo = p_codigo), '[]'::jsonb),
    'computadores', coalesce((select jsonb_agg(to_jsonb(i) order by i.esquecida_em nulls first, i.ultima_vez desc) from public.lex_computadores i where i.codigo = p_codigo), '[]'::jsonb),
    'eventos', coalesce((select jsonb_agg(to_jsonb(e) order by e.criado_em desc) from (select * from public.lex_eventos where codigo = p_codigo order by criado_em desc limit 100) e), '[]'::jsonb),
    'erros', coalesce((select jsonb_agg(to_jsonb(r) order by r.criado_em desc) from (select * from public.lex_registros where codigo = p_codigo order by criado_em desc limit 50) r), '[]'::jsonb),
    'avisos', coalesce((select jsonb_agg(to_jsonb(a) order by a.criado_em desc) from (select * from public.lex_avisos where codigo = p_codigo order by criado_em desc limit 50) a), '[]'::jsonb));
end $$;

revoke all on function public.admin_lex_aprovar_pessoa(text, text), public.admin_lex_esquecer_instalacao(text),
  public.admin_lex_criar(text, date, integer, text, text[]), public.admin_lex_salvar(jsonb), public.admin_lex_listar(),
  public.admin_lex_detalhe(text) from public, anon;
grant execute on function public.admin_lex_aprovar_pessoa(text, text), public.admin_lex_esquecer_instalacao(text),
  public.admin_lex_criar(text, date, integer, text, text[]), public.admin_lex_salvar(jsonb), public.admin_lex_listar(),
  public.admin_lex_detalhe(text) to authenticated;
-- DESFAZER: drop function public.admin_lex_aprovar_pessoa(text, text), public.admin_lex_esquecer_instalacao(text);
--           reaplicar nuvem/supabase/lex-admin.sql (admin_lex_criar, admin_lex_salvar, admin_lex_listar, admin_lex_detalhe originais).

-- ---------------------------------------------------------------------
-- 8. Retenção (pg_cron; pulado num Postgres sem a extensão)
-- ---------------------------------------------------------------------
do $$
begin
  if exists (select 1 from pg_catalog.pg_extension where extname = 'pg_cron') then
    perform cron.unschedule(jobid) from cron.job where jobname in ('lex-avisos-retencao-90d', 'lex-chamadas-limpeza');
    perform cron.schedule('lex-avisos-retencao-90d', '20 7 * * *', $job$ delete from public.lex_avisos where criado_em < now() - interval '90 days' $job$);
    perform cron.schedule('lex-chamadas-limpeza', '30 7 * * *', $job$ delete from public.lex_chamadas where janela < now() - interval '2 days' $job$);
  end if;
end $$;
-- DESFAZER: select cron.unschedule(jobid) from cron.job where jobname in ('lex-avisos-retencao-90d', 'lex-chamadas-limpeza');

-- ---------------------------------------------------------------------
-- 9. Conferência (só leitura): tudo "true"
-- ---------------------------------------------------------------------
select
  (select count(*) = 3 from information_schema.columns where table_schema = 'public' and table_name = 'lex_contas'
     and column_name in ('dominios', 'email_boas_vindas', 'exigir_aprovacao'))                                   as contas_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_usuarios' and column_name = 'aprovacao') as usuarios_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_instalacoes' and column_name = 'esquecida_em') as instalacoes_ok,
  exists (select 1 from pg_catalog.pg_views where schemaname = 'public' and viewname = 'lex_computadores')         as view_computadores_ok,
  exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'lex_pessoas' and column_name = 'aprovacao') as view_pessoas_ok,
  exists (select 1 from information_schema.tables where table_schema = 'public' and table_name = 'lex_avisos')    as avisos_ok,
  exists (select 1 from pg_catalog.pg_proc p join pg_catalog.pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'lex_contar_chamada') as contador_ok,
  (select count(*) = 2 from pg_catalog.pg_proc p join pg_catalog.pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname in ('admin_lex_aprovar_pessoa', 'admin_lex_esquecer_instalacao')) as admin_ok,
  not exists (select 1 from information_schema.role_table_grants where table_schema = 'public' and table_name like 'lex\_%' and grantee in ('anon', 'authenticated')) as sem_acesso_direto_ok;
