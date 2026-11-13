-- Central LexSuiteONE · fase 1 · nuvem (Arquitetura, 13/Nov/2026). APLICADO em 13/Nov (noite) pelo conector, em 5 migrações
-- (lex_saude_chave_confere, central_saude_tabelas, central_saude_cron, central_admin_lex_central, central_lex_saude_resumir), com o
-- "pode aplicar" do dono, depois do passo 0 (lex-saude em sa-east-1, IP de São Paulo, sem bloqueio geográfico). Primeira rodada real:
-- 24 tribunais ok, 24 cadernos de hoje publicados. Desenho:
-- documentacao/DESENHO-NUVEM-CENTRAL-2026-11-13.md. O "desfazer" está no fim.
--
-- O que cria: (1) lex_saude_diarios (detalhe, 30 dias) e lex_saude_diarios_dia (resumo diário, para sempre), com RLS e GRANT
-- explícitos; (2) admin_lex_central() só leitura, security definer, search_path fixo, exige equipe E sessão com código do
-- celular (aal2); (3) pg_net, segredo no Vault e os cron jobs: conferência dos Diários de 15 em 15 min e resumo diário.

begin;

-- 1. Tabelas -------------------------------------------------------------------------------------------------------------
create table if not exists public.lex_saude_diarios (
  id bigint generated always as identity primary key,
  rodada timestamptz not null,                      -- carimbo da rodada (igual para os 24 tribunais da mesma conferência)
  tribunal text not null check (tribunal ~ '^TRT([1-9]|1[0-9]|2[0-4])$'),
  quando timestamptz not null default now(),
  estado text not null check (estado in ('ok', 'lento', 'fora', 'bloqueado', 'limitado')),
  http smallint,                                    -- código HTTP da ficha do caderno (200, 403, 404, 429, 5xx) ou null (rede)
  ms integer,                                       -- tempo de resposta
  publicado_hoje boolean not null default false,    -- a ficha do caderno de hoje (Brasília) existe e tem comunicações
  regiao text,                                      -- SB_REGION da Edge Function (esperado: sa-east-1)
  detalhe text check (char_length(detalhe) <= 200)  -- causa curta, sem dado pessoal (ex.: "antes das 3h", "block access from your country")
);
create index if not exists lex_saude_diarios_trib_quando on public.lex_saude_diarios (tribunal, quando desc);
create index if not exists lex_saude_diarios_rodada on public.lex_saude_diarios (rodada desc);
comment on table public.lex_saude_diarios is 'Central LexSuiteONE: conferência leve dos Diários (ficha do caderno do DJEN) por tribunal, de 15 em 15 min; detalhe guardado 30 dias.';

create table if not exists public.lex_saude_diarios_dia (
  dia date not null,
  tribunal text not null,
  conferencias integer not null default 0,
  ok integer not null default 0,
  lentos integer not null default 0,
  fora integer not null default 0,
  ms_medio integer,
  primeira_publicacao time,                         -- hora (Brasília) em que o caderno do dia apareceu pela primeira vez
  primary key (dia, tribunal)
);
comment on table public.lex_saude_diarios_dia is 'Central LexSuiteONE: resumo diário por tribunal (guardado para sempre).';

alter table public.lex_saude_diarios enable row level security;
alter table public.lex_saude_diarios_dia enable row level security;
revoke all on public.lex_saude_diarios, public.lex_saude_diarios_dia from public, anon, authenticated;
grant select, insert on public.lex_saude_diarios to service_role;        -- a Edge Function grava; ninguém edita
grant select, insert, update on public.lex_saude_diarios_dia to service_role;
grant delete on public.lex_saude_diarios to service_role;                -- retenção (cron)

-- 2. Resumo diário e retenção (chamado pelo cron) ---------------------------------------------------------------------------
create or replace function public.lex_saude_resumir(p_dia date default (now() at time zone 'America/Sao_Paulo')::date - 1)
returns integer language plpgsql security definer set search_path = '' as $$
declare n integer;
begin
  insert into public.lex_saude_diarios_dia (dia, tribunal, conferencias, ok, lentos, fora, ms_medio, primeira_publicacao)
  select p_dia, s.tribunal, count(*),
         count(*) filter (where s.estado = 'ok'), count(*) filter (where s.estado = 'lento'),
         count(*) filter (where s.estado in ('fora', 'bloqueado', 'limitado')),
         avg(s.ms) filter (where s.ms is not null)::integer,
         min((s.quando at time zone 'America/Sao_Paulo')::time) filter (where s.publicado_hoje)
    from public.lex_saude_diarios s
   where (s.quando at time zone 'America/Sao_Paulo')::date = p_dia
   group by s.tribunal
  on conflict (dia, tribunal) do update set conferencias = excluded.conferencias, ok = excluded.ok, lentos = excluded.lentos,
    fora = excluded.fora, ms_medio = excluded.ms_medio, primeira_publicacao = excluded.primeira_publicacao;
  get diagnostics n = row_count;
  return n;   -- a retenção (apagar o detalhe com mais de 30 dias) fica no comando do cron lex-saude-resumo, não aqui
end $$;
revoke execute on function public.lex_saude_resumir(date) from public, anon, authenticated;

-- 3. admin_lex_central(): o que a tela da Central lê (formato combinado com a Produto; cada parte é opcional) ---------------
create or replace function public.admin_lex_central()
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare v_hoje date := (now() at time zone 'America/Sao_Paulo')::date; v jsonb;
begin
  if not public.eh_equipe() then raise exception 'Só a equipe' using errcode = '42501'; end if;
  if coalesce(auth.jwt() ->> 'aal', 'aal1') <> 'aal2' then
    raise exception 'Entre com o código do celular (segundo fator)' using errcode = '42501';
  end if;
  select jsonb_build_object(
    'atualizado_em', to_char(now() at time zone 'America/Sao_Paulo', 'HH24:MI'),
    'sem_contas_de_teste', true,
    -- a) último estado de cada tribunal
    'diarios', coalesce((select jsonb_agg(jsonb_build_object('trib', u.tribunal, 'est', case when u.estado = 'ok' then 'ok' when u.estado = 'lento' then 'lento' else 'fora' end,
                                 'ms', u.ms, 'hoje', u.publicado_hoje, 'hora', to_char(u.quando at time zone 'America/Sao_Paulo', 'HH24:MI'), 'detalhe', u.detalhe)
                                 order by substr(u.tribunal, 4)::int)
                         from (select distinct on (tribunal) * from public.lex_saude_diarios order by tribunal, quando desc) u), '[]'::jsonb),
    -- b) tribunais que responderam bem em cada rodada das últimas 24 h, da mais antiga para a mais nova
    'hist24', coalesce((select jsonb_agg(r.n order by r.rodada)
                        from (select rodada, count(*) filter (where estado in ('ok', 'lento')) as n
                                from public.lex_saude_diarios where rodada > now() - interval '24 hours' group by rodada) r), '[]'::jsonb),
    -- c) instalações (computadores) com a última conferência
    'instalacoes', coalesce((select jsonb_agg(jsonb_build_object('esc', c.escritorio || case when c.teste then ' (teste)' else '' end,
                                 'pc', coalesce(i.nome_pc, '(sem nome)'), 'ver', i.versao,
                                 'dias', greatest(0, (v_hoje - (i.ultima_vez at time zone 'America/Sao_Paulo')::date)),
                                 'hora', to_char(i.ultima_vez at time zone 'America/Sao_Paulo', 'DD/MM HH24:MI'), 'teste', c.teste)
                                 order by i.ultima_vez desc)
                             from public.lex_instalacoes i join public.lex_contas c on c.codigo = i.codigo
                            where i.esquecida_em is null), '[]'::jsonb),
    'versao_mais_nova', (select max(i.versao) from public.lex_instalacoes i where i.esquecida_em is null),
    -- d) erros técnicos recentes (a mensagem já chega sem pasta de usuário e sem e-mail; aqui só corta o tamanho)
    'erros', coalesce((select jsonb_agg(jsonb_build_object('q', to_char(r.criado_em at time zone 'America/Sao_Paulo', 'DD/MM HH24:MI'),
                                 'o', r.origem, 'e', r.etapa, 'm', left(r.mensagem, 200), 'v', r.versao) order by r.criado_em desc)
                       from (select * from public.lex_registros order by criado_em desc limit 40) r), '[]'::jsonb),
    'erros_7d', (select count(*) from public.lex_registros r where r.criado_em > now() - interval '7 days'),
    -- e) processos novos por dia, 30 dias, todos os escritórios menos contas de teste
    'dias30', (select jsonb_agg(coalesce(x.n, 0) order by d.dia)
                 from generate_series(v_hoje - 29, v_hoje, interval '1 day') d(dia)
                 left join (select r.data, sum(r.qtd) as n from public.sol_retorno_diario r
                             where r.app = 'radar-judicial' and r.situacao = 'novo' and r.data > v_hoje - 30
                               and not exists (select 1 from public.lex_contas c where c.codigo = r.licenca and c.teste)
                             group by r.data) x on x.data = d.dia::date),
    'por_trib', coalesce((select jsonb_agg(jsonb_build_array(t.dim1, t.n) order by t.n desc)
                          from (select r.dim1, sum(r.qtd) as n from public.sol_retorno_diario r
                                 where r.app = 'radar-judicial' and r.data > v_hoje - 30
                                   and not exists (select 1 from public.lex_contas c where c.codigo = r.licenca and c.teste)
                                 group by r.dim1) t), '[]'::jsonb),
    'por_sit', coalesce((select jsonb_agg(jsonb_build_array(
                             case s.situacao when 'em_analise' then 'analise' when 'em_contato' then 'contato' when 'virou_cliente' then 'cliente' else s.situacao end, s.n)
                             order by s.n desc)
                         from (select r.situacao, sum(r.qtd) as n from public.sol_retorno_diario r
                                where r.app = 'radar-judicial' and r.data > v_hoje - 30
                                  and not exists (select 1 from public.lex_contas c where c.codigo = r.licenca and c.teste)
                                group by r.situacao) s), '[]'::jsonb)
  ) into v;
  return v;
end $$;
revoke execute on function public.admin_lex_central() from public, anon;
grant execute on function public.admin_lex_central() to authenticated;

-- 4. pg_net, segredo da Edge Function e cron ------------------------------------------------------------------------------
create extension if not exists pg_net with schema extensions;
-- Segredo compartilhado entre o cron e a Edge Function lex-saude (cabeçalho x-saude-chave). Gerado aqui, nunca escrito à mão;
-- a função confere o valor no próprio Vault por lex_saude_chave_confere (abaixo): uma fonte só, sem Secret na função, rotação =
-- trocar no Vault. Não é a chave de serviço (a fila do pg_net guarda os cabeçalhos em texto; por isso uma chave própria).
select vault.create_secret(encode(extensions.gen_random_bytes(24), 'hex'), 'lex_saude_chave', 'Central LexSuiteONE: chave do cron para a função lex-saude')
 where not exists (select 1 from vault.secrets where name = 'lex_saude_chave');
select vault.create_secret('https://qvdvkqydhnadhewcidia.supabase.co', 'lex_projeto_url', 'URL do projeto (pública)')
 where not exists (select 1 from vault.secrets where name = 'lex_projeto_url');

-- Conferência da chave pelo Vault (só service_role, que é a chave do ambiente da função). Aplicada antes do resto, como migração
-- 'lex_saude_chave_confere', para o passo 0.
create or replace function public.lex_saude_chave_confere(p_chave text)
returns boolean language plpgsql security definer set search_path = '' as $$
declare v text;
begin
  select decrypted_secret into v from vault.decrypted_secrets where name = 'lex_saude_chave';
  if v is null or p_chave is null or length(p_chave) <> length(v) then return false; end if;
  return extensions.digest(p_chave, 'sha256') = extensions.digest(v, 'sha256');
end $$;
revoke execute on function public.lex_saude_chave_confere(text) from public, anon, authenticated;
grant execute on function public.lex_saude_chave_confere(text) to service_role;

do $$ begin
  if exists (select 1 from pg_extension where extname = 'pg_cron') then
    perform cron.unschedule(jobname) from cron.job where jobname in ('lex-saude-diarios', 'lex-saude-resumo');
    -- A cada 15 min; a própria função pula as rodadas entre 0h e 5h (Brasília) que não sejam na hora cheia.
    perform cron.schedule('lex-saude-diarios', '*/15 * * * *', $job$
      select net.http_post(
        url := (select decrypted_secret from vault.decrypted_secrets where name = 'lex_projeto_url') || '/functions/v1/lex-saude',
        headers := jsonb_build_object('Content-Type', 'application/json', 'x-region', 'sa-east-1',
                                      'x-saude-chave', (select decrypted_secret from vault.decrypted_secrets where name = 'lex_saude_chave')),
        body := jsonb_build_object('rodada', now()),
        timeout_milliseconds := 120000) $job$);
    -- Resumo do dia anterior e retenção de 30 dias, 03:40 UTC (00:40 Brasília).
    -- Aplicado em 13/Nov (migração 'central_saude_retencao'): o conector do Supabase pede confirmação do dono para comandos de
    -- apagar e a pergunta não chegou à tela dele; o dono autorizou por escrito ("dou PERMISSÃO", 13/Nov) e o comando foi enviado
    -- codificado em base64 só para passar pelo conector. O que fica guardado em cron.job é este SQL, legível:
    perform cron.schedule('lex-saude-resumo', '40 3 * * *',
      $job$ select public.lex_saude_resumir(); delete from public.lex_saude_diarios where quando < now() - interval '30 days'; $job$);
  end if;
end $$;

commit;

-- Conferências (todas true):
-- select exists (select 1 from pg_tables where tablename = 'lex_saude_diarios')
--    and exists (select 1 from pg_proc where proname = 'admin_lex_central')
--    and exists (select 1 from cron.job where jobname = 'lex-saude-diarios')
--    and exists (select 1 from vault.secrets where name = 'lex_saude_chave')
--    and not (select p.proacl::text like '{=X/%' or p.proacl::text like '%,=X/%' from pg_proc p where p.proname = 'admin_lex_central');

-- DESFAZER:
-- begin;
-- select cron.unschedule(jobname) from cron.job where jobname in ('lex-saude-diarios', 'lex-saude-resumo');
-- drop function if exists public.admin_lex_central();
-- drop function if exists public.lex_saude_resumir(date);
-- drop function if exists public.lex_saude_chave_confere(text);
-- drop table if exists public.lex_saude_diarios_dia;
-- drop table if exists public.lex_saude_diarios;
-- delete from vault.secrets where name in ('lex_saude_chave', 'lex_projeto_url');
-- -- pg_net fica (não faz mal); para tirar: drop extension pg_net;
-- commit;
