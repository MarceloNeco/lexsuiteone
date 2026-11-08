# Como publicar uma versão do robô

Quem publica não precisa de chave, senha, tag ou computador especial. Basta pedir.

## O jeito normal: pedir ao Claude

Diga à sessão de operação: "publica a versão 0.7.6". Ela sobe o número da versão no código (`robo/lexsuite/__init__.py`
e os lugares que o repetem), envia para a branch `main` e dispara a automação "Publicar versão assinada". A automação:

1. roda os testes;
2. monta os dois pacotes (download completo e pacote de atualização);
3. pede a assinatura ao serviço `assinatura.solverone.com.br`, provando que é esta automação, deste repositório,
   deste workflow (identidade OIDC do GitHub); a chave privada fica só no Cloudflare;
4. confere a assinatura com o próprio código do robô;
5. grava no site (`docs/downloads/`, `docs/atualizacao/`, `releases/`) e cria a tag `v0.7.6` para registro.

Em um ou dois minutos o GitHub Pages republica e os robôs instalados passam a ver a versão nova em
`https://judicial.solverone.com.br/atualizacao/versao.json`. Eles só instalam se a assinatura bater com a
`chave_publica.txt` que está no pacote deles.

## À mão, pelo site do GitHub (se um dia precisar)

Actions, "Publicar versão assinada", "Run workflow", digite a versão, deixe "Publicar de verdade" marcado, "Run workflow".
Desmarcando "Publicar de verdade", a automação só testa a assinatura e não grava nada.

Criar uma tag `vX.Y.Z` pela tela de Releases também dispara a publicação, mas não é necessário.

## Conferir

Em Actions, a execução "Publicar versão assinada" deve estar verde, e
`https://judicial.solverone.com.br/atualizacao/versao.json` deve mostrar a versão.

## Segurança

A chave privada é gerada e guardada dentro do Cloudflare (Durable Object do Worker `assinatura-lexsuite`) e não pode
ser lida nem pela API. O serviço só assina a pedido do workflow `publicar.yml` deste repositório, por tag `vX.Y.Z` ou
por disparo manual a partir da `main`. Trocar a chave exige publicar um pacote novo com a nova `chave_publica.txt`, por
isso só se faz em caso de incidente, com todos os clientes avisados.
