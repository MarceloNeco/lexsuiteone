# Desenho curto: ativação por e-mail e código (pedido da Produto, 11/Nov; programa na 0.7.32, depois da visita)

## Como é hoje (`lex-conta`, ação `cadastrar`)
- A licença tem **domínios liberados** (`lex_contas.dominios`): ficha da licença no RootifyONE (campo "Domínios"; o lote de
  e-mails também valida por eles). Se a ficha estiver vazia, o **primeiro cadastro** com e-mail de domínio próprio (não
  Gmail, Outlook etc.) preenche o domínio sozinho.
- E-mail do domínio liberado → pessoa **aprovada** na hora. E-mail de outro domínio → ficava **"aguardando"** a equipe
  (lia normalmente, a não ser que a licença tenha "exigir aprovação"). E-mail já ligado a outra licença → recusa genérica.

## Regra nova (dono, 11/Nov): "o código vale para o domínio do e-mail"
- Com domínios na ficha, e-mail de **fora** é **recusado** (`motivo: dominio_nao_liberado`), com a lista `dominios` na
  resposta para a tela dizer "Este código vale para e-mails @krlaw.com.br". Quem já estava aprovado não é afetado.
- Licença **sem domínio** (começo "aberto"): o primeiro e-mail de domínio próprio libera esse domínio; e-mail de provedor
  público entra sem liberar domínio (como hoje). A equipe ajusta os domínios na ficha quando quiser (RootifyONE).
- **Aplicado na nuvem em 11/Nov (`lex-conta` v15)**: vale já para o programa atual (que só vê a recusa no cadastro).

## Jornada no programa (Produto, 0.7.32)
1. **Pelo link do e-mail de boas-vindas** (`#codigo=…&email=…&nome=…` no instalador ou na primeira tela): código e e-mail
   chegam preenchidos e **fixos** (cinza, código mascarado `LEX-••••-XXXX`); a pessoa confere o nome e segue.
2. **Sem link**: a pessoa digita o código e o e-mail; antes de pedir o resto, o programa chama a nova ação
   **`conferir {codigo, email, instalacao}`** (não grava nada; 60 por hora por código) e trata a resposta:
   - `ok: true` → segue; mostra "Código do escritório X" (`escritorio`); se `dominio_novo`, avisa "o domínio @… será liberado para este escritório";
   - `dominio_nao_liberado` → "Este código vale para e-mails @krlaw.com.br. Use o e-mail do escritório ou fale com judicial@solverone.com.br" (`dominios` na resposta);
   - `codigo_desconhecido` / `email_recusado` / `dados_invalidos` → mensagens já existentes em `MOTIVOS`.
3. **Cadastro** (`cadastrar`) como hoje, com a caixa de aceite dos termos; a mesma regra de domínio vale lá (dupla conferência).
4. **Depois de salvo, código e e-mail não se editam**: o código só muda reinstalando (ou por "Esquecer esta licença" na
   Configuração, a desenhar); o e-mail só pelo fluxo "Sou outra pessoa" do Perfil, que refaz o `cadastrar` com o novo
   e-mail (e a conferência de domínio).
- Mensagens PT/EN; nada de código inteiro na tela (mascarado), inteiro só no e-mail de boas-vindas.

## RootifyONE
Nada novo: a ficha já tem "Domínios" e o lote valida por eles. Sugestão de (?) no campo: "E-mails desses domínios ativam o
programa com este código; e-mail de fora é recusado. Vazio = o primeiro cadastro de domínio próprio libera o domínio."
