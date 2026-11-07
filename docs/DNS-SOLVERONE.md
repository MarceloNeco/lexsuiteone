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

- `contato@solverone.com.br` e `integracao@solverone.com.br`: criar como **apelidos no ImprovMX**, encaminhando para a
  caixa que você lê. O cliente só vê `@solverone.com.br`.
- `integracao@` precisa também ser uma **Conta Google**, porque é com ela que o cliente compartilha a pasta do Drive. Crie em
  `accounts.google.com/SignUpWithoutGmail` usando `integracao@solverone.com.br` como e-mail (o código de confirmação chega
  pelo encaminhamento). Essa conta passa a ser a identidade do suporte no Drive, sem expor nenhum Gmail pessoal.
- `nao-responda@` não precisa existir: só envia, pelo Resend.

## DNSSEC: o detalhe que derruba tudo se for ignorado

O domínio tem **DNSSEC ativo** no Registro.br (há um registro DS na zona `.br`, chave 49771, algoritmo 13). Trocar os
servidores DNS para o Cloudflare sem antes desativar o DNSSEC faz o domínio inteiro parar de resolver, site e e-mail,
porque a assinatura antiga deixa de bater. A ordem certa está no roteiro abaixo.

## Cloudflare: zona já preparada (07/Nov/2026, à noite)

Pelo conector de API do Cloudflare, a zona `solverone.com.br` foi criada na conta da SolverONE com **os 21 registros da
tabela acima mais o CNAME `judicial`**, todos com proxy desligado (nuvem cinza). Ela está **pendente**: não tem efeito
nenhum enquanto os servidores DNS no Registro.br não forem trocados. Conferido registro a registro, inclusive as duas
chaves DKIM inteiras.

Servidores de nome do Cloudflare para esta zona: **`harlee.ns.cloudflare.com`** e **`lennon.ns.cloudflare.com`**.

### O que falta, e só o dono faz, no Registro.br

1. **Desativar o DNSSEC** no domínio solverone.com.br (aba DNSSEC). Esperar **pelo menos 2 horas**.
2. **Trocar os servidores DNS** em "Alterar servidores DNS": desmarcar o DNS do Registro.br e preencher
   `harlee.ns.cloudflare.com` e `lennon.ns.cloudflare.com`. Salvar.
3. Avisar o Claude: ele confere por fora (servidores, registros, Resend verificado, site) e então **liga o DNSSEC no
   Cloudflare** e devolve o registro DS para cadastrar na aba DNSSEC do Registro.br.

Se a troca ficar para depois da instalação de quinta, o site precisa do CNAME `judicial` criado no Registro.br
enquanto isso (ver "O que criar agora"). Se a troca for feita antes, esse passo é dispensável.

### Conector

O conector "Cloudflare" de API completa (`https://mcp.cloudflare.com/mcp`) já está ligado na conta do Claude e foi
usado nesta sessão. O "Cloudflare Developer Platform" (Workers) não mexe em DNS.
