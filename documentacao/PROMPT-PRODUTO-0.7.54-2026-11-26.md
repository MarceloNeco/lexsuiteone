# Prompt para a Produto: feedback do dono de 26/Nov (0.7.53 em uso)

Copie o texto abaixo e cole na conversa da Produto.

---

Produto, feedback do dono de 26/Nov, com a 0.7.53 em uso no escritório. São 5 itens para a próxima versão. A Operação já mediu as causas e escreveu as propostas.

1. Rode `git pull` e leia `docs/QUADRO.md`, em "Pedidos entre sessões", os cinco pedidos "Operação → Produto (26/Nov, …)". Eles têm os arquivos, as linhas, as medições e as propostas.
2. Pode fazer na mesma versão (0.7.54, ou a próxima livre), nesta ordem:
   a) **Desempenho, causa única.** `radar.data_de_referencia` (`radar.py:1144`) e `radar.py:1103` chamam `sinal_guardado(lead)` mesmo quando o processo já tem o `sinal` guardado. Isso refaz `sem_acento` no texto inteiro do Diário 4 vezes por processo.
      - Corrigir: usar `lead.get("sinal") or sinal_guardado(lead)` e calcular uma vez por processo dentro do mesmo `montar_radar`.
      - Ensaio da Operação com 53 mil processos fictícios: limpar a planilha caiu de 74 para 7 s; o Arquivo de 36 para 3 s; a Lista de 15 dias de 1,7 para 0,17 s.
      - Acrescentar um teste de tempo com cerca de 50 mil processos fictícios.
      - `armazenamento.limpar` monta a lista 3 vezes: reaproveitar.
   b) **Lista: trocar de período.** `trocarPeriodo`/`carregar` (`radar_modelo.html:2931-2977`) só reaproveitam o período exato. Ao ir de 15 para 7 dias, usar o maior período que já está na memória e filtrar no navegador pela data no Diário. Só pedir ao programa quando o período novo for maior.
   c) **Agrupar por empresa.**
      - `post()` (`radar_modelo.html:3009`) apaga `cacheEmp` em QUALQUER gravação: abrir a ficha (marca Visto), mudar a situação, trocar o período. Os blocos perdem os anteriores, "contraem" e buscam todas as empresas de novo.
      - Atualizar o processo dentro do cache. Apagar só a empresa afetada, e só quando muda quem pertence a ela (CNPJ provável, excluir, copiar contato). Nunca apagar no `dias_na_pagina`.
      - Quando a busca chegar, redesenhar só os blocos que mudaram, sem perder a rolagem nem os blocos abertos.
      - Pôr um bloco novo no `fluxos.js` que reproduza o problema: agrupar, expandir, esperar os anteriores, clicar num processo de baixo. O bloco tem de continuar aberto e na mesma posição.
   d) **Inglês contextual.**
      - A etiqueta `fonte_receita: "Revenue"` (`radar_modelo.html:2403`) passa a "TAX REGISTRY".
      - Os cerca de 15 "Federal Revenue" do programa passam a "federal tax registry", como o site já diz (`paginas/index.html:365`). Na primeira menção de cada tela, "federal tax registry (Receita Federal)".
      - O "revenue" do porte (faturamento) fica como está.
      - Regra para todo o EN: traduzir pelo contexto jurídico brasileiro, não ao pé da letra. Revise também os outros termos da tela em inglês.
   e) **Ordenar pelos mais antigos.** Opção nova "Mais antigos primeiro (ajuizados)" / "Oldest first (filed)", logo abaixo de "Mais novos primeiro (ajuizados)".
      - Os processos sem data de ajuizamento vão para o fim; desempate pelo maior valor.
      - Vale também no `comparador` ("Depois por"), nos filtros salvos e no CSV.
3. **Definition of done, com a folha `documentacao/dod/<versão>.md` preenchida.**
   - Manual: "Ordenar por" e os termos em inglês.
   - AssistONE: ajuda da Lista, busca "mais antigos"/"oldest".
   - Novidades, curtas: "Melhoria de desempenho da Lista, do Arquivo e da limpeza da planilha"; "Correção do agrupamento por empresa ao abrir processos"; "Opção de ordenar pelos processos ajuizados há mais tempo"; "Correção de termos em inglês".
   - Termos e e-mail: sem mudança.
   - Banco: sem tabela nova. Se precisar de índice no banco para a busca das empresas, peça antes à Arquitetura.
4. Rode `cd robo && python -m unittest discover -s testes` e `bash robo/testes/tela/rodar_tudo.sh` (tem de terminar em TUDO OK). Depois passe o revisor e anote no quadro "pronta para publicar" com o commit. Não publique: quem publica é a Operação, com o "publica a versão X" do dono.
5. No fim, me diga em até 5 linhas o que mudou e o que eu testo no Windows (no notebook do escritório):
   - limpar a planilha e medir o tempo;
   - trocar de 15 para 7 dias;
   - agrupar por empresa e clicar num processo de baixo;
   - ver a ficha em inglês;
   - ordenar pelos mais antigos.
