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
