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

## Levar o DNS para o Cloudflare (roteiro completo, pelo computador)

0. **Conector certo.** O conector "Cloudflare Developer Platform" (Workers) não mexe em DNS. Para o Claude gerir os
   registros no futuro, conecte em claude.ai, Conectores, o "Cloudflare" de API completa (`mcp.cloudflare.com/mcp`).
   Ele só aparece numa conversa nova. Para este roteiro não é necessário: tudo é feito no painel.
1. **Cloudflare, adicionar o domínio.** Em dash.cloudflare.com, "Add a domain", `solverone.com.br`, plano Free. O
   Cloudflare varre a zona e mostra os registros que encontrou.
2. **Conferir registro por registro** contra a tabela acima. Faltou, crie à mão. Costumam faltar os MX e TXT de `send`
   e `send.mail` e o TXT `_github-pages-challenge-marceloneco`. Aproveite e crie o novo: `judicial`, CNAME,
   `solverone.github.io` (ou `marceloneco.github.io` se o repositório ainda estiver na conta pessoal).
3. **Nuvem cinza em tudo que é site**: A, AAAA, CNAME `www`, CNAME `judicial`. Clique na nuvem laranja até ficar cinza
   ("DNS only"). Com a nuvem laranja o certificado do GitHub Pages falha. MX e TXT já são só DNS.
4. **Anote os dois servidores de nome** que o Cloudflare mostra ao final (terminam em `ns.cloudflare.com`).
5. **Registro.br, desativar o DNSSEC.** Em registro.br, o domínio, aba DNSSEC (ou "Configurar DNSSEC"), remover a
   chave / desativar. **Espere pelo menos 2 horas** antes do passo 6, para a assinatura antiga sumir dos caches.
6. **Registro.br, trocar os servidores DNS.** No domínio, "Alterar servidores DNS", trocar a opção do DNS do
   Registro.br pelos dois servidores do Cloudflare, salvar. O Registro.br confere se eles já respondem pelo domínio
   (respondem, porque a zona foi criada no passo 1).
7. **Esperar o aviso do Cloudflare** de domínio ativo (minutos a horas; limite de 24 h). Enquanto isso o site e o
   e-mail continuam funcionando, porque os dois lados têm os mesmos registros.
8. **Conferir**: site em solverone.com.br, e-mail de teste pelo Resend, domínios do Resend ainda "verificados", GitHub
   Pages com HTTPS. Avise o Claude, que confere por fora.
9. **Depois, com calma, religar o DNSSEC**: no Cloudflare, DNS, Settings, "Enable DNSSEC", copiar o registro DS que ele
   mostra e cadastrar no Registro.br, na aba DNSSEC. Ganha a proteção de volta, agora assinada pelo Cloudflare.

Nada disso é necessário para o JUDICIAL funcionar; o ganho é gerência de DNS mais cômoda, DNSSEC continuado e, no
futuro, proteção e cache.
