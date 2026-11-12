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
