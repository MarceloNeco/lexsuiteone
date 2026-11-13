# Definition of done ampliada e teia de integrações (pedido do dono, 12 e 13/Nov/2026)

Dois textos. O 1 vai só na conversa de diretrizes da SolverONE. O 2 vai em uma conversa de cada aplicativo (a que cuida
das regras do app; ver "Onde colar" no fim).

## 1. Para a conversa de diretrizes da SolverONE

```
Pedido do dono (12 e 13/Nov). Atualize a diretriz geral (diretrizes-gerais-apps) e traga um desenho curto antes de implementar qualquer integração nova. Regra zero: liste o que falta em cada app e confirme comigo. Nomes certos: RootifyONE (gestão dos apps e CRM), ArchONE (diagrama vivo da plataforma), EaglePlanONE (roadmap proprietário da SolverONE).

PARTE A · DEFINITION OF DONE (todo app, todo commit que muda o que a pessoa vê ou o que o app faz)
Uma mudança só está pronta quando cada ponto APLICÁVEL foi conferido contra o que o código faz de verdade, em PT e EN:
1. Manual e orientações espalhadas pelo app (botões (?), dicas, mensagens de erro e aviso, LEIA-ME, roteiros, páginas do site).
2. AssistONE: ajuda da tela, tour e busca (nada apontando para o que sumiu ou mudou de lugar).
3. Novidades da versão: formal, curta, uma linha por mudança, começando por substantivo.
4. Termos e condições: só mudam por necessidade jurídica real; cada versão e cada aceite guardados.
5. Comunicações e e-mails (boas-vindas, avisos, pós-venda): sem prometer o que não existe mais.
6. RootifyONE: compatível e integrado (interruptores em recursos-do-app.json, licenças, feedback e chamados, painel de uso); nada que o RootifyONE controla pode quebrar ou ficar sem controle.
7. ArchONE: o diagrama reflete a mudança (app novo, integração nova ou removida, MCP, serviço, segredo novo por ambiente, rota nova).
8. EaglePlanONE: o item do roadmap muda de estado (feito, parcial, adiado) com a versão e o link do commit.
9. Retrocompatibilidade e migração: quem atualiza da versão anterior não perde dado nem configuração; dado antigo é lido; há caminho de volta descrito.
10. Segurança e LGPD: nenhum segredo no código, no chat ou em arquivo; nenhum pedido externo novo fora do inventário; dados pessoais só os necessários.
11. Qualidade verificável: testes automáticos e de tela passando, revisão independente, acessibilidade (teclado, contraste no claro e no escuro, celular), desempenho medido quando a mudança mexe em volume.
12. Registro: quadro e pendências da conversa atualizados; o que ficou de fora anotado com o motivo.
Diga se falta algum ponto que você recomenda e por quê.

APLICABILIDADE (importante): nem todo app está no mesmo estágio. Alguns estão no banco de dados (Supabase), outros só no GitHub, e alguns são sites abertos, sem login. NÃO é para colocar login, migrar para banco ou criar integração só por causa desta diretriz. Cada ponto vale quando for aplicável ao estágio atual do app; quando não for, a entrega diz "não aplicável hoje" e o motivo em uma linha. O futuro de todos é o banco de dados (nada fica só livre no GitHub): quando um app ganhar login, banco ou uma integração nova, ele já nasce cumprindo os pontos que passaram a valer (RootifyONE, ArchONE, EaglePlanONE, eventos). Revisor trata como bloqueio só o ponto aplicável que faltou.

PARTE B · A TEIA DE INTEGRAÇÕES (RootifyONE, ArchONE, EaglePlanONE e os apps)
Objetivo: sistemas separados que se avisam sozinhos quando algo acontece, para os alinhamentos e ajustes.
- Barramento de eventos único da plataforma (por exemplo, uma tabela de eventos no Supabase com assinaturas): cada app publica eventos padronizados ("versão publicada", "integração criada ou removida", "item do roadmap concluído", "interruptor mudou", "erro em produção", "chamado aberto"). App sem banco publica pelo processo de entrega (automação do GitHub), sem precisar de login.
- Quem escuta: RootifyONE (gestão e controle), ArchONE (atualiza o diagrama), EaglePlanONE (marca o item) e os próprios apps quando o evento é para eles.
- Comandos: o EaglePlanONE e o RootifyONE podem pedir ações aos apps (ligar ou desligar um recurso, pedir uma versão, abrir uma tarefa para uma conversa do Claude). Todo comando passa por fila, lista do que é permitido por app, assinatura, registro de auditoria e aprovação do dono quando muda algo para cliente ou apaga algo. Nunca comando livre.
- Canal de agente com LLM agnóstico: hoje o Claude, amanhã qualquer modelo. Proponha um servidor MCP da plataforma que expõe só ferramentas com escopo (ler estado, propor comando, consultar eventos), com chave por ambiente guardada no cofre, limite de uso, registro de cada chamada e aprovação humana para o que é destrutivo ou visível ao cliente. O modelo nunca recebe segredo.
- Staging primeiro: a teia nasce no ambiente de teste (iniciativa de staging de 12/Nov) e só depois vai para produção.

PARTE C · RootifyONE: gestão de apps e CRM juntos ou separados?
Leitura da Produto do JUDICIAL: ficam no mesmo RootifyONE, em módulos separados ("Gestão dos apps" e "Clientes e CRM"), porque licença, cliente e chamado se cruzam o tempo todo; separar em dois sistemas agora duplicaria cadastro e integração. O RootifyONE é uma plataforma de administração (back-office), não um ERP. Separar só se o CRM crescer com usuários próprios. Desafie se discordar.

O QUE QUERO DE VOLTA, num documento curto:
1. A Definition of done nova, com a regra de aplicabilidade, pronta para entrar na diretriz.
2. Uma tabela: cada app, o estágio dele hoje (banco, só GitHub, site aberto, com ou sem login) e quais pontos valem hoje.
3. O desenho da teia: eventos (nome e campos), quem publica e quem escuta, comandos permitidos, segurança, custo e esforço.
4. Fases, com o que eu vejo e aprovo em cada uma.
Espere o meu "pode" antes de implementar.
```

## 2. Para cada aplicativo (uma conversa por app)

```
Aviso do dono (13/Nov): a Definition of done da plataforma passa a ter 12 pontos: manual e orientações, AssistONE, Novidades da versão, termos, comunicações e e-mails, RootifyONE, ArchONE, EaglePlanONE (roadmap), retrocompatibilidade, segurança e LGPD, qualidade verificável e registro. Vai nascer também uma teia de integrações entre os apps, o RootifyONE, o ArchONE e o EaglePlanONE (eventos e comandos com aprovação). A conversa de diretrizes da SolverONE está desenhando; quando a diretriz nova sair, siga-a.

Aplicabilidade: cada ponto vale quando for aplicável ao estágio atual deste app (com ou sem banco de dados, só no GitHub, site aberto sem login). NÃO crie login, não migre para banco e não crie integração por causa deste aviso. O que não se aplica hoje, diga "não aplicável hoje" e o motivo em uma linha. Quando este app ganhar login, banco ou integração nova (é o caminho de todos), ele já nasce cumprindo os pontos que passaram a valer.

Até a diretriz nova: (1) grave este aviso no arquivo de regras do app (CLAUDE.md ou equivalente), para valer em todas as conversas dele; (2) em cada entrega, diga no resumo o que o RootifyONE, o ArchONE ou o EaglePlanONE precisariam saber (integração nova ou removida, recurso novo, item do roadmap concluído); (3) nada de integração nova sem a regra zero. Responda só confirmando, em até 3 linhas.
```

## Onde colar

- Texto 1: só na conversa de diretrizes da SolverONE.
- Texto 2: em UMA conversa de cada app, a que cuida das regras dele, porque ela grava o aviso no arquivo de regras do
  repositório e as outras conversas do mesmo app leem esse arquivo na próxima tarefa:
  - RADAR JUDICIAL: na Arquitetura (Fable).
  - RootifyONE, ArchONE, EaglePlanONE, Kids (joguinhos) e os outros: na conversa mais recente e ativa de cada um.
- Não precisa colar nas três conversas do mesmo app.
