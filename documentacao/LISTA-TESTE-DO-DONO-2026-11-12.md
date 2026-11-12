# Teste do dono na 0.7.33 (12/Nov/2026): tudo o que ele pediu e onde está

Mantida pela Produto. Cada linha: o pedido, quem faz, em que versão e a situação. Visita à KR Law: sexta 13/Nov.
Decisão do dono (12/Nov): os termos continuam na versão 1.0 até a KR Law começar a usar; ajustes de texto não versionam.

## Feito

| Pedido | Versão | Situação |
|---|---|---|
| Aceite dos termos não reconhecido depois de aceitar (programa travado em "Falta aceitar os termos") | 0.7.34 | pronta, falta publicar |
| "database is locked" com a busca de estatísticas e a tela ao mesmo tempo | 0.7.34 | pronta, falta publicar |
| Página de aceite: a nuvem bloqueava o aceite pelo navegador (CORS) | lex-conta v18/v20 | no ar (Arquitetura confirmou) |
| Tela de abertura "RADAR JUDICIAL · carregando" no lugar da tela vazia | 0.7.35 | pronta, em revisão |
| "Conferir agora" em Licença e termos; "Trocar licença" com o mesmo código confere | 0.7.35 | pronta, em revisão |
| Mensagem errada ao encerrar pelo DIAGNOSTICO/Sair; janela tenta se fechar | 0.7.35 | pronta, em revisão |
| Faixa de andamento da leitura alta demais | 0.7.35 | pronta, em revisão |
| Novidades estreitas no computador; botão de fechar escondido | 0.7.35 | pronta, em revisão |
| Pasta das planilhas: "Abrir a pasta no Windows", título repetido, largura | 0.7.35 | pronta, em revisão |
| "Continuar à noite" só aparecia com a busca rodando | 0.7.35 | pronta, em revisão |
| "Guardada antes da 0.7.16 (regra antiga)" no gráfico de sinal | 0.7.35 | pronta: sinal pelo texto guardado; o resto vira "Sem sinal registrado" |
| E-mail de boas-vindas: aceite em uma frase; "não recebe respostas" em linha própria | 0.7.35 | pronta (o e-mail lê o site na hora do envio) |
| Prompts da visita: só os com login, nomeados pela ordem; pasta do Drive arrumada | docs | feito |

## Para hoje (0.7.36), pedidos do dono depois das 13h

1. **Cabeçalho fixo** (☰, RADAR JUDICIAL, versão, Abrir a planilha, Manual, busca, ⚙, PT/EN, perfil), sem cobrir os filtros
   fixos; o menu abre de qualquer ponto da página. Barra lateral só com ícones: depois.
2. **Barras empilhadas com escolha do que separar** em "Ações por dia" e em "Sazonalidade": seletor visível no alto do
   gráfico (não checkbox escondido), uma escolha por vez: nada, tribunal, situação no escritório (novo, visto, …,
   descartado, nessa ordem), faixa de valor da causa, setor. Cores sóbrias, as mesmas dos gráficos de pizza. Ao passar o
   mouse: total e cada parte ("100 ações: 30 novas, 20 vistas, 40 descartadas"). Sazonalidade: só com os atributos que as
   estatísticas mensais guardam (sem pesar o programa); o dourado "mês com mais ações" sai das barras.
3. **Arquivo: "Carregando…" demorado**: ícone discreto girando ao lado; depois de 5 s, aviso em vermelho, sem sublinhar,
   ao lado do "Limpar o que tem mais de 12 meses" e do (?): texto formal e curto sugerindo reduzir o período guardado.
4. **Histórico de leituras**: mostrar as 50 mais recentes (mais recente primeiro) com "Mostrar mais"; a dica do (?) da
   coluna Resposta em linhas ("200 = …", "403 = …"). Propor o que mais vale mostrar (falhas, interrupções) ou mover para
   um lugar menos nobre.
4b. **Histórico de leituras fora das abas** (protótipo 2, `documentacao/prototipos/historico-de-leituras-v2.png`, a
   validar): abre pela faixa vermelha do Painel (só quando uma leitura falha) e por Configurações → Sobre este computador →
   "Ver histórico de leituras"; a mesma janela, que substitui a de Configurações (sem janela sobre janela), com
   "← Configurações" quando se chegou por lá e ✕ que fecha tudo. Sem "ver histórico" ao lado de "Ler o Diário agora".
   Roadmap: opção de abrir em página inteira no lugar da janela.
4c. **E-mail de confirmação do aceite** em HTML, com a marca e uma tabela (Arquitetura; prompt entregue ao dono).
5. Avaliar: link para a Lista ao lado de cada valor dos gráficos, com o filtro aplicado (confirmar com o dono).

## 0.7.36: regra (decisão do dono, 12/Nov)

**Não desenvolver agora.** A 0.7.35 foi publicada (12/Nov, 15h22). O dono testa a 0.7.35 e traz o que encontrar; tudo
entra nesta lista e só se implementa quando ele mandar. A 0.7.36 já começada no ramo de trabalho (cabeçalho fixo, Arquivo
com indicador e aviso, Histórico 50 por vez e dica em linhas, fixo em tudo menos no celular) fica parada até lá.

### Ressalvas da segunda revisão da 0.7.35 (Operação, quadro), começar por (1) e (2)

1. **"Conferir agora" com leitura em andamento** diz "Licença conferida agora: ativa" sem consultar a SolverONE. Correção: a
   rota `/conta/conferir` devolve uma marca durante a leitura (ex.: `ocupado: true`), `conferirConta` ganha um 4º estado e
   o botão diz "Há uma leitura em andamento; ela confere a licença sozinha" (PT e EN, com chave), com teste.
2. **Testes que deixam passar mutações:** `test_durante_a_leitura_nao_vai_a_internet` é vazio (usar
   `mock.assert_not_called()` ou `assertNotIn("sem_internet", d)`); `test_sem_internet_nao_destrava` deve conferir o estado
   `aceite_pendente`; um teste pelo `/dados` com ação sem sinal (`or sinal_guardado(lead)`); conduta da tela coberta por
   roteiro de navegador que rode na automação.
3. **"Trocar licença" com o mesmo código:** `carregar()` e `conferirConta()` correm juntos e o aviso/faixa podem sumir;
   encadear `carregar().then(...)`.
4. **"Ler o Diário agora" com licença não ok** não dá retorno enquanto confere: "Conferindo…" num aviso temporário e botão
   desabilitado durante a espera (sem empilhar avisos iguais).
5. **Menu "Abrir a pasta das planilhas no Windows"** ainda mostra o texto velho quando a pasta não existe (PT e EN
   misturados); usar o texto próprio do botão das Configurações.
6. Baixas: `sinal_guardado` com "processo distribuído" em outro contexto (limite; dizer no manual); avisos iguais
   empilhados; "Sem conexão…" parcialmente atrás do diálogo a 1366 px; "Termos aceitos…" some rápido com leitura de outro
   processo; lupa "abrir pasta no windows" sem o "a"; manual: tabela "Quando algo não funciona" sem a mensagem de sem
   conexão e sem "notifique-se a reclamada"; `robo/LEIA-ME.md` com título "v0.7.32" e "Configuração" nas linhas 46 e 120;
   "Salvo. Leitura automática desligada." em PT na tela em EN; Novidades: trocar "Mensagem clara quando o programa se
   encerra" por "Mensagem ao encerrar o programa"; documentos internos com nome de sessão de IA (staging).
7. Aberto da primeira revisão, da Arquitetura: jornada do aceite por pessoa (item 10).

### Achados do teste do dono na 0.7.35

Em `documentacao/FEEDBACK-TESTE-0.7.35.md` (itens 1 a 34). **Feitos na 0.7.36** (12/Nov, noite, com o "pode" do dono), junto
com os itens 1 a 4b acima e as ressalvas (1) a (6). Roteiro do teste: `documentacao/ROTEIRO-TESTE-0.7.36.md`.

## Depois da visita

- Janelas largas no RootifyONE (ficha da licença, prévia do e-mail) e faixa vermelha do e-mail do responsável (RootifyONE).
- Lentidão com muitos processos (medir antes); pasta antiga "Cópias" para dentro de "Cópias da planilha".
- Termos dentro do programa quando já aceitos; página de aceite (largura, texto, aviso "role até o fim") (Arquitetura).
- Canal de teste antes dos clientes (Arquitetura). Regra das integrações a cada mudança (diretrizes e Arquitetura).
- Largura do e-mail no computador; quem atualiza mantém "todos os dias" na leitura (decidido: manter).

## Recomeçar o teste como cliente novo (roteiro para o dono)

Fazer depois de publicada a versão que vai à KR Law. No computador:
1. Fechar o RADAR (menu ☰ → Sair, ou `DIAGNOSTICO.bat`, opção 2).
2. Apagar a tarefa agendada: Agendador de Tarefas → "LexSuiteONE Radar" → Excluir.
3. Apagar a pasta `C:\LexSuiteONE` (programa, configuração e banco) e a pasta das planilhas de teste (`C:\testeradar`).
4. Apagar o atalho "RADAR JUDICIAL" da área de trabalho.
No RootifyONE: criar uma licença nova de teste (o aceite registrado não se desfaz, então a licença antiga já não serve
para testar o aceite), com o e-mail do responsável = o e-mail de teste, sem domínio; enviar o boas-vindas; seguir o e-mail
como o Leandro: baixar, instalar, colar o código e aceitar os termos depois de instalar (testa a correção da 0.7.34).
