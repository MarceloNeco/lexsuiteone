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
