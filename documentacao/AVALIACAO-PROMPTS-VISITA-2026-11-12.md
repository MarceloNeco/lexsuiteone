# Avaliação dos prompts da visita à KR Law (12/Nov/2026, Produto)

Conferido contra `docs/VISITA-KR-LAW.md` (última mudança 10/Nov, 15:48 UTC), o programa atual (0.7.32 publicada,
0.7.33 em revisão) e a documentação oficial da extensão Claude in Chrome, lida hoje. Nada foi alterado ainda.

## 1. Links (conferido hoje)

| O quê | Abre sem login? |
|---|---|
| GitHub: https://github.com/MarceloNeco/lexsuiteone/blob/main/docs/VISITA-KR-LAW.md | **Sim** (repositório público; tem o botão de copiar em cada prompt) |
| Manual: https://judicial.solverone.com.br/manual.html | Sim |
| Instalador: https://judicial.solverone.com.br/downloads/Instalar-LexSuiteONE.zip | Sim |
| Google Docs "PROMPTS DA VISITA… (USE ESTE)" e "ROTEIRO DA VISITA… (USE ESTE)" no seu Drive | **Não**: estão privados, só você abre. O conteúdo é o mesmo do GitHub (10/Nov, tarde) |

Para mandar ao Leandro: use o link do GitHub. Os Google Docs servem só para você ler no celular.

## 2. Qual conta usar no Chrome dele

**Recomendação: a sua conta Claude, num perfil novo do Chrome ("Visita SolverONE")**, sem sair da conta dele.

- Não precisa deslogar o Leandro: o perfil novo é um Chrome separado, e no fim do dia você apaga o perfil.
- As conversas do painel novo da extensão ficam no histórico da conta e abrem no claude.ai, no celular e no
  computador. Com a sua conta, os relatórios já estão com você. Não é preciso compartilhar nem copiar nada.
- O certificado digital do Leandro funciona em qualquer perfil, porque fica no Windows ou no token.
- Teste hoje, antes de ir: entre no claude.ai com a sua conta ("Brasino") e confira se o plano é pago (Pro ou acima),
  porque a extensão exige plano pago. Se não conseguir entrar, use a conta dele (item 3).

## 3. Se for a conta do Leandro

- A documentação não confirma que dá para "Compartilhar" uma conversa da extensão, nem que ela cria arquivo para
  baixar. O caminho seguro é este: no fim, o prompt já entrega o `RELATÓRIO FINAL` num bloco só. Ele seleciona o texto,
  copia e cola num e-mail para `integracao@solverone.com.br` ou num Google Doc. Isso dá uns 2 minutos por relatório.
- Oportunidade a testar hoje em casa (não confirmada na documentação): pedir no fim do prompt que a extensão abra uma
  aba em `docs.new` e cole o relatório lá. O documento cai no Drive da conta Google que está aberta naquele perfil.

## 4. Menos cliques (o que a extensão permite hoje)

- Modos de aprovação na caixa de conversa: "Manually approve", "Automatically approve" (o padrão no painel novo) e
  "Skip all approvals". Nas janelas A e B, escolha **"Skip all approvals"** antes de colar o prompt. Os prompts são só
  de leitura.
- Mesmo assim, ela **sempre pergunta antes de baixar arquivo**. Os prompts 1A, 1B e 4B pedem até 3 downloads. Proposta:
  1 download só, a petição inicial. Fica 1 clique por prompt, e o resto vira só anotação (nome do botão, link, formato).
  Os PDFs ficam no computador do Leandro e não vão para o seu Drive, porque têm dados do reclamante.
- Cuidado: com "Skip all approvals", um site malicioso pode tentar dar ordens à extensão. Use esse modo só nas janelas
  da visita, nos sites do tribunal e do Astrea, e não deixe seu Gmail aberto nesse perfil.
- O login continua sendo do Leandro. A `PAUSA PARA LOGIN` não muda, e isso é a única interação que sobra.

## 5. O que ficou velho no roteiro (mudanças depois de 10/Nov)

1. Diz "programa na versão 0.7.16". Hoje é a 0.7.32, ou a 0.7.33 se sair a tempo.
2. "Configuração → Armazenamento" agora é "Configurações → Armazenamento" (menu ☰).
3. Passo 6 ("anotar as regras que ele quer ajustar"): agora o próprio Leandro ajusta, em Configurações → Critérios da
   lista. Cada área tem os seus critérios, então ele precisa ajustar Trabalhista e Tributário, e também as empresas
   excluídas. Isso vale só para aquele computador, por pessoa.
4. "Clique em Permitir quando ela pedir" (prompts 1A, 1B, 3 e 4B): trocar por "escolha Skip all approvals antes de colar;
   ela só pede confirmação no download".
5. Entrega dos relatórios (passo 7): "Compartilhar e mandar o link" não está confirmado. Trocar pelo item 2 (sua conta)
   ou pelo item 3 (copiar e colar).
6. Estatísticas dos meses anteriores: na 0.7.33 elas leem tudo, com barra de andamento. Na instalação, não comece isso
   durante a visita. Use "Continuar à noite".
7. Prompt 2 (ficha de canais, em casa): avisar que o CNPJ pode ter letras (formato novo, desde julho de 2026).

Os prompts continuam válidos: tribunais, Astrea, regras de leitura e privacidade e o formato `RESPOSTA PARA O RADAR v1`
(que o programa ainda lê em "Área logada → Trazer dados da área logada" e "Buscar na área logada").

## 6. Proposta

Com o seu "pode", a Produto aplica os itens 4 e 5 (e o download único) em `docs/VISITA-KR-LAW.md`, na `main`. É texto
interno, que o cliente não vê. Depois atualiza os dois Google Docs "USE ESTE". Leva uns 20 minutos.
