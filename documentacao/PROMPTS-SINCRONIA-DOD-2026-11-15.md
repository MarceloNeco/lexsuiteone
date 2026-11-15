# Prompts para sincronizar a Definition of done nas três conversas (15/Nov/2026)

Por que: a regra de revisar comunicações a cada mudança (14/Nov) existia, mas dependia de memória. Na 0.7.48 escaparam a ajuda do
Painel no AssistONE e a linha do antivírus no e-mail; o Wizard nem estava nomeado na lista; o revisor e a Operação revisaram o
código, não os textos. Correção (dono, "pode", 15/Nov): folha `documentacao/dod/<versão>.md` com 13 pontos + teste
`robo/testes/test_dod.py` que trava a versão sem ela (feito pela Produto em `4b8fcfe`). Falta a cascata pelas regras.

## Arquitetura (colar lá)

```
Decisão do dono (15/Nov): a Definition of done passa a ser conferida por uma FOLHA por versão, e não de memória. Na 0.7.48
escaparam a ajuda do Painel (AssistONE) e uma linha do e-mail de boas-vindas; o Wizard nem estava nomeado. A Produto já criou
documentacao/dod/LEIA-ME.md (modelo com 13 pontos), documentacao/dod/0.7.48.md e robo/testes/test_dod.py (trava a versão sem a
folha completa), commit 4b8fcfe. Faça, como dona das regras:
1. CLAUDE.md, seção "Definition of done": nomear explicitamente Wizard/primeiro acesso, mensagens do instalador, ajuda de CADA
   tela do AssistONE, tour, busca, manual, Novidades, termos, e-mails e comunicações, site; e a regra "antes de 'pronta para
   publicar', preencher documentacao/dod/<versão>.md; ponto em branco ou falso é bloqueio". Em "Como entregar", citar a folha.
2. .claude/agents/revisor.md: o revisor lê a folha contra o diff, abre cada texto citado e trata ponto falso, vago ou em branco
   como bloqueio (não basta o teste passar).
3. Diretriz geral do rootify-one (skill diretrizes-gerais-apps): a mesma regra para todos os apps da SolverONE (RootifyONE, site e
   os que vierem): folha por versão com os pontos da Definition of done de 12 pontos + Wizard/primeiro acesso, e um teste
   automático que trava a versão sem a folha, onde o app tiver testes. Diga em uma linha o que o RootifyONE, o ArchONE e o
   EaglePlanONE precisam saber.
4. Anote no quadro e me devolva o resumo em até 10 linhas, em português.
```

## Operação (colar lá)

```
Decisão do dono (15/Nov): toda versão tem a folha documentacao/dod/<versão>.md (13 pontos; modelo documentacao/dod/LEIA-ME.md;
teste robo/testes/test_dod.py). Na revisão de cada versão: leia a folha contra o que mudou, abra os textos citados (manual,
AssistONE, Wizard, Novidades, e-mail, site, instalador) e NÃO publique com ponto falso, vago ou em branco. Isso vale para tudo
o que o cliente vê, inclusive instaladores e e-mail fora de versão. Pendente: os instaladores corrigidos da 0.7.48 (branch da
Produto, commit 0f1414e, pedido no quadro) esperam o meu "pode". Responda em até 10 linhas, em português.
```

## Produto (esta conversa)

Feito: folha, teste, folha da 0.7.48, e-mail de boas-vindas com o antivírus. Daqui em diante, toda versão da Produto só fica
"pronta para publicar" com a folha preenchida e o `test_dod.py` passando.
