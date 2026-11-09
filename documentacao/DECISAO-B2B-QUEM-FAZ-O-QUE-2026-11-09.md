# Decisão de arquitetura: quem faz o quê entre a conversa do LexSuiteONE e a do RootifyONE (B2B)

Data: 09/Nov/2026. Autora: sessão de Arquitetura do LexSuiteONE, a pedido do dono (Marcelo), depois que duas conversas
editaram o mesmo arquivo (`rootify-one/rootify-lex.js`) e publicaram o RootifyONE 0.18.16 e 0.18.17 quase juntas.
Escrito para ser lido pelas duas conversas, sem depender do contexto de nenhuma. Registro curto em
`lexsuiteone/docs/QUADRO.md` (Decisões do dono, 09/Nov). Vale a partir da próxima tarefa de cada conversa.

## Resumo para o dono

1. Cada arquivo tem um dono só. **Tudo que está dentro de `rootify-one/` é da conversa do RootifyONE**, inclusive a tela
   do RADAR (`rootify-lex.js`). **Tudo que está em `lexsuiteone/` (regras da licença, SQL `lex_*`, funções da nuvem
   `lex-conta` e `lex-equipe`, texto dos e-mails, termos) é da conversa do LexSuiteONE.**
2. O LexSuiteONE desenha e entrega "o que o banco devolve e o que a tela deve mostrar"; o RootifyONE implementa a tela e
   publica a versão. Nenhuma conversa publica versão do produto da outra.
3. A ponte entre as duas é o dono colando mensagens (as conversas não se falam). Para não depender de memória, cada
   pedido vai escrito num arquivo: `lexsuiteone/docs/QUADRO.md` (pedidos do LexSuiteONE) e
   `rootify-one/entrega/solverone-app/PEDIDOS-LEXSUITEONE.md` (pedidos do RootifyONE ao LexSuiteONE).
4. Termos e aceite, jornada do cliente, CRM e estatísticas são **genéricos para todo produto B2B**; o modelo do e-mail de
   boas-vindas é **por produto** (o texto fala da instalação daquele produto), mas com o mesmo molde e os mesmos campos.
5. O texto dos termos é genérico (suíte LexSuiteONE). O **nome do escritório não entra no texto**: a página de aceite o
   mostra na hora, lendo a licença pelo código, e o registro guarda o código da licença, que aponta para o cadastro.

## 1. Quem faz o quê

| Tema | Quem decide (desenho) | Quem implementa | Onde mora o código | Até onde vai / o que não pode |
|---|---|---|---|---|
| Moldura B2B no RootifyONE (menu, seletor de produto, 9 abas) | RootifyONE | RootifyONE | `rootify-one/rootify-b2b.js`, `rootify-catalogo.js` (`RF.cat.SUITES_B2B`) | LexSuiteONE não toca. Se precisar de aba ou campo novo, escreve pedido no QUADRO; não edita. |
| Telas do RADAR no RootifyONE (`rootify-lex.js`) | LexSuiteONE desenha **o que** mostrar (campos, botões, regras, que função chamar com que corpo); RootifyONE decide **como** (layout, componentes `ui.*`) | RootifyONE | `rootify-one/rootify-lex.js`, testes em `rootify-one/teste/` | **LexSuiteONE não edita mais este arquivo** (a 0.18.16 foi a última vez). RootifyONE não inventa regra de licença nem chama tabela `lex_*` direto: só funções `admin_lex_*` e `lex-equipe`. |
| Regras da licença (Ativar/Pausar, limites, aprovação de pessoa, teto de computadores, modalidade) | LexSuiteONE (Arquitetura), com "pode" do dono | LexSuiteONE (SQL e funções) | `lexsuiteone/nuvem/supabase/*.sql`, `lexsuiteone/documentacao/DESENHO-*.md` | RootifyONE só expõe o que a função devolve e manda o que ela aceita. Não cria regra na tela (ex.: não decide sozinho o que "parado" significa; pede). |
| SQL `admin_lex_*`, tabelas e views `lex_*` | LexSuiteONE | LexSuiteONE escreve o arquivo definitivo e aplica pelo conector | `lexsuiteone/nuvem/supabase/AAAA-MM-DD-*.sql` (arquivo datado, com "desfazer") | RootifyONE pode **propor** (rascunho, ver item 3), nunca aplica nem mantém a cópia oficial. Ninguém aplica sem o "pode aplicar" do dono. |
| SQL genérico da plataforma B2B (`sol_apps`, `sol_retorno_*`, `sol_aceites`, futuros `sol_clientes_*`) | LexSuiteONE (Arquitetura) desenha; RootifyONE opina sobre o que a tela precisa | LexSuiteONE escreve e aplica (hoje); quando a 2ª suíte B2B existir, passa para o RootifyONE | `lexsuiteone/nuvem/supabase/` hoje; o RootifyONE guarda um índice `rootify-one/entrega/solverone-app/supabase/INDICE-SOL.md` apontando para cada arquivo aplicado | Mesmo portão: "pode aplicar" do dono. Nome com prefixo `sol_`, nunca `lex_`. Agnóstico: nenhum campo específico do RADAR. |
| Funções da nuvem `lex-conta` (programa) e `lex-equipe` (equipe) | LexSuiteONE | LexSuiteONE publica pelo conector | `lexsuiteone/nuvem/supabase/functions/*/index.ts` | O **contrato** (ações, corpo, resposta, erros) fica no cabeçalho do `index.ts` e no DESENHO. RootifyONE só chama `lex-equipe` com login de admin. Mudança de contrato sem aviso = proibida: o LexSuiteONE escreve o pedido no QUADRO antes de publicar. |
| Modelo do e-mail de boas-vindas (texto e HTML, por produto) | LexSuiteONE (Produto escreve; Arquitetura confere o que entra de nuvem e termos) | LexSuiteONE; publicado no site do produto | `lexsuiteone/docs/email/email-boas-vindas.html` e `.txt`, lido em `judicial.solverone.com.br/email/…` | Campos são contrato: `{{nome}} {{codigo}} {{contato}} {{drive}} {{email}} {{marca.nome}} {{marca.curto}} {{marca.logo_email}}` e os marcadores `CODIGO-INICIO/FIM`. **Campo novo só com pedido ao RootifyONE** antes de ir ao modelo. Envio ao cliente só com o clique do dono. |
| Janela "Preparar e enviar e-mail" (prévia, confirmação, envio) | RootifyONE (tela); LexSuiteONE (função de envio e campos) | RootifyONE | `rootify-one/rootify-lex.js` hoje; a parte comum vai para `rootify-b2b.js` | A janela preenche todos os campos do contrato acima. Envio sempre pela `lex-equipe` (`acao: boas_vindas`), nunca pelo Resend direto. |
| Jornada do cliente (etapas e de onde vem cada dado) | LexSuiteONE define as etapas e **o campo da função que prova cada etapa**; RootifyONE define a exibição genérica | RootifyONE (motor genérico) + LexSuiteONE (campos em `admin_lex_listar`) | Motor em `rootify-b2b.js`; mapa por produto em `rootify-lex.js`; dados em `admin_lex_listar` | Etapas oficiais (seção 4). RootifyONE não deduz etapa de tabela: usa os campos devolvidos. |
| Aba Clientes / CRM empresarial (contatos, contratos, conversas) | LexSuiteONE (Arquitetura) desenha o modelo de dados genérico; RootifyONE desenha a tela | SQL: LexSuiteONE; tela: RootifyONE | SQL `sol_clientes*` em `lexsuiteone/nuvem/supabase/`; tela em `rootify-b2b.js` | Depois do onboarding da KR Law (não agora). Nada de dado pessoal além de nome, e-mail e telefone profissionais do contato. |
| Termos e condições (texto, versão, aceite, registro) | LexSuiteONE (Arquitetura), texto revisado pelo Leandro/advogado, "pode" do dono | LexSuiteONE: página, SQL, e-mail. RootifyONE: selo e etapa na tela | Texto e página: `lexsuiteone/paginas/aceite.html` → `docs/aceite.html`; registro: `sol_aceites` | Texto só muda com nova versão. RootifyONE não edita texto nem versão. Detalhe na seção 5. |
| Estatísticas agnósticas (totais por situação, vistos) | LexSuiteONE (dimensões declaradas em `sol_apps.retorno_dimensoes`) | RootifyONE desenha gráfico e tabela genéricos a partir de `admin_sol_retorno` | `rootify-b2b.js` | RootifyONE não escreve nome de situação na mão: usa as dimensões e chaves que vêm do banco. |
| Planos e cobrança B2B | LexSuiteONE (Arquitetura) desenha com o dono (preço, prazo, modalidade) | SQL: LexSuiteONE; tela: RootifyONE | Futuro `sol_planos_b2b`; aba "Planos e cobrança" | Depois do primeiro cliente pagar. Hoje a aba fica como está (vazia ou só leitura). |

## 2. Arquivo compartilhado (`rootify-one/rootify-lex.js`)

Concordo com a proposta: **a conversa do LexSuiteONE não edita mais `rootify-lex.js`** nem nenhum arquivo de
`rootify-one/`. Ela entrega (a) o desenho da tela, por escrito, no QUADRO ou num `documentacao/DESENHO-*.md`, e (b) o
SQL e as funções da nuvem já aplicados, com o contrato. O RootifyONE implementa, testa (`teste/licencas.js`) e publica.
Uma exceção só: se o RootifyONE pedir por escrito ("pode mexer no bloco X"), e o dono concordar, o LexSuiteONE abre um
PR e **não faz o merge**; o RootifyONE revisa e junta. O que muda em relação a hoje: o `teste/licencas.js` também passa
a ser só do RootifyONE.

## 3. SQL de uma função `admin_lex_*` que o RootifyONE precisa mudar

1. **RootifyONE escreve o pedido**, não o SQL definitivo: o que a tela precisa (campo novo, filtro, comportamento) e por
   quê. Pode anexar um rascunho de SQL, marcado `RASCUNHO`, em `rootify-one/entrega/solverone-app/supabase/`. O pedido
   vai para `rootify-one/entrega/solverone-app/PEDIDOS-LEXSUITEONE.md`, numerado, e o dono cola na conversa do LexSuiteONE.
2. **LexSuiteONE escreve o arquivo definitivo** em `lexsuiteone/nuvem/supabase/AAAA-MM-DD-*.sql` (partindo da versão
   atual da função, que mora lá; o rascunho do RootifyONE serve de guia), passa no verificador de GRANTs, pede
   "pode aplicar" ao dono e aplica pelo conector.
3. **Aviso de volta**: o LexSuiteONE escreve no QUADRO "aplicado em …; a função X agora devolve/aceita …" e o dono cola na
   conversa do RootifyONE. O RootifyONE marca o pedido como atendido e apaga o rascunho (ou o renomeia para
   `APLICADO-ver-lexsuiteone-…`).
4. Enquanto não vier o "aplicado", a tela do RootifyONE **tolera a falta do campo** (como já faz com `email_responsavel`).
5. Caso desta vez: o rascunho `rootify-one/entrega/solverone-app/supabase/2026-11-09-lex-listar-responsavel.sql`
   (`admin_lex_listar` devolvendo `email_responsavel` e `boas_vindas`) **vira pedido nº 1**. O LexSuiteONE o incorpora à
   versão atual de `admin_lex_listar` (que já devolve `dominios_pessoas`, `modalidade`, `em_uso`), junto com o campo
   `aceite` da seção 5, num arquivo só, e aplica com o "pode" do dono.

## 4. Genérico × por produto

| Item | Nível | Onde fica no RootifyONE | Observação |
|---|---|---|---|
| Boas-vindas (modelo) | **Por produto** (o texto ensina a instalar aquele produto) com **molde e campos genéricos** | Aba **E-mails** do produto: lista os modelos do produto (boas-vindas, aviso de pessoa nova…), cada um com "Preparar e enviar" e histórico. A suíte não tem aba E-mails própria. | O modelo mora no site do produto; a janela de envio é genérica em `rootify-b2b.js` e recebe a URL do modelo de `SUITES_B2B`. |
| Termos e aceite | **Suíte LexSuiteONE** (um texto para todos os produtos da suíte; cada produto tem um anexo curto com "o que este produto coleta"). Registro genérico para todo B2B (`sol_aceites`). | Aba **Configuração** do produto: bloco "Termos" (versão vigente, data, link da página, quantos aceites). Ficha da licença: **selo** "Termos aceitos por … em … (v1.0)" ou "Sem aceite". Jornada: etapa própria. | Não entra no módulo Termos dos apps B2C (seção 5). |
| Jornada do cliente | **Todo B2B** (motor e nomes das etapas) com mapa de dados por produto | Aba **Clientes** do produto; na **Visão geral** da suíte, soma por etapa de todos os produtos. | Etapas oficiais: 1 Licença criada → 2 Boas-vindas enviado (ou falhou) → 3 Termos aceitos → 4 Instalado → 5 Em uso / Parado (>14 dias). Prova de cada etapa: `admin_lex_listar` devolve `boas_vindas` (último envio), `aceite` (último aceite), `em_uso` (computadores) e `ultimo_uso`. |
| CRM de clientes (contatos, contratos, conversas) | **Todo B2B** (um escritório pode ter mais de um produto) | Aba **Clientes**, abrindo a ficha do escritório; a licença aponta para o cliente. | Depois da KR Law instalada. Modelo de dados pela Arquitetura antes da tela. |
| Estatísticas | **Todo B2B** (dimensões vêm de `sol_apps.retorno_dimensoes`) | Aba **Estatísticas** do produto; total da suíte na Visão geral. | Já existe `admin_sol_retorno`; a tela só não pode fixar nomes de situação. |
| Planos e cobrança | Todo B2B | Aba própria | Futuro. |

## 5. Termos e condições: desenho

- **Texto**: genérico da suíte LexSuiteONE, em três partes num só documento: Termos de uso (com cláusula de **uso exclusivo
  do escritório licenciado**, vedado repassar ou vender as informações), Política de privacidade da nuvem da SolverONE e
  Termo de tratamento de dados (controlador = escritório, operadora = SolverONE, LGPD art. 39). Sem nome do escritório
  no texto. Anexo por produto: o que ele coleta (para o RADAR: licença, pessoas, erros técnicos, totais por situação).
- **Nome do escritório**: a página lê a licença pelo código (função pública `sol_aceite_contexto`, só devolve o nome e se
  já há aceite, com limite de chamadas) e mostra "Este aceite é dado em nome de KR Law… (código LEX-…)". O registro guarda
  o **código da licença**, que aponta para o cadastro; não copia o nome do escritório (se o cadastro corrigir o nome, o
  aceite continua apontando certo). Quem aceita declara ter poderes para representar o escritório.
- **Versão**: `1.0 · 09/Nov/2026`. Toda mudança de texto vira versão nova; o registro guarda a versão e o **hash SHA-256
  do texto exatamente mostrado**, prova do que foi lido. Versão nova não apaga aceite antigo; o RootifyONE mostra "aceite
  da versão 1.0; vigente 1.1" e o dono decide se pede novo aceite.
- **Onde se aceita**: link no e-mail de boas-vindas, antes dos passos de instalação, para
  `judicial.solverone.com.br/aceite.html?codigo=…&email=…` (página do site do produto, sem login, sem pedido externo além
  do banco da SolverONE). A página exige rolar o texto até o fim, nome completo (nome e sobrenome), e-mail, código de
  cliente, caixa "li e aceito", e devolve um **protocolo** (`ACE-000001-ABCDEF`). Também vale pelo site, sem e-mail.
  No programa, numa versão seguinte, a `lex-conta` devolve `aceite: {aceito, versao}` e o RADAR só lembra (não bloqueia)
  na 0.7; bloquear instalação nova sem aceite é decisão para a 0.8.
- **O que se grava** (tabela genérica `sol_aceites`, imutável por trigger, sem acesso direto de anon/authenticated):
  app, licença (código), termo (`lexsuiteone-termos`), versão, hash, nome completo, e-mail, data e hora, início do IP
  (`200.150.10.x`), navegador (120 caracteres), origem (e-mail, site ou programa). Função `sol_aceite_registrar` (anon,
  de propósito: 5 por hora por e-mail, 30 por dia por licença, valida licença e campos). Leitura pela equipe:
  `admin_sol_aceites(app, licenca)`; para o programa: `sol_tem_aceite` (service_role). Arquivo:
  `lexsuiteone/nuvem/supabase/2026-11-09b-sol-aceites.sql` (pronto, **não aplicado**; aguarda "pode").
- **Como o RootifyONE mostra**: etapa 3 da jornada; selo na ficha da licença (nome, data, versão, protocolo); bloco
  "Termos" na aba Configuração; e a prévia do e-mail precisa preencher `{{email}}` (e-mail do responsável) no link.
  Tudo isso vem de `admin_lex_listar.aceite` e `admin_sol_aceites`; nenhuma consulta direta à tabela.
- **Módulo Termos dos apps B2C**: fica separado. Lá o aceite é por pessoa, dentro do app, no login; aqui é por escritório,
  por representante, antes de instalar, com registro probatório. Os dois podem aparecer juntos numa aba "Legal" do
  RootifyONE no futuro, lendo cada um a sua tabela.
- **LGPD e validade**: nome completo + e-mail + código + data/hora + hash + IP resumido é **assinatura eletrônica
  simples**, válida entre particulares (MP 2.200-2/2001, art. 10, §2º; Código Civil, art. 107: forma livre) e a prática
  usual de "click-wrap". Não precisa de DocuSign nem de certificado. O que fortalece: o aceite vir do e-mail do
  responsável cadastrado na licença, o protocolo devolvido e, numa etapa seguinte, um **e-mail de confirmação** ao
  aceitante com o protocolo (via `lex-equipe`). Dados mínimos, finalidade declarada no próprio texto, guarda pelo prazo do
  contrato e prescricional. **Validar o texto com o Leandro antes de publicar**; o aceite não substitui a proposta
  comercial (preço, prazo), que continua à parte.

## 6. Ordem de entrega

1. **Dono**: dá o "pode aplicar" para o SQL único de `admin_lex_listar` (pedido nº 1 do RootifyONE + campo `aceite`) e para
   `2026-11-09b-sol-aceites.sql`. **LexSuiteONE** aplica e escreve "aplicado" no QUADRO; o dono cola no RootifyONE.
2. **Dono + Leandro**: revisam o texto dos termos (`lexsuiteone/paginas/aceite.html`, rascunho pronto no repositório local
   da Arquitetura). Com o "pode publicar", **LexSuiteONE** publica a página e o e-mail de boas-vindas com o passo
   "Antes de instalar, aceite os termos" e o campo `{{email}}`.
3. **RootifyONE**: preenche `{{email}}` na prévia, mostra `email_responsavel` e `boas_vindas` (já no rascunho), selo e etapa
   de aceite, bloco Termos em Configuração. Publica a versão.
4. **Dono**: envia o e-mail de boas-vindas à KR Law pelo botão (prazo: quarta 11/Nov). Se o texto dos termos não estiver
   pronto até lá, o e-mail sai sem o passo de aceite e o aceite é pedido depois, por e-mail separado (decisão do dono).
5. Depois: e-mail de confirmação do aceite; `aceite` na `lex-conta` e no programa; CRM de clientes (modelo de dados
   primeiro); planos e cobrança.

## PARA A CONVERSA DO ROOTIFYONE

**Pode fazer sozinha (sem perguntar ao LexSuiteONE):**
- Tudo em `rootify-one/`: moldura B2B, abas, seletor, `rootify-lex.js`, `rootify-b2b.js`, testes, CSS, diretrizes, versão
  e publicação do RootifyONE.
- Exibir qualquer campo que `admin_lex_listar`, `admin_lex_detalhe`, `admin_sol_retorno`, `admin_sol_aceites` já devolvem,
  e chamar `admin_lex_salvar`, `admin_lex_ativar`, `admin_lex_convidar_lote`, `admin_lex_aprovar_pessoa`,
  `admin_lex_esquecer_instalacao`, `admin_lex_criar` e `lex-equipe` (`boas_vindas`) como estão.
- Motor genérico da jornada e das estatísticas, desde que use só os campos e dimensões que vêm do banco.
- Escrever pedidos numerados em `rootify-one/entrega/solverone-app/PEDIDOS-LEXSUITEONE.md` e rascunhos `RASCUNHO-*.sql`.
- Tolerar campo que ainda não existe (tela não quebra; mostra "—").

**Precisa esperar (vem do LexSuiteONE, colado pelo dono):**
- O "aplicado" do SQL de `admin_lex_listar` (pedido nº 1 + `aceite`) e de `sol_aceites`, com a lista exata dos campos.
- O "publicado" da página de aceite e do e-mail de boas-vindas com `{{email}}` (antes disso, a prévia pode preencher
  `{{email}}` em branco sem erro).
- Qualquer regra de negócio da licença (o que "parado", "pausada", "aprovada" significam) e qualquer campo novo no
  modelo de e-mail.

**Nunca faz:**
- Aplicar SQL no projeto `solverone-app` que toque `lex_*`, `admin_lex_*`, `sol_*` ou funções da nuvem `lex-*`; nem
  manter cópia "oficial" dessas funções fora do `lexsuiteone`.
- Ler ou escrever tabelas `lex_*`/`sol_*` direto da tela (só pelas funções `admin_*`).
- Editar texto ou versão dos termos, texto do e-mail de boas-vindas, ou arquivos do `lexsuiteone`.
- Enviar e-mail a cliente por conta própria (só pelo botão, com o clique do dono) ou chamar o Resend direto.
- Publicar versão do RADAR, do site `judicial.solverone.com.br` ou qualquer coisa do `lexsuiteone`.
- Colocar código de licença (`LEX-…`), chave ou segredo em arquivo, quadro ou chat.
