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

## 2. "O filtro talvez não esteja funcionando corretamente, ou eu não estou sabendo filtrar"
- Não disse qual filtro. Perguntar ao Leandro (pelo dono): qual filtro, o que escolheu, o que esperava e o que apareceu (print).
- Possível ligação com o item 1 (filtro "No Diário: últimos N dias" usa a data da publicação, não a da distribuição).

## 3. Vídeo tutorial curto para os sócios da KR Law
- O dono grava depois e põe no YouTube. A Produto pode preparar o **roteiro** (3 a 5 min): atualizar, Ler o Diário, filtros
  prontos, agrupar por empresa, ficha e contato, área logada, planilha. Sem dado real de pessoa física na tela.

## Ordem na retomada (sexta, 20/Nov)
1. Este arquivo primeiro (itens 1 e 2), antes da 0.7.51; levar ao dono as perguntas (número do processo, qual filtro).
2. Depois, `FEEDBACK-DONO-2026-11-16-TESTE-0750.md` e `PEDIDO-DONO-2026-11-16-NOVIDADES-E-0751.md`.
