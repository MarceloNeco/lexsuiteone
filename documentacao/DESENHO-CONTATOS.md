# Contatos da empresa processada · desenho curto (Arquitetura, 08/Nov/2026)

Pedido da Produto no quadro (itens 40 e 41 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`), em cima do requisito
"ficha de canais da empresa para o compliance" do `robo/PENDENCIAS.md`. **Nada é implementado antes do "pode" do dono.**
Quem implementa tela, planilha e arquivo é a Produto; o que é regra de dado está aqui.

## Em uma frase

Para cada ação nova, o RADAR mostra **todos os canais de contato da empresa** que conseguir, cada um com **fonte, data e
confiança**; o que faltar aparece em vermelho "Contato a buscar na área logada", e um botão prepara um arquivo para o
advogado completar pelo PJe com o Claude in Chrome e colar a resposta de volta. **Nada sai do computador do escritório**:
contatos não vão para a SolverONE (a 0.8 já decidiu isso: D2).

## 1. O que pode ser guardado (regra de dado)

| Dado | Pode? | Condição |
|---|---|---|
| Telefones, e-mail, site, endereço completo, LinkedIn e Instagram **da empresa** | sim | sempre com fonte e data |
| Nome e cargo de sócios e administradores | sim (já existe) | do cadastro público da Receita; o ajuste "Mostrar sócios" continua desligando |
| Celular ou e-mail **de um sócio ou administrador** | só se | a própria empresa o publica como contato comercial (site, petição, cadastro); fonte obrigatória; marcado como "pessoa" |
| Qualquer dado de reclamante, testemunha, advogado, preposto | **nunca** | o RADAR recusa a linha |
| CPF de quem quer que seja | **nunca** | recusa a linha |

Cada contato é uma linha: `processo, empresa, canal (telefone | e-mail | site | endereco | linkedin | instagram | outro),
valor, de_pessoa (sim/não), fonte (Receita | PJe petição inicial | PJe citação | site da empresa | outro), data da consulta,
confiança (alta: canal oficial confirmado por mais uma fonte; média: uma fonte oficial; baixa: só terceiros ou divergente),
origem (robô | área logada | digitado), validação do compliance (vazio | confirmado | descartado, com quem e quando)`.
Retenção: a mesma do resto do banco local (365 dias). Fica em `lexsuite.db`, tabela `contatos`, e na planilha do Drive.

## 2. Na tela e na planilha (item 40)

- Ficha da ação: bloco "Canais de contato" com uma linha por canal (valor, fonte, data, confiança, selo de validação).
  Canal que falta: linha em vermelho **"Contato a buscar na área logada"**. Botão "Validado pelo compliance" por linha
  (confirmar / descartar), que grava quem (perfil do computador) e quando (UTC e fuso).
- Lista: coluna "Contatos" com um resumo (ex.: "☎ ✉ 🌐 · 1 a buscar"), ordenável por "mais faltando".
- Planilha Radar: colunas Telefone, Telefone 2, E-mail, Site, Endereço, cada uma com a célula "(fonte, dd/mm)" ao lado ou
  a fonte numa coluna "Fontes dos contatos"; vazio vira "A BUSCAR". Aba nova **Contatos** (uma linha por canal, com
  validação), editável e preservada entre leituras como as abas Preferências e Exclusões, para o compliance marcar na
  própria planilha quando preferir.
- O que já existe entra sem mudar: telefone 1 e 2, e-mail e sócios da Receita (fonte "Receita", data do cache).
  Endereço completo passa a ser guardado (a consulta já traz). E-mail de outro domínio ganha o aviso "provável contador".

## 3. Completar pela área logada (item 41)

1. Botão **"Preparar busca de contatos"**: gera `saida/contatos/buscar-contatos-AAAA-MM-DD.md` com (a) as instruções para
   o Claude in Chrome (só leitura; só dados da empresa ré; nunca pessoa física nem CPF; onde olhar no PJe: petição
   inicial e citação; formato exato da resposta) e (b) a tabela dos processos sem contato: processo, tribunal, vara,
   empresa, CNPJ. A tela mostra o passo a passo: "abra o PJe logado, abra o Claude in Chrome, arraste este arquivo".
2. O advogado roda na aba logada; a resposta volta como tabela Markdown de 8 colunas:
   `| processo | empresa | canal | valor | de_pessoa | fonte | data | observação |`.
3. Botão **"Colar contatos encontrados"**: área de texto; o RADAR lê a tabela e confere linha a linha: processo existe
   na lista; empresa bate (ou avisa); canal é um dos aceitos; valor com formato (telefone com DDD, e-mail com @,
   endereço web com domínio); `de_pessoa = sim` só entra com fonte preenchida; linha com CPF ou com canal fora da lista
   é recusada e mostrada com o motivo. O que entra fica com origem "área logada", a data da linha e o nome do
   arquivo; a tela e a planilha atualizam na hora.
4. Histórico local (`lexsuite.db`, tabela `contatos_historico`, e aba Log da planilha): quando (UTC e fuso), quem colou
   (perfil do computador), arquivo gerado, linhas aceitas e recusadas. Nada disso vai para a nuvem.

## 4. Perguntas para o dono decidir

1. **MEI e empresário individual**: telefone e e-mail do cadastro costumam ser da própria pessoa. Mostrar a empresa
   **sem os contatos** (recomendo) ou tirar da lista como pessoa física?
2. **Quem valida** no compliance: qualquer pessoa do escritório, com nome e data registrados (recomendo), ou só quem o
   escritório marcar como responsável?
3. **Site, LinkedIn e Instagram da empresa**: só pelo fluxo guiado da área logada e do Claude in Chrome (recomendo) ou o
   RADAR procura sozinho na internet? Procurar sozinho é raspagem em massa, contra a regra do produto.
4. **Celular e e-mail de sócio achados na área logada**: aceitar quando a empresa os publica como contato comercial, com
   fonte (recomendo), ou nunca aceitar dado de pessoa, mesmo com fonte?
5. **Colunas de contato na planilha do Drive**: sim, com fonte e data (recomendo); a planilha fica no Drive do escritório,
   que é o controlador do dado.

## 5. Quem faz o quê

| Peça | Quem |
|---|---|
| Regra de dado, formato do arquivo e da resposta, validação das linhas (este documento) | Arquitetura |
| Tabelas `contatos` e `contatos_historico` no `lexsuite.db`; leitor da tabela Markdown; tela; planilha (colunas e aba Contatos); botões | Produto (versão 0.7.12 ou seguinte, depois do "pode") |
| Instruções do arquivo para o Claude in Chrome (texto) | Arquitetura escreve, Produto embute |
| Teste: arquivo gerado abre e tem só processos sem contato; resposta com linha de pessoa física é recusada; validação grava quem e quando; planilha preserva a aba Contatos entre leituras | Produto |
