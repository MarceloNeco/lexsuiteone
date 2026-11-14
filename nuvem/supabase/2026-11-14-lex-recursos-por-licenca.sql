-- Interruptores por licença (pedido do dono, 14/Nov): ligar ou desligar um recurso do RADAR para UM escritório, pela ficha do
-- RootifyONE. Primeiro uso: "área logada" (Trazer dados da área logada), desligada enquanto o recurso não amadurece ou conforme o
-- risco do escritório. APLICADO em 14/Nov/2026 pelo conector (Arquitetura), com o "pode aplicar" do dono; migração `lex_recursos_por_licenca` (coluna, admin_lex_listar, admin_lex_salvar) e dados iniciais em seguida. O texto abaixo é o que foi aplicado. Desenho: DESENHO-AREA-LOGADA-V2-2026-11-14.md, seção 6.
--
-- Como funciona: a lex-conta (ação verificar) já devolve `recursos` {id: ligado} lidos dos arquivos master do RootifyONE
-- (solverone-dados, global + app). Passa a aplicar por cima o que estiver em lex_contas.recursos (jsonb {id: true|false}); a
-- licença vence o global. O programa já esconde o que tem data-recurso desligado; só precisa marcar os elementos da área logada
-- com data-recurso="area-logada" e consultar `recursos` ao abrir (ele já faz na verificação da licença).

begin;

alter table public.lex_contas add column if not exists recursos jsonb not null default '{}'::jsonb;
alter table public.lex_contas drop constraint if exists lex_contas_recursos_objeto;
alter table public.lex_contas add constraint lex_contas_recursos_objeto check (pg_catalog.jsonb_typeof(recursos) = 'object');
comment on column public.lex_contas.recursos is 'Exceções desta licença {id: true|false}; vencem o global do RootifyONE (recursos/global.json + radar-judicial.json). Chave ausente = segue o global. Ex.: {"area-logada": false}.';

-- admin_lex_listar: texto de 2026-11-13-admin-lex-criar-sem-public.sql + o campo 'recursos', coalesce(c.recursos, '{}'::jsonb).
-- admin_lex_salvar: texto anterior + (a) validação de p.recursos (objeto; ids [a-z0-9.-]{1,40}; valores true|false);
--   (b) recursos = p->'recursos' quando p ? 'recursos' (conjunto completo das exceções; chave ausente = segue o global);
--   (c) um evento licenca_alterada por recurso que mudou: 'recurso <id>: ligado' | 'desligado' | 'segue o global', com motivo;
--   (d) quando p vem só com codigo, recursos e motivo, nada mais é tocado e NÃO sai o evento "ficha alterada".
--   Texto completo das duas funções: no banco (pg_get_functiondef) e na migração lex_recursos_por_licenca.
revoke all on function public.admin_lex_listar() from public, anon;
revoke all on function public.admin_lex_salvar(jsonb) from public, anon;
grant execute on function public.admin_lex_listar() to authenticated;
grant execute on function public.admin_lex_salvar(jsonb) to authenticated;

-- Padrão inicial (dados, aplicados logo depois): área logada DESLIGADA nas licenças que não são de teste (hoje, só a KR Law),
-- LIGADA na licença de teste; um evento por licença, quem = 'arquitetura'.
update public.lex_contas set recursos = recursos || '{"area-logada": false}'::jsonb where not teste and not (recursos ? 'area-logada');
update public.lex_contas set recursos = recursos || '{"area-logada": true}'::jsonb where teste and not (recursos ? 'area-logada');
insert into public.lex_eventos (codigo, tipo, detalhe, quem, motivo)
select codigo, 'licenca_alterada', 'recurso area-logada: ' || case when (recursos->>'area-logada')::boolean then 'ligado' else 'desligado' end,
       'arquitetura', 'padrão inicial da área logada por licença (desenho 2c, 14/Nov); o dono liga pela ficha do RootifyONE'
  from public.lex_contas where recursos ? 'area-logada'
   and not exists (select 1 from public.lex_eventos e where e.codigo = lex_contas.codigo and e.detalhe like 'recurso area-logada:%');

commit;

-- lex-conta v19 (Supabase v21, 14/Nov): em `verificar`, resposta.recursos = {...global+app do RootifyONE, ...conta.recursos}.
-- docs/recursos-do-app.json: 'area-logada' declarado com nome, onde e "padrao": false.

-- DESFAZER:
-- begin;
-- delete from public.lex_eventos where detalhe like 'recurso area-logada: % (padrão inicial, 14/Nov)';
-- alter table public.lex_contas drop column if exists recursos;
-- -- recriar admin_lex_listar e admin_lex_salvar sem o campo (texto de 2026-11-13-admin-lex-criar-sem-public.sql)
-- commit;
