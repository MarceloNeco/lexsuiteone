# Desenho curto: limpeza automática do banco do RADAR (Arquitetura, 14/Nov/2026)

Pedido da Produto (quadro, 14/Nov) depois das decisões 40 a 42 do dono: resumir com 6 meses, apagar com 24 meses, trabalhados
nunca saem, prazos em Armazenamento, estatísticas sempre guardadas. Implementa a Produto (0.7.48). Nada disto toca a nuvem.

## 1. O que muda e o que fica

| Hoje (conferido pela Produto) | Decidido |
|---|---|
| `limpar_antigos(guardar_dias=365)` resume o detalhe com ~12 meses; acima de 1 GB resume os nunca abertos com 6 meses | **Resumir com 6 meses** para todos (texto pesado do Diário sai; fica o resumo: número, tribunal, vara, data, partes com CNPJ, valor, situação, fonte) |
| nada é apagado | **Apagar a linha com 24 meses**, menos os trabalhados |
| 1 GB dispara resumo extra | mantém como segurança (não é regra de negócio; não aparece na tela) |

**Trabalhado** (nunca sai): situação diferente de `novo`; ou contato em `contatos`; ou anotação; ou pedido/resposta da área
logada (`area_logada`); ou situação `arquivado` marcada pela pessoa. "Visto" sem mais nada conta como não trabalhado (o dono: só
"situação diferente de Novo, contato ou anotação"; `visto` é marcado sozinho pelo programa ao abrir a ficha, por isso não conta).

## 2. O que vai junto quando a linha sai (resposta à pergunta 2 da Produto)

Tudo o que só existe por causa daquele processo e não é estatística: `contatos_historico`, `acoes`, `area_logada` (pedidos e
respostas daquele processo), publicações do monitor e linhas da planilha grande (a planilha é regerada da base). Como trabalhado
nunca sai, na prática esses filhos só existem em processos que ficam; a regra é por segurança e consistência (FK `on delete
cascade` ou apagar na mesma transação).

**Memória para não voltar como novo**: tabela `processos_apagados (processo text primary key, apagado_em date, diario_data date)`.
Só o número do processo e duas datas; sem nome, CNPJ ou texto. `importar` confere essa tabela antes de inserir; se o número está
lá, ignora e conta como "já apagado". Guardar por 12 meses depois de `apagado_em` (Diários mais velhos que isso não são relidos
na leitura automática; a leitura manual de um Diário antigo mostraria o processo como novo de novo, o que é aceitável e raro).
VACUUM depois da limpeza (já existe).

## 3. Ordem e onde fica

1. `atualizar_estatisticas()` primeiro (as `estatisticas_diarias` e o gráfico de tendência não dependem das linhas; nunca são
   tocadas pela limpeza).
2. Resumir (6 meses), apagar (24 meses, só não trabalhados), gravar `processos_apagados`, VACUUM.
3. Registro `limpeza` no histórico de leituras: quando, quantos resumidos, quantos apagados, tamanho antes/depois.
4. Prazos em `config.radar`: `resumir_meses` (padrão 6, mínimo 1) e `apagar_meses` (padrão 24, mínimo 6, `0` = nunca apagar), com
   a regra `apagar_meses >= resumir_meses`. Tela: Configurações → **Armazenamento** mostra os dois prazos, a última limpeza
   (quando, resumidos, apagados) e o tamanho do banco.

## 4. Definição de pronto (DoD)

- **Termos**: não mudam. A seção 6 dos termos trata do que a SolverONE guarda (nuvem); o banco local é do escritório, sob o
  controle dele (seção 4), e o prazo é ajustável por ele. Retenção local não é dado tratado pela SolverONE → sem nova versão
  nem novo aceite.
- **Manual** (ponto material do DoD 1): a linha "Depois de 12 meses (ajustável)" passa a descrever 6 e 24 meses, o que nunca sai e
  onde se ajusta; seção de privacidade do manual idem. AssistONE: ajuda de Armazenamento. Novidades: "Inclusão de limpeza
  automática com prazos ajustáveis em Armazenamento".
- **E-mails**: sem mudança.
- **Retrocompatibilidade**: quem já usava passa a resumir com 6 meses e a apagar com 24 na primeira leitura depois de atualizar;
  como nada trabalhado sai e o resumo preserva a ficha, não precisa de aviso prévio. A primeira limpeza grande pode demorar:
  rodar depois da leitura, com a mensagem "Limpando o banco…".

## 5. Filtro de cidade (0.7.48): vale na planilha?

Não. A planilha continua completa (é o registro do escritório, não uma visão); a coluna Cidade já existe nela e o Excel filtra.
O filtro de cidade é só da Lista e do Painel, como o de Estado.
