# Licença em uso · desenho curto (Arquitetura, 08/Nov/2026)

**Aprovado pelo dono em 08/Nov à noite ("Pode"), com as três respostas: (1) enquanto aguarda aprovação, o programa lê
normalmente (C1); (2) avisos enviados pela função da nuvem com a chave do Resend nos Secrets do Supabase, colada só pelo
dono (D1); (3) e-mail de boas-vindas devolvido só até a primeira pessoa se cadastrar (E).** Estado: SQL em
`nuvem/supabase/2026-11-08b-lex-licenca-em-uso.sql` (o dono revisa e roda, depois do SQL de correção); `lex-conta` v4
escrita em `nuvem/supabase/functions/lex-conta/index.ts`, **publicada só depois de o SQL rodar** (ela usa as colunas novas).

Pedido da Produto (quadro, 08/Nov) com a ideia aprovada pelo dono. **Nada é implementado antes do "pode" dele.**
Vale para o que já está no ar (0.7.10 instalada; KR Law instala quinta 12/Nov): todo campo novo é opcional e nenhum
programa antigo é bloqueado. SQL só em arquivo; o dono roda depois de revisar. Reaproveita o que existe: `lex_contas`,
`lex_usuarios`, `lex_instalacoes`, `lex_eventos`, função `lex-conta`, tela "Licenças do RADAR" do RootifyONE.

## Hoje, em uma frase

Quem tem o código entra calado: qualquer e-mail, qualquer pasta, reinstalar cria outro "computador". Nenhum dado de
processo vaza (a nuvem só devolve nome do escritório, validade e mensagem). O risco é **uso indevido de um código
vazado** e **lista de computadores suja**.

## A. Identificação estável do computador

| Opção | Como | Prós | Contras |
|---|---|---|---|
| **A1 (recomendada)** | O id continua aleatório (16 hex), mas fica guardado em `%LOCALAPPDATA%\LexSuiteONE\instalacao.json` **e** na pasta do programa. Instalador e programa leem antes de gerar; reinstalar na mesma pasta ou em outra reaproveita. | Zero dado do aparelho; reinstalação limpa; simples no `.bat` e no Python | Outro usuário do Windows no mesmo PC vira outro id (aceitável: "computador" = pessoa + PC) |
| A2 | Id derivado do `MachineGuid` do Windows (hash com sal) | Igual para qualquer usuário e reinstalação | Lê o registro do Windows; é identificador do aparelho (pseudonimizado, mas gera pergunta na LGPD); mais código no `.bat` |
| A3 | Guardar em `%ProgramData%\LexSuiteONE\` | Vale para todos os usuários do PC | Pode exigir permissão para gravar; nem sempre existe |

Com A1: programa 0.7.10 já instalado grava o id atual no `%LOCALAPPDATA%` na primeira abertura da versão nova (nada muda
para ele). Na nuvem: `lex_instalacoes.nome_pc` (opcional, `COMPUTERNAME` cortado em 60), visão `lex_computadores` com
`ativo = ultima_vez >= agora − 30 dias`, coluna `esquecida_em` e função `admin_lex_esquecer_instalacao` (marca, nunca
apaga; se o mesmo id voltar a chamar, revive e gera evento). RootifyONE: "inativo" em cinza, botão "Esquecer".

## B. Aviso "este código já está em uso"

A resposta de `verificar` ganha, **só quando a instalação é nova para aquele código**, o bloco
`em_uso: {pessoas: N, computadores: M, desde: "AAAA-MM"}`. Nunca nome nem e-mail de pessoa. A tela (Produto) mostra
no passo 1: "Este código já está em uso no escritório X (N pessoas, M computadores). Confirme que você é deste
escritório." com "Sou deste escritório" / "Não sou". "Não sou" apaga o código e volta ao campo. O instalador não muda.
Risco aceito: quem tem o código já recebe hoje o nome do escritório; contagens não identificam ninguém.

## C. Domínio do e-mail e aprovação

- `lex_contas.dominios text[]` (ex.: `{krlaw.com.br}`): a equipe preenche no RootifyONE ao criar a licença, ou a
  nuvem aprende com o **primeiro** cadastro quando o e-mail é de domínio próprio. Lista fixa de provedores públicos na
  função (`gmail.com`, `outlook.com`, `hotmail.com`, `live.com`, `yahoo.com(.br)`, `icloud.com`, `uol.com.br`,
  `bol.com.br`, `terra.com.br`, `proton.me`…): esses **nunca** viram domínio do escritório.
- `lex_usuarios.aprovacao` (`aprovado` · `aguardando` · `recusado`), `aprovado_por`, `aprovado_em`. Regra no cadastro:
  e-mail do domínio da licença → `aprovado`; primeira pessoa da licença → `aprovado` (é quem recebeu as boas-vindas);
  qualquer outro caso (provedor público, outro domínio) → `aguardando`. `max_pessoas` conta só `aprovado` e ativo.
- **Enquanto aguarda**, duas opções: **C1 (recomendada agora)** o programa lê normalmente e mostra "Seu cadastro está
  aguardando a confirmação da SolverONE" (ninguém fica parado na sexta à noite; a nuvem não entrega nada mesmo);
  **C2** o programa não lê até aprovar (mais duro; vira opção por licença `exigir_aprovacao`, desligada por padrão, para
  quando houver cliente que peça). `recusado` → a tela diz que o e-mail não foi aceito e pede outro; nada mais muda.
- Aprovar/recusar: `admin_lex_aprovar_pessoa(email, decisao)` na ficha do RootifyONE (equipe). Na 0.8, o responsável
  do escritório aprova pelo site (`acesso_site`, desenho da 0.8).

## D. Avisos por e-mail

Quando entra **pessoa nova** ou **computador novo** numa licença: e-mail ao responsável do escritório
(`lex_contas.email_boas_vindas`, item E) e a `judicial@solverone.com.br`. Reinstalação com o mesmo id não avisa.

| Opção | Como | Prós | Contras |
|---|---|---|---|
| **D1 (recomendada)** | `lex-conta` grava em `lex_avisos` (caixa de saída: para quem, assunto, estado, tentativas) e envia pelo Resend na mesma chamada; a chave do Resend fica **só nos Secrets do Supabase**, colada pelo dono (a diretriz já prevê chave de envio em Edge Function) | Imediato; falha fica registrada e visível no RootifyONE; nada no código | Mais uma chave a guardar (no painel, nunca no repositório) |
| D2 | Só a caixa de saída; a Operação envia à mão pelo conector | Nenhuma chave nova | Depende de gente; atrasa |
| D3 | Job do banco enviando | — | Precisa de `pg_net`, que não está instalado |

Texto PT/EN aprovado pelo dono; remetente `SolverONE <nao-responda@solverone.com.br>`, `Reply-To: judicial@`. Para o
responsável: nome e e-mail da pessoa nova (é gente do próprio escritório). Para `judicial@`: escritório e domínio do
e-mail, sem o e-mail (o detalhe está no RootifyONE). Teto: 20 avisos por licença por dia.

## E. E-mail de boas-vindas devolvido ao passo 1 (item 4 do feedback)

`lex_contas.email_boas_vindas` (a equipe preenche ao criar a licença; a Operação confere antes de enviar). A resposta
de `verificar` traz `email_sugerido` **só enquanto a licença não tem nenhuma pessoa aprovada** (a primeira instalação).
Depois disso, nunca mais. Risco: quem tem o código vê esse e-mail; mas quem tem o código recebeu o mesmo e-mail de
boas-vindas, onde os dois estão juntos, então não há vazamento novo. A tela mostra o e-mail preenchido e editável.

## F. Tipo de acesso do cliente (modalidade) e busca por domínio (pedido do dono, 08/Nov)

- `lex_contas.modalidade`: **Instalado** (o programa roda no computador do escritório; é o de hoje, também chamado
  on-premises) ou **Nuvem** (o RADAR roda em servidor da SolverONE e o escritório só acessa; ainda não é vendido, fica no
  cadastro como oportunidade). Todas as licenças de hoje nascem `instalado`. `modalidade_desde` guarda a data da troca.
- Migração: feita na ficha do RootifyONE (`admin_lex_salvar` com `modalidade`); gera evento `licenca_alterada`
  "modalidade: instalado -> nuvem" em `lex_eventos`, com a hora; quem mudou fica em `acesso_log`, como toda ação da equipe.
- Programa instalado numa licença marcada `nuvem`: a resposta da `lex-conta` traz `modalidade`; a tela mostra "Esta
  licença passou para a versão na nuvem; este computador continua lendo até a SolverONE desligar" e **continua lendo**.
  Desligar de verdade continua sendo `ativo = false`. Nada bloqueia sozinho.
- Busca por domínio no RootifyONE: `admin_lex_listar` devolve `dominios` (da licença) e `dominios_pessoas` (domínios
  dos e-mails cadastrados, **sem os e-mails**); a tela filtra por qualquer um dos dois. Busca por escritório, código e
  CNPJ/CPF já existe (Produto, 0.18.14).
- SQL: `nuvem/supabase/2026-11-08c-lex-modalidade.sql` (aplicado pelo conector em 08/Nov à noite). Função: `lex-conta`
  v4 passa a devolver `modalidade`.

## O que muda em cada arquivo e quem faz

| Arquivo | Mudança | Quem |
|---|---|---|
| `nuvem/supabase/2026-11-08b-lex-licenca-em-uso.sql` (novo) | colunas: `lex_contas.dominios`, `email_boas_vindas`, `exigir_aprovacao`; `lex_usuarios.aprovacao/aprovado_por/aprovado_em`; `lex_instalacoes.nome_pc/esquecida_em`; tabela `lex_avisos`; visão `lex_computadores`; tipos novos em `lex_eventos`; `admin_lex_aprovar_pessoa`, `admin_lex_esquecer_instalacao`; `admin_lex_salvar`/`admin_lex_detalhe`/`admin_lex_criar` ampliadas. Tudo opcional, com GRANT, "desfazer" e conferência | Arquitetura (dono roda) |
| `nuvem/supabase/functions/lex-conta/index.ts` → v4 | limites por chamada (revisão de 08/Nov), `em_uso`, `email_sugerido`, regra de aprovação, avisos (D1), respostas genéricas | Arquitetura |
| `robo/lexsuite/conta.py`, `config.py` | id em `%LOCALAPPDATA%\LexSuiteONE\instalacao.json` com cópia na pasta; `nome_pc`; ler `em_uso`, `email_sugerido`, `aprovacao` da resposta | Produto |
| `robo/radar_modelo.html`, `app.py` | passo 1: aviso "código em uso" com confirmação; e-mail preenchido; selo "aguardando confirmação" / "e-mail não aceito" | Produto |
| `instalador/INSTALAR.bat` | ler o id do `%LOCALAPPDATA%` antes de gerar; gravar lá também | Produto |
| `rootify-one/rootify-lex.js` | ficha: pessoas aguardando (Aprovar/Recusar), computadores inativos e Esquecer, domínios, e-mail de boas-vindas, avisos enviados/falhos, modalidade (Instalado/Nuvem) com histórico; lista com busca por domínio | Arquitetura (PR) |
| Texto dos avisos; chave do Resend nos Secrets do Supabase (passo a passo para o dono) | | Operação (texto), dono (chave) |
| `robo/testes/` | id estável, confirmação, aprovação, programa antigo contra resposta nova | Produto |

Ordem: SQL (dono roda) → `lex-conta` v4 → programa e instalador (Produto, versão 0.7.11) → RootifyONE → textos e chave.

## Estado em 08/Nov à noite e o que só o dono faz

Tudo aplicado pela Arquitetura pelo conector: SQL de correção, SQL da licença em uso (inclusive a regra de tipos de
`lex_eventos`, confirmada pelo dono no computador), SQL da modalidade; `lex-conta` v4 publicada e testada; RootifyONE
0.18.15 publicado. Falta um passo que exige login do dono:

1. **Chave do Resend nos Secrets.** resend.com → API Keys → Create API Key → nome `supabase-lex-conta`, permissão
   **Sending access**, domínio `solverone.com.br` → Create → copiar. Supabase → Edge Functions → Secrets → Add new
   secret → Name `RESEND_API_KEY_LEX`, Value = a chave → Save. Até lá os avisos ficam em `lex_avisos` como "pendente".
2. Na ficha da KR Law no RootifyONE (Clientes → Licenças do RADAR): preencher e-mail de boas-vindas e domínio do escritório.

## Plano de teste

1. Reinstalar na mesma pasta e em pasta nova: RootifyONE mostra **um** computador; `lex_eventos` sem "cadastro" repetido.
2. Segundo PC com o mesmo código: aviso com contagens; "Não sou" apaga o código; "Sou" segue.
3. E-mail do domínio → aprovado na hora; Gmail na segunda pessoa → `aguardando`, programa lê (C1), aviso chega ao
   responsável e a `judicial@`; aprovar no RootifyONE → selo some na próxima conferência; recusar → tela pede outro e-mail.
4. Primeira instalação pelo e-mail de boas-vindas: e-mail vem preenchido; depois da primeira pessoa, não vem mais.
5. Programa 0.7.10 (sem as mudanças) contra a função v4: tudo igual a hoje.
6. Limites: 200 chamadas seguidas → `limite`; 26ª instalação numa licença de 20 → recusada (trigger já no SQL de correção).
7. SQL no Postgres local (duas vezes) e `teste/sql-grants.js`; advisor do Supabase depois de o dono aplicar.
