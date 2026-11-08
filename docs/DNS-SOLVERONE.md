# DNS de solverone.com.br: o que existe e como mudar

**Desde 07/Nov/2026, 23h19 UTC, a zona está no Cloudflare** (servidores `harlee.ns.cloudflare.com` e
`lennon.ns.cloudflare.com`), com DNSSEC ativo (DS 2371 publicado pelo Registro.br). Registros novos são criados no
Cloudflare, pelo conector de API do Claude ou no painel. O Registro.br só guarda o domínio e os servidores de nome.

Histórico: até essa data a zona era hospedada no Registro.br (`e.sec.dns.br` e `f.sec.dns.br`). A tabela abaixo é o
conteúdo que foi migrado, idêntico nos dois lados, mais o CNAME `judicial`.

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
| `send.mail.solverone.com.br` | CNAME | `send.forge.rmta.net` | retorno e SPF do envio pelo `mail.` (o alvo é que tem o MX e o TXT) |
| `rsend.solverone.com.br` | CNAME | `send.forge.rmta.net` | registro auxiliar do Resend para o domínio `mail.` |
| `rsend.mail.solverone.com.br` | CNAME | `rsend-sae1.forge.rmta.net` | registro auxiliar do Resend para o domínio `mail.` |
| `moneytrio.solverone.com.br` | CNAME | `marceloneco.github.io` | site do MoneyTRIO (BudgetONE, InvestifyONE, TaxONE) no GitHub Pages |

Fonte definitiva desta tabela: o e-mail "Domínio solverone.com.br alterado" que o Registro.br mandou em 07/Nov/2026 às
18:13, com o conteúdo completo da zona. A consulta pública inicial não enxergava `moneytrio`, `rsend` e `rsend.mail`, e
mostrava `send.mail` como MX/TXT quando na verdade é um CNAME. A zona do Cloudflare foi corrigida nesse mesmo dia.

Não existe hoje: `judicial.solverone.com.br`, `lexsuiteone.solverone.com.br`, registros do Google Workspace.

## O que criar agora: o endereço do JUDICIAL

No painel do Registro.br, em `solverone.com.br`, "Editar zona", modo avançado, um registro só:

| Nome | Tipo | Valor |
|---|---|---|
| `judicial` | CNAME | `solverone.github.io` (se o repositório já estiver na organização `solverone`) ou `marceloneco.github.io` (se ainda estiver na conta pessoal) |

Depois, no repositório, Settings, Pages: branch `main`, pasta `/docs`, domínio `judicial.solverone.com.br`, e "Enforce HTTPS"
quando o GitHub liberar (até uma hora). O arquivo `docs/CNAME` já está no repositório.

## E-mail de recebimento: Cloudflare Email Routing (desde 08/Nov/2026, 00h39 UTC)

O recebimento saiu do ImprovMX e passou para o **Cloudflare Email Routing**, na própria zona. Registros no apex:
MX `route1/2/3.mx.cloudflare.net`, TXT SPF `v=spf1 include:_spf.mx.cloudflare.net ~all`, DKIM `cf2024-1._domainkey`.
Os registros do ImprovMX (MX `mx1/mx2.improvmx.com` e o SPF antigo) foram removidos; a conta do ImprovMX fica como
reserva por algumas semanas e depois pode ser cancelada.

Regras (lista fechada; endereço que não está aqui é recusado):

| Endereço | O que acontece |
|---|---|
| `contato@`, `admin@`, `privacidade@`, `suporte@`, `ceo@` | encaminhados para a caixa pessoal do dono (destino verificado no Cloudflare; o endereço não fica em documento nenhum) |
| `integracao@` | Email Worker `integracao-resposta`: encaminha em silêncio para a mesma caixa (por ali chegam os códigos da Conta Google) e, se o remetente for pessoa, responde: "Este endereço é usado por sistemas da SolverONE e não é lido por pessoas. Esta mensagem não será respondida." Mensagens automáticas (no-reply, listas, `Auto-Submitted`) não recebem resposta. |
| qualquer outro | recusado (catch-all desligado) |

- `nao-responda@` só envia (Resend) e não tem regra: resposta a ele é recusada, como deve ser.
- `integracao@` é também uma Conta Google (criada em 07/Nov), com a qual o cliente compartilha a pasta do Drive.
- Para mudar o destino, regras ou o texto da resposta: pelo conector de API do Cloudflare (o Worker é o script
  `integracao-resposta` na conta) ou no painel, Email, Email Routing.

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

Pelo conector de API do Cloudflare, a zona `solverone.com.br` foi criada na conta da SolverONE com **os 24 registros da
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
