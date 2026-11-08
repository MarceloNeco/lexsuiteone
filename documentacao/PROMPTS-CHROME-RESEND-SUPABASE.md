# Prompts para o Claude in Chrome: chave do Resend nos Secrets do Supabase (08/Nov/2026)

Dois prompts, um por aba. O valor da chave **nunca** é lido, copiado ou digitado pela extensão: quem copia e cola é o dono,
com Ctrl+C e Ctrl+V. Antes de cada prompt, o dono faz o login no site na própria aba, com a extensão fechada ou pausada.

## Prompt 1 · Resend: criar a chave só de envio

```
Você está numa aba do Chrome onde eu já fiz login em resend.com. Tarefa: criar UMA chave de API só de envio, sem nunca
ler, copiar, digitar ou repetir o valor dela.

1. Abra https://resend.com/api-keys.
2. Clique em "Create API Key".
3. Preencha: Name = supabase-lex-conta. Permission = "Sending access" (não "Full access"). Se houver o campo Domain,
   escolha solverone.com.br.
4. Clique no botão que cria ("Add" ou "Create").
5. Quando a chave aparecer na tela, PARE. Não clique em "Copy", não leia o valor, não escreva o valor em nenhuma
   mensagem. Diga só: "A chave está na tela. Copie você mesmo com o botão Copy; ela aparece uma vez só."
Se algum botão tiver outro nome ou a tela for diferente, descreva o que vê e espere a minha resposta. Não faça nada
além disso no Resend (não apague, não edite outras chaves).
```

Depois do prompt 1: o dono clica em **Copy** no Resend (a chave vai para a área de transferência) e abre a aba do Supabase.

## Prompt 2 · Supabase: guardar a chave como segredo da função

```
Você está numa aba do Chrome onde eu já fiz login em supabase.com. Eu já copiei a chave para a área de transferência.
Tarefa: guardar essa chave como segredo das Edge Functions do projeto solverone-app, sem nunca ler a área de
transferência nem o valor da chave.

1. Abra https://supabase.com/dashboard/project/qvdvkqydhnadhewcidia/settings/functions . Se essa página não tiver a
   seção de segredos, vá no menu da esquerda em "Edge Functions" e procure a aba ou o botão "Secrets" / "Manage secrets".
2. Na seção de segredos, clique em "Add new secret" (ou no campo vazio de nova linha).
3. No campo Key (ou Name), digite exatamente: RESEND_API_KEY_LEX
4. No campo Value, NÃO digite nada. Clique no campo para deixá-lo selecionado e me diga: "Cole a chave agora com
   Ctrl+V e me avise quando tiver colado." Então espere.
5. Só depois que eu disser "colei", clique em "Save" (ou "Add secret").
6. Confirme que RESEND_API_KEY_LEX aparece na lista de segredos. Diga só o nome; nunca o valor.
Se a tela pedir para confirmar ou mostrar erro, descreva e espere. Não mexa em outros segredos nem em outras
configurações do projeto.
```

Depois do prompt 2: avisar a Arquitetura "chave colada". A função `lex-conta` passa a enviar os avisos; os que ficaram
como "pendente" em `lex_avisos` não são reenviados (eram só testes ou aconteceram antes da chave).
