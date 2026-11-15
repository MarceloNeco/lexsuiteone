# Proposta: filtros já salvos para o escritório e limpeza explicada no Wizard (Produto, 15/Nov/2026; nada implementado)

Pedido do dono (15/Nov): 2 ou 3 filtros já configurados, como se o escritório já os tivesse salvo; um com contato (para agir) e
outro sem contato (para a área logada); TRT2 e TRT15 (São Paulo, capital e interior); no futuro, conforme onde fica o escritório;
tudo explicado no Wizard; e a limpeza automática ligada por padrão.

## O que já é assim hoje (conferido no código da 0.7.48)
- **A limpeza já vem ligada** em toda instalação: resume com 6 meses e apaga com 24 os processos que ninguém trabalhou; as
  estatísticas nunca se apagam; o escritório muda ou desliga em Configurações → Armazenamento. Falta só o Wizard dizer isso.
- Filtro salvo guarda situação, contato, tribunal, valor etc., e fica neste computador. **Não guarda o período** ("Publicado no
  Diário": 7 dias): para "últimos 7 dias" o filtro salvo precisa passar a guardar o período (mudança pequena na tela).

## Ponto de atenção: tributário
O RADAR hoje lê a frente **trabalhista** (TRTs). Processo tributário não sai nos TRTs: sai nos TRFs (TRF3 em SP) e no TJSP
(execução fiscal, mandado de segurança). Por isso os dois filtros abaixo são para o trabalhista, que já funciona; para o
tributário, a mesma ideia (com e sem contato) entra quando a frente tributária existir, com TRF3 e TJSP no lugar dos TRTs.

## Proposta (trabalhista; recomendação)

| | Filtro 1: "Para contatar (7 dias)" | Filtro 2: "Buscar contato na área logada (7 dias)" |
|---|---|---|
| Para quê | quem tem telefone ou e-mail: ligar ou escrever já | quem não tem: marcar todos e "Trazer dados da área logada" |
| Período | últimos 7 dias | últimos 7 dias |
| Tribunais | **os que o escritório escolheu no Wizard** (padrão TRT2 e TRT15) | os mesmos |
| Contato | só com contato | só sem contato |
| Situação | Novo e Visto (some o que já foi trabalhado ou descartado) | Novo e Visto |
| Outros | CNPJ confirmado | CNPJ confirmado (a área logada precisa achar a empresa certa) |
| Ordem | maior valor da causa primeiro | maior valor da causa primeiro |

Terceiro, opcional: **"Maiores causas da semana"** (7 dias, acima do valor mínimo dos Destaques, com e sem contato), para o
sócio ver o que vale mais a pena.

**Por que "os tribunais do Wizard"** em vez de TRT2 e TRT15 fixos: já se adapta ao escritório hoje, sem esperar a versão
"sofisticada". Escritório de SP fica com TRT2 e TRT15; de outro estado, com os TRTs que marcou. No futuro, o Wizard pode sugerir
os TRTs pelo estado do CNPJ do escritório (SP → TRT2 e TRT15; RJ → TRT1; MG → TRT3…).

## Regras propostas
- Os filtros aparecem em "Filtros salvos" na primeira abertura, com o nome acima; o escritório pode renomear, mudar, arquivar ou
  apagar (como os que ele salva). Se ele apagar, não voltam sozinhos.
- Quem já usa o programa recebe os filtros uma vez, na atualização, sem mexer nos que já salvou.
- A tela abre na Lista como hoje (sem filtro aplicado); o filtro é uma escolha a um clique.

## Wizard (passo 4, "Tudo pronto"), texto proposto
> Já deixamos dois filtros salvos na Lista: "Para contatar (7 dias)", com os processos que têm telefone ou e-mail, e "Buscar
> contato na área logada (7 dias)", com os que não têm. A limpeza automática também já vem ligada: os processos que ninguém
> trabalhou ficam resumidos depois de 6 meses e saem depois de 24; as estatísticas ficam para sempre. Tudo isso muda em
> Configurações.

## O que muda além da tela (Definition of done)
Manual (Filtros salvos e Wizard), AssistONE (ajuda da Lista, busca "filtros prontos"), Novidades, Wizard; termos não mudam; e-mail
de boas-vindas talvez uma frase ("a lista já vem com dois filtros prontos"). Sem nuvem e sem banco novo.
