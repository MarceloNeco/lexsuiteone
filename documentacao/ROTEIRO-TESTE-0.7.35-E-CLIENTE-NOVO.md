# Roteiro do dono: teste da 0.7.35 e simulação de cliente novo (12/Nov/2026)

## Parte 1 · Testar a 0.7.35 no computador que já tem o RADAR (uns 20 minutos)

1. **Atualizar.** Abra o RADAR pelo atalho e aceite a atualização. Deve aparecer a **tela de abertura** ("RADAR JUDICIAL ·
   Carregando…") e, depois, a janela **Novidades da versão 0.7.35**: larga, com as linhas da 0.7.34 e da 0.7.35 e o botão
   de fechar à vista.
2. **Versão.** Engrenagem ⚙ → Sobre este computador: "Versão instalada 0.7.35".
3. **Conferir agora.** ⚙ → Licença e termos → **Conferir agora**: "Licença conferida com a SolverONE agora: ativa."
4. **Sem internet.** Desligue o Wi-Fi e clique de novo em **Conferir agora**: "Sem conexão com a SolverONE: não foi possível
   conferir agora…". Religue o Wi-Fi.
5. **Trocar licença com o mesmo código.** Trocar licença → Trocar → digite o mesmo código → Salvar: a janela fecha e aparece
   "Licença conferida…" no alto da tela.
6. **Pasta das planilhas.** "Pasta das planilhas" escrito uma vez só, cartões na largura toda e o botão **Abrir a pasta no
   Windows**: o Explorador abre na pasta.
7. **Ler o Diário agora.** A faixa de andamento fica numa linha (barra, porcentagem e Interromper); as mensagens anteriores
   ficam em "Mensagens anteriores". Deixe terminar.
8. **Painel.** No gráfico "Como a ação nova foi reconhecida" não existe mais "Guardada antes da 0.7.16".
9. **Sazonalidade parada.** Com a busca de estatísticas parada aparece **Continuar à noite**; ao clicar, aparece o recado.
10. **Lupa** (🔍): "conferir agora" e "abrir a pasta" acham os botões novos.
11. **Sair.** Menu ☰ → Sair: "O RADAR foi encerrado. Pode fechar esta janela…" (a janela pode fechar sozinha).

Anote o que estranhar (print e uma frase) e mande para a Produto: entra na lista da 0.7.36.

## Parte 2 · Simular um cliente novo (depois que a Parte 1 passar)

Usa uma **licença nova de teste** e um e-mail novo que cai na sua caixa: `mafreitas1979+teste2@gmail.com` (o Gmail entrega
na mesma caixa; para o sistema é outro e-mail).

**No RootifyONE**
1. RADAR JUDICIAL → Licenças → **+ Criar licença**: escritório "Teste 2 (SolverONE)", e-mail do responsável =
   `mafreitas1979+teste2@gmail.com`, domínio em branco.
2. Lápis ✏️ da licença nova → **Preparar e-mail de boas-vindas** → Enviar agora → Enviar.

**No computador (zerar o RADAR atual, como se nunca tivesse sido instalado)**
3. Menu ☰ → Sair (ou `C:\LexSuiteONE\DIAGNOSTICO.bat`, opção 2).
4. Iniciar → "Agendador de Tarefas" → Biblioteca → "LexSuiteONE Radar" → Excluir.
5. Apague a pasta `C:\LexSuiteONE`, a pasta das planilhas de teste (`C:\testeradar`) e o atalho RADAR JUDICIAL da área de
   trabalho.

**Como cliente**
6. Abra o e-mail de boas-vindas → **Baixar o RADAR JUDICIAL** → abra o arquivo → INSTALAR.bat → cole o código.
7. Siga o assistente (nome, e-mail `mafreitas1979+teste2@gmail.com`, pasta, tribunais).
8. **Teste do pior caso:** não aceite os termos antes. Clique em "Ler o Diário agora": aparece "Falta aceitar os termos".
   Clique em **Aceitar os termos**, role o texto até o fim, marque, confirme e **volte ao programa**: em segundos ele deve
   liberar sozinho (ou clique em **Já aceitei**). Depois, "Ler o Diário agora" lê normalmente.
9. Confira: chegou o e-mail de confirmação do aceite; no RootifyONE, a ficha da licença mostra os termos aceitos.

Se algo falhar, pare e mande o print.
