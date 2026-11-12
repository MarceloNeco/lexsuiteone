# Prompt para a conversa do RootifyONE · sincronia com o LexSuiteONE (09/Nov/2026, noite)

Copiar e colar inteiro na conversa do RootifyONE. Escrito pela Arquitetura do LexSuiteONE a pedido do dono; não depende de
contexto de outra conversa. Fonte: `lexsuiteone/documentacao/DECISAO-B2B-QUEM-FAZ-O-QUE-2026-11-09.md` e `docs/QUADRO.md`.

---

**Para a conversa do RootifyONE (de Marcelo, com a decisão da Arquitetura do LexSuiteONE).**

**1. Regra de convivência (vale desde já).** Tudo em `rootify-one/` é seu, inclusive `rootify-lex.js` e `teste/licencas.js`;
a conversa do LexSuiteONE não edita mais nada aqui. Tudo em `lexsuiteone/` (SQL `lex_*` e `sol_*`, funções da nuvem
`lex-conta` e `lex-equipe`, modelos de e-mail, termos, página de aceite) é do LexSuiteONE; você não edita, não aplica
SQL nessas tabelas e funções, nem mantém cópia "oficial" delas. O que você precisa do banco vai como **pedido numerado**
em `rootify-one/entrega/solverone-app/PEDIDOS-LEXSUITEONE.md` (rascunho `RASCUNHO-*.sql` opcional); eu (Marcelo) levo ao
LexSuiteONE e trago de volta o "aplicado" com o contrato. Enquanto não vier, a tela tolera o campo que falta (mostra "—").
Nenhum pedido novo entra na versão antes do "aplicado". Antes de publicar uma versão, confira que não há pedido seu
pendente que a versão já supõe atendido.

**2. O que já está aplicado no banco `solverone-app` (pode usar agora).**
- `admin_lex_listar()` devolve, além do que já devolvia: `email_responsavel` (texto ou null); `boas_vindas`
  (`{ok, para, em}` do último envio pela `lex-equipe`, ou null); `aceite` (`{aceito:true, versao, aceito_em, nome, email,
  protocolo}` ou `{aceito:false}`); `exigir_aceite` (true/false).
- `admin_lex_salvar(p)` aceita `exigir_aceite` (mas para ligar/desligar use a função própria abaixo, que registra o motivo).
- `admin_lex_dispensar_aceite(p_codigo, p_dispensar boolean, p_motivo)`: **libera o uso sem aceite** (`p_dispensar = true`)
  ou volta a exigir (`false`). Motivo obrigatório (5 letras ou mais). Grava em `lex_eventos` (tipo `licenca_alterada`,
  detalhe "aceite dos termos dispensado pela equipe…", `quem = equipe:<uuid>`, `motivo`) e no log da plataforma. Devolve a ficha.
- `admin_sol_aceites(p_app, p_licenca default null)`: lista até 200 aceites (`id, app, licenca, termo, versao, hash, nome,
  email, aceito_em, ip_resumo, navegador, origem`). Para o RADAR: `p_app = 'radar-judicial'`.
- O aceite feito pelo cliente aparece sozinho: a `lex-conta` grava em `sol_aceites` e em `lex_eventos`
  (`licenca_alterada`, detalhe "termos aceitos: versão …, protocolo …, por …", `quem = cliente:<e-mail>`), e manda e-mail de
  confirmação ao responsável e à SolverONE. Nada a fazer do seu lado além de mostrar.
- Seu pedido nº 1 (`RASCUNHO-2026-11-09-lex-listar-responsavel.sql`) está atendido: renomeie para `APLICADO-…` ou apague.

**3. O que construir agora (versão sua, quando quiser publicar).**
- Ficha da licença: mostrar `email_responsavel` e `boas_vindas`; **selo** "Termos aceitos por {nome} em {data} (v{versao},
  protocolo {protocolo})" ou "Sem aceite"; **interruptor "Exigir aceite dos termos antes do uso"** lendo `exigir_aceite`.
  Ao mudar o interruptor, abrir confirmação com campo **motivo obrigatório** e chamar `admin_lex_dispensar_aceite`
  (`p_dispensar = !exigir`). Texto do (?) ao lado: "A licença fica ativa. Com o interruptor ligado, o programa só libera a
  leitura depois que o responsável aceita os termos pelo link do e-mail de boas-vindas. Desligar libera o uso sem aceite:
  é um risco assumido pela SolverONE e fica registrado com quem, quando e motivo."
- Histórico da ficha: já lê `lex_eventos`; os eventos de aceite e de dispensa aparecem como `licenca_alterada` com o detalhe
  acima (mostre `quem` e `motivo`, como já faz).
- Jornada (aba Clientes): etapa **3 "Termos aceitos"** entre "Boas-vindas enviado" e "Instalado", a partir de `aceite.aceito`.
  Se `exigir_aceite` for false e não houver aceite, mostrar "dispensado pela equipe" nessa etapa, não "pendente".
- Aba Configuração do produto: bloco "Termos" com versão vigente **1.0 (09/Nov/2026)**, link
  `https://judicial.solverone.com.br/aceite.html` e total de aceites (`admin_sol_aceites`). Enquanto a página não estiver
  publicada, marcar "página ainda não publicada".
- Prévia do e-mail de boas-vindas: preencher `{{email}}` com `email_responsavel` e `{{nome}}` (já preenche) também dentro
  do link do aceite (`aceite.html?codigo=…&email=…&nome=…`). O modelo ganha esses campos quando o LexSuiteONE publicar; até
  lá a prévia não muda. Se `email_responsavel` estiver vazio, avisar antes de enviar ("preencha o e-mail do responsável:
  é ele que pode aceitar os termos").
- Nada de regra nova além destas. Nenhuma consulta direta a `lex_*`/`sol_*`: só as funções `admin_*`.

**3b. Acréscimo (09/Nov, noite, decisão do dono): termos em duas camadas.** Além do aceite do escritório, cada pessoa que
usa o programa aceita os termos de uso no cadastro (por versão). Já aplicado no banco: tabela `sol_termos` (versões
vigentes), `admin_sol_termos()` (lista: `termo, suite, alcance escritorio|pessoa, titulo, versao, vigente_desde, link`),
`admin_sol_termo_publicar(p_termo, p_versao, p_link, p_hash_texto, p_motivo)` (muda a versão vigente, motivo obrigatório,
registrado) e `sol_aceite_situacao(p_app, p_licenca, p_termo, p_email)` (situação de um aceite: `aceito, versao,
aceito_em, fuso, nome, email, protocolo, versao_vigente, link, precisa_aceitar`). `admin_sol_aceites` passou a devolver
`fuso`. Na ficha da licença, bloco **"Termos"** com duas partes: (a) escritório, como já descrito; (b) **pessoas**: para
cada pessoa da licença, o último aceite do termo `lexsuiteone-uso` (de `admin_sol_aceites(app, codigo)` filtrado por
`termo`), mostrando nome, e-mail, versão, data/hora com o `fuso` informado e protocolo; se a versão for diferente da
vigente em `admin_sol_termos`, marcar "versão antiga: precisa aceitar de novo"; sem aceite, "ainda não aceitou". Na aba
Configuração do produto, a lista de `admin_sol_termos` (termo, alcance, versão, desde, link) e, por enquanto só leitura,
sem botão de publicar versão (fica para depois, com desenho).

**3c. Resposta ao seu pedido nº 2 (versão nova dos termos), 09/Nov.** Desenho completo em
`lexsuiteone/documentacao/DECISAO-B2B-QUEM-FAZ-O-QUE-2026-11-09.md`, seção 5d. Em resumo: o texto mora no site do produto
(LexSuiteONE publica a página com o número novo); a vigência mora no banco e **quem a liga é o dono, no RootifyONE**.
Construa em Configuração → Termos: (1) lista de `admin_sol_termos()` (termo, alcance, versão, desde, link, "exige novo
aceite"); (2) prévia do texto: iframe de `https://judicial.solverone.com.br/aceite.html?ler=1` (ou `?ler=uso` para o
termo de pessoa), como a prévia do e-mail; (3) botão **"Publicar versão"**: campos versão (obrigatório, diferente da
vigente), motivo (obrigatório), e, só para o termo `lexsuiteone-termos`, interruptor "Exigir novo aceite do responsável"
com (?) "Ligado: o programa volta a travar nos escritórios até o responsável aceitar a versão nova. Desligado: o aceite
antigo continua valendo"; antes de habilitar o botão, ler o `#versao` da página do site e exigir que seja igual à versão
digitada (se não, mostrar "a página ainda está na versão Y: peça ao LexSuiteONE"); confirmar e chamar
`admin_sol_termo_publicar(p_termo, p_versao, p_link: '', p_hash_texto: '', p_motivo, p_reaceite)`; (4) na ficha da
licença e na jornada, marcar "versão antiga" quando `versao` do aceite for diferente de `versao_vigente` (use
`sol_aceite_situacao` ou compare com `admin_sol_termos`); para o escritório, "pendente" só se `reaceite_obrigatorio`
estiver ligado ou nunca houver aceite. Para a pessoa, versão nova = aceita de novo, sempre. Não copie o texto dos termos
para dentro do RootifyONE nem para `termos.json`: a fonte é uma só, a página do produto.

**3d. Interruptores (Controle dos apps) valendo no RADAR JUDICIAL (pedido do dono, 09/Nov noite).** O RADAR é programa
instalado e não faz pedido externo: quem lê os interruptores é a função da nuvem `lex-conta`, em
`https://solverone.com.br/solverone-dados/recursos/global.json` e `recursos/radar-judicial.json` (o do app vence), e
devolve `recursos: {id: ligado}` ao programa. O que falta do seu lado: (1) o Controle dos apps precisa enxergar o app
`radar-judicial` (id de `sol_apps` e do catálogo B2B) e ler a lista do que ele obedece em
`https://judicial.solverone.com.br/recursos-do-app.json` (já publicado: declara `assistone`), porque o site do produto não
fica em `solverone.com.br/<repo>/`; (2) ao salvar, publicar `recursos/radar-judicial.json` no solverone-dados, no mesmo
formato dos outros apps (`{"app": "radar-judicial", "recursos": {"assistone": {"ligado": false, …}}}`); (3) o `global.json`
já vale para o RADAR hoje (desligar `assistone` em `*` desliga lá também, em até 5 minutos mais a próxima conferência do
programa). Nada de SQL.

**3e. Histórico de versões dos termos e e-mail do responsável (12/Nov).** (1) Na prévia do e-mail de boas-vindas, se
`email_responsavel` da ficha estiver vazio, avisar antes de enviar ("preencha o e-mail do responsável: ele vai no link do
aceite"); o `{{email}}` vazio do teste do dono veio daí. (2) Em Configuração → Termos, listar `sol_termos_versoes_lista(p_termo)`
(versão, data, link do texto, material, motivo) e, ao "Publicar versão", o interruptor "Exigir novo aceite" passa a chamar-se
"Mudança material (exige novo aceite de todos)"; sem ele, a versão é editorial e ninguém é perguntado. (3) Na ficha, o aceite
de cada pessoa continua vindo de `admin_sol_aceites` (termo único `lexsuiteone-termos`).

**3f. Chamados do RADAR JUDICIAL na central de feedback (desenho de 12/Nov, `documentacao/DESENHO-CRITERIOS-CHAMADOS-CNPJ-2026-11-12.md`,
seção 2).** O RADAR vai abrir chamados pelo AssistONE, que chegam em `sol_feedback` com `app = radar-judicial` pela `lex-conta` (a função
chama `sol_enviar_feedback`; nada muda no SQL da central). Na sua ficha e na fila: (1) aceitar e mostrar as categorias do RADAR
(`erro`, `duvida`, `sugestao`, `licenca-e-acesso`, `planilha-e-pasta`, `leitura-do-diario`, `outros`), hoje a lista de
`rootify-feedback.js` é fixa; (2) mostrar `aparelho.licenca` e `aparelho.escritorio` como "Licença" e "Escritório" na ficha
(o `anon_id` é o id da instalação); (3) a resposta ao chamado vai por e-mail só quando `pode_responder` for verdadeiro, como já é.
Quando a `lex-conta` v17 estiver publicada, aviso aqui; até lá, nada a fazer.

**3g. Contas de teste dentro da produção (pedido do dono, 12/Nov; desenho `documentacao/DESENHO-CONTAS-DE-TESTE-2026-11-12.md`).**
A Arquitetura aplica o SQL que cria o campo `teste` em `lex_contas`, `assinaturas` e `sol_feedback` (este último preenchido sozinho).
Na sua tela: (1) ficha da licença: interruptor "Conta de teste" (`admin_lex_listar` devolve `teste`; `admin_lex_salvar` aceita
`teste`; `admin_lex_criar` ganhou a versão com `p_teste` para a licença já nascer marcada); (2) lista de licenças e fila de chamados
com a etiqueta "TESTE"; (3) painéis: `admin_sol_retorno` e `admin_feedback_painel` já devolvem `sem_contas_de_teste: true` e
excluem as contas de teste; nenhum número seu conta conta de teste; (4) ficha da pessoa dos apps web: interruptor "Pessoa de teste"
gravando `assinaturas.teste` (crie a função admin correspondente no seu SQL e mande à Arquitetura aplicar); (5) a opção "limpar os
dados de teste" passa a usar `teste = true` e só roda depois do staging, com cópia e o "pode" do dono.

**4. O que esperar (vem do LexSuiteONE, colado por mim).** O "publicado" da página de aceite e do e-mail com `{{email}}`
e `&nome=`; o aviso de que a trava da KR Law foi ligada; a ampliação do check de `lex_eventos` com tipos próprios
(`termos_aceitos`, `aceite_dispensado`, `aceite_exigido`) numa sessão em que eu esteja no desktop (até lá, tudo é
`licenca_alterada` com o detalhe).

**5. O que nunca fazer.** Aplicar SQL que toque `lex_*`, `admin_lex_*`, `sol_*` ou funções `lex-*`; ler ou escrever essas
tabelas direto da tela; editar texto ou versão dos termos, o modelo do e-mail ou arquivos do `lexsuiteone`; enviar e-mail a
cliente por conta própria (só pelo botão, com o meu clique) ou chamar o Resend direto; publicar o RADAR ou o site
`judicial.solverone.com.br`; pôr código de licença (`LEX-…`), chave ou segredo em arquivo, quadro ou chat.

**6. Ao terminar**, me devolva em até 10 linhas: versão publicada, o que entrou, o que ficou esperando e o número de qualquer
pedido novo em `PEDIDOS-LEXSUITEONE.md`, para eu levar ao LexSuiteONE.

---

## Protocolo de sincronia (para o dono: quando e o que levar de uma conversa à outra)

| Quando | O que levar | De → para |
|---|---|---|
| O LexSuiteONE escrever "aplicado"/"publicado" no quadro | A linha inteira do quadro (ela traz o contrato dos campos) | LexSuiteONE → RootifyONE |
| O RootifyONE criar um pedido numerado | O número e o texto do pedido (ou o caminho do arquivo) | RootifyONE → LexSuiteONE |
| O RootifyONE publicar versão | O resumo de 10 linhas do item 6 | RootifyONE → LexSuiteONE (anoto no quadro) |
| Você mudar uma regra de negócio, de nuvem ou de banco | Primeiro ao LexSuiteONE (desenho curto); só depois o RootifyONE implementa | você → LexSuiteONE → RootifyONE |
| Conflito de arquivo entre conversas | Parar as duas; me avisar; a dona do arquivo resolve | qualquer → você |
