# Teste do dono na 0.7.35 (12/Nov/2026): feedbacks acumulados

Cada item: o que o dono viu, se era esperado e para onde vai. Tudo o que é "0.7.36" espera o "pode" do dono.

| # | Feedback | Esperado? | Destino |
|---|---|---|---|
| 1 | Cabeçalho não fica fixo | Esperado: o cabeçalho fixo é da 0.7.36 (pronto, parado) | 0.7.36 |
| 2 | Configurações: hierarquia confusa (seção e subseção se misturam), "A lista" soa estranho, "Critérios da lista" repete "lista", "Leitura" e "Leitura automática" repetem; seções sem faixa de fundo | Não: melhoria | 0.7.36, com os nomes decididos (abaixo) |
| 3 | Aparência no modo escuro: os quadros (Claro, Escuro, Igual ao sistema) perdem destaque | Não: defeito de contraste | 0.7.36 |
| 4 | "Sobre este computador" poderia ficar dentro de "Licença e termos" | Melhoria | 0.7.36 (proposta abaixo) |
| 5 | "Verificar atualização": "Nada a atualizar…" em verde; quando houver versão nova, a frase em destaque | Melhoria | 0.7.36: verde = em dia, azul = versão nova, vermelho = só erro (decidido) |
| 6 | Rodapé das Configurações repete "pasta" e "lista" e soa informal ("Não é preciso compartilhar nada com a SolverONE") | Melhoria de texto | 0.7.36 (texto revisto abaixo) |
| 7 | Pastas "Cópias", "Cópias da planilha" e "Cópias de segurança" | Esperado numa instalação antiga ("Cópias" é o nome de antes da 0.7.18); some ao zerar | Depois: mover a antiga para "Cópias da planilha" |
| 8 | "Conferir agora": ao clicar, nada parece acontecer (o resultado aparece só no rodapé da janela) | Não: falta retorno | 0.7.36: botão fica cinza com "Conferindo…" enquanto consulta e volta ao normal com o resultado |
| 9 | Rodapé "Licença conferida com a SolverONE agora: ativa": pode ficar, mas só a palavra "ativa" em verde | Melhoria | 0.7.36 (estado em vermelho quando não ativa) |
| 10 | "Termos (versão 1.0) / aceitos por… / Ler os termos" ocupa três linhas | Melhoria | 0.7.36: uma linha só, com "Ler os termos" no fim |
| 11 | "Licença e termos" e "Sobre este computador": títulos de seção com destaque; uma subcategoria para o código de cliente, em dourado, com a situação da licença logo abaixo, sem repetir "Licença"/"Código" | Melhoria | 0.7.36 (proposta abaixo) |
| 12 | Empresas excluídas: "Acrescentar" só apaga o que foi digitado e a empresa não aparece; sem motivo na tela | Não: defeito de tela. As empresas entram (a contagem subiu para 9), mas o campo de baixo é a **busca** da lista: com texto nela ("dsfsdfs"), a lista esconde tudo que não bate, sem aviso. A busca parece um campo de cadastro | 0.7.36, prioridade alta: ao acrescentar, limpar a busca e mostrar "✓ Acrescentada: …" com a linha em destaque; busca com 🔍, rótulo "Procurar na lista" e separada do cadastro; com busca sem resultado, "Nenhuma excluída com "…" · Limpar a busca"; todo recusado diz o motivo (CNPJ ou CPF inválido, já está na lista). Motivo segue opcional; obrigatório só o nome, CNPJ ou CPF |
| 13 | Empresas excluídas: ao digitar o CNPJ, buscar o nome da empresa sozinho; cada empresa da lista numa linha só, com letra menor | Ideia nova (regra zero: confirmar com o dono). Viável: o robô já consulta o cadastro público de CNPJ (BrasilAPI e Minha Receita, gratuitos, os mesmos dos sócios). CPF não é consultado (pessoa física) | 0.7.36 se o dono der o "pode": ao sair do campo com um CNPJ válido, mostra "Razão social · CNPJ" e guarda os dois (a exclusão passa a valer pelo nome e pelo CNPJ); sem internet, guarda só o CNPJ e avisa. Linha da lista: nome · CNPJ · motivo · Tirar, letra menor, sem quebrar |
| 14 | CNPJ com letras (CNPJ novo) no validador, na consulta e na busca; o que não entra mostra o motivo; texto sem sentido ("lfds fjsdlkfj sdl") entrou | Validador e consulta já aceitam letras desde a 0.7.33 (quando as fontes públicas ainda não conhecem um CNPJ novo, o robô tenta de novo em 7 dias). A busca da lista não acha um CNPJ digitado sem pontuação: corrigir. O texto sem sentido entrou porque o campo aceita nome livre (decisão da 0.7.33) | 0.7.36: busca ignora pontos, barras e traços; todo recusado mostra o motivo ao lado do campo. **Pergunta D ao dono** (abaixo) |
| 15 | "Copiar estes critérios para as outras áreas" só substitui e copia para todas | Esperado pelo desenho da 0.7.33, mas incompleto e, hoje, distração (só existe a área trabalhista) | 0.7.36: botão (e a escolha de área) aparecem sozinhos só quando houver mais de uma área em uso; senão ficam escondidos (sem configuração). Ao copiar: escolher a(s) área(s) de destino e o modo: **Acrescentar** (soma, sem repetir empresa com o mesmo CNPJ ou o mesmo nome) ou **Substituir**; Cancelar não faz nada |
| 16 | "✓ Critérios copiados para todas as áreas" em cinza, sem destaque; não diz para quais áreas; não fica claro o que é copiado | Conferido no código: copia **tudo** da área (valor mínimo e demais limites e opções **e** as empresas excluídas), substituindo o que havia, e já grava (sem precisar de Salvar) | 0.7.36 (com o item 15): confirmação em verde, com as áreas escolhidas ("Critérios copiados para Tributário e Empresarial"; "para todas as áreas" só quando forem todas); (?) ao lado do botão: "Copia os limites, as opções e as empresas excluídas desta área"; na janela de cópia, duas caixas marcadas: "Limites e opções" e "Empresas excluídas" |
| 17 | Depois de "Trocar licença": "O que a SolverONE recebe · Última conferência 12:19" não mudou; a chave de atualização muda? | Esperado: "Trocar licença" passou (aviso "Licença conferida… ativa" na tela inicial). "Última conferência" é o último **envio das quantidades**, feito ao fim de cada leitura (12:19), não a conferência da licença; a chave de atualização é a da SolverONE para conferir os pacotes, igual para todos, e não muda com a licença | 0.7.36: trocar "Última conferência" por "Último envio" (não confundir com "Conferir agora"); (?) na chave de atualização: "Confere que cada atualização veio da SolverONE; é a mesma em todo computador" |
| 18 | Pasta das planilhas: havia uma mensagem verde ao lado de "Abrir a pasta no Windows" que sumiu ao clicar; não ficou claro para que serve | Esperado em parte: o verde é a conferência automática ao abrir as Configurações ("✓ As planilhas ficam em: c:\testeradar\LexSuiteONE": a pasta existe e o RADAR consegue gravar). O recado de "Abrir a pasta" escreve no mesmo lugar e apaga a conferência | 0.7.36: a conferência fica numa linha própria, com o texto "✓ Pasta conferida: o RADAR consegue gravar em …"; o recado de abrir a pasta aparece por alguns segundos ao lado do botão e some sozinho |
| 19 | Botão "Usar o OneDrive (OneDrive - DataArt Inc)": nome da empresa do dono na tela | Esperado tecnicamente (o RADAR lista as pastas de nuvem que acha **neste** computador; no do Leandro aparecem as dele, nunca "DataArt"), mas expor o nome da organização é ruim | 0.7.36 (revisto com o dono: "para um advogado com pouca experiência em informática, o que faz sentido sem complicar"): no máximo um botão por serviço, sem nada entre parênteses: "Google Drive" (sem "My Drive") e "OneDrive". Com um OneDrive só, o botão usa direto. Com mais de um (pessoal e de empresa, como no notebook do dono ou num computador administrado pelo escritório), o botão abre uma escolha curta: "OneDrive pessoal" e "OneDrive de <organização>" (aqui o nome ajuda, porque no escritório é o do próprio escritório). O caminho aparece só no lugar final (item 22) |
| 20 | Botões da pasta em várias linhas; "Abrir a pasta no Windows" com a mesma cara dos outros | Melhoria | 0.7.36: "Escolher pasta…" primeiro, depois Google Drive e OneDrive, numa linha só e com a mesma aparência; "Abrir a pasta no Windows" separado e diferente (ícone 📂, estilo de link, à direita), porque não muda nada, só abre |
| 21 | Programa em C:\LexSuiteONE e planilha em c:\testeradar: "deveria ficar tudo junto" | Esperado (decisão de 09/Nov): o programa fica sempre em C:\LexSuiteONE porque o banco e a configuração não podem ficar em pasta sincronizada; "Outra pasta" leva só as planilhas, para a equipe abrir de outros computadores. Na instalação nova, o padrão é tudo junto em C:\LexSuiteONE (o teste do dono escolheu "Outra pasta") | 0.7.36: textos dos cartões mais claros: "Pasta padrão (recomendada): programa e planilhas juntos em C:\LexSuiteONE" e "Outra pasta, para a equipe abrir de outros computadores: só as planilhas vão para lá; o programa continua em C:\LexSuiteONE" |
| 22 | O mesmo caminho aparece três vezes (no cartão "Outra pasta", em "Caminho da pasta" e no verde), e o verde tem "\LexSuiteONE" a mais: confuso | Não: excesso de informação. Explicação: o dono escolhe a pasta (c:\testeradar\); o RADAR cria dentro dela a subpasta LexSuiteONE, para não misturar com os arquivos do escritório; as planilhas ficam em c:\testeradar\LexSuiteONE | 0.7.36: o caminho aparece uma vez só. O campo "Caminho da pasta" e os botões vão para dentro do cartão "Outra pasta" (só aparecem com ele marcado); o cartão deixa de repetir o caminho; a linha verde diz o lugar final: "✓ As planilhas ficam em c:\testeradar\LexSuiteONE (o RADAR cria a subpasta LexSuiteONE dentro da pasta escolhida)" |
| 23 | Leitura terminou com "0 publicações lidas; 0 ações novas" | Esperado: os cadernos até 11/NOV já tinham sido lidos ("Caderno TRT2 11/NOV: já conferido") e o de 12/NOV só sai à noite (por volta das 19h). Mas "0 publicações lidas" parece falha | 0.7.36: quando nada é novo, dizer "Nada novo: os cadernos até 11/NOV já tinham sido lidos. O Diário de hoje sai por volta das 19h; a próxima leitura automática é às 20h00." |
| 24 | Faixa de andamento: o texto quebra em duas linhas, o botão Interromper muda de lugar e aparece um caminho técnico ("Página: C:\LexSuiteONE\saida\radar\radar.html") | Não: defeito de tela e texto técnico | 0.7.36: texto da faixa numa linha (corta com "…" e mostra inteiro ao passar o mouse), Interromper em lugar fixo; sem caminho de arquivo (ex.: "Montando a lista: 31.662 ações") |
| 25 | Pizza: item riscado continua ocupando o arco (Setores mostra 31.662 no centro enquanto o resto do Painel mostra 2.799) | Não: a pizza deveria se redistribuir | 0.7.36: o arco mostra só os itens não riscados, o centro mostra o total que sobrou, e a mudança é animada (as fatias deslizam até a nova divisão, cerca de meio segundo; sem animação para quem pediu "reduzir movimento" no Windows). A legenda mantém o riscado, para devolver com um clique |
| 26 | "Empresas com mais ações" não deixa clicar nos itens (e "Outros" é 90%) | Esperado pelo desenho (empresa não é filtro do Painel), mas o dono quer poder clicar em todos | 0.7.36: em todo gráfico, clicar risca e a pizza se refaz. Onde o item vira filtro (setor, tribunal, porte, estado, situação, faixa), segue filtrando o Painel; onde não vira (empresas, sinal), só some daquele gráfico, com a dica "Some só deste gráfico". Riscar "Outros" faz as empresas pequenas aparecerem |

**Pergunta D (12/Nov, noite):** nas empresas excluídas, aceitar só CNPJ ou CPF, ou também um nome sem documento?
Recomendação da Produto: CNPJ como caminho principal (o nome vem sozinho pela consulta); nome sem documento continua
aceito, com o aviso "Sem CNPJ: a exclusão vale só para esse nome escrito igual". Há cliente de quem o escritório só sabe o nome.

## Decisão do dono (12/Nov, noite): nomes das Configurações

- A: **Processos** (não "Ações").
- B: "Critérios da lista" passa a **Destaques e exclusões**.
- C: "Leitura automática" passa a **Rotina de leitura** (o dono preferiu "rotina" a "agenda": não é uma agenda, é uma rotina).

## Configurações (itens 2 e 4), com os nomes decididos

- **Processos** (faixa de seção)
  - Destaques e exclusões (era "Critérios da lista": valor mínimo para destacar e empresas excluídas)
  - Filtros salvos (sai de "Leitura")
  - Pasta das planilhas
- **Leitura do Diário** (faixa de seção)
  - Rotina de leitura (era "Leitura automática": dias e horários)
  - Armazenamento dos processos
- **Tela** (faixa de seção): onde abre (janela ou navegador), aparência, assistente
- **Licença e termos** (faixa de seção): código de cliente, termos e condições, sobre este computador
- O menu ☰ → Configurações segue os mesmos nomes e a mesma ordem.

## Texto do rodapé das Configurações (item 6), revisto com o dono (12/Nov, noite)

Sem "hoje" e com o nome da planilha só como exemplo, para não mudar o texto quando entrar outra área do direito; "pasta"
uma vez só.

"Cada área do direito tem a sua planilha (exemplo: "LexSuiteONE - Trabalhista.xlsx"), guardada na pasta escolhida acima,
junto com as cópias de segurança. A aba Radar traz a relação completa dos processos; destaques e exclusões são individuais e
ficam neste computador. Nenhum desses arquivos precisa ser compartilhado com a SolverONE."

EN: "Each area of law has its own spreadsheet (example: "LexSuiteONE - Trabalhista.xlsx"), kept in the folder chosen above,
together with the backup copies. The Radar tab has the full list of cases; highlights and exclusions are personal and stay
on this computer. None of these files needs to be shared with SolverONE."

## Cores da mensagem de "Verificar atualização" (item 5), decisão do dono (12/Nov, noite)

- **Verde**: já está na última versão ("Nada a atualizar…").
- **Azul** (sóbrio): há versão nova; a frase em destaque, com o botão de instalar.
- **Vermelho**: só para erro (ex.: não foi possível verificar).

## Licença e termos (itens 8 a 11), proposta da Produto (12/Nov, noite)

Faixa de seção **LICENÇA E TERMOS** (destaque igual às outras seções), com três subtítulos em dourado:

- **Código de cliente**: `LEX-•••••-E3LF` · **ativa** (verde; vermelho quando não) · sem data de vencimento; botões
  "Conferir agora" (cinza com "Conferindo…" durante a consulta) e "Trocar licença". Sai a frase "Código confirmado. Para
  trocar, use "Trocar licença"." e saem as linhas "Licença" e "Validade" de "Sobre este computador" (estavam repetidas).
- **Termos e condições**: uma linha: "Versão 1.0, aceitos por Marcelo Teste Advogado em 12/NOV/2026 14:51 (Brasília) ·
  Ler os termos".
- **Sobre este computador**: versão instalada, pasta do programa, planilha, chave e pasta de atualização, o que a
  SolverONE recebe; "Ver histórico de leituras" (item 4b da lista) no lugar de "Ver registro".
- Rodapé da janela: "Licença conferida com a SolverONE agora: **ativa**" (só "ativa" em verde).
