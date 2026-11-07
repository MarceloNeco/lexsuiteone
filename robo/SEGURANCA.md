# Segurança do robô LexSuiteONE (v0.7.0)

Resumo para quem audita. O robô roda no computador do escritório, sem servidor na internet.

- **Sem segredos no código ou no pacote.** Nenhuma senha, chave de API ou certificado. A chave privada que assina
  atualizações nasce no computador do suporte e nunca sai dele; o pacote leva só a chave pública.
- **Tela local.** O servidor escuta só em 127.0.0.1 (nunca na rede). Pedidos que mudam algo (POST) exigem o cabeçalho
  `X-LexSuite` que só a própria página manda, e a origem é conferida: outro site aberto no navegador não consegue
  mandar o robô rodar nem mudar a configuração. Sem cookies, sem sessão, sem login.
- **Entradas tratadas como não confiáveis.** Planilha de controle: leitor próprio com limite de 50 MB, sem entidades
  externas; valores inválidos caem no padrão. Pacote de atualização: assinatura Ed25519 (RFC 8032) sobre versão e
  SHA-256, conferência do SHA-256 do zip, limite de tamanho e de quantidade de arquivos, lista fechada de nomes
  permitidos, recusa de `..`, caminhos absolutos e letras de unidade, e a chave pública nunca é substituída por um
  pacote. `config.json`, banco, Python e saídas não são tocados; a versão anterior fica em `_anterior\`.
- **Rede.** Só HTTPS para DJEN, PJe (consulta pública), BrasilAPI e Minha Receita, com intervalo mínimo entre pedidos
  e poucas tentativas. Nada de burlar captcha, trocar IP ou abrir várias cópias.
- **Dados pessoais.** Pessoas físicas das publicações são descartadas antes de gravar. Os contatos de empresa vêm do
  cadastro público da Receita; o uso é decisão do compliance do escritório. O relatório de diagnóstico mascara
  nomes e CPFs. O banco local guarda só as ações e um trecho curto do texto.
- **O que não é.** O "desligar pelo suporte" é cortesia, não trava: quem controla o computador controla o robô.
  A planilha compartilhada depende da conta Google do escritório e do compartilhamento que ele fizer.
- **Revisão.** Testes automáticos (55) cobrem assinatura (vetores da RFC), pacote adulterado, caminho suspeito,
  planilha corrompida e pedidos sem o cabeçalho da página. Revisão de segurança e LGPD trimestral com a skill
  `seguranca-lgpd-gdpr`; Bandit e Gitleaks entram no GitHub Actions quando houver repositório.
