-- 0.7.47, parte da nuvem ("CNJ fora e antivírus"). Dono: "pode aplicar" em 14/Nov/2026 (noite). APLICADO em 14/Nov pelo conector
-- (Arquitetura): migração `lex_0747_cnj_antivirus` + grant abaixo. Desenho: documentacao/DESENHO-LEITURA-E-ANTIVIRUS-2026-11-14.md
-- (1.1 diagnóstico e estado_cnj, 1.2 observador com alerta e sonda da consulta, 2.3 registro com antivírus, decisões 35 e 38).
-- Junto: lex-conta v20 (Supabase v22) e lex-saude v3 (textos em nuvem/supabase/functions/).

begin;

-- 1. Registro técnico: antivírus e sinal do bloqueio (nome de produto e o que falhou; nunca dado de pessoa).
alter table public.lex_registros
  add column if not exists antivirus text,
  add column if not exists antivirus_ligado boolean,
  add column if not exists sinal text;
alter table public.lex_registros drop constraint if exists lex_registros_sinal_check;
alter table public.lex_registros add constraint lex_registros_sinal_check
  check (sinal is null or sinal in ('zip_temp', 'bloqueio_gravacao', 'processo_morto', 'tarefa_falhou', 'rede_recusada', 'smartscreen'));

-- 2. Opção da instalação (decisão 35): e-mail quando o CNJ ficar fora por mais de 4 h em dia útil (um na queda, um na volta).
alter table public.lex_instalacoes add column if not exists avisar_cnj boolean not null default false;

-- 3. Aviso geral (decisão 38: só preparado; sem tela). Sem política de RLS: só a chave de serviço lê e escreve.
create table if not exists public.lex_avisos_gerais (
  id bigint generated always as identity primary key,
  app text not null default 'radar-judicial',
  tipo text not null check (tipo in ('cnj', 'prazos', 'manutencao', 'outro')),
  texto text not null check (length(texto) between 1 and 500),
  texto_en text check (texto_en is null or length(texto_en) <= 500),
  link_oficial text check (link_oficial is null or link_oficial ~ '^https://'),
  inicio timestamptz not null default now(), fim timestamptz,
  criado_em timestamptz not null default now(), criado_por text);
alter table public.lex_avisos_gerais enable row level security;

-- 4. Sonda da consulta pública (um tribunal por rodada, em rodízio), separada dos cadernos para não mexer no resumo diário.
create table if not exists public.lex_saude_consulta (
  id bigint generated always as identity primary key, rodada timestamptz not null, tribunal text not null,
  estado text not null check (estado in ('ok', 'lento', 'fora', 'bloqueado', 'limitado')),
  http smallint, ms integer, detalhe text, quando timestamptz not null default now(), regiao text);
create index if not exists lex_saude_consulta_quando on public.lex_saude_consulta (quando desc);
alter table public.lex_saude_consulta enable row level security;

-- 5. Quedas do CNJ (uma linha por queda: 6+ tribunais fora em duas rodadas seguidas) e registro dos e-mails (limite por chave).
create table if not exists public.lex_saude_quedas (
  id bigint generated always as identity primary key, inicio timestamptz not null, fim timestamptz,
  max_fora smallint not null default 0, tribunais text[] not null default '{}',
  aviso_solverone_em timestamptz, aviso_clientes_em timestamptz, volta_solverone_em timestamptz, volta_clientes_em timestamptz,
  destinatarios smallint not null default 0);
alter table public.lex_saude_quedas enable row level security;
create table if not exists public.lex_saude_alertas (
  id bigint generated always as identity primary key, tipo text not null, chave text not null, para text not null,
  assunto text not null, enviado_em timestamptz not null default now(), ok boolean not null default false, erro text);
create index if not exists lex_saude_alertas_chave on public.lex_saude_alertas (chave, enviado_em desc);
alter table public.lex_saude_alertas enable row level security;

-- 6. Estado do CNJ num objeto só (lido pela lex-conta em estado_cnj e pela lex-saude em ?modo=estado): última rodada, ok, fora,
--    desde (início da queda aberta), última sonda da consulta e avisos gerais vigentes. Só a chave de serviço executa.
create or replace function public.lex_saude_estado() returns jsonb
language sql stable security definer set search_path to '' as $$
  with ult as (select max(rodada) as r from public.lex_saude_diarios),
       l as (select * from public.lex_saude_diarios where rodada = (select r from ult)),
       q as (select inicio from public.lex_saude_quedas where fim is null order by inicio desc limit 1),
       c as (select tribunal, estado, quando from public.lex_saude_consulta order by quando desc limit 1)
  select jsonb_build_object(
    'rodada', (select r from ult), 'hora', to_char((select r from ult) at time zone 'America/Sao_Paulo', 'HH24:MI'),
    'total', (select count(*) from l), 'ok', (select count(*) from l where estado in ('ok', 'lento')),
    'fora', coalesce((select jsonb_agg(tribunal order by tribunal) from l where estado not in ('ok', 'lento')), '[]'::jsonb),
    'desde', (select to_char(inicio at time zone 'America/Sao_Paulo', 'HH24:MI') from q), 'desde_em', (select inicio from q),
    'consulta', (select jsonb_build_object('tribunal', tribunal, 'estado', estado, 'hora', to_char(quando at time zone 'America/Sao_Paulo', 'HH24:MI')) from c),
    'avisos', coalesce((select jsonb_agg(jsonb_build_object('tipo', a.tipo, 'texto', a.texto, 'texto_en', a.texto_en, 'link', a.link_oficial, 'inicio', a.inicio, 'fim', a.fim) order by a.inicio desc)
                        from public.lex_avisos_gerais a where a.app = 'radar-judicial' and a.inicio <= now() and (a.fim is null or a.fim > now())), '[]'::jsonb));
$$;
revoke all on function public.lex_saude_estado() from public, anon, authenticated;
grant execute on function public.lex_saude_estado() to service_role;   -- sem isto a lex-conta recebia "erro" (conferido no teste)
-- Tabelas novas não nascem com permissão para a chave de serviço (a sonda da rodada 22:45 UTC deu 403): concedida à mão.
grant select, insert, update, delete on table public.lex_saude_consulta, public.lex_saude_quedas, public.lex_saude_alertas, public.lex_avisos_gerais to service_role;
grant usage, select on all sequences in schema public to service_role;
revoke all on table public.lex_saude_consulta, public.lex_saude_quedas, public.lex_saude_alertas, public.lex_avisos_gerais from anon, authenticated;

commit;

-- Testes feitos em 14/Nov (licença de teste): registro com antivirus "Bitdefender Antivirus", antivirus_ligado "não" → false,
-- sinal tarefa_falhou gravados; verificar com avisar_cnj "sim" → lex_instalacoes.avisar_cnj = true; estado_cnj devolve
-- {ok: 24, total: 24, fora: [], desde: null, hora: "19:30", consulta: …} e, na segunda chamada em 5 min, HTTP 429.

-- DESFAZER:
-- begin;
-- drop function if exists public.lex_saude_estado();
-- drop table if exists public.lex_saude_alertas, public.lex_saude_quedas, public.lex_saude_consulta, public.lex_avisos_gerais;
-- alter table public.lex_instalacoes drop column if exists avisar_cnj;
-- alter table public.lex_registros drop constraint if exists lex_registros_sinal_check;
-- alter table public.lex_registros drop column if exists antivirus, drop column if exists antivirus_ligado, drop column if exists sinal;
-- commit;
-- -- e publicar de novo lex-conta v19 (Supabase v21) e lex-saude v2.
