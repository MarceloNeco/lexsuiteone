# Arquivo, status no banco, limpeza, Estatísticas e frente · desenho curto (Arquitetura, 09/Nov/2026)

Pedido da Produto (quadro, 09/Nov; itens 42 a 45, 51 e 59 de `documentacao/FEEDBACK-TESTE-2026-11-09.md`), lido junto com
`documentacao/PESQUISA-ACESSO-PJE-2026-11-09.md`. Tudo roda **no computador do escritório** (`lexsuite.db`, planilha do
Drive); nada disto vai para a nuvem. **A Produto implementa tela e planilha depois das respostas do dono (seção 6).**

## Em uma frase

A **Lista** passa a ser "o que é novo e ainda não tratei"; o **Arquivo** guarda tudo o que o RADAR já leu, de todos os
tribunais, para sempre em forma resumida; o **status** sai do navegador e vai para o banco do computador, com ações em
lote; a **limpeza** apaga só o dado bruto velho, mostrando o espaço; as **Estatísticas** são totais diários que nunca se
apagam; cada ação ganha a **frente** (trabalhista, tributário, cível, empresarial).

## 1. Lista × Arquivo (item 42)

- Hoje a tabela `leads` do `lexsuite.db` já guarda tudo (uma linha por processo, todos os tribunais); a tela só mostra o
  período e os tribunais escolhidos, por isso parece que "apaga".
- **Arquivo** = todas as linhas de `leads`, de qualquer tribunal, com o mesmo cartão da Lista, busca e filtros (tribunal,
  vara, frente, porte, faixa de valor, status, período). Ordem padrão: mais recente primeiro.
- **Lista** = Arquivo filtrado por status "em aberto" (seção 2) e pelo período da configuração. Nada some: trocar de
  tribunal só muda o filtro.
- Planilha do Drive: aba **Arquivo** com os últimos 12 meses (o mesmo período do dado bruto, seção 4); o Arquivo inteiro
  sai sob demanda pelo botão "Gerar planilha do Arquivo completo" (arquivo à parte, com data, na mesma pasta), para a
  planilha diária não crescer sem fim.

## 2. Status no banco e ações em lote (item 43)

- O status sai do navegador (`localStorage`) e vai para a coluna `leads.status`, que já existe. A tela grava por uma rota
  nova do programa (`POST /status`, com o cabeçalho `X-LexSuite` que já protege as outras rotas), um ou muitos processos
  de uma vez. Valer na planilha e em outra tela vem de graça.
- Status propostos (hoje: Novo, Visto, Em contato, Descartado): **Novo → Lido → Em tratamento → Tratado**, mais
  **Descartado**. "Em aberto" (fica na Lista) = Novo, Lido e Em tratamento. Tratado e Descartado saem da Lista e ficam
  no Arquivo. Nunca se apaga uma ação por status.
- Em lote: caixa de seleção no cartão e "Marcar os N filtrados como…". Passa pela função única `pode('lote')` do
  desenho dos contatos (hoje sempre sim; amanhã por nível de acesso) e grava na tabela `acoes` quem (perfil do
  computador), o quê, quantos e quando (UTC e fuso). Desfazer: "Voltar os N para o status anterior" na mesma sessão.
- Migração: na primeira abertura da versão nova, o que estiver no `localStorage` do navegador é levado para o banco
  (uma vez, com aviso "status trazidos para o programa").

## 3. Estatísticas que não se apagam (item 45)

- Tabela `estatisticas_diarias (data, tribunal, vara, frente, porte, faixa_valor, novas, encerradas, atualizado_em)`,
  chave `(data, tribunal, vara, frente, porte, faixa_valor)`, somada a cada leitura. Pequena: poucas centenas de linhas
  por dia no máximo. **Nunca é apagada** pela limpeza.
- Faixas de valor: as mesmas do filtro da tela (até 10 mil, 10 a 50 mil, 50 a 100 mil, 100 a 300 mil, 300 a 500 mil,
  500 mil a 1 milhão, acima; "sem valor" quando o Diário não traz).
- O gráfico (Produto) lê só essa tabela, por isso responde ao filtro na hora, sem reler o Arquivo.
- **Encerradas**: o Diário de distribuição não informa fim de processo. Fonte possível: a API pública do **DataJud**, que
  o RADAR já usa no raio-x da vara (`datajud.py`, códigos TPU de desfecho), com atraso de ~7 semanas e uso não
  comercial pelos termos do CNJ. Proposta: começar só com "novas por dia"; numa versão seguinte, uma rodada semanal
  consulta o DataJud para os processos do Arquivo e preenche "encerradas" com a data do desfecho, rotulada "com atraso
  de ~7 semanas". Depende da resposta do dono (seção 6).

## 4. Limpeza com espaço ocupado (item 44)

- Tela Arquivo mostra: tamanho do `lexsuite.db`, quantas ações, quantas com dado bruto, período coberto.
- **Dado bruto** = o JSON completo da ação (`leads.dados`, com o trecho do Diário e a ficha da Receita). **Resumo** =
  processo, tribunal, vara, data, frente, empresa, CNPJ, porte, faixa de valor, status, contatos com fonte (desenho dos
  contatos). A limpeza "Limpar o que tem mais de N meses" **apaga só o bruto** das ações mais velhas que N e deixa o
  resumo e as estatísticas. Nada de pessoa física fica no resumo (o trecho do Diário é o único lugar com nome de
  reclamante, e ele vai embora na limpeza).
- Padrões: bruto guardado por **12 meses** (hoje `guardar_dias` = 365, que apaga a linha inteira: passa a apagar só o
  bruto); resumo e estatísticas **sem limite**. Ajustável na Configuração; a Receita em cache continua com 30 dias.
- Botão "Compactar o banco" (VACUUM) depois da limpeza, para o espaço aparecer de verdade.

## 5. Frente em cada ação (item 51)

- Coluna `leads.frente` (`trabalhista` · `tributario` · `civel` · `empresarial`), regra escrita, sem IA, aplicada na
  leitura: **TRT e TST → trabalhista**; **TRF, TJ e STJ**: pela classe e pelo assunto do Diário: `execução fiscal`,
  `embargos à execução fiscal`, `mandado de segurança` com assunto tributário → **tributário**; `recuperação judicial`,
  `falência`, `dissolução de sociedade`, `cautelar antecedente` societária → **empresarial**; o resto → **cível**.
- Lista de palavras em `lexsuite/frentes.py`, ajustável; ação sem classe reconhecida fica "cível" com a marca "a
  conferir". Filtro "Frente" e cor discreta no cartão (Produto). Uma lista só, com a marca, como o dono pediu.

## 6. Perguntas para o dono (respondidas em 09/Nov; o que vale está em "Decisões do dono" no quadro)

**Respostas**: situações Novo · Visto · Em análise · Em contato · Virou cliente · Descartado · Arquivado (masculino; só Arquivado sai da Lista); dado completo 12 meses, resumo e estatísticas para sempre; encerradas pelo DataJud numa versão seguinte com o aviso do atraso; frente por regra escrita com "a conferir"; área logada até 30 processos por dia, ajustável. A Produto já implementa.

1. **Nomes dos status**: Novo, Lido, Em tratamento, Tratado, Descartado. Pode ser assim? Hoje são Novo, Visto, Em
   contato, Descartado.
2. **O que fica na Lista**: Novo, Lido e Em tratamento (recomendo); Tratado e Descartado vão só para o Arquivo. Ou só
   "Novo" fica na Lista?
3. **Limpeza**: dado bruto por 12 meses (ajustável), resumo e estatísticas para sempre. Pode?
4. **Encerradas pelo DataJud** (atraso de ~7 semanas; termos de uso não comercial do CNJ, que o RADAR já aceita no
   raio-x da vara): seguir com isso numa versão seguinte (recomendo, com o rótulo do atraso) ou esperar outra fonte?
5. **Frente pela regra escrita** (tribunal + classe + assunto), com "a conferir" quando não reconhecer. Pode?
6. **Área logada (item 59)**: o arquivo para o Claude in Chrome sai com no máximo **30 processos por dia** por padrão
   (o TRT6 bloqueia quem abre mais de 1.500 em 30 dias), com o aviso de que quem abre é o advogado, com a credencial
   dele, e de que telefone e e-mail quase nunca estão no processo (vêm do CNPJ). Pode?

## 7. Quem faz o quê

| Peça | Quem |
|---|---|
| Regras deste desenho; `frentes.py` (lista de palavras); formato da tabela de estatísticas e da limpeza | Arquitetura |
| Rota `/status`, migração do `localStorage`, tabela `acoes`, `estatisticas_diarias`, limpeza do bruto e VACUUM, coluna `frente`, telas Lista/Arquivo/Estatísticas, aba Arquivo e botão do Arquivo completo | Produto (0.8 do programa, com as respostas da seção 6) |
| Rodada semanal de "encerradas" pelo DataJud | Produto, versão seguinte, se o dono aprovar a pergunta 4 |
| Testes: status em lote vai para o banco e para a planilha; limpeza apaga só o bruto e mantém totais; frente certa para 10 classes de exemplo; Arquivo mostra tribunal que saiu da configuração | Produto |
