# Prompt para a conversa da Produto (colar inteiro) · 0.7.48 · 15/Nov/2026

```
Dono (15/Nov): "produto aprovado, pode codar a 0.7.48". Antes de tudo: git pull; leia documentacao/ESTADO-ATUAL-RADAR.md,
docs/QUADRO.md (Pedidos Arquitetura → Produto de 14 e 15/Nov; Decisões 14 e 15/Nov) e abra o protótipo aprovado:
documentacao/prototipos/0.7.48/prototipo.html (4 abas; cada uma começa com a caixa "Onde fica no RADAR": caminho de cliques,
vizinhos e conflitos). O protótipo é a referência de jornada e de palavras; o visual final segue o padrão do RADAR.

ARTEFATOS:
1. documentacao/DESENHO-LEITURA-E-ANTIVIRUS-2026-11-14.md, seção 1.3 (leitura pela consulta pública) e "Aplicado em 14/Nov".
2. documentacao/DESENHO-LIMPEZA-AUTOMATICA-2026-11-14.md (limpeza automática: o que é "trabalhado", o que vai junto, memória
   processos_apagados, ordem, prazos, tela, DoD).
3. robo/PENDENCIAS.md, seção 0.7.48 (filtro de cidade: desenho rápido; ajustes do instalador: ressalvas 3 a 5 da Operação).
4. Nuvem já no ar: lex-conta v20 devolve em estado_cnj o campo `consulta` {tribunal, estado, hora} (sonda da consulta pública do
   observador); use-o para não tentar a consulta quando a SolverONE também a vê fora.

O QUE ENTREGAR NA 0.7.48:
a. Leitura pela consulta pública quando o caderno cai (aba 3 do protótipo; desenho 1.3; decisão 37: ligada por padrão, só na leitura
   automática e no "Ler o Diário agora"; opção para desligar em Configurações → Leitura do Diário). Gatilho: caderno do dia com 5xx e
   consulta respondendo (e o observador não a vê fora). GET comunicacao por tribunal e dia, itensPorPagina 100, 1 pedido por segundo,
   15 s de limite, 1 nova tentativa só em timeout e 5xx, parar depois de 3 timeouts seguidos; se count chegar a 10.000, dividir por
   vara (orgaoId), com a lista de varas montada dos cadernos já lidos e guardada no banco. As comunicações entram no mesmo formato,
   marcadas fonte "consulta pública" e "caderno pendente"; quando o caderno voltar, a próxima leitura confere pelo caderno e completa
   sem duplicar (chave da comunicação). As quatro cenas na faixa do alto (faixa-topo): (1) falhou, com diagnóstico e "A SolverONE
   também vê" (já existe); (2) "Lendo pela consulta pública (vara por vara)…" com andamento e "Interromper", tela livre; (3) "Diário
   de hoje lido pela consulta: N processos novos" + "Ver os N processos" (Lista filtrada "novos desta leitura"); (4) "Caderno do CNJ
   voltou (HHhMM). Conferência feita: nada faltou" ou "N processos a mais, já incluídos". Histórico de leituras ganha a linha "Leitura
   pela consulta pública" e a da conferência. Confirmar na prática o limite de itensPorPagina e páginas vazias; anotar na PENDENCIAS.
b. Faixa do alto, em todas as cenas e também na 0.7.47 que já existe: texto na largura toda da faixa; "Detalhes técnicos" e demais
   ações embaixo do texto, em azul de link; vale minimizado e maximizado (feedback do dono, 15/Nov).
c. Limpeza automática (aba 1 do protótipo; desenho curto; decisões 40 a 42): resumir com 6 meses, apagar a linha com 24 meses, menos os
   trabalhados (situação diferente de Novo, contato, anotação, pedido ou resposta da área logada; "visto" não conta); roda depois de
   cada leitura, sempre depois de atualizar_estatisticas; estatísticas_diarias nunca são tocadas; filhos (contatos_historico, acoes,
   area_logada, publicações do monitor) saem junto; memória processos_apagados (só número do processo e datas, 12 meses) para não voltar
   como novo; VACUUM depois; registro "limpeza" no Histórico de leituras (quando, resumidos, apagados, mantidos por trabalhados, tamanho
   antes → depois). Prazos em config.radar (resumir_meses padrão 6, mínimo 1; apagar_meses padrão 24, mínimo 6, 0 = nunca;
   apagar >= resumir). Tela: dentro da seção Armazenamento que já existe, abaixo das cópias de segurança: os dois prazos com (?),
   "O que nunca sai", "Última limpeza" (tabela) e o botão "Limpar o banco agora" com confirmação em dois cliques na própria tela (sem
   janela do navegador), que não trava a tela. Primeira limpeza grande roda depois da leitura com "Limpando o banco…".
d. Filtro de cidade (aba 2 do protótipo; PENDENCIAS 0.7.48): na barra de filtros da Lista, logo à direita de Estado; opções do índice
   estado → cidades montado uma vez por carga; busca por digitação sem acento e sem maiúsculas; cidades com mais processos primeiro,
   com a contagem; "Sem cidade"; cidade que não existe no estado novo é limpa com aviso; filtros salvos guardam a cidade; o Painel obedece;
   a planilha NÃO muda. Conferir com 60 mil processos no teste de tela com rede lenta.
e. Textos (feedback do dono, 15/Nov): Armazenamento, "Tudo certo." vira "Tudo certo: planilha abaixo de 80 % do limite e espaço no
   disco". Leitura do Diário, opção do e-mail do CNJ: mostrar o endereço de verdade ("O aviso vai para <e-mail do cadastro deste
   computador>; um e-mail na queda e um na volta"); sem cadastro, caixa desligada com "cadastre-se primeiro".
f. Página de antivírus: links na index.html (perto do pacote completo) e no manual (instalação e "Não consegui criar a leitura
   automática"), se ainda não entraram; linha no e-mail de boas-vindas (se o arquivo for da Operação, pedido no quadro com o texto).
g. Instalador: ressalvas 3 a 5 da revisão da Operação (PENDENCIAS 0.7.48).
h. Definição de pronto (CLAUDE.md, 12 pontos onde aplicável): manual (a linha "depois de 12 meses" vira 6 e 24 meses, o que nunca sai,
   onde se ajusta; seção de privacidade do manual; leitura pela consulta pode demorar e ser completada depois; filtro de cidade;
   Armazenamento), AssistONE (ajuda de Armazenamento e da faixa; tour; busca: "limpeza", "apagar", "cidade", "consulta pública",
   "caderno pendente"), Novidades formais e curtas, termos SEM mudança (banco local é do escritório, seção 4; retenção da nuvem não
   muda), e-mail de boas-vindas sem mudança além da linha do antivírus. Testes: consulta com respostas gravadas (count 10.000 → divisão
   por vara; 3 timeouts → para; páginas vazias; conferência pelo caderno sem duplicar); limpeza (trabalhado nunca sai; visto sai;
   filhos saem junto; processos_apagados impede volta; estatísticas intactas; prazos inválidos recusados; 0 = nunca); cidade (índice,
   busca sem acento, troca de estado limpa com aviso, Painel obedece, planilha igual); rodar_tudo.sh TUDO OK.
i. Ao terminar: atualizar documentacao/ESTADO-ATUAL-RADAR.md (no ar, planejado, testes do dono para a 0.7.48, 6 passos no máximo),
   anotar "pronta para publicar" no quadro com o commit e a lista do que foi conferido; a Operação revisa e publica com o "publica a
   versão 0.7.48" do dono. Dúvida de desenho vai como pedido à Arquitetura no quadro, não ao dono.
```
