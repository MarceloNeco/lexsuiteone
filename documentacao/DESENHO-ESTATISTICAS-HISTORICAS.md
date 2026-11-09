# Desenho curto: "Atualizar estatísticas" (item 82 do feedback de 09/Nov)

Arquitetura, 09/Nov/2026. Para a Produto implementar na 0.7.15. Dono decide os pontos em "Perguntas ao dono" do quadro.

## O que é
Botão no Painel: escolher frente, tribunais e varas, e quanto tempo para trás (1, 3, 6 ou 12 meses). O programa lê os
Diários antigos **só para contar** (data, tribunal, vara, frente; porte e valor só quando já se sabem) e mostra
sazonalidade e picos. Nunca enche a Lista nem o Arquivo; não guarda nome, processo, CNPJ ou pessoa.

## Fatos levantados (09/Nov; os sites oficiais do CNJ recusaram o acesso automático, então o que está marcado
"a conferir" precisa de uma olhada no navegador pelo dono ou pela Operação)
1. **DJEN, caderno por tribunal e dia** (`comunicaapi.pje.jus.br/api/v1/caderno/{sigla}/{data}/D`, o que o robô já usa):
   um pedido por tribunal por dia, devolve o Diário inteiro em ZIP. É o caminho mais leve para o CNJ. **Não achamos
   documentado até quando os cadernos antigos ficam disponíveis** (a conferir: pedir um caderno de 12 meses atrás de um
   TRT pequeno e ver se responde 200 ou 404).
2. **DJEN, limites**: nada oficial publicado. Integradores relatam erro 500 em rajadas e recomendam ~500 ms entre pedidos
   com recuo exponencial; bloqueio (403) para IP fora do Brasil (já tratado em `rede.py`). O caderno do dia só sai às 3h.
3. **DataJud** (`api-publica.datajud.cnj.jus.br/api_publica_{sigla}/_search`, o robô já lê a chave pública na página do
   CNJ): consulta Elasticsearch por `dataAjuizamento`, classe e assunto, até 10.000 por página com `search_after`; termos
   de uso V1.2 reservam ao CNJ o direito de limitar pedidos (uma versão anterior falava em 120 por minuto); atraso típico
   de 30 dias, às vezes mais de 2 meses. **Não filtra por CNPJ e as partes vêm mascaradas**: serve para série longa
   "processos novos por mês, tribunal e classe", não para "contra pessoa jurídica".
4. Volume: 24 TRTs × ~250 dias úteis ≈ 6.000 cadernos por ano; o do TRT2 e o do TRT15 são grandes (dezenas de MB).

## Desenho recomendado
- **Fonte**: DJEN por caderno (igual à leitura normal), porque é a única que identifica a pessoa jurídica ré. DataJud fica
  como fonte opcional de "pano de fundo" (total de processos novos por mês e tribunal, sem distinguir PJ) numa versão
  seguinte, com o aviso do atraso.
- **Fila**: lista de (tribunal, dia) a ler, gravada no banco local; roda **só na janela noturna** (depois das 22h e antes
  das 6h, horário do computador) dentro da mesma tarefa do Windows da leitura noturna; **um caderno por vez**, pausa de
  2 s entre cadernos (ajustável), **30 cadernos por noite** (ajustável em Configuração), retoma de onde parou, barra
  "N de M Diários" e previsão de término ("faltam 4 noites").
- **Pede antes**: para 12 meses × 24 TRTs são 200 noites a 30 por noite; a tela mostra essa conta e sugere escolher
  menos tribunais ou menos meses. Padrão proposto: só os tribunais marcados pelo escritório e 3 meses.
- **Caderno indisponível (404 antigo)**: marca o dia como "não disponível no CNJ" e segue; a estatística mostra o
  buraco. Erro 429/500: espera 10 min e tenta de novo até 3 vezes na noite; depois deixa para a próxima noite.
- **O que grava** (`estatisticas_diarias`): data, tribunal, vara, frente, porte (quando conhecido), faixa de valor
  (quando conhecida), quantidade. Nada mais. Essa é a mesma tabela que já alimenta o "retorno" de totais à SolverONE, então
  os totais históricos **também sobem** no retorno (só contagens).
- **Agendamento periódico**: "atualizar sempre" = a fila recebe, toda noite, os dias que faltam dos últimos 3 meses (cobre
  cadernos republicados). Liga/desliga em Configuração.
- **Respeito ao CNJ**: `User-Agent` identificado (já existe em `rede.py`), 1 pedido por caderno, nunca em horário comercial,
  nunca em paralelo. Se o CNJ publicar limite oficial, ele entra em `rede.py` como constante.

## Perguntas ao dono (copiadas para o quadro)
P10. Padrão de 30 cadernos por noite e pausa de 2 s está bom, ou prefere mais lento (ex.: 15)?
P11. Período padrão 3 meses e só tribunais marcados? Ou 12 meses para a KR Law como primeira carga?
P12. Antes de implementar, alguém (você ou a Operação, no navegador) confere se o DJEN devolve um caderno de 12 meses
     atrás (ex.: TRT21, um dia útil de nov/2025). Se não devolver, o botão limita a escolha ao que existe.
