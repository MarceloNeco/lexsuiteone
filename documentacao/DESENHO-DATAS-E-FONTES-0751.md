# Desenho: datas do processo e fontes públicas (0.7.51)

Feito pela Arquitetura (subagente `arquiteto`, pedido da Produto) em 20/Nov/2026. Só leitura do código. A Produto implementa
depois do "pode" do dono. Origem: `documentacao/FEEDBACK-KRLAW-2026-11-16-PRIMEIRO-USO.md`.

## Problema
O 1000910-15.2026.5.02.0714 (ajuizado em 15/05) apareceu como "novo" em 13/11. Três causas juntas:
- `djen.leads` aceita a audiência de conciliação (`classificar._INICIO`) como sinal;
- o único freio de idade é o ano do número CNJ;
- `radar.item_de_lead` monta `distribuida_em = ajuizada_em or data_publicacao`: mostra a data da publicação com o rótulo de
  distribuição. A coluna "Distribuída em" da planilha tem o mesmo defeito.

## 1. Onde guardar (misto, recomendado)
- **Colunas novas em `leads`**: `ajuizada_em` (AAAA-MM-DD) e `ajuizada_fonte` (cnj | diario | area | digitado), no laço de
  `ALTER` que já existe.
- **No JSON `dados.cnj`**: ajuizamento e hora, classe, assuntos, órgão, até 60 marcos `[data, código, rótulo, situação]`, dias
  distintos do código 1061, andamento (vazio | acordo | sentença | trânsito | arquivado) e `consultado_em`.
- **No JSON `dados.diario_hist`**: 1ª e última publicação, número de dias e tipos. Só data, tipo e id; o texto e os destinatários
  se descartam na memória (Res. CNJ 121/2010; pessoa física nunca).
- **Tabela nova `fontes`**: (processo, fonte) como chave; fonte = cnj | diario_hist | receita; campos `estado`, `tentativas`,
  `ultima_em`, `proxima_em`, `ok_em`, `causa`. É a fila em disco, no padrão de `area_logada` e `historico`.
- **Migração**: `user_version` 719 → 751, com `_copia_antes(caminho, "0.7.51")`. Enfileira na `fontes` os leads com
  `fora_criterio = 0` dos últimos 12 meses (os da Lista primeiro). Nada é apagado, escondido ou movido.
- **Retrocompatível**: a 0.7.50 ignora a coluna e a tabela novas (`guardar_lead` nomeia as colunas).
- `cnj` e `diario_hist` entram em `banco._RESUMO`, para a limpeza não apagar.
- **Planilha**: "Distribuída em" vira **"Ajuizado em"** (só a data real; vazia quando não se sabe). Colunas novas no fim:
  - Fonte do ajuizamento;
  - Processo novo ou antigo;
  - 1ª publicação no Diário;
  - Última publicação no Diário;
  - Encontrado pelo RADAR em;
  - Andamento;
  - Classe;
  - Assuntos (CNJ).

  A jornada inteira não vai para a planilha.

## 2. Fluxo (fase dentro da leitura, com tempo máximo e fila)
- Módulo novo `lexsuite/completar.py`, chamado em `radar.executar` depois da Receita e de `guardar_lead`, antes de
  `registrar_consulta` e `gravar_saida`. Respeita `parar`, tempo máximo de 4 min e grava item a item.
- **Ordem**:
  1. CNJ dos novos desta leitura;
  2. histórico no Diário dos que entraram por sinal fraco;
  3. o que falhou antes (`proxima_em` vencido);
  4. o que está "aguardando" (uma vez por dia);
  5. se sobrar tempo, andamento dos ativos com CNJ "ok" há mais de 7 dias.
- **Processo que já está na base**: a leitura do caderno já vê as publicações do dia; atualiza última publicação e dias de
  publicação sem pedido extra.
- **DataJud em lote** (`datajud.por_numeros`):
  - Agrupa por `api_publica_<tribunal>`, 40 números por pedido.
  - Usa `terms` em `numeroProcesso` com os 20 dígitos. **Conferido pela Produto em 20/Nov: funciona**; o mesmo número vem em
    G1 e G2; fica o G1 com a atualização mais recente.
  - `_source` só com os campos usados.
- **Rede desta fase**: `tentativas=2`, intervalo mínimo de 1 s, tempo limite de 30 s.
  - Três falhas seguidas (sem resposta, 429, 5xx, `es_rejected_execution_exception`) param o CNJ nesta leitura. As novas
    tentativas vêm em 30 min, 2 h, 6 h e 24 h.
  - Resposta parcial (`_shards.failed`, `timed_out`, total maior que os documentos recebidos): o número que faltou fica
    "falhou", nunca "não encontrado".
  - Sem a chave pública: "falhou" com a causa "chave do CNJ não lida".
  - Observação de 20/Nov: 4 de 5 pedidos seguidos recusados por excesso, por isso a fila e as novas tentativas são essenciais.
- **Histórico no Diário**: `djen.buscar_filtrado({"numeroProcesso": ...})` do ano do processo até hoje, 1 pedido/s, no
  máximo 120 por leitura.
- **Estados por fonte**:
  - "ok" (com a data);
  - "aguardando": o CNJ não tem o processo, visto há até 15 dias. É atraso normal: sem botão, tenta 1×/dia;
  - "não encontrado": passou de 15 dias. Tenta 1×/dia até 60 dias, com botão;
  - "falhou": em vermelho, com causa curta e "Tentar de novo".
- **Rota `POST /completar`** (processos, fontes): marca `proxima_em = agora`. Se uma leitura estiver rodando, ela pega o
  pedido; se não, roda uma thread curta de 60 s com trava própria.

## 3. Regra de "novo" (função pura, calculada ao montar a página)
- **Referência**, na ordem: ajuizamento digitado ou da área logada; o do CNJ; a data da lista de distribuição do Diário. Sem
  nenhum deles, a 1ª publicação real conhecida.
- **Novo** = referência de até `dias_processo_novo` dias (padrão 30, por área, 1 a 365, na tela Regras). Mudar o limite vale na
  hora; quando o CNJ chega, o cartão muda sozinho.
- Quem entrou por sinal fraco e tem publicação mais antiga que o limite no histórico do Diário é **antigo**, mesmo sem o CNJ.
- **Não entram**: a classe "Cumprimento (Provisório) de Sentença" e a lista "por dependência". Se a classe aparecer depois,
  pelo CNJ, recebe `fora_criterio = 1` só se o processo estiver "Novo", sem dado digitado e sem contato, com registro em `acoes`.
- **Processo antigo**:
  - fica na Lista, marcado "PROCESSO ANTIGO · 6 MESES", e desce pela ordem de ajuizamento;
  - não vai sozinho para o Arquivo;
  - não conta em "N processos novos" nem no aviso do Windows.

## 4. Riscos e testes
- **Carga no CNJ**: 10 a 40 pedidos por leitura, teto de 60.
- **Tempo**: leitura 1 a 4 min mais longa, interrompível.
- **Histórico no Diário**: não dá para testar daqui (bloqueio fora do Brasil). Pôr no DIAGNÓSTICO uma sonda com um número
  público, para o dono rodar uma vez.
- **Conflito de datas**: se o ajuizamento do CNJ for diferente do do Diário, vale o do CNJ.
- **Testes** (unittest com `pedir` injetado e trava que falha qualquer rede):
  - montagem do lote;
  - G1 e G2 repetidos;
  - resposta parcial ou `es_rejected` dá "falhou";
  - três falhas param a fase;
  - marcos TPU com situação e dias do 1061;
  - tabela da regra de novo, incluindo o caso real (dados públicos), limites 30 e 90 e digitado vencendo o CNJ;
  - estados aguardando, não encontrado e falhou;
  - cumprimento de sentença e dependência ficam de fora;
  - migração de um banco fictício da 0.7.50;
  - o histórico nunca guarda texto nem destinatários;
  - planilha, `/dados`, `/completar` e `parar` no meio da fase.

## 5. Para depois, se o escopo pesar
- atualização semanal dos andamentos;
- etiquetas "Já tem acordo", "Já sentenciado" e "Empresa já tem advogado";
- filtro "só lista de distribuição";
- "CNJ atualizado até" por tribunal;
- Painel pelo ajuizamento;
- estimativa pela numeração da vara.

## Decisões do dono pedidas
1. Processo antigo visível e marcado, com "Idade: qualquer" como padrão (recomendado), ou filtro de fábrica "até 30 dias".
2. Limite de 30 dias, ajustável por área na tela Regras (recomendado).
3. Painel deixa de contar processo antigo como ação nova (recomendado para a 0.7.52).

## Termos e LGPD
- Os termos 1.1 citam "fontes públicas (o DJEN e os cadastros públicos de empresas)".
- O DataJud é fonte nova, sem dado pessoal. Não muda a finalidade nem as categorias de dado, então não pede novo aceite.
- O advogado decide se acrescenta o DataJud à lista de fontes já ou na próxima versão dos termos.

## Outros
- Pacote passa a 47 e 46 arquivos (módulo novo): atualizar `CLAUDE.md` (Arquitetura), `docs/PUBLICAR.md` e o teste de contagem.
- RootifyONE, ArchONE e EaglePlanONE:
  - integração nova de leitura com o DataJud (chave pública lida da página do CNJ, nada de segredo);
  - tabela `fontes` e duas colunas novas;
  - "Encerradas pelo DataJud" (decisão de 09/Nov) fica parcialmente adiantado.
