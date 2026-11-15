# Estado atual do RADAR JUDICIAL (uma página; toda sessão lê antes de responder ao dono)

Atualizado em 15/Nov/2026 pela Produto, com a 0.7.48 pronta (criada pela Arquitetura). **Quem mantém: a Produto**, a cada entrega ou decisão nova, e sempre
que o dono pedir "o que falta". A resposta ao dono sobre "o que tem para fazer" sai DAQUI, não da memória da conversa.

## 1. No ar
- Programa **0.7.47** (com a 0.7.46 Área logada v2 dentro), publicada em 14/Nov; instalador novo no site.
- Nuvem: lex-conta v20 (recursos por licença, estado do CNJ, antivírus no registro, opção de e-mail), lex-saude v3 (observador em São
  Paulo com alerta e sonda da consulta), página `judicial.solverone.com.br/antivirus.html`. Área logada: KR Law **desligada**, teste
  ligada (liga-se na ficha do RootifyONE).

## 2. Decidido (não perguntar de novo)
- Área logada: limite por pedido (25, máx. 50), nunca por dia; processos de terceiros, sim; petição inicial é fonte "a conferir".
- Prints e zips da visita: ficam só com o dono; nada se apaga; nada no repositório.
- Astrea e Aurum: **adiado**; não procurar a Aurum agora (dono: "ainda não estou maduro"). Dossiê: `DOSSIE-ASTREA-MCP-AI-2026-11-15.md`.
- CNJ e antivírus: sem certificado por enquanto; aviso geral só preparado; falso positivo aos fabricantes aguarda; leitura pela
  consulta por padrão (0.7.48).
- Limpeza automática (40 a 42): resumir 6 meses, apagar 24, trabalhados nunca saem, prazos em Armazenamento; termos não mudam.
- Janelas do programa: arrastar pelo título e mudar o tamanho; ao reabrir, sempre centro e tamanho padrão (15/Nov). Os 14
  ajustes do teste da área logada entram na 0.7.48.
- Filtro de cidade: Lista e Painel, não na planilha. Tarefa agendada sempre por `C:\LexSuiteONE\tarefa.xml`.

## 3. Planejado
- **0.7.48 pronta para publicar** (15/Nov; a Operação publica quando o dono escrever "publica a versão 0.7.48"; instaladores novos
  vão junto, da branch): leitura pela consulta pública quando o caderno cai; limpeza automática do banco; filtro de cidade; os 14
  ajustes da área logada; janelas arrastáveis; faixa com ações embaixo; textos de Armazenamento e do aviso do CNJ; ressalvas 3 a 5
  dos instaladores. Testes do dono na seção 6. A conferir no primeiro uso real: o limite de 100 por página da consulta.
- **Sem data**: varredura pela área logada (PJe e Astrea) dos processos recentes sem contato ou valor:
  `PLANO-VARREDURA-AREA-LOGADA-SEM-DATA.md`. Depende do teste de 5 min no PJe (consulta de terceiros).
- Depois da KR Law: staging e CI/CD (`DESENHO-STAGING-RADAR-2026-11-12.md`). Central LexSuiteONE: espera o repositório próprio.

## 4. O que só o dono pode fazer (lista única)
1. Terminar os testes da 0.7.47 no Windows (seção 5) e, depois de publicada, os da 0.7.48 (seção 6); o que falhar vira feedback na Produto.
2. Escrever "publica a versão 0.7.48" na conversa da Operação, quando quiser.
3. Quando quiser: teste de 5 min no PJe com advogado logado (`visita-kr-law/PROMPT-TESTE-GAP-PJE-2026-11-15.md`).
4. Supabase (Central): TOTP, desligar signups, usuários da equipe; repositório `central-lexsuiteone`.
5. RootifyONE: "aplicado" (recursos por licença) e os prompts pendentes de lá.

## 5. Testes pendentes da 0.7.47 (num Windows, ~20 min)
1. Instalador aberto de dentro do zip: avisa e para.
2. Instalação normal: "Antivírus encontrado: …" antes do código; passo 5 de 6 cria a leitura automática.
3. Agendador de Tarefas: tarefa LexSuiteONE Radar, autor SolverONE; `C:\LexSuiteONE\tarefa.xml` existe.
4. Configurações → Sobre este computador: antivírus, firewall, link da página, recursos da licença. (feito pelo dono em 15/Nov)
5. Configurações → Leitura do Diário: opção de e-mail do CNJ, salva e persiste.
6. Área logada: 4 passos, pedido pendente sobrevive ao fechar, resposta simulada (`prototipos/area-logada/resposta-simulada-TESTE-0.7.47.md`, com o passo a passo) gera o relatório "o que mudou". (passos 1 e 2 feitos pelo dono em 15/Nov; achados em `FEEDBACK-TESTE-0.7.47.md`)
7. Liga e desliga por licença na ficha do RootifyONE: os três lugares somem e voltam (passo a passo em `TESTES-DO-DONO.md`).

## 6. Testes da 0.7.48 (depois de publicada, num Windows, ~15 min)
1. Lista → marcar 2 processos → "Trazer dados da área logada": arraste a janela pelo título e mude o tamanho pelo canto; feche e
   abra de novo: volta ao centro. Os círculos 1 a 4 têm nome; "Sócio ou administrador" vem marcado; "Gerar o pedido" é rápido.
2. No passo 2: ícone de copiar no canto da caixa, (?) do .md, botões "Colar a resposta agora" e "Fechar (trago a resposta depois)".
   No passo 3: área "Arraste o arquivo aqui"; arraste `resposta-simulada-TESTE-0.7.47.md` (troque os números, como diz o arquivo).
3. Lista → Mais filtros → Cidade (logo depois do Estado): procure uma cidade sem acento; escolha um estado e veja a cidade de
   outro estado sair, com aviso. No Painel, os números seguem a cidade.
4. Configurações → Armazenamento: "Limpeza automática do banco" com 6 e 24 meses; "Limpar o banco agora" pede um segundo clique;
   depois, Ver histórico de leituras mostra a linha "Limpeza".
5. Configurações → Leitura do Diário: "Ler pela consulta pública quando o caderno do CNJ cair" vem ligada; o aviso por e-mail do
   CNJ mostra o seu e-mail. (A leitura pela consulta só aparece de verdade num dia em que o caderno do CNJ cair.)
6. Ajuda → Novidades da versão: a lista da 0.7.48.
