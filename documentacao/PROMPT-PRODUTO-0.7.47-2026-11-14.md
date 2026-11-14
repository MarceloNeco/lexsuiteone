# Prompt para a conversa da Produto (colar inteiro) · 0.7.47 · CNJ fora e antivírus · 14/Nov/2026

```
Prioridade do dono (14/Nov): a 0.7.47 é "CNJ fora e antivírus". Antes de tudo: git pull e leia docs/QUADRO.md inteiro
(pedidos Arquitetura → Produto de 14/Nov e as Decisões do dono 34 a 39).

ARTEFATOS (todos na main):
1. documentacao/DESENHO-LEITURA-E-ANTIVIRUS-2026-11-14.md: seções 1.1 (evidência e diagnóstico), 2.1 a 2.4 (instalador, checagem,
   registro, programa), 2.6.1 (tarefa agendada às claras) e "Decisões do dono".
2. Página do site já no ar: judicial.solverone.com.br/antivirus.html (paginas/antivirus.html, agora sua): o que liberar, texto
   para a TI e passo a passo de 13 antivírus com fonte oficial. O programa e o instalador apontam para ela; não repita o conteúdo.
3. Decisões do dono: 34 sem certificado de assinatura; 35 só a faixa + opção de e-mail em Configuração; 36 página e linha no
   e-mail: sim; 37 leitura pela consulta por padrão (fica para a 0.7.48); 38 aviso geral só preparado; 39 falso positivo aguarda.

O QUE ENTREGAR NA 0.7.47:
a. Diagnóstico "é do CNJ ou é daqui" (1.1): rede.py guarda, em cada falha, código HTTP, cabeçalhos date, server, via, x-cache,
   x-amz-cf-pop, x-amz-cf-id, content-type, retry-after, os 300 primeiros caracteres do corpo, tempo em ms, tentativas e IP
   resolvido; quando o CNJ falha, duas sondas de controle: judicial.solverone.com.br/atualizacao/versao.json e
   comunicaapi.pje.jus.br/api/v1/comunicacao?itensPorPagina=5. Nova coluna "origem" em causas.classificar com as seis
   mensagens da tabela da seção 1.1 (ex.: "O servidor do CNJ respondeu erro (aplicação). Sua internet está normal. Não é problema
   deste computador."). A frase vai na faixa do Painel, no Histórico de leituras e em "Detalhes técnicos".
b. Confirmação pela SolverONE: chamada à ação estado_cnj da lex-conta (1 por 5 min, só quando há falha do CNJ) e a linha "A
   SolverONE também vê o CNJ fora desde 13h30 (23 de 24 tribunais)". A ação é da Arquitetura (lex-conta v19, aguardando o
   "pode aplicar" do dono): até lá, se a resposta vier vazia ou com erro, a linha simplesmente não aparece. Nunca trava.
c. Opção em Configuração (decisão 35): "Avisar por e-mail quando o CNJ ficar fora por mais de 4 horas em dia útil", desligada por
   padrão, com a explicação "o aviso vai para o e-mail cadastrado para esta instalação; um e-mail na queda e um na volta". A
   preferência vai no campo avisar_cnj da ação verificar (a lex-conta v19 grava; antes disso o campo é ignorado sem erro).
d. Instalador reconhece o bloqueio e orienta (2.1 e 2.2): passo 0 do INSTALAR.bat antes de baixar: está dentro do zip
   (%TEMP% + ".zip")? antivírus e firewall (PowerShell Get-CimInstance -Namespace root/SecurityCenter2 -ClassName
   AntiVirusProduct | Select displayName, productState; FirewallProduct; sem o namespace = "não identificado"); pasta gravável;
   saída para os nossos endereços (curl leve). Aviso: "Antivírus encontrado: <nome>. Programas novos costumam ser barrados por ele.
   Antes de continuar, cadastre a exceção da pasta C:\LexSuiteONE (veja judicial.solverone.com.br/antivirus.html) ou peça à TI.
   Depois aperte Enter." Com Defender puro: só "se aparecer aviso, clique em Executar". Cada sinal da tabela 2.1 (zip_temp,
   bloqueio_gravacao, processo_morto, tarefa_falhou, rede_recusada, smartscreen) vira uma mensagem no lugar de "erro": o que
   aconteceu, o antivírus encontrado, os passos do Bitdefender e do Defender por extenso (os demais: link da página) e o texto
   pronto para a TI (o mesmo da página). Nunca "desligue o antivírus". ROTEIRO-INSTALACAO.md e docs/VISITA-KR-LAW.md ganham o
   checklist e perdem a linha que manda desligar a Defesa contra Ameaças.
e. Leitura automática às claras (2.6.1): a tarefa "LexSuiteONE Radar" é criada durante a instalação, na janela visível, com
   schtasks /create /sc daily /st HH:MM /tr "C:\LexSuiteONE\python\pythonw.exe …", sem XML na pasta temporária; quando precisar
   de XML (dias da semana, vários horários), ele fica em C:\LexSuiteONE\tarefa.xml com Author e Description "SolverONE ·
   LexSuiteONE · RADAR JUDICIAL". A tela continua alterando horários pelo mesmo caminho. O instalador avisa antes: "agora vou
   criar a leitura automática".
f. Programa instalado (2.4): Configuração → Sobre este computador mostra antivírus e firewall encontrados (lidos uma vez por dia),
   ligados ou não, e o link "Como liberar o RADAR no <antivírus>" (abre a página, na seção do antivírus). Erros que nomeiam o
   antivírus e apontam os passos: leitura automática não criada ou nunca executada; arquivo que sumiu (python.exe, lexsuite.db,
   planilha não gravada); rede recusada só para os nossos endereços. O painel de saúde registra o sinal no histórico.
g. Registro técnico (2.3): a ação registro da lex-conta passa a receber antivirus (só o displayName), antivirus_ligado (sim/não)
   e sinal (um dos seis acima). Nada de pessoa. A lex-conta v19 grava; antes disso os campos são ignorados sem erro.
h. Área logada por licença, a parte do programa (pedido de 14/Nov, se não entrou na 0.7.46): data-recurso="area-logada" na barra
   de lote, no menu Área logada e no botão do cartão; some quando recursos["area-logada"] === false na resposta da licença.
i. Definição de pronto (CLAUDE.md, 12 pontos onde aplicável): manual (instalação com antivírus, leitura automática, Sobre este
   computador, a opção de e-mail; link da página de antivírus nas linhas de instalação e de "Não consegui criar a leitura
   automática"); índex do site: link "O antivírus bloqueou?" perto do pacote completo; AssistONE (ajuda, tour, busca: "antivírus",
   "CNJ fora", "é daqui ou do CNJ", "leitura automática", "aviso por e-mail"); Novidades formais e curtas; termos SEM mudança (o
   nome do antivírus é dado do computador, coberto por 6.2 (c); o esclarecimento editorial fica para a 1.1); e-mail de
   boas-vindas: uma linha "Se o antivírus bloquear, veja judicial.solverone.com.br/antivirus.html" (se o arquivo for da
   Operação, deixe o pedido no quadro com o texto pronto). Testes: classificador com respostas gravadas (5xx JSON do CNJ +
   sonda ok; HTML da CloudFront; tempo esgotado + sonda falha; sonda ok + reset só no CNJ; 403 de país); os seis sinais do
   instalador simulados; comando do schtasks sem XML em %TEMP% e XML em C:\LexSuiteONE quando há dias da semana; registro
   com os três campos; avisar_cnj persistido e enviado; recurso desligado esconde os três lugares.

Ao terminar, anote "pronta para publicar" no quadro com o commit e a lista do que foi conferido; a Operação revisa e publica
com o "publica a versão 0.7.47" do dono. Dúvida de desenho vai como pedido à Arquitetura no quadro, não ao dono.
```
