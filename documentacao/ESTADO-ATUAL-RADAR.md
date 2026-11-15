# Estado atual do RADAR JUDICIAL (uma página; toda sessão lê antes de responder ao dono)

Atualizado em 15/Nov/2026 pela Produto (criada pela Arquitetura). **Quem mantém: a Produto**, a cada entrega ou decisão nova, e sempre
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
- Filtro de cidade: Lista e Painel, não na planilha. Tarefa agendada sempre por `C:\LexSuiteONE\tarefa.xml`.

## 3. Planejado
- **0.7.48** (só depois dos testes da 0.7.47 e do "pode codar" do dono): leitura pela consulta quando o caderno cai; limpeza
  automática; filtro de cidade; links da página de antivírus; ajustes do instalador. Mais os 11 ajustes da janela "Trazer dados da área logada"
  do teste do dono de 15/Nov (`FEEDBACK-TESTE-0.7.47.md`: janela arrastável, voltar aos passos, pedido rápido com indicador de
  carregamento, ícone de copiar, (?) do .md, botões mais claros, área de arrastar arquivo, sócio marcado, (?) na frente, limite na
  caixa "Quantos"). **Protótipo (Arquitetura):**
  `documentacao/prototipos/0.7.48/prototipo.html`; o dono quer ver antes de mandar codar.
- **Sem data**: varredura pela área logada (PJe e Astrea) dos processos recentes sem contato ou valor:
  `PLANO-VARREDURA-AREA-LOGADA-SEM-DATA.md`. Depende do teste de 5 min no PJe (consulta de terceiros).
- Depois da KR Law: staging e CI/CD (`DESENHO-STAGING-RADAR-2026-11-12.md`). Central LexSuiteONE: espera o repositório próprio.

## 4. O que só o dono pode fazer (lista única)
1. Testar a 0.7.47 no Windows (seção 5) e depois escrever na Produto "pode codar a 0.7.48".
2. Ver o protótipo da 0.7.48 e dizer se cobre a jornada.
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
