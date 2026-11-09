# Próximos passos e prompts para copiar (09/Nov/2026, noite) · Produto

Decisão do dono: **tudo entra na 0.7.16, antes da visita de quinta** (não haverá outra visita ao Leandro). A Produto
decidiu a estrutura da planilha por delegação do dono: `documentacao/DESENHO-PLANILHA-GRANDE.md`.

## Onde cada coisa está

| Conversa | Estado | Rodando algo? |
|---|---|---|
| Operação | 0.7.15 publicada e conferida. Espera de você o teste no Windows e o "feito" do Drive. | Não |
| Arquitetura (Fable) | Termos e passo do aceite no e-mail prontos só na branch dela, esperando o seu "pode publicar". | Não |
| RootifyONE | 0.18.20 publicada. Falta o item 3c (botão "Publicar versão" dos termos). | Não |
| Produto (esta) | Fazendo a 0.7.16 completa (itens 89 a 101). | Sim, a 0.7.16 |

## Calendário

| Quando | O quê | Quem |
|---|---|---|
| Agora | Colar os prompts abaixo no Fable e no RootifyONE | Você |
| Quarta 11/Nov, manhã | 0.7.16 pronta na `main`; eu aviso aqui | Produto |
| Quarta 11/Nov | Escrever na Operação: `publica a versão 0.7.16` (prompt abaixo) | Você |
| Quarta 11/Nov | Enviar o e-mail de boas-vindas ao Leandro pelo botão do RootifyONE (sem o passo do aceite) | Você |
| Quinta 12/Nov | Visita com `docs/VISITA-KR-LAW.md` (já atualizado para a 0.7.16) | Você |

## 1. Fable (Arquitetura): colar agora

```
Pode ser repetido: confira o quadro antes; se já foi feito, responda "já feito".
git pull e leia docs/QUADRO.md inteiro.
(1) Termos 1.1: o dono aprovou a proposta da Produto em documentacao/TERMOS-V1.1-PROPOSTA.html. Leve o texto para
paginas/aceite.html na sua branch (duas camadas, nome completo obrigatório, aceite sem desfazer, busca com setas e
contador, página na largura da tela). Não publique: o Leandro revisa a página na visita de quinta e o dono dá o "pode
publicar" depois. Até lá vale a decisão registrada: o e-mail de quarta sai sem o passo do aceite e a trava da KR Law
continua desligada.
(2) Leia documentacao/DESENHO-PLANILHA-GRANDE.md. O dono delegou à Produto a estrutura da planilha e mandou pôr tudo na
0.7.16 (uma planilha por frente na mesma pasta, cópias de segurança, limite com aviso, armazenamento e disco, regra de
"ação nova" mais estreita). Revise a parte "Para a Arquitetura" sem bloquear a 0.7.16: se algo ferir regra de negócio
ou de nuvem, anote no quadro como pedido à Produto ainda hoje.
(3) Perguntas 10 a 13: quando o dono responder, a Produto registra em "Decisões do dono"; confira lá antes do item 82.
Devolva em até 10 linhas o que fez e o que ficou esperando.
```

## 2. RootifyONE: colar agora

```
Pode ser repetido: confira antes; se já foi feito, responda "já feito".
No repositório lexsuiteone (git pull), leia documentacao/PROMPT-ROOTIFYONE-2026-11-09.md, item 3c (versão nova dos
termos), e implemente o que cabe ao RootifyONE: Configuração → Termos com a lista, a prévia, o botão "Publicar versão"
com motivo e a marca "versão antiga" na ficha. Siga os itens 5 (o que nunca fazer) e 6 (como me devolver).
```

## 3. Operação: só quando eu avisar que a 0.7.16 está pronta

```
Pode ser repetido: confira o quadro antes; se a 0.7.16 já foi publicada, responda "já feito".
git pull e leia docs/QUADRO.md. publica a versão 0.7.16: revise com o revisor (testes, Bandit, tela, pacote, atualização
a partir da 0.7.15 sem tocar em config.json, lexsuite.db e saida/; a planilha antiga LexSuiteONE.xlsx deve virar
"LexSuiteONE - Trabalhista.xlsx" com as abas editadas preservadas). Se aprovar, dispare "Publicar versão assinada" e
confira por fora. Se não aprovar, não publique: anote o bloqueio no quadro como pedido à Produto.
```

Até lá, a Operação só espera você: o teste no Windows da 0.7.15 pode ser pulado (a 0.7.16 o substitui); o "feito" do
Drive continua valendo.

## 4. Claude in Chrome na visita

Os prompts 1 a 4 de `docs/VISITA-KR-LAW.md` **não mudaram** nesta conversa (o Prompt 1 já devolve o bloco "RESPOSTA
PARA O RADAR v1", que a 0.7.16 lê). Mudou o roteiro: instalar no computador que fica ligado nos horários, conferir
Configuração → Armazenamento (espaço livre no disco), a planilha agora se chama `LexSuiteONE - Trabalhista.xlsx` e não
se compartilha com a SolverONE. Antes de cada prompt na área logada, a autorização do Leandro (seção "Antes de começar").

## Perguntas 10 a 13 (do Fable), em linguagem simples

| # | Pergunta | Recomendação |
|---|---|---|
| 10 | Ao buscar estatísticas antigas à noite, quantos Diários por noite? | 30 por noite, ajustável |
| 11 | Quanto tempo para trás na primeira carga? | 3 meses, só os tribunais marcados |
| 12 | Alguém precisa abrir no navegador um Diário de um ano atrás para ver se o CNJ ainda o entrega | Você, no Windows, quando puder |
| 13 | Quem já usa o programa aceita os termos de pessoa na primeira abertura da versão nova? | Sim, todos |

Para aceitar as quatro, escreva aqui: **aceito as recomendações 10 a 13**.
