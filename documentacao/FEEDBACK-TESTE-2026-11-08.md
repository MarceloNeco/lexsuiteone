# Feedback do dono no teste da instalação (08/Nov/2026, versão 0.7.9)

Teste feito numa conta Google de teste, sem o e-mail de boas-vindas (um segundo teste, começando pelo e-mail, vem
depois). Lista viva da Produto: cada item vira proposta, o dono dá o "pode", a Produto prepara a 0.7.10 e anota
"pronta para publicar" no quadro; quem publica é a Operação. Nada aqui foi implementado ainda.

| # | O que o dono viu | Proposta | Depende de |
|---|---|---|---|
| 1 | O endereço da tela é `127.0.0.1:8765` | Abrir a tela numa janela própria (Edge ou Chrome em modo aplicativo), sem barra de endereço, com o título "RADAR JUDICIAL" e o martelinho | "pode" do dono |
| 2 | Atalho na área de trabalho com o martelinho dourado e o nome completo | O instalador já cria o atalho "RADAR JUDICIAL" com o ícone. Falta decidir o nome: "RADAR JUDICIAL" ou "LexSuiteONE RADAR JUDICIAL" | decisão do dono |
| 3 | No Passo 1 dá para mudar o código de cliente já digitado no instalador | Código vindo do instalador aparece em cinza, só leitura (informativo). Troca de código só em Configuração | "pode" |
| 4 | Começando pelo e-mail de boas-vindas, o e-mail da pessoa deveria vir preenchido | O e-mail para quem a licença foi enviada fica guardado na licença (nuvem) e volta junto com a conferência do código; o Passo 1 já mostra o e-mail preenchido (editável) | mudança na nuvem: desenho curto da Arquitetura e "pode" do dono |
| 5 | Função no escritório: falta "Outra"; "opcional" deixa passar em branco | Escolha obrigatória com as funções de hoje + "Outra" (abre um campo de texto) + "Prefiro não informar". Ícone (i) com a dica: "Ajuda a SolverONE a adaptar o RADAR ao seu trabalho." | "pode" |
| 6 | Pasta da planilha lista o OneDrive (nunca testado) e confunde | Listar só o Google Drive deste computador. OneDrive fica "sob consulta", como no site | "pode" |
| 7 | Não há como clicar e escolher a pasta; "Outra pasta" exige digitar o caminho | Botão "Escolher pasta…" que abre a janela de pastas do Windows | "pode" |
| 8 | Pasta digitada que não existe dá erro e o dono teve de criá-la à mão | O RADAR cria a pasta sozinho (pergunta "Criar a pasta?") | "pode" |
| 9 | Não ficou claro para que serve a planilha nem onde ela deve ficar | Passo 2 vira três opções explicadas: (a) "No Google Drive deste computador (recomendado)": a planilha do escritório, que você compartilha com a SolverONE; (b) "Escolher outra pasta…"; (c) "Só neste computador, por enquanto" (na pasta do RADAR; dá para mover para o Drive depois). Texto curto do porquê | "pode" |
| 10 | O RADAR deve funcionar em qualquer pasta, não só em `C:\LexSuiteONE` | Já funciona: o programa roda de onde foi instalado e a planilha pode ficar em qualquer pasta (o teste usou outra). Deixar isso claro no manual | só texto |
| 11 | Passo 3 já vem com os 24 TRTs escolhidos, sem poder mexer ali; engessado para quando vier o tributário | Passo 3 com a frente (Trabalhista hoje; Tributário "em breve", visível e desativado) e a escolha dos tribunais ali mesmo ("Todos os 24 TRTs" ou "Escolher…"), com o horário das leituras. Tudo continua mudável em Tribunais e Configuração | "pode" |
| 12 | **Defeito (crítico):** a primeira leitura, num domingo, terminou com "0 publicações lidas" | `monitor.coletar_caderno` conta os dias para trás no calendário: no domingo olha sábado e domingo (sem Diário) e na segunda às 8h pula a sexta. Corrigir para "hoje + os N últimos dias úteis". Teste novo para sábado, domingo e segunda | correção; vai na 0.7.10 |
| 13 | Duas pastas "LexSuiteONE" (em `C:\` e dentro de `c:\testeradar`); não ficou claro onde está a planilha | São coisas diferentes: `C:\LexSuiteONE` é o programa; `c:\testeradar\LexSuiteONE` é a pasta da planilha. Para instalações novas, a pasta da planilha passa a se chamar "RADAR JUDICIAL - planilha" (as existentes ficam como estão), e o fim do assistente e a Configuração mostram "A planilha está em: …" com o botão "Abrir a pasta" | "pode" |
| 14 | Parecem duas planilhas | É uma só (`LexSuiteONE.xlsx`); o `LexSuiteONE - Radar.html` é uma cópia da tela para abrir no celular. Dar um nome claro à cópia ("Lista para abrir no celular.html") e explicar no assistente | "pode" |
| 15 | Como o RADAR acha o Google Drive? Precisa do Google Drive para computador? | Sim: a planilha vai para o Drive pelo "Google Drive para computador" (a letra G:). O assistente detecta se ele está instalado; se não estiver, explica em uma frase, com o link oficial, e oferece "Só neste computador, por enquanto" | "pode" |
| 16 | Faltou orientar o compartilhamento da pasta com a SolverONE | Passo novo no assistente, depois da pasta: "Compartilhe a pasta com integracao@solverone.com.br como Editor" com o botão "Abrir a pasta no Google Drive", o passo a passo de 3 cliques e a caixa "Já compartilhei". Sem compartilhar, o RADAR funciona normalmente no escritório; a SolverONE só não vê o registro das leituras para ajudar | "pode" |

## Para o segundo teste (pelo e-mail de boas-vindas)

Antes de começar: limpar o computador de novo (Parte A do roteiro) para o instalador não só atualizar. A licença de
teste já tem uma pessoa e um computador do primeiro teste; isso não impede o segundo (o mesmo e-mail volta a ser
"ativa"), mas, se o dono quiser a licença zerada, o pedido vai para a Arquitetura (SQL só em arquivo, o dono roda).
