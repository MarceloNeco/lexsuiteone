# Planilha grande e armazenamento no computador do escritório (Produto, 09/Nov/2026)

Pedido do dono (09/Nov, itens 98 a 101 de `FEEDBACK-TESTE-2026-11-09.md`): a planilha vai crescer (só dois TRTs já deram
20.699 processos), e o escritório pequeno não tem pessoa de TI. O RADAR precisa avisar antes de encher, guardar cópia
antes de limpar e mostrar quanto ocupa no computador. O dono considera isso necessário **para o lançamento**, não para
depois.

## O que aconteceu (0.7.15)

- A planilha passou de 50 MB por dentro (limite de segurança da leitura) e o RADAR mostrou "Não consegui ler
  LexSuiteONE.xlsx (ValueError). Usando o padrão". Efeito: Preferências e Exclusões ignoradas e a planilha não foi
  regravada (o programa não regrava o que não consegue ler, para não apagar o que o escritório editou). Nada se perdeu.
- Causa de fundo: a aba **Arquivo** da planilha leva 12 meses de tudo o que foi lido. Com o TRT2 e o TRT15, isso são
  centenas de milhares de linhas por ano; o Excel fica lento e o próprio robô gasta muita memória para escrever.
- Correção já feita no ramo (vai na 0.7.16): o RADAR lê só as três abas editáveis, rápido e sem limite prático.

## Princípio

**A planilha é a vitrine; o arquivo completo fica no banco do computador** (que já guarda 12 meses, decisão de 09/Nov).
Nada do que o escritório trabalhou sai da planilha; o que é só leitura antiga sai da planilha, mas fica no banco e na
cópia de segurança.

## Decisões (Produto, por delegação do dono, 09/Nov noite: "tome as melhores decisões"; tudo na 0.7.16, antes da visita)

O dono não terá outra visita ao Leandro: a estrutura da pasta e da planilha precisa nascer definitiva na 0.7.16.

1. **A pasta escolhida nunca muda.** Dentro dela, na subpasta `LexSuiteONE/`, ficam: **uma planilha por frente**
   (`LexSuiteONE - Trabalhista.xlsx` agora; `LexSuiteONE - Tributário.xlsx`, `- Cível.xlsx` e `- Empresarial.xlsx`
   nascem sozinhas na mesma pasta quando a frente tiver processos), `Cópias de segurança/`, `Cópias/` e o
   `Retrato da última leitura.html`. A frente é a do `frentes.py` (TRT e TST = trabalhista).
2. **Migração**: na primeira leitura da 0.7.16, a `LexSuiteONE.xlsx` antiga vira `LexSuiteONE - Trabalhista.xlsx`, com
   as abas editadas preservadas (se estiver aberta no Excel, tenta de novo na leitura seguinte).
3. **Preferências por planilha** (o valor mínimo de uma causa tributária não é o de uma trabalhista); **Exclusões
   somadas**: quem está na aba Exclusões de qualquer planilha some de todas (cliente é cliente em todas as frentes).
4. **Aba Arquivo da planilha**: últimos 90 dias (ajustável na aba Preferências) + todo processo trabalhado (Em análise,
   Em contato, Virou cliente), de qualquer idade. O resto continua no banco do computador (12 meses, decisão de 09/Nov)
   e na tela Arquivo, que passa a buscar no computador em páginas de 200.
5. **Limite por planilha**: 60 mil linhas (ajustável). A partir de 80%: aviso na faixa do topo da tela, na linha 1 da
   planilha (vermelho) e na janela preta, com o botão **"Limpar a planilha (com cópia)"**. A 100%, o RADAR faz a limpeza
   com cópia sozinho antes de gravar e avisa.
6. **Limpar com cópia**: grava a planilha inteira (Excel) e o Arquivo completo do banco em CSV em
   `Cópias de segurança/AAAA-MM-DD HHhMM/`; depois deixa na aba Arquivo só os últimos 30 dias + trabalhados.
   Ficam as **6 cópias** mais recentes; a mais antiga sai com aviso. Botão "Exportar o Arquivo completo (CSV)" a qualquer
   hora.
7. **Armazenamento** (seção nova na Configuração e na tela de boas-vindas da instalação): planilhas (tamanho, linhas,
   % do limite), banco do computador, pasta `saida/`, cópias de segurança e **espaço livre no disco** (o Windows informa
   o espaço livre; o RADAR não abre arquivo de ninguém). Botões: abrir a pasta das cópias, limpar agora, exportar CSV.
8. **Disco quase cheio** (menos de 5 GB ou menos de 10% livres): o RADAR não faz cópia nova, avisa em vermelho na tela e
   na janela preta e continua lendo (a lista fica no banco). Menos de 1 GB: não grava planilha, só o banco, e avisa.
9. **"Ação nova" mais estreita**: entra o processo do ano com lista de distribuição, notificação inicial, citação inicial
   ou audiência inicial/una; deixa de entrar a intimação comum ("fica notificado", "designada audiência" sem ser
   inicial). A janela preta e o Histórico mostram quantas entraram por cada sinal, para conferir com o Leandro.

## Para a Arquitetura (revisar, sem bloquear a 0.7.16)

- Conferir que as decisões 1 a 9 não ferem regra de negócio ou de nuvem (nada vai à SolverONE além do que já ia; o
  retorno por situação continua igual, somando as frentes).
- Banco do computador com o volume de muitos tribunais: avaliar resumo mais cedo do que 12 meses para o que nunca foi
  trabalhado (decisão do dono depois; o painel de armazenamento já mostra o tamanho).
