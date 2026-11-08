# Retomar o projeto numa sessão nova (estado em 08/Nov/2026, noite)

Este arquivo existe para uma conversa nova do Claude Code começar sem reler o histórico. Leia junto `CLAUDE.md`,
`robo/PENDENCIAS.md`, `docs/DNS-SOLVERONE.md`, `docs/PUBLICAR.md` e `docs/VISITA-KR-LAW.md`. Confirme o estado por fora antes de agir: nada aqui substitui conferir.

## O que já existe e funciona

- Robô v0.7.5 (`robo/`), testes verdes, pacote em `releases/` e `docs/downloads/`. Tela local em 127.0.0.1, planilha
  `LexSuiteONE.xlsx` no Drive do escritório, atualização assinada (chave só na nuvem), manual personalizado, revisão de
  segurança (risco baixo).
- Site https://judicial.solverone.com.br **no ar** (GitHub Pages, pasta `docs/`, HTTPS forçado): página inicial PT/EN,
  manual, 404, download do pacote em `/downloads/Instalar-LexSuiteONE.zip` (pacote completo em `/downloads/LexSuiteONE-RADAR.zip`), atualização assinada em `/atualizacao/`.
- Domínio `solverone.com.br` no Cloudflare (DNS + DNSSEC), e-mail de recebimento pelo Cloudflare Email Routing
  (`contato@`, `judicial@`, `admin@`, `privacidade@`, `suporte@`, `ceo@` encaminham; `integracao@` responde sozinho que é
  caixa de sistemas). Envio pelo Resend (`nao-responda@`). Detalhes em `docs/DNS-SOLVERONE.md`.
- Assinatura das versões na nuvem: serviço `assinatura.solverone.com.br` (Cloudflare Worker); a automação `publicar.yml`
  assina e publica. Ninguém tem a chave privada: nem o dono, nem o PC dele. Roteiro em `docs/PUBLICAR.md`.
- E-mail de boas-vindas (`docs/email/`), remetente `LexSuiteONE <nao-responda@solverone.com.br>` pelo Resend, domínio já
  verificado. Teste entregue ao dono. Falta só o e-mail corporativo do Leandro para o envio real.
- Repositório `MarceloNeco/lexsuiteone` (público, MIT, CI com testes, Bandit, Gitleaks, Dependabot, ações fixadas por SHA,
  automação de publicação assinada). Os 12 primeiros commits da `main` têm o e-mail pessoal do dono como autor; a branch
  `limpo` é a mesma história com autoria anônima, congelada em 08/Nov/2026. **Trabalhe só na `main`.** Na mudança para a
  organização `solverone` (depois de 12/Nov), `limpo` será refeita com os commits novos da `main` e passará a ser a `main`
  do repositório novo. Decisão do dono: o piloto do Leandro sai do repositório pessoal mesmo.
- Documentos de referência também na pasta do Drive do dono (cópia de consulta; o GitHub é a fonte).

## Decisões do dono que valem

- Nome: LexSuiteONE é a suíte; JUDICIAL é o produto (maiúsculas, "IA" em latão). Endereço `judicial.solverone.com.br`.
- Frentes nesta ordem: trabalhista (existe), tributário, cível e empresarial.
- Cópia HTML estática no Drive fica como reserva; o caminho principal é o sistema (tela local hoje; site na 0.8).
- 0.8: o robô manda a lista do dia para a nuvem da SolverONE (Supabase) e o site mostra, com login por link no e-mail e
  código de cliente `LEX-XXXX-XXXX`. Desenho detalhado em `robo/PENDENCIAS.md`.
- Nada de contato pessoal do dono em nada que o cliente vê. Caixas: `judicial@` (contato de toda a suíte LexSuiteONE; no
  futuro `moneytrio@` etc. para outras suítes), `contato@` (genérico), `integracao@` (só sistemas: compartilhar Drive;
  responde sozinho, sem citar outro e-mail por ora), `nao-responda@` (só envia). `integracao@` é também uma Conta Google
  sem Gmail. ImprovMX fica de reserva até ser cancelado (~2 semanas).
- Repositório segue no GitHub pessoal até depois da visita; migração para a organização `solverone` sem impacto para o
  cliente (tudo que ele vê aponta para `judicial.solverone.com.br`). Roteiro em `robo/PENDENCIAS.md`.
- Instalação no cliente (KR Law) na quinta-feira 12/Nov, na casa do Leandro, pelo dono. O pacote de quinta é o 0.7.5.
  Roteiro da visita e prompts do Claude in Chrome (PJe, contatos e anúncios, Astrea) em `docs/VISITA-KR-LAW.md`.

## O que só o dono faz (sem conector)

Registro.br, GitHub (organização, transferência, Pages, configurações de conta), ImprovMX (cancelar), Conta Google do
`integracao@`, DIAGNOSTICO.bat e testes no PC dele, visita à KR Law. Para esses passos ele usa a extensão Claude in Chrome
(Sonnet para o rotineiro): escreva o prompt completo, sem campo em aberto, dizendo site, modelo e o que confirmar.

## Estado do Cloudflare (08/Nov, noite)

Zona `solverone.com.br` ativa no Cloudflare, DNSSEC ligado nos dois lados (Registro.br aponta para os servidores
`harlee`/`lennon` com o DS keytag 2371). Email Routing ativo, Worker `integracao-resposta` em `integracao@`, Worker
`assinatura-lexsuite` em `assinatura.solverone.com.br`. Tudo gerido pelo conector "Cloudflare" (API). Detalhes em
`docs/DNS-SOLVERONE.md`.

## O que falta, na ordem (estado em 08/Nov à noite)

A infraestrutura está completa. Falta:

1. **E-mail de boas-vindas ao Leandro** (sessão de operação), pelo Resend, quando o dono passar o endereço corporativo
   dele: `python docs/email/preencher.py --nome "Leandro" ...` e enviar com o conector Resend. Ver `docs/email/LEIA-ME.md`.
2. **Antes de quinta, no PC do dono**: ensaio da instalação com a segunda conta Google, `DIAGNOSTICO.bat`, rodada real
   nos 24 TRTs. Roteiro em `robo/ROTEIRO-INSTALACAO.md`.
3. **Quinta (12/Nov)**: instalação na KR Law e os três prompts de `docs/VISITA-KR-LAW.md` (relatórios vão para a sessão
   de produto).
4. **Depois de quinta**: organização `solverone` no GitHub (refazer `limpo` como nova `main`, Pages, CNAME para
   `solverone.github.io`), triagem de e-mail por Worker, calibração da regra com o diagnóstico, desenho da 0.8 e da
   frente tributária, cancelar ImprovMX.

## Sessões (três conversas do Claude Code, criadas em 08/Nov)

- **Operação** (Sonnet; repositório `lexsuiteone`): DNS, e-mails (boas-vindas, Resend), Drive, documentos, publicar
  versão pela automação, ajustes pequenos. Não muda regra de negócio.
- **Produto** (Opus; repositório `lexsuiteone`): site e manual (feedbacks do dono sobre a página vão aqui), textos PT/EN,
  frente tributária, relatórios da visita virando desenho de integração, correções do robô. Não mexe no pacote de
  quinta sem o dono aprovar.
- **Arquitetura** (Fable; `lexsuiteone`, `rootify-one`, `solverone-app`, `solverone-dados`): desenho da 0.8 (conta na
  nuvem, lista no site, código de cliente, SQL para o dono revisar), migração para a organização `solverone`, integração
  com o RootifyONE, segurança.
- A conversa que montou tudo isso até 08/Nov foi renomeada "old" e não recebe mais tarefas.

## Prompt sugerido para abrir uma sessão nova

> Você está retomando o projeto LexSuiteONE · JUDICIAL, da SolverONE, como a sessão de [Operação | Produto | Arquitetura].
> Leia primeiro `CLAUDE.md` e `docs/NOVA-SESSAO.md` deste repositório e siga o que está lá. Confira o estado real por
> fora (repositório, DNS, Pages, Resend) antes de agir. Depois me diga, em até dez linhas, o que entendeu do estado atual
> e qual é o primeiro passo da sua sessão. O que só eu posso fazer, me guie passo a passo, em português, como para
> iniciante, com prompts completos para a extensão Claude in Chrome quando for o caso.
