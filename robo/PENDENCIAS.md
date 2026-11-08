# Pendências do robô LexSuiteONE (07/Nov/2026, depois da v0.7.0)

Lista viva. Quem continuar (qualquer modelo ou pessoa) lê este arquivo e o `ARQUITETURA.md` antes de mexer.

## Decisões do dono em 07/Nov (tarde)

- Endereço do produto: `judicial.solverone.com.br` (decisão final: mais fácil de falar e de lembrar). Marca: **LexSuiteONE**
  é a suíte jurídica da SolverONE; **JUDICIAL** é este produto, escrito em maiúsculas com o "IA" em latão; as frentes
  (Radar Trabalhista, Tributário, Cível e empresarial) vivem dentro dele. `lexsuiteone.solverone.com.br` não é usado.
- Frentes, nesta ordem: trabalhista (existe), tributário, depois cível e empresarial. Leandro: trabalhista e tributário.
- Cópia HTML estática no Drive: fica, como reserva. O caminho principal é o sistema (tela local hoje; site na 0.8).
- 0.8 confirmada: o robô envia a lista do dia para a nuvem da SolverONE (Supabase) e o site em judicial.solverone.com.br
  mostra, com login por link no e-mail e código de cliente. O Drive continua com a planilha editável.
- Zero impacto na KR Law quando o repositório mudar de dono: tudo que o cliente vê aponta para
  `judicial.solverone.com.br` (site, download, manual, atualização assinada), nunca para a conta do GitHub. Na
  transferência para a organização: mover o repositório, religar o Pages com o mesmo domínio, trocar o alvo do CNAME
  `judicial` para `solverone.github.io` (no Cloudflare, pelo conector), atualizar links do README. O GitHub redireciona
  os endereços antigos. A chave pública de assinatura não muda.
- E-mail: **feito em 08/Nov**. Recebimento no Cloudflare Email Routing, com Email Worker que responde automaticamente
  em `integracao@` e encaminha `contato@` e os demais apelidos. Texto da resposta, por decisão do
  dono: **"Este endereço é usado por sistemas da SolverONE e não é lido por pessoas. Esta mensagem não será
  respondida."** Sem indicar outro e-mail por enquanto; quando houver processo de atendimento, passa a indicar
  `contato@`. Mais tarde, triagem em `contato@` (problema, contato comum, comercial).
- Cara profissional em tudo que o cliente vê: nenhum contato pessoal do dono (e-mail, usuário pessoal do GitHub) em site,
  e-mail, repositório ou planilha. Organização `solverone` no GitHub e endereços: `judicial@` para dúvidas de qualquer produto da suíte LexSuiteONE (e `moneytrio@` etc. para as outras suítes;
  `contato@` é o genérico da SolverONE; no futuro, triagem por programa), `integracao@` só para sistemas (Drive;
  vira Conta Google; não é monitorado e deve responder automaticamente que não é caixa de atendimento).

## Esperando o dono (Marcelo)

- Rodar `DIAGNOSTICO.bat` no computador no Brasil e mandar `diagnostico\radar-diagnostico.txt` (arrastar para o Drive).
  Sem ele a regra de "ação nova" fica frouxa: 6.816 ações num dia em TRT2+TRT15, esperado 1.500 a 2.000.
- Testar a v0.6.0: `INSTALAR-PYTHON.bat`, `ABRIR.bat`, escolher tribunais, "Salvar e atualizar agora", print da tela e da ficha.
- Rodar `teste-djen-supabase.sql` no SQL Editor do projeto solverone-app e mandar o resultado (decide se o coletor
  central pode viver no Supabase ou precisa de um servidor pequeno em São Paulo).
- Decidir o repositório público no GitHub (núcleo aberto, MIT ou Apache 2.0). Nada é criado sem esse sim.
- Criar a Conta Google `integracao@solverone.com.br` (sem Gmail; o apelido já existe no ImprovMX), para o cliente compartilhar o Drive.

## v0.6.1 (correções)

- Regra estrita de "ação nova" calibrada com o diagnóstico (pistas em `lexsuite/diagnostico.py`, `ESTRITA`).
- Achar o CNPJ pelo nome da empresa (o Diário traz CNPJ em ~1% dos casos): base pública da Receita no portal novo
  (SERPRO); índice compacto por UF para o robô local; tabela completa no SaaS.
- Ao apertar a regra, orientar: apagar `lexsuite.db` e rodar uma vez limpa.

## Feito na v0.7.0

- Tela com Configuração (escritório, pasta compartilhada detectada), 59 tribunais por ramo/região/estado, 24 TRTs por padrão.
- Planilha de controle (Preferências, Exclusões, Controle oculto) e planilha Radar (Log, Saúde, Sobre ocultas) na pasta do Drive.
- Atualização assinada (Ed25519 + SHA-256) pela pasta compartilhada ou endereço fixo; `ferramentas/publicar.py`.
- `AGENDAR.bat`, saúde sem IA, log de rodadas, `SEGURANCA.md`, `MANUTENCAO.md`, `ROTEIRO-INSTALACAO.md`.

## v0.7.x (ainda do robô local)

- Privacidade: trocar o trecho de 600 caracteres guardado no banco por rótulos (assunto, rito), eliminando o único
  dado sensível possível; pre-commit com gitleaks e bandit; plano de incidente de uma página (ver SEGURANCA-REVISAO).
- GitHub: proteção do ramo `main`, Dependabot, 2FA, ações da CI fixadas por SHA.

- Preferências que faltam: porte, CNAE e valor da causa como filtros (dependem do CNPJ pelo nome e do valor digitado).
- Avisos por Telegram e e-mail só do que passa nas regras (reaproveitar `avisar.py`).
- Regra de "ação nova" nos TJs e TRFs (hoje marcada "a calibrar"); classe "execução fiscal" para a frente tributária.
- Endereço fixo de atualização (precisa do repositório público no GitHub).
- Integração de saída: webhook JSON (um POST por ação, com HMAC) e CSV importável; começar por EasyJur e ADVBOX (APIs
  documentadas) e pelo Astrea quando houver API; ver `docs/INTEGRACOES-MERCADO.md`.
- Wizard de um arquivo (`INSTALAR-LEXSUITE.bat`, para WhatsApp): cria a pasta, baixa pacote e Python, abre a tela.
  Depende de um endereço público de download (Drive "qualquer pessoa com o link" ou GitHub).
- Tela: mostrar a hora da próxima rodada agendada; botão "Abrir pasta de saída".

## v0.8 (cliente-servidor e conta na nuvem)

- Conta na nuvem (`judicial.solverone.com.br`): o robô, se tiver internet, pergunta a cada abertura se a conta do
  escritório continua ativa e registra um batimento (versão, última rodada, contagens). Gestão no RootifyONE.
  Regra de queda: sem resposta da nuvem, vale a aba Controle da planilha; sem nenhuma das duas por 30 dias, avisa
  e continua (não trava, por ser instalação local). Tabelas `lex_contas` e `lex_batimentos` no Supabase (SQL
  entregue para revisão e execução pelo dono, regra C10); chave publicável no `config.json`, nunca secreta.
- Código de cliente: formato `LEX-XXXX-XXXX` (letras e números, sem 0/O/1/I para não confundir), gerado no
  RootifyONE, enviado no e-mail de boas-vindas (bloco opcional já previsto no modelo em `docs/email/`) e pedido
  pelo passo a passo na instalação. Identifica a conta; não é senha e não dá acesso a nada sozinho.
- Endereço fixo de atualização: `judicial.solverone.com.br/atualizacao/` (site do produto). Assinatura na nuvem desde 08/Nov
  (serviço `assinatura.solverone.com.br`; publicação por tag `vX.Y.Z`, ver `docs/PUBLICAR.md`).

- Log de cada rodada numa aba oculta de uma planilha Google do cliente (via Apps Script publicado na conta da SolverONE;
  o robô só faz POST com biblioteca padrão; chave por cliente no `config.json`, nunca no código).
- Aba "Radar" com o incremento do dia e aba "Preferências" editável pelos advogados (as mesmas regras da v0.7).
- Painel de auditoria do fornecedor: leitura das abas de log pelo conector do Drive.

## 1.0 (SaaS no RootifyONE)

- Coletor central no Brasil (Supabase pg_cron + pg_net para a consulta leve; servidor pequeno para o caderno de 150 MB),
  lendo cada TRT uma vez para todos os escritórios. Tabelas `lex_publicacoes`, `lex_acoes`, `lex_regras`, `lex_eventos`.
- Fila de eventos: cada ação que passa nas regras de um escritório vira evento; entrega por e-mail, WhatsApp,
  notificação no app (PWA) e webhook de saída para o sistema do escritório.
- Interruptores do RootifyONE (`data-recurso`, `recursos-do-app.json`), PT/EN, feedback 💬, trabalho em `Fundo`.
- Bandit e Gitleaks no GitHub Actions (sem IA). Revisão de segurança e LGPD trimestral com a skill existente.

## Ideias registradas (portfólio)

- Monitor de publicações dos processos do escritório (já existe em `monitor.py`; virar produto).
- Jurimetria da vara e do juiz (DataJud); raio-x trabalhista de um CNPJ (para empresas); radar cível nos TJs
  (o DJEN cobre todos os tribunais).
- IA opcional e trocável (resumo, peças) com chave do próprio escritório, nunca no caminho principal.
