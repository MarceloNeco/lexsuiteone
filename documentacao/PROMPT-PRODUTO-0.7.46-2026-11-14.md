# Prompt para a conversa da Produto (colar inteiro) · 0.7.46 · Área logada v2 · 14/Nov/2026

```
Prioridade do dono (14/Nov): a 0.7.46 é a "Área logada v2". Antes de tudo: git pull e leia docs/QUADRO.md inteiro, depois
documentacao/DESENHO-AREA-LOGADA-V2-2026-11-14.md (o que existe, o que falta), documentacao/visita-kr-law/PROMPT-PJE-AREA-LOGADA-V2.md
(o prompt) e os protótipos em documentacao/prototipos/area-logada/ (pedido gerado e resposta esperada).

O que entregar (seção 2 do desenho):
1. Prompt v2 embutido no texto que "Preparar busca" gera (contatos.PEDIDO_V1), com a variante por tribunal (TRT = mapa "pjekz";
   outros = roteiro genérico) e o cabeçalho "lote N de M".
2. Lotes de 25 processos, cada um com o próprio bloco de resposta; limite diário padrão 100, ajustável em Configuração
   (area_logada_por_dia), com o aviso de que processos onde o advogado não atua podem ter bloqueio por excesso.
3. Janela "Trazer dados da área logada": texto colado OU arquivo (.md, .txt, .zip com .md/.txt dentro; até 20 MB; zipfile da
   biblioteca padrão, nada executado). O leitor acha todos os blocos "RESPOSTA PARA O RADAR v1" no texto, em qualquer ordem, com
   conversa em volta, e ignora o resto; linha repetida entre lotes conta uma vez; resultado por lote (aceitas, recusadas, motivo).
4. colar_v1 aceita a fonte "PJe dados do processo"; endereço vindo da petição entra como "a conferir"; o do cadastro da parte tem
   prioridade.
5. Textos da tela: "8 colunas" vira a tabela v1 de 7 colunas; passo a passo em 3 linhas (copiar → colar na ferramenta com o PJe
   aberto → colar ou subir a resposta aqui); (?) com o que nunca entra (CPF, autor, testemunhas, advogados); nome da ferramenta
   genérico ("sua extensão de navegação com IA: Claude in Chrome, Codex ou outra").
6. Definição de pronto (CLAUDE.md, 12 pontos onde aplicável): manual (seção Área logada), AssistONE (ajuda, tour, busca: "área
   logada", "prompt", "colar resposta", "subir arquivo", "lote"), Novidades formais e curtas, termos SEM mudança (seção 5 da 1.0 já
   descreve o fluxo), e-mail sem mudança. Testes: pedido com 48 processos vira 2 lotes; resposta com 2 blocos em ordem trocada e
   texto em volta; .zip com dois .md; linha com CPF recusada; fonte nova aceita; "a conferir" na ficha.

Ao terminar, anote "pronta para publicar" no quadro com o commit e a lista do que foi conferido; a Operação revisa e publica com o
"publica a versão 0.7.46" do dono. Dúvida de desenho vai como pedido à Arquitetura no quadro.
```
