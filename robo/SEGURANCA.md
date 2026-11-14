# Segurança do robô LexSuiteONE · RADAR JUDICIAL (v0.7.47)

Resumo para quem audita. O robô roda no computador do escritório. Com a SolverONE ele troca só: a conferência da
licença (código, versão e só quantidades por situação, dia, tribunal, frente e faixa de valor; nenhum nome, processo ou
contato), o cadastro de quem usa (nome, e-mail, função e documento do
escritório), o aceite dos termos (versão, data e fuso horário), avisos técnicos de erro (sem conteúdo de processos) e a
procura de versão nova; ver "Rede". A relação de processos, as fichas, os contatos, as anotações e as estatísticas dos meses
anteriores (totais e, só no computador, o número dos processos já contados) não saem do computador e da pasta do escritório.

- **Sem segredos no código ou no pacote.** Nenhuma senha, chave de API ou certificado. A chave privada que assina
  atualizações existe só dentro do serviço de assinatura da SolverONE (ninguém a tem); o pacote leva só a chave pública.
- **Registro local (0.7.29).** Sem janela preta, o que aparecia nela vai para `saida/registro.txt` (até 3 arquivos de
  1 MB, no computador; não sai dele). A tela mostra as últimas linhas em Configuração → Ver registro; o
  `DIAGNOSTICO.bat` leva as últimas 200, com CPF mascarado, só quando o escritório gera e manda o relatório.
- **Tela local.** O servidor escuta só em 127.0.0.1 (nunca na rede). Pedidos que mudam algo (POST) exigem o cabeçalho
  `X-LexSuite` que só a própria página manda, e a origem é conferida: outro site aberto no navegador não consegue
  mandar o robô rodar nem mudar a configuração. Sem cookies, sem sessão, sem login.
- **Entradas tratadas como não confiáveis.** Planilha: leitor próprio que lê só as abas editáveis, com limite de 50 MB por parte e 1 GB no total, DTD e entidades recusadas; valores
  inválidos caem no padrão; planilha ilegível nunca é sobrescrita. Pacote de atualização: assinatura Ed25519 (RFC 8032) sobre versão e
  SHA-256, conferência do SHA-256 do zip, limite de tamanho e de quantidade de arquivos, lista fechada de nomes
  permitidos, recusa de `..`, caminhos absolutos e letras de unidade, e a chave pública nunca é substituída por um
  pacote. `config.json`, banco, Python e saídas não são tocados; a versão anterior fica em `_anterior\`.
- **Rede.** Só HTTPS para DJEN, PJe (consulta pública), BrasilAPI, Minha Receita e a conferência da licença na SolverONE
  (Supabase, função `lex-conta`: código de cliente, identificação da instalação, versão e, desde a 0.7.14, a tabela de
  totais por situação, dia, tribunal, frente e faixa de valor, sem nome, processo, CNPJ ou contato; a tela mostra a tabela
  enviada); o cadastro de quem usa (nome, e-mail, função e documento do escritório: CNPJ, CPF ou passaporte) e o aceite
  dos termos de uso (versão e fuso horário); avisos
  técnicos de erro (etapa, versão, Windows e mensagem sem caminhos pessoais; desde a 0.7.47 também o nome do antivírus
  encontrado, se está ligado e o tipo de bloqueio, um de seis sinais, nada de pessoa); desde a 0.7.47, na conferência da licença,
  a preferência `avisar_cnj` e, só quando o CNJ falha, a pergunta `estado_cnj` (no máximo 1 a cada 5 minutos); também só quando o
  CNJ falha, duas sondas de controle sem dado nenhum (`judicial.solverone.com.br/atualizacao/versao.json` e a consulta pública
  do CNJ); a procura de versão nova no site; DataJud
  (consulta pública do CNJ, quando ligada) e, só se o escritório configurar, e-mail (SMTP) e Telegram para avisos. Com intervalo mínimo entre pedidos,
  poucas tentativas e teto de 2 GB por download (lido em pedaços; caderno descompactado também limitado). Nada de burlar
  captcha, trocar IP ou abrir várias cópias. A tela não faz nenhum pedido externo (fontes do sistema); desde a 0.7.20 o programa manda ao navegador uma regra de segurança (Content-Security-Policy) que proíbe a página de carregar script, imagem ou fonte, abrir conexão ou enviar formulário para endereço de fora deste computador; os links que a pessoa clica (PJe, termos, manual) continuam abrindo no navegador. O AssistONE embutido é só ajuda, sem IA; os erros técnicos das estatísticas antigas vão à SolverONE como os das leituras (etapa, versão, Windows, mensagem sem caminhos pessoais).
- **Tela só local.** Além de escutar em 127.0.0.1, recusa qualquer pedido cujo cabeçalho Host não seja 127.0.0.1 ou
  localhost na porta do robô (contra DNS rebinding).
- **Planilhas e CSV.** O `.xlsx` é texto puro (nunca fórmula). No CSV exportado, célula que começa com `=`, `+`, `-` ou
  `@` recebe um apóstrofo, para o texto do Diário não virar fórmula no Excel.
- **Dados pessoais.** Pessoas físicas das publicações são descartadas antes de gravar. Os contatos de empresa vêm do
  cadastro público da Receita; o uso é decisão do compliance do escritório, e os nomes de sócios podem ser desligados
  em Configurações → Destaques e exclusões (cada pessoa, por área). O relatório de diagnóstico mascara nomes e CPFs. O banco local guarda os processos com um trecho
  curto do texto; depois de 12 meses (`radar.guardar_dias`) o trecho do Diário é apagado e fica um resumo (número do
  processo, tribunal, vara, classe, data, link, valor, empresas, CNPJ e, da Receita, porte, atividade, cidade, endereço,
  telefone, e-mail e nomes de sócios, sem o autor da ação), e os totais diários (estatísticas) ficam para sempre. Contatos de sócios só com fonte e data
  (decisão do dono); CPF e dado de reclamante são recusados na colagem. Revisão completa em
  `SEGURANCA-REVISAO-2026-11-07.md`.
- **O que não é.** O "desligar pelo suporte" é cortesia, não trava: quem controla o computador controla o robô.
  A planilha compartilhada depende da conta Google do escritório e do compartilhamento que ele fizer.
- **Agendamento.** `schtasks` chamado sem shell, com argumentos fixos; só cria ou remove as tarefas do robô. Desde a 0.7.47 o
  XML da tarefa fica na pasta do programa (`tarefa.xml`, com autor e descrição da SolverONE), nunca na pasta temporária, e o
  instalador cria a tarefa na própria janela, às claras.
- **Instalador (0.7.47).** Antes de baixar, lê o antivírus e o firewall na Central de Segurança do Windows (só leitura, sem
  administrador) e faz três pedidos leves (site do produto, `lex-conta` e consulta pública do CNJ) para saber se a rede barra os
  endereços do programa; nunca desliga nem contorna o antivírus. Em erro, o aviso técnico leva também o antivírus e o sinal.
- **Este computador (0.7.47).** O programa lê o antivírus e o firewall uma vez por dia pelo PowerShell (só leitura), guarda em
  `saida/computador.json` e mostra em Configurações → Sobre este computador.
- **Revisão.** Testes automáticos (mais de 110) cobrem assinatura (vetores da RFC), pacote adulterado, caminho suspeito,
  planilha corrompida e pedidos sem o cabeçalho da página. Revisão de segurança e LGPD trimestral com a skill
  `seguranca-lgpd-gdpr`; Bandit e Gitleaks entram no GitHub Actions quando houver repositório.
