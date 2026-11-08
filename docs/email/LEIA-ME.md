# E-mail de boas-vindas do LexSuiteONE

Modelo em duas versões, `email-boas-vindas.html` (o que a pessoa vê) e `email-boas-vindas.txt` (versão em texto
puro, obrigatória para não cair em spam). Campos a preencher:

| Campo | O que entra | Padrão |
|---|---|---|
| `{{nome}}` | primeiro nome de quem recebe | (obrigatório) |
| `{{contato}}` | e-mail para dúvidas; o cliente escreve para ele, nunca responde ao e-mail | `judicial@solverone.com.br` (contato de toda a suíte LexSuiteONE; `contato@` é o genérico da SolverONE) |
| `{{drive}}` | endereço de sistemas da SolverONE, com quem o cliente compartilha a subpasta LexSuiteONE do Drive (não é caixa de atendimento) | `integracao@solverone.com.br` |
| `{{codigo}}` | código de cliente `LEX-XXXX-XXXX`, opcional; entra em uso com a versão 0.8 | (sem código, o bloco sai) |

`python preencher.py --nome Leandro` gera os dois arquivos preenchidos em `saida/`. Com `--codigo LEX-...`, inclui o
bloco do código; sem ele, o bloco é removido. Nada é enviado por esse script.

## Como é enviado

- Remetente: `LexSuiteONE <nao-responda@solverone.com.br>`, pelo Resend. O domínio `solverone.com.br` já está
  verificado (SPF, DKIM e DMARC no Registro.br); nenhum registro de DNS precisa ser mexido. O endereço
  `nao-responda@` não precisa existir como caixa: ele só envia, e o e-mail avisa que não recebe respostas.
- Assunto: `Bem-vindo ao <nome do produto>: seu pacote de instalação` (hoje, RADAR JUDICIAL). O `preencher.py` mostra o
  assunto pronto. O nome vem de `docs/marca.json`: o modelo usa `{{marca.nome}}`, `{{marca.curto}}` e `{{marca.logo_email}}`.
- O link de download é o instalador de um arquivo, `https://judicial.solverone.com.br/downloads/Instalar-LexSuiteONE.zip`,
  servido pelo site do produto (pasta `docs/downloads/` do repositório). Não depende da conta do GitHub: mudar o repositório de dono não muda o link.
- Sem anexo, sem rastreador de abertura, sem pedir nada além de baixar o pacote.

## Regras

- As caixas `{{contato}}` e `{{drive}}` precisam existir antes do envio ao cliente. O domínio recebe e-mail pelo
  ImprovMX (encaminhamento), então as duas são apelidos lá; `{{drive}}` precisa também ser uma Conta Google criada com esse
  e-mail, senão o compartilhamento do Drive não chega. Passo a passo em `docs/DNS-SOLVERONE.md`.
- Um e-mail por pessoa, enviado depois que ela pediu o pacote. Não é lista nem campanha.
- Nada de senha ou chave no corpo do e-mail. O código de cliente não é segredo: identifica a conta, não dá acesso.
