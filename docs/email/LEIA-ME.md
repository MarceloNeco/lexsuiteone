# E-mail de boas-vindas do LexSuiteONE

Modelo em duas versões, `email-boas-vindas.html` (o que a pessoa vê) e `email-boas-vindas.txt` (versão em texto
puro, obrigatória para não cair em spam). Campos a preencher:

| Campo | O que entra | Padrão |
|---|---|---|
| `{{nome}}` | primeiro nome de quem recebe | (obrigatório) |
| `{{contato}}` | e-mail para dúvidas; o cliente escreve para ele, nunca responde ao e-mail | `judicial@solverone.com.br` (contato de toda a suíte LexSuiteONE; `contato@` é o genérico da SolverONE) |
| `{{drive}}` | (sem uso desde 09/Nov: nada é compartilhado com a SolverONE; o modelo não usa mais este campo) | `integracao@solverone.com.br` |
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

- A caixa `{{contato}}` precisa existir antes do envio ao cliente (apelido no ImprovMX; passo a passo em
  `docs/DNS-SOLVERONE.md`). O e-mail não pede para compartilhar pasta com a SolverONE: diz que é opcional, só para
  suporte (termos, seção 6.1).
- Revisado em 12/Nov contra o programa 0.7.33 (instalador que pede o código na primeira janela, assistente, planilha por
  área, Configurações com critérios da lista, leitura automática por dias e horários, "O que a SolverONE recebe") e os
  termos vigentes; traz um resumo em inglês.
- Um e-mail por pessoa, enviado depois que ela pediu o pacote. Não é lista nem campanha.
- Nada de senha ou chave no corpo do e-mail. O código de cliente não é segredo: identifica a conta, não dá acesso.

- 12/Nov (dono): texto mais curto e formal, largura de 760 px no computador, aceite "agora ou depois de instalar", sem prometer campos preenchidos, sem o parágrafo do compartilhamento, rodapé "LexSuiteONE · RADAR JUDICIAL é um produto da SolverONE".
