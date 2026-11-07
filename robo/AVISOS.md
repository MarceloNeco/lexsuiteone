# Avisos na hora: Telegram e e-mail (opcional)

A cada rodada do `RODAR.bat`, o robô pode mandar o que achou de novo nos processos do escritório. Nenhuma senha
ou token entra em arquivo: ficam nas variáveis de ambiente do Windows.

## Telegram (grátis, recomendado)

1. No Telegram, procure **@BotFather**, mande `/newbot` e siga as perguntas (nome, por exemplo "Avisos do
   escritório"; o usuário precisa terminar em `bot`). Ele responde com um **token** (um código longo).
   **Não cole esse token em arquivo nem em conversa.**
2. Guarde o token no Windows: menu Iniciar → digite **variáveis de ambiente** → "Editar as variáveis de ambiente
   para sua conta" → em "Variáveis de usuário", **Novo** → Nome: `LEXSUITE_TELEGRAM_TOKEN` · Valor: o token → OK.
3. Crie um grupo no Telegram (ex.: "Publicações do escritório"), ponha o bot e as pessoas que devem receber.
   Mande `/start` no grupo.
4. Descubra o número do grupo: `RODAR.bat monitor --descobrir-chat`. Copie o `chat_id` (começa com `-`).
5. No `config.json`, em `"telegram"`, ponha `"ativo": true` e o `chat_id` entre aspas.
6. Teste: `RODAR.bat monitor --teste-aviso`. Deve chegar uma mensagem marcada "TESTE".

## E-mail (Gmail)

1. Em `config.json`, em `"email"`, ponha `"ativo": true`, o seu Gmail em `"de"` e os destinatários em `"para"`.
2. No Gmail, crie uma **senha de app**: https://myaccount.google.com/apppasswords (precisa da verificação em
   duas etapas ligada). Ela tem 16 letras.
3. Guarde como variável de ambiente do usuário do Windows (mesmo caminho acima): Nome `LEXSUITE_SMTP_SENHA`,
   Valor: a senha de app.

Com os dois ligados, chegam os dois. Para mandar o aviso sem o trecho do texto, ponha `"trecho_no_aviso": false`.
Se nenhum aviso conseguir sair numa rodada, as publicações ficam guardadas para avisar na próxima.
