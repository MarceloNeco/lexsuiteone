# Dossiê: antivírus na instalação da KR Law (13/Nov/2026) e o que mudar no instalador, no programa e no manual

Montado pela Operação a pedido do dono (14/Nov): "faça um dossiê, guarde todas as imagens… o instalador tem que detectar o
antivírus, não para contornar, mas para orientar". **As fotos não ficam no repositório**: elas mostram dados do cliente
(agenda, nomes de pessoas, e-mail, números de processo, código de cliente, pasta do usuário do Windows). Ficam com o dono
(pacote `dossie-antivirus-2026-11-13.zip`, entregue no chat da Operação) e são citadas aqui pelo número. Para usar no
manual, recortar só a janela do antivírus, sem nada do cliente.

## 1. O que aconteceu (horário de Brasília, 13/Nov)

| Hora | Foto | O que se viu |
|---|---|---|
| ~11h30 | (não há foto nesta conversa; ver a seção 6) | 1ª instalação. O programa instalou e abriu. Ao criar a leitura automática, o Bitdefender barrou: notificação "Comportamento malicioso bloqueado" (2 h antes da foto 03). |
| 13h35 | 01 | 2ª instalação, com o **pacote completo** baixado antes da 0.7.40 (instalou a 0.7.39). Código confirmado, impressão digital conferida, e no passo 3: `lexsuite_robo.py: Can't create '\\?\C:\LexSuiteONE\lexsuite_robo.py': No such file or directory` / `tar.exe: Error exit delayed from previous errors` / "Não consegui descompactar o pacote em C:\LexSuiteONE". O teste de escrita na pasta tinha passado: o Windows deixava criar arquivo; o antivírus barrava o `.py`. |
| 13h36 | 02 | Bitdefender **Total Security**, painel "Você está seguro" (nenhum alerta em destaque: o bloqueio fica escondido em Notificações). |
| 13h37 | 03 | Notificações → Crítico: **"Comportamento malicioso bloqueado"**, recurso **Defesa contra Ameaças**, "Você precisa reiniciar seu dispositivo para finalizar o processo de limpeza", "bloqueou todos os aplicativos envolvidos", ID `SuspiciousBehavior.CF5CA6A45DED44C4`. Botões: Ver cronologia de ataques, Ver aplicativos, Reiniciar. (Abaixo, "Conexão suspeita bloqueada" de 22 h e de 28/Out: anteriores, sem relação conhecida.) |
| 13h39 | 04 | "Ver aplicativos": **62 aplicativos foram bloqueados**. O primeiro, marcado **Malware: `schtasks.exe`** com a linha de comando `schtasks /create /f /tn "LexSuiteONE Radar" /xml C:\Users\<usuário>\AppData\Local\Temp\lexsuite-tarefa-<aleatório>.xml`; depois `pythonw.exe` (`C:\LexSuiteONE\python`) e até `chrome.exe`. **É a criação da leitura automática** (`robo/lexsuite/agendar.py`, `schtasks /create … /xml` a partir de um XML na pasta temporária, chamado pelo `pythonw` sem janela). |
| 13h40 | 05 | Defesa contra Ameaças → Configurações: chaves "Defesa contra Ameaças" e "Detecção de exploit"; links **Administrar exceções** e **Gerenciar quarentena**. |
| 13h41 | 06 | "Opções de exceções": campo "Digite o caminho, nome da extensão, URL ou domínio" e três chaves: Antivírus, Detecção Ameaças Online, Defesa contra Ameaças. |
| 13h42 | 07 | `C:\LexSuiteONE\*` **não é aceito** (com asterisco o Salvar fica apagado). |
| 13h42 | 08 | `c:\LexSuiteONE\` (sem asterisco) aceito; "Defesa contra Ameaças" ligada, Salvar aceso. |
| 13h43 | 09 | Ao ligar "Antivírus" aparecem três caixas: Verificação ao acessar, Análise a-pedido, **Scripts incorporados**. "Detecção Ameaças Online" não ligou. |
| ~13h50 | — | Exceção salva, computador reiniciado, instalação de novo: **funcionou** (foto 10 mostra o RADAR 0.7.40 aberto). |
| 14h00–14h54 | 10 a 15 | Outro problema, sem relação com o antivírus: o **serviço de caderno do CNJ caiu** (erro 500 em 11, 12 e 13/11, TRT2, TRT7 e TRT9, também na casa do dono). Fotos 16 a 18: testes no navegador (caderno com 500; a consulta respondia, com o limite de 10 mil). Ver a seção 5. |

## 2. Por que o antivírus barrou (o que o nosso pacote faz que parece ataque)

O Bitdefender (Defesa contra Ameaças, por comportamento) somou, em poucos minutos:

1. um `.bat` **sem assinatura digital** baixado da internet, que descompacta um Python inteiro (`python.zip`) e um pacote em
   `C:\LexSuiteONE`;
2. um `pythonw.exe` (Python **sem janela**) rodando de uma pasta fora de `Program Files`;
3. esse `pythonw` chamando `schtasks /create` com um **XML da pasta temporária** para criar uma tarefa que roda sozinha
   (o mesmo desenho que um programa malicioso usa para "persistir" no computador);
4. PowerShell criando atalhos e `curl` mandando dados para a nuvem (`supabase.co`).

Isoladas, nenhuma é ataque; juntas, batem com o padrão "baixa, descompacta, roda escondido e se agenda". O antivírus
então bloqueou **todos** os programas envolvidos (62), marcou o `schtasks` como malware e deixou uma "limpeza" pendente
até reiniciar. Enquanto a limpeza estava pendente, ele barrava a criação dos arquivos do programa (foto 01).

## 3. O que já mudou depois do dia 13 (publicado)

- **0.7.43**: os dois instaladores, se o `tar.exe` falha, tentam o `Expand-Archive` do PowerShell e, numa instalação nova,
  a pasta do usuário (`%LOCALAPPDATA%\LexSuiteONE`); a mensagem final diz que o mais provável é o antivírus e pede para
  liberar `C:\LexSuiteONE` e `%LOCALAPPDATA%\LexSuiteONE`.
- **0.7.44**: quando a leitura automática não pode ser criada, a mensagem cita o antivírus (ex.: Bitdefender) e pede para
  liberar a pasta e salvar de novo.
- **0.7.45**: com a tela aberta, se a hora marcada passa e a tarefa do Windows não roda, o programa lê sozinho (uma vez por
  horário).

**Ainda falta** o que o dono pediu agora: o programa **saber qual antivírus** está no computador e **orientar antes**, em vez
de esperar o erro.

## 4. O que o dono pediu (14/Nov) e a proposta

Regra do dono: **detectar e orientar; nunca contornar** (nada de desligar proteção, esconder processo ou mudar o nome das
coisas para fugir do antivírus).

### 4.1 Detectar o antivírus (instalador e programa)

- No Windows 10 e 11 (não no Windows Server), a Central de Segurança informa os antivírus instalados:
  `Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct` → `displayName` (ex.: "Bitdefender
  Antivirus", "Windows Defender") e `productState` (ligado ou não). Só leitura, sem permissão de administrador.
- **Instalador** (`INSTALAR.bat` e `INSTALAR-COMPLETO.bat`): logo depois do código de cliente, mostrar
  "Antivírus encontrado: Bitdefender. Ele costuma bloquear programas novos. Antes de continuar, libere a pasta
  C:\LexSuiteONE (passo a passo: …)" e esperar a pessoa confirmar.
- **Programa** (tela e Configurações → Sobre este computador): mostrar o antivírus encontrado e um link "Como liberar o
  RADAR no <antivírus>" para o manual.
- **Nos erros** (instalador: descompactar, preparar o Python, criar atalho; programa: criar a leitura automática): em vez
  de "erro", dizer "O <antivírus> bloqueou…" com o passo a passo daquele antivírus.

### 4.2 Passo a passo por antivírus (manual, roteiro de instalação e mensagens)

- **Bitdefender (verificado nas fotos 03 a 09)**: Proteção → Defesa contra Ameaças (Abrir) → Configurações → Administrar
  exceções → "+ Adicionar uma exceção" → `C:\LexSuiteONE\` (**sem asterisco**) → ligar Antivírus (com Verificação ao
  acessar, Análise a-pedido e Scripts incorporados) e Defesa contra Ameaças → Salvar. Se já houve bloqueio: Notificações
  → "Comportamento malicioso bloqueado" → **Reiniciar** (a limpeza só termina depois de reiniciar) e instalar de novo.
  Repetir para `%LOCALAPPDATA%\LexSuiteONE\` se a instalação foi para a pasta do usuário.
- **Microsoft Defender, Kaspersky, ESET, Norton, McAfee, Avast/AVG, Sophos, Trend Micro**: **a pesquisar** (pedir ao
  `pesquisador`, com a página oficial de cada um e a data), porque a tela muda de versão para versão. Não escrever de cabeça.
- Antivírus corporativo gerenciado pela TI (o escritório não consegue mudar sozinho): texto pronto para a TI, com as pastas,
  os arquivos (`python\python.exe`, `python\pythonw.exe`, `lexsuite_robo.py`), a tarefa do Windows ("LexSuiteONE Radar") e
  os endereços (`judicial.solverone.com.br`, `comunicaapi.pje.jus.br`, `qvdvkqydhnadhewcidia.supabase.co`, `brasilapi.com.br`,
  `minhareceita.org`).

### 4.3 Diminuir o que parece ataque (sem esconder nada)

- **Assinatura digital** do instalador e dos executáveis (certificado de assinatura de código, Authenticode). Um `.bat`
  não se assina; trocar por um instalador `.exe`/`.msi` assinado é a medida que mais reduz falso positivo. Decisão do dono
  (custo do certificado, por ano) e desenho da Arquitetura.
- **Avisar os fabricantes do falso positivo**: enviar o pacote ao Bitdefender e à Microsoft pelos formulários oficiais de
  falso positivo (o `pesquisador` acha os endereços oficiais). Fazer de novo a cada versão grande.
- **Leitura automática**: criar a tarefa sem XML na pasta temporária (argumentos diretos do `schtasks`, ou XML dentro da
  pasta do programa), e de preferência **durante a instalação**, com a pessoa vendo, e não depois pelo `pythonw` escondido.
  Avaliar com a Arquitetura: não é para enganar o antivírus, é para o programa fazer às claras o que precisa fazer.

### 4.4 Manual, roteiro de instalação, e-mail e site

- Seção nova no manual: "Antivírus" (por que bloqueia, como saber, como liberar, com fotos **recortadas** sem dado do
  cliente; uma por antivírus).
- `robo/ROTEIRO-INSTALACAO.md` e `docs/VISITA-KR-LAW.md`: checklist **antes** de instalar ("qual antivírus? quem
  administra? já liberar a pasta").
- E-mail de boas-vindas e site: uma linha "Se o antivírus bloquear, veja: <link do manual>".

### 4.5 Saber quanto isso acontece

- O instalador já manda à SolverONE a etapa em que falhou. Mandar também **o nome do antivírus** (só o `displayName`, que
  não é dado pessoal) ajudaria a saber quais antivírus os escritórios usam. Muda o que é enviado: precisa do "pode" do dono
  e da revisão da Arquitetura (termos e LGPD).

## 5. A outra causa do dia: o CNJ fora (para não confundir com o antivírus)

Das 13h30 em diante, o serviço de **caderno** do DJEN respondeu "500 Server Error" para todos os dias e tribunais testados.
Não era o antivírus nem a rede do hotspot (a resposta vinha do servidor do CNJ, e a consulta pública respondia). O que mudou:
0.7.41 (o dia de hoje com erro não para a leitura), 0.7.42 (pula dias com erro, guarda como pendentes e lê quando o CNJ
volta), 0.7.44 (confere o CNJ de 15 em 15 minutos com a tela aberta). Falta (Arquitetura): caminho alternativo pela
consulta, dividindo por vara por causa do limite de 10 mil resultados.

## 6. Material em outras conversas

- A 1ª instalação (~11h30) e o primeiro bloqueio foram contados à conversa da Produto ou da visita; o resumo está em
  `docs/VISITA-KR-LAW.md` (seção "Se o Windows ou o antivírus bloquear"). Resultado da busca nas outras conversas: ver a
  linha do quadro "Dossiê do antivírus".

## 7. Lista das fotos (pacote do dono)

01 instalador com erro no tar · 02 Bitdefender painel · 03 notificação "Comportamento malicioso bloqueado" · 04 62
aplicativos bloqueados (schtasks como malware) · 05 Configurações e Administrar exceções · 06 Opções de exceções vazio ·
07 asterisco não aceito · 08 pasta sem asterisco aceita · 09 opções do Antivírus · 10 a 15 RADAR com o CNJ fora · 16 a 18
testes do CNJ no navegador. Cada arquivo tem a hora no nome.
