# RELATÓRIO FINAL · Prompt 3 · Astrea (sistema de gestão do escritório)

Execução: 13/11/2026, ~14h30–14h40 (horário de Brasília), no Chrome com o Astrea já logado (com o usuário do advogado, escritório KR Law). Cerca de 55 ações, somente leitura.

**Diferença em relação ao prompt original:** a pedido do Marcelo, desta vez as telas também foram salvas como imagem (arquivos `TELA-xx_*.jpg` neste mesmo .zip). O número da TELA no texto é o mesmo do nome do arquivo.

## Conferência antes de entregar

- Nada foi criado, alterado, importado, exportado ou excluído. Os formulários "Editar contato", "Adicionar contato", "Editar processo" e "Adicionar atendimento" foram abertos só para ler os rótulos e fechados por "Cancelar" ou saindo da página, sem clicar em SALVAR.
- Nenhum botão "Exportar", "Descartar", "Gravar como histórico", "Concluir" ou "Adicionar prazo" foi clicado (só os menus foram abertos para ler as opções).
- Ao chegar em Publicações já havia um aviso "As publicações estão sendo descartadas, por favor aguarde a execução da ação!". Isso não foi disparado nesta visita (estava em andamento antes).
- Neste texto não há nome de pessoa física nem de magistrado. **As imagens, porém, mostram o que estava na tela** (nomes de advogados e membros da equipe, alguns clientes pessoa física em listas). Dois dados foram tarjados de preto: o login (CPF) na TELA 05 e os dados do cartão na TELA 31. Não repasse as imagens para fora do projeto sem revisar.
- Faltou a **Parte A** (página pública até a tela de login): quando a visita começou, a sessão já estava logada, então não houve a PAUSA PARA LOGIN. Não saí da conta para não derrubar a sessão do advogado.

---

## 1. Mapa dos módulos e caminhos de menu

Base de todas as URLs: `https://astrea.net.br/` (o app é de página única; a rota vem depois do `#`).

| Módulo (nome exato no menu) | URL | TELA |
|---|---|---|
| Área de trabalho | `#/main/workspace/[,]` | 01 |
| Gestão kanban | `#/main/kanban` | 25 |
| Agenda | `#/main/calendar` | — |
| Workflows | `#/main/workflow-module` | 26, 27 |
| Contatos | `#/main/contacts` | 07, 08 |
| Atendimentos | `#/main/consulting/list/` | 23, 24 |
| Processos e casos | `#/main/folders/[,,]` | 16–18 |
| Publicações | `#/main/clippings` | 19–22 |
| Financeiro | `#/main/financial/entries` | 33 |
| Peças jurídicas (JUX, IA) | `#/main/argo/start` | — |
| Jurisprudência (JUX, IA) | `#/main/jurisprudence/start-conversation` | — |
| Documentos | `#/main/documents/[,,]` | — |
| Indicadores | `#/main/dashboard-module` | 34 |
| Alertas | `#/main/alerts` | — |
| Suporte | `#/main/support` | — |

Barra superior (ícones, com o título exato ao passar o mouse): ✦ (assistente de IA), **Adicionar** (+), **Resultados de buscas** (nuvem), **Cronômetro timesheet**, **Comentários**, **Novidades Astrea**, **Administração** (engrenagem), menu do usuário (**Meu perfil**, **Meu plano**, **Sair**) — TELAS 15 e 32.

Menu "Adicionar" (+): Processo manual · Processo busca automática · Caso · Atendimento · Tarefa · Evento · Prazo · Audiência · Contato (TELA 15).

Administração do Astrea (`#/main/admin/...`), abas: Escritório · Equipe · Acesso (Usuários / Clientes) · Publicações (Publicações Astrea / Intimações eletrônicas) · Modelos de documento · Integrações · Certificado Digital · Segurança (TELAS 02–06).

Módulos que **não existem** com esses nomes: "Clientes" (é um tipo dentro de Contatos), "Prospecção", "Oportunidades", "Funil", "Leads", "CRM", "Relatórios" (o mais próximo é Indicadores + botões de imprimir/Excel em cada lista), "Configurações" (é "Administração").

## 2. Tabela de campos do processo

Tela: Processo → ⋮ → **Editar** → "Editar processo" (`#/main/folders/lawsuit/add-edit/[id,,,true]`), TELAS 18a/b/c. A tela de leitura (Resumo) é a TELA 16.

| Campo | Rótulo exato | Obrigatório? | Formato |
|---|---|---|---|
| Pasta | Pasta | não | busca ("Digite o nome ou número da pasta") |
| Cliente(s) + papel | Clientes* + Qualificação | **sim** | busca em Contatos + texto/busca do papel (ex.: Agravante); "Adicionar cliente" para mais de um |
| Outras partes | Outros envolvidos + Qualificação | não | busca em Contatos + papel (ex.: Agravado); "Adicionar envolvido" |
| Título | Título* | **sim** | texto com busca |
| Etiquetas | Etiqueta | não | seletor de etiquetas |
| Instância | Instância | não | lista: 1º Grau / 2º Grau / Superior / Supremo / Outra |
| Número CNJ | Número | não | texto ("Digite o número do processo") |
| Tribunal / vara / foro | Juízo (Nº · Vara · Foro) | não | 3 campos; Vara e Foro com busca |
| Classe / tipo de ação | Ação | não | busca ("Digite a ação") |
| Link | Link no tribunal | não | URL |
| Objeto | Objeto | não | texto longo |
| Valor | Valor da causa | não | moeda |
| Distribuição | Distribuído em | não | data |
| Condenação | Valor da condenação | não | moeda |
| Observações | Observações | não | texto longo |
| Responsável | Responsável* | **sim** | busca entre usuários |
| Acesso | Acesso | — | Público / Privado / Equipe |

Na tela de leitura aparecem também: Status (ex.: "Ativo 1º Grau"), Criado por, Criado em, partes com o papel e o selo **CLIENTE PRINCIPAL**, Últimos históricos, Recursos e desdobramentos, Valores, Apensos, Próximas atividades, Documentos, Atendimentos, Honorários, Despesas, Timesheet.

- **Juiz ou relator:** não encontrei campo próprio. O nome só aparece dentro do texto das publicações/andamentos.
- **"Origem" / "como chegou o caso":** **não existe** no processo. Existe no contato com perfil Cliente (ver item 4).
- Menu ⋮ do processo (TELA 17): Apensar outro processo a este · Apensar este processo a outro · Alterar instância atual · Desvincular do tribunal · Imprimir relatório · Editar · Encerrar · Excluir.

## 3. Publicações e intimações (como entram hoje)

- **Onde aparecem:** menu Publicações (`#/main/clippings`), com contador no menu (6 no dia). Painel: "Não tratadas de hoje", "Tratadas hoje", "Descartadas hoje", "Não tratadas" + gráfico da semana (TELA 19).
- **Lista** (TELA 20), colunas: DIVULGADO EM (e "Publicado em") · TIPO · PROCESSO (número + pasta vinculada + responsável) · **DIÁRIO** · NOME PESQUISADO · STATUS (ex.: NÃO TRATADA). Filtros: texto, ESTADOS, STATUS. Ícones: Imprimir, **Exportar Publicações**, Atualizar publicações.
- **De onde veio:** sim, cada publicação mostra o diário na coluna DIÁRIO (códigos como `TJSPDJN`, `TRSPNDJN`, `TJSP2` + órgão) e, ao expandir, o texto traz "Meio: Diário de Justiça Eletrônico Nacional" e um `comunicacao_id` — ou seja, a fonte principal hoje é o **DJEN**.
- **Configuração de captura** (Administração → Publicações):
  - **Publicações Astrea** (TELA 04): lista por nome pesquisado, colunas TIPO (PF) · NOME · DIÁRIO DE JUSTIÇA ("Todos os estados, Superiores") · QUEM RECEBE · STATUS · DIÁRIOS OFICIAIS MONITORADOS ("Visualizar lista de diários monitorados"). O plano dá 5 nomes; 3 em uso, "2 vagas para pesquisas em diários oficiais". Opção sobre publicações duplicadas quando mais de um nome é citado.
  - **Intimações eletrônicas** (TELA 05): login do advogado em tribunais (ex.: TRF03 PJe 1º e 2º grau, TJRJ PJe), colunas TRIBUNAL · NOME/PERFIL DE ACESSO · LOGIN · QUEM RECEBE · STATUS. No dia, as 3 estavam com erro ("Falha no login" / "Falha no cadastro, realize o cadastro novamente").
  - Aviso vermelho na tela de Publicações: "Instabilidade na Captura de Informações — 3 nomes cadastrados no Astrea não estão sendo monitorados", botão VERIFICAR INSTABILIDADE.
  - **Domicílio Judicial Eletrônico:** não encontrei configuração com esse nome. **Aviso por e-mail:** não encontrei configuração específica (só o "Quem recebe" por usuário).
- **Publicação → tarefa ou prazo** (TELA 21): ícone **+** (Adicionar) → Adicionar prazo · Adicionar audiência · Adicionar tarefa · Adicionar evento. Ícone ✔ = **Concluir** (marcar como tratada). Menu ⋮ (TELA 22): Abrir em nova aba · Descartar. Há também sugestões de IA ("Tratamentos sugeridos: GRAVAR COMO HISTÓRICO", "ADICIONAR UM PRAZO PARA [data]").
- **Outra porta de entrada de processos:** "Resultados de buscas" (nuvem, `#/main/pending-search/...`), TELAS 28–30: Buscas individuais (por número CNJ ou tribunal), **Buscas em lote pela OAB** (nunca usada) e Vínculos (23 processos vinculados, 1 com erro; 170 créditos de 1000 processos monitorados). Ao vincular, o Astrea passa a puxar os andamentos do tribunal.

## 4. Prospecção, contatos e CRM

- **Módulo de prospecção/funil/leads/CRM:** não existe com nenhum desses nomes.
- O que mais se aproxima:
  - **Atendimentos** (TELAS 23–24): registro de conversas/reuniões com cliente. Status: Todos / Em andamento / Fechados. Formulário "Adicionar atendimento": Clientes* · Assunto* · Etiqueta · Processo, caso ou atendimento · 1º Registro do atendimento*. O escritório usa um atendimento chamado "Oportunidades Comerciais" como controle comercial.
  - **Workflows** (TELAS 26–27): há um workflow "Gestão de clientes" com 5 passos (contatar, reunião mensal, destacar casos, oferecer novas oportunidades, pedir feedback).
  - **Gestão kanban** (TELA 25): quadro "QUADRO KANBAN PADRAO" com colunas A Fazer / Fazendo / Concluída — para tarefas, não para leads.
- **Contato e cliente:** é o mesmo cadastro, com o campo **Perfil** = Cliente ou Contato (ver item 6).

### Tabela de campos do contato pessoa jurídica

Tela: Contatos → ADICIONAR → "Pessoa juridica" (`#/main/contacts/add-edit-merge/[,,false,[],]/personal`), TELAS 11–14. Três abas: **Informações pessoais · Informações complementares · Documentação**.

| Campo | Rótulo exato | Obrigatório? | Formato |
|---|---|---|---|
| Razão social | Empresa* | **sim** | texto |
| Nome fantasia | Nome fantasia | não | texto |
| Tipo | Perfil | — | Cliente / Contato (padrão: Contato) |
| Etiquetas | Etiquetas | não | seletor |
| Telefone | Telefone (tipo + número + Operadora) | não | **vários** ("Adicionar telefone"); tipos: Celular comercial, Telefone comercial, Fax, Celular pessoal, Telefone pessoal, **WhatsApp**, Outro |
| E-mail | Email (tipo + e-mail) | não | **vários** ("Adicionar email"); tipos: Comercial, Pessoal |
| Site | Site | não | **vários** ("Adicionar site") |
| Redes sociais | — | — | **não existe campo**; só dá para usar "Site" ou Comentários |
| Origem | Origem do cliente | não | **só aparece com Perfil = Cliente**; texto com busca; dica: "Sugestões: contato direto, indicação, site, entre outros." |
| Endereço | Endereço (tipo + CEP, rua, número, bairro, complemento, cidade, estado, país) | não | vários ("Adicionar endereço"); tipos Comercial / Pessoal |
| Pessoa de contato | Contato | não | busca em Contatos (aba Informações complementares) |
| Cargo | Cargo | não | texto com busca |
| Código interno | Código | não | texto |
| Observações | Comentários | não | texto longo |
| Conta bancária | Conta corrente / Conta poupança · Banco · Agência · Conta · Pix | não | texto |
| CNPJ | CNPJ | não | texto (aba Documentação) |
| IE / IM | Inscrição estadual · Inscrição municipal | não | texto |
| Simples | Optante Simples Nacional | não | Sim / Não |
| Responsável | — | — | **não existe** no contato |

Observações:
- O único campo obrigatório é **Empresa\***.
- O contato de exemplo aberto (uma "LTDA", TELAS 09–10) está cadastrado como **pessoa física**, com campos de CPF/RG etc. — sinal de que a equipe nem sempre escolhe "Pessoa juridica". Na integração, convém forçar PJ.

## 5. Importação de contatos

- **Não encontrei** importação de contatos ou clientes por planilha (CSV/Excel) em lugar nenhum: nem no menu ⋮ de Contatos (que só tem Exportar contatos · Extrair emails · Ficha resumida · Ficha completa — TELA 07), nem em Administração, nem no menu do usuário.
- Em "Meu plano" (TELA 31) aparece "Serviços adicionais: **Migrações de dados**, jornadas de implantação e consultorias. Compra única, cobrada à parte" — ou seja, carga em massa hoje parece ser **serviço pago da Aurum**, não autoatendimento.
- **Duplicados:** o formulário de contato tem a mensagem (oculta até acontecer) "Já existe um contato com este CNPJ" e existe a tela **"Unificar contatos"** ("Separamos os dados dos contatos escolhidos. Para mesclar…"). Ou seja: o sistema avisa duplicado **por CNPJ** e permite mesclar manualmente.
- Colunas de modelo, formatos aceitos: não se aplica (não há tela de importação).

## 6. De contato a cliente

1. Contatos → abrir o contato → ícone de lápis (Editar) → campo **Perfil** → trocar de "Contato" para **"Cliente"** → aparece o campo **"Origem do cliente"** → SALVAR (não cliquei).
2. Não há botão "converter em cliente"; a troca é só o campo Perfil.
3. O que muda: a ficha passa a mostrar "TIPO: CLIENTE" e o campo Origem; as abas da ficha são Cadastro · Documentos · Atendimentos · Processos · Despesas · Honorários · Timesheets · Notificações (TELA 09). Contrato/honorários ficam nas abas Honorários/Despesas e no Financeiro, não no cadastro.
4. Filtro de Contatos (TELA 08): Mostrar Todos / **Só clientes** / **Só contatos** / Só usuários.
5. **Ligação processo ↔ cliente:** no processo, campo **Clientes\*** (busca no cadastro de Contatos) + Qualificação; as demais partes em "Outros envolvidos". Na ficha do contato, a aba "Processos" lista os processos ligados.

## 7. Entrada de dados em lote / integrações

- Administração → **Integrações** (`#/main/admin/third-party-integrations`, TELA 03): só existe **"Envio de informações via WhatsApp"** (Desabilitada, botão VER DETALHES). Em "Meu plano" o WhatsApp integrado é um "turbo" pago.
- Financeiro: emissão de boletos via **Asaas** (TELA 33).
- **API pública, webhooks, aplicativos:** não encontrei nada nas telas. Não há link para documentação de API.
- Entrada em lote existente: **Buscas em lote pela OAB** (traz processos do tribunal pelo número da OAB) e captura automática de publicações (DJEN) e intimações (login nos tribunais).

## 8. Saída de dados

- **Administração → Escritório → Manutenção de conta → "EXPORTAR OS DADOS DO ASTREA"** (TELA 06): gera um **arquivo único** com Área de trabalho, Agenda, Contatos, Financeiro, Processos e casos "no Excel ou Google Planilhas"; o link chega **por e-mail** ("clique aqui").
- Contatos → ⋮ → Exportar contatos · Extrair emails · Ficha resumida · Ficha completa (TELA 07).
- Processos e casos: ícones Imprimir e Excel no topo da lista.
- Publicações: Imprimir e "Exportar Publicações".
- Financeiro: Imprimir e Excel.
- Processo: ⋮ → Imprimir relatório.
- Indicadores (TELA 34): Visão geral · Gestão estratégica · Indicadores pessoais (só tela, sem exportação vista).

---

## Mapa técnico para quem vai construir a integração

| O quê | URL (após `https://astrea.net.br/`) | Ordem de cliques / observações |
|---|---|---|
| Início | `#/main/workspace/[,]` | — |
| Lista de contatos | `#/main/contacts` | caixa de busca guarda o último termo; ⋮ = exportar |
| Ficha do contato | `#/main/contacts/detail/{id}/data` | id numérico longo |
| Novo contato | `#/main/contacts/add-edit-merge/[,,false,[],]/personal` (abas `/additional`, `/documentation`) | ADICIONAR → Pessoa juridica → Perfil → Origem do cliente (se Cliente) |
| Editar contato | `#/main/contacts/add-edit-merge/[{id},,,[],]/personal` | lápis na ficha |
| Lista de processos | `#/main/folders/[,,]` | filtro ATIVOS; ícones Imprimir/Excel |
| Ficha do processo | `#/main/folders/detail/{id}` | abas Resumo · Atividades · Histórico |
| Editar processo | `#/main/folders/lawsuit/add-edit/[{id},,,true]` | ⋮ → Editar |
| Publicações | `#/main/clippings` | + / ✔ / ⋮ por linha |
| Captura de publicações | `#/main/admin/clippings/` | aba Intimações eletrônicas na mesma rota |
| Busca de processos | `#/main/pending-search/search-results` · `…-oab` · `…-lawsuitlink` | ícone nuvem |
| Atendimentos | `#/main/consulting/list/` · novo: `#/main/consulting/add` | — |
| Integrações | `#/main/admin/third-party-integrations` | só WhatsApp |
| Exportar tudo | `#/main/admin/office` | rolar até "Manutenção de conta" |
| Meu plano | `#/main/plan-module/my-plan` | limites: 1000 processos, 10 usuários, 5 nomes de publicação |

- Formatos de arquivo aceitos para entrada: **nenhum** (não há upload de planilha). Saída: Excel / Google Planilhas.
- Onde a sessão pede login de novo: não aconteceu durante a visita (~10 min). As **intimações eletrônicas** dependem do login do advogado em cada tribunal e estavam falhando.

## Dificuldades

- A sessão já estava aberta, por isso a Parte A não foi feita.
- A busca de contatos guardava um termo de uma visita anterior ("side"), o que filtrou a lista sem aviso.
- Um clique caiu num rádio do "Filtro Avançado" (Só clientes) porque o painel não fechou; desfeito com "Todos" e "Cancelar", sem aplicar.
- O "Cancelar" do formulário de contato novo nem sempre saiu da tela; saí navegando para outro módulo (nada foi salvo).
- Algumas telas (Workflows, Intimações) carregam devagar e o print saiu com "Carregando..." na primeira tentativa.
- Rótulos de ícones só aparecem ao passar o mouse; foram lidos pelo título do elemento.

## Sugestão em 5 linhas

1. Entregar cada empresa nova como **contato Pessoa jurídica**, Perfil "Contato", com **Etiqueta "JUDICIAL"** (o campo Origem só aparece para Cliente).
2. Preencher Empresa, Nome fantasia, CNPJ, telefones (com tipo WhatsApp), e-mails, sites e, em **Comentários**, o número CNJ da ação nova, o tribunal e as redes sociais (não há campo próprio).
3. Como não há importação nem API, a entrada será **digitada** (pessoa ou robô de navegador seguindo o mapa acima) ou via o serviço pago de **Migração de dados** da Aurum; o JUDICIAL pode gerar uma planilha pronta para isso.
4. Quando virar cliente, a pessoa troca o Perfil para "Cliente", preenche **Origem do cliente = "JUDICIAL"** e cadastra o processo pela **busca automática por número CNJ** (o Astrea passa a trazer os andamentos).
5. Fica com a pessoa: decidir se a empresa vira cliente, fazer o contato comercial (Atendimento / workflow "Gestão de clientes") e conferir duplicados pelo aviso de CNPJ ou por "Unificar contatos".

## Lista das telas registradas

| TELA | Nome curto | O que mostra |
|---|---|---|
| 01 | area-de-trabalho-menu | Menu principal e barra superior |
| 02 | administracao-acesso | Abas da Administração; usuários |
| 03 | administracao-integracoes | Única integração: WhatsApp (desabilitada) |
| 04 | administracao-publicacoes-captura | Nomes pesquisados nos diários |
| 05 | administracao-intimacoes-eletronicas | Logins em tribunais com erro (CPF tarjado) |
| 06 | administracao-escritorio-exportar-dados | "Exportar os dados do Astrea" |
| 07 | contatos-lista-menu-exportar | Lista de contatos e menu ⋮ (exportar/fichas) |
| 08 | contatos-filtro-avancado | Só clientes / Só contatos / Só usuários |
| 09 | contato-exemplo-cadastro-tipo-cliente | Ficha de contato "TIPO: CLIENTE", abas e campo ORIGEM |
| 10 | contato-formulario-editar-PF | Formulário de edição (não salvo) |
| 11 | contato-PJ-novo-informacoes-pessoais | Formulário PJ: Empresa*, Perfil, telefones |
| 12 | contato-PJ-informacoes-complementares | Contato, Cargo, Código, Comentários, conta |
| 13 | contato-PJ-documentacao-CNPJ | CNPJ, IE, IM, Simples |
| 14 | contato-PJ-perfil-cliente-origem | Campo "Origem do cliente" com Perfil = Cliente |
| 15 | menu-adicionar-mais | Opções do botão + |
| 16 | processo-exemplo-PJ-resumo | Ficha de processo PJ × PJ |
| 17 | processo-menu-opcoes | Menu ⋮ do processo |
| 18a/b/c | processo-editar-campos | Todos os campos do processo (não salvo) |
| 19 | publicacoes-painel | Contadores e aviso de instabilidade |
| 20 | publicacoes-lista-colunas-diario | Colunas e fonte (DIÁRIO) |
| 21 | publicacao-virar-prazo-tarefa | Menu + da publicação |
| 22 | publicacao-mais-acoes | Abrir em nova aba / Descartar |
| 23 | atendimentos-lista | Atendimento "Oportunidades Comerciais" |
| 24 | atendimento-novo-formulario | Campos do atendimento (não salvo) |
| 25 | gestao-kanban | Quadro kanban de tarefas |
| 26 | workflows-lista | Workflows do escritório |
| 27 | workflow-gestao-de-clientes | Passos do workflow de clientes |
| 28 | resultado-buscas-processos-individuais | Busca por número CNJ |
| 29 | buscas-em-lote-pela-OAB | Busca em lote pela OAB |
| 30 | vinculos-processos-creditos | Processos vinculados e créditos |
| 31 | meu-plano-consumo | Limites do plano; "Migrações de dados" (cartão tarjado) |
| 32 | menu-usuario | Meu perfil / Meu plano / Sair |
| 33 | financeiro-lancamentos | Financeiro, Asaas, imprimir/Excel |
| 34 | indicadores | Painel de indicadores |
