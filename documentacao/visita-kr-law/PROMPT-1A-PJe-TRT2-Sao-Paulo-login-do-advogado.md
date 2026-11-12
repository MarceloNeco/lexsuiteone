# Prompt 1A · PJe do TRT2 (Justiça do Trabalho, São Paulo capital e Grande SP)

Cópia do prompt de [`docs/VISITA-KR-LAW.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/docs/VISITA-KR-LAW.md)
(revisão de 12/Nov/2026), que é a fonte. Precisa do login do advogado.

| | |
|---|---|
| Onde roda | Janela A, primeiro, no perfil "Visita SolverONE" do Chrome do Leandro, extensão Claude in Chrome |
| Login | Leandro, com o certificado digital, quando aparecer `PAUSA PARA LOGIN` |
| Trocar no texto | o número de um processo do escritório no TRT2 |
| Antes de colar | Conversa nova na extensão; modo "Skip all approvals"; modelo Sonnet, se aparecer a escolha |
| Quanto tempo | Até 45 minutos; ela para sozinha e escreve `RELATÓRIO FINAL` |
| Única interação | O login (e, se pedir, confirmar o download de 1 arquivo); depois do login, digitar `continue` |
| Onde fica o resultado | Na conversa, no claude.ai da conta do dono (celular ou computador) |

Para copiar: botão de copiar no canto do bloco cinza abaixo.

## O prompt: Prompt 1A · PJe do TRT2, da página inicial à área logada (na visita, com o login do advogado)

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
