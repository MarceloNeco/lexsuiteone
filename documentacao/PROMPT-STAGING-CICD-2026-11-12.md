# Iniciativa: ambiente de staging, CI/CD e DevSecOps (pedido do dono, 12/Nov/2026)

Prioridade: **depois do lançamento na KR Law**. Registrar agora como ideia no backlog ("0-SolverONE DIRETRIZES E
BACKLOG") e como iniciativa no app de roadmap. Abaixo, os textos que o dono cola em cada conversa.

## 1. Para "(SolverONE) Fable diretrizes" (vale para toda a plataforma)

```
Nova iniciativa da plataforma (dono, 12/Nov), prioridade logo depois do lançamento na KR Law (RADAR JUDICIAL). Registre agora como ideia na planilha "0-SolverONE DIRETRIZES E BACKLOG" e como iniciativa no app de roadmap, com a prioridade "depois da KR Law". Não implemente nada ainda: desenhe e traga ao dono.

CONTEXTO
- A SolverONE é uma empresa de uma pessoa só: o dono não é desenvolvedor e as conversas do Claude são a equipe. Ele tem as boas práticas de anos de mercado e quer trabalhar com profissionalismo.
- Hoje tudo vai direto para produção: o site, os pacotes do RADAR JUDICIAL, as funções e o banco no Supabase, o RootifyONE e os e-mails. Dados de teste estão misturados com dados reais (o RootifyONE tem até a opção "limpar os dados de teste"). Com o primeiro cliente (KR Law) e, em seguida, os chamados pelo AssistONE, isso deixa de ser aceitável.

OBJETIVO
Um ambiente de teste chamado "staging" para TODOS os apps da SolverONE (RADAR JUDICIAL, RootifyONE, site, ArcONE, o app de roadmap e os que vierem), com todas as funções (e-mail de boas-vindas, licenças, aceite dos termos, chamados, interruptores do RootifyONE), protegido dos clientes, e um caminho automático de promoção para produção (CI/CD com DevSecOps).

COMO CHEGAR LÁ (o caminho invertido)
1. Produção fica exatamente como está.
2. Montar o staging como réplica da produção (estrutura, funções, telas), mas só com dados fictícios ou de teste.
3. Montar o processo: tudo passa primeiro por staging; aprovado pelo dono, é promovido.
4. Inverter o fluxo: a partir daí, nada vai direto para produção.
5. Limpar os dados de teste da produção (com cópia de segurança e o "pode" do dono), que passam a viver só em staging.

REQUISITOS
- Nome em inglês: "staging", em endereços e rótulos (ex.: staging.judicial.solverone.com.br, ou um prefixo ou caminho /staging; você propõe o padrão único para todos os apps).
- Etiqueta visível em toda tela, e-mail e documento de staging: "STAGING · ambiente de teste / test environment" no cabeçalho (cor discreta, inconfundível). Ela sai sozinha na promoção, por configuração, nunca por edição manual de código.
- Promoção = o MESMO artefato testado (mesmo pacote, mesmo hash e assinatura no RADAR; o mesmo commit nos sites). Nada é recompilado na promoção.
- Proteção: staging não aparece para clientes (sem link público, sem indexação, acesso só do dono e da equipe); nunca recebe dado real de cliente.
- E-mails de staging: só para uma lista permitida (e-mails do dono, incluindo os de "+" do Gmail) e com "[STAGING]" no assunto; chave do Resend própria.
- Segredos separados por ambiente (Supabase, Resend, serviço de assinatura), nunca no repositório nem no chat.
- Pipeline automático em cada mudança: testes, Bandit, Gitleaks, varredura de dependências, testes de tela com prints, e um resumo em português para o dono aprovar no celular. A promoção pede a aprovação dele (um clique ou a frase "promove a versão X").
- Desfazer (rollback): voltar à versão anterior de produção com um passo só.
- Simplicidade: o dono não executa comando nenhum; aprova olhando prints e um resumo curto.

O QUE QUERO DE VOCÊ (em um documento curto)
1. Inventário: cada app, onde publica hoje (GitHub Pages, Cloudflare, Supabase, Resend, serviço de assinatura), que segredos usa e onde há dado de teste em produção.
2. Desenho do staging por peça: GitHub (ramos, Environments com aprovação, Actions), sites (subdomínios ou caminhos), Supabase (projeto separado, branches ou prefixo; compare custo e risco), funções (cópia de staging), Resend, assinatura, RootifyONE (como ele mostra e controla os dois ambientes) e RADAR (canal de atualização por licença; ver o pedido da Arquitetura do JUDICIAL).
3. Fases, com o que o dono vê e aprova em cada uma, o esforço e o custo mensal (o que é grátis, o que é pago).
4. Riscos e como evitá-los (cliente preso em staging, segredo vazado, e-mail de teste para cliente, banco divergente).
5. Mudanças na diretriz geral (diretrizes-gerais-apps): "nada vai a produção sem passar por staging"; a Definition of done ganha "testado em staging" e o 6º ponto (integrações e controle administrativo) passa a rodar em staging antes de promover.
6. Quem faz o quê entre as conversas (diretrizes, Arquitetura e Operação do JUDICIAL, RootifyONE, demais apps).
Traga ao dono numa mensagem curta, com o documento em anexo, e espere o "pode" antes de qualquer implementação.
```

## 2. Para "(JUDICIAL) Fable Arquitetura" (a parte do RADAR)

```
Iniciativa nova do dono (12/Nov), prioridade depois do lançamento na KR Law: ambiente de staging e CI/CD para toda a plataforma (a conversa "(SolverONE) Fable diretrizes" desenha o padrão geral; o texto completo está em documentacao/PROMPT-STAGING-CICD-2026-11-12.md). Para o RADAR JUDICIAL, desenhe a sua parte seguindo esse padrão: (1) "Publicar versão assinada" com destino staging ou produção; em staging, o mesmo pacote assinado vai para um canal próprio (ex.: staging.judicial.solverone.com.br/atualizacao/) e "promover X" copia o mesmo pacote (hash e assinatura iguais) para produção; (2) a licença tem o canal (staging ou produção), controlado na ficha do RootifyONE e devolvido pela lex-conta; o programa busca atualizações no canal da licença e mostra a etiqueta "STAGING · ambiente de teste" no cabeçalho quando está em staging; (3) lex-conta, lex-equipe e o banco em staging (projeto, branch ou prefixo, conforme o padrão da plataforma), com as licenças e os dados de teste vivendo só lá; (4) e-mail de boas-vindas e de aceite em staging só para a lista permitida, com "[STAGING]" no assunto; (5) site e página de aceite em staging; (6) plano para tirar os dados de teste da produção depois, com cópia e o "pode" do dono; (7) um Windows de teste na nuvem, ligado só quando precisa, para a instalação, o Agendador e o aceite (custo e alternativa), já que o notebook do dono não deve rodar testes. Diga o que muda em publicar.yml, atualizar.py, conta.py, lex-conta, lex-equipe, RootifyONE e nos documentos, os riscos e quem faz cada parte. Registre no quadro como "depois da KR Law" e traga ao dono antes de implementar.
```

## 3. Para "(JUDICIAL) Sonnet Operação" (só para saber)

```
Aviso do dono (12/Nov): depois do lançamento na KR Law vem a iniciativa de staging e CI/CD (documentacao/PROMPT-STAGING-CICD-2026-11-12.md). Quando a Arquitetura trouxer o desenho, a automação "Publicar versão assinada" vai ganhar o destino staging e a promoção para produção. Até lá, nada muda no seu processo.
```
