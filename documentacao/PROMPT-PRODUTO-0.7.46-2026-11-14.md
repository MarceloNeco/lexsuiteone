# Prompt para a conversa da Produto (colar inteiro) · 0.7.46 · Área logada v2 · 14/Nov/2026

```
Prioridade do dono (14/Nov): a 0.7.46 é a "Área logada v2". Antes de tudo: git pull e leia docs/QUADRO.md inteiro.

ARTEFATOS (todos na main):
1. documentacao/DESENHO-AREA-LOGADA-V2-2026-11-14.md: o que já existe (seção 1), o que falta (seção 2), as correções do teste do
   dono na 0.7.45 e as regras novas (seção 2b: limite por sessão, memória do que foi pedido, filtro e selo, nunca apagar, relatório
   "o que mudou", menu com Gerar pedido e Trazer resposta, arquivo, fluxo que não trava a tela), o interruptor por licença (2c).
2. documentacao/prototipos/area-logada/prototipo.html: a experiência de tela (abra no navegador e percorra os 4 passos, a faixa de
   pedido pendente e o resultado). É a referência; o visual final segue o padrão do RADAR.
3. documentacao/visita-kr-law/PROMPT-PJE-AREA-LOGADA-V2.md: o texto do pedido (roteiro real do PJe) que vai embutido em
   contatos.PEDIDO_V1, com cabeçalho "lote N de M" e variante por tribunal (TRT = mapa pjekz; outros = roteiro genérico).
4. documentacao/prototipos/area-logada/pedido-pje-exemplo-0.7.46.md e resposta-exemplo-0.7.46.md: como o pedido e a resposta
   ficam (fictícios).
5. documentacao/prototipos/area-logada/resposta-simulada-TESTE-0.7.45.md: resposta com conversa em volta, emoji, acentos, CPF,
   reclamante, dado inventado, processo fora da lista, linha repetida, lote com coluna a mais: vira teste automatizado do leitor
   (o topo do arquivo diz o que deve ser aceito e recusado).

O QUE ENTREGAR:
a. Defeitos da 0.7.45: (?) da barra de lote abrindo fora da tela e rolando com a lista (abrir para cima, fixo); janela "Pedido
   pronto" aparecendo mais de uma vez e sem o texto; "8 colunas" → tabela v1 de 7 colunas; não abrir a pasta sozinho.
b. Passo 1 (escopo): só os marcados / os primeiros N da lista filtrada / os próximos N que ainda não foram ao PJe; quais dados;
   limite POR PEDIDO (padrão 25, máximo 50; Configuração → Área logada), em lotes de 25; contagem, nº de lotes e tempo estimado.
   Nada de "por dia": cada pedido é uma sessão do PJe (login com token USB expira).
c. Passo 2: ferramenta (Claude in Chrome / Codex / outra, só rótulo), caixa com o pedido e "Copiar de novo", "Salvar como
   arquivo", 3 instruções; botão "Fechar e voltar quando tiver a resposta" (não trava a tela) e "Já tenho a resposta".
d. Pedido pendente: faixa no alto da lista "pedido de <data> (<n> processos) aguardando resposta" com "Trazer resposta" e
   "Cancelar"; gravado em disco (sobrevive a fechar o programa); menu ☰ → Área logada com "Gerar pedido…" e "Trazer resposta…".
e. Passo 3: colar texto OU subir arquivo (.md, .txt, .zip com .md/.txt; até 20 MB; zipfile da biblioteca padrão); o leitor acha
   todos os blocos "RESPOSTA PARA O RADAR v1" em qualquer ordem, com conversa em volta; lotes em dias diferentes; se não achar
   bloco nenhum: "Não achei a tabela RESPOSTA PARA O RADAR v1 neste texto" + 3 primeiras linhas do que chegou; formato parecido
   mas diferente: aceita o reconhecível e lista o resto como recusado com motivo, nunca trava.
f. Passo 4 (resultado): barra por lote; totais (pedidos, com dado novo, nada no processo, tentar depois, recusadas com motivo);
   achados por tipo de dado; tabela "o que mudou" por processo (acrescentado / alterado com antes → depois / igual); botões "Ver
   na lista" e "Novo pedido só com o que faltou". Regra: nunca apagar; substituir só por fonte mais forte (PJe dados do processo >
   petição > citação > Receita > digitado) ou mais nova; o anterior vai para o histórico da ficha.
g. Lista: memória por processo e dado (pedido em / respondido em / resultado); filtro "Área logada: ainda não pedido / com dados /
   nada no processo / tentar depois" (só aparece depois do 1º resultado); selo "área logada · <data>" no cartão.
h. Interruptor por licença: data-recurso="area-logada" na barra de lote, no menu Área logada e no botão do cartão; some quando
   recursos["area-logada"] === false na resposta da licença (a nuvem e a ficha do RootifyONE são da Arquitetura; até lá, tudo
   ligado).
i. Definição de pronto (CLAUDE.md, 12 pontos onde aplicável): manual (seção Área logada reescrita), AssistONE (ajuda, tour, busca:
   "área logada", "pedido", "trazer resposta", "subir arquivo", "lote", "pendente"), Novidades formais e curtas, termos SEM mudança
   (seção 5 da 1.0 descreve o fluxo), e-mail sem mudança. Testes: 48 processos → 2 lotes; a resposta simulada do item 5 com os
   aceites e recusas previstos; 2 blocos em ordem trocada; .zip com dois .md; pedido pendente sobrevive a reiniciar; selo e filtro;
   substituição por fonte mais forte com histórico; recurso desligado esconde os 3 lugares.

Ao terminar, anote "pronta para publicar" no quadro com o commit e a lista do que foi conferido; a Operação revisa e publica
com o "publica a versão 0.7.46" do dono. Dúvida de desenho vai como pedido à Arquitetura no quadro, não ao dono.
```
