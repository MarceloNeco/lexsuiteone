# Feedback do teste do dono — 09/Nov/2026 (continuação de FEEDBACK-TESTE-2026-11-08.md, itens 42 em diante)

Teste na instalação antiga do dono (pasta C:\LexSuiteONE, planilha na pasta escolhida na época), TRT15, 2.874 ações no
período. Quem faz: **P** = Produto (tela, planilha, textos), **A** = Arquitetura (banco, nuvem, regra de negócio,
desenho antes do código), **O** = Operação (publicar). Nada aqui foi implementado ainda: espera o "pode" do dono.

## Respostas diretas (o que já é assim hoje)

- **"A lista perdeu o TRT2 quando li o TRT15."** Não perdeu: tudo o que foi lido fica no banco do computador
  (`lexsuite.db`, 365 dias). A tela e a aba Radar da planilha mostram só os **tribunais marcados agora** e o
  **período escolhido** (último dia, 3, 7, 15, 30). Desmarcou o TRT2, ele sai da tela e da planilha, mas continua
  guardado. O item 42 resolve a confusão.
- **"Não capturado" no cartão do print.** Nesse caso o motivo é outro: o Diário não trouxe o CNPJ da empresa, então o
  RADAR não teve como consultar a Receita, e todos os campos da empresa ficaram vazios. Não é sigilo. Hoje há três
  motivos diferentes com o mesmo texto; o item 53 separa cada um.
- **"Se alguém mexer na planilha, o robô se perde?"** Não. A aba Radar é regravada inteira a cada leitura: o que a
  pessoa digitar ali some na próxima leitura, mas não confunde o robô. O robô só **lê** Preferências e Exclusões, e um
  erro nelas cai no padrão com aviso. O item 49 deixa isso claro na própria planilha.
- **Pasta antiga.** A instalação feita antes da 0.7.10 continua com a pasta da época (de propósito, para não mudar o
  lugar da planilha de quem já usa). Instalação nova usa "RADAR JUDICIAL - planilha". Dá para trocar em Configuração.
- **"Lista para abrir no celular".** É uma cópia da tela, gravada junto da planilha a cada leitura. Abre em qualquer
  aparelho pelo Drive, sem o programa. Ela **não** se atualiza sozinha entre uma leitura e outra, e o que se digita
  nela (valor, status) fica só naquele aparelho. Item 58: decidir se fica, com outro nome, ou se sai.

## Itens

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 42 | A lista e a planilha não acumulam; mudar o tribunal "apaga" o anterior | **Arquivo**: tudo o que já foi lido, de todos os tribunais, pesquisável, com o mesmo cartão. A Lista continua sendo "o que é novo e ainda não tratei". Na planilha, uma aba Arquivo acumulada | A desenha (o que guarda e por quanto tempo), P faz a tela e a planilha | 0.8 |
| 43 | Ações em lote: marcar os selecionados ou todos os do filtro como lido, tratado ou descartado | Caixa de seleção no cartão e "Marcar todos os N filtrados"; os marcados saem da Lista e vão para o Arquivo (nunca apagam). O status hoje fica no navegador: passa para o banco do computador, para valer na planilha e em outra tela | A (status no banco local), P | 0.8 |
| 44 | Arquivo com o espaço ocupado e limpeza do que é velho, sem perder as estatísticas | Tela Arquivo mostra o tamanho e oferece "Limpar o que tem mais de N meses" (apaga o dado bruto e mantém os totais) | A (regra de retenção), P | 0.8 |
| 45 | **Estatísticas** persistentes: totais por dia, vara, tribunal, porte e valor guardados para sempre; gráfico de linhas de ações novas × encerradas, que se mexe ao filtrar | Tabela de totais diários no banco (pequena, nunca apagada). "Encerradas": o Diário de distribuição não informa encerramento; exige acompanhar cada processo (DataJud ou intimações). Começar com "novas por dia" e deixar "encerradas" para quando houver fonte | A (fonte do encerramento e tabela), P (gráfico) | 0.8 |
| 46 | Menu ☰ como nos outros apps, com Radar, Arquivo, Estatísticas, Configuração; não gostou da Configuração no alto | Menu ☰ à esquerda: Painel, Lista, Arquivo, Estatísticas, Configuração, Manual, Perfil. A engrenagem sai do alto | P | 0.7.13 |
| 47 | Um cartão por linha (duas colunas atrapalham a ordem por valor) | Volta a uma coluna em qualquer largura | P | 0.7.13 |
| 48 | Texto cortado na ficha aberta (print: número do processo, valor, "não capturado") | Defeito do layout em duas colunas; com uma coluna e a ficha ajustada, nada corta | P | 0.7.13 |
| 49 | Planilha protegida: só olhar e filtrar; aviso em vermelho na primeira linha; "gerar uma cópia para uso" | Primeira linha vermelha: "Esta planilha é regravada pelo RADAR. Para trabalhar, use 'Gerar uma cópia' no programa". Aba Radar protegida **sem senha**, com filtro e ordenação liberados (cautela, não trava). Botão "Gerar uma cópia" na tela (cópia com data, na mesma pasta). **Macro não**: arquivo com macro não roda no Google Planilhas e o Windows bloqueia | P | 0.7.13 |
| 50 | Aviso antes de abrir a planilha, com "Entendi" e "não mostrar de novo"; reaparece em outra máquina, usuário ou perfil | Janela antes de abrir. O "não mostrar de novo" fica guardado no navegador daquele usuário do Windows; outro computador, outro usuário ou outro perfil vê de novo | P | 0.7.13 |
| 51 | Agnóstico de frente: trabalhista, tributário, cível, empresarial | Cada ação ganha a marca da frente; filtro "Frente" e cor discreta no cartão. Uma lista só com a marca (não seções separadas), para comparar e ordenar tudo junto | A (campo no banco), P | 0.7.13 (marca) + 0.8 |
| 52 | Selo de contato no próprio cartão (verde = encontrado, vermelho = falta) e filtro "Com contato" | Selo no cartão: "Contato: telefone e e-mail" (verde) ou "Sem contato" (vermelho), com o motivo ao passar o mouse. Filtro "Só com contato" | P | 0.7.13 |
| 53 | Saber **por que** está "não capturado" | Três textos: "Sem CNPJ no Diário" (não deu para consultar), "Não consta na Receita" (consultou, a empresa não informou) e "Só na área logada do PJe" (valor da causa, data de ajuizamento) | P | 0.7.13 |
| 54 | Valor mínimo com faixas e valor personalizado | Botão de valor vira uma lista: Todos, 10 mil, 50 mil, 100 mil, 300 mil, 500 mil, 1 milhão, "Outro valor..." | P | 0.7.13 |
| 55 | Ordenação avançada (1º critério e 2º critério) | "Ordenar por" e "depois por" (data, valor, porte, empresa, vara) | P | 0.7.13 |
| 56 | Busca por parte, número do processo, vara, CNPJ | Caixa de busca no alto da Lista, sem acento e sem pontuação, em todos os campos | P | 0.7.13 |
| 57 | Animação dos gráficos ao filtrar | Barras e colunas deslizam até o novo tamanho (sem biblioteca) | P | 0.7.13 |
| 58 | "Lista para abrir no celular": o que é? | Ver acima. Proposta: renomear para "Retrato da última leitura (abre no celular)" ou deixar de gravar. Decisão do dono | P | 0.7.13 |
| 59 | Completar os dados não públicos com o login do advogado (Claude in Chrome ou integração), escolhendo um grupo de processos | Liga aos itens 40 e 41. Pesquisa feita em `PESQUISA-ACESSO-PJE-2026-11-09.md` (resumo: não há caminho oficial simples; contato vem do CNPJ, não do processo; há bloqueio por volume); o desenho fica com a Arquitetura; os prompts do Claude in Chrome (`docs/VISITA-KR-LAW.md`) a Produto revisa com o resultado | A, P, pesquisa | depois da pesquisa |
| 60 | Gráficos também na planilha | Aba "Estatísticas" com a tabela de totais (funciona no Excel e no Google Planilhas). Gráfico desenhado dentro do arquivo fica para depois: dá muito trabalho só com a biblioteca padrão e o Google Planilhas converte mal | P | 0.8 |

## Segunda rodada do mesmo dia (situação do processo e ações em lote)

Reforço do dono: leu o TRT2, depois o TRT15, e o TRT2 sumiu da tela **e da planilha**. Confirma o item 42: a planilha
hoje é o espelho da tela (tribunais marcados e período escolhido); o dado continua no banco, mas o escritório não o vê.
O Arquivo resolve.

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 61 | O status fica escondido e cortado na ficha; tem que aparecer no cartão, com filtro e mudança em lote | O campo passa a se chamar **Situação** e vira uma etiqueta no próprio cartão. Filtro "Situação". Muda pelo cartão (um clique) ou em lote | P (tela); A (guardar no banco, item 43) | 0.7.13 (etiqueta e filtro) + 0.8 (banco) |
| 62 | Rever as situações: o que é novo, visto, em contato, descartado, arquivado, "em análise" | Proposta: **Nova** (ainda não aberta) → **Vista** (abriu a ficha; automático) → **Em análise** (buscando contato, valor, decidindo) → **Em contato** (o escritório já falou com a empresa) → **Arquivada** (sai da Lista e vai para o Arquivo, com motivo: sem interesse, já é cliente, fora do perfil, outro). "Descartado" vira "Arquivada: sem interesse". Decisão do dono | P, dono decide | 0.7.13 |
| 63 | Ações em lote: arquivar, mudar a situação, completar dados pendentes; selecionar todos da lista | Caixa em cada cartão e "Selecionar todos os N desta lista (com os filtros)". Barra de ações em lote, que aparece só quando há seleção, com o nome **"Com os selecionados:"** e os botões "Mudar a situação", "Arquivar", "Preparar busca na área logada" | P; A (item 43) | 0.8 (precisa da situação no banco) |
| 64 | Mostrar quantos processos serão afetados antes de aplicar em lote | O botão diz o número ("Arquivar 1.512 processos") e, acima de 20, pede confirmação escrita na janela ("Arquivar 1.512 processos? Eles saem da Lista e continuam no Arquivo"). Dá para desfazer logo depois | P | 0.8 |
| 65 | Pílulas de filtro com aparência diferente das ações em lote | Filtros: pílulas claras com contorno (como hoje). Ações em lote: barra própria em azul-marinho com botões em latão, presa ao rodapé da tela enquanto houver seleção. Ninguém confunde "filtrar" com "aplicar" | P | 0.8 |
| 66 | Filtro de valor: personalizado e **"valor não informado"** | A lista do item 54 ganha "Sem valor informado" (as que dependem do PJe) ao lado de Todos, 10 mil ... 1 milhão e "Outro valor..." | P | 0.7.13 |
| 67 | Termos que o advogado entende, nada técnico | "Situação" (não status), "Com os selecionados" (não "ações em lote"), "Arquivar" (não "descartar"), "Sem valor informado", "Contato encontrado" e "Sem contato" | P | 0.7.13 |

## Terceira rodada (filtros e endereço)

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 68 | Um botão para desligar todos os filtros de uma vez | "Limpar filtros (N)" ao lado dos filtros, aparece só quando há algum ligado e mostra quantos | P | 0.7.13 |
| 69 | Filtros salvos (preferidos) | "Salvar estes filtros" com um nome ("TRT15 acima de 300 mil, indústria"); os salvos viram atalhos acima da lista. Na 0.7.13 ficam neste computador; na 0.8, no banco, para valer em outra tela | P | 0.7.13 |
| 70 | Endereço da parte passiva (local de trabalho; nunca a casa de ninguém) | O cadastro do CNPJ, que o RADAR já consulta, traz o endereço da **empresa** (rua, número, bairro, CEP); hoje só a cidade é guardada. Passa a aparecer na ficha e na planilha. Endereço de **sócio** não existe em cadastro público e é dado de pessoa física: não entra. Cuidado: no MEI e no empresário individual o endereço da empresa costuma ser a casa do dono. Proposta: nesses casos mostrar só cidade e UF. Decisão do dono | P (tela e planilha); A (regra do MEI, junto do pedido sobre MEI) | 0.7.13 |
| 71 | Em todos os filtros, a opção "não informado", como no valor | Cada filtro ganha "Não informado" quando houver ações sem aquele dado (porte, setor, estado, CNPJ, contato, valor), com o motivo na dica (sem CNPJ no Diário, não consta na Receita, só na área logada) | P | 0.7.13 |

## Quarta rodada (teste da 0.7.13, 09/Nov madrugada)

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 72 | "Abrir a planilha" deve abrir só para leitura, para o advogado não travar a gravação do robô | O botão abre o Excel em modo **somente leitura** (Excel com `/r`, achado pelo registro do Windows); o arquivo ganha também a marca "recomendado abrir como somente leitura", que o Excel pergunta ao abrir por fora. Filtrar e ordenar continuam funcionando. Para trabalhar na planilha: "Gerar uma cópia" (botão no programa) | P | 0.7.14 |
| 73 | Se a planilha estiver aberta e travada, gravar sozinho quando fechar | Depois de uma leitura com a planilha travada, o programa tenta de novo a cada 2 minutos (até 2 horas) e grava sozinho quando ela for fechada; a tela troca o aviso por "Planilha atualizada" | P | 0.7.14 |
| 74 | Macros na planilha (cópia, aviso) | Macro não: arquivo com macro não abre no Google Planilhas e o Windows bloqueia. No lugar: primeira linha vermelha de aviso na aba Radar, proteção sem senha (filtro e ordenação liberados) e o botão "Gerar uma cópia" no programa (item 49) | P | 0.7.14 |
| 75 | Log e Exclusões "estranhos" na planilha | Exclusões é a lista de empresas que o escritório não quer ver (clientes, por exemplo), não o Arquivo; ganha a explicação na primeira linha. A aba Log passa a se chamar "Histórico de leituras" e vai para o fim. O Arquivo vira aba própria na 0.7.14 | P | 0.7.14 |
| 76 | Aviso estranho "TRT2, TRT15 tribunal(is): O Diário de hoje..." e cortado | Texto novo: "TRT2 e TRT15: o Diário de hoje só sai às 3h; li até 06/11." em linha que quebra, sem cortar | P | 0.7.14 |
| 77 | Situação (Novo, Visto...) aparecer na página e na planilha | Hoje fica escondida dentro da ficha e só neste navegador. Na 0.7.14: etiqueta no cartão, filtro, mudança em lote, coluna "Situação" na planilha | P | 0.7.14 |

## Quinta rodada (gráficos no tempo e abas)

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 78 | Gráfico ao longo do tempo (ações novas por dia, depois as encerradas), alimentado pelas estatísticas que vão se acumulando, no Painel | Gráfico de linha "ações novas por dia" (por mês acima de 60 dias) lendo a tabela de estatísticas que nunca se apaga; muda com os filtros (tribunal, vara, porte, faixa de valor), com movimento suave. A linha "encerradas" entra quando houver a fonte (DataJud, decisão de 09/Nov) | P | 0.7.14 |
| 79 | Botão para coletar só as estatísticas do último mês (sem puxar tudo), para ver os picos de volume | "Montar as estatísticas do último mês": lê os Diários dos últimos ~22 dias úteis dos tribunais marcados e guarda **só os totais** (data, tribunal, vara, frente; porte e valor só quando já se sabem, sem consultar a Receita de novo). Não entra na Lista nem no Arquivo. Roda em segundo plano, com barra de andamento; os Diários grandes (TRT2) podem levar dezenas de minutos | P | 0.7.15 |
| 80 | Histórico de leituras como aba, ao lado de Painel e Lista; e uma aba Arquivo | Abas no alto: **Painel · Lista · Arquivo · Histórico de leituras** (no lugar do link que abre e fecha) | P | 0.7.14 |
| 81 | O código 403 não diz nada ao advogado | Coluna principal em palavras ("Diário de hoje só às 3h"); o código técnico vai para uma coluna discreta no fim, com o botão (?) que abre a explicação simples ao clicar e fecha ao clicar fora | P | 0.7.14 |

## Sexta rodada: "Atualizar estatísticas" (amplia o item 79)

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 82 | Botão **"Atualizar estatísticas"** no Painel: escolher frente (trabalhista, tributário...), tribunais e varas (as marcadas ou todas) e quanto tempo para trás (1, 3, 6 ou 12 meses); roda em paralelo com barra de andamento que vai enchendo; de noite, aos poucos, para não pesar; e um agendamento para atualizar de tempos em tempos e mostrar sazonalidade e picos | Guarda **só totais** (data, tribunal, vara, frente; porte e valor só quando já se sabem), nunca enche a Lista nem o Arquivo. Fila de Diários a ler, um por vez, com limite por noite (ex.: 30 Diários por noite, ajustável) dentro da janela da leitura noturna; retoma de onde parou; barra "N de M Diários". O agendamento usa a mesma tarefa do Windows. Antes de implementar: a Arquitetura confirma até quando o CNJ guarda os Diários antigos, o volume (o do TRT2 é grande) e um limite seguro de consultas | A (limites e desenho), P (tela e programa) | 0.7.15 |

## Sétima rodada: preparo do Painel e uso da tela

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 83 | Na 0.7.14, o Painel já preparado para receber os gráficos novos da 0.7.15 (estatísticas no tempo), sem refazer o desenho | O Painel vira uma grade de blocos: cada gráfico é um bloco com título, (?) e os mesmos filtros; a 0.7.15 só acrescenta blocos. Nada é específico da frente trabalhista | P | 0.7.14 |
| 84 | **Regra permanente**: a tela usa toda a largura disponível. No notebook ocupa a tela inteira; arrastada para um monitor maior, estica e aproveita o espaço (gráficos e números maiores); no celular, uma coluna legível. Não pode piorar de uma versão para outra | Largura fluida (sem teto fixo de largura no conteúdo), grade de blocos que ganha colunas conforme a tela, números e gráficos que crescem com a largura. Teste automático a cada versão em 4 larguras (celular 390, notebook 1366, monitor 1920 e 2560) que falha se sobrar faixa vazia nas laterais, se algo sair da tela ou se o texto cortar; prints das 4 larguras para o dono antes de publicar | P | 0.7.14 (e toda versão) |

## Oitava rodada (leitura das 9h17, 09/Nov)

| # | O que o dono viu | Explicação e proposta | Quem | Pacote |
|---|---|---|---|---|
| 85 | A leitura automática rodou às 9h17, mas os horários são 8h e 20h | A tarefa do Windows tem "executar assim que possível": se o computador estava desligado ou dormindo às 8h, a leitura acontece quando ele volta (por isso 9h17). O "Histórico de leituras" mostra a origem "fora do horário" nesses casos. Proposta: a tela dizer isso com todas as letras ("leitura das 8h feita às 9h17, porque o computador estava desligado ou dormindo") | P | 0.7.15 |
| 86 | Às 9h19 a tela ainda dizia "Próxima leitura automática: hoje às 08h00" | A tela tinha sido aberta às 2h46 e não recarregou. Na 0.7.14 ela recarrega ao fim de cada leitura, inclusive a agendada; na 0.7.15, a "próxima leitura" também se atualiza sozinha quando o horário passa | P | 0.7.15 |
| 87 | Mensagem clara quando a leitura é a de um horário perdido | Faixa na tela: "Fazendo agora a leitura das 08h00, que não rodou na hora porque o computador estava desligado ou em repouso." (EN: "Running now the 8:00 a.m. reading, which did not run on time because the computer was off or asleep."). O programa descobre qual horário foi perdido pelos horários da Configuração | P | 0.7.15 |
| 88 | Botão "Interromper" sem deixar sujeira | Dá para fazer com segurança: o botão só pede para parar, e a leitura para no próximo ponto seguro (entre um tribunal e outro, ou entre uma consulta à Receita e outra; durante o download de um Diário grande, pode levar até um minuto). Cada ação é gravada inteira ou não é gravada (o banco garante); o Diário interrompido não é marcado como lido, então a próxima leitura continua de onde parou, sem repetir nem perder nada; a planilha não é tocada no meio (só é regravada inteira, com o que já estava salvo). O histórico registra "interrompida por <pessoa> às <hora>". Vale também para a leitura agendada, que roda em outra janela. Enquanto roda, "Ler o Diário agora" continua desligado; aparece "Interromper" com confirmação | P | 0.7.15 |

## Nona rodada (teste da 0.7.14 instalada, 09/Nov)

| # | O que o dono pediu | Proposta | Quem | Pacote |
|---|---|---|---|---|
| 89 | "Sair do RADAR" que feche também a janela preta; não deixar o programa aberto à toa | Item "Sair do RADAR" no menu ☰ (confirma e fecha a tela e a janela preta). E a janela preta fecha sozinha 2 minutos depois de a tela ser fechada, se não houver leitura rodando (a leitura agendada não depende dela) | P | 0.7.17 |
| 90 | Tela em branco por alguns segundos depois de "Atualizar agora" | Enquanto o programa reinicia, a tela mostra um carregamento animado ("Atualizando para a versão X…") e recarrega sozinha quando volta, sem tela vazia | P | 0.7.17 |
| 91 | **Buscar dados na área logada por processo, com a extensão de IA que o escritório usar** (Claude in Chrome, ChatGPT/Codex no navegador, Gemini…) | Em cada cartão sem contato ou sem valor: botão "Buscar na área logada" com (?) explicando o passo a passo para leigo. O RADAR monta na hora um texto para colar na extensão, só com o que falta naquele processo (contato, valor da causa, data de ajuizamento, endereço). A extensão devolve um bloco de resposta padronizado; o advogado copia e cola num campo do RADAR, que preenche a ficha e a planilha sem IA. A resposta diz, item por item: encontrado (com a fonte), "não consta no processo" ou "não foi possível agora (tentar depois)". Em lote: o mesmo para os selecionados ou filtrados (até 30 por dia). Agnóstico de fornecedor: o texto não depende da extensão | P (desenho da resposta conforme o dos contatos, Arquitetura) | 0.7.17 |
| 92 | Atualizar dados já preenchidos (contato, sócios, endereço) se mudarem | Botão "Atualizar dados" no cartão e em lote (mesmo fluxo do 91). Receita: o programa consulta de novo o CNPJ a cada 30 dias e marca o que mudou. Área logada: lembrete opcional de rever processos estratégicos a cada N dias | P; A (periodicidade) | 0.7.17 |
| 93 | Configuração "bolachuda", sem fechar nem salvar com clareza | Configuração vira uma janela própria (por cima da tela), com fundo e cabeçalho escuros, seções com títulos destacados (Licença e código · Onde fica a planilha · Leituras automáticas · Tela · Termos e condições · O que a SolverONE recebe), botões Salvar e Fechar (X); se houver mudança não salva, o X pergunta "Salvar, descartar ou continuar editando" | P | 0.7.17 |
| 94 | Cartões da pasta grandes demais; Google Drive com destaque demais; o que acontece ao mudar a pasta? | Opções compactas em uma linha, sem "recomendado"; texto curto explicando: mudar a pasta **não move** a planilha antiga; o programa cria a planilha na pasta nova na próxima leitura (a antiga fica onde está) | P | 0.7.17 |
| 95 | Confirmação visual ao salvar um campo do cartão | ✓ verde ao lado do campo salvo (situação, valor da causa); "Salvar" do valor fica cinza enquanto o valor não mudar | P | 0.7.17 |
| 96 | Termos e condições na Configuração | Seção "Termos e condições" sempre visível: versão vigente, link para ler, "escritório aceitou em … por …" e "você aceitou em …" (camadas da Arquitetura); "ainda não aceito" quando faltar | P | 0.7.17 |
| 97 | Defeitos vistos no cartão do print | (a) "Outras empresas" repetia a própria empresa ("Fundacao do Abc e Outros (1)"): tirar "e Outros (n)" do nome; (b) classe com letras trocadas ("AçãO TRABALHISTA - RITO ORDINáRIO"): corrigir a caixa das letras; (c) o valor da causa digitado fica só no navegador: passar a guardar no programa (vale em outra tela e na planilha) | P | 0.7.17 |
| 98 | "Não consegui ler LexSuiteONE.xlsx (ValueError). Usando o padrão" com TRT2 e TRT15 | A planilha passou de 50 MB por dentro (limite de segurança da leitura): Preferências e Exclusões ignoradas e planilha não regravada. Corrigido no ramo: o RADAR lê só as três abas editáveis; mensagem clara em PT e EN | P | 0.7.16 |
| 99 | 20.699 "processos novos" em dois TRTs em poucos dias | Regra de "ação nova" larga demais ("fica notificado", "citação" aparecem em quase toda intimação de processo de 2026). Apertar para lista de distribuição e notificação inicial, com teste | P | 0.7.16 |
| 100 | A planilha vai encher (mais tribunais, outras frentes) | Aba Arquivo da planilha com 90 dias + trabalhados (0.7.16); aviso a 80% em três lugares, "Limpar a planilha (com cópia)" em `Cópias de segurança/`, limpeza sozinha a 100%, 6 cópias guardadas (0.7.17). Desenho em `documentacao/DESENHO-PLANILHA-GRANDE.md` | P | 0.7.16 e 0.7.17 |
| 101 | Mostrar o armazenamento do computador e proteger o equipamento de quem não tem TI | Seção "Armazenamento" na Configuração (planilha, banco, `saida/`, cópias, espaço livre no disco); sem cópia nova e aviso vermelho com menos de 5 GB ou 10% livres. Uma planilha por frente quando o tributário entrar: desenho da Arquitetura | P; A (planilha por frente) | 0.7.17 |
