# Visita à KR Law (quinta, 12/Nov/2026): roteiro e prompts do Claude in Chrome

**Revisão de 12/Nov/2026 (dono), a que vale:** programa na versão **0.7.33**. A extensão roda na **conta Claude do dono**,
num perfil novo do Chrome do Leandro ("Visita SolverONE"), apagado no fim do dia; a conta do Leandro não é tocada. Antes de
colar cada prompt, escolher na extensão o modo **"Skip all approvals"** (pular aprovações): ela só para no login e pede
confirmação antes de baixar o único arquivo de cada prompt. Os relatórios ficam no histórico do claude.ai do dono; nada a
compartilhar. Os quatro prompts que precisam do login do advogado também estão separados, um arquivo por sistema, em
[`documentacao/visita-kr-law/`](https://github.com/MarceloNeco/lexsuiteone/tree/main/documentacao/visita-kr-law), com a
lista de links do dia em [`00-LINKS-DA-VISITA.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/documentacao/visita-kr-law/00-LINKS-DA-VISITA.md).
Os critérios da lista agora são por pessoa e por área, e o próprio Leandro os ajusta no programa (passo 6).
**Ajuste de 12/Nov (manhã, dono):** em vez do perfil novo, uma **janela anônima** do Chrome do Leandro com a conta Claude do
dono. Antes, em `chrome://extensions` → Claude → Detalhes, ligar "Permitir no modo anônimo". Ao fechar todas as janelas
anônimas, sessões e logins somem (não há perfil para apagar). Se a extensão não aparecer na janela anônima, use o perfil
novo "Visita SolverONE", como descrito abaixo. A 0.7.33 está publicada: o botão de baixar do site já entrega essa versão.

Complementa `robo/ROTEIRO-INSTALACAO.md` (instalação do robô). Aqui ficam os prompts para usar no **Claude in Chrome**
no computador do Leandro, com o consentimento dele, para aprender como os sistemas funcionam e planejar as integrações.
Nada aqui produz efeito nos sistemas: é leitura e anotação. Histórico das revisões anteriores (vale a de 12/Nov, acima): **09/Nov/2026 (noite)**: programa na versão 0.7.16
(tudo o que a visita precisa: planilha por frente, cópias de segurança, armazenamento, "Trazer dados da área logada"), termos de uso 1.1 com aceite, autorização do Leandro antes de qualquer prompt na área logada e
formato padronizado de resposta que o RADAR lê (seção "Resposta para o RADAR"). Os prompts foram escritos para o Claude
in Chrome, mas servem em qualquer extensão de IA de navegador. Versão anterior: 08/Nov/2026 (foco na ficha de canais; prompts
escritos para rodar **sozinhos**, no Sonnet, na conta do escritório, sem ninguém acompanhando; o relatório volta para a
SolverONE pela conversa compartilhada). Cópia para o celular: Google Doc na pasta "VISITA KR LAW (quinta 12-Nov)" do
Drive do dono. O GitHub é a fonte.

**Revisão de 10/Nov (pedido do dono), com o que aprendemos estudando os pacotes de skills jurídicas:** cada prompt agora
começa identificando em que sistema está (PJe de 1º ou 2º grau, e-SAJ, eproc, Projudi, Diário do tribunal, DJEN), porque o
mesmo processo tem várias portas oficiais; ganhou a regra "só o que leu na tela nesta sessão" e uma conferência antes do
relatório; a Parte B do Prompt 2 só cita norma aberta na fonte oficial; o Prompt 1 anota onde aparece quem assinou as
decisões (sem copiar o nome); e há um Prompt 5, público e sem login, que testa a ideia do raio-x da vara e do juiz (LexRay).
Segunda revisão de 10/Nov (dono): **na visita, só o que exige login**, e cada prompt começa na página inicial do site, mapeia
a jornada pública até a tela de entrada, escreve `PAUSA PARA LOGIN`, espera o Leandro entrar e continua: 1A (PJe TRT2),
1B (PJe TRT15), 3 (Astrea) e 4B (TJSP logado). **Em casa, antes da visita, tudo o que é público:** 2 (ficha de canais),
4A (TJSP e DJEN, parte pública) e 5 (LexRay).

| Prompt | Onde roda | Login |
|---|---|---|
| 1A · PJe do TRT2 | Visita, janela A | Leandro (certificado) |
| 1B · PJe do TRT15 | Visita, janela A, depois do 1A | Leandro (certificado) |
| 3 · Astrea | Visita, janela B, ao mesmo tempo que o 1A | Leandro |
| 4B · TJSP área logada | Visita, janela B, depois do 3, se o Leandro quiser | Leandro (certificado) |
| 2 · Ficha de canais | Em casa | Nenhum |
| 4A · TJSP e DJEN, parte pública | Em casa | Nenhum |
| 5 · LexRay | Em casa | Nenhum |

TRT2 e TRT15 são sites e logins separados, mas o sistema é o mesmo (PJe da Justiça do Trabalho); a vara não muda a
mecânica. Os outros TRTs também usam o PJe, com endereço próprio e às vezes outra versão: TRT2 e TRT15 bastam como amostra.

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

Os prompts 1A, 1B, 3 e 4B rodam na área logada do Leandro, com a credencial dele. Antes do primeiro, ele confirma, em voz alta
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
cola no RADAR ("Trazer dados da área logada", grupo "Área logada", desde a 0.7.21). O RADAR lê esse bloco sem IA, confere linha por linha
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

- **Conta e modelo (12/Nov).** A extensão Claude in Chrome roda no computador do Leandro, num **perfil novo do Chrome**
  ("Visita SolverONE") com a **conta Claude do dono** (plano pago; a extensão exige). A conta do Leandro não é tocada, e o
  perfil é apagado no fim do dia. O certificado digital do Leandro funciona em qualquer perfil do Chrome (fica no Windows
  ou no token). Modelo **Sonnet**, se a extensão mostrar a escolha. Os prompts são longos e dizem tudo: o que ver, em
  que ordem, quando parar e como relatar. Se a conta do dono não entrar, use a conta do escritório no Chrome do Leandro
  (ver "Relatório e como chega ao dono").
- **Modo de aprovação (12/Nov).** Antes de colar cada prompt, no menu da caixa de conversa da extensão, escolha
  **"Skip all approvals"** (pular aprovações). Os prompts só leem. Mesmo nesse modo a extensão pede confirmação antes de
  baixar arquivo (um por prompt) e antes de ações sensíveis: quem estiver perto clica. Use esse modo só nessas janelas,
  nos sites do tribunal e do Astrea; nesse perfil não se abre e-mail nem Drive, porque um site malicioso poderia tentar
  dar ordens à extensão.
- **Sem supervisão.** A extensão trabalha sozinha enquanto o Leandro testa o robô e o dono cuida de outras coisas. Ela
  para em dois casos: na tela de entrada do sistema escreve `PAUSA PARA LOGIN` (o Leandro entra e digita "continue"); e
  se o site pedir token, certificado ou captcha no meio do caminho escreve `BLOQUEIO`, entrega o que já tem e espera. Quem voltar à tela resolve o login (só o Leandro) e digita
  "continue".
- **Janelas próprias.** A extensão roda em janelas do Chrome só para ela (A e B, uma por prompt), com a aba do sistema. Ninguém usa essa janela
  enquanto ela trabalha; o robô e o resto ficam em outra janela. Se num site ela ainda pedir permissão, escolha
  "Always allow actions on this site" antes de sair de perto.
- **Um prompt por conversa.** Cada prompt é colado inteiro numa conversa nova da extensão. Não misture dois prompts.
- **Sem prints.** A extensão não salva arquivos nem entrega imagens. No lugar de prints ela escreve "telas" em texto,
  num formato fixo (endereço, título, menus, campos com rótulos, botões, o que acontece ao clicar). Para construir um
  robô isso vale mais do que uma imagem.
- **Relatório e como chega ao dono.** Ao fim, a extensão escreve `RELATÓRIO FINAL` num bloco só, em Markdown. Com a
  conta do dono, cada conversa fica no histórico dele e abre no claude.ai, no celular ou no computador (a documentação da
  extensão diz que as sessões do painel aparecem no histórico, 12/Nov): nada a compartilhar. **Testar isso no começo da
  visita** com uma conversa curta. Se for a conta do escritório: selecionar o texto do painel da extensão (Ctrl+A, Ctrl+C)
  e colar num e-mail para `integracao@solverone.com.br` ou num Google Doc; "Compartilhar" uma conversa da extensão não
  aparece na documentação.
- **Pode compartilhar porque não tem nada sensível.** Nenhuma tela de login entra no relatório, nenhuma credencial é
  vista e nomes de pessoas físicas não são copiados. Os relatórios ainda assim não entram no repositório nem no site.

## O mesmo processo tem várias portas (leia antes)

Um processo aparece em mais de um lugar oficial, e cada lugar mostra uma parte. Os prompts pedem para a extensão dizer
primeiro em qual está e anotar as diferenças. Os nomes abaixo são os mais comuns; o que vale é o que aparecer na tela.

| Porta | O que costuma mostrar | Login |
|---|---|---|
| Sistema do tribunal, painel do advogado (PJe nos TRTs, TRFs e em vários TJs; e-SAJ, eproc ou Projudi em outros) | Autos completos, documentos, expedientes, prazos | Advogado, com certificado ou token |
| Consulta pública do mesmo sistema | Capa do processo e movimentações; poucos documentos | Não (às vezes captcha) |
| DJEN, Diário de Justiça Eletrônico Nacional (comunica.pje.jus.br) | Intimações e decisões publicadas, de todos os tribunais | Não |
| Diário próprio do tribunal (ex.: DJE do TJSP) | Publicações do tribunal, em cadernos | Não |
| Domicílio Judicial Eletrônico | Citações e intimações enviadas a empresas | A empresa ou quem a representa |
| Sistema do escritório (Astrea) | O que o escritório cadastrou ou capturou | Advogado |

Qual porta vale para contar prazo e quando cada uma recebe a publicação é pergunta para o Leandro, não para a extensão:
ela só anota os avisos que o próprio site mostrar.

## Ordem do dia (quinta 12/Nov)

Links para abrir no celular, todos sem login: este arquivo; instalação em
[`robo/ROTEIRO-INSTALACAO.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/robo/ROTEIRO-INSTALACAO.md);
manual em https://judicial.solverone.com.br/manual.html; pacote em https://judicial.solverone.com.br/downloads/Instalar-LexSuiteONE.zip.
Lista completa (GitHub, site e pastas do Drive): `documentacao/visita-kr-law/00-LINKS-DA-VISITA.md`.
No computador do Leandro, abrir os prompts pelo GitHub (sem login), um arquivo por sistema em `documentacao/visita-kr-law/`,
e copiar pelo botão de copiar do bloco.

**Antes, em casa (até quarta).** Ensaio da instalação no PC do dono com a segunda conta Google, `DIAGNOSTICO.bat` e uma
rodada real. Rodar no Claude in Chrome, com a conta do dono, os prompts sem login: 2 (três empresas da lista do RADAR),
4A e 5. Confirmar com o Leandro: certificado digital em mãos para o PJe; em que pasta fica a planilha
(no computador ou numa pasta do Google Drive; não é preciso compartilhar com a SolverONE); o texto dos termos 1.1.
Conferir que a conta Claude do dono entra e tem plano pago (a extensão roda nela, num perfil novo do Chrome do Leandro,
"Visita SolverONE", apagado no fim). O notebook do dono não recebe login nem certificado de ninguém. Combinar um
processo de referência no TRT2 e um no TRT15 (do próprio escritório) e, se houver, um no TJSP.

1. **Chegada (15 min).** Explicar o que vai acontecer e pedir o OK: instalar o robô e até quatro observações só de
   leitura com a extensão, que trabalham sozinhas e param só para o Leandro fazer o login. Criar o perfil "Visita
   SolverONE" no Chrome dele, instalar a extensão, entrar com a conta Claude do dono e abrir **duas janelas** só para a
   extensão (A e B; modo "Skip all approvals", modelo Sonnet). Testar com uma conversa curta e conferir se ela aparece no
   claude.ai do dono (no celular) e se a extensão aceita trabalhar nas duas janelas ao mesmo tempo (se não aceitar, rode
   um prompt depois do outro).
2. **Instalar o robô, versão 0.7.33 (45 a 60 min).** Seguir o `ROTEIRO-INSTALACAO.md`: baixar o pacote do site, `DIAGNOSTICO.bat`,
   configurar, escolher a pasta da planilha (no computador ou no Drive do escritório; **não** se compartilha com a
   SolverONE), agendar a rodada diária e iniciar a primeira rodada agora (demora: deixar rodando). Instalar no
   computador que fica ligado nos horários das leituras (o do escritório ou o de casa: perguntar ao Leandro qual).
   **Conferir o armazenamento** (menu ☰ → Configurações → Armazenamento): espaço livre no disco (o ideal é mais de 10 GB), onde
   ficam `LexSuiteONE - Trabalhista.xlsx` e a pasta `Cópias de segurança`, e se o aviso de disco aparece. Anotar
   quantos GB livres o computador tem. A pasta escolhida aqui não precisa mudar depois: as frentes novas (tributário,
   cível, empresarial) ganham a própria planilha na mesma pasta, sozinhas. As estatísticas dos meses anteriores
   (Painel → Sazonalidade) rodam à noite, depois da leitura automática: na visita não é preciso buscá-las; se alguém
   clicar em "Buscar estatísticas", use "Continuar à noite".
3. **Janela A: Prompt 1A (PJe do TRT2). Janela B: Prompt 3 (Astrea).** Ao mesmo tempo. Em cada janela, conversa nova,
   cola o prompt (o modo já está em "Skip all approvals"). A extensão abre a página inicial sozinha, mapeia o caminho e escreve `PAUSA PARA LOGIN`:
   o Leandro faz o login naquela aba (certificado no PJe) e digita "continue". Se depois ela escrever `BLOQUEIO` (token,
   nova autenticação), só o Leandro resolve e digita "continue".
4. **Janela A: Prompt 1B (PJe do TRT15)**, igual ao 1A, numa conversa nova. **Janela B, se o Leandro quiser: Prompt 4B
   (TJSP logado).** **No fim, feche o ciclo dentro do RADAR:** copie o bloco
   `RESPOSTA PARA O RADAR v1` que a extensão devolveu e cole no RADAR (menu ☰, "Área logada" → "Trazer dados da área logada"); confira
   no cartão do processo se o valor, a data e os contatos apareceram, com a fonte. Depois teste o caminho do próprio
   programa: num cartão de um processo novo da lista, clique em "Buscar na área logada" (o pedido vai copiado, só com o
   que falta), cole na extensão, e cole a resposta de volta. Anote o que deu certo e o que travou: é a base da próxima
   versão da área logada.
5. **Conversa sobre o LexRay, enquanto as janelas trabalham.** Levar o resultado do Prompt 5 (rodado em casa) e
   perguntar: como ele descobre quem vai julgar (titular, substituto, divisão por final de número, mutirões), se no
   recurso o relator fica com o caso, e o que mais queria saber de um juiz antes de redigir.
6. **Lista do dia pronta.** Mostrar na tela local e na planilha; validar 3 ou 4 itens com o Leandro (é ação nova? é
   empresa? a comarca interessa?). O próprio Leandro ajusta os critérios no programa (menu ☰ → Configurações → Critérios
   da lista), área por área (Trabalhista e Tributário), com as empresas excluídas; valem para ele, naquele computador. Levar a ficha de canais do Prompt 2 (rodado
   em casa) e perguntar se o formato serve ao compliance dele.
7. **Fechamento (15 min).** Conferir: rodada agendada, Leandro sabe abrir a tela e a planilha, sabe o que fazer se
   aparecer o aviso "a planilha está ficando grande" (clicar em "Limpar a planilha (com cópia)"),
   manual e `judicial@solverone.com.br` como contato. Relatórios: conferir no celular que as conversas aparecem no
   claude.ai do dono (se usou a conta do escritório, copiar cada `RELATÓRIO FINAL` num e-mail para `integracao@`). Sair
   da conta Claude na extensão e apagar o perfil "Visita SolverONE" do Chrome (Chrome → ícone do perfil → Gerenciar
   perfis → Excluir); os PDFs baixados ficam no computador do Leandro. Anotar feedbacks e
   dizer o que vem na 0.8.

Depois: relatórios e feedbacks vão para a sessão de Produto; dúvidas de instalação e e-mail, para a sessão de Operação.

## Regras que valem para todos os prompts

- **Nunca pedir, digitar, copiar, fotografar ou anotar senha, token, código de certificado ou qualquer credencial.** A
  extensão vai até a tela de entrada, lista as formas de login sem tocar em nada, escreve `PAUSA PARA LOGIN` e para; o
  advogado faz o login sozinho e digita "continue". Se o site
  pedir login, captcha, token ou certificado no meio do caminho, a extensão **para, escreve BLOQUEIO e espera o
  advogado**. Nenhuma tela de login, senha, token, certificado ou captcha entra no relatório.
- Somente leitura: não cadastrar, peticionar, assinar, marcar como lido, alterar campo, nem clicar em "enviar",
  "assinar", "protocolar", "excluir", "importar", "converter" ou similares. Se um botão parecer gravar algo, não clica e
  anota o nome.
- Nada é enviado a ninguém: nenhuma ligação, e-mail, mensagem, comentário, convite, curtida ou formulário.
- Uma ação por vez, sem pressa, uma aba só. Dados de pessoas físicas seguem a tabela acima: "pessoa física" no lugar do
  nome. Empresas (razão social, CNPJ e os canais da empresa) podem ser citadas.
- Ignorar processos de outros clientes que apareçam na tela; abrir só o de referência.
- **Só o que leu na tela nesta sessão.** A extensão não deduz, não completa e não cita de memória: o que não viu vira
  "não encontrei" (ou `nao_consta` na resposta para o RADAR). Antes do `RELATÓRIO FINAL`, ela confere a própria resposta
  por uma lista curta (padrão que os melhores pacotes de skills jurídicas usam).
- **Nome de juiz, desembargador ou servidor não é copiado:** vira "magistrado 1", "magistrado 2" (o mesmo número para a
  mesma pessoa), com o cargo. Serve para saber se dá para montar o raio-x por juiz sem guardar nomes agora.
- Modelo da extensão: Sonnet. Cada prompt termina com `RELATÓRIO FINAL`, que é colado na sessão de Produto para virar
  desenho de integração e skills de navegação.

## Prompt 1A · PJe do TRT2, da página inicial à área logada (na visita, com o login do advogado)

Como usar: na janela da extensão, abra uma conversa nova e cole o texto abaixo (troque o número do processo). A extensão abre sozinha a página inicial do TRT2, mapeia o caminho até a tela de login e escreve `PAUSA PARA LOGIN`. Aí o Leandro faz o login com o certificado nessa mesma aba e escreve "continue". Modo da extensão: "Skip all approvals"; ela só pede confirmação no download. Pode rodar em paralelo com o Prompt 3 (Astrea), cada um na sua janela.

```
Comece abrindo, nesta aba, a página inicial do Tribunal Regional do Trabalho da 2ª Região: https://www.trt2.jus.br. Sua tarefa tem duas partes. Parte A, sem login: mapear a jornada pública, da página inicial até a tela de entrada do PJe. Parte B, depois que o advogado fizer o login: mapear, somente lendo, como se consulta um processo e como se baixam os documentos dele, e anotar onde aparecem os dados de contato da empresa ré (endereço, e-mail e telefone), para que um robô e prompts especialistas possam fazer isso depois. Processo de referência: 0000000-00.0000.5.02.0000 (troque pelo número real).

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui. Se faltar uma informação, anote "faltou: ..." e siga.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga para o próximo passo.
- Se se perder, volte ao painel inicial do advogado (na Parte A, à página inicial do tribunal) e continue do passo em que parou.
- Telas: você não entrega imagens. Quando uma tela importar para quem vai construir o robô, registre-a em texto, num bloco que comece com TELA e um número, neste formato: TELA 01 — nome-curto — URL: ... | Título: ... | Caminho de menu: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações (paginação, tempo de carga, avisos): ... Numere em sequência. Não registre tela de login, senha, token, certificado ou captcha, e não copie nomes de pessoas físicas.
- Bloqueio: se o site pedir login, senha, token, certificado ou captcha, não tente resolver nem contornar. Escreva BLOQUEIO, diga o que foi pedido e em que passo você estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome do passo em que parou.
- Pare depois de 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto, marcando o que faltou.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco de texto em Markdown, citando as telas pelo número (por exemplo: ver TELA 03).

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial.
- Somente leitura: não cadastre, não peticione, não assine, não marque como lido, não altere nenhum campo, não clique em "enviar", "assinar", "protocolar", "excluir" ou similares. Se um botão parecer que grava algo, não clique e anote o nome dele.
- Não abra várias abas do PJe ao mesmo tempo. Se o sistema mostrar erro ou lentidão, espere e tente uma única vez.
- Na Parte A, navegue só pelo site do tribunal e do PJe; na Parte B, só pelo PJe. Nada é enviado a ninguém.
- Dados da empresa ré (razão social, CNPJ, endereço, e-mail, telefone) podem ser anotados. Dados do reclamante e de qualquer outra pessoa física (testemunhas, advogados, prepostos), nunca: escreva "pessoa física" no lugar. A qualificação da petição inicial traz os dados do reclamante logo ao lado dos da empresa: anote só a parte da empresa.
- Se a tela do advogado mostrar processos de outros clientes, ignore-os: só abra o processo de referência.
- Só vale o que você leu na tela nesta sessão. Não deduza, não complete e não cite nada de memória: o que não viu é "não encontrei".
- Nome de juiz, desembargador ou servidor não se copia: escreva "magistrado 1", "magistrado 2" (o mesmo número para a mesma pessoa) e o cargo.

Parte A · Jornada pública, da página inicial até o login (sem login), nessa ordem:
A1. Na página inicial do tribunal, registre a TELA (endereço final, se houve redirecionamento, título, menus principais).
A2. Encontre o caminho até o PJe (links como "PJe", "Processo Judicial Eletrônico", "Acesso ao PJe", "Advogados"). Anote cada clique, o texto exato do link, o endereço de cada página e se abriu nova aba. Se houver entradas separadas para 1º e 2º grau, anote as duas e siga pela do 1º grau.
A3. Na tela de entrada do PJe, liste as formas de login que aparecem (certificado digital, login único ou PDPJ, gov.br, usuário e senha, token), com o texto exato dos botões. Não clique em nenhuma e não toque nos campos. Registre a TELA só com os nomes das opções, nunca com dados digitados.
A4. Anote se há consulta pública de processos sem login e onde fica o link (não precisa usar).
A5. Escreva exatamente: PAUSA PARA LOGIN — Leandro, faça o login nesta aba. Quando o painel do advogado aparecer, escreva continue. Depois disso, não faça nada até alguém escrever "continue". Não leia nem registre o que for digitado na tela de login.

Parte B · Depois do login (somente leitura), nessa ordem:
0. Identificar onde você está. Anote o nome do sistema e a versão que a tela mostrar (PJe, e-SAJ, eproc, Projudi ou outro), o tribunal, se é 1º ou 2º grau e se é o painel do advogado ou uma consulta pública. Se não for o PJe, siga o mesmo roteiro com os nomes que aparecerem e anote cada diferença.
1. Localizar a consulta. A partir do painel do advogado, encontre a função de consulta de processo por número (menu, atalho ou campo de busca). Anote: caminho de menu, URL da tela, nome do campo e formato que o número precisa ter. Registre a TELA do painel e a TELA da consulta.
2. Abrir o processo de referência. Anote a URL que abre e se ela contém um identificador interno (um número que não é o número CNJ).
3. Mapear os dados do processo. Na tela do processo, liste os blocos que existem e quais campos cada um mostra. Procure especialmente: classe, assunto(s), data de distribuição (ou autuação), valor da causa, órgão julgador (vara), grau e fase (conhecimento, execução, recurso), partes do polo passivo com CNPJ e endereço, advogados das partes, situação atual, última movimentação. Para cada campo, anote o rótulo exato e em qual aba ou seção ele está. Veja se o cadastro da parte ré (clicando no nome dela, se o PJe permitir só visualizar) mostra endereço, e-mail ou telefone. Registre a TELA do processo e a TELA do cadastro da parte ré.
4. Mapear as movimentações e os documentos. Encontre a lista de movimentações e a lista de documentos (petição inicial, notificação ou citação inicial, decisões, atas). Anote como a lista é organizada (ordem, paginação, filtros) e que tipos de documento aparecem. Registre a TELA da lista de documentos.
5. Baixar. Procure as opções de download: documento individual, "autos completos" ou "download do processo" (PDF único ou vários). Baixe só a petição inicial, para a pasta padrão de downloads do Chrome (a extensão pede confirmação a quem estiver perto). Para os autos completos, não baixe: anote o nome do botão, o endereço e o formato oferecido. Anote: nome do botão, se é um link com endereço (qual) ou um botão sem endereço, se abre nova aba, formato, tamanho aproximado, tempo e se pediu confirmação. Não baixe mais de 1 arquivo. Registre a TELA de download.
6. Contatos da empresa ré nos autos. Abra no visualizador do PJe (sem baixar outro arquivo):
   a) A petição inicial. Ache a qualificação da reclamada (normalmente no primeiro parágrafo, depois dos dados do reclamante, com expressões como "em face de", "pessoa jurídica de direito privado", "inscrita no CNPJ", "com sede na", "endereço eletrônico", "e-mail", "telefone"). Anote em que página e em que trecho aparecem o endereço, o e-mail e o telefone da empresa, e qual expressão vem antes de cada um. Não registre essa página como TELA: ela tem dados do reclamante; anote só a posição e as expressões.
   b) A notificação ou citação inicial da ré (aba de expedientes, intimações ou documentos; anote o nome exato). Anote para qual endereço ou meio ela foi expedida (Correios, oficial de justiça, Domicílio Judicial Eletrônico, e-mail) e se há aviso de recebimento ou certidão dizendo se a empresa foi encontrada naquele endereço.
   c) Para cada documento: o texto é selecionável (PDF de texto) ou é imagem escaneada? Os dados estão sempre no mesmo lugar e com as mesmas expressões?
7. Intimações e publicações. No painel do advogado, veja onde chegam as intimações e os expedientes (nome da aba, filtros, prazos, como se marca ciência, sem marcar nada). Registre a TELA de intimações.
8. Verificar o que pediu intervenção humana. Liste cada momento em que o site exigiu captcha, token, certificado ou nova autenticação, e quanto tempo a sessão durou sem pedir login de novo.
9. Quem decide (para um futuro raio-x da vara e do juiz). Nas decisões, despachos e sentenças do processo, veja se aparece quem assinou e onde (rodapé de assinatura eletrônica, cabeçalho, campo próprio na capa do processo). Para cada documento: tipo, data, "magistrado N" e cargo (juiz titular, juiz substituto, relator, outro). Veja também se a capa do processo ou a vara indicam o juiz responsável. Não copie nomes.

Antes de entregar, confira a sua resposta e corrija o que falhar:
- Cada valor da RESPOSTA PARA O RADAR tem documento e página que você leu nesta sessão. Nada foi deduzido.
- Não há dado do reclamante, de testemunha, de advogado da outra parte, CPF nem nome de magistrado.
- O número do processo está no formato 0000000-00.0000.0.00.0000; valores sem "R$" e com vírgula nos centavos (150000,00); datas como 2026-11-12.
- O que você não leu está como nao_consta (o processo não traz) ou tentar_depois (problema técnico), nunca em branco.

RELATÓRIO FINAL, neste formato:
- Jornada pública: da página inicial ao login, passos com endereços, textos dos links e as formas de login oferecidas.
- Sistema: nome, versão, tribunal, grau, painel do advogado ou consulta pública.
- Mapa do fluxo: passos numerados, cada um com "tela → ação → resultado", incluindo URLs e nomes exatos de menus, botões e campos, e o número da TELA quando houver.
- Tabela de campos: campo | rótulo na tela | aba ou seção | exemplo (mascarado se for pessoa física).
- Downloads: o que baixou, como (link com endereço, botão, nova aba), formato, tamanho e onde ficou.
- Contatos da ré nos autos: documento | dado (endereço, e-mail ou telefone) | aparece? | página e trecho | expressão que vem antes | texto ou imagem | valor encontrado (só da empresa).
- Extração repetível: para cada dado, "sim", "parcial" ou "não", com o motivo (mesmo lugar e mesmas expressões em todo processo? texto selecionável? depende de alguém ter digitado certo?). Diga também se esses dados só aparecem com o login do advogado.
- Intimações: onde chegam e como funcionam.
- Quem decide: documento | data | magistrado N | cargo | onde aparece a assinatura. Diga quantos magistrados diferentes assinaram e se a capa ou a vara indicam o juiz responsável.
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
```

## Prompt 1B · PJe do TRT15, da página inicial à área logada (na visita, com o login do advogado)

Como usar: igual ao 1A, com o processo de referência do TRT15. É o mesmo sistema (PJe da Justiça do Trabalho) num site e num login separados; o relatório mostra o que muda entre os dois. Os outros 22 TRTs usam o mesmo sistema, com endereço próprio e, às vezes, outra versão: por isso TRT2 e TRT15 bastam como amostra.

```
Comece abrindo, nesta aba, a página inicial do Tribunal Regional do Trabalho da 15ª Região: https://www.trt15.jus.br. Sua tarefa tem duas partes. Parte A, sem login: mapear a jornada pública, da página inicial até a tela de entrada do PJe. Parte B, depois que o advogado fizer o login: mapear, somente lendo, como se consulta um processo e como se baixam os documentos dele, e anotar onde aparecem os dados de contato da empresa ré (endereço, e-mail e telefone), para que um robô e prompts especialistas possam fazer isso depois. Processo de referência: 0000000-00.0000.5.15.0000 (troque pelo número real).

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui. Se faltar uma informação, anote "faltou: ..." e siga.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga para o próximo passo.
- Se se perder, volte ao painel inicial do advogado (na Parte A, à página inicial do tribunal) e continue do passo em que parou.
- Telas: você não entrega imagens. Quando uma tela importar para quem vai construir o robô, registre-a em texto, num bloco que comece com TELA e um número, neste formato: TELA 01 — nome-curto — URL: ... | Título: ... | Caminho de menu: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações (paginação, tempo de carga, avisos): ... Numere em sequência. Não registre tela de login, senha, token, certificado ou captcha, e não copie nomes de pessoas físicas.
- Bloqueio: se o site pedir login, senha, token, certificado ou captcha, não tente resolver nem contornar. Escreva BLOQUEIO, diga o que foi pedido e em que passo você estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome do passo em que parou.
- Pare depois de 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto, marcando o que faltou.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco de texto em Markdown, citando as telas pelo número (por exemplo: ver TELA 03).

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial.
- Somente leitura: não cadastre, não peticione, não assine, não marque como lido, não altere nenhum campo, não clique em "enviar", "assinar", "protocolar", "excluir" ou similares. Se um botão parecer que grava algo, não clique e anote o nome dele.
- Não abra várias abas do PJe ao mesmo tempo. Se o sistema mostrar erro ou lentidão, espere e tente uma única vez.
- Na Parte A, navegue só pelo site do tribunal e do PJe; na Parte B, só pelo PJe. Nada é enviado a ninguém.
- Dados da empresa ré (razão social, CNPJ, endereço, e-mail, telefone) podem ser anotados. Dados do reclamante e de qualquer outra pessoa física (testemunhas, advogados, prepostos), nunca: escreva "pessoa física" no lugar. A qualificação da petição inicial traz os dados do reclamante logo ao lado dos da empresa: anote só a parte da empresa.
- Se a tela do advogado mostrar processos de outros clientes, ignore-os: só abra o processo de referência.
- Só vale o que você leu na tela nesta sessão. Não deduza, não complete e não cite nada de memória: o que não viu é "não encontrei".
- Nome de juiz, desembargador ou servidor não se copia: escreva "magistrado 1", "magistrado 2" (o mesmo número para a mesma pessoa) e o cargo.

Parte A · Jornada pública, da página inicial até o login (sem login), nessa ordem:
A1. Na página inicial do tribunal, registre a TELA (endereço final, se houve redirecionamento, título, menus principais).
A2. Encontre o caminho até o PJe (links como "PJe", "Processo Judicial Eletrônico", "Acesso ao PJe", "Advogados"). Anote cada clique, o texto exato do link, o endereço de cada página e se abriu nova aba. Se houver entradas separadas para 1º e 2º grau, anote as duas e siga pela do 1º grau.
A3. Na tela de entrada do PJe, liste as formas de login que aparecem (certificado digital, login único ou PDPJ, gov.br, usuário e senha, token), com o texto exato dos botões. Não clique em nenhuma e não toque nos campos. Registre a TELA só com os nomes das opções, nunca com dados digitados.
A4. Anote se há consulta pública de processos sem login e onde fica o link (não precisa usar).
A5. Escreva exatamente: PAUSA PARA LOGIN — Leandro, faça o login nesta aba. Quando o painel do advogado aparecer, escreva continue. Depois disso, não faça nada até alguém escrever "continue". Não leia nem registre o que for digitado na tela de login.

Parte B · Depois do login (somente leitura), nessa ordem:
0. Identificar onde você está. Anote o nome do sistema e a versão que a tela mostrar (PJe, e-SAJ, eproc, Projudi ou outro), o tribunal, se é 1º ou 2º grau e se é o painel do advogado ou uma consulta pública. Se não for o PJe, siga o mesmo roteiro com os nomes que aparecerem e anote cada diferença.
1. Localizar a consulta. A partir do painel do advogado, encontre a função de consulta de processo por número (menu, atalho ou campo de busca). Anote: caminho de menu, URL da tela, nome do campo e formato que o número precisa ter. Registre a TELA do painel e a TELA da consulta.
2. Abrir o processo de referência. Anote a URL que abre e se ela contém um identificador interno (um número que não é o número CNJ).
3. Mapear os dados do processo. Na tela do processo, liste os blocos que existem e quais campos cada um mostra. Procure especialmente: classe, assunto(s), data de distribuição (ou autuação), valor da causa, órgão julgador (vara), grau e fase (conhecimento, execução, recurso), partes do polo passivo com CNPJ e endereço, advogados das partes, situação atual, última movimentação. Para cada campo, anote o rótulo exato e em qual aba ou seção ele está. Veja se o cadastro da parte ré (clicando no nome dela, se o PJe permitir só visualizar) mostra endereço, e-mail ou telefone. Registre a TELA do processo e a TELA do cadastro da parte ré.
4. Mapear as movimentações e os documentos. Encontre a lista de movimentações e a lista de documentos (petição inicial, notificação ou citação inicial, decisões, atas). Anote como a lista é organizada (ordem, paginação, filtros) e que tipos de documento aparecem. Registre a TELA da lista de documentos.
5. Baixar. Procure as opções de download: documento individual, "autos completos" ou "download do processo" (PDF único ou vários). Baixe só a petição inicial, para a pasta padrão de downloads do Chrome (a extensão pede confirmação a quem estiver perto). Para os autos completos, não baixe: anote o nome do botão, o endereço e o formato oferecido. Anote: nome do botão, se é um link com endereço (qual) ou um botão sem endereço, se abre nova aba, formato, tamanho aproximado, tempo e se pediu confirmação. Não baixe mais de 1 arquivo. Registre a TELA de download.
6. Contatos da empresa ré nos autos. Abra no visualizador do PJe (sem baixar outro arquivo):
   a) A petição inicial. Ache a qualificação da reclamada (normalmente no primeiro parágrafo, depois dos dados do reclamante, com expressões como "em face de", "pessoa jurídica de direito privado", "inscrita no CNPJ", "com sede na", "endereço eletrônico", "e-mail", "telefone"). Anote em que página e em que trecho aparecem o endereço, o e-mail e o telefone da empresa, e qual expressão vem antes de cada um. Não registre essa página como TELA: ela tem dados do reclamante; anote só a posição e as expressões.
   b) A notificação ou citação inicial da ré (aba de expedientes, intimações ou documentos; anote o nome exato). Anote para qual endereço ou meio ela foi expedida (Correios, oficial de justiça, Domicílio Judicial Eletrônico, e-mail) e se há aviso de recebimento ou certidão dizendo se a empresa foi encontrada naquele endereço.
   c) Para cada documento: o texto é selecionável (PDF de texto) ou é imagem escaneada? Os dados estão sempre no mesmo lugar e com as mesmas expressões?
7. Intimações e publicações. No painel do advogado, veja onde chegam as intimações e os expedientes (nome da aba, filtros, prazos, como se marca ciência, sem marcar nada). Registre a TELA de intimações.
8. Verificar o que pediu intervenção humana. Liste cada momento em que o site exigiu captcha, token, certificado ou nova autenticação, e quanto tempo a sessão durou sem pedir login de novo.
9. Quem decide (para um futuro raio-x da vara e do juiz). Nas decisões, despachos e sentenças do processo, veja se aparece quem assinou e onde (rodapé de assinatura eletrônica, cabeçalho, campo próprio na capa do processo). Para cada documento: tipo, data, "magistrado N" e cargo (juiz titular, juiz substituto, relator, outro). Veja também se a capa do processo ou a vara indicam o juiz responsável. Não copie nomes.

Antes de entregar, confira a sua resposta e corrija o que falhar:
- Cada valor da RESPOSTA PARA O RADAR tem documento e página que você leu nesta sessão. Nada foi deduzido.
- Não há dado do reclamante, de testemunha, de advogado da outra parte, CPF nem nome de magistrado.
- O número do processo está no formato 0000000-00.0000.0.00.0000; valores sem "R$" e com vírgula nos centavos (150000,00); datas como 2026-11-12.
- O que você não leu está como nao_consta (o processo não traz) ou tentar_depois (problema técnico), nunca em branco.

RELATÓRIO FINAL, neste formato:
- Jornada pública: da página inicial ao login, passos com endereços, textos dos links e as formas de login oferecidas.
- Sistema: nome, versão, tribunal, grau, painel do advogado ou consulta pública.
- Mapa do fluxo: passos numerados, cada um com "tela → ação → resultado", incluindo URLs e nomes exatos de menus, botões e campos, e o número da TELA quando houver.
- Tabela de campos: campo | rótulo na tela | aba ou seção | exemplo (mascarado se for pessoa física).
- Downloads: o que baixou, como (link com endereço, botão, nova aba), formato, tamanho e onde ficou.
- Contatos da ré nos autos: documento | dado (endereço, e-mail ou telefone) | aparece? | página e trecho | expressão que vem antes | texto ou imagem | valor encontrado (só da empresa).
- Extração repetível: para cada dado, "sim", "parcial" ou "não", com o motivo (mesmo lugar e mesmas expressões em todo processo? texto selecionável? depende de alguém ter digitado certo?). Diga também se esses dados só aparecem com o login do advogado.
- Intimações: onde chegam e como funcionam.
- Quem decide: documento | data | magistrado N | cargo | onde aparece a assinatura. Diga quantos magistrados diferentes assinaram e se a capa ou a vara indicam o juiz responsável.
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
```

## Prompt 2 · Ficha de canais da empresa processada (em casa, sem login, para o compliance)

Como usar: aba nova no Chrome, sem login em nada. Roda em casa, no computador do dono, com a conta dele. Troque as três
empresas de exemplo por empresas reais da lista do JUDICIAL (razão social, CNPJ e cidade; se a linha do JUDICIAL já
trouxer telefone, e-mail e sócios, cole junto, que a extensão usa como ponto de partida e confere). Nenhuma mensagem é
enviada a ninguém. O uso do que for encontrado é decisão do compliance do escritório.

```
Preciso de uma "ficha de canais" de cada empresa abaixo, feita só em fontes públicas, para o time de compliance de um escritório de advocacia analisar e decidir se e como agir. Você não envia nada a ninguém: não liga, não manda e-mail nem mensagem, não preenche formulário, não segue perfis, não comenta, não cria conta e não burla nenhum login.

Empresas (razão social, CNPJ, cidade, e o que o JUDICIAL já trouxe, se houver). O CNPJ pode ter letras (formato novo, de julho de 2026, como 12.ABC.345/01DE-35): copie e procure como está.
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

Parte B, contexto para o compliance (curta): diga o que não é permitido ou não é recomendável pelas regras da OAB sobre publicidade e captação de clientela (Provimento 205/2021 e Código de Ética e Disciplina), e o que a LGPD exige para usar dados de contato de empresa e de sócios. Só cite o que você abrir nesta sessão numa fonte oficial: o Provimento 205/2021 em https://www.oab.org.br/leisnormas/legislacao/provimentos/205-2021?provimentos=True, o Código de Ética no site da OAB, a LGPD (Lei 13.709/2018) no site do Planalto e as orientações da ANPD no gov.br. Para cada ponto, copie o trecho curto que o sustenta e o endereço. Se a página não abrir, escreva "não conferido" e não preencha de memória: número de artigo errado aqui custa caro. Se der tempo, na Biblioteca de Anúncios da Meta (facebook.com/ads/library), país Brasil, pesquise "defesa trabalhista para empresas" e "sua empresa foi processada" e anote os 3 anúncios mais relevantes: anunciante, mensagem resumida, chamada para ação e link.

Antes de entregar, confira e corrija o que falhar:
- Toda linha da ficha tem fonte, data da consulta e grau de confiança.
- Nenhum contato de pessoa entrou sem estar publicado pela própria empresa, com o lugar anotado.
- Nada sobre o reclamante ou outra pessoa física.
- Na Parte B, toda regra citada tem trecho e endereço abertos nesta sessão; o resto está como "não conferido".

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

## Prompt 3 · Astrea, da página inicial à área logada (na visita, com o login do advogado)

Como usar: na janela da extensão, abra uma conversa nova e cole o texto. A extensão abre a página inicial do Astrea, mapeia o caminho até a tela de entrada e escreve `PAUSA PARA LOGIN`; o Leandro faz o login nessa aba e escreve "continue". Modo da extensão: "Skip all approvals". Roda em paralelo com o Prompt 1A, cada um na sua janela. Serve para desenhar como o JUDICIAL vai entregar as ações novas e as fichas de canais dentro do sistema que o escritório já usa.

```
Comece abrindo, nesta aba, a página inicial do Astrea, o sistema de gestão do escritório: https://www.astrea.net.br (se redirecionar, anote para onde). Parte A, sem login: mapeie o caminho até a tela de entrada. Parte B, depois que o advogado fizer o login: mapeie, somente lendo, como o sistema organiza processos, publicações, contatos e clientes, e por onde dados podem entrar e sair, para que um outro sistema possa alimentá-lo depois. Nada aqui deve ser criado, alterado ou excluído.

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

Parte A · Da página inicial até o login (sem login):
A1. Registre a TELA da página inicial e o caminho até a tela de entrada do sistema (links "Entrar", "Login", "Acessar"), com endereços.
A2. Liste as formas de entrada que aparecem (e-mail e senha, Google, outra), com o texto exato dos botões, sem clicar e sem tocar nos campos.
A3. Escreva exatamente: PAUSA PARA LOGIN — Leandro, faça o login nesta aba. Quando a tela inicial do Astrea aparecer, escreva continue. Depois disso, não faça nada até alguém escrever "continue". Não leia nem registre o que for digitado na tela de login.

Parte B · Depois do login (somente leitura), nessa ordem:
1. Menu principal: liste os módulos (processos, clientes, contatos, atendimentos, prospecção ou oportunidades, publicações/intimações, agenda, financeiro, relatórios, configurações) com o nome exato de cada um. Registre a TELA do menu.
2. Cadastro de processo: abra um processo de exemplo e liste os campos (número CNJ, tribunal, vara, juiz ou relator, classe, partes e papéis, valor, responsável, etiquetas, situação) com o rótulo exato de cada um. Veja se há campo para "origem" ou "como chegou" o caso. Registre a TELA do processo.
3. Publicações e intimações: onde aparecem, como o sistema as capta (há configuração de OAB? de diários? de DJEN? do Domicílio Judicial Eletrônico? aviso por e-mail?), se cada publicação mostra de qual diário ou fonte veio, e como uma publicação vira tarefa ou prazo. Registre a TELA de publicações e a TELA da configuração de captura, se existir.
4. Prospecção, contatos e CRM: existe módulo de prospecção, oportunidades, funil, leads, atendimentos ou CRM (com qualquer um desses nomes)? Se existir, descreva as etapas e os campos. Abra um contato pessoa jurídica de exemplo e liste os campos com o rótulo exato: razão social, CNPJ, telefone (quantos), e-mail (quantos), site, redes sociais (quais), endereço, pessoa de contato e cargo, origem do contato, etiquetas, responsável, observações. Anote quais são obrigatórios. Registre a TELA do cadastro do contato pessoa jurídica.
5. Importação de contatos: há importação de contatos ou clientes por planilha (CSV, Excel)? Que modelo ou colunas pede? Aceita telefone, e-mail e redes? Trata duplicados (por CNPJ ou nome)? Abra a tela só para ler e pare antes de escolher arquivo. Registre a TELA de importação.
6. De contato a cliente: contato e cliente são o mesmo cadastro com um tipo, ou cadastros separados? Há botão ou etapa para transformar um contato em cliente? O que muda (campos, contrato, honorários)? Como um processo é ligado ao cliente?
7. Entrada de dados em lote em geral: procure "importar" (planilha, CSV), "integrações", "API", "webhooks" ou "aplicativos" nas configurações. Anote o que existe, que formatos aceita e que campos pede, sem executar nada. Se houver link para documentação de API, anote o endereço. Registre a TELA de integrações.
8. Saída de dados: procure "exportar" e "relatórios"; anote formatos disponíveis.

Antes de entregar, confira e corrija o que falhar: nada foi criado, alterado ou importado; nenhum nome de pessoa física ou de magistrado foi copiado; cada campo listado tem o rótulo exato que você leu na tela; o que você não achou está como "não encontrei".

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

## Prompt 4A · TJSP e DJEN, parte pública (em casa, sem login)

Como usar: em casa, aba nova, sem login em nada. Cole numa conversa nova da extensão. Serve para as frentes tributária e cível e já deixa pronto o mapa público antes da visita.

```
Comece abrindo, nesta aba, a página inicial do Tribunal de Justiça de São Paulo: https://www.tjsp.jus.br. Sua tarefa é mapear, somente lendo e sem login, como se chega e como se consulta um processo e uma publicação no e-SAJ (https://esaj.tjsp.jus.br), no Diário da Justiça Eletrônico do TJSP (https://dje.tjsp.jus.br) e no Diário de Justiça Eletrônico Nacional, DJEN (https://comunica.pje.jus.br), para um produto que no futuro vai listar execuções fiscais e ações cíveis novas contra empresas. Não há processo de referência: escolha como exemplo a primeira execução fiscal contra empresa (pessoa jurídica) que aparecer no DJE do TJSP de um dia útil recente, e use esse mesmo número no e-SAJ e no DJEN.

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
- Somente leitura. Nada é enviado a ninguém. Não baixe mais de 1 arquivo.
- Dados de empresas podem ser anotados. Dados de pessoas físicas, nunca: escreva "pessoa física". Nome de magistrado vira "magistrado 1", "magistrado 2".
- Só vale o que você leu na tela nesta sessão. Não deduza qual diário vale para prazo: anote só o aviso que o próprio site mostrar, com o endereço.

O que fazer, nessa ordem:
0. Na página inicial do TJSP, registre a TELA e o caminho até o e-SAJ e até o DJE (textos exatos dos links e endereços). Veja também se o site do tribunal avisa que o processo ou a consulta mudou de sistema (por exemplo, para o eproc) ou que as publicações passaram ao DJEN. Anote o aviso com o endereço e siga a mesma lógica no sistema indicado.
1. Consulta de processos do 1º grau: quais campos de busca existem (número, nome da parte, documento da parte, OAB, outros), se há captcha e em que momento ele aparece, o que a lista de resultados mostra e o que a tela do processo mostra sem login (partes, classe, assunto, vara, valor, movimentações). Quais documentos abrem sem login? Registre a TELA da busca e a TELA do processo.
2. Filtros por classe ou assunto: dá para localizar execuções fiscais ou ações contra empresas por classe, assunto, vara ou período na consulta pública? Se não, anote o que falta.
3. Diário da Justiça Eletrônico (dje.tjsp.jus.br): como se pesquisa (por nome, OAB, data, caderno), em que formato vem (PDF por caderno?), se há busca por texto dentro do diário, e como uma publicação de execução fiscal ou citação de empresa apareceria lá. Registre a TELA da pesquisa.
4. DJEN (https://comunica.pje.jus.br), sem login: pesquise o processo de exemplo que você escolheu. A mesma publicação aparece no DJE do TJSP e no DJEN? Em que datas? O texto é igual? Algum dos dois mostra quem assinou? Anote as diferenças.
5. Anote o que é possível fazer sem login e o que parece exigir o advogado (o Prompt 4B, na visita, confere a parte logada).

Antes de entregar, confira: nenhum nome de pessoa física ou de magistrado; cada afirmação sobre o site tem a TELA ou o endereço; o que não viu está como "não encontrei".

RELATÓRIO FINAL:
- Mapa do fluxo público, com URLs, nomes exatos de campos e botões, e os números das telas.
- Tabela: o que aparece | e-SAJ sem login | DJE do TJSP | DJEN.
- Avisos de mudança de sistema ou de diário que o site mostrou, com o endereço.
- Captcha: onde aparece, de que tipo, e o que isso impede um robô de fazer sozinho.
- Diário: formato, pesquisa, e como achar execuções fiscais e citações de empresa.
- Mapa técnico para quem vai construir o robô: endereços de cada tela e o que muda neles; campos e botões exatos; ordem de cliques; como é o download; onde entram captcha, certificado e token; o que dá para fazer sem login.
- Barreiras e dificuldades.
- Sugestão em 5 linhas: o que um robô consegue fazer sem login no TJSP e no DJEN, e o que deve ficar para a parte logada.
- Lista das telas registradas.
```

## Prompt 4B · TJSP, da página inicial à área logada (na visita, se o Leandro quiser)

Como usar: na visita, depois do 1A, numa janela da extensão. A extensão abre a página inicial do TJSP, mapeia o caminho até a entrada do advogado e escreve `PAUSA PARA LOGIN`; o Leandro faz o login com o certificado e escreve "continue". Modo da extensão: "Skip all approvals". O DJEN não tem área logada: fica todo no 4A.

```
Comece abrindo, nesta aba, a página inicial do Tribunal de Justiça de São Paulo: https://www.tjsp.jus.br. Sua tarefa tem duas partes. Parte A, sem login: mapear o caminho da página inicial até a entrada do advogado no e-SAJ (Portal de Serviços) ou no sistema que o tribunal indicar. Parte B, depois que o advogado fizer o login: mapear, somente lendo, o painel do advogado (intimações, processos, prazos) e o que muda em relação à consulta pública. Processo de referência do TJSP: [número], se o escritório tiver um; se não, use um da lista de intimações dele, sem abrir mais de 2.

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
- Somente leitura. Nada é enviado a ninguém. Não baixe mais de 1 arquivo.
- Dados de empresas podem ser anotados. Dados de pessoas físicas, nunca: escreva "pessoa física". Nome de magistrado vira "magistrado 1", "magistrado 2".
- Só vale o que você leu na tela nesta sessão. Não deduza qual diário vale para prazo: anote só o aviso que o próprio site mostrar, com o endereço.

Parte A · Da página inicial até o login (sem login):
A1. Registre a TELA da página inicial e o caminho até a entrada do advogado (links como "e-SAJ", "Portal de Serviços", "Peticionamento", "Advogados"), com textos exatos e endereços. Se o site avisar que a área do advogado mudou de sistema (por exemplo, para o eproc), siga o caminho indicado e anote o aviso.
A2. Liste as formas de login que aparecem (certificado digital, usuário e senha, outra), com o texto exato dos botões, sem clicar e sem tocar nos campos.
A3. Escreva exatamente: PAUSA PARA LOGIN — Leandro, faça o login nesta aba. Quando o painel do advogado aparecer, escreva continue. Depois disso, não faça nada até alguém escrever "continue". Não leia nem registre o que for digitado na tela de login.

Parte B · Depois do login (somente leitura), nessa ordem:
B1. Painel do advogado: onde ficam intimações, processos e prazos; nomes exatos de menus e abas. Registre as TELAS.
B2. Abra o processo de referência: o que aparece a mais do que na consulta pública (documentos, download dos autos, dados das partes, quem assinou as decisões, como "magistrado N")?
B3. Baixe no máximo 1 documento de exemplo e anote formato, tamanho e como foi o download.
B4. Intimações: como chegam, se mostram de qual diário vieram e como o prazo aparece. Não marque ciência de nada.

Antes de entregar, confira: nada foi assinado, peticionado ou marcado como lido; nenhum nome de pessoa física ou de magistrado; cada afirmação tem a TELA ou o endereço; o que não viu está como "não encontrei".

RELATÓRIO FINAL:
- Jornada pública: da página inicial ao login, com endereços e as formas de login oferecidas.
- Mapa do fluxo logado, com URLs, nomes exatos de campos e botões, e os números das telas.
- Tabela: o que aparece | consulta pública | painel do advogado.
- Download: como é, formato, tamanho.
- Mapa técnico para quem vai construir o robô: endereços, ordem de cliques, onde entram certificado e token, quanto tempo a sessão durou sem pedir login de novo.
- Barreiras e dificuldades.
- Sugestão em 5 linhas: o que só dá para fazer com o advogado logado e o que um robô poderia fazer com ele logado.
- Lista das telas registradas.
```

## Prompt 5 · LexRay: dá para fazer o raio-x da vara e do juiz? (em casa, sem login)

Como usar: em casa, aba nova, sem login em nada, com a conta do dono. Vem pronto para a 1ª Vara do Trabalho de São Paulo (TRT2);
para testar outra vara, troque o nome. Testa duas perguntas do produto LexRay: as
decisões publicadas mostram quem assinou? Uma vara é decidida sempre pelo mesmo juiz ou por vários? E quais leis e súmulas
ela mais cita? Nada de nome de pessoa física nem de magistrado: só "magistrado 1", "magistrado 2".

```
Você está numa aba do Chrome, sem login. Sua tarefa é testar, somente lendo e só em fonte pública, se as decisões publicadas de uma vara permitem descrever o perfil de quem julga ali, para um produto de jurimetria descritiva (sem ranking e sem prever resultado). Fonte principal: o Diário de Justiça Eletrônico Nacional, DJEN (https://comunica.pje.jus.br). Tribunal: TRT2. Vara: 1ª Vara do Trabalho de São Paulo (se o nome no DJEN for um pouco diferente, use o que aparecer). Não há processo de referência.

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui. Se faltar uma informação, anote "faltou: ..." e siga.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga.
- Telas: registre em texto as que importarem para quem vai construir o robô: TELA 01 — nome-curto — URL: ... | Filtros e campos (rótulo exato): ... | Botões e links: ... | Paginação: ... | Observações: ...
- Captcha ou login: não resolva nem contorne. Escreva BLOQUEIO, entregue o RELATÓRIO FINAL com o que já tem e espere.
- Pare depois de 30 publicações lidas, 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto.

Regras que não se negociam:
- Só leitura, só fonte pública. Nada é enviado a ninguém.
- Nunca copie nome de parte que seja pessoa física (reclamante, testemunha), de advogado, de servidor ou de magistrado. Magistrado vira "magistrado 1", "magistrado 2" (o mesmo número para a mesma pessoa em todo o relatório), com o cargo que aparecer (juiz titular, juiz substituto, outro). Empresas podem ser citadas.
- Só vale o que você leu nesta sessão. Não deduza o desfecho: se a publicação não diz, escreva "não diz".
- Leis, súmulas e orientações: anote como aparecem no texto (ex.: "art. 477 da CLT", "Súmula 331 do TST"). Não corrija, não complete e não explique: só conte.

O que fazer, nessa ordem:
1. No DJEN, descubra como filtrar por tribunal, por órgão (vara), por período e por número de processo. Anote os filtros que existem e os rótulos exatos. Registre a TELA da pesquisa.
2. Pesquise as publicações da vara nos últimos 60 dias. Se não houver filtro por vara, pesquise pelo processo de referência e anote que o filtro não existe.
3. Leia até 30 publicações que sejam decisão, despacho ou sentença (ignore editais e listas). Para cada uma, anote: data | tipo (sentença, decisão, despacho, ata, outro) | assunto, se aparecer | aparece quem assinou? onde? | magistrado N e cargo | desfecho, se for sentença (procedente, parcialmente procedente, improcedente, acordo homologado, extinção, não diz) | leis, súmulas e orientações citadas.
4. Escolha um processo dessa vara que tenha sentença entre as publicações lidas e liste todas as publicações dele no DJEN, na ordem, com o mesmo formato do item 3.

Antes de entregar, confira e corrija o que falhar: nenhum nome de pessoa física, advogado, servidor ou magistrado; cada linha tem data e tipo lidos na publicação; desfecho só quando a publicação diz.

RELATÓRIO FINAL:
- Viabilidade em 5 linhas: as publicações mostram quem assinou (sempre, às vezes, nunca)? Dá para saber o desfecho pelo texto? Dá para filtrar por vara?
- Quem assina na vara: magistrado N | cargo | quantas publicações | percentual. Diga se um magistrado concentra a maior parte ou se há rodízio.
- Tabela das publicações lidas (o item 3), sem nomes.
- Normas mais citadas: norma como aparece no texto | quantas vezes | em quantas publicações.
- Desfechos das sentenças lidas: tipo | quantas.
- Mapa técnico para quem vai construir o robô: endereços, filtros, paginação, formato do texto (HTML, PDF), limites e bloqueios que apareceram.
- Lista das telas registradas.
```

## Depois da visita

Os relatórios ficam nas conversas da extensão, no claude.ai do dono (ou chegam por e-mail a `integracao@solverone.com.br`,
se a conta do escritório foi usada). Os relatórios vão para a sessão de Produto, que os transforma em desenho de integração
(`docs/INTEGRACOES-MERCADO.md`), em skills de navegação das áreas logadas (para o robô e para os prompts especialistas),
no desenho da ficha de canais (`robo/PENDENCIAS.md`) e em pendências. Nenhum dado de pessoa física entra no repositório,
e nenhum dado real de empresa cliente entra no repositório: as fichas reais ficam com o escritório.
