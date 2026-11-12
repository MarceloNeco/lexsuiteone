# Roteiro de instalação no cliente — RADAR JUDICIAL 0.7.35 (LexSuiteONE)

## Antes de sair de casa

1. **Teste o instalador no seu computador.** Em judicial.solverone.com.br, "Baixar o RADAR JUDICIAL", abra o arquivo
   baixado e dê dois cliques em `INSTALAR.bat`. Confira: o atalho **RADAR JUDICIAL** apareceu na área de trabalho, a
   tela abriu no navegador, a janela Configurações aceitou a sua pasta do Drive e "Ler o Diário agora" com 2 TRTs criou a planilha
   `LexSuiteONE - Trabalhista.xlsx` (e a pasta `Cópias de segurança`) na pasta da planilha, dentro da pasta escolhida.
2. **Plano B no pen drive:** baixe também o pacote completo (link "Baixe o pacote completo" no fim da página inicial).
   Serve se a rede do cliente bloquear o instalador.
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
2. Na tela (janela própria), o assistente de 4 passos: documento, escritório, nome, e-mail e função; onde fica a
   planilha (Google Drive, outra pasta ou só neste computador); frente e tribunais; o resumo mostra onde a
   planilha ficou. Instale no computador que fica ligado nos horários das leituras.
3. Menu ☰, Configurações, **Armazenamento**: anote o espaço livre no disco (o ideal é mais de 10 GB) e confira onde ficam
   a planilha e a pasta `Cópias de segurança`. Nada é compartilhado com a SolverONE.
4. "Ler o Diário agora" (os 24 TRTs já vêm escolhidos; em Tribunais dá para reduzir a 2 ou 3 para a primeira leitura ser
   rápida). Enquanto roda, mostre a ficha, os filtros, a exportação e a planilha no Drive.
5. Se o agendamento automático falhar (a janela Configurações avisa): em `C:\LexSuiteONE`, `AGENDAR.bat` com botão direito,
   Executar como administrador.
6. Deixe anotado: abre pelo atalho RADAR JUDICIAL; desde a 0.7.29 não há janela preta (para sair: ☰ → Sair; se travar: DIAGNOSTICO.bat, opção 2; suporte: ABRIR.bat --ver); os critérios
   da lista e as empresas excluídas são de cada pessoa, em Configurações → Critérios da lista (a planilha é completa); "Sair do RADAR" (menu ☰) fecha tudo; se aparecer "a planilha
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
