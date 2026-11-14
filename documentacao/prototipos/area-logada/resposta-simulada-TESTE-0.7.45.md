# Resposta simulada "do Claude in Chrome" para testar na 0.7.45 (dados fictícios)

COMO USAR (2 minutos):
1. No RADAR, marque 2 processos e clique em "Preparar busca na área logada". Abra o arquivo que ele gerou
   (C:\LexSuiteONE\saida\contatos\pedido-pje-2026-11-14.md) e copie os dois números de processo da tabela "Processos".
2. Abra este arquivo no Bloco de Notas e use Ctrl+H: troque `AAAAAAA-AA.2026.5.09.0001` pelo 1º número e
   `BBBBBBB-BB.2026.5.09.0002` pelo 2º número (em todas as ocorrências).
3. Copie TUDO daqui para baixo (inclusive a conversa em volta) e cole em "Trazer dados da área logada" → "Ler a resposta".

O QUE DEVE ACONTECER na 0.7.45 (confira):
- Aceitas: valor da causa, data, e-mail, telefone, endereço (com UF PR) e sócio do processo A; valor e endereço "a conferir" do B.
- nao_consta: 1 (site do A). tentar_depois: 2 (telefone e e-mail do B, "petição em PDF").
- Recusadas, com o motivo na tela: linha com CPF; linha do reclamante; dado "porte" (não existe no v1); processo fora da lista;
  valor vazio com "encontrado"; linha com "resultado" inventado. A linha repetida do e-mail conta uma vez.
- O texto fora das tabelas (saudações, emoji, markdown) é ignorado, sem erro.

---------- copie daqui para baixo ----------

Pronto! 🎉 Percorri os 2 processos do lote 1 de 2 no PJe do TRT9, só leitura, como pedido. Observação: o painel demorou
~8 s para carregar o segundo processo. Segue o bloco:

### RESPOSTA PARA O RADAR v1 · lote 1 de 2
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

RESPOSTA PARA O RADAR v1 · lote 2 de 2
| processo | dado | valor | resultado | fonte | data | observação | coluna_extra |
|---|---|---|---|---|---|---|---|
| BBBBBBB-BB.2026.5.09.0002 | valor_causa | 48250,50 | encontrado | PJe dados do processo | 2026-11-14 | | x |
| BBBBBBB-BB.2026.5.09.0002 | endereco | Av. Vicente Machado, 2.000, Ponta Grossa/PR, 84010-000 | encontrado | PJe petição inicial | 2026-11-14 | a conferir | x |
| BBBBBBB-BB.2026.5.09.0002 | telefone | | tentar_depois | | 2026-11-14 | petição em PDF | x |
| BBBBBBB-BB.2026.5.09.0002 | email | | tentar_depois | | 2026-11-14 | petição em PDF | x |
esta linha não começa com barra e deve ser ignorada | BBBBBBB-BB.2026.5.09.0002 | site | lixo |

Terminei. Quer que eu faça mais algum lote? 😊
