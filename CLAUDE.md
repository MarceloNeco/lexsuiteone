# LexSuiteONE · JUDICIAL — regras para o Claude Code neste repositório

Leia antes de qualquer alteração: `robo/ARQUITETURA.md` (como o robô é feito), `robo/PENDENCIAS.md` (decisões do dono e o
que falta), `docs/DNS-SOLVERONE.md` (domínio, e-mail, site), `docs/PUBLICAR.md` (como sai uma versão), `docs/email/LEIA-ME.md`
e `docs/VISITA-KR-LAW.md` (visita de quinta e prompts do Claude in Chrome). Para retomar o projeto numa sessão
nova, leia `docs/NOVA-SESSAO.md` primeiro.

## Quem é quem

- Dono: Marcelo, da SolverONE. Não é desenvolvedor: instruções em português, passo a passo, como para iniciante. Ele
  costuma mandar áudio transcrito, e nomes saem errados ("Lex Switch One" = LexSuiteONE, "solver1" = solverone, "Torex" = TORIX).
- Produto: **JUDICIAL**, da suíte **LexSuiteONE**. Endereço `judicial.solverone.com.br`. Frentes: trabalhista (pronta),
  tributário, cível e empresarial. Primeiro cliente: KR Law (Leandro), trabalhista e tributário; o escritório usa o Astrea.

## Regras que não se negociam

- Nenhuma senha, chave, token ou segredo entra no código, no repositório, no chat ou em arquivo. A chave privada de
  assinatura existe só dentro do serviço `assinatura.solverone.com.br` (Cloudflare); ninguém a tem, nem o dono. Se uma
  chave aparecer no chat, peça para revogar.
- Regra zero: antes de implementar um requisito novo, liste o que falta e confirme com o dono. Não publique nada que o
  cliente vê (Pages, pacote, DNS, e-mail a cliente) sem permissão explícita dele.
- Nunca reescreva histórico nem force push sem o dono pedir na hora. Nunca commite `config.json`, `*.db`, `saida/`,
  `diagnostico/`, `chave_privada.txt`.
- O robô é só biblioteca padrão do Python, sem IA no caminho principal, sem contornar captcha, sem dado fictício no
  produto (só em `exemplos/` e testes, marcados como fictícios). Pessoa física nunca sai do robô.
- Contatos pessoais do dono não aparecem em nada que o cliente vê: site, e-mail, repositório, planilha. Antes do
  primeiro commit de qualquer sessão, rode uma vez na pasta do repositório:
  `git config user.name "Marcelo Freitas" && git config user.email "169572628+MarceloNeco@users.noreply.github.com"`
  (o endereço anônimo do GitHub). Nunca commite com e-mail pessoal.
- Branches: trabalhe e publique só na `main`. A branch `limpo` é uma cópia da `main` com a autoria antiga corrigida,
  congelada em 08/Nov/2026; não a toque. Na mudança para a organização `solverone`, ela será refeita a partir da `main`.
- Publicar versão do robô: nunca crie tag à mão. Suba a versão no código, envie para a `main` e dispare a automação
  "Publicar versão assinada" (workflow_dispatch, `publicar.yml`); ela assina, publica e cria a tag. Ver `docs/PUBLICAR.md`.
- Textos para o usuário em PT e EN. Nenhum identificador de modelo de IA em commits, PRs ou código.
- SQL do Supabase nunca roda sem revisão: o dono roda depois de revisar.
- As páginas do produto não fazem nenhum pedido externo: sem fontes de fora, sem rastreador, sem script de terceiros.

## Como entregar

- Versão em `robo/lexsuite/__init__.py`. Pacote: os mesmos 39 arquivos em `releases/LexSuiteONE-robo.zip`,
  `releases/LexSuiteONE-robo-<versão>.zip` e `docs/downloads/LexSuiteONE-robo.zip`. Atualize `robo/LEIA-ME.md`,
  `robo/ARQUITETURA.md` e `robo/PENDENCIAS.md` junto.
- Testes: `cd robo && python -m unittest discover -s testes`. A automação do GitHub roda testes, Bandit e Gitleaks.
- Arquivos `.bat` sempre com fim de linha CRLF.
- A pasta do Drive do dono (LEXSUITE-ONE-ROBO) é cópia de consulta: só atualize quando ele pedir.
