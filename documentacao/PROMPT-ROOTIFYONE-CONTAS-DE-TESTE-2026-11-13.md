# Prompt para a conversa do RootifyONE (colar inteiro) · contas de teste · 13/Nov/2026

```
Pedido do dono (13/Nov), vindo da Arquitetura do LexSuiteONE: contas de teste dentro da produção. Primeiro me diga COMO ESTÁ
no RootifyONE hoje e depois faça a parte da tela. Não aplique SQL: o banco é da Arquitetura do LexSuiteONE; se precisar de
função nova, escreva o SQL no seu repositório e me devolva o caminho para eu levar.

O QUE JÁ ESTÁ NO BANCO (aplicado em 12/Nov, desenho em lexsuiteone/documentacao/DESENHO-CONTAS-DE-TESTE-2026-11-12.md):
- Coluna `teste` (boolean, padrão false) em `lex_contas` (licenças do RADAR), `assinaturas` (pessoas dos apps web) e
  `sol_feedback` (chamados e feedback; esta se marca sozinha por gatilho, a partir de `aparelho.licenca` ou de `pessoa_id`).
- `admin_lex_listar()` devolve `teste`; `admin_lex_salvar(p)` grava `teste` (evento "conta de teste: sim/não");
  `admin_lex_criar(escritorio, validade, max_pessoas, email_boas_vindas, dominios, p_teste)` cria a licença já marcada.
- `admin_sol_retorno` e `admin_feedback_painel` excluem contas de teste dos números e devolvem `sem_contas_de_teste`.
- A licença "Teste Marcelo (SolverONE)" está marcada como teste; a KR Law é real.
- Regra: conta de teste funciona igual a uma real (e-mail, aceite, leitura, chamados); só fica fora de números, cobrança,
  planos, métricas e CRM, e sai no "limpar dados de teste" quando o staging existir (nunca antes, e só com cópia e o meu "pode").

1. DIAGNÓSTICO (responda antes de mexer, em até 10 linhas): onde o RootifyONE mostra, conta ou cobra licenças, pessoas,
   chamados e feedback hoje (Licenças do RADAR, ficha, fila de chamados, painéis, planos/assinaturas, "limpar dados de
   teste", relatórios), e em quais desses lugares a conta de teste ainda aparece misturada com as reais.

2. TELA (depois do diagnóstico, com os 5 pontos da definição de pronto e PR como sempre):
   a. Ficha da licença: interruptor "Conta de teste" (lê `teste` de admin_lex_listar, grava por admin_lex_salvar); ao criar
      licença, caixa "Conta de teste" chamando a versão de admin_lex_criar com `p_teste`.
   b. Lista de licenças e fila de chamados: etiqueta "TESTE" discreta e inconfundível; filtro "ocultar contas de teste".
   c. Painéis e números: mostrar "sem contas de teste" quando a função devolver `sem_contas_de_teste`; nenhum número do
      RootifyONE conta conta de teste (licenças ativas, pessoas, computadores, chamados, retorno, assinaturas).
   d. Ficha da pessoa dos apps web: interruptor "Pessoa de teste" gravando `assinaturas.teste` (função admin nova no seu
      SQL, que eu levo à Arquitetura para aplicar); planos e cobrança ignoram pessoas de teste.
   e. "Limpar dados de teste": passa a selecionar por `teste = true` e fica DESLIGADO até o staging existir (botão visível
      com aviso "disponível depois do staging"); nunca apaga nada agora.
   f. Manual, AssistONE (ajuda, tour, busca: "conta de teste", "pessoa de teste"), Novidades da versão em linguagem formal;
      e-mails e termos sem mudança (a conta de teste recebe os mesmos e-mails).

3. AO TERMINAR, me devolva em até 10 linhas: o diagnóstico, o que entrou, a versão publicada e o caminho do SQL novo (se
   houver), para eu levar à Arquitetura do LexSuiteONE.
```
