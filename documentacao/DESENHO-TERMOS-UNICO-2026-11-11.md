# Desenho: termo único, aceite por pessoa e versão nova com trava (pedido da Produto "Termos e aceite", 11/Nov)

Arquitetura, 11/Nov/2026. Responde aos 4 pontos do dono. **Nada aplicado**: banco, função da nuvem e página só mudam com o
"pode" do dono (itens marcados com ⏳).

## 4. Por que a conta de teste lê o Diário sem aceite (conferido no banco, 11/Nov)
- Não existe **nenhum** aceite registrado (`sol_aceites` vazia), nem da KR Law nem da licença de teste.
- As duas licenças (criadas em 08/Nov) estão com a trava do escritório **desligada** (`exigir_aceite = false`): foi a
  decisão de 09/Nov (página ainda não publicada; depois, "KR Law desligada até depois da visita"). A licença de teste
  entrou na mesma regra. Com a trava desligada, a `lex-conta` responde `ok` e o programa lê.
- A trava **por pessoa** só liga quando o programa declara `suporta_aceite_uso: true` na conferência. A 0.7.28 instalada
  ainda não declara (a Produto deixou para a versão com a caixa de aceite no cadastro). Até lá, ninguém trava por pessoa.
- Conclusão: funciona como desenhado; o que falta é ligar a trava da sua licença de teste (⏳ pede o "pode") e a Produto
  publicar a versão que declara o suporte.

## 1. Página de aceite: campos fixos sem foco, código mascarado
- Pelo link do e-mail, **código e e-mail deixam de ser campos**: viram texto cinza (sem borda de foco, sem cursor, fora
  da ordem do Tab), com o código **mascarado como no Perfil do programa** (`LEX-••••-XXXX`, mesma regra de `mascaraCodigo`).
  O valor real fica guardado na página e vai no envio. Pelo site, sem link, os campos continuam editáveis.
- Nome continua editável (às vezes o cadastro está errado).

## 2. Um texto só; aceite do escritório guardado com o e-mail de quem aceitou; cada pessoa aceita o mesmo texto
- **Termo único**: `lexsuiteone-termos` (as 11 seções da página). O termo `lexsuiteone-uso` deixa de existir como termo à
  parte (⏳ fica inativo no banco, para histórico). O link de leitura passa a ser `aceite.html?ler=1` (mesmo texto).
- **Registro por pessoa**: cada aceite em `sol_aceites` é (licença, e-mail, versão, data/hora com fuso, protocolo).
  - **Escritório aceito** = existe aceite da versão vigente por alguém da licença. O primeiro é o responsável, pelo link
    do e-mail de boas-vindas (ou qualquer pessoa já cadastrada na licença, pelo programa).
  - **Pessoa aceita** = o próprio e-mail tem aceite da versão vigente. Cada pessoa aceita **o mesmo texto** na máquina
    dela, na tela de cadastro do programa (caixa "Li e aceito os termos", com o link `?ler=1`); o programa já manda
    `aceite_uso {versao, fuso}` (nome do campo mantido para a Produto não mexer) e a nuvem grava no termo único.
- **Texto** (⏳ versão 1.2 da página, só a seção 2): "O responsável aceita em nome do escritório; cada pessoa que usa o
  programa aceita estes mesmos termos, com o próprio nome e e-mail, na primeira vez e a cada versão nova."
- **`lex-conta`** (⏳ v14): `termos.escritorio` = situação da licença; `termos.pessoa` = situação do e-mail deste
  computador, **os dois no termo único**; nada muda no formato da resposta. RootifyONE: ficha mostra o aceite de cada
  pessoa e o do escritório a partir do mesmo termo (prompt, item 3b ajustado).

## 3. Versão nova (lei mudou): exigir novo aceite e segurar até cada um aceitar
- Já existe a base (desenho 5d): o dono clica **"Publicar versão"** no RootifyONE (Configuração do produto → Termos),
  com motivo e o interruptor **"Exigir novo aceite"**. Com o termo único, ligado significa:
  1. a licença volta a `aceite_pendente` (o programa não lê) até o **responsável** aceitar a versão nova pelo link;
  2. depois, cada **pessoa** fica em `aceite_uso_pendente` (não lê) até aceitar a nova no cadastro do programa;
  3. o RootifyONE mostra quem está na versão antiga; aceites antigos ficam guardados.
- "Licença pausada" de verdade (Ativar/Pausar) não é necessária: a trava automática segura o uso e solta sozinha a cada
  aceite, sem a equipe ter de lembrar de reativar. Se o dono preferir pausar à mão, o botão Ativar/Pausar já existe.
- Antes de a lei mudar: o LexSuiteONE publica o texto novo na página (versão X), e só então o dono publica a versão X
  no RootifyONE. Enquanto o botão não existe no RootifyONE, a Arquitetura faz o mesmo por SQL, com o "pode".
- Aviso por e-mail aos escritórios ("os termos mudaram, versão X") fica para a `lex-equipe` (ação `aviso_termos`),
  quando houver mais de um cliente.

## O que pede o "pode" do dono
1. Banco: inativar o termo `lexsuiteone-uso` (fica para histórico) e a `lex-conta` v14 (termo único). Sem dado de cliente.
2. Página de aceite 1.2: campos fixos sem foco com código mascarado; seção 2 com o texto acima; versão vigente 1.1 → 1.2
   **sem** exigir novo aceite (ninguém aceitou ainda).
3. **Ligar a trava da sua licença de teste** (`exigir_aceite = true`), para você ver o programa travar e aceitar pelo link.
   A KR Law continua desligada até você mandar.
4. Produto: versão do programa que declara `suporta_aceite_uso: true` e mostra a caixa com o link `?ler=1` (pedido no quadro).

## 5e. Histórico de versões, novo aceite só por mudança material, aceite pela página antes de instalar (12/Nov)

Responde ao pedido da Produto "Aceite dos termos e e-mail de boas-vindas" (12/Nov) e à diretriz do dono (ponto 4 da
definição de pronto). Aplicado em 12/Nov: `nuvem/supabase/2026-11-12-sol-termos-versoes.sql` e `lex-conta` v16.

1. **`{{email}}` vazio no e-mail de teste**: a ficha da licença de teste não tem "e-mail do responsável" preenchido (a da
   KR Law tem). A prévia do RootifyONE preenche `{{email}}` com esse campo; vazio na ficha = vazio no link. Preencher o
   campo na ficha; o RootifyONE deve avisar antes de enviar quando estiver vazio (já pedido no prompt, item 3).
2. **Código visível na primeira vez**: pelo link do e-mail, a página mostra o código inteiro (campo fixo e faixa "em nome
   de…") até confirmar; depois do aceite, mascarado (`LEX-••••-XXXX`). Publicado.
3. **Aceitar pela página e depois instalar**: o aceite é por licença e por e-mail; quem aceita pela página (responsável) e
   depois instala com o mesmo e-mail já entra com `termos.escritorio.aceito` e `termos.pessoa.aceito` verdadeiros. Quem
   instala primeiro recebe o link com o e-mail (da ficha ou da própria pessoa) na mensagem de `aceite_pendente`.
4. **O assistente não pede de novo a quem já aceitou**: a ação `conferir {codigo, email}` (antes do cadastro) devolve
   `termos.escritorio` e `termos.pessoa` para aquele e-mail; `termos.pessoa.precisa_aceitar = false` → sem caixa de aceite;
   `true` → caixa com o link `?ler=1` e envio de `aceite_uso`. `cadastrar` e `verificar` continuam devolvendo `termos`.
5. **Novo aceite só quando os termos mudarem de verdade**: `admin_sol_termo_publicar(…, p_reaceite)`: `p_reaceite = true`
   significa **mudança material** (finalidade, dados, compartilhamento, retenção, controlador, obrigações); só então a licença
   e cada pessoa precisam aceitar de novo. `false` = mudança editorial: versão nova registrada, ninguém é perguntado
   (`sol_aceite_situacao.precisa_aceitar` só fica verdadeiro sem aceite algum ou com versão material mais nova). Versão
   nova do programa nunca mexe nos termos.
6. **Histórico**: `sol_termos_versoes` guarda cada versão (texto por link, hash, material, motivo, quem publicou), imutável;
   `sol_aceites` guarda cada aceite. O texto de cada versão fica numa cópia estática do site
   (`judicial.solverone.com.br/termos/v1.0.html`, feita pelo LexSuiteONE a cada versão). A `lex-conta` devolve
   `termos.versoes` na `verificar` para a Configuração mostrar a versão aceita e as anteriores com link; o RootifyONE lê
   `sol_termos_versoes_lista(termo)`. Retenção: contrato + 5 anos (pesquisa da Produto); nada se apaga por rotina. Base
   legal (contrato × consentimento) e prazo: validar com o Leandro, como a Produto recomendou.
