# Prompt de sincronização (colar inteiro na Produto e na Operação) · 14/Nov/2026, noite

```
Sincronização da Arquitetura (14/Nov, noite). Antes de tudo: git pull e leia docs/QUADRO.md inteiro (seção Arquitetura, Feito 11 e 12;
Pedidos entre sessões de 14/Nov; Decisões do dono de 14/Nov).

APLICADO NA NUVEM HOJE (com o "pode aplicar" do dono):
1. Recursos por licença (área logada): lex_contas.recursos, admin_lex_listar/salvar com recursos e eventos por recurso, lex-conta v19
   devolvendo `recursos` com a licença por cima do global, recursos-do-app.json com "area-logada" (padrão desligado). KR Law começa
   DESLIGADA; licença de teste ligada. A ficha do RootifyONE (0.18.31) liga e desliga.
2. Nuvem da 0.7.47: lex-conta v20 (ação estado_cnj explícita, 1 por 5 min por instalação, resposta {ok, total, fora: [..], desde:
   "HH:MM", hora, consulta} em `estado_cnj` e em `estado`, mais `avisos`; registro com antivirus, antivirus_ligado "sim"/"não" e sinal;
   verificar grava avisar_cnj), SQL (lex_registros, lex_instalacoes.avisar_cnj, lex_avisos_gerais preparada, lex_saude_consulta,
   lex_saude_quedas, lex_saude_alertas, função lex_saude_estado) e lex-saude v3 (alerta à SolverONE quando 6+ tribunais caem em duas
   rodadas; e-mail às instalações que marcaram quando a queda passa de 4 h em dia útil, um na queda e um na volta; sonda da consulta
   pública um tribunal por rodada). Registro: nuvem/supabase/2026-11-14-lex-recursos-por-licenca.sql e
   nuvem/supabase/2026-11-14-nuvem-0747-cnj-antivirus.sql.
3. Página do site judicial.solverone.com.br/antivirus.html (13 antivírus, fonte oficial, texto para a TI), já no ar.

DECISÕES REGISTRADAS (Decisões do dono, 14/Nov):
- 34 a 39 (CNJ e antivírus): sem certificado por enquanto; faixa + opção de e-mail em Configuração; página e linha no e-mail: sim;
  leitura pela consulta por padrão (0.7.48); aviso geral do CNJ só preparado; falso positivo aos fabricantes aguarda.
- 21 a 28 (visita à KR Law): 21 o uso da extensão no PJe é escolha do escritório (termos, seção 5), limite por pedido (25, máx. 50);
  22 processos de terceiros sim (é o propósito; o limite por pedido contém o risco); 26 ordem A (feito), C e B conforme o Leandro
  responder; 27 nada se apaga, tudo fica só com o dono fora do repositório; 28 petição inicial é fonte "a conferir", cadastro da
  parte tem prioridade. 23, 24 e 25 continuam ABERTAS: são perguntas ao Leandro (Astrea e Aurum); o dono entrega quando quiser.
- 40 a 42 (limpeza automática): desenho curto em documentacao/DESENHO-LIMPEZA-AUTOMATICA-2026-11-14.md (o que é "trabalhado", o que
  vai junto, memória processos_apagados, prazos em config.radar, tela Armazenamento). Termos NÃO mudam; manual muda.
- Desvio do XML da tarefa agendada ACEITO (sempre C:\LexSuiteONE\tarefa.xml). Filtro de cidade NÃO vale na planilha.

O QUE CADA SESSÃO FAZ AGORA:
- Produto: (a) 0.7.47 já está no formato da lex-conta v20 (testado); se a 0.7.47 já saiu, nada a mudar; (b) 0.7.48 = leitura pela
  consulta quando o caderno cai (desenho 1.3), limpeza automática (desenho curto), filtro de cidade (Lista e Painel), links da página
  de antivírus (index, manual, e-mail), data-recurso="area-logada" nos três lugares + conferência de 30 min/foco/F5 se não entrou na
  0.7.47; (c) revisar e limpar a própria lista "Preciso do dono" no quadro.
- Operação: (a) publicar a 0.7.47 com o "publica" do dono (trazer o commit dos instaladores, como a Produto pediu); (b) conferir no
  Supabase, nos próximos dias, lex_saude_consulta crescendo 1 linha por rodada e lex_saude_alertas sem alerta falso; (c) falso
  positivo aos fabricantes: NÃO fazer (decisão 39: aguardar); (d) revisar e limpar a própria lista "Preciso do dono" no quadro.
- Arquitetura: desenho 1.3 detalhado para a 0.7.48 se a Produto pedir; staging depois da KR Law; Central (admin_lex_central já lê
  lex_saude_diarios; pode passar a ler lex_saude_consulta e lex_saude_quedas quando a Produto quiser a aba).

O QUE AINDA DEPENDE DO DONO (lista única, seção Arquitetura → "Preciso do dono"): entregar ao Leandro as perguntas 23 a 25 e o prompt v2
do PJe; painel do Supabase (TOTP, signups, usuários da equipe; segunda pessoa da equipe); repositório central-lexsuiteone; "aplicado"
no RootifyONE e os prompts pendentes de lá; "pode" do staging depois da KR Law.
```
