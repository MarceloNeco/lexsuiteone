# Roteiro de instalação no cliente — RADAR JUDICIAL (LexSuiteONE; vale para a versão que o site entrega)

## Antes de sair de casa

1. **Teste o instalador no seu computador.** Em judicial.solverone.com.br, "Baixar o RADAR JUDICIAL", abra o arquivo
   baixado e dê dois cliques em `INSTALAR.bat`. Confira: o atalho **RADAR JUDICIAL** apareceu na área de trabalho, a
   tela abriu no navegador, a janela Configurações aceitou a sua pasta do Drive e "Ler o Diário agora" com 2 TRTs criou a planilha
   `LexSuiteONE - Trabalhista.xlsx` (e a pasta `Cópias de segurança`) na pasta da planilha, dentro da pasta escolhida.
2. **Plano B no pen drive:** baixe também o **pacote completo** (link "Baixe o pacote completo (11 MB)", logo abaixo do botão
   de baixar, ou https://judicial.solverone.com.br/downloads/Instalar-LexSuiteONE-completo.zip). Ele traz o programa e o
   Python e não baixa nada durante a instalação: serve se o antivírus ou a rede do cliente bloquearem o instalador.
3. A planilha não precisa ser levada: ela nasce no Drive de quem instala, na primeira leitura.

## No cliente (30 a 45 minutos, mais o tempo da primeira leitura)

Perguntas antes de começar:
- O computador tem o **Google Drive para computador**? (Ícone na bandeja; pasta "Meu Drive" no Explorador.) Se não
  tiver, instale pelo site do Google Drive, com a conta do escritório.
- Qual conta Google é a do escritório? É nela que a planilha vai morar.
- Em que dias e horários o computador costuma estar ligado? (O padrão é de segunda a sexta, às 20h e às 8h; em
  Configurações, Leitura, dá para mudar os dias da semana e os horários. Se estiver desligado na hora, a leitura acontece quando ele ligar.)

Passos:
1. No navegador do cliente, judicial.solverone.com.br, "Baixar o RADAR JUDICIAL". Abra o arquivo baixado e dê dois
   cliques em `INSTALAR.bat` ("Executar"; ou "Mais informações" e "Executar assim mesmo"). Ele instala em
   `C:\LexSuiteONE` (ou na pasta do usuário, se o Windows não deixar), cria o atalho e abre a tela. Na primeira janela
   ele pede o **código de cliente** (está no e-mail de boas-vindas): cole com o botão direito do mouse e aperte Enter.

   **Antivírus: checklist antes de instalar** (0.7.47; regra do dono: detectar, explicar e orientar, sem tirar a proteção.
   Em 13/Nov o Bitdefender do Leandro barrou a leitura automática):
   - [ ] **Extrair o .zip antes** (botão direito → Extrair tudo) e rodar o `INSTALAR.bat` de dentro da pasta extraída. Aberto
     de dentro do .zip, o instalador para e pede isso.
   - [ ] **Ver qual antivírus o computador tem**: o instalador mostra no começo ("Antivírus encontrado: …"), antes de baixar.
   - [ ] **Cadastrar a exceção antes de continuar**: a pasta `C:\LexSuiteONE` (com as subpastas) e os programas
     `C:\LexSuiteONE\python\pythonw.exe` e `python.exe`. No Bitdefender: Proteção → Defesa contra Ameaças → Configurações →
     Administrar exceções → `C:\LexSuiteONE\` sem asterisco, ligando Antivírus (Verificação ao acessar, Análise a pedido,
     Scripts incorporados) e Defesa contra Ameaças → Salvar; se já houve bloqueio, Notificações → **Reiniciar** antes de
     instalar de novo. Os outros antivírus, com a fonte oficial: judicial.solverone.com.br/antivirus.html.
   - [ ] **Se a TI cuida do antivírus ou da rede**: mandar o "Texto para a TI" da página (botão Copiar): pasta, programas,
     tarefa "LexSuiteONE Radar" e os endereços `judicial.solverone.com.br`, `comunicaapi.pje.jus.br`,
     `qvdvkqydhnadhewcidia.supabase.co`, `brasilapi.com.br` e `minhareceita.org`.
   - [ ] Aviso "O fornecedor não pôde ser verificado": clicar em **Executar** (ou "Mais informações" → "Executar assim mesmo").
     O programa ainda não tem assinatura digital.
   - [ ] No passo "5 de 6" o instalador cria a leitura automática (tarefa "LexSuiteONE Radar") na própria janela e confere.
     Se não conseguir, diz qual antivírus impediu e mostra os passos; a tela aberta lê sozinha enquanto isso.
   - [ ] Se o instalador disser que o programa "fechou logo ao abrir" ou que não conseguiu gravar os arquivos: é o
     antivírus. Restaurar da quarentena, cadastrar a exceção e rodar o instalador de novo. Não é preciso tirar a proteção.
   - Plano B: o **pacote completo** (11 MB), que não baixa nada durante a instalação:
     https://judicial.solverone.com.br/downloads/Instalar-LexSuiteONE-completo.zip → botão direito no arquivo → **Extrair
     tudo** → dois cliques em `INSTALAR.bat` → Executar → código de cliente.
2. Na tela (janela própria), o assistente de 4 passos: documento, escritório, nome, e-mail e função; onde fica a
   planilha (Google Drive, outra pasta ou só neste computador); frente e tribunais; o resumo mostra onde a
   planilha ficou. Instale no computador que fica ligado nos horários das leituras.
   **Aceite dos termos:** o ideal é o responsável aceitar pelo link do e-mail antes de instalar. Se aceitar depois, basta
   voltar ao programa: ele confere sozinho em segundos (ou clique em "Já aceitei", ou Configurações → Licença e termos →
   "Conferir agora"). Antes do aceite, o programa não lê o Diário.
3. Menu ☰, Configurações, **Armazenamento**: anote o espaço livre no disco (o ideal é mais de 10 GB) e confira onde ficam
   a planilha e a pasta `Cópias de segurança`. Nada é compartilhado com a SolverONE.
4. "Ler o Diário agora" (os 24 TRTs já vêm escolhidos; em Tribunais dá para reduzir a 2 ou 3 para a primeira leitura ser
   rápida). Enquanto roda, mostre a ficha, os filtros, a exportação e a planilha no Drive.
5. A leitura automática é criada pelo instalador (passo "5 de 6"). Se ele avisar que não conseguiu, depois de cadastrar a
   exceção do antivírus abra Configurações → Leitura do Diário e clique em **Salvar**: o programa cria a tarefa de novo e confirma.
6. Deixe anotado: abre pelo atalho RADAR JUDICIAL; desde a 0.7.29 não há janela preta (para sair: ☰ → Sair; se travar: DIAGNOSTICO.bat, opção 2; suporte: ABRIR.bat --ver); os destaques
   e as empresas excluídas são de cada pessoa, em Configurações → Destaques e exclusões (a planilha é completa); "Sair do RADAR" (menu ☰) fecha tudo; se aparecer "a planilha
   está ficando grande", clique em "Limpar a planilha (com cópia)"; dúvidas para **judicial@solverone.com.br**.

Plano B (o instalador não baixou): descompacte o pacote completo do pen drive em `C:\LexSuiteONE` e dê dois cliques em
`ABRIR.bat`. Ele prepara o que falta e abre a mesma tela.

## Depois, do seu lado

- Na planilha compartilhada, as abas ocultas Log (leu? quantas?), Saúde (algum aviso?) e Sobre (versão, impressão da chave).
- Para desligar, avisar ou exigir versão: aba oculta Controle. A linha "suporte" já vem com `judicial@solverone.com.br`.
- Versão nova: pela automação "Publicar versão assinada" (ver `docs/PUBLICAR.md` no repositório). O programa instalado
  busca em judicial.solverone.com.br/atualizacao ao abrir, ou quando alguém clica em "Verificar atualização".

## Ensaio geral com uma segunda conta Google (simulando o cliente)

1. No computador de teste, instale o Google Drive para computador com a conta "cliente".
2. Instale pelo site (`INSTALAR.bat`), aponte a janela Configurações para o "Meu Drive" dessa conta e rode com 2 TRTs.
3. No Drive da conta cliente, dê acesso de editor à subpasta `LexSuiteONE` para a sua conta principal.
4. Na conta principal, abra a planilha (abas ocultas em "Ver > Planilhas ocultas"), mude `ativo` para `não` na aba
   Controle e, no computador de teste, clique em "Ler o Diário agora": o programa deve recusar e mostrar a mensagem.
   Volte para `sim`.
5. Rode o `INSTALAR.bat` de novo: deve atualizar sem perder a configuração nem a lista.

A instalação pede o **código do cliente** (está no e-mail de boas-vindas); depois de confirmado pela SolverONE, ele
fica travado e mascarado, e só se troca em Configurações → Licença e termos → "Trocar licença".
