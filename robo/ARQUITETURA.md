# Arquitetura do robô LexSuiteONE · RADAR JUDICIAL (v0.7.23)

Leia antes de mexer. Python puro (só biblioteca padrão), **sem IA**, sem chave no código. Nada depende de modelo de
linguagem nenhum: as regras são escritas e explicáveis. Se um dia entrar IA (resumos, peças), entra como peça opcional
e trocável, com a chave do próprio escritório, nunca no caminho principal.

| Arquivo | O que faz | Onde mudar o quê |
|---|---|---|
| `lexsuite_robo.py` | linha de comando: `app` (a tela, o principal), `radar` (uma rodada sem tela), `monitor`, `orgaos`, `diagnostico`, `varas`, `vara`, `pauta`, `djen`, `tudo`. O `monitor` faz uma rodada (nossos processos + radar das varas), registra a rodada e gera a página do dia | novos comandos e o fluxo de cada um |
| `INSTALAR-PYTHON.bat`, `ABRIR.bat`, `RODAR.bat`, `AGENDAR.bat`, `DIAGNOSTICO.bat` | Windows sem instalar nada: baixa o Python portátil oficial para a pasta `python\`; abre a tela; roda uma rodada sem tela (agendador); gera o relatório de diagnóstico | |
| `lexsuite/app.py` | a tela local: servidor pequeno em 127.0.0.1 (só biblioteca padrão) que serve `radar_modelo.html`, entrega os dados (`/dados`), lista pastas sincronizadas (`/pastas`), salva configuração e tribunais (`/config`, `/testar-pasta`), roda o radar numa thread (`/rodar`, `/estado`) e aplica atualização assinada (`/atualizar`). POST só com o cabeçalho `X-LexSuite` da própria página. 0.7.10: abre a tela numa janela do Chrome ou do Edge (`--app`, sem barra de endereço), escolhe pasta pela janela do Windows (`/escolher-pasta`, PowerShell sem shell), cria a pasta que falta, aceita a função "Outra" e "Prefiro não informar", e ecoa cada passo da leitura na janela preta, com a hora | rotas, portas |
| `lexsuite/tribunais.py` | os 59 tribunais do DJEN que o robô lê (24 TRTs, 27 TJs, 6 TRFs, STJ e TST): sigla, estados, região, ramo; consulta pública do PJe nos TRTs; validação da escolha | nomes, regiões |
| `lexsuite/preferencias.py` | as abas editáveis da planilha única (`LexSuiteONE.xlsx`): Preferências, Exclusões e a aba oculta Controle (ativo, validade, versão mínima, mensagem); `bloqueio()` e `aplicar()` (marca excluídas, nunca apaga) | chaves e padrões |
| `lexsuite/compartilhar.py` | a pasta compartilhada: detecção das pastas do Drive/OneDrive, teste de gravação e a planilha única `LexSuiteONE.xlsx` (Radar + abas editáveis preservadas + ocultas Log, Saúde, Sobre); se a planilha estiver em uso, não regrava. 0.7.10: só o Google Drive na lista; pasta da planilha "<produto> - planilha" para instalação nova; "Testar" não deixa pasta vazia | colunas, nomes dos arquivos |
| `lexsuite/agendar.py` | "Ler sozinho" (0.7.9): uma tarefa "LexSuiteONE Radar" no Agendador do Windows (schtasks com XML, sem shell), um gatilho por horário de `radar.horarios` (padrão 20h e 8h, até 6), `radar.dias` todos ou úteis, e "executar assim que possível" quando o horário foi perdido; se o XML for recusado, uma tarefa simples por horário. Migra as tarefas antigas (19h40/7h10) ao abrir a tela. `notificar()`: aviso no canto da tela ao fim de cada leitura (PowerShell escondido, texto por variável de ambiente) | `PADRAO`, `MAXIMO` |
| `lexsuite/armazenamento.py` | 0.7.16 (`documentacao/DESENHO-PLANILHA-GRANDE.md`): a planilha é a vitrine, o arquivo completo fica no banco. `selecionar_arquivo` (últimos N dias + trabalhados, depois do corte da última limpeza), `caber` (limite de linhas), `aviso_tamanho` (80%), `disco` (`shutil.disk_usage`: ok, baixo < 5 GB ou 10%, crítico < 1 GB), `copia_seguranca` (planilhas + Arquivo em CSV em `Cópias de segurança/AAAA-MM-DD HHhMMmSS/`, 6 guardadas), `limpar` (cópia + corte em 30 dias, registrado como `limpeza_planilha`), `situacao` (o retrato da Configuração). Rotas `POST /armazenamento/limpar|copia|exportar`, `/abrir` com `copias` | números em `PASTA_COPIAS`, `COPIAS_GUARDADAS`, `AVISO_PCT`, `DISCO_*`; limite e dias na aba Preferências |
| planilha por frente (0.7.16) | `preferencias.NOMES_FRENTE` (`LexSuiteONE - Trabalhista.xlsx` etc.), `migrar_nome` (a `LexSuiteONE.xlsx` antiga vira a trabalhista), `planilhas_existentes`; `carregar(frente=)` soma as Exclusões das outras planilhas; `radar.gravar_planilha` grava uma por frente presente; `planilha.ler_xlsx(so_abas=)` lê só as abas editáveis (teto de 50 MB por parte, 1 GB no total) | nomes em `NOMES_FRENTE` |
| `lexsuite/historico.py` | 0.7.18 (itens 79 e 82; decisões 10 a 14): estatísticas dos meses anteriores. Tabelas `historico` (fila por tribunal e dia: fila, lido, sem_diario, erro) e `historico_processos` (para não contar o mesmo processo duas vezes). `pedir(meses, tribunais)`, `processar(limite=30, pausa=2 s)` soma só totais em `estatisticas_diarias` (nada em `leads`), `por_mes`, `por_dia_da_semana`. Roda à noite depois da leitura agendada (`lexsuite_robo.cmd_radar`, 18h a 7h) ou pela rota `POST /estatisticas/ler` (andamento em `GET /estatisticas`, parar em `/estatisticas/parar`) | `POR_VEZ`, `PAUSA_S`, `MESES_PADRAO` |
| 0.7.21/0.7.22 planilha e pastas | **Todo gravador do `.xlsx` passa por `planilha.escrever_xlsx`**, que chama `liberar_escrita` (bit de escrita do `st_mode`) antes do `os.replace` e, com `marcar=True` (planilha de consulta: `gravar_radar` e `criar_se_faltar`), `marcar_so_leitura` depois, e de novo no `except` se a troca falhar; `/abrir` "editar" libera; cópias de segurança com `copyfile` (sem a marca). `compartilhar.nuvens(gdrive)` acha Google Drive para computador e OneDrive (variáveis de ambiente e `~/OneDrive*`) para os atalhos da "Pasta compartilhada". `conta.situacao` devolve `texto` e `texto_en`; `_dias_para_tras` limita 0 a 10 | |
| 0.7.22 AssistONE | bloco `assistone-master` trocado pela cópia fiel de `rootify-one/assistone.js` 1.1.1 (tour com balão que desliza, personagem visível, botões do tour no tamanho certo sem o módulo comum); sem regra CSS local | |
| 0.7.21 revisão | CSP com `form-action 'self'` e `frame-ancestors 'none'`; `_ERRO_HIST_NEUTRO` na tela antes do `registrar_erro` (o texto com "avisada" só se o envio deu certo); `ultima_do_banco` tenta a URI só leitura e depois o caminho comum (UNC) | |
| 0.7.20 interruptores | `conta.verificar` guarda `recursos` da `lex-conta` v12 (`{id: bool}`, até 50, nomes até 60) em `cfg["conta"]["recursos"]`; sem o campo, mantém o último; `conta.situacao` devolve; a tela expõe `window.SolverRecursos` (`ligado`, `valor`, `aoMudar`) lendo `APP.conta.recursos`, que o AssistONE já obedece. Link do aceite com fragmento `#codigo=…&email=…&nome=…` | |
| 0.7.19 AssistONE | `<script id="assistone-master">` em `radar_modelo.html`: cópia fiel de `rootify-one/assistone.js` 1.0.0 (não editar; trocar o bloco quando o master mudar). Embutido porque o `atualizar.RAIZ_PERMITIDA` da versão instalada recusaria arquivo novo na raiz. Configurado no fim do script principal (`AssistONE.configurar`: telas por `telaAone()`, tour, dicas, busca; imagem em data URI 232 px); no retrato salvo (`MODO` arquivo) fica `ativo: false`. Preferências em `localStorage` (`dgo:radar-judicial:pref:aone:*`). Sem pedido externo | |
| 0.7.19 (tela e revisão) | `Servidor.estado_atual` cai na última execução "radar" do banco quando a tela reinicia (`ultima_do_banco`: conexão só leitura, guardada até a data do arquivo mudar); `config.json` aceita `radar.estatisticas_por_vez` (padrão 30, `historico.POR_VEZ`); `/testar-pasta` com `leve` só confere permissão, sem gravar (teste automático da tela); `/testar-pasta` devolve `alvo` (caminho inteiro); `escolher_pasta` mostra um formulário invisível ativo para a janela de pastas abrir na frente; `historico.processar` reserva cada Diário ("lendo"), para a fila só depois de 3 falhas seguidas de site fora, mensagens `{pt,en}`; `banco._copia_antes` grava `lexsuite.db.antes-<versão>-<data>` via `.tmp` + `os.replace`; `user_version` 719 devolve a turma trabalhada; item da tela ganha `sinal`. Tela: `gruposMenu()` alimenta o menu (gaveta com `transform`, 240 ms, `prefers-reduced-motion`) e a busca geral (`#busca-global`: opções, ações da Lista e do Arquivo, títulos do manual com `#:~:text=`) | |
| 0.7.18 (banco e tela) | coluna `leads.fora_criterio` e `_reclassificar_0718` (uma vez, `user_version` 718): o que a regra antiga guardou sem sinal de ação nova, ou de 2º grau, sai de lista, arquivo, planilha, retorno e estatísticas, sem apagar; `banco.completar` aceita `uf` (do endereço da área logada, `contatos.uf_do_endereco`). Tela: engrenagem e perfil em janela; `modoPagina` pelo menu; perfil com licença e e-mail/escritório fixos; cópia com `/abrir` `ultima_copia` e `pasta_copias` | |
| 0.7.17 | `classificar.segundo_grau` (turma, gabinete, seção especializada, pleno, presidência) tira o 2º grau em `djen.leads` e em `radar.montar_radar` (os já guardados); `banco.limpar_detalhe(so_nunca_abertos=True)` com 6 meses quando o banco passa de 1 GB (decisão 14); `armazenamento.limpar` não enxuga sem cópia; evento `criterio` com a data da mudança da regra (mostrado no Painel). Tela: `MULTI`, `passaFiltros(i, menos)` e `desenharMulti` (filtros com várias opções e contagem que segue os outros filtros) | `_SEGUNDO_GRAU`, `MULTI` |
| tela 0.7.16 | `app.vigiar_tela` fecha a janela preta 3 min sem pedido da tela (relógio que pula = computador acordou: recomeça); `POST /sair`; `POST /valor` (valor da causa no banco, `banco.completar`); `/contatos/preparar` monta o pedido só do que falta (`contatos.preparar_v1`) e `/contatos/colar` lê a `RESPOSTA PARA O RADAR v1` (`contatos.colar_v1`); `/dados?visao=arquivo` manda as 5 mil mais recentes e busca no programa com `q` | `ARQUIVO_NA_TELA`, `FECHAR_SEM_TELA_S` |
| leitura interrompível (0.7.15) | `radar.Interrompida`; `radar.executar(parar=...)` e `monitor.coletar_caderno(parar=...)` checam entre Diários e entre ações; a tela pede pela rota `POST /interromper`, que grava `saida/parar.json` (vale também para a leitura agendada, que roda noutro processo; `Estado.parar()` só aceita pedido posterior ao início); `saida/leitura.json` leva `atrasada` (`agendar.horario_perdido`, só com `RODAR.bat --agendado` e se não houve leitura depois do horário marcado) | |
| `lexsuite/contatos.py` | 0.7.14: completar contatos pela área logada (desenho dos contatos, Arquitetura): `preparar` grava `saida/contatos/buscar-contatos-AAAA-MM-DD.md` com instruções e até N processos sem contato (padrão 30 por dia); `colar` lê a tabela Markdown de 8 colunas sem IA e recusa linha a linha (CPF, reclamante/testemunha/preposto, processo fora da lista, canal desconhecido, formato inválido, contato de pessoa sem fonte) | regra de dado: Arquitetura |
| `lexsuite/frentes.py` | 0.7.14: frente de cada ação por regra escrita (TRT/TST = trabalhista; nos outros, classe e assunto: tributário, empresarial, cível; "a conferir" quando não reconhece) | lista de palavras |
| `lexsuite/causas.py` | 0.7.13: por que uma leitura não deu certo, pela resposta do site (nunca pelo relógio): ok, ainda_nao_liberado_3h (o 403 do DJEN "só a partir das 03:00"), nao_publicado, governo_fora (429, 5xx, tempo esgotado), bloqueio_fora_do_brasil, sem_internet, erro_do_programa; mensagens claras em PT e EN. `rede.ErroHTTP` e `rede.SemResposta` guardam o código e o texto da resposta. `monitor.coletar_caderno` trata cada tribunal à parte (um com problema não derruba os outros) e devolve as tentativas; `radar.registrar_tentativas` grava o histórico (tabela `execucoes`, tipo `tentativa`), que aparece na tela ("Histórico de leituras", rota `/historico`) e na aba Log da planilha, agora visível | causas e textos |
| `lexsuite/banco.py` (0.7.14) | situações do processo com as chaves da Arquitetura (`novo, visto, em_analise, em_contato, virou_cliente, descartado, arquivado`; as antigas migram sozinhas), `mudar_situacao` em lote com o "antes" para desfazer, tabela `acoes` (quem, quando UTC e fuso, o quê, quantos), `contatos` e `contatos_historico`, `estatisticas_diarias` (nunca apagada), colunas `frente`, `data`, `porte`, `faixa_valor`, `motivo`, `status_em`, `bruto_limpo`; `limpar_detalhe` troca o dado completo das ações velhas por um resumo (sem o trecho do Diário) e `compactar` (VACUUM); `retorno()` monta os totais por situação que vão à SolverONE na conferência da licença (`conta.verificar(retorno=...)`) | regra: Arquitetura |
| `lexsuite/planilha.py` | leitor e escritor de `.xlsx` só com a biblioteca padrão (strings inline, abas ocultas, cabeçalho em negrito, limite de 50 MB na leitura; 0.7.12: aba com `visual` ganha cabeçalho azul-marinho com letra branca, quebra de texto, colunas `moeda` em R$, linhas `destacar` em latão claro, `filtro` com autoFilter e o nome `_xlnm._FilterDatabase`, que o Excel e o Google Planilhas reconhecem) | |
| `lexsuite/saude.py` | avaliação sem IA de cada rodada (DJEN mudou? regra frouxa? Receita sem resposta?) gravada no banco e na aba Saúde | limiares |
| `lexsuite/atualizar.py` | atualização assinada: procura em `<compartilhada>/LexSuiteONE/atualizacao` e no endereço fixo, verifica Ed25519 + SHA-256, lista fechada de arquivos, guarda a anterior em `_anterior/` | nomes permitidos |
| `lexsuite/assinatura.py` | Ed25519 (RFC 8032) em Python puro, com vetores de teste da RFC | |
| `ferramentas/publicar.py` | ferramenta do suporte (fora do pacote do cliente): gera chaves e empacota uma versão assinada | |
| `lexsuite/config.py` | `config.json`: padrão, criação automática na primeira vez, gravação | chaves novas |
| `lexsuite/rede.py` | todo pedido à internet: intervalo mínimo, novas tentativas, aviso de bloqueio fora do Brasil | velocidade (não diminuir os intervalos) |
| `lexsuite/datajud.py` | DataJud: chave pública lida da página do CNJ, busca paginada, estatística da vara, códigos TPU de desfecho | métricas da vara |
| `lexsuite/djen.py` | DJEN: caderno diário (padrão), busca paginada e busca filtrada (OAB, processo, parte); transforma publicações em leads | nomes de campos do DJEN |
| `lexsuite/monitor.py` | monitor: o que acompanhar, conferência (OAB, processo, cliente, CNPJ), tipo do ato e urgência, não avisar duas vezes; radar das varas (`varas_alvo`, `coletar_radar`, `acoes_novas`); nota (`pontuar`); sinais e setor; montagem dos dados da página (`montar_pagina`). `dias_uteis`: hoje e os N dias úteis anteriores (0.7.10: domingo e segunda leem a sexta) | regras de tipo de ato (`_REGRAS_ATO`), sinais |
| `lexsuite/radar.py` | o radar: `executar` (uma rodada: cadernos, ações novas, Receita, banco, saída), `montar_radar` (dados da página por período), `item_de_lead` (a ficha), regra "jurídico próprio provável" (capital social acima do teto ou grande grupo), planilha | teto do gigante, lista de grandes grupos, colunas |
| `lexsuite/diagnostico.py` | relatório `diagnostico\radar-diagnostico.txt` do que o radar guardou: contagens por tipo, classe, pista de "ação nova" e vara, empresas mais citadas e amostras com reclamante, advogado e CPF mascarados. Serve para calibrar a regra com dados reais sem mandar o banco | pistas (`PISTAS`), regra estrita em teste (`ESTRITA`) |
| `lexsuite/prazos.py` | publicação (D+1 útil), início do prazo (D+2 útil), vencimento estimado; feriados nacionais e forenses, recesso e suspensão de 20/12 a 20/01 | feriados |
| `lexsuite/pauta.py` | pauta pública de audiências do PJe (segunda fonte, roda de qualquer lugar) | tipos de audiência aceitos |
| `lexsuite/classificar.py` | regras: empresa × pessoa física, CNPJ, valor da causa, nota 0–100 com motivos, carteira de clientes | pesos da nota |
| `lexsuite/conta.py` | licença do escritório: código `LEX-XXXX-XXXX` conferido na função `lex-conta` do Supabase (sem chave no programa) ao abrir e antes de cada leitura; cadastro de quem usa (e-mail é a chave, um escritório por e-mail) e do CNPJ; bloqueia sem código, desconhecido, desativado, vencido ou 15 dias sem resposta. Na nuvem (`nuvem/supabase`): pessoa ativa = num computador e vista em 30 dias; só ativas contam no limite; histórico em `lex_eventos`; a tela Clientes → Licenças do RADAR do RootifyONE usa `lex-admin.sql`. Na tela (0.7.9), o perfil (iniciais no alto) muda um dado por vez pelo `POST /config` | `DIAS_SEM_RESPOSTA`, `URL_PADRAO` |
| `lexsuite/cnpj.py` | cadastro público da empresa pela Receita (BrasilAPI / Minha Receita), com cache: porte, capital, CNAE principal e secundários, cidade, telefone, e-mail, sócios e administradores | campos da empresa |
| `lexsuite/banco.py` | SQLite `lexsuite.db`: leads (ações), publicacoes (nossos processos), rodadas, cadernos, cache de CNPJ, execucoes | tabelas (na fase SaaS viram tabelas do Supabase) |
| `lexsuite/saidas.py` | CSV (; + BOM, abre no Excel), painel HTML e dados.json | colunas da planilha |
| `lexsuite/avisar.py` | e-mail SMTP (senha só pela variável `LEXSUITE_SMTP_SENHA`) e Telegram (token só pela variável `LEXSUITE_TELEGRAM_TOKEN`; nunca aparece em mensagem de erro) | texto dos avisos |
| `painel_modelo.html` | o painel (PT/EN, claro/escuro, celular). O robô troca `window.LEXSUITE_DADOS = null;` pelos dados | visual do painel |
| `radar_modelo.html` | a tela: uma linha por ação, clique abre a ficha estruturada (cada dado numa linha, "não informado" / "não capturado"), valor da causa digitável (fica no navegador), status, exportar planilha. 0.7.12: abas Painel e Lista; o Painel mostra números do período, ações por dia (por mês acima de 31 dias), faixas de valor, setores, empresas, porte, tribunais (ou varas) e estados, com os mesmos filtros da lista; clicar numa barra abre a lista filtrada; barras em HTML e CSS, sem biblioteca nem pedido externo; nada é específico da frente trabalhista. Servida pelo `app.py` (busca `/dados`; barra de tribunais por região/estado, período, Atualizar agora) ou gravada com os dados embutidos em `saida/radar/radar.html` (o robô troca `window.LEXSUITE_RADAR = null;`) | visual e textos |
| `monitor_modelo.html` | a página "O dia nos tribunais" (tema do escritório, PT/EN, claro/escuro, celular): exige ação, fita do dia por rodada e tribunal, empresas/tribunais/setores, lista com agrupamentos; modo "Ao vivo" (o navegador consulta o DJEN). O robô troca `window.LEXSUITE_MONITOR = null;` pelos dados | visual e textos da página |
| `exemplos/` | `radar_exemplo.json` (gerado por `gerar_radar_exemplo.py`): um dia **fictício** do Radar SP; `dia_exemplo.json`: um dia **fictício** em 3 tribunais e 4 rodadas (gerado por `gerar_dia_exemplo.py`) para `monitor --exemplo` e `--teste-aviso` | a amostra |
| `testes/` | 55 testes: regras, tela, planilha, assinatura (vetores da RFC 8032), atualização e preferências (`TESTAR.bat`) | acrescentar um teste a cada regra nova |

## O que não se toca

- Pessoa física nunca sai do robô: `djen.leads` e `pauta.leads_da_pauta` descartam antes de guardar;
  `saidas.lead_para_saida` é a lista do que pode sair.
- Nada de contornar captcha, trocar de IP para fugir de limite ou abrir várias cópias ao mesmo tempo.
- Nenhuma chave ou senha em arquivo. A chave do DataJud é pública e lida da página do CNJ a cada rodada.
- Monitor: o texto das publicações dos processos do escritório fica só no `lexsuite.db` local e nos avisos
  para o próprio escritório. Uma publicação só é marcada como vista depois que algum aviso ligado saiu
  (se o Telegram e o e-mail falharem, ela volta na rodada seguinte).
- `config.json`, `carteira.csv`, `processos.csv`, `lexsuite*.db`, `saida/` e `diagnostico/` nunca vão para
  o GitHub (estão no `.gitignore`).

## Como o Radar acha as coisas (e o que fica com gente)

1. Caderno do DJEN de cada tribunal do config (1 download por tribunal por dia, lido na memória e descartado).
2. Fica só o que é ação nova contra pessoa jurídica (lista de distribuição ou notificação inicial); reclamante (pessoa
   física) é descartado antes de gravar.
3. Rito: ordinário = acima de 40 salários mínimos; é o primeiro corte de valor que o Diário permite.
4. CNPJ no texto do Diário → Receita (porte, capital social, CNAE, cidade, telefone, e-mail, sócios). Sem CNPJ no texto,
   a ficha fica "a conferir" e o CNPJ sai do mesmo clique do valor da causa.
5. Valor da causa: o Diário não traz; está na consulta pública do PJe atrás de um captcha. A página tem "Abrir consulta
   no PJe" e o campo para a pessoa digitar (fica no navegador e sai na planilha). O robô não burla captcha.
6. "Jurídico próprio provável": capital social acima do teto do config ou nome de grande grupo. Vai para o fim, não some.

## Como o monitor acha as coisas (e quanto pesa)

- **Nossos processos**: uma consulta à API do DJEN por OAB, por número de processo e por nome de cliente,
  só do período (`dias_para_tras`). Resposta em texto (JSON), poucos KB. Vale para todos os tribunais.
- **Radar das varas** (`alvos` do config): uma consulta por vara, pelo `orgao_id` (idOrgao). O id é descoberto
  uma vez com `orgaos --tribunal TRTn` (baixa o caderno daquele dia, guarda só o mapa nome → id em
  `orgaos_TRTn.json`). Depois disso nada de caderno: só texto do período.
- **Caderno do dia** (`--caderno`): opcional, ~150 MB por TRT; lido na memória e descartado; só o que casa
  é guardado. Serve de rede de segurança ou quando a busca filtrada estiver bloqueada (403).
- **Identidade de uma publicação**: hash do processo + data + texto; a mesma publicação vinda por caminhos
  diferentes nunca avisa duas vezes.
- **Rodadas**: cada execução do `monitor` vira uma linha em `rodadas` (hora, modo, quantas conferidas, quantas
  novas, por tribunal). É isso que a página desenha na fita do dia.

## Caminho para a plataforma (fase SaaS)

O formato dos leads (`dados.json`) é o mesmo que vira tabela no banco da plataforma. Migrar é trocar
`banco.py` (SQLite → Supabase) e rodar o coletor do DJEN num servidor no Brasil.

Monitor na plataforma: o coletor roda num servidor em São Paulo a cada 15–30 min à noite e grava em
`lex_publicacoes` (uma linha por publicação, por escritório). A partir daí o "webhook" é nosso: cada linha
nova dispara o aviso no app (notificação do PWA), no e-mail e no Telegram, e aparece na caixa do app.

## O fluxo da v0.7 (pasta compartilhada)

1. `ABRIR.bat` abre a tela; na primeira vez o assistente pede o cadastro, a pasta da planilha (Google Drive detectado, outra pasta ou a do programa) e os tribunais.
2. Cada rodada: lê as abas editáveis de `LexSuiteONE.xlsx` (bloqueio? exclusões? mínimo de ações?), baixa os cadernos,
   guarda as ações, avalia a saúde, registra no log, grava `saida/radar/` e regrava `LexSuiteONE.xlsx` (preservando as
   abas editadas) + `.html` na pasta compartilhada. Planilha em uso: deixa como está e tenta na próxima rodada.
3. O suporte lê Log/Saúde/Sobre pela pasta compartilhada; edita a aba Controle para pausar, avisar ou exigir versão;
   solta pacotes assinados em `atualizacao/`. Nada disso usa internet própria do robô: o Drive carrega.

## Nomes e endereços: um só nome em tudo

SolverONE é a empresa. **LexSuiteONE** é a suíte jurídica (o repositório e o remetente dos e-mails). **RADAR JUDICIAL** é
este produto, escrito em maiúsculas com o "IA" em latão (`RADAR JUDIC<b>IA</b>L` na tela e no manual); dentro dele ficam as frentes
(Radar Trabalhista hoje; Tributário e Cível e empresarial a seguir). Outros produtos da suíte seguirão o mesmo padrão.

**O nome do produto é configuração** (decisão do dono, 08/Nov): fica só em `docs/marca.json` (`nome` exato, `curto`,
`destaque` em latão), hoje "RADAR JUDICIAL". O site (`paginas/` → `ferramentas/marca.py` → `docs/`) e o e-mail de
boas-vindas já leem dali, e o pacote leva uma cópia (`robo/marca.json`) que a tela, o manual, o atalho e o aviso do
Windows usam. Ainda fixos: a aba Sobre da planilha e o e-mail de aviso (ver `PENDENCIAS.md`).

| Onde | Nome |
|---|---|
| Suíte (repositório, remetente, nome do pacote) | LexSuiteONE |
| Produto (tela, manual, site) | JUDICIAL, frente Radar Trabalhista |
| Site e serviço | `judicial.solverone.com.br` (GitHub Pages servindo a pasta `docs/` do repositório; CNAME na zona do Cloudflare) |
| Download | instalador `judicial.solverone.com.br/downloads/Instalar-LexSuiteONE.zip`; pacote completo (plano B) `downloads/LexSuiteONE-RADAR.zip` (arquivos em `docs/downloads/`; as cópias em `releases/` são histórico) |
| Atualização assinada | `judicial.solverone.com.br/atualizacao/versao.json` e o `.zip` ao lado (pasta `docs/atualizacao/`), além da subpasta `atualizacao` do Drive do cliente |
| Assinatura das versões | serviço `assinatura.solverone.com.br` (Worker do Cloudflare com a chave Ed25519 guardada num Durable Object: a chave privada nunca sai do Cloudflare e ninguém a lê). Só assina a pedido da automação deste repositório, para uma tag `vX.Y.Z`. A chave pública está em `chave_publica.txt`, dentro do pacote |
| Remetente dos e-mails | `LexSuiteONE <nao-responda@solverone.com.br>`, pelo Resend; não recebe respostas |
| Dúvidas do cliente | `judicial@solverone.com.br` (contato de toda a suíte LexSuiteONE; cada suíte tem o seu, ex. `moneytrio@`; `contato@` é o genérico da SolverONE) |
| Compartilhamento do Drive | `integracao@solverone.com.br`: endereço de sistemas, não é caixa de atendimento; vira Conta Google para o Drive |
| Contato de pessoas (suporte) | `judicial@solverone.com.br` (`preferencias.SUPORTE`): manual, aba Sobre e linha "suporte" da aba Controle; planilha antiga com `integracao@` passa a `judicial@` |
| Instalação | `instalador/INSTALAR.bat` (fora do pacote), servido em `docs/downloads/Instalar-LexSuiteONE.zip`; lê `docs/atualizacao/instalar.txt` (gerado por `ferramentas/marca.py` a partir de `versao.json` e `marca.json`) e o ícone `docs/radar.ico` |
| Manual | um só: `paginas/manual.html` gera o do site (`docs/manual.html`) e o do pacote (`robo/MANUAL-DO-ESCRITORIO.html`, com os marcadores `<!--OLA-->` e `<!--PARA_VOCE-->`) |

A zona DNS de `solverone.com.br` está no Cloudflare desde 07/Nov/2026 (servidores `harlee` e `lennon.ns.cloudflare.com`),
com DNSSEC ativo; o Claude altera registros pelo conector de API. O site segue no GitHub Pages, com proxy desligado.
Nenhum contato pessoal do dono aparece no que o cliente vê.
