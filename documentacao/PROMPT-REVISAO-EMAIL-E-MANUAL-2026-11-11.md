# Prompt para a Produto: revisar o e-mail de boas-vindas e o manual com tudo o que mudou (dono, 11/Nov)

Cole na conversa da **Produto** (dona de `docs/email/` conteúdo, `paginas/manual.html` e `robo/MANUAL-DO-ESCRITORIO.html`).
A Operação só revisa e publica o pacote; o texto é da Produto.

---
git pull e leia docs/QUADRO.md. Pedido do dono (11/Nov): **revisar o e-mail de boas-vindas e atualizar o manual do
produto com tudo o que já foi feito**, antes da visita à KR Law. Entrego o e-mail só quando o dono clicar no RootifyONE;
não comente o envio.

1. `docs/email/email-boas-vindas.txt` e `.html` (e `LEIA-ME.md`): conferir contra o programa atual (0.7.29) e os termos
   1.2: (a) passo "Antes de instalar, aceite os termos" com o link `aceite.html#codigo={{codigo}}&email={{email}}&nome={{nome}}`
   (já está; manter); (b) os quatro passos de instalação batem com o instalador e a tela de hoje (janela própria, sem
   janela preta, assistente, planilha por área numa pasta escolhida pelo escritório, não mais "Google Drive" obrigatório);
   (c) o que vai à SolverONE: só totais por situação, cadastro, licença e avisos técnicos (termos 1.2, seções 6 e 7); (d)
   nada de "compartilhar a pasta com a SolverONE" como obrigação (termos 1.2, seção 6.1: opcional, só para suporte);
   (e) PT e EN; (f) a prévia do RootifyONE lê esses arquivos do site, então basta publicar na `main` com o "pode" do dono.
2. `paginas/manual.html` → `docs/manual.html` e `robo/MANUAL-DO-ESCRITORIO.html` (via `ferramentas/marca.py`): cobrir o
   que entrou da 0.7.14 à 0.7.29: situações e lote com Desfazer, Arquivo e Histórico, contatos e "Buscar na área logada"
   com extensão de IA (resposta padronizada), valor da causa e data de ajuizamento pela credencial do advogado, planilha
   por área, cópias de segurança, limite e Armazenamento, Interromper, leitura agendada visível e recuperação de atraso,
   AssistONE (ajuda por tela, tour, interruptor no RootifyONE), aceite dos termos (escritório pelo link; cada pessoa no
   cadastro, mesmo texto, `aceite.html?ler=1`), "O que a SolverONE recebe" na Configuração, Sair do RADAR, sem janela
   preta. Tirar frases velhas ("pessoas físicas não aparecem" vira a regra dos termos, seção 4; "365 dias" vira 12 meses
   com resumo; "nada sai do computador" vira a lista exata do que sai).
3. Devolver no quadro: o que mudou em cada arquivo e o commit; o manual entra no pacote na próxima versão (a Operação
   publica com o "publica a versão X" do dono); o site e o e-mail só com o "pode" do dono.
---
