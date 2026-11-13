# RELATÓRIO FINAL · Prompt 1A · PJe do TRT2

Execução: 13/11/2026, das 14h09 às 14h20 (horário de Brasília), aba única no Chrome do Leandro, ~45 ações.
Processo de referência (escolhido no Acervo Geral, primeiro da lista): **ATOrd 1001386-53.2016.5.02.0019**, 19ª Vara do Trabalho de São Paulo.
Todos os prints estão neste pacote com o nome `PJe-TRT2_TELA_NN_...`. Por decisão do Marcelo, os prints estão **sem tarja** (aparecem nomes de pessoas físicas); o texto deste relatório segue as regras do prompt (sem nomes de pessoas físicas, magistrados como "magistrado N").

**Diferenças em relação ao prompt (leia antes):**

1. O Leandro já estava logado quando comecei. Fiz a **Parte B primeiro** e a Parte A depois, para não arriscar a sessão. Não houve PAUSA PARA LOGIN.
2. **Baixei os autos completos sem querer.** O botão "Baixar processo completo" (menu do processo) não tem tela de opções nem confirmação: ao clicar, o download começa na hora (ver TELA 07 e TELA 08). O arquivo foi para a pasta Downloads do Chrome do Leandro. Como o limite era 1 arquivo, **não baixei a petição inicial**; li a inicial no visualizador.
3. A sessão caiu no fim da Parte A, depois de abrir a tela de login `/primeirograu/login.seam` (ver BLOQUEIO, TELA 20). Toda a Parte B já estava concluída.

---

## Jornada pública (Parte A)

| Passo | Tela | Ação | Resultado |
|---|---|---|---|
| A1 | `https://www.trt2.jus.br` → redireciona para `https://ww2.trt2.jus.br/` · título "Início" (TELA 15) | Menus: Institucional, Serviços, Notícias, Jurisprudência, Transparência, Legislação, Ouvidoria, Contato. Na própria home há "Consulta Processual" (campos Número, Dígito, Ano, 5, 02, Vara) com botões "Consulta Cidadão" e "Consulta Completa" | — |
| A2 | Home, coluna da direita | Clique no atalho **"PJe"** (mesma aba) | `https://ww2.trt2.jus.br/servicos/acesso-online/processo-judicial-eletronico-pje/page` · "PROCESSO JUDICIAL ELETRÔNICO" (TELA 16). Breadcrumb: Início / Serviços / Acesso Online / Processo Judicial Eletrônico - PJe |
| A2 | Mesma página | Expandir **"Acesso ao PJe (TRT2)"** | Duas colunas (TELA 17): **PJe 1º Grau** → "Acesso ao PJe de 1º grau" (`https://pje.trt2.jus.br/primeirograu/login.seam`, abre **nova aba**) e "Validação de documentos (chave de acesso)" (`/pjekz/validacao`); **PJe 2º Grau** → "Acesso ao PJe de 2º grau" (`/segundograu/login.seam`, nova aba). Observação na página: acesso exclusivo via **PDPJ, usando o PJeOffice**; Service Desk (11) 2898-3443 |
| A3 | `https://pje.trt2.jus.br/primeirograu/login.seam` · "Bem-vindo ao PJe · Processo Judicial Eletrônico" (TELA 18) | Só leitura | Formas de login visíveis: botão **"Entrar com PDPJ"** e link **"Esqueci minha senha"**. Versão 2.22.0.1. No HTML existe um botão oculto "Clique para habilitar o login" (login antigo por certificado/Shodo), não visível na tela. Menu lateral com: Certidões, Consulta Processual, Fale conosco, Gerar boleto de depósito judicial, Gerenciamento de Precatórios, Indisponibilidade do Sistema, Manuais, Otimizador do PDF, PJe-Calc Cidadão, PJe-Calc Tribunal, Pré-requisitos, Verificação de autenticidade de documento |
| A4 | Consulta pública sem login | — | Sim: `https://pje.trt2.jus.br/consultaprocessual` (TELA 19), campo "Número do processo"; outros serviços: Consulta Cidadão (`/consultaprocessual/consulta-cidadao`), Consulta de pautas, Sessão de Julgamento, Acesso restrito, PJe 1º Grau, PJe 2º Grau. Também acessível pelos botões da home do tribunal e pelo menu da tela de login. Não usei |
| A5 | — | PAUSA PARA LOGIN não foi necessária (já logado) | — |

## Sistema

PJe (interface "pjekz"), versão **2.22.0.1 - IPÊ** (rodapé), TRT da 2ª Região, **1º grau**, **painel do advogado** (perfil "Advogado").

## Mapa do fluxo (Parte B)

1. **Painel** `https://pje.trt2.jus.br/pjekz/painel/usuario-externo` · "Meu Painel - PJE" (TELA 01) → cartões **Acervo Geral (68)**, **Meus Expedientes (7)**, **Arquivados (140)**; campo de busca "Entre com o número do processo para consulta" (id `inputNumeroProcesso`). Menu lateral (ícones): Meu Painel, Consulta Processos de Terceiros, Minha Pauta, Novo Processo, Solicitação de Habilitação, Apresentação de Renúncia, Perícias.
2. **Acervo Geral** → `/pjekz/painel/usuario-externo/acervo-geral` (TELA 02). Abas por foro (Barueri, Cotia, Diadema, Franco da Rocha, »), filtros "Classe Judicial", "Fase processual", "CPF, CNPJ ou Nome da parte", "Juízo 100% Digital". Colunas: Processo | Órgão Julgador | Data da Audiência | Data da Autuação. Paginação: "Linhas por página: 10 · 1 - 10 de 68".
3. **Consulta por número**: digitar `1001386-53.2016.5.02.0019` no campo de busca + Enter → vira filtro (chip) e a URL passa a `/acervo-geral/1001386-53.2016.5.02.0019` (TELA 03). Formato aceito: número CNJ com traço e pontos (0000000-00.0000.0.00.0000), sem a classe.
4. **Abrir o processo**: clique no número (aria-label "Detalhes do Processo ATOrd ...") → abre em **nova aba/janela** (`window.open`) o endereço `https://pje.trt2.jus.br/pjekz/processo/1110293/detalhe`. **1110293 é o identificador interno** (não é o número CNJ). Abri esse endereço na mesma aba (TELA 04).
5. **Tela do processo**: cabeçalho com classe+número, vara / cargo do juízo ("19ª Vara do Trabalho de São Paulo / Juiz do Trabalho Titular"), partes resumidas; faixa com Valor da causa, Distribuído, Autuado. À esquerda, linha do tempo; à direita, visualizador do documento.
6. **Dados completos**: clicar no número no cabeçalho → janela "Dados do processo" com Polo Ativo / Polo Passivo (TELA 05).
7. **Menu do processo** (ícone ☰ à direita, TELA 06): Acesso de terceiros, Audiências e Sessões, Baixar processo completo, Baixar processo por instância, Cálculos do processo, Expedientes, Obrigação de Pagar, Perícias, Peticionar, Quadro de Recursos, Apresentação de Renúncia.
8. **Documentos**: linha do tempo, ordem padrão do mais novo para o mais antigo; ícone "Ordenação ascendente" inverte (TELA 09). Primeiro documento: **Petição Inicial f000442** (11/07/2016, 12 anexos); segundo: **Notificação 5a107b9** (12/07/2016).
9. **Notificação da ré** (TELA 10) → ícone de envelope "Visualizar Expedientes" (TELA 11).
10. **Assinaturas**: sentença e04cb21 em PDF, assinatura no rodapé (TELA 12, TELA 13).
11. **Intimações**: Painel → "Meus Expedientes" (TELA 14).

## Tabela de campos

| Campo | Rótulo na tela | Aba ou seção | Exemplo |
|---|---|---|---|
| Classe | sigla antes do número ("ATOrd") | Cabeçalho do processo; "Número do Processo" em Dados do processo | ATOrd (Ação Trabalhista - Rito Ordinário, conforme a notificação) |
| Número | Número do Processo | Dados do processo | 1001386-53.2016.5.02.0019 |
| Órgão julgador | Órgão julgador | Dados do processo / cabeçalho | 19ª Vara do Trabalho de São Paulo |
| Distribuição | Distribuído: | Faixa do cabeçalho / Dados do processo | 11/07/2016 17:42 |
| Autuação | Autuado: | idem | 11/07/2016 17:42 |
| Valor da causa | Valor da causa: | idem | R$ 105.000,00 |
| Prioridade | Prioridade(s): | Dados do processo | Idoso |
| Justiça gratuita | Pedido de Assistência Judiciária Gratuita | Dados do processo | não concedida em 22/08/16 |
| Assuntos | Assunto(s): | Dados do processo | Acidente de Trabalho; Aviso Prévio; Correção Monetária; Indenização/Dobra/Terço Constitucional; PLR; Saldo de Salário |
| Polo ativo | Polo Ativo · Reclamante: | Dados do processo | pessoa física (+ advogado: pessoa física) |
| Polo passivo | Polo Passivo · Reclamado: | Dados do processo | 5 reclamados: 1 empresa (INDEBRAS INDUSTRIA ELETROMECANICA BRASILEIRA LTDA (Massa Falida de), CNPJ 61.574.299/0001-82) + 4 pessoas físicas |
| Endereço/e-mail da parte | linha após CNPJ; "(email: ...)" | Dados do processo, Polo Passivo | ver Contatos da ré |
| Advogados | nome (ADVOGADO), CPF, OAB, E-mail | abaixo de cada parte | pessoa física |
| Grau | — | não aparece rótulo; 1º grau pela URL de acesso e pela aba "1º grau" dos expedientes | 1º grau |
| Fase | — | não encontrei rótulo de fase na tela do processo; o Acervo tem filtro "Fase processual" | não encontrei |
| Situação / última movimentação | — | topo da linha do tempo (ordem padrão) | 01/09/2023 Manifestação ff23143 |

## Downloads

| O quê | Como | Formato | Tamanho / tempo | Onde ficou |
|---|---|---|---|---|
| **Autos completos** (sem querer) | Menu do processo → **"Baixar processo completo"** (aria-label "Download do processo completo"). É **botão sem endereço**; não abre nova aba, não pede confirmação nem opções | o arquivo é entregue ao navegador como `data:`/blob; formato não aparece na tela | ~10 s entre "Download iniciado. Por favor, aguarde." (TELA 07) e "Download realizado com sucesso. Verifique sua pasta de downloads." (TELA 08); tamanho não aparece | Pasta Downloads do Chrome do Leandro |
| Petição inicial | **Não baixada** (limite de 1 arquivo). O download individual é o ícone de seta no cabeçalho do documento (ao lado do cadeado), não clicado | — | — | — |
| Outras opções vistas | "Baixar processo por instância" (menu) e "Baixar documentos filtrados." (barra da linha do tempo) — botões sem endereço, não clicados | — | — | — |

## Contatos da ré nos autos

| Documento | Dado | Aparece? | Página e trecho | Expressão antes | Texto ou imagem | Valor (só empresa) |
|---|---|---|---|---|---|---|
| Petição inicial f000442 | endereço | sim | documento HTML (sem paginação), 1º parágrafo após a qualificação do reclamante | "em face de ... devidamente inscrita no C.N.P.J. sob o nº ... requerendo seja esta notificada na" | texto selecionável (HTML) | Rua Manoel Monteiro de Araújo nº 961, Vila Jaguará, São Paulo, SP, CEP 05113-020 |
| Petição inicial f000442 | e-mail | não | — | — | texto | nao_consta |
| Petição inicial f000442 | telefone | não (o único "fone" é do escritório do advogado do reclamante, no fim da peça) | — | — | texto | nao_consta |
| Notificação 5a107b9 | endereço | sim | topo, campo "DESTINATÁRIO:" | "DESTINATÁRIO:" | PDF com texto | Avenida Manoel Monteiro de Araujo, 961, Parque São Domingos, São Paulo - SP, CEP 05113-020 |
| Expedientes da notificação | meio de expedição | sim | tabela "Expediente(s) do(a) Notificação" (TELA 11) | "Meio de Expedição" | tela | **Correios**, criado 12/07/2016, ciência 14/07/2016, "Confirmado por: Sistema", prazo 5 dias até 19/07/2016; código de rastreio postal JJ525842473BR na notificação |
| Cadastro da parte (Dados do processo) | endereço | sim | Polo Passivo, linha após o CNPJ (TELA 05) | "CNPJ: ..." | tela | Rua São Paulo, 37, N/P Adm Jud Cabezon Adm Judicial Eireli, Centro, São Roque - SP, CEP 18130-120 (endereço da administradora judicial da massa falida) |
| Cadastro da parte | e-mail | sim | mesma linha, entre parênteses | "(email:" | tela | contabilidade@indebras.com.br |
| Cadastro da parte | telefone | não | — | — | — | nao_consta |

Aviso de recebimento: não encontrei AR digitalizado da notificação inicial; a ciência consta como confirmada pelo "Sistema". Há 11 certidões "Devolução de mandado" mais adiante no processo (fase de execução), não abertas.

## Extração repetível

- **Valor da causa, distribuição, órgão julgador, assuntos**: **sim** — sempre no mesmo lugar (faixa do cabeçalho e "Dados do processo"), rótulos fixos.
- **CNPJ, endereço e e-mail da ré pelo cadastro**: **sim** — mesmo bloco "Polo Passivo", padrão "CNPJ: ... / endereço / (email: ...)"; depende de alguém ter cadastrado o e-mail.
- **Endereço da ré na inicial**: **parcial** — texto selecionável aqui (HTML), mas a frase muda de advogado para advogado ("requerendo seja esta notificada na" neste caso); petições em PDF escaneado não terão texto.
- **E-mail e telefone na inicial**: **não** — não constavam neste processo.
- **Meio de citação**: **sim** — tabela de expedientes tem colunas fixas.
- Tudo isso só apareceu **com o advogado logado**; a consulta pública não foi testada.

## Intimações

Painel → cartão **"Meus Expedientes" (7)** → `/pjekz/painel/usuario-externo/pendentes-manifestacao` (TELA 14). Abas por foro (Guarulhos; São Paulo - Zonas Central, Norte e Oeste). Filtros: Classe Judicial, Fase processual, Juízo 100% Digital; "Filtrar resultados por: Prazo (Sem prazo, No prazo) · Ciência (Automática, Manual, Sem ciência)". Colunas: Processo | Órgão Julgador | Data de Criação | Data da Audiência | Data de Ciência | Prazo Final. Ações por linha: "Visualizar Expediente", "Detalhar Expediente", "Abrir o Peticionar", "Responder o Peticionar". Não cliquei em nenhuma (abrir o expediente pode registrar ciência). Dentro do processo, cada intimação tem o ícone de envelope "Visualizar Expedientes".

## Quem decide

| Documento | Data | Magistrado | Cargo | Onde aparece a assinatura |
|---|---|---|---|---|
| Despacho 91945df | 2016-08-18 | magistrado 1 | Juiz do Trabalho Substituto | linha "Assinado eletronicamente por" no documento HTML |
| Sentença 3b46759 | 2016-08-22 | magistrado 1 | Juiz do Trabalho Substituto | idem |
| Despacho efbce62 | 2018-01-18 | magistrado 2 | Juiz(a) do Trabalho Titular | idem |
| Despacho 01cfe8f | 2018-08-24 | magistrado 2 | Juiz(a) do Trabalho Titular | idem |
| Despacho 46b3442 | 2018-09-21 | magistrado 2 | Juiz(a) do Trabalho Titular | idem |
| Despacho c36af70 | 2018-11-22 | magistrado 2 | Juiz(a) do Trabalho Titular | idem |
| Despacho 562f455 | 2018-11-30 | magistrado 2 | Juiz(a) do Trabalho Titular | idem |
| Despacho d43c275 | 2019-02-05 | magistrado 1 | Juiz(a) do Trabalho Substituto | idem |
| Despacho a0c95a5 | 2019-02-14 | magistrado 1 | Juiz(a) do Trabalho Substituto | idem |
| Decisão 1eb9331 | 2019-06-24 | magistrado 2 | Juiz do Trabalho | rodapé (fim do documento) |
| Despacho 43cae24 | 2019-12-17 | magistrado 2 | Juiz(a) do Trabalho Titular | linha "Assinado eletronicamente por" |
| Despacho ba97965 | 2020-02-05 | magistrado 3 | Juiz(a) do Trabalho Substituto | idem |
| Decisão 96b2f5d (PDF) | 2020-03-06 | magistrado 2 | não li | cabeçalho "Juntado por"; rodapé do PDF não lido |
| Despacho 377dd30 (PDF) | 2020-12-11 | magistrado 2 | não li | idem |
| Sentença 19a89bf, prescrição intercorrente (PDF) | 2023-08-15 | magistrado 4 | não li | idem |
| Sentença e04cb21 (PDF) | 2023-08-23 | magistrado 4 | Juiz do Trabalho Titular | bloco de assinatura no fim + rodapé PJe com QR code: "Assinado eletronicamente por: ... - Juntado em: 23/08/2023 17:59:04" e link de validação `https://pje.trt2.jus.br/pjekz/validacao/<número do documento>?instancia=1` (TELA 12) |

**4 magistrados diferentes** assinaram. A capa indica o **cargo** do juízo ("19ª Vara do Trabalho de São Paulo / Juiz do Trabalho Titular"), sem nome.

## Mapa técnico para quem vai construir o robô

- **URLs**: painel `/pjekz/painel/usuario-externo`; acervo `/pjekz/painel/usuario-externo/acervo-geral[/<numero CNJ>]`; expedientes `/pjekz/painel/usuario-externo/pendentes-manifestacao`; processo `/pjekz/processo/<id interno>/detalhe` (o id interno, ex. 1110293, só se descobre pela lista do painel); validação de documento `/pjekz/validacao/<número do documento>?instancia=1`.
- **Ordem de cliques**: Painel → campo `inputNumeroProcesso` (número + Enter) → clique no número (abre nova janela) → ☰ Menu do processo / linha do tempo / clique no número do cabeçalho para os dados das partes.
- **Download**: botões sem link; o arquivo é gerado pelo navegador (data/blob). "Baixar processo completo" baixa direto, sem confirmação.
- **Linha do tempo**: rolagem contínua (não vi paginação), 172 links de documento contando anexos; ordenação ascendente/descendente; filtro por tipo e por data; pesquisa textual.
- **Documentos**: os mais antigos (2016–2019) abrem como HTML com texto; os mais novos abrem em PDF dentro de um iframe (texto não acessível pela página, só pela imagem/visualizador).
- **Sessão**: durou pelo menos ~11 minutos sem pedir login (já estava logada quando comecei). **Caiu** depois de abrir `/primeirograu/login.seam` na mesma aba.
- **Certificado/token**: login só por "Entrar com PDPJ" (PJeOffice/certificado). Precisa de pessoa.
- **Sem advogado logado**: consulta pública (`/consultaprocessual`). **Com advogado**: tudo da Parte B. **Com pessoa**: o login PDPJ.

## Barreiras

- Login exige pessoa (PDPJ + PJeOffice/certificado).
- **Sessão perdida ao visitar a tela de login** com o usuário já logado: o painel passou a mostrar "Acesso Negado — É preciso logar para acessar a página" e o aviso "Autenticação: Token de autenticação não informado. (SJT-004)" (TELA 20, TELA 20b). O robô nunca deve abrir `login.seam` com a sessão ativa.
- Abrir processo usa `window.open` (nova janela), o que complica extensões de navegador; dá para contornar indo direto em `/pjekz/processo/<id>/detalhe`.
- Documentos recentes em PDF dentro de iframe: o texto não sai pela página.
- "Baixar processo completo" sem confirmação: risco de downloads pesados acidentais.

## Dificuldades

- A ferramenta de leitura da página falhou no painel; usei leitura por script.
- O clique no processo não abriu aba visível (abre janela nova); precisei capturar o endereço.
- O download dos autos completos começou sem aviso (ver Diferenças).
- Fase processual não aparece com rótulo na tela do processo.

## Sugestão (5 linhas)

1. Pessoa faz o login PDPJ uma vez; o robô trabalha só em `/pjekz/...`, sem nunca abrir `login.seam`.
2. Para cada número CNJ: buscar no Acervo, pegar o id interno e ir direto em `/pjekz/processo/<id>/detalhe`.
3. Ler "Dados do processo" (valor, datas, vara, CNPJ, endereço e e-mail da ré) e a tabela de expedientes da notificação inicial.
4. Ler a petição inicial no visualizador (HTML) ou baixar só ela pelo ícone do documento quando for PDF; nunca usar "Baixar processo completo".
5. Fica com a pessoa: login, qualquer ciência de intimação e qualquer protocolo.

## Lista das telas registradas (todas com print neste pacote)

| TELA | Nome curto | O que mostra |
|---|---|---|
| 01 | painel-advogado | Meu Painel: Acervo Geral, Meus Expedientes, Arquivados, menu lateral |
| 02 | acervo-geral | Lista de processos com filtros e colunas |
| 03 | consulta-por-numero | Acervo filtrado pelo número do processo de referência |
| 04 | processo-detalhe-timeline | Tela do processo: cabeçalho, linha do tempo, visualizador |
| 05 | detalhes-processo-partes | Dados do processo, Polo Ativo e Polo Passivo |
| 06 | menu-do-processo | Menu ☰ com opções de download, expedientes etc. |
| 07 | baixar-processo-completo-download-iniciado | Aviso "Download iniciado" |
| 08 | download-concluido | Aviso "Download realizado com sucesso" |
| 09 | documentos-ordem-ascendente-peticao-inicial | Linha do tempo do mais antigo; petição inicial aberta |
| 10 | notificacao-inicial-re | Notificação à ré com destinatário e rastreio postal |
| 11 | expedientes-da-notificacao | Tabela de expediente: Correios, datas, prazo |
| 12 | sentenca-assinatura-rodape | Fim da sentença com bloco de assinatura e QR code |
| 13 | sentenca-pdf-visualizador | Início da sentença em PDF |
| 14 | meus-expedientes-intimacoes | Painel de intimações com filtros e colunas |
| 15 | A1-pagina-inicial-trt2 | Home do TRT2 |
| 16 | A2-pagina-processo-judicial-eletronico | Página "Processo Judicial Eletrônico" |
| 17 | A2-acesso-pje-1o-e-2o-grau | Links de acesso ao PJe 1º e 2º grau |
| 18 | A3-tela-login-pje-1o-grau | Tela de login: "Entrar com PDPJ" |
| 19 | A4-consulta-processual-publica | Consulta processual pública |
| 20 / 20b | bloqueio-sessao-perdida | "Acesso Negado" + erro SJT-004 |

---

RESPOSTA PARA O RADAR v1

| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|
| 1001386-53.2016.5.02.0019 | valor_causa | 105000,00 | encontrado | Dados do processo / cabeçalho (TELA 04, TELA 05); confere com o fim da petição inicial f000442 | 2026-11-13 | — |
| 1001386-53.2016.5.02.0019 | data_ajuizamento | 2016-07-11 | encontrado | "Distribuído: 11/07/2016 17:42" (TELA 05) | 2026-11-13 | autuação na mesma data |
| 1001386-53.2016.5.02.0019 | telefone | — | nao_consta | inicial f000442 e cadastro da parte | 2026-11-13 | o único telefone da inicial é do escritório do advogado do reclamante |
| 1001386-53.2016.5.02.0019 | email | contabilidade@indebras.com.br | encontrado | cadastro da parte, Polo Passivo (TELA 05) | 2026-11-13 | não consta na inicial |
| 1001386-53.2016.5.02.0019 | site | — | nao_consta | inicial f000442 e cadastro da parte | 2026-11-13 | — |
| 1001386-53.2016.5.02.0019 | endereco | Rua São Paulo, 37, N/P Adm Jud Cabezon Adm Judicial Eireli, Centro, São Roque - SP, CEP 18130-120 | encontrado | cadastro da parte, Polo Passivo (TELA 05) | 2026-11-13 | endereço atual da massa falida (administradora judicial) |
| 1001386-53.2016.5.02.0019 | endereco | Rua Manoel Monteiro de Araújo, 961, Vila Jaguará, São Paulo - SP, CEP 05113-020 | encontrado | petição inicial f000442, 1º parágrafo; notificação 5a107b9 (TELA 10) | 2026-11-13 | endereço de 2016; notificação via Correios com ciência em 14/07/2016 |
| 1001386-53.2016.5.02.0019 | socio_contato | — | nao_consta | petição inicial f000442 | 2026-11-13 | a inicial não traz sócio nem administrador da ré |
