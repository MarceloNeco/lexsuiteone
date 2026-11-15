# Resposta simulada para testar o passo 3 da área logada na 0.7.47 (dados FICTÍCIOS)

Serve para testar em casa, sem PJe. Os dados abaixo são inventados e marcados "exemplo-teste"; eles entram na ficha dos 2 processos
que você escolher, **só neste computador**. Use no computador de teste, não no da KR Law.

COMO USAR (3 minutos):
1. No RADAR, faça o passo 1 e o passo 2 (pode ser o pedido de 25 que você já gerou). No passo 2, na caixa "O pedido", procure a
   tabela "Processos" e copie **dois números de processo que estão nela** (número fora do pedido é recusado, de propósito).
2. Abra este arquivo no Bloco de Notas e use Ctrl+H: troque `AAAAAAA-AA.2026.5.09.0001` pelo 1º número e
   `BBBBBBB-BB.2026.5.09.0002` pelo 2º número (em todas as ocorrências). Salve.
3. No RADAR: faixa amarela do pedido → "Trazer resposta" (ou menu ☰ → Área logada → Trazer resposta…). Cole TUDO o que está
   abaixo da linha "copie daqui para baixo" (ou use "Subir arquivo" com este arquivo salvo) e clique em "Ler a resposta".

O QUE DEVE APARECER no passo 4:
- Processo A: valor da causa, data, e-mail, telefone, endereço (Curitiba/PR) e sócio aceitos; site "não consta".
- Processo B: valor e endereço "a conferir" aceitos; telefone e e-mail "tentar depois" (petição em PDF).
- Recusadas, com o motivo: linha com CPF; e-mail do reclamante; dado "porte"; processo fora do pedido (9999999-99…); valor
  vazio com "encontrado"; resultado inventado ("talvez"). A linha repetida do e-mail conta uma vez.
- A conversa em volta (saudações, emoji) e a linha que não começa com barra são ignoradas, sem erro.
- Como o lote 1 de 1 chegou, o pedido é dado como respondido e a faixa amarela some. Os outros 23 processos ficam como
  "Aguardando resposta" no filtro "Área logada"; o botão "Novo pedido só com o que faltou", no passo 4, pede de novo.

---------- copie daqui para baixo ----------

Pronto! 🎉 Percorri os 2 processos do lote 1 de 1 no PJe do TRT9, só leitura, como pedido. Observação: o painel demorou
~8 s para carregar o segundo processo. Segue o bloco:

### RESPOSTA PARA O RADAR v1 · lote 1 de 1
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|
| AAAAAAA-AA.2026.5.09.0001 | valor_causa | R$ 1.234.567,89 | encontrado | PJe dados do processo | 2026-11-14 | cabeçalho do processo |
| AAAAAAA-AA.2026.5.09.0001 | data_ajuizamento | 13/11/2026 | encontrado | PJe dados do processo | 2026-11-14 | "Distribuído: 13/11/2026 09:41" |
| AAAAAAA-AA.2026.5.09.0001 | email | financeiro@exemplo-teste.com.br | encontrado | PJe dados do processo | 2026-11-14 | (email: …) no cadastro da parte |
| AAAAAAA-AA.2026.5.09.0001 | email | financeiro@exemplo-teste.com.br | encontrado | PJe dados do processo | 2026-11-14 | linha repetida de propósito |
| AAAAAAA-AA.2026.5.09.0001 | telefone | (41) 99876-5432 | encontrado | PJe petição inicial | 2026-11-14 | WhatsApp citado na qualificação da ré; caracteres: ç ã é — "aspas" 'simples' & <b>negrito</b> ; ponto-e-vírgula |
| AAAAAAA-AA.2026.5.09.0001 | endereco | Rua das Araucárias, 1.500, sala 3, Bigorrilho, Curitiba - PR, CEP 80710-000 | encontrado | PJe dados do processo | 2026-11-14 | |
| AAAAAAA-AA.2026.5.09.0001 | site | | nao_consta | PJe petição inicial | 2026-11-14 | não consta na inicial nem no cadastro |
| AAAAAAA-AA.2026.5.09.0001 | socio_contato | Fulano de Tal (sócio-administrador): fulano@exemplo-teste.com.br | encontrado | PJe petição inicial | 2026-11-14 | citado como administrador da ré |
| AAAAAAA-AA.2026.5.09.0001 | telefone | 123.456.789-09 | encontrado | PJe petição inicial | 2026-11-14 | TESTE: isto é um CPF e tem de ser recusado |
| AAAAAAA-AA.2026.5.09.0001 | email | reclamante.exemplo@gmail.com | encontrado | PJe petição inicial | 2026-11-14 | TESTE: e-mail do reclamante, tem de ser recusado |
| AAAAAAA-AA.2026.5.09.0001 | porte | Médio | encontrado | PJe dados do processo | 2026-11-14 | TESTE: dado que não existe no v1 |
| 9999999-99.2026.5.09.0099 | valor_causa | 10000,00 | encontrado | PJe dados do processo | 2026-11-14 | TESTE: processo que não está na lista |
| AAAAAAA-AA.2026.5.09.0001 | telefone | | encontrado | PJe citação | 2026-11-14 | TESTE: valor vazio com "encontrado" |
| AAAAAAA-AA.2026.5.09.0001 | site | www.exemplo-teste.com.br | talvez | PJe petição inicial | 2026-11-14 | TESTE: resultado inventado |

Agora o segundo processo. A petição inicial dele abriu como PDF dentro da página e o texto não era selecionável, então marquei
telefone e e-mail para tentar depois, como manda o roteiro. 👇

(continuação do mesmo lote, com uma coluna a mais de propósito)

### RESPOSTA PARA O RADAR v1 · lote 1 de 1
| processo | dado | valor | resultado | fonte | data | observação | coluna_extra |
|---|---|---|---|---|---|---|---|
| BBBBBBB-BB.2026.5.09.0002 | valor_causa | 48250,50 | encontrado | PJe dados do processo | 2026-11-14 | | x |
| BBBBBBB-BB.2026.5.09.0002 | endereco | Av. Vicente Machado, 2.000, Ponta Grossa/PR, 84010-000 | encontrado | PJe petição inicial | 2026-11-14 | a conferir | x |
| BBBBBBB-BB.2026.5.09.0002 | telefone | | tentar_depois | | 2026-11-14 | petição em PDF | x |
| BBBBBBB-BB.2026.5.09.0002 | email | | tentar_depois | | 2026-11-14 | petição em PDF | x |
esta linha não começa com barra e deve ser ignorada | BBBBBBB-BB.2026.5.09.0002 | site | lixo |

Terminei. Quer que eu faça mais algum lote? 😊
