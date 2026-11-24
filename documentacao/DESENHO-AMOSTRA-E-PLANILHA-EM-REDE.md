# Desenho: amostra anonimizada da área logada, planilha em rede e enriquecimento compartilhado (24/Nov/2026)

Feito pela Arquitetura (subagente `arquiteto`, pedido da Produto) em 24/Nov/2026, a partir do pedido do dono do mesmo dia. Só leitura do código.

**Achados no código que mudam o desenho:**
- `planilha.py` só grava abas com `state="hidden"`. O modo "veryHidden" (aba que nem aparece na lista de reexibir do Excel) ainda não existe; é uma linha a mais.
- Os termos 3.4 e 6.1 e o manual (`paginas/manual.html:295`) prometem que a SolverONE não recebe os contatos. Por isso, mandar amostras **pede termos 1.2 e advogado**.
- O OneDrive não sincroniza arquivos que começam com `~$`, e o Google Drive provavelmente também não (não conferi). Nessas pastas, o nome de quem está com a planilha aberta só aparece em pasta de rede. Nelas o Excel também não trava a planilha entre computadores.
- Hoje quem grava por último apaga da aba Contatos o que o outro computador trouxe. É por isso que a parte C tem de vir com a B, ou antes dela.

Arquitetura, a pedido do dono. Nada é implementado antes do "pode". Base: versão 0.7.51. A 0.7.52 já tem o inglês e as ressalvas.

## A) Amostra anonimizada da resposta da área logada

**Como é hoje.** A resposta colada é lida sem IA (`contatos.py:475` `blocos_v1`, `:518` `ler_resposta`, `:360` `colar_v1`). Também vale o formato antigo de 8 colunas (`:115`). Quando o texto não é reconhecido, a tela recebe `nao_achou` (`app.py:2270`). Nenhuma cópia fica guardada. Quando a extensão muda o formato, só sabemos pelo relato do advogado.

**Canais que já existem para falar com a SolverONE** (`conta.py`, função `lex-conta`, sem chave no programa): `registro` (registro técnico, até 2.000 caracteres), `chamado` (v17, escondido no AssistONE por decisão de 12/Nov) e `estado_cnj`. Além disso: os totais por situação a cada leitura (termos, seção 7), os botões de e-mail do registro técnico (0.7.51) e a planilha compartilhada com `integracao@` para suporte (termos 6.1).

**Algoritmo (irreversível, sem chave guardada)**
1. Entra o texto colado ou o arquivo, até 64 KB. O resto é cortado e marcado com "[cortado: N caracteres]".
2. Caractere por caractere, sorteado com `secrets` e mantendo a classe: maiúscula vira maiúscula, minúscula vira minúscula, acentuada vira acentuada da mesma caixa, dígito vira dígito. Espaço, tabulação, quebra de linha, `|`, `-`, `.`, `/`, `@`, `(`, `)`, `:`, `#` e emoji ficam iguais. A quantidade de caracteres não muda.
3. Ficam sem troca só palavras do protocolo, e só no lugar delas:
   - na linha do cabeçalho: "RESPOSTA PARA O RADAR v1 · lote N de M" (os números N e M também ficam);
   - na linha de títulos: os nomes das colunas;
   - na coluna "dado": os valores de `DADOS_V1`;
   - na coluna "resultado": os valores de `RESULTADOS_V1`;
   - na coluna "fonte": o começo, pela lista de `FORCA_FONTE`;
   - na coluna "observação": as frases fixas ("sessão expirou", "outro tribunal", "a conferir");
   - no e-mail e no site: `http`, `https`, `www` e os finais `.com`, `.br`, `.adv`, `.gov`, `.org`, `.net`.
4. A lista fixa fica no código e passa pela revisão. Ela não é tirada do texto do pedido, porque o roteiro muda.
5. O texto em volta dos blocos (a conversa da extensão) é trocado inteiro. Ficam só a forma (linhas, títulos `#`, blocos de código).
6. Número de processo, telefone, CNPJ e datas mantêm a máscara, com todos os dígitos trocados. CPF ou CNPJ que saia com dígito verificador válido tem o último dígito trocado, para que nunca saia um documento válido.
7. O domínio do e-mail também é trocado (é o ponto que mais identifica).
8. A mesma palavra repetida dentro de uma amostra vira o mesmo sorteio, para que o padrão de "linha repetida" continue visível. O mapa fica só na memória e é descartado no fim.
9. Junto vai um resumo que não é conteúdo: versão do RADAR, dia, sigla do tribunal, ferramenta informada no pedido, lotes esperados e recebidos, formato (v1, antigo ou não reconhecido), tamanho original e, por linha, aceita, repetida ou recusada com o motivo. Esse resumo permite refazer a leitura sem a lista do escritório.

**Risco de reidentificação.** Sobra o tamanho de cada valor e a estrutura. A SolverONE sabe qual escritório mandou, e o Diário do dia é público. Daria, em tese, para cruzar o tamanho do endereço ou do nome de um sócio com as empresas daquele dia. O risco é baixo e cai mais se o tamanho for arredondado só no `valor` do sócio (pergunta 3). Empresa não é dado pessoal na LGPD; sócio e MEI são. Se a troca de fato não tiver volta, a LGPD (art. 12) não trata o resultado como dado pessoal. Quem confirma é o advogado.

**Onde guardar**
- Tabela `amostras` no `lexsuite.db`. É a fonte; ficam as últimas 20.
- Cópia na aba "Amostras" da planilha da área, em modo veryHidden.
- Aba oculta não é segredo: quem abre o .xlsx como zip lê. Por isso só entra o texto já anonimizado.
- Com vários computadores, a aba mostra as amostras de quem gravou por último. A fonte continua sendo o banco.

**Como enviar (opções)**

| Opção | Prós | Contras | Custo | Risco |
|---|---|---|---|---|
| A1. Ação nova `amostra` na `lex-conta` (v21), tabela `lex_amostras` guardada 90 dias, tela no RootifyONE | automática, sem chave, limite por licença (10 por dia, 64 KB) | nuvem nova, SQL, tela no RootifyONE, termos 1.2 | M | baixo |
| A2. Reaproveitar `registro` em pedaços | sem nuvem nova | 2.000 caracteres; o termo 6.2(c) diz "sem conteúdo de processos": forçado | P | médio (jurídico) |
| A3. Só a aba oculta mais o botão "Copiar a amostra para o suporte" (e-mail, como o registro técnico) | nada novo na nuvem; a pessoa vê o que manda | depende da pessoa; o e-mail limita o tamanho | P | baixo |

**Recomendação.** Na 0.7.53, A3: guardar, mostrar a aba e o botão manual. Na 0.7.54, A1, depois do advogado e dos termos 1.2. Quando ligado, o RADAR manda as pendentes na conferência da licença de cada leitura, ou logo depois de colar se houver internet.

**Interruptor.** "Enviar amostras anonimizadas para melhorar o RADAR", em Configurações. Vem com a prévia exata do que vai, no mesmo lugar de "O que a SolverONE recebe". O RootifyONE pode desligar pelo recurso `amostras`.

**O que a SolverONE faz com isso.** O RootifyONE recebe e lista as amostras por licença, versão e ferramenta. Avisa quando chega uma não reconhecida ou com mais de 30 % de linhas recusadas, que é sinal de que o formato mudou. A Arquitetura usa as amostras para ajustar o `PEDIDO_V1` e o leitor, com teste novo a partir da amostra.

**Testes**
- Mesmo tamanho e mesmos símbolos nas mesmas posições.
- Nenhuma palavra de 3 letras ou mais de fora da lista sobrevive, em centenas de respostas fictícias.
- Duas rodadas do mesmo texto dão resultados diferentes.
- `blocos_v1` acha os mesmos blocos, linhas, `dado` e `resultado` na amostra.
- Nenhum CPF ou CNPJ válido gerado.
- Corte em 64 KB.
- Aba "Amostras" com veryHidden.
- Nada sai com o interruptor ou o recurso desligado.
- A prévia é igual ao que é enviado.

**Esforço:** guardar mais a aba, P; envio, M.

## B) Vários computadores na mesma planilha

**Como é hoje.**
- `planilha.py:170` grava a planilha num arquivo temporário e troca com `os.replace`; se falhar, tenta mais uma vez (`:280-287`).
- `radar.py:822` mostra o aviso genérico.
- `app.py:467-470` tenta a cada 120 s por até 2 h.
- Não há trava própria e o arquivo `~$` do Excel não é lido. Quem grava por último vence.

**Proposta**
1. **Trava própria** `<planilha>.radar-trava`, ao lado da planilha.
   - Conteúdo: identificação aleatória da instalação, nome do perfil, nome do computador, começo, validade (5 min) e versão.
   - É criada de uma vez só (`os.open` com `O_CREAT|O_EXCL`), renovada a cada 60 s enquanto grava e apagada no fim.
   - Trava vencida pode ser tomada. Depois de tomar, o RADAR relê para confirmar que é a dele.
   - Cobre só "juntar e gravar", que leva segundos. Ler o Diário ao mesmo tempo em dois computadores não dá conflito, porque cada um tem o seu banco.
2. **Nome de quem está com a planilha aberta.** Só depois de `PermissionError`, o RADAR procura `~$` + nome e também `~$` + nome sem os 2 primeiros caracteres (o Excel encurta nomes longos).
   - Leitura: byte 0 é o tamanho e depois vem o nome em ANSI; perto do byte 54 está o nome em UTF-16. **Conferir num arquivo real do Excel antes de codar**, com nome acentuado.
   - Se não der para ler: "A planilha está aberta em outro computador ou programa".
   - O nome aparece só na tela. Não vai para Saúde, Histórico nem registro técnico.
   - Planilha aberta só para leitura (o padrão, porque está marcada) não cria o `~$`. Aí não há nome. Conferir no Windows se mesmo assim ela trava a gravação.
3. **Espera.** Novas tentativas em 10 s, 30 s e 60 s, depois a cada 120 s por até 2 h. Depois disso, faixa no Painel: "Planilha desatualizada desde…".
4. **Mensagem** (PT e EN): "Maria Souza está com a planilha aberta no Excel. Peça para fechar; o RADAR grava sozinho quando ela fechar."
5. **Para quem abre só para ler**, a faixa do alto da aba Radar diz: "Gravada por <pessoa> (<computador>) em 24/11 às 10:32; juntou dados de N computadores. Feche quando terminar; o RADAR não consegue atualizar enquanto ela estiver aberta."
6. **Drive e OneDrive.** O `~$` não chega aos outros computadores, a trava sincroniza com atraso e pode nascer uma cópia de conflito ("(1)" ou "-NOMEDOPC"). O RADAR procura esses nomes e avisa. Nessas pastas, a recomendação é que **um computador grave a planilha** (Configurações: "Nesta pasta, quem grava a planilha: este computador / qualquer um"). Os outros mandam o que fizeram pela troca da parte C.

**Opções:** B1 trava própria (rede: boa; Drive: fraca); B2 um computador grava (bom em qualquer pasta; se ele estiver desligado, a planilha atrasa); B3 uma planilha por pessoa (sem conflito; confunde o escritório). **Recomendação:** B1 sempre, mais B2 sugerida pelo assistente quando a pasta for Drive ou OneDrive.

**Testes**
- Dois processos gravando na mesma pasta.
- Trava vencida.
- Trava tomada ao mesmo tempo por dois.
- Arquivos `~$` de teste (nome ANSI, UTF-16, acentuado, encurtado).
- Cópia de conflito detectada.
- No Windows, com o dono: rede e Drive.

**Esforço:** M.

## C) Enriquecimento compartilhado entre os computadores

**Como é hoje.** Cada computador tem o seu banco. A planilha só é gravada; o RADAR lê dela apenas a aba Controle. Os critérios e as exclusões são por pessoa (12/Nov) e ficam assim.

**Opções**

| Opção | Prós | Contras |
|---|---|---|
| C1. Aba oculta "Troca" na planilha | um arquivo só, como o dono disse | quem grava por último apaga; precisa do Excel fechado; conflito no Drive |
| C2. Um arquivo por computador em `_RADAR (não mexer)/troca/<área>/<instalação>.json`: cada um só grava o seu e lê o de todos | ninguém sobrescreve ninguém; funciona em rede, Drive e OneDrive; não precisa de trava | uma subpasta a mais (com um LEIA-ME dentro) |
| C3. Ler as colunas visíveis da planilha | nada novo | frágil (coluna muda de versão); descartada |

**Recomendação: C2.** A planilha continua sendo o espelho visível do resultado juntado. As abas Contatos e Radar ganham "Incluído por" e "Quando".

**O que vai na troca.** Só os processos trabalhados neste computador, com quem e quando (UTC):
- situação (Em análise, Em contato, Virou cliente, Descartado, Arquivado), com o motivo;
- campos da área logada (valor da causa, ajuizamento, UF), com a fonte;
- contatos, com fonte, confiança e origem;
- validação de contato (confirmado ou descartado).

**Quando lê.** Ao abrir o RADAR, antes de cada gravação da planilha e depois de colar uma resposta.

**Regras de conflito**
- Campos: a regra de hoje (`banco.py:371` `completar_fonte`): fonte mais forte, ou igual e mais nova. A anterior vai ao histórico da ficha.
- Contatos: soma, nunca apaga (único por processo, canal e valor), com a marca "trazido de <pessoa> em <data>".
- Validação: a mais recente vence.
- Situação: a mais recente vence, com registro em `acoes`. "Visto" fica por pessoa e não é compartilhado (pergunta 6).
- Não entram: critérios, exclusões e "Excluir esta empresa" (por pessoa, 12/Nov).

**O que nunca entra.** Pessoa física que não responde pela empresa. A importação passa de novo pelos mesmos filtros do leitor (`_CPF`, `_PROIBIDO`, linha de pessoa sem fonte), porque o arquivo da pasta não merece confiança.

**Também fica fora**
- processo que este computador não tem (fica no arquivo e entra quando o processo aparecer);
- processo já apagado pela limpeza (`processos_apagados`);
- arquivo de outra licença, corrompido, de formato desconhecido ou maior que 20 MB.

**Retrocompatibilidade.** Computador ainda na 0.7.51 não lê a troca e continua gravando a planilha inteira. Recomendação: atualizar todos juntos. O RootifyONE já vê a versão de cada instalação.

**Testes**
- Dois bancos fictícios e uma pasta de troca; juntar duas vezes dá o mesmo resultado.
- Cada regra de conflito.
- CPF ou reclamante dentro do arquivo é recusado.
- Processo apagado não volta.
- Arquivo corrompido é ignorado.
- Relógios com minutos de diferença.

**Esforço:** G.

## Versões sugeridas
- **0.7.53:** B inteira; A sem envio (guardar, aba, botão manual, prévia).
- **0.7.54:** C (o jeito certo de vários computadores gravarem) e o envio automático de A, depois do advogado e dos termos 1.2.

## Definition of done (o que muda nos 13 pontos)
- **Manual:**
  - corrigir `paginas/manual.html:295` ("a SolverONE não recebe nenhum deles");
  - seção nova "Vários computadores na mesma pasta";
  - (?) no interruptor e em "quem grava".
- **AssistONE:** ajuda de Configurações (interruptor e quem grava) e do Painel (faixa "planilha desatualizada"); tour; busca ("amostra", "outro computador", "planilha aberta").
- **Wizard:** no passo da pasta, a pergunta "Outras pessoas vão usar esta pasta?". As mensagens do instalador não mudam.
- **Novidades:** "Inclusão do aviso de quem está com a planilha aberta"; "Inclusão de amostras anonimizadas das respostas da área logada"; "Inclusão do compartilhamento de situações, contatos e dados da área logada entre computadores da mesma pasta".
- **Termos:**
  - A muda: 3.4, 6.1, 6.2 (alínea "f", amostras anonimizadas), 6.4 (90 dias), novo aceite;
  - B e C não mudam (o dado fica na pasta do escritório; seções 4 e 6.1).
- **E-mails:** conferir se o de boas-vindas diz algo sobre um computador só. O aviso por e-mail não muda.
- **Site:** o manual. O `index` não promete nada que A contrarie (conferido).
- **Segurança e LGPD:**
  - o nome de quem está com a planilha aberta não sai do computador;
  - a amostra nasce anonimizada;
  - a troca é validada na entrada.
- **RootifyONE:** tela de amostras e recurso `amostras` (0.7.54).
- **ArchONE:** integração nova (RADAR → `lex-conta` → RootifyONE, amostras) e o padrão "um arquivo por computador" para pastas sincronizadas, que pode servir aos outros apps.
- **EaglePlanONE:** itens de roadmap "Amostras da área logada" e "Vários computadores na mesma pasta".

## Revisão jurídica e LGPD (advogado antes da 0.7.54)
1. A amostra conta como anonimização de verdade (art. 12) com o tamanho preservado?
2. Sigilo profissional e processos em segredo de justiça vistos na área logada.
3. Texto dos termos 1.2 e se o envio é com aceite prévio ou com interruptor.
4. O nome do colega mostrado na tela, só localmente.

## Perguntas ao dono (sugestão: 59 a 66; a Produto confirma a numeração)
59. Guardar as amostras já na 0.7.53 e só mandar à SolverONE depois do advogado (0.7.54)? **Recomendo sim.**
60. O envio automático vem ligado ou desligado? **Recomendo perguntar ao escritório uma vez, na primeira resposta colada** ("Sim / Não"), com o interruptor para mudar depois.
61. Arredondar o tamanho só do contato do sócio, para proteger melhor? **Recomendo sim;** o resto fica com o tamanho exato.
62. Guardar as últimas 20 amostras e a SolverONE apagar depois de 90 dias? **Recomendo sim.**
63. Em Google Drive ou OneDrive, um computador só grava a planilha (os outros mandam o que fizeram)? **Recomendo sim, sugerido pelo assistente.**
64. Compartilhar o enriquecimento por um arquivo de cada computador numa subpasta "_RADAR (não mexer)", em vez de uma aba na planilha? **Recomendo sim:** ninguém apaga o trabalho do outro.
65. "Visto" fica de cada pessoa (cada um vê o que ele mesmo abriu)? **Recomendo sim;** as outras situações são do escritório, e a mais recente vence.
66. Pode levar ao advogado o texto dos termos 1.2 (amostras)? **Recomendo sim,** antes da 0.7.54.

## Regras conferidas
- Robô só com biblioteca padrão (`secrets`, `os`, `json`) e sem IA.
- Pessoa física: a amostra e a troca não carregam nada que o leitor recusaria.
- Nenhum segredo: a `lex-conta` identifica a instalação por código e instalação, como hoje.
- SQL (`lex_amostras`) só pela Arquitetura, com arquivo datado e o desfazer ao lado.
- Nenhuma página do produto faz pedido externo.
- Não há login nem banco na nuvem para os dados do escritório.
