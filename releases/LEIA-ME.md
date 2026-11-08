# Pacotes para download

- O download oficial é `https://judicial.solverone.com.br/downloads/LexSuiteONE-robo.zip` (arquivo em `docs/downloads/`,
  servido pelo site do produto). Esta pasta `releases/` guarda o histórico: `LexSuiteONE-robo-<versão>.zip`.
- Os pacotes são gerados e assinados pela automação do GitHub quando uma tag `vX.Y.Z` é publicada (ver `docs/PUBLICAR.md`).
  O pacote de atualização assinado e o `versao.json` ficam em `docs/atualizacao/`, que o robô instalado consulta em
  `https://judicial.solverone.com.br/atualizacao/versao.json`.
- Ninguém gera chave em computador nenhum: a chave privada vive só no serviço de assinatura, no Cloudflare.
