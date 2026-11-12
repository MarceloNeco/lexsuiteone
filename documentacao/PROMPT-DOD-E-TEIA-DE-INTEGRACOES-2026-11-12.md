# Definition of done ampliada e teia de integrações (pedido do dono, 12/Nov/2026, noite)

Dois textos para colar: o 1 na conversa de diretrizes da SolverONE; o 2 em cada aplicativo.

## 1. Para a conversa de diretrizes da SolverONE

```
Pedido do dono (12/Nov, noite). Atualize a diretriz geral (diretrizes-gerais-apps) e traga um desenho curto antes de implementar qualquer integração nova. Regra zero: liste o que falta em cada app e confirme comigo.

PARTE A · DEFINITION OF DONE (vale para todo app, todo commit que muda o que a pessoa vê ou o que o app faz)
Uma mudança só está pronta quando cada ponto foi conferido contra o que o código faz de verdade, em PT e EN:
1. Manual e orientações espalhadas pelo app (botões (?), dicas, mensagens de erro e aviso, LEIA-ME, roteiros, páginas do site).
2. AssistONE: ajuda da tela, tour e busca (nada apontando para o que sumiu ou mudou de lugar).
3. Novidades da versão: formal, curta, uma linha por mudança, começando por substantivo.
4. Termos e condições: só mudam por necessidade jurídica real; cada versão e cada aceite guardados.
5. Comunicações e e-mails (boas-vindas, avisos, pós-venda): sem prometer o que não existe mais.
6. RootifyONE (gestão dos apps): compatível e integrado. Interruptores (recursos-do-app.json), licenças, feedback e chamados, painel de uso; nada que o RootifyONE controla pode quebrar ou ficar sem controle.
7. ArcONE (diagrama vivo da plataforma): o diagrama reflete a mudança (app novo, integração nova, MCP, serviço, segredo novo por ambiente, rota nova). Se a mudança cria ou remove uma ligação, o ArcONE mostra.
8. App de roadmap: o item correspondente muda de estado (feito, parcial, adiado) com a versão e o link do commit.
9. Retrocompatibilidade e migração: quem atualiza da versão anterior não perde dado nem configuração; dado antigo é lido; há caminho de volta (rollback) descrito.
10. Segurança e LGPD: nenhum segredo no código, no chat ou em arquivo; nenhum pedido externo novo sem estar no inventário; dados pessoais só os necessários.
11. Qualidade verificável: testes automáticos e de tela passando, revisão independente, acessibilidade (teclado, contraste no claro e no escuro, celular), desempenho medido quando a mudança mexe em volume.
12. Registro: quadro/pendências da conversa atualizados, e o que ficou de fora anotado com o motivo.
Diga se faltou algum ponto que você recomenda e por quê. Revisor trata a falta como bloqueio; quem publica não publica versão em que falte.

PARTE B · A TEIA DE INTEGRAÇÕES (RootifyONE, ArcONE, roadmap e os apps)
Objetivo: sistemas separados que se avisam sozinhos quando algo acontece, para os alinhamentos e ajustes.
- Barramento de eventos único da plataforma (por exemplo, uma tabela de eventos no Supabase com assinaturas): cada app publica eventos padronizados ("versão publicada", "integração criada ou removida", "item do roadmap concluído", "interruptor mudou", "erro em produção", "chamado aberto").
- Quem escuta: RootifyONE (gestão e controle), ArcONE (atualiza o diagrama), roadmap (marca o item), e os próprios apps quando o evento é para eles.
- Comandos: o roadmap e o RootifyONE podem pedir ações aos apps (ligar ou desligar um recurso, pedir uma versão, abrir uma tarefa para uma conversa do Claude). Todo comando passa por fila, lista do que é permitido por app, assinatura, registro de auditoria e aprovação do dono quando muda algo para cliente ou apaga algo. Nunca comando livre.
- Canal de agente com LLM agnóstico: hoje o Claude, amanhã qualquer modelo. Proponha um servidor MCP da plataforma que expõe só ferramentas com escopo (ler estado, propor comando, consultar eventos), com chave por ambiente guardada no cofre, limite de uso, registro de cada chamada e aprovação humana para o que é destrutivo ou visível ao cliente. O modelo nunca recebe segredo.
- Staging primeiro: a teia nasce no ambiente de teste (iniciativa de staging de 12/Nov) e só depois vai para produção.

PARTE C · RootifyONE: gestão de apps e CRM juntos ou separados?
Minha leitura (Produto do JUDICIAL): ficam no mesmo RootifyONE, em módulos separados ("Gestão dos apps" e "Clientes e CRM"), porque licença, cliente e chamado se cruzam o tempo todo; separar em dois sistemas agora duplicaria cadastro e integração. O RootifyONE é uma plataforma de administração (back-office), não um ERP. Separar só se o CRM crescer com usuários próprios. Desafie se discordar.

O QUE QUERO DE VOLTA, num documento curto:
1. A Definition of done nova (12 pontos, ou o que você recomendar), pronta para entrar na diretriz.
2. O desenho da teia: eventos (nome e campos), quem publica e quem escuta, comandos permitidos, segurança, custo e esforço.
3. Fases, com o que eu vejo e aprovo em cada uma.
4. O texto curto que cada app recebe (como o abaixo) já ajustado.
Espere o meu "pode" antes de implementar.
```

## 2. Para cada aplicativo (RADAR JUDICIAL, RootifyONE, ArcONE, roadmap, site e os que vierem)

```
Aviso do dono (12/Nov, noite): a Definition of done da plataforma passa a ter 12 pontos (manual e orientações, AssistONE, Novidades, termos, comunicações, RootifyONE, ArcONE, roadmap, retrocompatibilidade, segurança e LGPD, qualidade verificável, registro) e vai nascer uma teia de integrações entre os apps, o RootifyONE, o ArcONE e o roadmap (eventos e comandos com aprovação). A conversa de diretrizes está desenhando; quando a diretriz nova sair, siga-a. Até lá: (1) em cada entrega, diga no resumo o que mudou que o RootifyONE, o ArcONE ou o roadmap precisariam saber (integração nova ou removida, recurso novo, item do roadmap concluído); (2) não crie integração nova sem passar pela regra zero. Responda só confirmando.
```
