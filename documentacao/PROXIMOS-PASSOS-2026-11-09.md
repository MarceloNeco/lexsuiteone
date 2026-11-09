# Próximos passos (varredura de 09/Nov/2026, noite) · Produto

## Onde cada coisa está

| Conversa | Estado agora | Está rodando algo? |
|---|---|---|
| Operação (Sonnet) | 0.7.15 **publicada** às 14h55 e conferida (43 e 42 arquivos). Esperando de você o teste no Windows e o "feito" do Drive. | Não |
| Arquitetura (Fable) | Termos v1.0 e o passo do aceite no e-mail prontos **só na branch dela**, esperando o seu "pode publicar". Respondeu o pedido nº 2 do RootifyONE (item 3c). | Não |
| RootifyONE | 0.18.20 publicada. **Ainda não fez o item 3c** (botão "Publicar versão" dos termos). | Não |
| Produto (esta) | Correção da planilha grande pronta no ramo. Desenho do armazenamento em `documentacao/DESENHO-PLANILHA-GRANDE.md`. | Não |

Nada está rodando. Ninguém espera ninguém, só você.

## Achado importante desta noite (Produto)

Os 20.699 "processos novos" em dois TRTs são, quase certamente, **inflados**: a regra que reconhece "ação nova" aceita
frases que aparecem em quase toda intimação ("fica notificado", "citação"), e qualquer processo numerado em 2026 entra.
A estatística pública dos dois tribunais fica perto de 2,5 a 3 mil ações novas por dia útil. Isso enche a planilha e
confunde o advogado. A correção é a primeira coisa da 0.7.16.

## Proposta de ordem (com o seu "segue")

1. **0.7.16 pequena, antes do e-mail de quarta (11/Nov)**, porque o Leandro usa exatamente o TRT2 e o TRT15:
   (a) leitura da planilha grande (já feita); (b) regra de "ação nova" mais estreita; (c) aba Arquivo da planilha com os
   últimos 90 dias e todo processo trabalhado (o resto fica no banco do computador); (d) tirar "compartilhar a pasta" do
   e-mail, do site e do manual; (e) ressalvas da Operação. A Operação revisa e publica com o seu "publica a versão 0.7.16".
2. **0.7.17**: armazenamento completo (aviso em três lugares, limpar com cópia de segurança, painel na Configuração,
   espaço livre no disco, tela Arquivo em páginas) e os itens 89 a 97 (sair do programa, Configuração em janela, busca na
   área logada com a resposta padronizada etc.).
3. **Quinta (12/Nov)**: visita à KR Law com `docs/VISITA-KR-LAW.md`; o Leandro revisa os termos 1.1 na página real.

## O que colar em cada conversa

### Arquitetura (Fable)

```
Pode ser repetido: confira o quadro antes; se já foi feito, responda "já feito".
git pull e leia docs/QUADRO.md inteiro.
(1) Termos 1.1: o dono aprovou a proposta da Produto em documentacao/TERMOS-V1.1-PROPOSTA.html. Leve o texto para
paginas/aceite.html na sua branch (duas camadas, nome completo obrigatório, aceite sem desfazer, busca com setas e
contador, página na largura da tela). Não publique: o Leandro revisa a página na visita de quinta e o dono dá o "pode
publicar" depois. Até lá vale a decisão registrada: o e-mail de quarta sai sem o passo do aceite e a trava da KR Law
continua desligada.
(2) Desenho curto da parte "Para a Arquitetura" de documentacao/DESENHO-PLANILHA-GRANDE.md (uma planilha por frente
quando o tributário entrar; teto ou resumo mais cedo do banco do computador com esse volume). Responda no quadro, como
pedido à Produto. Nada disso entra na 0.7.16.
(3) Perguntas 10 a 13: quando o dono responder, a Produto registra em "Decisões do dono"; confira lá antes do item 82.
Devolva em até 10 linhas o que fez e o que ficou esperando.
```

### RootifyONE

```
Pode ser repetido: confira antes; se já foi feito, responda "já feito".
No repositório lexsuiteone, leia documentacao/PROMPT-ROOTIFYONE-2026-11-09.md, item 3c (versão nova dos termos), e
implemente o que cabe ao RootifyONE: Configuração → Termos com a lista, a prévia, o botão "Publicar versão" com motivo
e a marca "versão antiga" na ficha. Siga os itens 5 (o que nunca fazer) e 6 (como me devolver).
```

### Operação

Nada novo. Ela espera você:
- o **teste no Windows** da 0.7.15 (lista de 7 passos na seção "Preciso do dono" da Operação, em `docs/QUADRO.md`);
- o **"feito"** depois de você restringir a pasta "Estudos de Casos Juridicos" no Drive.

Quando a 0.7.16 estiver pronta, eu aviso, e você escreve lá: **publica a versão 0.7.16**.

## Perguntas 10 a 13 (do Fable), em linguagem simples, com a recomendação

| # | Pergunta | Recomendação |
|---|---|---|
| 10 | Ao buscar estatísticas antigas à noite, quantos Diários por noite? | 30 por noite, ajustável |
| 11 | Quanto tempo para trás na primeira carga? | 3 meses, só os tribunais marcados |
| 12 | Alguém precisa abrir no navegador um Diário de um ano atrás para ver se o CNJ ainda o entrega | Você, no Windows, quando puder; se não entregar, o botão só oferece o que existe |
| 13 | Quem já usa o programa precisa aceitar os termos de pessoa na primeira abertura da versão nova? | Sim, todos |

Para aceitar as quatro, basta escrever: **aceito as recomendações 10 a 13**.
