# Desenho: amostras de formato, planilha em rede e estatística leve (revisão 2, 24/Nov/2026)

Feito pela Arquitetura (subagente `arquiteto`), só lendo o código da 0.7.52. Incorpora as decisões do dono de 24/Nov (perguntas 59 a 67 do quadro). Substitui a revisão 1: sai o interruptor, sai o computador mestre e sai a aba "Amostras" na planilha. Nada é implementado antes do "pode" do dono.

**O problema, em três linhas.** (1) Quando uma fonte (Diário, Receita, CNJ, área logada) muda de formato, a SolverONE só fica sabendo pelo relato do advogado. (2) Com vários computadores, quem grava a planilha por último apaga o que o outro trouxe. (3) A planilha cresce com tribunais que ninguém escolheu (51 mil linhas no caso real), e a limpeza não a diminui.

**Achados no código que mudam o desenho**
- O aviso de tamanho continua depois da limpeza por dois motivos:
  - `radar.py:779` monta a aba Arquivo com `montar_radar(visao="arquivo")`, que traz **todos** os tribunais já lidos.
  - `armazenamento.selecionar_arquivo` conta os 90 dias por `primeira_vez` (quando o RADAR leu), não pela data do processo no Diário. Por isso os 24 TRTs lidos uma vez ficam inteiros.
- `estatisticas_diarias` guarda dia, tribunal, vara, frente, porte e faixa, mas **não** guarda situação nem setor. `banco.retorno()` já conta por situação, só nos últimos 60 dias. O setor é calculado na hora (`radar.py:143`).
- O "Visto" é automático: abrir um card Novo marca Visto (`radar_modelo.html:4555`).
- `conta.instalacao` já é uma identificação aleatória (`secrets.token_hex(8)`) e serve para nomear a pasta de cada computador.
- Toda busca externa passa por `rede.pedir_json`. Mesmo assim, a amostra é capturada **por chamada explícita em cada fonte**, para nunca amostrar a própria `lex-conta` nem `judicial.solverone`.

## A) Amostras e assinaturas de formato de todas as fontes (59, 60, 61, 62)

**A.1 O que se captura** (função `amostras.observar(fonte, dados)`, chamada depois de ler cada fonte)

| Fonte (chave) | Onde | Amostra | Assinatura |
|---|---|---|---|
| `djen_caderno:<TRT>` | `djen.baixar_caderno` | os 5 primeiros itens do JSON do zip | o JSON inteiro, mais os nomes dos arquivos do zip |
| `djen_consulta` | `djen.buscar_filtrado`, `consulta_dia` | 1 página | sim |
| `receita:brasilapi`, `receita:minhareceita` | `cnpj.consultar` | 1 resposta | sim |
| `datajud:<TRT>` | `datajud._buscar` e `consultar_lote` | até 3 itens | sim |
| `datajud_wiki` | `datajud.chave_publica` | nenhuma (a página traz a chave pública) | só "achou ou não achou" |
| `area_logada:<ferramenta>` | `contatos.ler_resposta` | o texto colado, até 64 KB | cabeçalho v1, títulos, `dado`, `resultado`, formato |
| fontes novas | a mesma chamada | igual | igual |

O computador guarda as **20 mais recentes de cada fonte** na tabela local `amostras`, já anonimizadas, e manda no máximo **uma por fonte por dia**.

**A.2 Anonimização** (o algoritmo da revisão 1 continua e passa a valer para JSON)
- Os valores são trocados caractere por caractere, com `secrets`, mantendo a classe (maiúscula, minúscula, acentuada, dígito). Símbolos e o tamanho ficam iguais.
- As máscaras ficam, com todos os dígitos trocados. Nunca sai CPF ou CNPJ com dígito verificador válido.
- No JSON ficam as **chaves** (o esquema público das fontes), os tipos e as listas de valores fixos que estão no código e passam pela revisão. Exemplos: o tipo de comunicação do Diário e a situação cadastral da Receita.
- Chave com dígito ou com cara de dado (por exemplo, um número usado como chave) também é trocada.
- O contato do sócio (`socio_contato`) e os campos de sócio e e-mail da Receita saem com o **tamanho arredondado** a múltiplos de 8 (pergunta 61). O resto mantém o tamanho exato.
- O mapa de troca fica só na memória e é descartado. Nada de pessoa física sobrevive, nem nome de reclamante, de MEI ou de sócio.

**A.3 Assinatura de formato** (não leva conteúdo nenhum)
- É a lista ordenada de caminhos com o tipo e a presença de cada um. Exemplos: `items[].destinatarios[].nome:str 100%`, `items[].valor:num 40%`. No texto da área logada: versão do protocolo, títulos das colunas e valores de `dado` e `resultado`.
- Leva também um `sha256` da lista. Fica guardada com a data na tabela local `formatos` (fonte, hash, assinatura, primeira_vez, ultima_vez, vezes).
- Hash novo numa fonte gera um evento de mudança com a diferença: campo novo, campo que sumiu, tipo trocado, presença que caiu mais de 30 pontos. Exemplo: "djen_caderno:TRT9: campo `valor` sumiu em 24/11".
- No computador, isso vai só para a aba Saúde e para o diagnóstico. **Nunca aparece na tela** (decisão 60).

**A.4 Como enviar (opções)**

| Opção | Prós | Contras | Custo | Risco |
|---|---|---|---|---|
| **A1. Assinatura sempre, amostra quando a nuvem pede.** A ação `formato` manda os hashes e as mudanças; a resposta traz `quer_amostra:[fontes]`; a ação `amostra` manda só essas | pouco tráfego (as fontes públicas são iguais para todos); a SolverONE regula pelo recurso `amostras` no RootifyONE, sem nada no programa | duas ações novas | M | baixo |
| A2. Mandar todas as amostras, uma por fonte por dia | simples | cerca de 75 fontes × 64 KB por instalação por dia; o volume se repete entre escritórios | M | médio (custo, retenção) |
| A3. Reaproveitar `registro` (2.000 caracteres) | sem nuvem nova | não cabe amostra; o termo diz "de erro" | P | médio |

**Recomendação: A1.** As fontes públicas são as mesmas para todos os escritórios: basta uma instalação mandar a amostra quando o hash muda, ou quando a fonte tem menos de 10 amostras em 30 dias. Os limites por instalação são 20 amostras por dia, 64 KB cada (compactadas com gzip e em base64) e 50 chamadas `formato` por dia.

**A.5 Fila silenciosa** (decisão 60)
- Tabela local `envios` com tipo, corpo, tentativas e `proxima_em`.
- Novas tentativas em 5 min, 30 min, 2 h e 12 h, depois uma por dia. Teto de 5 MB: saem primeiro as amostras mais velhas; as mudanças de formato ficam.
- Nenhuma mensagem na tela. A `lex-conta` v20 responde "ação desconhecida", e o item continua na fila. Assim, a 0.7.53 pode sair antes da nuvem v21: a fila esvazia sozinha quando a v21 entrar.
- Transparência: em Configurações → "O que a SolverONE recebe", um bloco novo "Amostras de formato (conteúdo trocado)" mostra a última amostra enviada de cada fonte, exatamente como foi, e a data do último envio. **Sem chave para desligar.**

**A.6 Termos: cabe na 6.2 (c)?**
- A 6.2 é a lista do que a SolverONE recebe. A alínea (c) diz "registros técnicos de erro, sem conteúdo de processos". O 3.4 e o 6.1 prometem não receber a relação de ações, as fichas, os contatos e as anotações.
- Depois da troca irreversível, a amostra não tem número, nome, CNPJ nem contato. Cumpre o "sem conteúdo de processos", o 3.4 e o 6.1, e não é dado pessoal (LGPD, art. 12).
- A assinatura é só o esquema da fonte pública. Cabe com folga.
- A lacuna é literal: "**de erro**". A amostra também é colhida quando a leitura dá certo, justamente para achar o erro que o programa não enxerga (o formato que mudou).
- **Conclusão:** cabe sem mudar os termos, por uma leitura razoável e com risco baixo, desde que:
  1. a anonimização seja a da A.2;
  2. amostras e assinaturas por instalação sejam guardadas 90 dias (o prazo de "registros técnicos" da 6.4);
  3. a finalidade seja a da 6.3 ("prestar o serviço, dar suporte");
  4. a prévia continue em "O que a SolverONE recebe".
- O registro de mudança de formato da fonte não leva nada do escritório e pode ficar sem prazo.
- **Se o advogado discordar** (ele revisa a tradução em inglês antes da 0.7.54, decisão 66), muda só isto, em PT e EN:
  - 6.2 (c): "registros técnicos de erro e de funcionamento, inclusive amostras do formato das respostas das fontes lidas, com todo o conteúdo trocado de forma irreversível antes do envio, sem conteúdo de processos";
  - 6.4: "Registros técnicos e amostras de formato: 90 dias";
  - isso faz uma versão 1.2 dos termos, com aceite novo;
  - o 3.4 e o 6.1 continuam verdadeiros.

**A.7 Nuvem (Arquitetura, pelo conector, com o "pode" do dono)**
- `lex-conta` v21 com as ações `formato` e `amostra`. A identificação é por `codigo` e `instalacao`, como hoje.
- Tabelas, com RLS ligada e sem política pública (só a função usa):
  - `lex_formatos`: instalação, fonte, hash, assinatura, primeira e última vez;
  - `lex_amostras`: instalação, versão, fonte, hash, conteúdo de até 64 KB, resumo, `criado_em`; a própria função apaga o que tiver mais de 90 dias, em lotes;
  - `lex_formato_mudancas`: fonte, quando, hash antes e depois, diferença, quantas instalações viram.
- Recurso `amostras` em `lex_recursos`, ligado por padrão, que o RootifyONE pode desligar.
- Registro em `nuvem/supabase/2026-11-2X-lex-amostras-formatos.sql`, com o desfazer ao lado (`…-desfazer.sql`). Anotação no quadro. A Arquitetura avisa o dono antes de aplicar, porque recebe dado vindo do cliente, mesmo anonimizado.

## B) Planilha em rede sem computador mestre (63, 64, 65)

**Princípio.** A planilha é só um **espelho** que se gera de novo. A fonte de verdade é o banco de cada computador, mais um **registro de eventos de cada computador** na pasta do escritório. Por isso, regravar a planilha nunca apaga dado.

**B.1 Estrutura da pasta** (`<pasta da área>/_RADAR (não mexer)/`, com um LEIA-ME.txt)
- `troca/<instalacao>/<seq_ini>-<seq_fim>.json.gz`: lotes de eventos que **nunca são reescritos**. Nascem como `.parcial` e trocam de nome com `os.replace`. Só o dono da pasta escreve nela.
- Uma vez por mês, o próprio computador junta os lotes com mais de 30 dias em `base-AAAA-MM.json.gz` e só depois apaga os lotes.
- `estado/<instalacao>.json`: perfil, computador (`platform.node()`), versão, até que número de evento já mandou, cobertura (tribunal e até que data leu) e `licenca` = `sha256(código)[:16]`. O código de cliente em si não vai.
- `gravando.trava`: a trava curta (B.4).

**B.2 Eventos.** Cada um leva um id (`instalacao:seq`), um relógio híbrido `quando_utc` (o maior entre o relógio local e o maior já visto, mais 1 ms), o perfil e o computador.
- `lido`: o resumo do processo (`_RESUMO` + `_RESUMO_RECEITA`, que já não têm o texto do Diário nem o reclamante). Só dos tribunais escolhidos e dos últimos 30 dias.
- `cobertura`: tribunal, data e origem (caderno, consulta ou histórico).
- `situacao`, com o motivo.
- `visto`.
- `campo`: valor da causa, ajuizamento, UF, com a fonte.
- `contato` e `contato_removido`, que só desfaz uma cópia feita pelo mesmo evento (o Desfazer da 0.7.50).
- `validacao`.
- `estatistica`: linhas por dia e tribunal, só quando mudam.
- Não entram: critérios, exclusões e "Excluir esta empresa" (são por pessoa, 12/Nov).

**B.3 Junção** (no banco local; não depende da ordem e pode rodar duas vezes sem mudar nada)
- Momentos:
  - **automática ao abrir o programa**, antes da primeira tela;
  - **antes de cada gravação da planilha**;
  - depois de colar uma resposta;
  - no botão da B.6.
- Fora desses momentos não roda sozinha, para a lista não mudar debaixo da mão de quem está trabalhando.
- Regras:
  - processo: entra se não existe aqui e não está em `processos_apagados`; a leitura local depois substitui o resumo, e o enriquecimento fica;
  - campos: `completar_fonte` (fonte mais forte, ou igual e mais nova);
  - contatos: soma (único por processo, canal e valor);
  - validação: a mais recente;
  - situação: a mais recente pelo relógio híbrido, com desempate pela instalação, e registro em `acoes`;
  - **Visto: só muda de Novo para Visto**, nunca passa por cima de uma situação trabalhada, e guarda quem viu;
  - estatística: por dia e tribunal, fica a versão com mais processos (a leitura mais completa), nunca a soma.
- A entrada não é confiável. Passa de novo pelos filtros do leitor (`_CPF`, `_PROIBIDO`, pessoa sem fonte). É ignorado o arquivo com mais de 20 MB, de outra licença, corrompido, de formato desconhecido ou com nome fora do padrão.

**B.4 Gravação sem passar por cima**
1. **Trava curta**: `gravando.trava` criada com `os.open(O_CREAT|O_EXCL)`, válida por 2 min e só durante juntar e gravar (segundos). Trava vencida pode ser tomada; depois de tomar, o RADAR relê para confirmar.
2. **Vetor de versão**: a aba oculta Sobre da planilha guarda até que evento de cada instalação aquela planilha contém. O computador **só grava se o que ele sabe cobre esse vetor**, instalação por instalação. Se não cobre, espera os lotes que faltam chegarem pela sincronização e tenta de novo em 60 s. Assim, **a planilha nunca anda para trás.** Se em 2 h não chegarem (alguém apagou a pasta `troca`), grava assim mesmo e marca na Saúde.
3. **Cópias de conflito** (Drive: "nome (1).xlsx"; OneDrive: "nome-COMPUTADOR.xlsx"; conferir os nomes no Windows): se a aba Sobre diz que é do RADAR, vão para `Cópias de segurança/conflitos/` e nunca são apagadas.
4. **Excel aberto**: o que a revisão 1 desenhou continua. O nome de quem abriu sai do `~$`, só em pasta de rede e só na tela. Novas tentativas em 10 s, 30 s e 60 s, depois a cada 120 s por até 2 h. Depois disso, a faixa "Planilha desatualizada desde…".

**B.5 Por que nada se perde quando A leu o Diário e B trouxe contatos**
- A lê às 10:00: 300 processos vão para o banco de A e para os lotes `lido` de A.
- B cola a resposta às 10:05: os contatos do P7 vão para o banco de B e para um evento `contato` de B.
- B grava às 10:06: primeiro junta os lotes de A que já chegaram, depois grava os 300 processos com os contatos.
- Se os lotes de A ainda não tinham chegado, o vetor da planilha (que A gravou) mostra que falta o que A fez. B espera, em vez de gravar uma planilha mais velha.
- Os dados de A e de B estão nos dois bancos e nas duas pastas `troca`. Nenhum arquivo é escrito por dois computadores. Regravar a planilha só reflete o que já foi juntado.

**B.6 Botão "Trazer do escritório (N)"** (ideia do dono)
- Aparece ao lado de "Ler o Diário agora" **só quando N > 0**. N é o número de processos com novidade de outros computadores ainda não juntada aqui. A pasta é olhada a cada 120 s, só listando nomes de arquivos, o que é barato.
- O clique junta em segundos. O botão vira "Trazido" por 3 s e some. A dica de acessibilidade diz "de Maria (NOTE-02), até 10:32".
- Layout:
  - **1366 px**: botão secundário (contorno) na mesma linha; o texto "Lê N de K tribunais" desce para a linha de baixo;
  - **abaixo de 1100 px** (notebook com zoom de 125 %): rótulo curto "Do escritório (12)";
  - **1600 px ou mais**: uma linha pequena embaixo, "de Maria e João, até 10:32".
- Entra nos testes de `larguras.js`.

**B.7 "Visto por" e autoria** (65)
- Colunas novas em `leads`: `visto_pessoa`, `visto_pessoa_em` e `status_por`. Colunas novas em `contatos`: `incluido_por` e `computador`. Tudo por `ALTER TABLE`, como as migrações de hoje.
- No card: "Visto por Maria (NOTE-02) · 24/11 10:32"; se forem várias pessoas, "Visto por Maria e mais 2".
- Na planilha:
  - abas Radar e Arquivo: "Visto por", "Situação marcada por" e "Quando";
  - aba Contatos: "Incluído por", "Computador" e "Quando".
- "Visto por pessoa" vai para o backlog.

**Opções:**
- **B1, eventos que não se apagam, um computador por pasta, com vetor** (recomendada): ninguém escreve no arquivo do outro e funciona em rede, Drive e OneDrive. Custo G, risco médio (atraso da sincronização).
- B2, uma aba de troca na planilha: um arquivo só, mas quem grava por último apaga, e não funciona com o Excel aberto. Descartada.
- B3, computador mestre: recusada pelo dono (decisão 63).

## C) Planilha enxuta, aba de estatística e aviso no Painel (67)

**C.1 O que fica na planilha**
- Só os **tribunais escolhidos hoje**.
- A aba Radar com no máximo **30 dias**, contados pela data no Diário.
- A aba Arquivo continua com 90 dias (o padrão decidido em 12/Nov), mas contados **pela data no Diário**, não por `primeira_vez`. Todo processo trabalhado entra, de qualquer idade.
- O que sai da planilha continua no programa (tela Arquivo).
- Antes da primeira gravação enxuta, a planilha inteira é copiada para `Cópias de segurança/antes da 0.7.53/`, uma vez só, como na 0.7.33.

**C.2 Estatística leve de TODOS os tribunais**
- Tabela local nova `estatisticas_situacao`: data, tribunal, frente, faixa, setor, porte, situação, quantidade.
- É recalculada como `atualizar_estatisticas`: os dias que ainda têm processos são refeitos; os outros ficam como estavam e nunca se apagam.
- A coluna `setor` entra em `leads` ao gravar, e uma vez para os processos que já existem.
- A aba "Estatística" vai em formato longo: período, tribunal, área, dimensão (total, situação, faixa, setor ou porte), valor, processos, dias lidos e dias úteis.
  - por mês, em todos os meses;
  - por dia, só o total, nos últimos 31 dias.
- Os números saem da **mesma função** que alimenta os gráficos do Painel e a Sazonalidade.

**C.3 Aviso no Painel**
- Tabela `cobertura` (tribunal, data, origem), feita a partir de `cadernos`, `historico`, `consultas_dia` e da cobertura vinda da troca.
- Nos gráficos por dia e por mês, um asterisco quando os dias lidos ficam abaixo de 80 % dos dias úteis.
- Nota embaixo do gráfico: "* Parcial: TRT9 (12 de 20 dias úteis em out.). Também há dados de TRT3 e TRT5 (12/11): aba Estatística da planilha."
- Os gráficos continuam mostrando só os escolhidos.

**C.4 O caso real** (contas que supõem só o TRT9 escolhido hoje)
- Hoje: cerca de 51 mil linhas.
- Na 0.7.53, com o TRT9 lido há cerca de 30 dias: cerca de 11 mil linhas mais os trabalhados, ou seja, **cerca de 78 % a menos**.
- Com o TRT9 lido há 90 dias ou mais (Arquivo de 90 dias): cerca de 33 mil linhas, **cerca de 35 % a menos**. Fica abaixo do aviso de 80 % (48 mil). Se o Arquivo da planilha for igualado aos 30 dias, fica perto de 11 a 12 mil linhas; é uma constante, `preferencias.PADRAO`.
- Aba Estatística: cerca de 25 linhas por tribunal por mês, ou seja, cerca de 7 mil linhas por ano com os 24 TRTs, mais umas 750 por dia; em torno de 0,3 a 0,5 MB.

## Versões
- **0.7.53** (nada depende da nuvem), na ordem: C inteira; B.4 itens 1, 3 e 4; captura, anonimização, assinaturas e fila da A; B.1 a B.7.
  - Se a troca não passar no teste do Windows com Drive, B.1 a B.7 vão para a 0.7.54 e o resto sai na 0.7.53.
- **Nuvem v21** (Arquitetura, com o "pode"): A.4 e A.7. Pode entrar antes ou depois da 0.7.53, porque a fila espera.
- **RootifyONE** (repositório `rootify-one`, com a regra zero de lá): tela "Formatos das fontes", com a linha do tempo das mudanças e as amostras antes e depois.

## Riscos
- **Atraso do Drive ou do OneDrive**: a planilha fica atrás por alguns minutos (o vetor impede que ande para trás). A faixa diz "Gravada por B às 10:06; juntou 2 computadores".
- **Alguém apaga `_RADAR (não mexer)`**: os dados continuam nos bancos. Cada computador manda tudo de novo quando a sua pasta some.
- **Computador ainda na 0.7.52**: grava a planilha sem a troca. O próximo na 0.7.53 regrava (é só espelho). O aviso "um computador na 0.7.52" vem da aba Sobre. Recomendação: atualizar todos juntos.
- **Volume no Drive**: cerca de 11 MB por mês sem compressão para 11 mil processos, uns 2 a 3 MB compactados (estimativa; medir no teste).
- **Colega mal-intencionado**: pode injetar uma situação falsa. É a mesma confiança que se tem nas pessoas do escritório, e fica registrado "trazido de".
- **Desempenho**: a junção num banco de 51 mil processos tem de levar menos de 5 s; medir.
- **Termos**: a leitura da 6.2 (c) pode ser contestada; o texto alternativo da A.6 está pronto.
- **Amostra da área logada**: pode vir de processo em segredo de justiça; o risco cai com a troca irreversível.

## Testes
- **Amostras**:
  - mesmo tamanho e mesmos símbolos;
  - nenhuma palavra de 3 letras ou mais de fora da lista, em centenas de respostas fictícias de cada fonte;
  - o JSON continua válido e com as mesmas chaves;
  - **a assinatura da amostra é igual à do original**;
  - nenhum CPF ou CNPJ válido;
  - sócio com tamanho arredondado;
  - campo que sumiu, campo novo e tipo trocado são detectados;
  - nada amostrado de `judicial.solverone` nem da chave do DataJud;
  - sem rede: nada na tela e a fila cresce até o teto;
  - v20 com "ação desconhecida": o item fica na fila;
  - a prévia é igual ao que é enviado.
- **Rede**:
  - dois bancos e uma pasta que simula o atraso do Drive (lotes fora de ordem): ordens diferentes dão o mesmo banco, e juntar duas vezes também;
  - a planilha nunca anda para trás;
  - trava vencida e trava disputada;
  - cópias de conflito;
  - `~$` com nome em ANSI, UTF-16, acentuado e encurtado;
  - arquivo com CPF, de outra licença, corrompido ou grande é recusado;
  - processo apagado não volta;
  - relógio adiantado 10 min;
  - um computador na 0.7.52 gravando no meio;
  - a junção mensal rodando enquanto o outro lê;
  - Visto não passa por cima de "Em contato";
  - botão: N certo, some depois do clique, em 1024, 1366 e 1920 px.
- **Planilha**:
  - só os escolhidos;
  - aba Radar com até 30 dias, pela data no Diário;
  - aba Estatística igual aos gráficos;
  - asterisco de cobertura;
  - banco fictício de 51 mil dá as linhas esperadas;
  - cópia de segurança antes da primeira gravação enxuta.
- **No Windows, com o dono**: pasta de rede, Google Drive e OneDrive, com dois computadores.

## Definition of done (13 pontos)
1. **Manual**:
   - `paginas/manual.html:299`: dizer que vão também as amostras de formato com o conteúdo trocado;
   - seção nova "Vários computadores na mesma pasta" (botão, Visto por, planilha só com os escolhidos, aba Estatística);
   - `robo/SEGURANCA.md` e `robo/LEIA-ME.md`.
2. **Ajuda de cada tela**: Painel (asterisco, botão) e Configurações ("O que a SolverONE recebe").
3. **Tour**: o passo do botão, só quando ele existir.
4. **Busca**: "outro computador", "trazer do escritório", "visto por", "estatística", "amostra" (PT e EN).
5. **Wizard**: sem mudança (a troca é automática); conferir o texto do passo da pasta.
6. **Novidades da versão**:
   - "Inclusão do compartilhamento de processos, situações e contatos entre os computadores da mesma pasta";
   - "Inclusão de 'Visto por' na tela e na planilha";
   - "Planilha só com os tribunais escolhidos e inclusão da aba Estatística";
   - "Inclusão do envio de amostras de formato anonimizadas das fontes lidas, para detectar mudanças".
7. **Termos**: sem mudança (A.6), salvo parecer contrário do advogado.
8. **E-mails**: o de boas-vindas não fala de um computador só (conferir); o aviso por e-mail não muda.
9. **RootifyONE, ArchONE e EaglePlanONE**: ver abaixo.
10. **Retrocompatibilidade**:
    - migração das colunas e tabelas;
    - a primeira exportação para a troca roda em segundo plano;
    - cópia antes da primeira gravação enxuta.
11. **Segurança e LGPD**: o nome do perfil e o do computador ficam só na pasta do escritório; só sai a amostra anonimizada e a assinatura.
12. **Qualidade**: os testes acima, `rodar_tudo.sh` e o revisor.
13. **Registro**: quadro, `ESTADO-ATUAL-RADAR.md`, `PENDENCIAS.md` e `ARQUITETURA.md`.

## O que RootifyONE, ArchONE e EaglePlanONE precisam saber
- **RootifyONE**: recurso `amostras` (ligado por padrão), tela "Formatos das fontes", alerta de mudança de formato e versão de cada instalação (para cobrar quem está atrasado).
- **ArchONE**: integração nova RADAR → `lex-conta` v21 (`formato`, `amostra`) → Supabase → RootifyONE. Padrão reutilizável "eventos que não se apagam, um por computador, mais vetor" para pastas sincronizadas.
- **EaglePlanONE**: "Amostras e assinaturas de formato", "Vários computadores sem mestre" e "Estatística leve". No backlog: "Visto por pessoa" e "aproveitar a leitura de outro computador" (não baixar de novo um caderno que outro já leu).

## Revisão jurídica e LGPD (não bloqueia, por decisão do dono)
1. A amostra conta como anonimização (art. 12), mesmo com o tamanho preservado?
2. A leitura da 6.2 (c) se sustenta, ou entra o texto da A.6 junto com a revisão da tradução em inglês?
3. Amostra da área logada de processo em segredo de justiça.
4. Nome do colega e do computador mostrados só na pasta do escritório.

## O que precisa do dono
Nenhuma pergunta nova. Falta só o "pode" para este desenho e, à parte, o "pode aplicar" da nuvem v21.

## Regras conferidas
- Só biblioteca padrão (`secrets`, `hashlib`, `gzip`, `json`, `os`), sem IA.
- Pessoa física não sai: nem na amostra, nem na troca, que é validada na entrada.
- Nenhum segredo: o código de cliente vai só como hash e a chave do DataJud nunca é amostrada.
- SQL só pela Arquitetura, com o arquivo datado e o desfazer.
- Nenhuma página do produto faz pedido externo.
- Nada de login, nem banco na nuvem para os dados do escritório.
