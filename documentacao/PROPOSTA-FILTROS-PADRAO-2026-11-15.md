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

## Terceiro filtro salvo: "Empresas da semana (visão completa)" (pedido do dono, 15/Nov)

**Ideia:** em vez de uma linha por processo, um bloco por empresa. Entram as empresas que tiveram processo novo nos últimos 7 dias;
dentro do bloco, os processos novos da semana e, logo abaixo, **todos os processos anteriores daquela empresa** que o programa já
tem (Lista e Arquivo), para ver o que ela está enfrentando.

**Ordem:** as empresas pela data do processo mais recente (a de ontem primeiro); empate, maior valor somado da semana. Dentro do
bloco, do mais novo para o mais antigo. Exemplo: 16/OUT ABC (3 processos na semana + 5 anteriores, desde MAR/2026), depois
15/OUT XYZ (1 + 0).

**Cabeçalho do bloco:** nome da empresa, CNPJ, porte e cidade; "3 processos nesta semana · 5 anteriores · R$ … em causas";
contato da empresa uma vez só (telefone, e-mail) e a situação mais avançada entre os processos (por exemplo, "Em contato").

**Os anteriores:** aparecem com um tom mais claro e a etiqueta "anterior", com a data e a situação de cada um; até 10 no bloco e,
se houver mais, "ver os 23 no Arquivo". Ficam fora dos números do alto ("Mostrando…"), que contam os processos da semana.

**Quem é "a mesma empresa":** o CNPJ (a raiz de 8 dígitos junta matriz e filiais); sem CNPJ, o nome normalizado (sem acento,
sem "LTDA"/"S.A."). Só a empresa principal do processo; as de "Também no processo" não abrem bloco próprio.

**Filtros do salvo:** últimos 7 dias, os tribunais do Wizard, com e sem contato, situação Novo e Visto. A nova ordem
"Agrupar por empresa" também fica disponível em "Ordenar por" para qualquer filtro.

**Por que vale:** contato é da empresa, não do processo: uma ligação cobre todos os processos dela; e quem tem muitos processos
recentes é a oportunidade maior. Com a área logada, marcar o bloco inteiro pede o que falta de todos de uma vez.

**Peso técnico:** pequeno a médio. Os anteriores que já estão na Lista vêm da tela; os do Arquivo, de um pedido ao programa só
para as empresas mostradas (sem carregar o Arquivo inteiro). Empresa gigante (centenas de processos) mostra os 10 e o link.
Conferir com 60 mil processos antes de dar como pronto. A planilha não muda.
