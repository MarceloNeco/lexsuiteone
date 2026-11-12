# Roteiro do dono: teste da 0.7.35 e simulação de cliente novo (12/Nov/2026)

## Parte 1 · Testar a 0.7.35 no computador que já tem o RADAR (detalhado, 12/Nov, noite)

Licença em uso neste teste: **"Teste Marcelo"**, código terminado em **E3LF**. Para copiar o código inteiro sem procurar
e-mail: RootifyONE → RADAR JUDICIAL → Licenças → linha "Teste Marcelo" → coluna **Código** (selecione e Ctrl+C).

1. **ATUALIZAR: JÁ FEITO.**
2. **VERSÃO 0.7.35: JÁ FEITO.**
3. **CONFERIR AGORA: JÁ FEITO** (anotados os itens 8 a 11 da lista de feedbacks).
4. **Sem internet.** Desligue o Wi-Fi (ícone de rede no canto inferior direito do Windows). No RADAR: ⚙ → Licença e
   termos → Conferir agora. Esperado, no rodapé da janela: "Sem conexão com a SolverONE: não foi possível conferir agora…";
   a licença continua ativa (falta de internet não bloqueia). Religue o Wi-Fi.
5. **Trocar licença com o mesmo código.** Para quê: é o caminho de quem recebe um código novo ou quer forçar a conferência
   (por exemplo, logo depois de aceitar os termos). Na 0.7.33, com o mesmo código, o programa não conferia nada e ficou
   preso em "Falta aceitar os termos". O teste confirma que agora ele confere, fecha a janela e não apaga nada. Passos: ⚙ →
   Licença e termos → Trocar licença → confirme → cole o código da "Teste Marcelo" → Salvar. Esperado: a janela fecha, aparece
   "Licença conferida com a SolverONE agora: ativa" no alto da tela, e destaques e exclusões continuam lá.
6. **Pasta das planilhas.** ⚙ → Pasta das planilhas. Esperado: o título uma vez só, os cartões na largura toda e o botão
   **Abrir a pasta no Windows**, que abre o Explorador em `c:\testeradar\LexSuiteONE`.
7. **Ler o Diário agora.** Feche as Configurações e clique em Ler o Diário agora. Esperado: a faixa de andamento numa linha
   (barra, porcentagem e Interromper) e as mensagens antigas em "Mensagens anteriores" (clique para abrir). Deixe terminar.
8. **Painel.** Aba Painel → gráfico "Como a ação nova foi reconhecida". Esperado: não existe mais "Guardada antes da
   0.7.16"; as antigas aparecem pelo sinal do texto ou como "Sem sinal registrado".
9. **Sazonalidade parada.** No Painel, o quadro Sazonalidade. Se a busca estiver rodando, clique em Pausar. Esperado: aparecem Continuar e
   **Continuar à noite**; ao clicar em Continuar à noite, aparece o recado.
10. **Lupa.** Clique em 🔍 no topo e digite "conferir agora": o resultado leva ao botão. Depois digite "abrir a pasta": leva
    ao botão da Pasta das planilhas.
11. **Sair.** Menu ☰ → Sair. Esperado: "O RADAR foi encerrado. Pode fechar esta janela…" (a janela pode fechar sozinha).
    Para abrir de novo: atalho RADAR JUDICIAL na área de trabalho.

Estranhou algo: print e uma frase para a Produto.

## Parte 2 · Simular um cliente novo (depois que a Parte 1 passar)

Usa uma **licença nova de teste** e um e-mail novo que cai na sua caixa: o seu e-mail com "+teste2" antes do @ (ex.: `seunome+teste2@gmail.com`) (o Gmail entrega
na mesma caixa; para o sistema é outro e-mail).

**No RootifyONE**
1. RADAR JUDICIAL → Licenças → **+ Criar licença**: escritório "Teste 2 (SolverONE)", e-mail do responsável =
   o seu e-mail com "+teste2" antes do @ (ex.: `seunome+teste2@gmail.com`), domínio em branco.
2. Lápis ✏️ da licença nova → **Preparar e-mail de boas-vindas** → Enviar agora → Enviar.

**No computador (zerar o RADAR atual, como se nunca tivesse sido instalado)**
3. Menu ☰ → Sair (ou `C:\LexSuiteONE\DIAGNOSTICO.bat`, opção 2).
4. Iniciar → "Agendador de Tarefas" → Biblioteca → "LexSuiteONE Radar" → Excluir.
5. Apague a pasta `C:\LexSuiteONE`, a pasta das planilhas de teste (`C:\testeradar`) e o atalho RADAR JUDICIAL da área de
   trabalho.

**Como cliente**
6. Abra o e-mail de boas-vindas → **Baixar o RADAR JUDICIAL** → abra o arquivo → INSTALAR.bat → cole o código.
7. Siga o assistente (nome, e-mail o seu e-mail com "+teste2" antes do @ (ex.: `seunome+teste2@gmail.com`), pasta, tribunais).
8. **Teste do pior caso:** não aceite os termos antes. Clique em "Ler o Diário agora": aparece "Falta aceitar os termos".
   Clique em **Aceitar os termos**, role o texto até o fim, marque, confirme e **volte ao programa**: em segundos ele deve
   liberar sozinho (ou clique em **Já aceitei**). Depois, "Ler o Diário agora" lê normalmente.
9. Confira: chegou o e-mail de confirmação do aceite; no RootifyONE, a ficha da licença mostra os termos aceitos.

Se algo falhar, pare e mande o print.
