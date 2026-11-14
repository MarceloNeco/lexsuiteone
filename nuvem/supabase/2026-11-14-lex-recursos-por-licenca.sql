-- Interruptores por licença (pedido do dono, 14/Nov): ligar ou desligar um recurso do RADAR para UM escritório, pela ficha do
-- RootifyONE. Primeiro uso: "área logada" (Trazer dados da área logada), desligada enquanto o recurso não amadurece ou conforme o
-- risco do escritório. PROPOSTA: NÃO APLICADA; entra com o "pode aplicar" do dono. Desenho: DESENHO-AREA-LOGADA-V2-2026-11-14.md, seção 6.
--
-- Como funciona: a lex-conta (ação verificar) já devolve `recursos` {id: ligado} lidos dos arquivos master do RootifyONE
-- (solverone-dados, global + app). Passa a aplicar por cima o que estiver em lex_contas.recursos (jsonb {id: true|false}); a
-- licença vence o global. O programa já esconde o que tem data-recurso desligado; só precisa marcar os elementos da área logada
-- com data-recurso="area-logada" e consultar `recursos` ao abrir (ele já faz na verificação da licença).

begin;

alter table public.lex_contas add column if not exists recursos jsonb not null default '{}'::jsonb
  check (jsonb_typeof(recursos) = 'object');
comment on column public.lex_contas.recursos is 'Interruptores desta licença {id: true|false}; vence o global do RootifyONE. Ex.: {"area-logada": false}.';

-- admin_lex_listar devolve `recursos`; admin_lex_salvar aceita `recursos` (objeto inteiro, só chaves [a-z0-9.-]{1,40} e valores booleanos).
-- (Trechos completos no momento de aplicar: as duas funções são recriadas com o texto atual + o campo.)

-- Padrão inicial: área logada DESLIGADA na KR Law até o dono ligar pela ficha; LIGADA na licença de teste.
update public.lex_contas set recursos = recursos || '{"area-logada": false}'::jsonb where escritorio = 'KR Law';
update public.lex_contas set recursos = recursos || '{"area-logada": true}'::jsonb where teste;
insert into public.lex_eventos (codigo, tipo, detalhe, quem)
select codigo, 'licenca_alterada', 'recurso area-logada: ' || case when (recursos->>'area-logada')::boolean then 'ligado' else 'desligado' end || ' (padrão inicial, 14/Nov)', 'arquitetura'
  from public.lex_contas where recursos ? 'area-logada';

commit;

-- lex-conta v19 (junto): em `verificar`, resposta.recursos = {...recursosDoRootify(), ...conta.recursos}; o programa esconde a
-- barra "Preparar busca", o item do menu Área logada e o botão do cartão quando recursos["area-logada"] === false.
-- Programa (Produto): data-recurso="area-logada" nesses três lugares + manual/AssistONE ("este recurso é ligado pela SolverONE por escritório").

-- DESFAZER:
-- begin;
-- delete from public.lex_eventos where detalhe like 'recurso area-logada: % (padrão inicial, 14/Nov)';
-- alter table public.lex_contas drop column if exists recursos;
-- -- recriar admin_lex_listar e admin_lex_salvar sem o campo (texto de 2026-11-12-contas-de-teste.sql)
-- commit;
