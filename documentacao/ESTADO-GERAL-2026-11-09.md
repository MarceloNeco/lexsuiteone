# Estado geral do RADAR JUDICIAL — 09/Nov/2026 (fim do dia), para o dono

Feito pela Produto a partir do `docs/QUADRO.md` e dos dois repositórios. Atualizar quando mudar.

## 1. Programa do escritório (versões)

| Versão | Situação | O que traz |
|---|---|---|
| 0.7.13 | publicada | erro das 3h corrigido, histórico de leituras |
| 0.7.14 | **publicada e conferida** pela Operação | tela nova (menu, abas, situações, lote, busca, filtros, contatos), planilha só para leitura e cópia, aviso de leitura agendada, aviso de aceite dos termos |
| 0.7.15 | **pronta na `main`, falta o "publica"** | botão Interromper, aviso "leitura das 08h00 feita agora porque o computador estava desligado", próxima leitura que se atualiza |
| 0.7.16 | a fazer (Produto) | termos por pessoa (contrato pronto pela Arquitetura), sair do programa fechando a janela preta, ressalvas de texto da 2ª revisão da 0.7.14, "Atualizar estatísticas" (depende das perguntas 10 a 12) |

## 2. Nuvem e RootifyONE

- Arquitetura (Fable): termos em duas camadas prontos na nuvem (`sol_termos`, `lex-conta` v10). A trava por pessoa só
  vale para programas que avisam que sabem tratá-la (`suporta_aceite_uso`): **as versões instaladas hoje continuam
  funcionando** (retrocompatível). As licenças antigas (a de teste e a da KR Law) estão com a trava do escritório
  **desligada** até a página de aceite ser publicada: **não é preciso criar licença nova**.
- Página de aceite e e-mail de boas-vindas com o passo do aceite: prontos **só na branch da Arquitetura**; entram no ar
  com o seu "pode publicar", depois de o Leandro revisar o texto dos termos.
- RootifyONE 0.18.19 no ar: botão "Preparar e-mail de boas-vindas" com prévia, menu B2B, ficha com responsável, lote
  de e-mails, Ativar/Pausar com motivo. Fica esperando a Arquitetura para mostrar a etapa "Termos aceitos".

## 3. Antes de mandar o e-mail de boas-vindas ao Leandro (prazo: quarta, 11/Nov)

1. Operação publica a 0.7.15 (para ele instalar a mais nova).
2. Você escolhe sobre os termos:
   - **A (mais rápido):** manda o e-mail **sem** o passo do aceite (trava desligada) e pede o aceite depois, num
     e-mail separado, quando o Leandro aprovar o texto.
   - **B:** o Leandro revisa os termos → você diz "pode publicar" ao Fable → o Fable liga a trava da KR Law → você manda
     o e-mail com o passo do aceite.
3. No RootifyONE: B2B → LexSuiteONE → RADAR JUDICIAL → Licenças → KR Law: confira o e-mail do responsável e o de
   boas-vindas, clique em "Preparar e-mail de boas-vindas", leia a prévia e clique em Enviar.
4. Para testar antes com a sua licença de teste: peça ao Fable para ligar a trava só na licença de teste (opção B
   exige a página publicada).

## 4. Perguntas abertas para você (do quadro)

| # | Pergunta | Recomendação |
|---|---|---|
| 10 | Ritmo da leitura histórica das estatísticas | 30 Diários por noite, ajustável |
| 11 | Carga padrão | 3 meses, só os tribunais marcados |
| 12 | O Diário (DJEN) devolve cadernos de 12 meses atrás? | **Você** abre no Chrome: `https://comunicaapi.pje.jus.br/api/v1/caderno/TRT21/2025-11-10/D` e conta o que apareceu (um texto com "url" = sim; erro = não) |
| 13 | A trava de aceite por pessoa vale também para quem já usa hoje? | Sim, todos aceitam na primeira abertura da versão nova |
