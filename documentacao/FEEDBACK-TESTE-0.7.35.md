# Teste do dono na 0.7.35 (12/Nov/2026): feedbacks acumulados

Cada item: o que o dono viu, se era esperado e para onde vai. Tudo o que é "0.7.36" espera o "pode" do dono.

| # | Feedback | Esperado? | Destino |
|---|---|---|---|
| 1 | Cabeçalho não fica fixo | Esperado: o cabeçalho fixo é da 0.7.36 (pronto, parado) | 0.7.36 |
| 2 | Configurações: hierarquia confusa (seção e subseção se misturam), "A lista" soa estranho, "Critérios da lista" repete "lista", "Leitura" e "Leitura automática" repetem; seções sem faixa de fundo | Não: melhoria | 0.7.36, com os nomes decididos (abaixo) |
| 3 | Aparência no modo escuro: os quadros (Claro, Escuro, Igual ao sistema) perdem destaque | Não: defeito de contraste | 0.7.36 |
| 4 | "Sobre este computador" poderia ficar dentro de "Licença e termos" | Melhoria | 0.7.36 (proposta abaixo) |
| 5 | "Verificar atualização": "Nada a atualizar…" em verde; quando houver versão nova, a frase em destaque | Melhoria | 0.7.36 |
| 6 | Rodapé das Configurações repete "pasta" e "lista" e soa informal ("Não é preciso compartilhar nada com a SolverONE") | Melhoria de texto | 0.7.36 (texto proposto abaixo) |
| 7 | Pastas "Cópias", "Cópias da planilha" e "Cópias de segurança" | Esperado numa instalação antiga ("Cópias" é o nome de antes da 0.7.18); some ao zerar | Depois: mover a antiga para "Cópias da planilha" |

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

## Texto proposto para o rodapé das Configurações (item 6)

"Cada área do direito tem a sua planilha (hoje, LexSuiteONE - Trabalhista.xlsx), guardada na pasta escolhida acima, ao lado
da pasta Cópias de segurança. A aba Radar traz a relação completa dos processos; os destaques e as exclusões são de cada
pessoa, neste computador. A pasta não precisa ser compartilhada com a SolverONE."
