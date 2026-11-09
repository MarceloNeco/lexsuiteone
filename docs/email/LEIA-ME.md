# E-mail de boas-vindas do LexSuiteONE

Modelo em duas versões, `email-boas-vindas.html` (o que a pessoa vê) e `email-boas-vindas.txt` (versão em texto
puro, obrigatória para não cair em spam). Campos a preencher:

| Campo | O que entra | Padrão |
|---|---|---|
| `{{nome}}` | primeiro nome de quem recebe | (obrigatório) |
| `{{contato}}` | e-mail para dúvidas; o cliente escreve para ele, nunca responde ao e-mail | `judicial@solverone.com.br` (contato de toda a suíte LexSuiteONE; `contato@` é o genérico da SolverONE) |
| `{{drive}}` | endereço de sistemas da SolverONE, com quem o cliente compartilha a subpasta LexSuiteONE do Drive (não é caixa de atendimento) | `integracao@solverone.com.br` |
| `{{email}}` | e-mail do responsável pela licença (campo "e-mail do responsável" da ficha no RootifyONE); vai dentro do link do aceite dos termos, fixo na página | (vazio: a página pede o e-mail) |
| `{{codigo}}` | código de cliente `LEX-XXXX-XXXX`, **obrigatório desde a 0.7.7**: o instalador não instala sem ele. Pegar no RootifyONE (Clientes → Licenças do RADAR); o código real nunca entra no repositório nem no quadro | (sem código, o bloco sai; não mandar o e-mail assim) |

`python preencher.py --nome Leandro` gera os dois arquivos preenchidos em `saida/`. Com `--codigo LEX-...`, inclui o
bloco do código; sem ele, o bloco é removido, e o cliente não consegue instalar. Nada é enviado por esse script.

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
