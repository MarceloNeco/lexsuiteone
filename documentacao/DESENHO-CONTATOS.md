# Contatos da empresa processada · desenho curto (Arquitetura, 08/Nov/2026)

Pedido da Produto no quadro (itens 40 e 41 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`), em cima do requisito
"ficha de canais da empresa para o compliance" do `robo/PENDENCIAS.md`. **Aprovado pelo dono em 08/Nov à noite (seção 4).**
Quem implementa tela, planilha e arquivo é a Produto; o que é regra de dado está aqui.

## Em uma frase

Para cada ação nova, o RADAR mostra **todos os canais de contato da empresa e dos seus sócios** que conseguir, cada um com **fonte, data e
confiança**; o que faltar aparece em vermelho "Contato a buscar na área logada", e um botão prepara um arquivo para o
advogado completar pelo PJe com o Claude in Chrome e colar a resposta de volta. **Nada sai do computador do escritório**:
contatos não vão para a SolverONE (a 0.8 já decidiu isso: D2).

## 1. O que pode ser guardado (regra de dado)

| Dado | Pode? | Condição |
|---|---|---|
| Telefones, e-mail, site, endereço completo, LinkedIn e Instagram **da empresa** | sim | sempre com fonte e data |
| Nome e cargo de sócios e administradores | sim (já existe) | do cadastro público da Receita; o ajuste "Mostrar sócios" continua desligando |
| Celular ou e-mail **de um sócio ou administrador** | sim (decisão 4) | fonte obrigatória; marcado como "de pessoa" para o compliance filtrar |
| Qualquer dado de reclamante, testemunha, advogado da outra parte, preposto | **nunca** | o RADAR recusa a linha |
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

1. Botão **"Preparar busca de contatos"** (no máximo 30 processos por dia, ajustável; aviso de que quem abre é o advogado com a credencial dele e de que telefone e e-mail quase nunca estão no processo, decisão do dono de 09/Nov): gera `saida/contatos/buscar-contatos-AAAA-MM-DD.md` com (a) as instruções para
   o Claude in Chrome (só leitura; só dados da empresa ré; nunca pessoa física nem CPF; onde olhar no PJe: petição
   inicial e citação; formato exato da resposta) e (b) a tabela dos processos sem contato: processo, tribunal, vara,
   empresa, CNPJ. A tela mostra o passo a passo: "abra o PJe logado, abra o Claude in Chrome, arraste este arquivo".
2. O advogado roda na aba logada; a resposta volta como tabela Markdown de 8 colunas:
   `| processo | empresa | canal | valor | de_pessoa | fonte | data | observação |`.
3. Botão **"Colar contatos encontrados"**: área de texto; o RADAR lê a tabela e confere linha a linha: processo existe
   na lista; empresa bate (ou avisa); canal é um dos aceitos; valor com formato (telefone com DDD, e-mail com @,
   endereço web com domínio); `de_pessoa = sim` exige fonte preenchida (decisão 4); canal `outros` aceita texto livre curto; linha com CPF ou com canal fora da lista
   é recusada e mostrada com o motivo. O que entra fica com origem "área logada", a data da linha e o nome do
   arquivo; a tela e a planilha atualizam na hora.
4. Histórico local (`lexsuite.db`, tabela `contatos_historico`, e aba Log da planilha): quando (UTC e fuso), quem colou
   (perfil do computador), arquivo gerado, linhas aceitas e recusadas. Nada disso vai para a nuvem.

## 4. Decisões do dono (08/Nov/2026, noite)

| # | Decisão | O que muda no desenho |
|---|---|---|
| 1 | **MEI e empresário individual entram com todos os contatos** (telefone, e-mail, endereço completo, CEP), mesmo quando coincidem com os da pessoa. O advogado tem fé pública e precisa desses dados; a responsabilidade pelo uso é do escritório, que tem compliance para isso. | Some a regra "sem contatos para MEI". A ficha marca o porte (MEI, EI) para o compliance saber; nada é escondido. |
| 2 | **Quem usa o RADAR é advogado com OAB**; hoje todos veem e fazem tudo. **Preparar a arquitetura para níveis de acesso** (ver, operar, administrar; ações em lote só para quem puder), inclusive para um advogado júnior só ler. | A validação de contato grava quem (perfil do computador) e quando. Seção 6 abaixo: níveis de acesso como estrutura pronta, sem tela ainda. |
| 3 | **Independência de IA**: o fluxo com Claude in Chrome pode existir, mas o produto tem de funcionar sem nenhum modelo de linguagem (escritórios que não usam IA). **Busca própria de site e redes sociais entra no roadmap**, sem IA. | Seção 7 abaixo: o que dá para fazer sem IA e sem quebrar regra, e o que não dá. |
| 4 | **Todo contato encontrado entra**, inclusive celular e e-mail de sócio e dados fora dos campos oficiais do processo, sempre com fonte e data; o que não tem campo próprio vai para **"Outros"**. Responsabilidade do advogado, que tem fé pública. | Some a condição "só se publicado como contato comercial". Fica a fonte obrigatória e a marca "de pessoa", para o compliance filtrar se quiser. O que continua fora: dados do **reclamante** e de outras pessoas físicas que não são a parte representada ou seus sócios (regra do produto). |
| 5 | **Planilha do Drive é o espelho detalhado da lista**: pode ter mais colunas que a tela, agrupadas ou escondidas. | Colunas de contato, fonte, data, confiança e validação na aba Radar (grupo recolhível) e a aba Contatos completa. |

Regra de dado atualizada (substitui a tabela da seção 1 onde conflitar): pode guardar **qualquer canal de contato da
empresa processada e dos seus sócios e administradores**, com fonte, data e confiança; **nunca** dados do reclamante,
de testemunhas, de advogados da outra parte ou de prepostos. CPF continua fora de tela e planilha (não é contato).

## 6. Níveis de acesso (estrutura pronta, tela depois)

Hoje: todo mundo que entra no programa faz tudo. Para não ter de refazer depois, a 0.8 já guarda a base:

- `lex_usuarios.nivel` (`administra` · `opera` · `le`), padrão `opera` para quem existe hoje; a equipe muda no RootifyONE.
- Toda ação do programa que muda dado (validar contato, descartar, arquivar, ações em lote, colar contatos) passa por
  **uma função só** (`pode(acao)`), que hoje devolve sempre "sim" e amanhã olha o nível. A tela esconde o botão quando
  `pode` diz não. Ações em lote (arquivar vários, exportar tudo) ficam marcadas como `opera` ou mais.
- Registro de quem fez o quê (já existe para contatos) vale para todas as ações: `lexsuite.db`, tabela `acoes`, com
  perfil, ação, alvo, quando (UTC e fuso). Nada vai para a nuvem além das contagens.
- Na 1.0 (site), o nível vem do banco (`acesso_site` do desenho da 0.8 ganha o mesmo vocabulário).

## 7. Busca de site e redes sociais sem IA (roadmap)

O que dá para fazer com a biblioteca padrão do Python, sem modelo de linguagem, e dentro das regras do produto (sem
contornar login, sem raspagem em massa, respeitando `robots.txt` e um pedido por vez):

| Passo | Como | Confiança |
|---|---|---|
| Site da empresa | pelo domínio do e-mail da Receita (se não for provedor público); conferir que a página responde e cita a razão social ou o CNPJ | alta se cita; média se só responde |
| Telefones, e-mails, endereço no site | ler a página inicial e a de contato do próprio site da empresa (texto, `tel:`, `mailto:`) | média |
| Redes sociais | só os **links que o próprio site da empresa publica** (LinkedIn, Instagram, Facebook, WhatsApp); o RADAR não entra nas redes | alta (é a empresa que aponta) |
| Cadastro público | Receita (já existe) e, quando houver, a página de transparência do e-Social/Junta Comercial pública | alta |

O que **não** entra, e por quê: buscar no Google ou no Bing (os termos de uso proíbem robôs; o resultado muda todo dia e
bloqueia rápido); abrir LinkedIn ou Instagram por conta própria (exigem login e proíbem coleta automática); comprar base
de dados de contatos (dado pessoal sem base legal clara). Se um dia for preciso mais, o caminho é uma API paga e oficial
(ex.: Google Places para telefone e endereço do estabelecimento), com chave da plataforma no servidor, decisão à parte.
O fluxo com Claude in Chrome (seção 3) fica como **opção** para quem quiser, nunca como requisito.

## 8. Quem faz o quê

| Peça | Quem |
|---|---|
| Regra de dado, formato do arquivo e da resposta, validação das linhas (este documento) | Arquitetura |
| Tabelas `contatos`, `contatos_historico` e `acoes` no `lexsuite.db`; função `pode(acao)`; leitor da tabela Markdown; tela; planilha (colunas e aba Contatos); botões; endereço completo e canal "Outros" | Produto (versão 0.7.12 ou seguinte; **aprovado pelo dono em 08/Nov com as 5 decisões**) |
| Busca de site e redes sem IA (seção 7) | Produto, versão seguinte, depois de um desenho curto da Arquitetura com o teste de `robots.txt` |
| Instruções do arquivo para o Claude in Chrome (texto) | Arquitetura escreve, Produto embute |
| Teste: arquivo gerado abre e tem só processos sem contato; resposta com linha de pessoa física é recusada; validação grava quem e quando; planilha preserva a aba Contatos entre leituras | Produto |
