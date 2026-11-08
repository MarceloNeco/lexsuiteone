# Como publicar uma versão do robô

Quem publica não precisa de chave, senha ou computador especial. O fluxo inteiro é no GitHub.

1. No código, suba a versão em `robo/lexsuite/__init__.py` (`VERSAO = "0.7.6"`, por exemplo) e, junto, o número que
   aparece em `robo/LEIA-ME.md`, `robo/MANUAL-DO-ESCRITORIO.html` e `robo/ARQUITETURA.md`. Rode os testes.
2. Faça o commit na branch `main` e envie.
3. Crie a tag com a mesma versão e envie: `git tag v0.7.6 && git push origin v0.7.6`. Pela tela do GitHub: Releases,
   "Draft a new release", "Choose a tag", digite `v0.7.6`, "Create new tag", "Publish release".
4. A automação "Publicar versão assinada" roda sozinha: testa, monta os dois pacotes, pede a assinatura ao serviço
   `assinatura.solverone.com.br` provando que é esta automação (identidade OIDC do GitHub, só para este repositório e
   só para tags `vX.Y.Z`), confere a assinatura com o próprio código do robô, e grava no site: `docs/downloads/`,
   `docs/atualizacao/` e `releases/`.
5. Em um ou dois minutos o GitHub Pages republica. Os robôs instalados veem a versão nova em
   `https://judicial.solverone.com.br/atualizacao/versao.json` e instalam só se a assinatura bater com a
   `chave_publica.txt` que está no pacote deles.

Para conferir: em Actions, a execução "Publicar versão assinada" da tag deve estar verde, e
`https://judicial.solverone.com.br/atualizacao/versao.json` deve mostrar a versão.

Segurança: a chave privada é gerada e guardada dentro do Cloudflare (Durable Object do Worker `assinatura-lexsuite`) e
não pode ser lida nem pela API. Trocar a chave exige publicar um pacote novo com a nova `chave_publica.txt`, por isso
só se faz em caso de incidente, e com todos os clientes avisados.
