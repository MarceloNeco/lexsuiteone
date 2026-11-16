# Feedback do dono na 0.7.49 publicada (16/Nov/2026, em andamento: o dono ainda está testando; só coletar, nada de código): notebook, filtros e agrupamento por empresa

Contexto: o Leandro (KR Law) trabalha quase sempre no **notebook**; o layout tem de funcionar bem ali (tela de 1280 a 1440 px de
largura, muitas vezes com zoom de 125% no Windows, ou seja, ~1100 a 1200 px úteis). Nada implementado. Causa conferida no código
quando dá; o resto é proposta. A pesquisa (CNPJ dos Correios, notificação na Justiça do Trabalho, contato por empresa, busca de
CNPJ pelo nome) está com o subagente pesquisador e entra aqui quando voltar.

| # | O que o dono viu ou pediu | Causa / situação hoje | Proposta |
|---|---|---|---|
| 1 | No notebook, "Mais filtros", "Filtros salvos", "★ Salvar" e "Limpar filtros" quebram para uma 2ª linha | A 1ª linha ganhou o Tribunal na 0.7.49 e os itens têm largura mínima; a linha quebra (`flex-wrap`) | 1ª linha numa linha só no notebook: busca menor (ícone de lupa com o texto curto "Procurar"), rótulos curtos ("Tribunais", "Situação", "Valor"), "Filtros salvos" virando ícone ★ com contador e menu; "Mais filtros" abre na linha de baixo |
| 2 | Os filtros ocupam quase metade da tela, mesmo na parte fixa ao rolar | Barra fixa com cabeçalho "Filtros da lista", 1ª linha, linha de ordenação e "Selecionar todos" | Ao rolar, barra fixa compacta numa linha (filtros ativos em pílulas + "Filtros (N)"), sem o cabeçalho e sem a linha de ordenação; volta inteira ao subir |
| 3 | O texto da busca "Procure por empresa, nº ou CNPJ" não cabe | Campo encolhe até 140 px | Texto curto "Procurar empresa, nº ou CNPJ" + dica completa no balão; largura mínima maior quando sobra espaço |
| 4 | "Todos os tribunais" ocupa muito; deveria ser "Tribunais" e mostrar quando há filtro (ex.: TRT9) | Rótulo longo do "todos" | "Tribunais" quando todos; "TRT9" quando 1; "Tribunais (3)" quando vários (mesma regra para Situação). **Dono (16/Nov): aprovado; com vários marcados, ao passar o mouse aparece a dica "Tribunais selecionados: TRT9, TRT5, TRT2"** (vale para os outros filtros de várias opções). No celular (fora do foco por enquanto): a mesma lista aparece ao tocar e segurar, ou na primeira linha da lista aberta |
| 5 | **Agrupar, "Últimos 10 processos" mostrou 79 de 560** | Causa: o bloco mostra **todos** os processos do período (69) e soma os 10 anteriores; o alcance só limita os anteriores | O alcance vale para o bloco inteiro: "Últimos 10" = os 10 mais recentes da empresa, do período ou não (na mesma data, desempate pelo número do processo); "até 50 dos últimos 6 meses" idem |
| 6 | **Card "fora dos filtros" quebrado**: caixinha, nome e valor fora do enquadramento dos outros | Causa: a etiqueta é inserida como primeiro filho do cartão e empurra a grade (caixinha à esquerda, valor à direita) | A etiqueta vai na linha de data/tribunal do próprio cartão (pequena, cinza), sem mudar a grade; o cartão continua idêntico aos outros |
| 7 | Processo do 8º dia com "No Diário: últimos 7 dias" tem de ser "anterior" | Hoje "anterior" = antes de hoje − N dias corridos; o período da Lista conta pelo Diário | Usar exatamente o mesmo corte da Lista (data inicial do período carregado) para "anterior" × "fora dos filtros"; teste com o 8º dia |
| 8 | **Chevron** ao lado do nome da empresa para recolher e expandir os processos; com muitas empresas, começar recolhido; manter o alinhamento | — | Chevron (▸/▾ em traço fino) antes do nome; recolhido mostra só o cabeçalho (nome, CNPJ, contas); "Expandir todos / Recolher todos" no alto do agrupamento; padrão recolhido quando há mais de 10 empresas ou o bloco tem mais de 10 processos; a escolha fica lembrada |
| 9 | **Caixinha no cabeçalho da empresa** marca todos os processos dela | — | Caixinha no cabeçalho, na mesma coluna das caixinhas dos cartões; marcado/parcial/desmarcado; funciona recolhido; alimenta a barra de seleção (situação em lote, área logada) |
| 10 | Empresa **sem CNPJ** (ex.: Empresa Brasileira de Correios e Telégrafos, 560 processos): aviso visível e jeito de achar o CNPJ | O Diário não trouxe CNPJ; o agrupamento cai no nome | Triângulo âmbar (sinal de trânsito, traço fino, sem emoji) ao lado do nome, com (?) curto: "O Diário não trouxe o CNPJ destes processos. Eles foram agrupados pelo nome; confira antes de usar os dados." Achar o CNPJ: (a) **dentro do programa**: se outros processos com o mesmo nome têm um CNPJ só, mostrar "CNPJ provável: …" com "Usar este CNPJ nos N processos" (com confirmação; se houver mais de um CNPJ, não sugere); (b) busca externa pelo nome: depende da pesquisa (fonte pública e gratuita por nome) e passa pela Arquitetura |
| 11 | Empresa pública (Correios) provavelmente não é cliente; vai sujar o RADAR | Hoje entra como qualquer empresa | Sugestão no cabeçalho: "Excluir esta empresa" (vai para Empresas excluídas, por área); e, se o dono quiser, opção de esconder empresas públicas/órgãos (lista por natureza jurídica da Receita: 2011 empresa pública, 2038 sociedade de economia mista, 1xxx administração pública) — pergunta ao dono |
| 12 | **Replicar o contato** de um processo para os outros da mesma empresa (mesmo CNPJ), com critério: abertos nos últimos X dias/semanas/meses | Contato é por processo (cadastro da Receita é por CNPJ; o da área logada é por processo) | Ação no cabeçalho da empresa e na barra de seleção: "Copiar contato para os outros processos desta empresa" → escolher a origem (o contato mais recente), o critério (últimos 30, 90, 180 dias ou 12 meses) e confirmar; o copiado fica marcado "copiado de 0001234-…, em 16/NOV" (fonte "copiado", mais fraca que PJe e petição; nunca troca um contato que já existe; desfazer). Regras finais depois da pesquisa (item 3 dela) |
| 13 | (Operação, 15/Nov) o Modo diz "Não incluído na sua licença" sem consultar a licença; para a KR Law (trabalhista e tributário) é falso | Texto fixo da tela | Ler da licença (frentes contratadas) quando a `lex-conta` disser; até lá, texto verdadeiro: "Ainda não disponível no programa" — pergunta ao dono |
| 14 | (Operação, 15/Nov) folha da 0.7.48 não cita os instaladores corrigidos (`ba38b72`) | Folha preenchida antes | Acrescentar a linha na folha da 0.7.48 |
| 15 | **Tour guiado: dá para rolar a tela durante o tour**, e o destaque sai de cima do que está sendo explicado (prints: passo 10 de 13, "Pedido à área logada", com a faixa fixa embaixo; ao rolar, o fundo escurecido e o recorte ficam no lugar e a faixa se move) | O destaque e o balão são posicionados uma vez, em relação à tela; a página continua rolando por baixo | Durante o tour, travar a rolagem da página (cada passo rola sozinho até o alvo e trava); se a janela mudar de tamanho, reposicionar. Ao sair do tour, a rolagem volta. Vale para o AssistONE de todos os apps (módulo comum): pedido também à Arquitetura/RootifyONE |
| 16 | (observação nos prints, sem pedido) No Painel, "Estado da empresa: Sem estado (sem CNPJ) 5.185 · 99%" (TRT9) | O estado vem do cadastro da Receita, que só existe com CNPJ; no TRT9 quase nenhum processo trouxe CNPJ no Diário | Reforça os itens 10 e 12 (CNPJ provável pelo nome dentro do programa); conferir se o TRT9 publica o CNPJ em outro campo da comunicação |

## Perguntas ao dono (vão ao quadro)
- Item 11: esconder empresas públicas e órgãos por padrão, ou só oferecer "Excluir esta empresa"?
- Item 13: texto do Modo até a licença dizer as frentes: "Ainda não disponível no programa"?
- Item 12: critério padrão para copiar o contato (recomendação: últimos 90 dias, só para quem não tem contato)?

## Antes de codar
Protótipo de notebook (1280×720 e 1366×768 com zoom 125%) para os itens 1 a 4, 6, 8 e 9, conferido com o dono; depois "pode codar".

## Pesquisa (pesquisador, 16/Nov; fontes secundárias marcadas; conferir as oficiais antes de usar em texto ao cliente)
- **Correios (ECT)**: CNPJ da matriz 34.028.316/0001-03 (fonte de terceiro e relatórios dos Correios; conferir na Receita); as
  filiais usam a mesma raiz 34028316. Empresa pública federal. Ou seja: com a regra "a chave é o CNPJ" (raiz), os processos dos
  Correios com CNPJ já se juntam; os 560 sem CNPJ caem no nome, e o item 10 (CNPJ provável) resolve dentro do programa.
- **Notificação na Justiça do Trabalho** (CLT art. 841; Súmula 16 do TST; fontes secundárias): vai por correio ao endereço da
  empresa indicado em cada ação (sede ou local de trabalho), não a sócio nem a advogado. Pode mudar de processo para processo
  (endereço, filial e advogado de cada caso).
- **Reaproveitar contato**: o cadastro da Receita é por estabelecimento (matriz ou filial); contato de petição é daquele processo;
  advogado ou escritório da empresa é contato de terceiro; contato de pessoa física (sócio) é dado pessoal (LGPD art. 7º, §§3º e 4º:
  finalidade e necessidade). **Consequência para o item 12**: copiar só o contato da empresa (telefone, e-mail e endereço do
  cadastro, mesma raiz de CNPJ, preferindo o mesmo estabelecimento); nunca copiar contato de advogado/escritório nem de pessoa
  física; marcar "copiado de…" e permitir desfazer.
- **OAB, Provimento 205/2021**: publicidade só informativa; mala direta vedada; contato ativo e não solicitado com empresa
  recém-processada tem risco ético (leitura de fonte secundária). O programa já diz que o uso dos contatos é decisão do compliance do
  escritório; não muda o produto, mas vale lembrar ao dono e ao escritório.
- **Busca de CNPJ pelo nome**: não há consulta oficial gratuita por nome; só os dados abertos da Receita em lote (arquivos grandes,
  atualização mensal ou trimestral) ou o catálogo Conecta gov.br (pode exigir adesão). Por isso a proposta do item 10 começa
  **dentro do programa** (CNPJ que já aparece em outros processos com o mesmo nome); a busca externa fica para a Arquitetura.
