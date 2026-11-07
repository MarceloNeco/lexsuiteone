# Retomar o projeto numa sessão nova (estado em 07/Nov/2026, noite)

Este arquivo existe para uma conversa nova do Claude Code começar sem reler o histórico. Leia junto `CLAUDE.md`,
`robo/PENDENCIAS.md` e `docs/DNS-SOLVERONE.md`. Confirme o estado por fora antes de agir: nada aqui substitui conferir.

## O que já existe e funciona

- Robô v0.7.2 (`robo/`), 62 testes verdes, pacote em `releases/` e `docs/downloads/`. Tela local em 127.0.0.1, planilha
  `LexSuiteONE.xlsx` no Drive do escritório, atualização assinada, manual personalizado, revisão de segurança (risco baixo).
- Site estático em `docs/` (página inicial PT/EN, manual, 404, `CNAME` = judicial.solverone.com.br). Ainda **não** publicado:
  depende do GitHub Pages e do registro DNS.
- E-mail de boas-vindas (`docs/email/`), remetente `LexSuiteONE <nao-responda@solverone.com.br>` pelo Resend, domínio já
  verificado. Teste entregue ao dono. Falta só o e-mail corporativo do Leandro para o envio real.
- Repositório `MarceloNeco/lexsuiteone` (público, MIT, CI com testes, Bandit, Gitleaks, Dependabot, ações fixadas por SHA).
  Branch `main` tem 12 commits antigos com o e-mail pessoal do dono como autor; a branch `limpo` tem o **mesmo conteúdo**
  com autoria anônima. Plano: criar a organização `solverone`, criar `solverone/lexsuiteone` a partir de `limpo` e apagar
  o repositório antigo. Se ao ler isto o repositório já estiver na organização, este item está feito.
- Documentos de referência também na pasta do Drive do dono (cópia de consulta; o GitHub é a fonte).

## Decisões do dono que valem

- Nome: LexSuiteONE é a suíte; JUDICIAL é o produto (maiúsculas, "IA" em latão). Endereço `judicial.solverone.com.br`.
- Frentes nesta ordem: trabalhista (existe), tributário, cível e empresarial.
- Cópia HTML estática no Drive fica como reserva; o caminho principal é o sistema (tela local hoje; site na 0.8).
- 0.8: o robô manda a lista do dia para a nuvem da SolverONE (Supabase) e o site mostra, com login por link no e-mail e
  código de cliente `LEX-XXXX-XXXX`. Desenho detalhado em `robo/PENDENCIAS.md`.
- Nada de contato pessoal do dono em nada que o cliente vê. Caixas: `contato@` (dúvidas) e `integracao@` (Drive), ambas
  apelidos no ImprovMX; `integracao@` vira também uma Conta Google. `nao-responda@` só envia.
- Instalação no cliente (KR Law) na quinta-feira 12/Nov, na casa do Leandro, pelo dono. O pacote de quinta é o 0.7.2.

## O que só o dono faz (sem conector)

Registro.br (DNSSEC, servidores DNS, registros), GitHub (organização, transferência, Pages, configurações de conta),
ImprovMX (apelidos), Conta Google do `integracao@`, chaves de assinatura no PC dele, DIAGNOSTICO.bat no PC no Brasil.

## Tarefa imediata desta sessão nova: DNS no Cloudflare e site no ar

Com o conector "Cloudflare" de API completa ligado (`https://mcp.cloudflare.com/mcp`; o "Developer Platform" não serve
para DNS), a sessão pode fazer pelo conector: criar a zona `solverone.com.br` no Cloudflare, criar todos os registros da
tabela de `docs/DNS-SOLVERONE.md` mais o CNAME `judicial`, deixar os registros de site com proxy desligado (nuvem cinza),
ler os dois servidores de nome, e no fim ligar o DNSSEC e ler o registro DS. O dono faz, na ordem: desativar o DNSSEC no
Registro.br, esperar 2 horas, trocar os servidores DNS, e depois cadastrar o DS novo. A sessão confere tudo por fora
(NS, registros, Resend verificado, site com HTTPS) antes de dizer que terminou.

## Depois disso, em ordem

1. Envio do e-mail de boas-vindas ao Leandro (quando o dono passar o e-mail corporativo), pelo Resend, usando
   `docs/email/preencher.py`.
2. Calibrar a regra de "ação nova" com o `radar-diagnostico.txt` que o dono vai gerar no PC dele.
3. Desenhar a 0.8 por escrito (conta na nuvem, lista no site, código de cliente, SQL para o dono revisar) antes de codar.
4. Frente tributária: classes do CNJ (execução fiscal, embargos, mandado de segurança), TRFs e varas de Fazenda Pública.

## Prompt sugerido para abrir a sessão nova

> Você está retomando o projeto LexSuiteONE · JUDICIAL, da SolverONE. Leia primeiro `CLAUDE.md` e `docs/NOVA-SESSAO.md`
> deste repositório e siga o que está lá. Confira o estado real por fora (repositório, DNS, Pages, Resend) antes de
> agir. Depois me diga, em até dez linhas, o que entendeu do estado atual e qual é o primeiro passo. Conectores que
> devem estar ligados: GitHub, Cloudflare (API), Resend, Google Drive, Supabase. A tarefa de hoje é levar o DNS de
> solverone.com.br para o Cloudflare com segurança, criar o registro `judicial` e deixar o site judicial.solverone.com.br
> no ar. O que só eu posso fazer (Registro.br, GitHub), me guie passo a passo, em português, como para iniciante.
