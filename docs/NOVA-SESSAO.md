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
- Nada de contato pessoal do dono em nada que o cliente vê. Caixas: `contato@` (dúvidas) e `integracao@` (Drive), ambas
  apelidos no ImprovMX; `integracao@` vira também uma Conta Google. `nao-responda@` só envia.
- Instalação no cliente (KR Law) na quinta-feira 12/Nov, na casa do Leandro, pelo dono. O pacote de quinta é o 0.7.2.

## O que só o dono faz (sem conector)

Registro.br (DNSSEC, servidores DNS, registros), GitHub (organização, transferência, Pages, configurações de conta),
ImprovMX (apelidos), Conta Google do `integracao@`, chaves de assinatura no PC dele, DIAGNOSTICO.bat no PC no Brasil.

## Estado do Cloudflare (07/Nov, noite)

Zona `solverone.com.br` **ativa** no Cloudflare desde 07/Nov 23h19 UTC, com todos os registros e o CNAME `judicial`;
site judicial.solverone.com.br respondendo (HTTPS depende do "Enforce HTTPS" no GitHub Pages).
Servidores: `harlee.ns.cloudflare.com` e `lennon.ns.cloudflare.com`. DNSSEC do Cloudflare já ligado (DS keytag 2371). Falta só o dono, no Registro.br,
trocar os servidores e cadastrar esse DS no mesmo formulário; o Registro.br assinava a zona automaticamente e não tem
desligamento manual. Detalhes em
`docs/DNS-SOLVERONE.md`.

## O que falta, na ordem (estado em 07/Nov à noite)

Infraestrutura, sem testar o robô (o dono vai testar depois, com calma):

1. **HTTPS do site**: no GitHub Pages do repositório, "Check again" e "Enforce HTTPS" (o dono, pela extensão).
2. **E-mail de recebimento no Cloudflare**: feito em 08/Nov (regras, Worker de resposta em `integracao@`, MX trocado;
   detalhes em `docs/DNS-SOLVERONE.md`). ImprovMX fica como reserva até ser cancelado.
3. **Assinatura das versões**: feita em 08/Nov pela opção "na nuvem": serviço `assinatura.solverone.com.br` (Cloudflare),
   chave privada só lá; a automação `publicar.yml` assina e publica ao receber uma tag `vX.Y.Z`. Roteiro em `docs/PUBLICAR.md`.
4. **E-mail de boas-vindas ao Leandro**, pelo Resend, quando o dono passar o endereço corporativo dele.
5. Depois da instalação: organização `solverone` no GitHub (roteiro em `robo/PENDENCIAS.md`), triagem em `contato@`,
   calibração da regra com o diagnóstico, desenho da 0.8.

Testes que o dono fará depois, no PC dele: ensaio da instalação com a segunda conta Google, `DIAGNOSTICO.bat`, rodada
real nos 24 TRTs.

## Sessões

- Sessão de operação (Sonnet): DNS, e-mails, Drive, documentos, ajustes pequenos.
- Sessão de produto (Fable, com `lexsuiteone`, `rootify-one`, `solverone-app` e `solverone-dados`): desenho e código da 0.8
  (conta na nuvem, lista no site, código de cliente, SQL para o dono revisar), frente tributária, integração com o RootifyONE.
  Não mexe no pacote da instalação sem o dono aprovar.

## Prompt sugerido para abrir a sessão nova

> Você está retomando o projeto LexSuiteONE · JUDICIAL, da SolverONE. Leia primeiro `CLAUDE.md` e `docs/NOVA-SESSAO.md`
> deste repositório e siga o que está lá. Confira o estado real por fora (repositório, DNS, Pages, Resend) antes de
> agir. Depois me diga, em até dez linhas, o que entendeu do estado atual e qual é o primeiro passo. Conectores que
> devem estar ligados: GitHub, Cloudflare (API), Resend, Google Drive, Supabase. A tarefa de hoje é levar o DNS de
> solverone.com.br para o Cloudflare com segurança, criar o registro `judicial` e deixar o site judicial.solverone.com.br
> no ar. O que só eu posso fazer (Registro.br, GitHub), me guie passo a passo, em português, como para iniciante.
