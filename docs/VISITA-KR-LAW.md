# Visita à KR Law (quinta, 12/Nov/2026): roteiro e prompts do Claude in Chrome

Complementa `robo/ROTEIRO-INSTALACAO.md` (instalação do robô). Aqui ficam os prompts para usar no **Claude in Chrome**
no computador do Leandro, com o consentimento dele, para aprender como os sistemas funcionam e planejar as integrações.
Nada aqui produz efeito nos sistemas: é leitura e anotação. **Atualizado em 09/Nov/2026 (noite)**: programa na versão 0.7.16
(tudo o que a visita precisa: planilha por frente, cópias de segurança, armazenamento, "Colar resposta da área logada"), termos de uso 1.1 com aceite, autorização do Leandro antes de qualquer prompt na área logada e
formato padronizado de resposta que o RADAR lê (seção "Resposta para o RADAR"). Os prompts foram escritos para o Claude
in Chrome, mas servem em qualquer extensão de IA de navegador. Versão anterior: 08/Nov/2026 (foco na ficha de canais; prompts
escritos para rodar **sozinhos**, no Sonnet, na conta do escritório, sem ninguém acompanhando; o relatório volta para a
SolverONE pela conversa compartilhada). Cópia para o celular: Google Doc na pasta "VISITA KR LAW (quinta 12-Nov)" do
Drive do dono. O GitHub é a fonte.

## Para que serve

O dono não é advogado e não tem acesso às áreas logadas dos tribunais nem ao Astrea. O Leandro é o parceiro que abre
essas portas: com o que a extensão mapear, a SolverONE constrói o robô e os prompts especialistas que vão navegar nessas
áreas (consultar, baixar autos, ler publicações, alimentar o Astrea). Por isso os relatórios pedem o **mapa técnico**:
endereços, nomes exatos de menus, campos e botões, ordem de cliques, onde entram certificado e token, o que dá para fazer
sem advogado logado e o que não dá.

## Foco da visita: a ficha de canais da empresa processada

O Leandro apontou o diferencial do produto: **levantar e confirmar os canais de contato da empresa processada**, para o
time de compliance do escritório analisar e decidir se e como agir. O JUDICIAL e a extensão **não enviam nada a
ninguém**: não ligam, não mandam e-mail nem mensagem, não seguem perfis, não preenchem formulário.

O que pode entrar na ficha e o que nunca entra:

| Pode | Só com condição | Nunca |
|---|---|---|
| Dados da empresa: telefone geral, e-mail comercial, formulário de contato, site, LinkedIn e Instagram **da empresa**, endereço, e nomes e cargos públicos de sócios e administradores, sempre com a fonte | Celular ou e-mail de uma pessoa, **só se a própria empresa o publica como contato comercial** (no site, na página ou no perfil da empresa), anotando onde | Qualquer dado do reclamante e de outras pessoas físicas (testemunhas, advogados da parte contrária, familiares): no relatório, escrever "pessoa física" no lugar |

## Antes de começar: autorização do Leandro (obrigatório)

Os prompts 1, 3 e 4 rodam na área logada do Leandro, com a credencial dele. Antes do primeiro, ele confirma, em voz alta
e por escrito na primeira mensagem da conversa da extensão ("Autorizo esta extensão a navegar, só lendo, na minha
sessão do PJe/Astrea, para mapear o sistema, conforme o roteiro da SolverONE"), que:
1. o login é feito por ele, e a extensão nunca vê senha, token ou certificado;
2. a extensão só lê: não peticiona, não assina, não marca ciência, não altera nada;
3. são poucos processos (o de referência e, no máximo, os 3 do Prompt 2; nunca mais de 30 por dia), porque há tribunal
   que bloqueia quem abre muitos processos de terceiros;
4. dados de pessoas físicas (autor da ação, testemunhas) não são copiados;
5. a escolha da extensão e o uso da credencial são do escritório (termos de uso 1.1, seção 5).
Se ele não autorizar algum ponto, aquele prompt não roda.

## Resposta para o RADAR (formato padronizado, versão 1)

Além do `RELATÓRIO FINAL` (que é para a SolverONE), os prompts que olham processos devolvem um bloco que o advogado copia e
cola no RADAR ("Colar resposta da área logada", na versão 0.7.16). O RADAR lê esse bloco sem IA, confere linha por linha
e preenche a ficha e a planilha. Formato:

```
RESPOSTA PARA O RADAR v1
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|
| 0000000-00.0000.5.02.0000 | valor_causa | 150000,00 | encontrado | PJe petição inicial | 2026-11-12 | |
| 0000000-00.0000.5.02.0000 | telefone | (11) 0000-0000 | encontrado | PJe petição inicial | 2026-11-12 | da empresa |
| 0000000-00.0000.5.02.0000 | email | | nao_consta | PJe petição inicial | 2026-11-12 | |
| 0000000-00.0000.5.02.0000 | endereco | | tentar_depois | | 2026-11-12 | a sessão expirou |
```

- `dado`: valor_causa, data_ajuizamento, telefone, email, site, endereco, socio_contato, outro.
- `resultado`: `encontrado` (com valor e fonte), `nao_consta` (o processo não traz), `tentar_depois` (problema técnico,
  sessão expirada, site fora do ar: o RADAR marca para buscar de novo).
- Nunca: dado do autor da ação, de testemunha ou de advogado da outra parte, nem CPF. O RADAR recusa essas linhas.
- O exemplo acima é fictício.

## Como os prompts rodam na visita (leia antes)

- **Conta e modelo.** A extensão Claude in Chrome roda no Chrome do Leandro, na conta Claude do escritório (provavelmente
  Pro), com o modelo **Sonnet**, para não gastar os créditos de Opus dele. Por isso os prompts são longos e dizem tudo: o
  que ver, em que ordem, quando parar e como relatar. Se o plano dele travar por limite de uso, espere o tempo que a tela
  indicar ou passe para a conta do dono num perfil novo do Chrome ("Visita SolverONE"), apagado no fim do dia.
- **Sem supervisão.** A extensão trabalha sozinha enquanto o Leandro testa o robô e o dono cuida de outras coisas. Ela
  não pede nada a ninguém no meio do caminho. Só para quando um site exige login, token, certificado ou captcha: aí
  escreve `BLOQUEIO`, entrega o que já tem e espera. Quem voltar à tela resolve o login (só o Leandro) e digita
  "continue".
- **Janela própria.** A extensão roda numa janela do Chrome só para ela, com a aba do sistema. Ninguém usa essa janela
  enquanto ela trabalha; o robô e o resto ficam em outra janela. Na primeira ação em cada site a extensão pede permissão
  para agir ("Permitir"): clicar nisso antes de sair de perto.
- **Um prompt por conversa.** Cada prompt é colado inteiro numa conversa nova da extensão. Não misture dois prompts.
- **Sem prints.** A extensão não salva arquivos nem entrega imagens. No lugar de prints ela escreve "telas" em texto,
  num formato fixo (endereço, título, menus, campos com rótulos, botões, o que acontece ao clicar). Para construir um
  robô isso vale mais do que uma imagem.
- **Relatório e como chega ao dono.** Ao fim, a extensão escreve `RELATÓRIO FINAL` num bloco só, em Markdown. A
  conversa fica guardada na conta do escritório e, pelo que sabemos, aparece no claude.ai dessa conta. Lá o Leandro usa
  "Compartilhar" e manda o link ao dono, que copia a conversa para a conta dele e avisa para o Leandro desfazer o
  compartilhamento. Se a conversa não aparecer no claude.ai, ele seleciona todo o texto do painel da extensão (Ctrl+A,
  Ctrl+C) e cola num Google Doc compartilhado com `integracao@solverone.com.br`. **Testar isso no começo da visita** com
  uma conversa curta.
- **Pode compartilhar porque não tem nada sensível.** Nenhuma tela de login entra no relatório, nenhuma credencial é
  vista e nomes de pessoas físicas não são copiados. Os relatórios ainda assim não entram no repositório nem no site.

## Ordem do dia (quinta 12/Nov)

Links para abrir no celular, todos sem login: este arquivo; instalação em
[`robo/ROTEIRO-INSTALACAO.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/robo/ROTEIRO-INSTALACAO.md);
manual em https://judicial.solverone.com.br/manual.html; pacote em https://judicial.solverone.com.br/downloads/Instalar-LexSuiteONE.zip.
No computador do Leandro, abrir os prompts por este arquivo no GitHub (sem login) e copiar pelo botão de copiar do bloco.

**Antes, em casa (até quarta).** Ensaio da instalação no PC do dono com a segunda conta Google, `DIAGNOSTICO.bat` e uma
rodada real; e-mail de boas-vindas já enviado ao Leandro (pelo dono, no botão "Preparar e-mail de boas-vindas" do
RootifyONE, com prévia). Confirmar com o Leandro: certificado digital em mãos para o PJe; em que pasta fica a planilha
(no computador ou numa pasta do Google Drive; não é preciso compartilhar com a SolverONE); o texto dos termos 1.1; se a conta Claude do escritório tem a extensão
Claude in Chrome (plano pago). Se não tiver, a extensão roda num perfil novo do Chrome dele ("Visita SolverONE") com a
conta do dono, e o perfil é apagado no fim. O notebook do dono não recebe login nem certificado de ninguém. Combinar um
processo de referência no TRT2 e um no TRT15 (do próprio escritório) e, se houver, um no TJSP.

1. **Chegada (15 min).** Explicar o que vai acontecer e pedir o OK: instalar o robô e três ou quatro observações só de
   leitura com a extensão, que trabalham sozinhas, sem senhas. Abrir uma janela do Chrome só para a extensão (conta do
   escritório ou perfil novo, extensão instalada, modelo Sonnet). Testar com uma conversa curta e conferir se ela aparece
   no claude.ai dessa conta.
2. **Instalar o robô (45 a 60 min).** Seguir o `ROTEIRO-INSTALACAO.md`: baixar o pacote do site, `DIAGNOSTICO.bat`,
   configurar, escolher a pasta da planilha (no computador ou no Drive do escritório; **não** se compartilha com a
   SolverONE), agendar a rodada diária e iniciar a primeira rodada agora (demora: deixar rodando). Instalar no
   computador que fica ligado nos horários das leituras (o do escritório ou o de casa: perguntar ao Leandro qual).
   **Conferir o armazenamento** (Configuração → Armazenamento): espaço livre no disco (o ideal é mais de 10 GB), onde
   ficam `LexSuiteONE - Trabalhista.xlsx` e a pasta `Cópias de segurança`, e se o aviso de disco aparece. Anotar
   quantos GB livres o computador tem. A pasta escolhida aqui não precisa mudar depois: as frentes novas (tributário,
   cível, empresarial) ganham a própria planilha na mesma pasta, sozinhas.
3. **Em paralelo: Prompt 3, Astrea.** O Leandro entra no Astrea na janela da extensão, cola o Prompt 3, clica em
   "Permitir" quando ela pedir, e deixa a janela sozinha. Se ela escrever `BLOQUEIO`, só o Leandro resolve e digita
   "continue".
4. **Depois: Prompt 1, PJe.** O Leandro faz o login no PJe do TRT2 com o certificado, na janela da extensão, cola o
   Prompt 1 com o número do processo de referência e deixa sozinha. Quando o PJe pedir token ou certificado, ela escreve
   `BLOQUEIO` e espera o Leandro. Depois o TRT15.
5. **Se der tempo: Prompt 4, e-SAJ e DJE do TJSP.** Parte pública sem login; parte logada só se o Leandro quiser.
   Serve para as frentes tributária e cível.
6. **Lista do dia pronta.** Mostrar na tela local e na planilha; validar 3 ou 4 itens com o Leandro (é ação nova? é
   empresa? a comarca interessa?); anotar as regras que ele quer ajustar. Escolher 3 empresas para o Prompt 2, que roda
   em casa, sem login em nada.
7. **Fechamento (15 min).** Conferir: rodada agendada, Leandro sabe abrir a tela e a planilha, sabe o que fazer se
   aparecer o aviso "a planilha está ficando grande" (clicar em "Limpar a planilha (com cópia)"),
   manual e `judicial@solverone.com.br` como contato. Entregar os relatórios: em cada conversa da extensão, no claude.ai
   da conta do escritório, "Compartilhar" e mandar o link ao dono; se não der, selecionar todo o texto do painel e colar
   num Google Doc compartilhado com `integracao@`. Apagar o perfil do Chrome se usou a conta do dono. Anotar feedbacks e
   dizer o que vem na 0.8.

Depois: relatórios e feedbacks vão para a sessão de Produto; dúvidas de instalação e e-mail, para a sessão de Operação.

## Regras que valem para todos os prompts

- **Nunca pedir, digitar, copiar, fotografar ou anotar senha, token, código de certificado ou qualquer credencial.** O
  advogado faz o login sozinho, com a extensão fechada ou pausada; só depois a extensão entra na aba já logada. Se o site
  pedir login, captcha, token ou certificado no meio do caminho, a extensão **para, escreve BLOQUEIO e espera o
  advogado**. Nenhuma tela de login, senha, token, certificado ou captcha entra no relatório.
- Somente leitura: não cadastrar, peticionar, assinar, marcar como lido, alterar campo, nem clicar em "enviar",
  "assinar", "protocolar", "excluir", "importar", "converter" ou similares. Se um botão parecer gravar algo, não clica e
  anota o nome.
- Nada é enviado a ninguém: nenhuma ligação, e-mail, mensagem, comentário, convite, curtida ou formulário.
- Uma ação por vez, sem pressa, uma aba só. Dados de pessoas físicas seguem a tabela acima: "pessoa física" no lugar do
  nome. Empresas (razão social, CNPJ e os canais da empresa) podem ser citadas.
- Ignorar processos de outros clientes que apareçam na tela; abrir só o de referência.
- Modelo da extensão: Sonnet. Cada prompt termina com `RELATÓRIO FINAL`, que é colado na sessão de Produto para virar
  desenho de integração e skills de navegação.

## Prompt 1 · PJe com o login do advogado (consulta, download e contatos da ré nos autos, somente leitura)

Como usar: o advogado faz o login no PJe do tribunal na aba da janela da extensão. Com a aba logada, abra uma conversa
nova na extensão, cole o texto abaixo (troque o número do processo e o tribunal), clique em "Permitir" quando ela pedir e
deixe a janela sozinha.

```
Você está numa aba do PJe do TRT2 (https://pje.trt2.jus.br) onde um advogado já fez login com as credenciais dele. Sua tarefa é mapear, somente lendo, como se consulta um processo e como se baixam os documentos dele, e anotar onde aparecem os dados de contato da empresa ré (endereço, e-mail e telefone), para que um robô e prompts especialistas possam fazer isso depois. Processo de referência: 0000000-00.0000.5.02.0000 (troque pelo número real).

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui. Se faltar uma informação, anote "faltou: ..." e siga.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga para o próximo passo.
- Se se perder, volte ao painel inicial do advogado e continue do passo em que parou.
- Telas: você não entrega imagens. Quando uma tela importar para quem vai construir o robô, registre-a em texto, num bloco que comece com TELA e um número, neste formato: TELA 01 — nome-curto — URL: ... | Título: ... | Caminho de menu: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações (paginação, tempo de carga, avisos): ... Numere em sequência. Não registre tela de login, senha, token, certificado ou captcha, e não copie nomes de pessoas físicas.
- Bloqueio: se o site pedir login, senha, token, certificado ou captcha, não tente resolver nem contornar. Escreva BLOQUEIO, diga o que foi pedido e em que passo você estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome do passo em que parou.
- Pare depois de 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto, marcando o que faltou.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco de texto em Markdown, citando as telas pelo número (por exemplo: ver TELA 03).

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial.
- Somente leitura: não cadastre, não peticione, não assine, não marque como lido, não altere nenhum campo, não clique em "enviar", "assinar", "protocolar", "excluir" ou similares. Se um botão parecer que grava algo, não clique e anote o nome dele.
- Não abra várias abas do PJe ao mesmo tempo. Se o sistema mostrar erro ou lentidão, espere e tente uma única vez.
- Não navegue para fora do PJe. Nada é enviado a ninguém.
- Dados da empresa ré (razão social, CNPJ, endereço, e-mail, telefone) podem ser anotados. Dados do reclamante e de qualquer outra pessoa física (testemunhas, advogados, prepostos), nunca: escreva "pessoa física" no lugar. A qualificação da petição inicial traz os dados do reclamante logo ao lado dos da empresa: anote só a parte da empresa.
- Se a tela do advogado mostrar processos de outros clientes, ignore-os: só abra o processo de referência.

O que fazer, nessa ordem:
1. Localizar a consulta. A partir do painel do advogado, encontre a função de consulta de processo por número (menu, atalho ou campo de busca). Anote: caminho de menu, URL da tela, nome do campo e formato que o número precisa ter. Registre a TELA do painel e a TELA da consulta.
2. Abrir o processo de referência. Anote a URL que abre e se ela contém um identificador interno (um número que não é o número CNJ).
3. Mapear os dados do processo. Na tela do processo, liste os blocos que existem e quais campos cada um mostra. Procure especialmente: classe, assunto(s), data de distribuição (ou autuação), valor da causa, órgão julgador (vara), partes do polo passivo com CNPJ e endereço, advogados das partes, situação atual, última movimentação. Para cada campo, anote o rótulo exato e em qual aba ou seção ele está. Veja se o cadastro da parte ré (clicando no nome dela, se o PJe permitir só visualizar) mostra endereço, e-mail ou telefone. Registre a TELA do processo e a TELA do cadastro da parte ré.
4. Mapear as movimentações e os documentos. Encontre a lista de movimentações e a lista de documentos (petição inicial, notificação ou citação inicial, decisões, atas). Anote como a lista é organizada (ordem, paginação, filtros) e que tipos de documento aparecem. Registre a TELA da lista de documentos.
5. Baixar. Procure as opções de download: documento individual, "autos completos" ou "download do processo" (PDF único ou vários). Baixe a petição inicial e, se existir, o PDF dos autos completos, para a pasta padrão de downloads do Chrome. Anote: nome do botão, se é um link com endereço (qual) ou um botão sem endereço, se abre nova aba, formato, tamanho aproximado, tempo e se pediu confirmação. Não baixe mais de 3 arquivos. Registre a TELA de download.
6. Contatos da empresa ré nos autos. Abra no visualizador do PJe (sem baixar outro arquivo):
   a) A petição inicial. Ache a qualificação da reclamada (normalmente no primeiro parágrafo, depois dos dados do reclamante, com expressões como "em face de", "pessoa jurídica de direito privado", "inscrita no CNPJ", "com sede na", "endereço eletrônico", "e-mail", "telefone"). Anote em que página e em que trecho aparecem o endereço, o e-mail e o telefone da empresa, e qual expressão vem antes de cada um. Não registre essa página como TELA: ela tem dados do reclamante; anote só a posição e as expressões.
   b) A notificação ou citação inicial da ré (aba de expedientes, intimações ou documentos; anote o nome exato). Anote para qual endereço ou meio ela foi expedida (Correios, oficial de justiça, Domicílio Judicial Eletrônico, e-mail) e se há aviso de recebimento ou certidão dizendo se a empresa foi encontrada naquele endereço.
   c) Para cada documento: o texto é selecionável (PDF de texto) ou é imagem escaneada? Os dados estão sempre no mesmo lugar e com as mesmas expressões?
7. Intimações e publicações. No painel do advogado, veja onde chegam as intimações e os expedientes (nome da aba, filtros, prazos, como se marca ciência, sem marcar nada). Registre a TELA de intimações.
8. Verificar o que pediu intervenção humana. Liste cada momento em que o site exigiu captcha, token, certificado ou nova autenticação, e quanto tempo a sessão durou sem pedir login de novo.

RELATÓRIO FINAL, neste formato:
- Mapa do fluxo: passos numerados, cada um com "tela → ação → resultado", incluindo URLs e nomes exatos de menus, botões e campos, e o número da TELA quando houver.
- Tabela de campos: campo | rótulo na tela | aba ou seção | exemplo (mascarado se for pessoa física).
- Downloads: o que baixou, como (link com endereço, botão, nova aba), formato, tamanho e onde ficou.
- Contatos da ré nos autos: documento | dado (endereço, e-mail ou telefone) | aparece? | página e trecho | expressão que vem antes | texto ou imagem | valor encontrado (só da empresa).
- Extração repetível: para cada dado, "sim", "parcial" ou "não", com o motivo (mesmo lugar e mesmas expressões em todo processo? texto selecionável? depende de alguém ter digitado certo?). Diga também se esses dados só aparecem com o login do advogado.
- Intimações: onde chegam e como funcionam.
- Mapa técnico para quem vai construir o robô: endereços (URLs) de cada tela e o que muda neles; nomes exatos de menus, campos e botões; ordem de cliques; como é o download (link direto e qual endereço, nova aba ou botão sem link); paginação; quanto tempo a sessão durou sem pedir login de novo; em que passo exato entram certificado ou token; o que dá para fazer sem o advogado logado, o que exige o advogado logado e o que exige uma pessoa.
- Barreiras: onde exigiu captcha, token ou certificado, e o que mais pode impedir um robô (limite de tempo da sessão, mensagens de erro).
- Dificuldades que você teve navegando (o que não achou, o que demorou).
- Sugestão: em 5 linhas, qual seria o caminho mais curto para um robô fazer o mesmo com o advogado logado, e o que teria de ficar com a pessoa.
- Lista das telas registradas: número, nome curto e o que mostra.

Depois do RELATÓRIO FINAL, escreva também, num bloco separado, a RESPOSTA PARA O RADAR v1 do processo de referência, exatamente neste formato (uma linha por dado; use "encontrado", "nao_consta" ou "tentar_depois"; nunca dados do reclamante nem CPF):
RESPOSTA PARA O RADAR v1
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|
Os dados a buscar são: valor_causa, data_ajuizamento, telefone, email, site e endereco da empresa ré, e socio_contato se a petição trouxer contato de sócio ou administrador da ré.

Se, depois do relatório, alguém escrever "TRT15" e colar outro número de processo, repita o mesmo roteiro em https://pje.trt15.jus.br e diga o que é diferente entre os dois.
```

## Prompt 2 · Ficha de canais da empresa processada (fontes públicas, para o compliance)

Como usar: aba nova no Chrome, sem login em nada. Roda em casa, no computador do dono, com a conta dele. Troque as três
empresas de exemplo por empresas reais da lista do JUDICIAL (razão social, CNPJ e cidade; se a linha do JUDICIAL já
trouxer telefone, e-mail e sócios, cole junto, que a extensão usa como ponto de partida e confere). Nenhuma mensagem é
enviada a ninguém. O uso do que for encontrado é decisão do compliance do escritório.

```
Preciso de uma "ficha de canais" de cada empresa abaixo, feita só em fontes públicas, para o time de compliance de um escritório de advocacia analisar e decidir se e como agir. Você não envia nada a ninguém: não liga, não manda e-mail nem mensagem, não preenche formulário, não segue perfis, não comenta, não cria conta e não burla nenhum login.

Empresas (razão social, CNPJ, cidade, e o que o JUDICIAL já trouxe, se houver):
1. [Razão social 1], [CNPJ], [cidade]
2. [Razão social 2], [CNPJ], [cidade]
3. [Razão social 3], [CNPJ], [cidade]

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se uma página não abrir em 2 tentativas, anote e siga.
- Se um site pedir login ou captcha, não resolva nem contorne: anote e pule para a próxima fonte.
- Pare depois de 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco em Markdown.

O que pode entrar na ficha:
- Dados da empresa: telefone geral, e-mail comercial, formulário de contato, site oficial, perfil da empresa no LinkedIn e no Instagram, ficha da empresa no Google, endereço da sede e das filiais, e nomes e cargos públicos de sócios e administradores. Sempre com a fonte.
- Celular ou e-mail de uma pessoa só entra se a própria empresa o publica como contato comercial (no site, na página ou no perfil da empresa). Anote exatamente onde está publicado. Se o único contato de uma pessoa estiver fora dos canais da empresa, não anote.
- Perfil profissional público de um sócio ou administrador pode ser aberto só para confirmar nome e cargo atual. Não anote mais nada dele.
- Nunca: dados do reclamante e de outras pessoas físicas. Não procure o processo nem quem processou.

Regras de navegação:
- Fontes públicas apenas: site institucional da empresa, página "fale conosco", perfil público da empresa no LinkedIn e no Instagram, ficha da empresa no Google, cadastro público do CNPJ (Receita Federal ou consulta pública equivalente).
- Não use ferramenta de raspagem, não faça buscas em massa, não visite mais de 10 páginas por empresa. Não tente entrar em área logada.
- Se um site pedir login, captcha ou cookie de rastreamento obrigatório, pule e anote.
- Não teste se um e-mail ou telefone funciona (nada de ligar, enviar ou usar serviço de verificação). "Confirmar" aqui é cruzar fontes.

Como confirmar cada canal (cruzamento de fontes):
- O site é mesmo da empresa? Procure o CNPJ ou a razão social no rodapé, na política de privacidade ou na página de contato.
- O e-mail comercial usa o domínio do site? O telefone é o mesmo no site, na ficha do Google e no cadastro do CNPJ?
- O perfil do LinkedIn e o do Instagram apontam para o mesmo site? Têm atividade recente?
- O e-mail do cadastro do CNPJ é de outro domínio (por exemplo, de um escritório de contabilidade)? Se for, anote "provável contato do contador".
- O endereço do cadastro do CNPJ bate com o do site e com o da ficha do Google?

Grau de confiança de cada linha:
- Alta: publicado pela própria empresa num canal oficial (site, perfil da empresa) e confirmado por mais uma fonte.
- Média: uma fonte só, oficial (site da empresa ou cadastro do CNPJ), sem confirmação.
- Baixa: só em fonte de terceiros (diretório, agregador), divergente entre fontes ou com sinal de estar desatualizado.

Parte B, contexto para o compliance (curta): diga o que não é permitido ou não é recomendável pelas regras da OAB sobre publicidade e captação de clientela (Provimento 205/2021 e Código de Ética e Disciplina), e o que a LGPD exige para usar dados de contato de empresa e de sócios. Cite a fonte de cada ponto. Se der tempo, na Biblioteca de Anúncios da Meta (facebook.com/ads/library), país Brasil, pesquise "defesa trabalhista para empresas" e "sua empresa foi processada" e anote os 3 anúncios mais relevantes: anunciante, mensagem resumida, chamada para ação e link.

RELATÓRIO FINAL, pronto para o compliance:
- Uma ficha por empresa, com o cabeçalho "Razão social · CNPJ · cidade · data do levantamento" e esta tabela:
  canal | dado encontrado | fonte (endereço da página ou nome da fonte) | data da consulta | confiança (alta, média ou baixa) | confirmado por | observação
  Linhas, nesta ordem: site oficial; página de contato ou formulário; telefone geral; e-mail comercial; endereço da sede; filiais; LinkedIn da empresa; Instagram da empresa; ficha no Google; sócios e administradores (uma linha por pessoa: nome e cargo); contato de pessoa publicado pela empresa (se houver); outros.
  Se um canal não foi encontrado, escreva "não encontrado" e onde procurou.
- Divergências: o que não bate entre as fontes (telefone, endereço, e-mail).
- Observações para o compliance, em até 3 linhas por empresa: quais canais são institucionais da empresa e quais pedem cautela (e-mail do contador, celular, perfil sem atividade). Não recomende abordagem: a decisão é do compliance.
- Mapa técnico para quem vai construir o robô: para cada fonte, o endereço da página consultada, como se chega ao dado (busca, menu, rolagem), se pediu captcha ou cookie, e se o dado está em texto na página ou só em imagem.
- Tabela da Parte B: regra | o que diz | fonte; e, se houver, anunciante | mensagem resumida | chamada para ação | link.
- Lista do que não conseguiu abrir e por quê.
```

## Prompt 3 · Astrea, o sistema do escritório (mapear para integrar, somente leitura)

Como usar: o advogado faz o login no Astrea na aba da janela da extensão. Com a aba logada, abra uma conversa nova na
extensão, cole o texto, clique em "Permitir" quando ela pedir e deixe a janela sozinha. Serve para desenhar como o
JUDICIAL vai entregar as ações novas e as fichas de canais dentro do sistema que o escritório já usa.

```
Você está numa aba do Astrea (sistema de gestão do escritório) onde um advogado já fez login. Sua tarefa é mapear, somente lendo, como o sistema organiza processos, publicações, contatos e clientes, e por onde dados podem entrar e sair, para que um outro sistema possa alimentá-lo depois. Nada aqui deve ser criado, alterado ou excluído.

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui. Se faltar uma informação, anote "faltou: ..." e siga.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga.
- Se se perder, volte à tela inicial do Astrea e continue do passo em que parou.
- Telas: você não entrega imagens. Quando uma tela importar para quem vai construir a integração, registre-a em texto, num bloco que comece com TELA e um número, neste formato: TELA 01 — nome-curto — URL: ... | Título: ... | Caminho de menu: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações: ... Numere em sequência. Não registre tela de login, senha ou token, e não copie nomes de pessoas físicas: em listas de clientes ou contatos, descreva as colunas, não as linhas.
- Bloqueio: se o sistema pedir login, senha ou token, não tente resolver. Escreva BLOQUEIO, diga em que passo estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome do passo em que parou.
- Pare depois de 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto, marcando o que faltou.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco em Markdown, citando as telas pelo número.

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token ou qualquer credencial.
- Somente leitura: não crie processo, cliente, contato, oportunidade, tarefa ou anotação; não altere campo; não clique em "salvar", "enviar", "excluir", "importar", "exportar", "converter em cliente" ou outro botão que grave ou dispare algo. Anote o nome do botão e siga. Telas de importação podem ser abertas só para ler os campos: pare antes de escolher arquivo.
- Não copie dados de pessoas físicas (clientes pessoa física, contatos pessoa física, partes, testemunhas): escreva "pessoa física". Empresas podem ser citadas. Não abra mais do que 2 processos e 2 contatos de exemplo; prefira os que forem pessoa jurídica.
- Uma ação por vez, uma aba só. Nada é enviado a ninguém.

O que mapear, nessa ordem:
1. Menu principal: liste os módulos (processos, clientes, contatos, atendimentos, prospecção ou oportunidades, publicações/intimações, agenda, financeiro, relatórios, configurações) com o nome exato de cada um. Registre a TELA do menu.
2. Cadastro de processo: abra um processo de exemplo e liste os campos (número CNJ, tribunal, vara, classe, partes e papéis, valor, responsável, etiquetas, situação) com o rótulo exato de cada um. Veja se há campo para "origem" ou "como chegou" o caso. Registre a TELA do processo.
3. Publicações e intimações: onde aparecem, como o sistema as capta (há configuração de OAB? de diários? de DJEN? aviso por e-mail?), e como uma publicação vira tarefa ou prazo. Registre a TELA de publicações e a TELA da configuração de captura, se existir.
4. Prospecção, contatos e CRM: existe módulo de prospecção, oportunidades, funil, leads, atendimentos ou CRM (com qualquer um desses nomes)? Se existir, descreva as etapas e os campos. Abra um contato pessoa jurídica de exemplo e liste os campos com o rótulo exato: razão social, CNPJ, telefone (quantos), e-mail (quantos), site, redes sociais (quais), endereço, pessoa de contato e cargo, origem do contato, etiquetas, responsável, observações. Anote quais são obrigatórios. Registre a TELA do cadastro do contato pessoa jurídica.
5. Importação de contatos: há importação de contatos ou clientes por planilha (CSV, Excel)? Que modelo ou colunas pede? Aceita telefone, e-mail e redes? Trata duplicados (por CNPJ ou nome)? Abra a tela só para ler e pare antes de escolher arquivo. Registre a TELA de importação.
6. De contato a cliente: contato e cliente são o mesmo cadastro com um tipo, ou cadastros separados? Há botão ou etapa para transformar um contato em cliente? O que muda (campos, contrato, honorários)? Como um processo é ligado ao cliente?
7. Entrada de dados em lote em geral: procure "importar" (planilha, CSV), "integrações", "API", "webhooks" ou "aplicativos" nas configurações. Anote o que existe, que formatos aceita e que campos pede, sem executar nada. Se houver link para documentação de API, anote o endereço. Registre a TELA de integrações.
8. Saída de dados: procure "exportar" e "relatórios"; anote formatos disponíveis.

RELATÓRIO FINAL:
- Mapa dos módulos e caminhos de menu, com o número da TELA quando houver.
- Tabela de campos do processo: campo | rótulo | obrigatório? | formato.
- Prospecção, contatos e CRM: existe? onde? etapas e como funciona.
- Tabela de campos do contato pessoa jurídica: campo | rótulo | obrigatório? | formato (incluindo telefone, e-mail, site e redes).
- Importação de contatos: formatos, colunas do modelo, tratamento de duplicados.
- De contato a cliente: o caminho, passo a passo, com os nomes dos botões (sem clicar).
- Como entram publicações hoje e o que falta para entrar uma "ação nova contra empresa" vinda de fora.
- Portas de entrada e saída (importação, API, webhook, exportação) com o que cada uma aceita e o endereço da documentação, se houver.
- Mapa técnico para quem vai construir a integração: endereços (URLs) de cada tela; nomes exatos de menus, campos e botões; ordem de cliques; formatos de arquivo aceitos; onde a sessão pede login de novo.
- Dificuldades que você teve navegando.
- Sugestão em 5 linhas: o caminho mais simples para o JUDICIAL entregar as ações novas e as fichas de canais dentro do Astrea (por exemplo, como contato pessoa jurídica com origem "JUDICIAL"), e o que ficaria com a pessoa.
- Lista das telas registradas: número, nome curto e o que mostra.
```

## Prompt 4 · e-SAJ e Diário do TJSP (frentes tributária e cível, se der tempo)

Como usar: aba nova na janela da extensão, sem login. A parte logada só acontece se o Leandro quiser entrar no e-SAJ
com o certificado dele. Troque o número do processo de referência, se houver um do TJSP. Cole, clique em "Permitir" e
deixe a janela sozinha.

```
Você está numa aba do Chrome. Sua tarefa é mapear, somente lendo, como se consulta um processo e uma publicação no e-SAJ do Tribunal de Justiça de São Paulo (https://esaj.tjsp.jus.br) e no Diário da Justiça Eletrônico do TJSP (https://dje.tjsp.jus.br), para um produto que no futuro vai listar execuções fiscais e ações cíveis novas contra empresas. Duas partes: pública, sem login; e logada, só se o advogado quiser entrar.

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga.
- Telas: você não entrega imagens. Quando uma tela importar, registre-a em texto, num bloco que comece com TELA e um número: TELA 01 — nome-curto — URL: ... | Título: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações: ... Numere em sequência. Não registre tela de login, senha, token, certificado ou captcha, e não copie nomes de pessoas físicas.
- Captcha: descreva em palavras (tipo, em que momento aparece), mas não tente resolver nem contornar. Se ele impedir de seguir, trate como bloqueio.
- Bloqueio: se o site pedir login, senha, token, certificado ou captcha para seguir, escreva BLOQUEIO, diga em que passo estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome.
- Pare depois de 45 ações ou 30 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco em Markdown, citando as telas pelo número.

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial.
- Somente leitura. Nada é enviado a ninguém. Não baixe mais de 2 arquivos.
- Dados de empresas podem ser anotados. Dados de pessoas físicas, nunca: escreva "pessoa física".

Parte pública, nessa ordem:
1. Consulta de processos do 1º grau: quais campos de busca existem (número, nome da parte, documento da parte, OAB, outros), se há captcha e em que momento ele aparece, o que a lista de resultados mostra e o que a tela do processo mostra sem login (partes, classe, assunto, vara, valor, movimentações). Quais documentos abrem sem login? Registre a TELA da busca e a TELA do processo.
2. Filtros por classe ou assunto: dá para localizar execuções fiscais ou ações contra empresas por classe, assunto, vara ou período na consulta pública? Se não, anote o que falta.
3. Diário da Justiça Eletrônico (dje.tjsp.jus.br): como se pesquisa (por nome, OAB, data, caderno), em que formato vem (PDF por caderno?), se há busca por texto dentro do diário, e como uma publicação de execução fiscal ou citação de empresa apareceria lá. Registre a TELA da pesquisa.
4. Anote o que é possível fazer sem login e o que exige o advogado.

Parte logada (só se o advogado já estiver logado quando você chegar a este passo; se não estiver, pule):
5. Painel do advogado: intimações, processos, prazos. O que muda em relação à parte pública (documentos, download de autos, dados das partes)?
6. Baixe no máximo 1 documento de exemplo e anote formato e tamanho.

RELATÓRIO FINAL:
- Mapa do fluxo público e, se houver, do fluxo logado, com URLs, nomes exatos de campos e botões, e os números das telas.
- Tabela: o que aparece | sem login | com login.
- Captcha: onde aparece, de que tipo, e o que isso impede um robô de fazer sozinho.
- Diário: formato, pesquisa, e como achar execuções fiscais e citações de empresa.
- Mapa técnico para quem vai construir o robô: endereços de cada tela e o que muda neles; campos e botões exatos; ordem de cliques; como é o download; onde entram captcha, certificado e token; o que dá para fazer sem login.
- Barreiras e dificuldades.
- Sugestão em 5 linhas: o que um robô consegue fazer sem login no TJSP e o que teria de ficar com a pessoa.
- Lista das telas registradas.
```

## Depois da visita

Os relatórios chegam ao dono pela conversa compartilhada (claude.ai da conta do escritório) ou por Google Doc
compartilhado com `integracao@solverone.com.br`. O dono copia para a conta dele e pede ao Leandro para desfazer o
compartilhamento. Os relatórios vão para a sessão de Produto, que os transforma em desenho de integração
(`docs/INTEGRACOES-MERCADO.md`), em skills de navegação das áreas logadas (para o robô e para os prompts especialistas),
no desenho da ficha de canais (`robo/PENDENCIAS.md`) e em pendências. Nenhum dado de pessoa física entra no repositório,
e nenhum dado real de empresa cliente entra no repositório: as fichas reais ficam com o escritório.
