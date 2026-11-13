# Retorno do dono no teste da 0.7.36 (13/Nov/2026) — vai para a 0.7.37

1. **Painel: filtro que aparecia do nada.** Ao tirar um setor clicando no gráfico "Setores", surgia "7 setores ✕" em
   "Mais filtros", onde antes não havia filtro de setor. Causa: desde a 0.7.33 o Painel escondia os filtros que os
   gráficos também mudam e só os mostrava quando ligados. Correção (feita): no Painel, Situação, Vara, Setor, Porte e
   Estado ficam sempre à vista (Situação na primeira linha, os outros em "Mais filtros"); o clique no gráfico só muda um
   filtro que já está ali. Tribunal e Data continuam em "Estes números".
2. **Painel: faltava Situação para escolher.** Resolvido pelo item 1. A pizza de Situação só não se mexe quando todos os
   processos estão numa situação só (por exemplo, todos "Novo"): o RADAR não deixa um clique esvaziar o Painel. A
   confirmar com o dono no próximo teste.
3. **Configurações: parágrafo de abertura inútil e desatualizado** ("O código de cliente, onde fica a planilha…"; o código
   foi para Licença e termos). Correção (feita): sem o parágrafo; a janela começa direto em "Processos".
4. **Configurações mais larga.** Correção (feita): de 1100 para 1280 px no computador (continua 96% da tela em telas menores).
5. **Empresas excluídas: "Procurar na lista" repetido** acima do campo "Procurar na lista de excluídas". Correção (feita): o
   rótulo visível saiu (fica só para leitor de tela).

Ressalvas da Operação que já esperavam a 0.7.37: "Gravando em" na linha de andamento; faixa de andamento a 360 px.
