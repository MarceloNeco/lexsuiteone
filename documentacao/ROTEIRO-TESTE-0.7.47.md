# Roteiro de teste da 0.7.47 (CNJ fora e antivírus) — para o dono

Faça num computador com Windows, depois que a Operação publicar a 0.7.47. Cada passo diz o que você deve ver.

## 1. Instalação (o instalador novo)

1. Baixe o instalador no site e **abra o .zip sem extrair**: dê dois cliques no `INSTALAR.bat` de dentro dele.
   Deve aparecer: "Este instalador foi aberto de dentro do arquivo .zip, sem extrair" e os 3 passos. Feche.
2. Clique com o botão direito no .zip → "Extrair tudo" → dois cliques no `INSTALAR.bat` da pasta extraída.
3. Antes de pedir o código, ele mostra "Conferindo este computador antes de instalar..." e:
   - com só o Microsoft Defender: "Antivírus encontrado: Windows Defender" e a dica de clicar em "Executar";
   - com outro antivírus (ex.: Bitdefender): o nome, os passos para cadastrar a exceção e "Depois aperte Enter".
4. Siga até o fim. No passo **"5 de 6"** ele diz "Agora vou criar a leitura automática" e depois "Leitura automática criada".
5. Confira no Windows: menu Iniciar → "Agendador de Tarefas" → a tarefa **LexSuiteONE Radar** existe, e na aba Geral o autor é
   "SolverONE · LexSuiteONE · RADAR JUDICIAL". Na pasta `C:\LexSuiteONE` há o arquivo `tarefa.xml`.

## 2. Sobre este computador

1. Abra o RADAR → Configurações (engrenagem) → **Sobre este computador**.
2. Deve ver: **Antivírus** (nome, ligado ou desligado), **Firewall** e o link **"Como liberar o RADAR no …"**. Clique: abre a
   página de antivírus do site, já na seção daquele antivírus.
3. Logo abaixo, **Recursos da licença**: "Trazer dados da área logada: ligado" (ou "desligado pela licença").

## 3. Aviso por e-mail do CNJ

1. Configurações → Leitura do Diário: a caixa **"Avisar por e-mail quando o CNJ ficar fora por mais de 4 horas em dia útil"**
   vem **desmarcada**, com a explicação embaixo.
2. Marque, clique em Salvar, feche e abra de novo: continua marcada. (O e-mail de verdade só sai quando a Arquitetura ligar a
   parte da nuvem.)

## 4. Quando o CNJ falha (só dá para ver num dia em que o CNJ estiver fora)

- A faixa vermelha do Painel e o Histórico de leituras mostram uma frase como "O servidor do CNJ respondeu erro (aplicação).
  Sua internet está normal. Não é problema deste computador." Em "Ver detalhes técnicos" aparecem os cabeçalhos e o tempo.
- Quando a nuvem da SolverONE tiver a função nova (Arquitetura), aparece também "A SolverONE também vê o CNJ fora desde…".

## 5. O que já foi testado aqui (sem Windows)

Testes automáticos: `robo/testes/test_v0747.py` (classificador com respostas gravadas, sondas, linha da SolverONE, opção de
e-mail, registro com os três campos, tarefa sem XML na pasta temporária, os seis sinais do instalador) e o bloco 7 de
`robo/testes/tela/fluxos.js` (a tela). Os instaladores `.bat` não rodaram num Windows de verdade: por isso os passos 1 e 2 acima
são os mais importantes.
