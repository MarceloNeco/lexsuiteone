-- LexSuiteONE / SolverONE · contas de teste dentro da produção (pedido do dono, 12/Nov/2026; antes do staging).
-- Desenho: documentacao/DESENHO-CONTAS-DE-TESTE-2026-11-12.md. Aplicado pela Arquitetura pelo conector, com o "pode" do dono.
-- O que faz: campo `teste` (sim/não) na licença do RADAR (lex_contas), na assinatura dos apps web (assinaturas) e no
-- chamado/feedback (sol_feedback, preenchido sozinho a partir da licença ou da pessoa); as funções admin_lex_* leem e gravam;
-- os números (admin_sol_retorno, admin_feedback_painel) deixam as contas de teste de fora; a licença "Teste Marcelo (SolverONE)"
-- nasce marcada. Uma conta de teste funciona igual a uma real (e-mail, aceite, leitura): o campo só a tira das contas e da cobrança.
-- O "desfazer" está no fim do arquivo.

begin;

-- 1. Campo nas três tabelas que têm conta ou cliente neste banco (CRM e cobrança não existem aqui: ver o desenho).
alter table public.lex_contas   add column if not exists teste boolean not null default false;
alter table public.assinaturas  add column if not exists teste boolean not null default false;
alter table public.sol_feedback add column if not exists teste boolean not null default false;
comment on column public.lex_contas.teste   is 'Conta de teste: funciona como real, mas fica fora de números, cobrança, planos e CRM; sai no "limpar dados de teste".';
comment on column public.assinaturas.teste  is 'Pessoa/assinatura de teste dos apps web (mesma regra de lex_contas.teste).';
comment on column public.sol_feedback.teste is 'Chamado ou feedback vindo de conta de teste (preenchido pelo gatilho sol_feedback_marcar_teste).';

-- 2. Chamado/feedback: marcado sozinho quando vem de licença de teste (RADAR: aparelho.licenca) ou de pessoa de teste (apps web).
-- (12/Nov, noite, relato da Operação: SECURITY DEFINER, para a leitura de lex_contas e assinaturas não depender de quem insere;
--  o insert só acontece dentro de sol_enviar_feedback, que já é SECURITY DEFINER. Aplicado como migração 'sol_feedback_marcar_teste_definer'.)
create or replace function public.sol_feedback_marcar_teste()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.teste then return new; end if;
  if (new.aparelho ->> 'licenca') is not null
     and exists (select 1 from public.lex_contas c where c.codigo = new.aparelho ->> 'licenca' and c.teste) then
    new.teste := true;
  elsif new.pessoa_id is not null
     and exists (select 1 from public.assinaturas a where a.user_id = new.pessoa_id and a.teste) then
    new.teste := true;
  end if;
  return new;
end $$;
drop trigger if exists sol_feedback_marcar_teste on public.sol_feedback;
create trigger sol_feedback_marcar_teste before insert on public.sol_feedback
  for each row execute function public.sol_feedback_marcar_teste();
revoke execute on function public.sol_feedback_marcar_teste() from public, anon, authenticated;

-- 3. admin_lex_listar: devolve `teste`.
create or replace function public.admin_lex_listar()
 returns jsonb language plpgsql security definer set search_path to '' as $function$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'codigo', c.codigo, 'escritorio', c.escritorio, 'doc_tipo', c.doc_tipo, 'documento', c.documento,
      'ativo', c.ativo, 'validade', c.validade, 'max_pessoas', c.max_pessoas, 'max_computadores', c.max_computadores,
      'mensagem', c.mensagem, 'criado_em', c.criado_em, 'dominios', c.dominios, 'email_boas_vindas', c.email_boas_vindas,
      'email_responsavel', c.email_responsavel, 'exigir_aceite', c.exigir_aceite, 'teste', c.teste,
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
end $function$;

-- 4. admin_lex_salvar: aceita `teste` e registra a mudança no evento.
create or replace function public.admin_lex_salvar(p jsonb)
 returns jsonb language plpgsql security definer set search_path to '' as $function$
declare antes jsonb; depois jsonb; v_mod_antes text; v_mod_depois text; v_teste_antes boolean; v_teste_depois boolean;
        v_quem text := 'equipe:' || coalesce(auth.uid()::text, '?'); v_detalhe text;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select to_jsonb(c), c.modalidade, c.teste into antes, v_mod_antes, v_teste_antes from public.lex_contas c where c.codigo = p->>'codigo';
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
    teste             = coalesce((p->>'teste')::boolean, teste),
    dominios          = case when p ? 'dominios' then coalesce((select array_agg(pg_catalog.lower(pg_catalog.btrim(d))) from jsonb_array_elements_text(p->'dominios') d where pg_catalog.btrim(d) <> ''), '{}') else dominios end,
    modalidade        = coalesce(p->>'modalidade', modalidade),
    modalidade_desde  = case when p ? 'modalidade' and p->>'modalidade' <> modalidade then pg_catalog.now() else modalidade_desde end
  where codigo = p->>'codigo';
  select to_jsonb(c), c.modalidade, c.teste into depois, v_mod_depois, v_teste_depois from public.lex_contas c where c.codigo = p->>'codigo';
  v_detalhe := case when v_mod_depois <> v_mod_antes then 'modalidade: ' || v_mod_antes || ' -> ' || v_mod_depois
                    when v_teste_depois <> v_teste_antes then 'conta de teste: ' || case when v_teste_depois then 'sim' else 'não' end
                    else 'ficha alterada' end;
  insert into public.lex_eventos (codigo, tipo, detalhe, quem, motivo)
  values (p->>'codigo', 'licenca_alterada', v_detalhe, v_quem, pg_catalog.left(coalesce(p->>'motivo', ''), 300));
  perform public.lab_registrar_log('lex_salvar_licenca', null, depois, antes);
  return depois;
end $function$;

-- 5. admin_lex_criar com `p_teste` (a licença de teste já nasce marcada). As duas versões antigas continuam valendo.
create or replace function public.admin_lex_criar(p_escritorio text, p_validade date, p_max_pessoas integer, p_email_boas_vindas text, p_dominios text[], p_teste boolean)
 returns text language plpgsql security definer set search_path to '' as $function$
declare novo text;
begin
  novo := public.admin_lex_criar(p_escritorio, p_validade, p_max_pessoas, p_email_boas_vindas, p_dominios);
  if coalesce(p_teste, false) then
    update public.lex_contas set teste = true where codigo = novo;
    insert into public.lex_eventos (codigo, tipo, detalhe, quem)
    values (novo, 'licenca_alterada', 'conta de teste: sim (criada assim)', 'equipe:' || coalesce(auth.uid()::text, '?'));
  end if;
  return novo;
end $function$;
grant execute on function public.admin_lex_criar(text, date, integer, text, text[], boolean) to authenticated;
revoke execute on function public.admin_lex_criar(text, date, integer, text, text[], boolean) from anon;

-- 6. Números sem as contas de teste. admin_sol_retorno: quando a pergunta é pela licença de teste, mostra; sem licença, exclui.
create or replace function public.admin_sol_retorno(p_app text, p_licenca text default null, p_de date default null, p_ate date default null)
 returns jsonb language plpgsql security definer set search_path to '' as $function$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return jsonb_build_object(
    'dimensoes', (select a.retorno_dimensoes from public.sol_apps a where a.codigo = p_app),
    'sem_contas_de_teste', p_licenca is null,
    'por_situacao', coalesce((select jsonb_agg(jsonb_build_object('situacao', s.situacao, 'qtd', s.qtd) order by s.qtd desc)
      from (select situacao, sum(qtd) as qtd from public.sol_retorno_diario r
             where r.app = p_app and (p_licenca is null or r.licenca = p_licenca) and (p_de is null or r.data >= p_de) and (p_ate is null or r.data <= p_ate)
               and (p_licenca is not null or not exists (select 1 from public.lex_contas c where c.codigo = r.licenca and c.teste))
             group by situacao) s), '[]'::jsonb),
    'por_dia', coalesce((select jsonb_agg(jsonb_build_object('data', d.data, 'situacao', d.situacao, 'qtd', d.qtd) order by d.data)
      from (select data, situacao, sum(qtd) as qtd from public.sol_retorno_diario r
             where r.app = p_app and (p_licenca is null or r.licenca = p_licenca) and (p_de is null or r.data >= p_de) and (p_ate is null or r.data <= p_ate)
               and (p_licenca is not null or not exists (select 1 from public.lex_contas c where c.codigo = r.licenca and c.teste))
             group by data, situacao) d), '[]'::jsonb),
    'por_dimensao', coalesce((select jsonb_agg(jsonb_build_object('dim1', x.dim1, 'dim2', x.dim2, 'dim3', x.dim3, 'situacao', x.situacao, 'qtd', x.qtd) order by x.qtd desc)
      from (select dim1, dim2, dim3, situacao, sum(qtd) as qtd from public.sol_retorno_diario r
             where r.app = p_app and (p_licenca is null or r.licenca = p_licenca) and (p_de is null or r.data >= p_de) and (p_ate is null or r.data <= p_ate)
               and (p_licenca is not null or not exists (select 1 from public.lex_contas c where c.codigo = r.licenca and c.teste))
             group by dim1, dim2, dim3, situacao) x), '[]'::jsonb));
end $function$;

-- 7. admin_feedback_painel: só contas reais nos números (a fila continua mostrando tudo, com a coluna `teste`).
create or replace function public.admin_feedback_painel(p_dias integer default 30)
 returns jsonb language plpgsql stable security definer set search_path to '' as $function$
declare
  v_desde timestamptz := pg_catalog.now() - pg_catalog.make_interval(days => greatest(1, least(coalesce(p_dias, 30), 366)));
  v jsonb;
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  select pg_catalog.jsonb_build_object(
    'dias', greatest(1, least(coalesce(p_dias, 30), 366)),
    'sem_contas_de_teste', true,
    'total', (select pg_catalog.count(*) from public.sol_feedback f where f.criado_em >= v_desde and not f.teste),
    'novos', (select pg_catalog.count(*) from public.sol_feedback f where f.criado_em >= v_desde and f.situacao = 'novo' and not f.teste),
    'nota_media', (select round(avg(f.nota)::numeric, 2) from public.sol_feedback f where f.criado_em >= v_desde and f.nota is not null and not f.teste),
    'positivos', (select pg_catalog.count(*) from public.sol_feedback f where f.criado_em >= v_desde and f.rapido = 1 and not f.teste),
    'negativos', (select pg_catalog.count(*) from public.sol_feedback f where f.criado_em >= v_desde and f.rapido = -1 and not f.teste),
    'por_app_tipo', coalesce((select pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object('app', x.app, 'tipo', x.tipo, 'total', x.total,
                                     'nota_media', x.nota_media, 'novos', x.novos) order by x.app, x.tipo)
                                from (select f.app, f.tipo, pg_catalog.count(*) as total, round(avg(f.nota)::numeric, 2) as nota_media,
                                             pg_catalog.count(*) filter (where f.situacao = 'novo') as novos
                                        from public.sol_feedback f where f.criado_em >= v_desde and not f.teste group by f.app, f.tipo) x), '[]'::jsonb),
    'medido_em', pg_catalog.now())
    into v;
  return v;
end $function$;

-- 8. A licença de teste do dono já nasce marcada; a KR Law continua real.
update public.lex_contas set teste = true where escritorio = 'Teste Marcelo (SolverONE)' and not teste;
insert into public.lex_eventos (codigo, tipo, detalhe, quem)
select codigo, 'licenca_alterada', 'conta de teste: sim (marcação inicial, 12/Nov)', 'arquitetura'
  from public.lex_contas where escritorio = 'Teste Marcelo (SolverONE)';

commit;

-- Conferências (todas devem dar true):
-- select (select teste from public.lex_contas where escritorio = 'Teste Marcelo (SolverONE)') = true
--    and (select teste from public.lex_contas where escritorio = 'KR Law') = false
--    and exists (select 1 from information_schema.columns where table_name = 'sol_feedback' and column_name = 'teste')
--    and exists (select 1 from pg_trigger where tgname = 'sol_feedback_marcar_teste')
--    and (select count(*) from pg_proc where proname = 'admin_lex_criar') = 3;

-- DESFAZER (na ordem; os dados das contas não são tocados):
-- begin;
-- drop function if exists public.admin_lex_criar(text, date, integer, text, text[], boolean);
-- drop trigger if exists sol_feedback_marcar_teste on public.sol_feedback;
-- drop function if exists public.sol_feedback_marcar_teste();
-- -- admin_lex_listar, admin_lex_salvar, admin_sol_retorno e admin_feedback_painel: recriar com o texto anterior
-- -- (registrado em nuvem/supabase/lex-admin.sql e 2026-10-10-feedback-usuarios.sql do rootify-one; o pg_get_functiondef de 12/Nov
-- -- está em documentacao/DESENHO-CONTAS-DE-TESTE-2026-11-12.md, seção "antes").
-- alter table public.sol_feedback drop column if exists teste;
-- alter table public.assinaturas  drop column if exists teste;
-- alter table public.lex_contas   drop column if exists teste;
-- delete from public.lex_eventos where detalhe like 'conta de teste: sim (marcação inicial%';
-- commit;
