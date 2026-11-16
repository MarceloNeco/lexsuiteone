# Feedback do dono no teste da 0.7.50 (16/Nov/2026; em andamento: só coletar, nada de código antes de sexta, 20/Nov)

Base do dono: ~5,5 mil processos, nenhum de São Paulo (TRT9, TRT17…). Prints: filtros numa linha com "Tribunais (2)",
"Situação (2)", "Últimos 10 processos"; bloco dos Correios "71 no período · 10 de 562 da empresa", cartão "FORA DOS FILTROS".

| # | O que o dono viu ou pediu | Proposta (a confirmar na hora de fazer) |
|---|---|---|
| 1 | Ao escolher tribunais com muito processo, demora e **não há sinal de carregando** | Só a Lista fica "cinza" (sem clicar em caixinhas) com "Carregando a lista… aguarde", o resto da tela livre; medir e acelerar o filtro de tribunal (cache por tribunal) |
| 2 | Dica dos filtros com vários marcados: mostrar também **a quantidade de cada um**, uma por linha | "Situações selecionadas:" ↵ "Novo (120)" ↵ "Visto (35)"; idem Tribunais ("TRT9 (3.210)" ↵ "TRT17 (2.334)") e os outros filtros |
| 3 | "Selecionar todos os N desta lista", "Expandir todas" e "Recolher todas" em **linhas diferentes**: desperdiça espaço | Uma linha só, logo acima da primeira empresa (selecionar à esquerda; expandir/recolher à direita) |
| 4 | **Expandir está lento** (com 5 mil processos); medo com volume maior. Prioridade: navegação rápida | Medir; desenhar só os blocos visíveis (abre um bloco sem redesenhar a lista toda), reaproveitar os já buscados; avaliar com 60 mil |
| 5 | Aplicou "Em contato" em 10 e não usou o Desfazer: **como achar os que mudaram?** | Resposta ao dono: filtro Situação → "Em contato" mostra todos; nada se perde. Avaliar: "Ver os N alterados" no aviso e no Histórico |
| 6 | Etiqueta **"FORA DOS FILTROS" em vermelho** (sem ficar pesado) | Vermelho de aviso, mesmo tamanho; conferir claro/escuro |
| 7 | No cartão, depois do TRT (bom espaço): **"Processo 0000000-00.0000.0.00.0000"** no formato CNJ, depois a vara | Número no formato do CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO) |
| 8 | Na ficha aberta, número do processo **no formato CNJ** e **ícone de copiar** (dois quadrados) | Mesmo formato; ícone à direita |
| 9 | **Ícone de copiar** em todo campo preenchido que vale copiar, alinhado à direita, de cima a baixo: razão social, CNPJ (formatado), CNAE (formatado), telefone (com DDD; avaliar +55), e-mail, número do processo. Não: nome fantasia vazio, cidade, endereço, porte, capital | "Copiado" por um instante; nada aparece em campo vazio; telefone copia com DDD (ex.: (41) 3333-4444); avaliar o +55 |
| 10 | No cabeçalho da empresa **sem CNPJ** (Correios), onde iria o CNPJ, um texto curto **em itálico** (tentar em vermelho; se pesar, revisitar) dizendo que o RADAR não capturou o CNPJ (não que ele não existe). Com CNPJ, fica como está (cinza menor) | Ex.: "CNPJ não capturado" ao lado do nome, depois do triângulo; o (?) do triângulo explica |
| 11 | (no print) "Expandir todas / Recolher todas" ficam **por baixo da barra fixa** dos filtros ao rolar (cortados no alto) | Resolve junto com o item 3 (uma linha só acima da primeira empresa, com folga da barra fixa) |

O dono ainda está testando; o que chegar entra aqui.
