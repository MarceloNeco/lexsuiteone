# Folha de conferência da Definition of done (uma por versão)

Decisão do dono (15/Nov/2026, "pode"): toda versão nova do RADAR JUDICIAL tem a sua folha `documentacao/dod/<versão>.md`,
preenchida por quem prepara a versão (a Produto, em geral) **antes** de marcar "pronta para publicar". O teste
`robo/testes/test_dod.py` falha se a versão do código (`robo/lexsuite/__init__.py`) não tiver folha, se faltar algum dos 13
pontos ou se algum ficar em branco. O revisor e a Operação tratam folha incompleta como bloqueio.

## Como preencher

Copie o bloco abaixo para `documentacao/dod/<versão>.md`. Em cada ponto, escreva **uma** das duas formas, sempre com o porquê:

- `conferido: <onde e o quê>` — o texto foi lido contra o que o programa faz e corrigido onde estava velho (arquivo, tela, chave).
- `não se aplica: <motivo em uma linha>` — por exemplo, "a versão não muda nada do primeiro acesso".

"Existe" ou "está nos dois idiomas" não é conferir: conferir é ler contra o código. Texto que descreve o comportamento antigo,
caminho de menu que mudou ou passo do tour apontando para o vazio é defeito.

## Os 13 pontos

```
# Definition of done da <versão>

- **1. Manual e orientações** (manual, (?), dicas, mensagens de erro e aviso, LEIA-ME, páginas do site): conferido: …
- **2. AssistONE: ajuda de cada tela** (Painel, Lista, Arquivo, Histórico, Configurações, Perfil, Carregando, Primeiro acesso): conferido: …
- **3. AssistONE: tour** (passos que mudaram de lugar ou sumiram, passos novos): conferido: …
- **4. AssistONE: busca** (termos novos e os que mudaram de nome): conferido: …
- **5. Wizard (primeiro acesso)** (os 4 passos e os textos do instalador que levam a ele): conferido: …
- **6. Novidades da versão** (formal, sucinta e genérica, itens parecidos numa linha só, PT e EN): conferido: …
- **7. Termos e condições** (mudam só por necessidade jurídica real; PT e EN andam juntos): conferido: …
- **8. E-mail de boas-vindas e comunicações** (`docs/email/`, avisos por e-mail, site): conferido: …
- **9. RootifyONE, ArchONE e EaglePlanONE** (integração nova ou removida, recurso novo, item do roadmap): conferido: …
- **10. Retrocompatibilidade** (atualização a partir da versão publicada, dados e configuração antigos): conferido: …
- **11. Segurança e LGPD** (o que sai do computador, o que é guardado, por quanto tempo): conferido: …
- **12. Qualidade verificável** (testes novos, `rodar_tudo.sh`, revisor): conferido: …
- **13. Registro** (quadro, `ESTADO-ATUAL-RADAR.md`, `PENDENCIAS.md`, `LEIA-ME.md`, `ARQUITETURA.md`): conferido: …
```

## Diretrizes do dono que a folha confere (24/Nov/2026)

- **Termos em PT e EN andam juntos.** A cada versão, se uma funcionalidade mudar o que os termos descrevem, a mudança é feita no
  texto em português e rebatida no inglês na mesma versão (`paginas/aceite.html`, seções `s1`…`s11` e `e1`…`e11`). O texto em
  português é o que vale; o inglês é tradução e passa pelo advogado junto com a versão nova. Trocar só o idioma não muda a versão
  nem pede aceite novo (o hash do texto em português continua o mesmo; `test_v0752.TermosEmIngles` confere).
- **Novidades sucintas e genéricas.** Poucas linhas, cada uma começando por substantivo; mudanças parecidas vão juntas numa linha
  ("Melhorias no design, correções e atualização do manual").
