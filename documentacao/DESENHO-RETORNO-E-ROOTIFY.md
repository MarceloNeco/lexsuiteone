# Retorno dos processos à SolverONE e ficha da licença no RootifyONE · desenho curto (Arquitetura, 09/Nov/2026)

Decisões do dono de 09/Nov (quadro, "Decisões do dono"). Só o que é novo; o desenho de Arquivo, situações, limpeza,
Estatísticas, frente e contatos já está com a Produto e não se repete aqui.

## 1. Retorno dos processos à SolverONE (só totais)

**O que é**: a cada leitura, junto da conferência da licença, o programa manda à SolverONE **quantos processos estão em
cada situação**, por dia, tribunal, frente e faixa de valor. **Nunca** vai nome de empresa, número de processo, CNPJ,
pessoa ou contato: só contagens. A Configuração do programa mostra ao escritório exatamente a tabela enviada. O termo de
tratamento de dados prevê essa obrigação (rascunho em `documentacao/TERMO-TRATAMENTO-DADOS-RASCUNHO.md`).

**Onde fica no Supabase** (SQL `nuvem/supabase/2026-11-09-sol-retorno-e-lex-auditoria.sql`, ⏳ a aplicar na próxima sessão
com conector): tabela **agnóstica** `sol_retorno_diario (app, licenca, data, dim1, dim2, dim3, situacao, qtd)`, chave
única por essa combinação, nunca apagada. Cada app diz em `sol_apps.retorno_dimensoes` o nome das suas dimensões; no
RADAR: `["tribunal", "frente", "faixa_valor"]`. Função `sol_retorno_gravar(app, licenca, linhas)` (só service_role) e
`admin_sol_retorno(app, licenca, de, ate)` para a equipe (totais por situação, por dia e por dimensão).

**O que muda na `lex-conta`** (versão 6, Arquitetura): a ação `verificar` aceita o campo opcional
`retorno: [{data, tribunal, frente, faixa_valor, situacao, qtd}, …]` (até 2.000 linhas; situações da lista fixa:
novo, visto, em_analise, em_contato, virou_cliente, descartado, arquivado; dimensões até 40 caracteres; qtd inteiro ≥ 0).
Qualquer outro campo é descartado; linha com texto fora do padrão é recusada e contada em `recusadas` na resposta.
Limite: 1 envio a cada 10 minutos por instalação. A função grava por `sol_retorno_gravar` e devolve `{retorno:
{gravadas, recusadas}}`. Não altera nada do que já existe.

**O que muda no programa** (Produto): a cada leitura, montar a tabela de totais a partir do banco local (data da leitura,
tribunal, frente, faixa de valor, situação → quantidade), mandar junto da conferência e guardar a última tabela enviada;
em Configuração, bloco "O que a SolverONE recebe" com a tabela exata, a data e a frase "só quantidades; nenhum nome,
processo ou contato". Sem internet, a tabela vai na próxima leitura (é um retrato: a mais nova substitui a anterior).

**No RootifyONE** (Arquitetura): na ficha da licença, bloco "Retorno" com totais por situação nos últimos 30 dias e por
tribunal/frente/faixa; na lista das licenças, coluna "Virou cliente (30 d)". Feito de forma agnóstica (`admin_sol_retorno`
serve a qualquer app da SolverONE que mande totais).

## 2. Ficha da licença no RootifyONE: o que entra e quem faz

| Item | Como | Quem |
|---|---|---|
| **E-mail do responsável** | coluna `lex_contas.email_responsavel`; o e-mail de boas-vindas (`email_boas_vindas`) continua separado e, vazio, usa o do responsável; os avisos vão ao responsável | SQL: Arquitetura · tela: Arquitetura |
| **Cadastro de e-mails em lote** | campo de colar vários (vírgula, espaço ou linha); a função `admin_lex_convidar_lote` valida formato, repetidos, e-mail já em outra licença e domínio; a tela mostra os inválidos **antes** de salvar e pede confirmação para os fora do domínio | SQL: Arquitetura · tela: Arquitetura |
| **Ativar / Pausar como botão** | `admin_lex_ativar(codigo, ativo, motivo)`: pede o motivo, grava quem (equipe), quando e motivo em `lex_eventos` (colunas novas `quem` e `motivo`) e em `acesso_log`; o histórico da ficha mostra quem/quando/motivo em toda mudança (Salvar também passa a registrar) | SQL: Arquitetura · tela: Arquitetura |
| **Enviar e-mail de boas-vindas com prévia** | função nova `lex-equipe` (Edge Function com JWT da equipe, confere `eh_admin_equipe()`; ação `boas_vindas` com destinatário, assunto, HTML e texto; envia pelo Resend com `RESEND_API_KEY_LEX`; registra em `lex_eventos` e `acesso_log`). A tela monta a prévia a partir do modelo `docs/email/` já preenchido (nome, código, links) e só envia depois de o dono clicar "Enviar"; o código da licença aparece só na prévia, nunca no log | função: Arquitetura · prévia e texto: Produto · botão e chamada: Arquitetura |
| **Estatísticas da licença** | bloco "Retorno" (seção 1) + "vistos e não vistos" vindos das situações (novo = não visto) | Arquitetura |
| **Apps da plataforma** | `sol_apps` ganha `suite` e `acesso` (web · instalado · nuvem); linha `radar-judicial` (suíte `lexsuiteone`, `instalado`), separada do RadarONE (`eleicoes-2026`, web) | SQL: Arquitetura · `apps.json` e tela de Apps do RootifyONE: Arquitetura |
| **Menu por linha de negócio** | grupo novo **B2B** no menu do RootifyONE → **LexSuiteONE** → RADAR JUDICIAL (Licenças, Retorno) e, depois, as próximas frentes; "Licenças do RADAR" sai do grupo Clientes. Regra para a diretriz geral: produto B2B entra no menu pela suíte | catálogo e menu: Arquitetura · texto na diretriz geral (rootify-one): pedido no quadro |

Ordem: SQL (aplicar) → `lex-conta` v6 → RootifyONE 0.18.16 (ficha, lote, ativar/pausar, retorno, menu B2B, apps) →
função `lex-equipe` + botão de boas-vindas (depois do texto e da prévia da Produto) → programa (Produto) manda o retorno.

## 3. Acréscimos do dono (09/Nov, tarde) e estado

- **Autorização do e-mail de boas-vindas = o clique do dono no botão do RootifyONE**, depois da prévia (destinatário,
  assunto e texto preenchidos) e de uma confirmação. Não existe "pode enviar" em conversa. Prazo: sair até quarta, 11/Nov.
  A Operação preenche a ficha da KR Law (responsável, e-mail de boas-vindas, domínio) quando a 0.18.16 estiver no ar.
- **Botões (?)** em todo campo não óbvio do RootifyONE (começando pela ficha de licenças) e na diretriz geral: quadrinho
  ali mesmo, sem escurecer a tela; clicou fora, fecha. Feito na 0.18.16 (`RF.ui.ajuda`, `RF.ui.campoAjuda`).
- **Situações do processo** no programa usam as chaves `novo, visto, em_analise, em_contato, virou_cliente, descartado,
  arquivado` (a Produto alinha); são as mesmas que a `lex-conta` aceita no `retorno` e que o RootifyONE mostra.
- Estado em 09/Nov: código pronto e testado (RootifyONE 0.18.16, `lex-conta` v6, `lex-equipe` v1, SQL 2026-11-09);
  **falta aplicar o SQL e publicar as duas funções no Supabase**, que depende do conector voltar numa sessão da
  Arquitetura. Sem isso o botão de boas-vindas mostra "a função lex-equipe ainda não foi publicada". Plano B para
  quarta, se o conector não voltar: o dono envia o e-mail pelo próprio Resend ou Gmail, com o texto da prévia copiado
  (o RootifyONE monta a prévia mesmo sem a função).
