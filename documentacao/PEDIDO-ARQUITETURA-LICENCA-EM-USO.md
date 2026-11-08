# Pedido à Arquitetura: licença em uso, reinstalação e e-mail de outro domínio (Produto, 08/Nov/2026)

O dono aprovou a ideia em 08/Nov e pediu o desenho à Arquitetura antes de qualquer código. Prompt para colar na
conversa da Arquitetura:

---

Tarefa (Arquitetura): desenhar a "licença em uso" do RADAR JUDICIAL. Não implemente nada antes do "pode" do dono.

Antes: `git pull`, leia `CLAUDE.md`, `docs/QUADRO.md` (anote na sua seção o que vai fazer) e o que já existe:
`nuvem/supabase/functions/lex-conta/index.ts` (conferência do código, cadastro, eventos), `nuvem/supabase/lex-licencas.sql`
e `nuvem/supabase/lex-admin.sql` (tabelas `lex_*` e funções `admin_lex_*`), `robo/lexsuite/conta.py` (programa),
`instalador/INSTALAR.bat` (gera a identificação da instalação e grava `conta-inicial.json`), a tela de licenças do
RootifyONE (`rootify-lex.js`, repositório rootify-one) e `documentacao/FEEDBACK-TESTE-2026-11-08.md` (item 4).

Como é hoje (conferido pela Produto):
1. Reinstalar do zero no mesmo computador gera identificação nova: o RootifyONE passa a mostrar dois computadores; o
   antigo fica parado para sempre.
2. Um código já em uso é aceito em silêncio numa segunda instalação, com qualquer pasta e qualquer e-mail, inclusive de
   outro domínio; um documento (CNPJ/CPF) diferente do primeiro é ignorado sem aviso.
3. Não há vazamento de dados de processo: lista e planilha nunca vão para a nuvem; a nuvem devolve a quem tem o código
   só o nome do escritório, a validade e a mensagem. O risco é uso indevido de um código vazado.

Desenhe (opções, recomendação, riscos):
A. Identificação estável do computador: guardar fora da pasta do programa (ex.: `%LOCALAPPDATA%\LexSuiteONE\`), para
   reinstalar reaproveitar; computador sem uso há 30 dias aparece "inativo"; "esquecer computador" no RootifyONE.
B. Aviso no passo 1 do assistente quando o código já está em uso: "Este código já está em uso no escritório X.
   Confirme que você é deste escritório." A nuvem devolve só contagens (pessoas, computadores), nunca nomes ou e-mails.
C. Domínio do e-mail: a licença guarda o(s) domínio(s) do escritório (do primeiro cadastro ou definido no RootifyONE);
   provedores públicos (Gmail, Outlook etc.) tratados à parte; e-mail fora do domínio entra como "aguardando aprovação"
   (aprovação no RootifyONE). Decidir o que o programa faz enquanto aguarda (mostra aviso e lê ou não lê).
D. Avisos: e-mail ao responsável do escritório e à SolverONE quando entra pessoa ou computador novo (envio pela
   Operação, Resend; remetente e texto aprovados pelo dono).
E. Junto: o item 4 do feedback (e-mail de boas-vindas guardado na licença e devolvido na conferência, para o passo 1
   vir preenchido), que já está pedido no quadro.

Restrições: SQL só em arquivo, anotado no quadro; o dono roda depois de revisar (nenhuma sessão aplica migração).
Nenhum segredo em código ou arquivo. LGPD: o mínimo de dado, nada de e-mail de uma pessoa mostrado a outra. Limite de
chamadas na função. Compatível com o que está no ar: a 0.7.10 já está instalada e a KR Law instala na quinta, 12/Nov;
campos novos opcionais, nada pode bloquear quem já usa. Mudanças na tela e no instalador são da Produto; SQL e função
são seus.

Entrega: desenho curto (até 2 páginas) em `documentacao/DESENHO-LICENCA-EM-USO.md`, com o que muda em cada arquivo,
quem implementa, plano de teste e as perguntas para o dono decidir (em linguagem simples, até 10 linhas na resposta a
ele). Registre no quadro e pare.

---

## Complemento (dono, 08/Nov): tipo de acesso do cliente e busca

Prompt para colar na mesma conversa da Arquitetura (pode entrar no mesmo desenho, como item F):

Acrescente ao desenho da licença em uso o item F, "tipo de acesso do cliente". Cada licença (escritório) passa a ter
uma modalidade: **Instalado** (o programa roda no computador do escritório; é o que existe hoje, chamado também de
"on-premises") ou **Nuvem** (o RADAR roda em servidor da SolverONE e o escritório só acessa; ainda não é vendido, mas
deve existir no cadastro como oportunidade). Desenhe: (1) o campo na licença, com "Instalado" para todas as licenças
de hoje; (2) a migração de uma modalidade para a outra, registrada no histórico (`lex_eventos`) com data e quem mudou,
feita no RootifyONE; (3) o que o programa instalado faz se a licença for marcada "Nuvem" (sugestão: aviso e continua
lendo até a SolverONE desligar); (4) a busca no RootifyONE por domínio do e-mail das pessoas (as funções `admin_lex_*`
passam a devolver os domínios de cada licença, sem os e-mails). A busca por escritório, código e CNPJ/CPF já foi feita
pela Produto no RootifyONE 0.18.14, sem mexer no banco. Mesmas restrições: SQL só em arquivo, o dono roda depois de
revisar; nada pode bloquear quem já usa; a KR Law instala na quinta, 12/Nov.
