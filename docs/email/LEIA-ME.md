# E-mail de boas-vindas do LexSuiteONE

Modelo em duas versões, `email-boas-vindas.html` (o que a pessoa vê) e `email-boas-vindas.txt`
(a versão em texto puro, obrigatória para não cair em spam). Os dois têm dois campos para preencher
antes de enviar:

| Campo | O que entra |
|---|---|
| `{{nome}}` | o primeiro nome de quem vai receber (ex.: Leandro) |
| `{{suporte}}` | o e-mail de suporte que a pessoa deve usar e com quem compartilhar a pasta do Drive (ex.: integracao@solverone.com.br) |

## Como é enviado

- Remetente: `LexSuiteONE <nao-responda@solverone.com.br>`, pelo Resend (domínio `solverone.com.br` já verificado,
  com SPF, DKIM e DMARC; nenhum registro de DNS precisa ser mexido).
- Assunto: `Bem-vindo ao LexSuiteONE: seu pacote de instalação`.
- O link de download é fixo e aponta para o pacote publicado neste repositório:
  `https://github.com/MarceloNeco/lexsuiteone/raw/main/releases/LexSuiteONE-robo.zip`.
  Quem atualiza o pacote em `releases/` não precisa mudar o e-mail.
- O e-mail não tem anexo, não tem rastreador de abertura e não pede nada além de baixar o pacote.

## Regras

- A caixa `{{suporte}}` precisa existir antes do envio ao cliente (a pessoa vai responder para ela).
- Um e-mail por pessoa, enviado depois que ela pediu o pacote. Não é lista nem campanha.
- Nada de senha, chave ou código de cliente no corpo do e-mail.
