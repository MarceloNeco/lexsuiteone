# Ideia (depois de quinta, 12/Nov): planilha numa pasta de rede, usada por várias pessoas

Registrada pela Produto a pedido do dono em 08/Nov/2026. Não é prioridade: a instalação da KR Law é standalone.
Prompt para colar na conversa da Arquitetura quando o dono decidir retomar:

---

Tarefa (Arquitetura): desenhar o uso da planilha do RADAR JUDICIAL numa pasta compartilhada por várias pessoas
(pasta de rede do escritório, Google Drive compartilhado). Não implemente antes do "pode" do dono.

Como é hoje: o RADAR lê o Diário pela internet, guarda tudo no computador (`lexsuite.db`) e grava uma planilha só,
`LexSuiteONE.xlsx`, na pasta escolhida; a cada leitura ele também lê as abas editáveis dela (Preferências, Exclusões)
e a oculta Controle. O Google Drive é só um lugar: não é exigido; compartilhar com `integracao@` serve para a SolverONE
ver Log e Saúde. Qualquer pasta que o Windows enxergue serve, inclusive uma pasta de rede (o assistente tem
"Escolher pasta…").

Perguntas a responder: (1) Excel trava o arquivo enquanto alguém o tem aberto: o que o RADAR faz se não conseguir
gravar (tentar de novo, gravar uma cópia com data, avisar)? (2) Vários computadores com RADAR apontando para a mesma
planilha: quem grava, como evitar duas leituras ao mesmo tempo e duas listas diferentes (um computador "principal",
uma trava na pasta, ou cada um com a sua aba)? (3) Preferências e Exclusões editadas por várias pessoas: como não
perder o que um escreveu quando outro salva? (4) Google Planilhas em vez de Excel (edição simultânea de verdade)
exigiria conta Google e API: vale para a 0.8 (nuvem)? (5) O que o assistente pergunta e o manual explica para a
pasta de rede. Entrega: desenho curto em `documentacao/DESENHO-PLANILHA-EM-REDE.md`, com opções, recomendação,
riscos e plano de teste; anotar no quadro e parar.
