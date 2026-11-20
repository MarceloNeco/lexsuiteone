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

**Diretriz do dono (16/Nov): "deveria consultar o máximo de fontes públicas possível".** O DataJud (CNJ) já estava no código
(`datajud.py`, comandos de estatística por vara) e não era usado para completar o RADAR: falha nossa de não ter proposto antes.
Fontes públicas e o que cada uma dá: **DJEN/Diário** (descobre o processo e a empresa; histórico por número; bloqueia acesso de fora
do Brasil), **DataJud** (data e hora do ajuizamento, classe, assuntos, órgão, movimentos; **não traz as partes**, atrasa alguns dias
e às vezes recusa por excesso de pedidos), **Receita/CNPJ** (cadastro da empresa, já usado). A Arquitetura desenha o uso conjunto
(com fila, ritmo e "tenta de novo"). Tentativa da Produto (16/Nov) de achar o processo do Leandro no DataJud por vara e dia de
ajuizamento: a API respondeu "ocupado" várias vezes; nova tentativa em segundo plano.

**Decisões do dono (16/Nov, para a 0.7.51):**
- O RADAR **complementa** cada processo com todas as fontes públicas (Diário/DJEN, DataJud/CNJ, Receita/CNPJ), cobrindo os buracos.
- **Toda leitura** ("Ler o Diário agora" e a rotina) tenta de novo o que faltou nas leituras anteriores.
- Quando uma fonte falhar para um processo, o cartão/ficha diz **qual fonte e por quê**, em texto curto (ex.: "Datas do CNJ: não
  carregadas (CNJ sem resposta)"), com o botão **"Tentar de novo"** ali mesmo.
- Prioridade máxima da 0.7.51, junto com a data certa (1ª publicação real e ajuizamento).

**Processo achado (Produto, 16/Nov, DataJud do CNJ; acesso público, sem pessoa física):** **1000910-15.2026.5.02.0714** — 14ª VT de
São Paulo - Zona Sul; ajuizado em **15/05/2026 13:15:22**; "Dispensa Discriminatória"; Ação Trabalhista - Rito Ordinário; Juízo 100%
Digital. **1ª publicação no Diário: 20/05/2026**; 6 dias de publicação até 08/09/2026 (13 movimentos, em dobro; o DataJud está atualizado até 08/10/2026, ~1 mês de
atraso); audiências de conciliação e de instrução designadas em 28/07. Logo, a publicação de 13/11 que o RADAR achou é mais uma
sobre audiência (o sinal "audiência … de conciliação" de `_INICIO` casou). **Confirmado: falso positivo por sinal fraco, não atraso do
tribunal.** Como achamos: busca por vara e dia de ajuizamento; o número faltante na sequência da vara (0909, 0911…) + dígito
verificador CNJ. Lições para o desenho: o DataJud responde daqui (o DJEN não), mas recusa por excesso de pedidos (várias tentativas e
uma resposta parcial: "total 1" sem o documento) — precisa de fila e de "tentar de novo".

### Amostra de outros tribunais (DataJud, 16/Nov; TRT9 com 4 processos de mar–abr/2026; TRT17 e outros chegando)
- **1ª publicação nem sempre fica perto do ajuizamento**: Guarapuava, ajuizado 30/04, 1ª publicação **02/07** (2 meses); Londrina 24/03 →
  27/03; Ponta Grossa 25/03 → 26/03; Maringá 05/03 → 09/03. Conclusão: o critério de "novo" deve ser o **ajuizamento** (quando o CNJ
  tiver); a 1ª publicação é a aproximação quando o CNJ ainda não tem o processo (o CNJ atualiza com atraso: TRT9 até 09/11, TRT2 até 08/10).
- **A jornada varia muito** e os andamentos vêm com código padronizado (tabela do CNJ), então dá para montar sozinha: audiência inicial
  (12747), de instrução (12749), de julgamento (12751), com situação "designada/realizada/cancelada/redesignada"; antecipação de tutela
  (785); gratuidade (787); acordo homologado (466); sentença procedente em parte (221) ou improcedente (220); trânsito em julgado (848);
  liquidação (11384); remessa ao tribunal (123); mandados (985, 106). Andamentos de rotina (petição, expedição, publicação, conclusão,
  prazo) ficam fora da jornada.
- **Valor para o escritório**: processo com acordo, sentença ou trânsito em julgado já não é oportunidade; com "advogado constituído"
  da empresa (Diário traz os advogados intimados), provavelmente já defendida. Propor etiquetas: "Já tem acordo", "Já sentenciado",
  "Empresa já tem advogado".
- Amostra completa (TRT9, TRT17, TRT4, TRT3, TRT15, TRT1; processos de mar–jun/2026): a 1ª publicação vem de 1 a 13 dias depois
  do ajuizamento na maioria, mas chega a 2 meses (Guarapuava). **Rito sumaríssimo anda rápido**: em Venda Nova do Imigrante (TRT17),
  ajuizado 03/03, sentença 12/05, trânsito em julgado 27/05 — a janela de oportunidade pode ser de semanas. **Classe importa**:
  "Cumprimento Provisório de Sentença" (TRT17, distribuído por dependência) não é ação nova; distribuição "por dependência" ou com
  "reconhecimento de prevenção" pede cuidado. O CNJ estava atualizado de 05/11 a 09/11 nesses tribunais (TRT2: 08/10).
- Protótipo com tudo o que as fontes públicas trazem do caso real: `documentacao/prototipos/datas-do-processo/prototipo-fontes-publicas.html`.

## 2. "O filtro talvez não esteja funcionando corretamente, ou eu não estou sabendo filtrar"
- Não disse qual filtro. Perguntar ao Leandro (pelo dono): qual filtro, o que escolheu, o que esperava e o que apareceu (print).
- Possível ligação com o item 1 (filtro "No Diário: últimos N dias" usa a data da publicação, não a da distribuição).

## 3. Vídeo tutorial curto para os sócios da KR Law
- O dono grava depois e põe no YouTube. A Produto pode preparar o **roteiro** (3 a 5 min): atualizar, Ler o Diário, filtros
  prontos, agrupar por empresa, ficha e contato, área logada, planilha. Sem dado real de pessoa física na tela.

## Ordem na retomada (sexta, 20/Nov)
1. Este arquivo primeiro (itens 1 e 2), antes da 0.7.51; levar ao dono as perguntas (número do processo, qual filtro).
2. Depois, `FEEDBACK-DONO-2026-11-16-TESTE-0750.md` e `PEDIDO-DONO-2026-11-16-NOVIDADES-E-0751.md`.

## Achado de 16/Nov (noite): o CNJ chega atrasado para processo novo

- Consulta ao DataJud em 16/11: o ajuizamento mais recente nos TRT3, 4, 15 e 17 é de **31/10** (TRT15: 29/10); nada de novembro. O TRT2 respondeu zero. Os processos de sexta, 13/11, ainda não estão no CNJ.
- Consequência para a 0.7.51: nos primeiros ~15 dias, **o Diário é a única fonte** de um processo novo. A data de ajuizamento sai da lista de distribuição ou da notificação inicial do Diário; o CNJ confirma depois. O cartão mostra "ajuizado (pelo Diário)" até o CNJ confirmar, e a falta do CNJ nesse período não é falha (não mostrar "Tentar de novo").
- Valor da causa: o DataJud não tem. Vem só do texto da publicação do Diário, quando ela traz ("Valor da causa: R$ …"), ou da área logada.
- Empresa com mais de 10 processos: o DataJud não traz as partes; o exemplo depende do Diário, que não abre desta nuvem (bloqueio fora do Brasil). Caminho: o dono exporta do RADAR dele (Agrupar por empresa → Baixar a lista) e a Produto completa pelo CNJ.

## Decisões do dono sobre o protótipo (16/Nov, noite)

- Etiquetas de fonte (CNJ, DIÁRIO, RECEITA, ÁREA LOGADA): saem do lado de cada campo. Ficam só no alto da ficha, numa linha, com um (?) ao lado. O (?) abre um quadro estruturado: o nome de cada fonte em dourado e, embaixo, os campos que vieram dela nesta leitura (ex.: CNJ → ajuizamento, classe, assuntos, andamentos; Diário → empresa, publicações, advogados, valor; Receita → CNPJ, CNAE, porte, telefone, endereço, sócios). Fonte que falhou aparece em vermelho com "Tentar de novo".
- Toda leitura do Diário consulta também a Receita e o CNJ (com nova tentativa), como já decidido.
- O que já está publicado (Selecionar todos, Expandir todos, caixinha da empresa, Excluir esta empresa, cópia de contato) continua igual; a 0.7.51 mexe em datas, jornada, etiquetas e filtros novos.
- Seta do agrupamento no protótipo é só imitação; no programa fica a da 0.7.50.
