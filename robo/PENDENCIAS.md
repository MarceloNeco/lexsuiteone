# Pendências do robô LexSuiteONE (07/Nov/2026, depois da v0.7.0)

Lista viva. Quem continuar (qualquer modelo ou pessoa) lê este arquivo e o `ARQUITETURA.md` antes de mexer.

## Esperando o dono (Marcelo)

- Rodar `DIAGNOSTICO.bat` no computador no Brasil e mandar `diagnostico\radar-diagnostico.txt` (arrastar para o Drive).
  Sem ele a regra de "ação nova" fica frouxa: 6.816 ações num dia em TRT2+TRT15, esperado 1.500 a 2.000.
- Testar a v0.6.0: `INSTALAR-PYTHON.bat`, `ABRIR.bat`, escolher tribunais, "Salvar e atualizar agora", print da tela e da ficha.
- Rodar `teste-djen-supabase.sql` no SQL Editor do projeto solverone-app e mandar o resultado (decide se o coletor
  central pode viver no Supabase ou precisa de um servidor pequeno em São Paulo).
- Decidir o repositório público no GitHub (núcleo aberto, MIT ou Apache 2.0). Nada é criado sem esse sim.
- Criar a conta Google `integracao@solverone.com.br` (e o apelido `lexsuite@`), para a trilha cliente-servidor.

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
- Endereço fixo de atualização já aponta para as Releases do GitHub (`marceloneco/lexsuiteone`).

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
