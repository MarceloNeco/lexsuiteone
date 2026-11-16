# PRIORIDADE MÁXIMA (16/Nov/2026): primeiro uso real do Leandro (KR Law) — verificar ASAP quando os créditos reiniciarem

O Leandro atualizou para a 0.7.50, clicou "Ler o Diário" e **os processos chegaram** ("deu certo!!!", testou em alguns TRTs).
O dono vai entregar a resposta na semana que vem (Leandro volta ao trabalho; quarta viaja). Dados de pessoa física da conversa
(reclamante: nome, CPF, endereço; nomes de advogados) foram **retirados** daqui de propósito (regra do produto e LGPD).

## 1. Data errada: "apareceu como distribuído nos últimos dias, mas foi em maio" (o mais importante)
- Caso real (dados públicos do processo, sem pessoa física): 14ª Vara do Trabalho de São Paulo - Zona Sul (TRT2); distribuído e
  autuado em **15/05/2026**; valor R$ 141.237,64; reclamada Garantia Real Serviços Ltda. (CNPJ 00.215.548/0001-59). O número do
  processo não veio na conversa: pedir ao dono/Leandro.
- Hipóteses a conferir no código e no Diário desse dia:
  1. O cartão mostra a **data da publicação no Diário** (ex.: uma intimação ou audiência de novembro), e a pessoa lê como data de
     distribuição. Rótulo do cartão e da ficha não deixa claro ("No Diário: …" × "Distribuído em …").
  2. A regra de "ação nova" (lista de distribuição, audiência inicial, notificação inicial, "notifique-se a reclamada", citação
     inicial) aceitou como nova uma publicação de processo antigo (ex.: audiência inicial redesignada, notificação repetida).
  3. Conferir se o número CNJ traz o ano (2026) e se dá para usar o **número sequencial / ano** ou o DataJud para descartar processo
     distribuído há mais de N dias, ou ao menos marcar "distribuído em MAI/2026 (publicação de NOV)".
- Saída esperada: (a) o cartão diz claramente as duas datas (publicação × distribuição, quando conhecida); (b) processo antigo não
  entra como "novo" (ou entra marcado e fora do padrão "novos"); (c) teste com o caso real; (d) explicação simples no (?) e no manual.

### Anamnese (Produto, 16/Nov, só leitura do código; sem mexer em nada)
**Causa mais provável (alta confiança): a regra de "ação nova" aceita a audiência inicial como sinal, e no TRT2 a audiência
inicial costuma ser marcada meses depois da distribuição.**
- Como o RADAR decide (`djen.leads`, `classificar._INICIO`): é "novo" quem (a) aparece na **lista de distribuição** (sinal forte:
  publicada logo depois da distribuição) ou (b) tem no texto "audiência inicial/una/de conciliação", "notificação inicial",
  "notifique-se a reclamada" ou "citação inicial". O único freio de idade é o **ano** do número CNJ (`ano_minimo`): processo de
  2026 passa sempre. O caso do Leandro (distribuído em 15/05/2026) passa no ano e, se a publicação de novembro for a notificação
  da audiência inicial (ou uma redesignação), passa no sinal (b).
- Ordem de grandeza: no registro do dono de 16/Nov (TRT9 e TRT17), dos 317 "novos", 227 vieram da lista de distribuição e **90
  (28 %) da audiência ou notificação inicial**, que podem ser de processos de meses atrás. No TRT2 (São Paulo, pauta longa) a
  fatia antiga tende a ser maior.
- A data mostrada no cartão é a **data da publicação no Diário** (`data_publicacao`); "Ajuizada em" só existe quando vem da área
  logada ou é digitada. O cartão não diz "publicado em", por isso se lê como data de distribuição.
- O que já existe e ajuda: `lexsuite/datajud.py` (API pública do CNJ, chave lida da página oficial, nada no código) já consulta
  `dataAjuizamento`; hoje só é usado nos comandos de estatística por vara, não no RADAR.

**Soluções (para decidir com o dono; ordem recomendada)**
1. **Data de ajuizamento pelo DataJud** para os "novos" que NÃO vieram da lista de distribuição: uma consulta em lote por número
   (dezenas por pedido) depois da leitura; grava `ajuizada_em` com fonte "DataJud". Regra: ajuizado há mais de 30 dias (ajustável)
   → **não entra como novo** (fica no Arquivo, marcado "processo antigo: ajuizado em 15/05/2026; publicação de 13/11"). Limite:
   o DataJud atrasa alguns dias para processo muito recente; sem resposta, o processo entra e fica "data de ajuizamento a conferir".
   Passa pela Arquitetura (rede, ritmo de pedidos, regra de negócio).
2. **Cartão e ficha com as duas datas**: "Publicado no Diário em 13/NOV" e "Ajuizado em 15/MAI/2026" (quando conhecida); filtro
   e ordenação "por data de ajuizamento" quando houver. Barato e independente do item 1.
3. **Selo do sinal** no cartão ("lista de distribuição" × "audiência inicial"), com (?) explicando que a audiência pode ser de
   processo distribuído antes; filtro "só lista de distribuição" (o mais seguro) num filtro salvo de fábrica.
4. Plano B sem rede: estimar pela numeração sequencial da vara (o número CNJ cresce ao longo do ano) — pouco confiável, só se o
   DataJud não servir.
- Teste: o caso real (pedir o número ao Leandro) e casos fictícios com publicação de audiência inicial de processo de maio.

Protótipo para o dono: `documentacao/prototipos/datas-do-processo/prototipo.html` (glossário, linha do tempo, cartão com as duas
datas, selo da origem, ordenar e filtros novos). Pedido à Arquitetura no quadro (16/Nov).

Esclarecimento ao dono (16/Nov): a data dourada do cartão (`data_publicacao`) é a **primeira publicação do processo que o RADAR
encontrou** (a mais antiga das publicações daquela leitura, `djen.leads`, `min(pubs)`), não a última; depois que o processo entra,
ela não muda. Rótulo proposto: **"Encontrado no Diário em 13/NOV"** com (?) "a publicação que trouxe este processo ao RADAR; não é a
data em que a ação começou", e ao lado **"Ajuizado em 15/MAI/2026"** quando conhecido. Ajustar o protótipo e os textos (cartão,
ficha, filtro "No Diário", manual, AssistONE).

Correção do esclarecimento (dono, 16/Nov: "você está me induzindo ao erro"): a data dourada é a primeira publicação **que o RADAR
viu**; no caso do Leandro ela é a **mais recente** de verdade (13/NOV), porque as publicações de maio aconteceram antes de o RADAR
começar a ler. Nunca dizer "primeira publicação" sem "que o RADAR viu".

**Solução reforçada (proposta ao dono, 16/Nov):** para os processos que entraram por audiência ou notificação (não pela lista de
distribuição), antes de chamar de "novo": (1) **histórico no DJEN pelo número** — `djen.buscar_filtrado` já aceita `numeroProcesso`
e devolve todas as publicações do processo (data e tipo); havendo publicação anterior ao período (ou lista de distribuição antiga),
não é novo; (2) **DataJud** pela data de ajuizamento. Mais de 30 dias → "processo antigo" com as datas reais, fora dos novos.
Cartão: "Ajuizado em …", "1ª publicação no Diário em …" e "Encontrado pelo RADAR em …". Custo: ~1 pedido/s (90 processos ≈ 2 min,
em segundo plano). Vai junto no pedido à Arquitetura. Atualizar o protótipo com esses rótulos.

## 2. "O filtro talvez não esteja funcionando corretamente, ou eu não estou sabendo filtrar"
- Não disse qual filtro. Perguntar ao Leandro (pelo dono): qual filtro, o que escolheu, o que esperava e o que apareceu (print).
- Possível ligação com o item 1 (filtro "No Diário: últimos N dias" usa a data da publicação, não a da distribuição).

## 3. Vídeo tutorial curto para os sócios da KR Law
- O dono grava depois e põe no YouTube. A Produto pode preparar o **roteiro** (3 a 5 min): atualizar, Ler o Diário, filtros
  prontos, agrupar por empresa, ficha e contato, área logada, planilha. Sem dado real de pessoa física na tela.

## Ordem na retomada (sexta, 20/Nov)
1. Este arquivo primeiro (itens 1 e 2), antes da 0.7.51; levar ao dono as perguntas (número do processo, qual filtro).
2. Depois, `FEEDBACK-DONO-2026-11-16-TESTE-0750.md` e `PEDIDO-DONO-2026-11-16-NOVIDADES-E-0751.md`.
