# Pedido do dono, 16/Nov/2026 (à noite): para depois de quinta-feira, 19/Nov (créditos reiniciam)

Nada disto começa antes de sexta, 20/Nov. Quem faz: a Produto.

## 1. Versão 0.7.51 (já autorizada: "já aplicar as correções identificadas pela operação, já gerar uma nova versão")
As 5 ressalvas da revisão da 0.7.50 (quadro, "Operação → Produto, 16/Nov"):
1. "Excluir esta empresa": com CNPJ, excluir só pelo CNPJ (o homônimo de outro CNPJ fica; "a chave é o CNPJ").
2. "CNPJ provável": não juntar "X Ltda" e "X S.A."; mostrar na confirmação os nomes exatos.
3. Novidades: tirar "caixinha" (coloquial) e "now" (EN).
4. Manual: "limpeza automática" → "rotina de limpeza" (`paginas/manual.html`, linha ~237).
5. Pré-filtro do CNPJ provável que pode falhar com acento.
Mais o que o dono achar no teste da 0.7.50 (seção 8 de `ESTADO-ATUAL-RADAR.md`), se chegar até lá.

## 2. Janela "Novidades da versão" (decidido pelo dono; entra na 0.7.51)
- A janela aparece **toda vez** que o programa abre, até a pessoa marcar a caixa **"Não mostrar novamente"** (por versão: versão
  nova volta a aparecer). Hoje aparece uma vez só.

## 3. Pesquisa de mercado (bench) antes de decidir; levar ao dono com recomendação
1. **Menu**: manter "Ajuda → Novidades da versão" ou tirar (o dono acha que é distração que ninguém reabre)?
2. **Histórico de versões** (o que entrou em cada versão, inclusive anteriores): é obrigatório por lei (CDC, LGPD, regras de
   software para advogados/OAB) ou é boa prática de mercado (exemplos: Slack, Notion, Microsoft, Google, apps jurídicos como
   Astrea, Projuris)? Onde fica (dentro do app, site, e-mail)?
3. Nome: "Novidades" ou "Versões".
Regra do dono: **se não for obrigatório nem boa prática, tirar**; se for preciso ter o histórico, manter também as novidades.
