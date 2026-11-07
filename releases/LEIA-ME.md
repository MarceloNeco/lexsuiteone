# Pacotes para download

- O download oficial é `https://judicial.solverone.com.br/downloads/LexSuiteONE-robo.zip` (arquivo em `docs/downloads/`,
  servido pelo site do produto). Esta pasta `releases/` guarda o histórico: `LexSuiteONE-robo-<versão>.zip`.
- `LexSuiteONE-robo.zip` aqui é a mesma versão atual, por conveniência; quem atualizar um, atualiza o outro.
- Atualização assinada: `versao.json` e `LEXSUITE-ONE-ROBO-<versão>.zip` gerados por `ferramentas/publicar.py` vão para
  `docs/atualizacao/`, que o robô consulta em `https://judicial.solverone.com.br/atualizacao/versao.json`.
- `LexSuiteONE-suporte.zip`: **só para o dono**, não vai para cliente. Extraia por cima de `C:\LexSuiteONE` e dê dois
  cliques em `ferramentas\GERAR-CHAVES.bat`: gera o par de chaves em `Documentos\SolverONE-chaves`. A chave pública vai
  para o pacote (`chave_publica.txt`); a privada fica só nesse computador. O cliente nunca mexe em chave nenhuma.
