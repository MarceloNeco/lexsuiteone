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

## Proposta para a 0.7.16 (Produto implementa; números ajustáveis em Configuração)

1. **Limite da planilha**: 60 mil linhas (abas Radar e Arquivo somadas; ≈ 100 MB por dentro, ≈ 5 MB no disco).
2. **Aviso em três lugares** a partir de 80% do limite: faixa amarela no topo da tela, linha 1 em vermelho na planilha
   e mensagem na janela preta. Texto: "A planilha está ficando grande (48 mil de 60 mil linhas). Recomendamos limpar:
   antes, o RADAR guarda uma cópia completa." Botão **Limpar a planilha (com cópia)**.
3. **Limpar com cópia**: grava a planilha inteira (Excel) e o Arquivo em CSV em
   `<pasta escolhida>/Cópias de segurança/AAAA-MM-DD HHhMM/`; depois a aba Arquivo fica com os **últimos 90 dias** e
   **todo processo trabalhado** (Em análise, Em contato, Virou cliente), de qualquer idade. O banco não perde nada.
4. **Ao chegar a 100%**, o RADAR faz a limpeza com cópia sozinho antes de gravar, e avisa. Assim a planilha nunca
   quebra, mesmo sem ninguém olhar.
5. **Cópias de segurança**: ficam as 6 mais recentes; ao fazer a 7ª, a mais antiga sai, com aviso na tela.
6. **Armazenamento** (seção nova na Configuração): planilha (tamanho, linhas, % do limite), banco do computador, pasta
   `saida/`, cópias de segurança (quantas e quanto ocupam) e **espaço livre no disco** (o Windows informa isso sem o RADAR
   abrir arquivo de ninguém). Botões: abrir a pasta das cópias, limpar agora.
7. **Disco quase cheio** (menos de 5 GB livres ou menos de 10%): o RADAR não faz cópia nova, avisa em vermelho e
   continua lendo (a lista fica no banco).
8. **Tela Arquivo** com dezenas de milhares de processos: a busca passa a ser feita no computador, em páginas de 200
   (hoje a página carrega tudo de uma vez).
9. **Conferir o volume**: 20.699 "novos" em dois TRTs parece alto (a estatística pública fica perto de 2,5 a 3 mil
   ações novas por dia útil nos dois). Conferir se a regra de "ação nova" está deixando passar comunicações de processos
   já em andamento.

## Para a Arquitetura (regra de negócio e estrutura)

- **Uma planilha por frente** (ideia do dono, para quando o tributário entrar; as colunas são diferentes):
  `LexSuiteONE - Trabalhista.xlsx`, `LexSuiteONE - Tributário.xlsx`, na mesma pasta; Preferências e Exclusões por
  frente ou comuns? Configuração lista as planilhas; migração da planilha atual sem perder as abas editadas; textos do
  manual, do e-mail e do site falam de "planilhas". Desenho curto antes do tributário; nada muda na 0.7.16.
- Confirmar que limpar a **planilha** (vitrine) não conflita com a retenção de 12 meses do **banco** (decisão de 09/Nov).
- Avaliar se o banco do computador precisa de teto próprio com esse volume (estimativa: 1 a 2 GB por ano com dois TRTs
  e dado completo de 12 meses) ou resumo mais cedo para quem não foi trabalhado.
