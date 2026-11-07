# DNS de solverone.com.br: o que existe e o que criar

Levantamento feito em 07/Nov/2026 por consulta pública (DNS). A zona está hospedada no **Registro.br**
(servidores `e.sec.dns.br` e `f.sec.dns.br`). É lá que qualquer registro novo é criado hoje.

## Registros que existem hoje e para que servem

| Nome | Tipo | Valor | Serve para |
|---|---|---|---|
| `solverone.com.br` | A | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 | site da SolverONE no GitHub Pages |
| `solverone.com.br` | AAAA | 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 | idem, IPv6 |
| `www.solverone.com.br` | CNAME | `marceloneco.github.io` | idem, com www |
| `_github-pages-challenge-marceloneco.solverone.com.br` | TXT | `7a877520c809583275440831e55532` | prova ao GitHub que o domínio é seu |
| `solverone.com.br` | MX | `10 mx1.improvmx.com`, `20 mx2.improvmx.com` | **recebimento** de e-mail: ImprovMX encaminha os endereços @solverone.com.br para uma caixa sua |
| `solverone.com.br` | TXT | `v=spf1 include:spf.improvmx.com -all` | SPF do recebimento/encaminhamento |
| `_dmarc.solverone.com.br` | TXT | `v=DMARC1; p=none;` | DMARC em modo observação |
| `resend._domainkey.solverone.com.br` | TXT | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCpm4SssgL28o3Nr9Om5C8XYJPI/kS+tuDiAh8k44G7EhlTkF00WZ/VbwopS3YeFbsk6Fz0a+IzRmw0ZDrhLYvfs+QociKiMRkck3sGB9ikZmtzoUr2lV61Gpz+zIKxcYj83/aEjZbklXxuRdfuF5Po12uOnIYlna2onHv1WRiVJQIDAQAB` | DKIM do **envio** pelo Resend (e-mails do LexSuiteONE) |
| `send.solverone.com.br` | MX | `10 feedback-smtp.sa-east-1.amazonses.com` | retorno (bounce) do envio pelo Resend |
| `send.solverone.com.br` | TXT | `v=spf1 include:amazonses.com ~all` | SPF do envio pelo Resend |
| `resend._domainkey.mail.solverone.com.br` | TXT | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcZY/HoPbVPCPxVwJcSQAagQhpe4Gg4Uw8bMTHRFVOH4cq+d/SoRz39XO641LVXRyYVF2APYIGEYIR93PwkmQ6Uj9fNmYoGYPddkKe42zCubZgOtrbr6V2gYwsSn0cq1sCqY4lzPZ7A2o2Y1FHCkXXGd7a5+giWWmnB56A3BZmcwIDAQAB` | DKIM do segundo domínio verificado no Resend (`mail.`) |
| `send.mail.solverone.com.br` | MX | `10 feedback.forge.rmta.net` | retorno do envio pelo `mail.` |
| `send.mail.solverone.com.br` | TXT | `v=spf1 ip4:52.3.252.119 ip4:44.222.39.36 ip4:199.249.231.0/24 ~all` | SPF do envio pelo `mail.` |

Não existe hoje: `judicial.solverone.com.br`, `lexsuiteone.solverone.com.br`, registros do Google Workspace.

## O que criar agora: o endereço do JUDICIAL

No painel do Registro.br, em `solverone.com.br`, "Editar zona", modo avançado, um registro só:

| Nome | Tipo | Valor |
|---|---|---|
| `judicial` | CNAME | `solverone.github.io` (se o repositório já estiver na organização `solverone`) ou `marceloneco.github.io` (se ainda estiver na conta pessoal) |

Depois, no repositório, Settings, Pages: branch `main`, pasta `/docs`, domínio `judicial.solverone.com.br`, e "Enforce HTTPS"
quando o GitHub liberar (até uma hora). O arquivo `docs/CNAME` já está no repositório.

## Caixas de e-mail sem Google Workspace

O recebimento é pelo ImprovMX (encaminhamento), não pelo Google Workspace. Isso muda como criar as caixas:

- `contato@solverone.com.br` e `suporte@solverone.com.br`: **apelidos no ImprovMX** (já existem), encaminhando para a
  caixa que você lê. O cliente só vê `@solverone.com.br`.
- `suporte@` precisa também ser uma **Conta Google**, porque é com ela que o cliente compartilha a pasta do Drive. Crie em
  `accounts.google.com/SignUpWithoutGmail` usando `suporte@solverone.com.br` como e-mail (o código de confirmação chega
  pelo encaminhamento). Essa conta passa a ser a identidade do suporte no Drive, sem expor nenhum Gmail pessoal.
- `nao-responda@` não precisa existir: só envia, pelo Resend.

## DNSSEC: como está e como trocar sem derrubar

O domínio **está assinado** (há um DS na zona `.br`, chave 49771, algoritmo 13), mas não por uma configuração manual:
quando o domínio usa "os servidores DNS do Registro.br", o próprio Registro.br assina a zona automaticamente. Por isso
o painel não mostra uma aba DNSSEC para desligar; o DS automático é removido junto com a troca de servidores.

O caminho seguro, então, é **trocar os servidores e cadastrar o DS do Cloudflare no mesmo formulário** ("Alterar
servidores DNS", botão "+ DNSSEC"). O DNSSEC do Cloudflare já foi ligado pelo conector (07/Nov, 20h42) e o DS é:

| Campo | Valor |
|---|---|
| Keytag | `2371` |
| Algoritmo | `13` (ECDSA P-256 com SHA-256) |
| Tipo de digest | `2` (SHA-256) |
| Digest | `7550D5D0FE766CBDF581A08D089C206ECF2141DB04AAD8BF3742DD5A302E5AD5` |

Janela esperada: até 1 hora depois da troca, alguns resolvedores que ainda guardam o DS antigo podem falhar ao
validar o domínio (site não abre para alguns, e-mail atrasa mas não se perde). Fazer fora do horário comercial.

## Cloudflare: zona já preparada (07/Nov/2026, à noite)

Pelo conector de API do Cloudflare, a zona `solverone.com.br` foi criada na conta da SolverONE com **os 21 registros da
tabela acima mais o CNAME `judicial`**, todos com proxy desligado (nuvem cinza). Ela está **pendente**: não tem efeito
nenhum enquanto os servidores DNS no Registro.br não forem trocados. Conferido registro a registro, inclusive as duas
chaves DKIM inteiras.

Servidores de nome do Cloudflare para esta zona: **`harlee.ns.cloudflare.com`** e **`lennon.ns.cloudflare.com`**.

### O que falta, e só o dono faz, no Registro.br

1. Em "Alterar servidores DNS": desmarcar o DNS do Registro.br, preencher `harlee.ns.cloudflare.com` e
   `lennon.ns.cloudflare.com`, clicar em "+ DNSSEC" e preencher o DS da tabela acima (keytag 2371, algoritmo 13,
   digest tipo 2, digest 7550D5D0...). Salvar. O Registro.br confere se os servidores respondem e se o DS bate com a
   chave publicada pelo Cloudflare.
2. Avisar o Claude: ele confere por fora (servidores, registros, DNSSEC válido, Resend verificado, site com HTTPS).

Se a troca ficar para depois da instalação de quinta, o site precisa do CNAME `judicial` criado no Registro.br
enquanto isso (ver "O que criar agora"). Se a troca for feita antes, esse passo é dispensável.

### Conector

O conector "Cloudflare" de API completa (`https://mcp.cloudflare.com/mcp`) já está ligado na conta do Claude e foi
usado nesta sessão. O "Cloudflare Developer Platform" (Workers) não mexe em DNS.
