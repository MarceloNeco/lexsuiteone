# Manutenção do LexSuiteONE (por gente ou por qualquer agente de IA)

Leia antes: `ARQUITETURA.md` (o que cada arquivo faz), `PENDENCIAS.md` (o que falta) e `SEGURANCA.md`.
O produto não usa IA; a manutenção pode usar qualquer agente (Claude Code, Codex, Gemini, Aider com modelo local).

## Check-up mensal

1. Abrir a planilha compartilhada de cada cliente: aba **Log** (rodou nos dias escolhidos, de segunda a sexta no padrão? erros?) e aba **Saúde** (avisos).
2. Rodar `TESTAR.bat` (ou `python -m unittest discover -s testes`) no pacote atual: tudo verde.
3. Conferir se o Python portátil (3.13.x) e as fontes (DJEN, PJe, BrasilAPI, Minha Receita) ainda respondem como antes.
4. Se nada mudou: nada a fazer.

## Quando a aba Saúde avisa

- **"formato do DJEN pode ter mudado"**: baixar uma amostra (`RODAR.bat radar --diagnostico` grava 20 itens em
  `diagnostico\`), comparar os campos com `lexsuite/djen.py` (`normalizar`) e ajustar os nomes. Teste novo em `testes/`.
- **"regra está frouxa" ou "nenhuma ação nova"**: `DIAGNOSTICO.bat`, ler `radar-diagnostico.txt`, ajustar as pistas em
  `lexsuite/classificar.py` (`_INICIO`) e `lexsuite/diagnostico.py` (`ESTRITA`).
- **"Receita sem resposta"**: conferir BrasilAPI e Minha Receita; trocar a ordem em `lexsuite/cnpj.py` (`FONTES`).
- **"Pasta compartilhada: erro"**: o Drive do cliente está pausado ou a pasta mudou; pedir para abrir a Configuração.

## Publicar uma versão

1. Mudar `VERSAO` em `lexsuite/__init__.py`, atualizar `LEIA-ME.md`, `ARQUITETURA.md` e `PENDENCIAS.md`.
2. `python -m unittest discover -s testes` verde e `python ferramentas/marca.py --conferir` (na raiz) em dia.
3. Enviar para a `main` e disparar a automação "Publicar versão assinada" (ver `docs/PUBLICAR.md`): ela empacota,
   pede a assinatura ao serviço `assinatura.solverone.com.br`, publica `LexSuiteONE-RADAR-atualizacao-X.Y.Z.zip` e
   `versao.json` em `docs/atualizacao/`, o pacote completo em `docs/downloads/LexSuiteONE-RADAR.zip`, refaz o
   `instalar.txt` do instalador e cria a tag. Nunca criar tag à mão.
4. O programa instalado procura em `https://judicial.solverone.com.br/atualizacao/versao.json` ao abrir.
5. Se a versão for obrigatória, escrever `versao_minima` na aba Controle da planilha do cliente.

## Revisão de segurança trimestral

Rodar a skill `seguranca-lgpd-gdpr` sobre o pacote, ler `SEGURANCA.md`, conferir que nenhum segredo entrou no
código, no Drive ou no chat, e que `testes/test_v07.py` (atualização) e `testes/test_assinatura.py` continuam verdes.
