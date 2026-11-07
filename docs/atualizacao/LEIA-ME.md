# Atualização assinada

Aqui ficam `versao.json` e o `.zip` assinado gerados por `robo/ferramentas/publicar.py`. O robô instalado consulta
`https://judicial.solverone.com.br/atualizacao/versao.json`; sem o arquivo, ele entende que não há atualização e segue.
Só instala se a assinatura Ed25519 bater com a `chave_publica.txt` do pacote.
