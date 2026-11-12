# Desenho curto: contas de teste dentro da produção (Arquitetura, 12/Nov/2026)

Pedido do dono (12/Nov), para os testes de hoje e de amanhã, antes do staging: marcar as contas de teste na produção, para que
funcionem como reais, mas fiquem fora de números, cobrança, planos, métricas e CRM, e saiam no "limpar dados de teste" quando o
staging existir. SQL: `nuvem/supabase/2026-11-12-contas-de-teste.sql` (com o "desfazer" no fim). **Aplicado só com o "pode" do dono.**

## O que existe no banco com conta ou cliente (conferido em 12/Nov)

| Tabela | O que é | Marcação |
|---|---|---|
| `lex_contas` | licenças do RADAR (hoje: KR Law e "Teste Marcelo (SolverONE)") | coluna `teste` (padrão não); ficha no RootifyONE |
| `assinaturas` | planos/acessos das pessoas dos apps web (6 linhas, todas "membro") | coluna `teste` (padrão não); o RootifyONE marca na ficha da pessoa |
| `sol_feedback` | chamados e feedback de todos os apps | coluna `teste`, preenchida sozinha (gatilho) a partir da licença (`aparelho.licenca`) ou da pessoa (`pessoa_id`) |
| `sol_retorno_diario`, `sol_app_uso`, `lex_eventos`, `lex_avisos`, `sol_aceites` | dados gerados pela conta | sem coluna: seguem a conta pela licença ou pessoa (chave) |
| CRM, cobrança | **não existem neste banco** (não há tabela de CRM nem de cobrança; os planos são `assinaturas`) | quando nascerem, nascem com `teste` (regra para a diretriz geral) |

## Regras

1. Conta de teste **funciona igual** a uma real: e-mail de boas-vindas, aceite dos termos, cadastro, leitura, chamados. Nada no
   programa muda; a `lex-conta` não precisa saber (numa versão futura ela pode devolver `teste` para a tela mostrar "conta de teste").
2. **Fora dos números**: `admin_sol_retorno` (retorno dos processos) ignora licenças de teste quando a pergunta é geral e mostra
   quando a pergunta é por uma licença específica; `admin_feedback_painel` ignora chamados de teste. A fila de chamados e a lista
   de licenças continuam mostrando tudo, com a etiqueta "teste" (parte da tela, RootifyONE).
3. **Fora de cobrança e planos**: `assinaturas.teste` é o sinal para o RootifyONE não contar nem cobrar; a cobrança ainda não existe.
4. **Limpar dados de teste** (quando o staging existir): `delete`/`desativar` por `teste = true`, com cópia antes e o "pode" do dono
   (desenho do staging, seção 6). O que é imutável por desenho (`sol_aceites`) fica, com a conta desativada.
5. A licença "Teste Marcelo (SolverONE)" já nasce marcada pelo próprio SQL; licenças novas de teste nascem marcadas pela ficha
   (`admin_lex_criar` com `p_teste` ou `admin_lex_salvar` com `teste`), com evento `licenca_alterada` "conta de teste: sim".

## O que muda no RootifyONE (pedido à conversa de lá: prompt, item 3g)

Ficha da licença: interruptor "Conta de teste" (lê e grava `teste`; `admin_lex_listar` já devolve); lista de licenças e fila de
chamados com a etiqueta "TESTE"; painéis lendo `sem_contas_de_teste`; ficha da pessoa dos apps web com o mesmo interruptor
(`assinaturas.teste`, função admin a criar lá); nenhum número do painel conta conta de teste.

## Antes (texto das funções substituídas, para o "desfazer")

`admin_lex_listar`, `admin_lex_salvar`, `admin_sol_retorno` e `admin_feedback_painel`: o texto anterior é o de
`nuvem/supabase/lex-admin.sql` e `2026-11-09g-*.sql` (RADAR) e de `rootify-one/entrega/solverone-app/supabase/2026-10-10-feedback-usuarios.sql`
(feedback), já com as alterações de 09 a 12/Nov; a única diferença das versões novas é a coluna `teste` e os filtros `not teste`.
