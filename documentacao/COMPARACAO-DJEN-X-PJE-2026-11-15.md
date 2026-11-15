# O que o PJe traz a mais que o Diário (DJEN): comparação e o teste que falta (Arquitetura, 15/Nov/2026)

Pergunta do dono: a navegação no PJe mostrou contatos, valores e outras coisas que não estão no Diário? Qual é o tamanho do "gap"?

## 1. Fontes comparadas

- **DJEN (público)**: duas consultas reais feitas em 15/Nov pela API pública (`comunicaapi.pje.jus.br/api/v1/comunicacao`), TRT2 e
  TRT15, comunicações de 13/Nov. Aqui só o **esquema** dos itens; os textos têm nomes de pessoas e ficaram fora deste arquivo.
- **PJe logado** (visita de 13/Nov, prompt 1A): `visita-kr-law/resultados/2026-11-13-PJe-TRT2-prompt-1A-relatorio.md`, processo
  1001386-53.2016.5.02.0019 (processo **do próprio escritório**, ré pessoa jurídica).
- Tentativa de cruzar o mesmo processo nas duas fontes: o DJEN devolveu **0 comunicações** para esse número (é de 2016; o DJEN só
  cobre o período recente). Não há par exato; a comparação abaixo é por campo.

## 2. Campo a campo

| Dado | DJEN (o que o RADAR já lê) | PJe logado (visita) | Gap |
|---|---|---|---|
| Número, classe, vara/órgão, tribunal, data de disponibilização | sim | sim | nenhum |
| Partes (nomes) e polo (A/P) | sim (`destinatarios`: nome + polo) | sim | nenhum |
| Advogados | nome, OAB e UF | nome, OAB, **CPF e e-mail** | PJe traz mais, mas é dado de pessoa física: **não interessa ao RADAR** |
| **CNPJ da ré** | **não** (o RADAR descobre pelo nome, na Receita, com "a conferir") | sim, no cadastro da parte | **grande**: tira a ambiguidade de nome |
| **Valor da causa** | só quando o texto da comunicação cita (raro nas distribuições; hoje "a conferir") | sim, sempre ("Valor da causa:") | **grande** |
| **Data de distribuição / autuação** | não (só a data da comunicação) | sim | médio |
| **Endereço da ré** | não | sim: cadastro da parte e petição inicial | **grande** |
| **E-mail da ré** | não | sim, quando alguém cadastrou ("(email: …)") | **grande**, mas depende do cadastro |
| Telefone da ré | não | não constava (nem cadastro nem inicial) | nenhum (os dois não têm) |
| Assuntos, prioridade, justiça gratuita | não | sim | pequeno (útil para qualificar) |
| Meio de citação (Correios, edital, DJE) | às vezes no texto | sim (tabela de expedientes) | médio |
| Texto da petição inicial | não | sim (HTML ou PDF) | grande, mas é dado pesado e sensível; o RADAR só precisa do endereço |

Resumo: o PJe acrescenta **CNPJ, valor da causa, data de distribuição, endereço e (às vezes) e-mail da ré**. Telefone não vem de
nenhum dos dois; sai do cadastro público (Receita), como hoje. É isso que a área logada v2 (0.7.46/0.7.47) já pede e aceita.

## 3. A dúvida que ainda não foi testada (importante)

O processo da visita era **do próprio escritório**: o advogado é parte, e o PJe mostra tudo. Os processos do RADAR são **de
terceiros** (ações novas contra empresas que o escritório não representa). No PJe, o advogado logado consulta processo de terceiro
pela **consulta processual**, e não está confirmado que essa tela mostre CNPJ, endereço e e-mail da parte; pode mostrar só partes,
classe, órgão e movimentações. Se mostrar menos, o gap real que a área logada consegue fechar é menor (talvez só valor e data).

**Teste de 5 minutos** (precisa de login de advogado; prompt em `visita-kr-law/PROMPT-TESTE-GAP-PJE-2026-11-15.md`): pegar 3
processos da lista do RADAR (de terceiros, do mesmo TRT), abrir cada um no PJe logado pela consulta processual e anotar, sem baixar
nada, se aparecem: valor da causa, data de distribuição, CNPJ, endereço e e-mail da ré. O resultado define o tamanho do gap e se
vale continuar investindo na área logada ou concentrar na Receita + Diário.

## 4. O que fazer com isso

- Nada muda na 0.7.47/0.7.48. A área logada v2 já está preparada para os cinco dados; se o teste mostrar que a consulta de terceiros
  não dá endereço e e-mail, o pedido ao PJe passa a pedir só valor e data, e o endereço continua vindo da Receita.
- O DJEN não "atualiza" o passado: as comunicações ficam na API por data de disponibilização; o que pode acontecer é o CNJ limitar
  a janela consultável. Por isso a comparação por campo (acima) já vale; o teste de terceiros é o que falta.
