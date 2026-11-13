# Pendências do robô LexSuiteONE (07/Nov/2026, depois da v0.7.0)

Lista viva. Quem continuar (qualquer modelo ou pessoa) lê este arquivo e o `ARQUITETURA.md` antes de mexer.

## Decisões do dono em 07/Nov (tarde)

- Endereço do produto: `judicial.solverone.com.br` (decisão final: mais fácil de falar e de lembrar). Marca: **LexSuiteONE**
  é a suíte jurídica da SolverONE; **JUDICIAL** é este produto, escrito em maiúsculas com o "IA" em latão; as frentes
  (Radar Trabalhista, Tributário, Cível e empresarial) vivem dentro dele. `lexsuiteone.solverone.com.br` não é usado.
- Frentes, nesta ordem: trabalhista (existe), tributário, depois cível e empresarial. Leandro: trabalhista e tributário.
- Cópia HTML estática no Drive: fica, como reserva. O caminho principal é o sistema (tela local hoje; site na 0.8).
- 0.8 confirmada: o robô envia a lista do dia para a nuvem da SolverONE (Supabase) e o site em judicial.solverone.com.br
  mostra, com login por link no e-mail e código de cliente. O Drive continua com a planilha editável.
- Zero impacto na KR Law quando o repositório mudar de dono: tudo que o cliente vê aponta para
  `judicial.solverone.com.br` (site, download, manual, atualização assinada), nunca para a conta do GitHub. Na
  transferência para a organização: mover o repositório, religar o Pages com o mesmo domínio, trocar o alvo do CNAME
  `judicial` para `solverone.github.io` (no Cloudflare, pelo conector), atualizar links do README. O GitHub redireciona
  os endereços antigos. A chave pública de assinatura não muda.
- E-mail: **feito em 08/Nov**. Recebimento no Cloudflare Email Routing, com Email Worker que responde automaticamente
  em `integracao@` e encaminha `contato@` e os demais apelidos. Texto da resposta, por decisão do
  dono: **"Este endereço é usado por sistemas da SolverONE e não é lido por pessoas. Esta mensagem não será
  respondida."** Sem indicar outro e-mail por enquanto; quando houver processo de atendimento, passa a indicar
  `contato@`. Mais tarde, triagem em `contato@` (problema, contato comum, comercial).
- Cara profissional em tudo que o cliente vê: nenhum contato pessoal do dono (e-mail, usuário pessoal do GitHub) em site,
  e-mail, repositório ou planilha. Organização `solverone` no GitHub e endereços: `judicial@` para dúvidas de qualquer produto da suíte LexSuiteONE (e `moneytrio@` etc. para as outras suítes;
  `contato@` é o genérico da SolverONE; no futuro, triagem por programa), `integracao@` só para sistemas (Drive;
  vira Conta Google; não é monitorado e deve responder automaticamente que não é caixa de atendimento).
- Envio de e-mail pelo Resend (anotado em 08/Nov): a mesma conta e o mesmo domínio `solverone.com.br` enviam o LexSuiteONE
  e o Vagas Nutri (outro projeto do dono, para outra pessoa). Decisão do dono: **mais tarde, separar o envio por
  subdomínio** (um por produto, cada um verificado no Resend), para que devolução ou reclamação de um projeto não afete a
  reputação do outro. Nada a fazer agora.

## Requisito novo (08/Nov): ficha de canais da empresa para o compliance

Apontado pelo Leandro como o diferencial do produto: para cada ação nova, **levantar e confirmar os canais de contato da
empresa processada**, para o time de compliance do escritório analisar e decidir se e como agir. **Nada é enviado a
ninguém** pelo JUDICIAL. Ainda não implementado; o desenho sai depois da visita de 12/Nov (prompts em `docs/VISITA-KR-LAW.md`)
e passa pela regra zero antes de virar código.

- Pode: dados da empresa (telefone geral, e-mail comercial, site, LinkedIn e Instagram da empresa, endereço, nomes e
  cargos públicos de sócios e administradores), sempre com fonte. Celular e e-mail de uma pessoa só se a própria
  empresa os publica como contato comercial. Nunca: dados do reclamante e de outras pessoas físicas.
- Formato: uma ficha por empresa, uma linha por canal, com **fonte, data da consulta e grau de confiança** (alta: canal
  oficial da empresa confirmado por mais uma fonte; média: uma fonte oficial; baixa: só terceiros ou divergente).

O que o robô já traz hoje (conferido no código da 0.7.5, `lexsuite/cnpj.py` e `lexsuite/radar.py`):

- Do cadastro público da Receita (BrasilAPI, com Minha Receita de reserva; cache de 30 dias): telefone 1 e telefone 2,
  e-mail, cidade/UF e até 8 sócios e administradores com nome e qualificação. Aparece na ficha da tela; na planilha
  Radar do Drive e no `radar.csv` vão telefone, e-mail e nomes dos sócios. O ajuste "Mostrar sócios e administradores"
  desliga os nomes.
- Só quando o Diário traz o CNPJ, o que acontece em cerca de 1% dos casos. Sem CNPJ, a ficha fica vazia.

O que falta para a ficha de canais:

1. Achar o CNPJ pelo nome da empresa (já pendente na v0.6.1): é o que destrava todo o resto.
2. Endereço completo da sede: o robô guarda só cidade/UF, embora a mesma consulta à Receita devolva logradouro,
   número, bairro e CEP.
3. Telefone 2 e a qualificação dos sócios não vão para a planilha nem para o CSV (só para a tela).
4. Fonte, data da consulta e grau de confiança por dado: a data existe no cache (`consultado_em`), mas não aparece.
5. Sinalizar "provável contato do contador" quando o e-mail da Receita for de outro domínio (comum no cadastro).
6. Contatos da ré na petição inicial e na citação do PJe: dependem do relatório do Prompt 1 (onde aparecem, se dá para
   extrair de forma repetível) e do login do advogado.
7. Site, LinkedIn, Instagram e ficha no Google: o robô não procura hoje. Decidir se fica como levantamento guiado pela
   pessoa (como o Prompt 2) ou se entra em versão futura, sempre sem raspagem em massa e sem contornar login.
8. Entrega no Astrea como contato pessoa jurídica (depende do relatório do Prompt 3).
9. **Pergunta ao dono:** empresário individual e MEI entram hoje como empresa (`classificar.py` reconhece "ME" e "MEI"),
   mas o telefone e o e-mail do cadastro deles costumam ser da própria pessoa. Tratar como pessoa física (fora da
   lista) ou mostrar sem os contatos?

## Site e nome (feedback do dono, 08/Nov)

- Nome por enquanto: **RADAR JUDICIAL**, sempre em maiúsculas (o "IA" segue em latão), sob a marca LexSuiteONE.
  Aplicado na página inicial do site e no e-mail de boas-vindas. Manual, página 404, tela do robô e pacote continuam
  "JUDICIAL" (só o Leandro vê o nome antigo na tela).
- No que o cliente lê, o programa é "o RADAR", não "o robô". Pastas e arquivos internos (`robo/`) não mudam.
- Ícone do site: martelo dourado sobre azul-marinho (balança como alternativa). Um ícone só, fixo: trocar a cada carga
  confunde quem procura a aba e o navegador guarda o ícone em cache.
- Onde roda: o site e o e-mail dizem que o RADAR lê nos horários escolhidos (padrão 20h e 8h), e o site oferece "Na
  nuvem, sob consulta" (judicial@). A versão na nuvem ainda não existe: é a 1.0 (coletor central), mais abaixo.
- OneDrive: "sob consulta" no site. A tela já aceita a pasta do OneDrive para a planilha, mas o compartilhamento com o
  suporte nunca foi testado lá (pediria uma conta Microsoft para `integracao@`).
- ~~Horário das rodadas ajustável pela tela~~: feito na 0.7.9 (dono, 08/Nov).
- Imagem de fundo da capa: o dono vai gerar no Higgsfield; a página já aceita uma imagem por trás do radar.

### 0.7.7 (08/Nov, para antes da instalação de 12/Nov): licença, cadastro e tela nova

- **Licença por código de cliente** (`lexsuite/conta.py`): o código `LEX-XXXX-XXXX` vem no e-mail de boas-vindas e é
  pedido no primeiro passo; é conferido com a SolverONE ao abrir e antes de cada leitura (função `lex-conta` do
  Supabase, `nuvem/supabase/functions/lex-conta`; nenhuma chave no programa). Desativar ou vencer: na tabela
  `lex_contas` (Table Editor do Supabase; depois, tela no RootifyONE). Sem resposta da SolverONE, segue até 15 dias.
- **Cadastro de quem usa**: nome, e-mail (chave: um e-mail, um escritório) e função, e o CNPJ do escritório, nas
  tabelas `lex_usuarios` e `lex_instalacoes` (cada computador). Sem limite de pessoas; a SolverONE vê quantas são.
- **SQL para o dono revisar e rodar**: `nuvem/supabase/lex-licencas.sql`. Criar a licença: `select public.lex_criar_conta('KR Law');`.
- **Tela com a identidade do site**: cabeçalho azul, ícone e nome de `marca.json` (que agora vai no pacote), fonte
  embutida, fundo branco; boas-vindas formais e só até concluir; "Abrir a planilha"; "Baixar a lista (.csv)"; só os
  24 TRTs (TJs e TRFs voltam com as frentes deles).
- A "mira" do escritório (passo 1 do site, decisão do dono 08/Nov): em poucos cliques, frente, tribunais, valor mínimo e
  exclusões (existem); faltam **filtro por porte** (a Receita traz microempresa, pequena, média ou grande) e ~~horário
  ajustável das leituras~~ (feito na 0.7.9).
- **Mac (decisão do dono, 08/Nov):** o site trata Mac como "sob consulta" (requisito e mensagem com contato em
  judicial@), sem recusar o público. Para atender de verdade: o programa já é só Python padrão; faltam o instalador
  `.command` (ou `.pkg`), o agendamento pelo launchd no lugar do Agendador do Windows e a detecção da pasta do Google
  Drive no Mac. Alternativa: a versão na nuvem (1.0), que dispensa instalação.
- Falta depois: confirmação do e-mail por código (Resend); tela de licenças no RootifyONE; termos de uso e aviso de
  privacidade do cadastro; trocar a licença MIT antes de vender em escala (decisão do dono).

### Feito na 0.7.6 (08/Nov): contato do suporte e instalador de um arquivo

- Suporte é sempre `judicial@solverone.com.br`: manual, aba Sobre e linha "suporte" da aba Controle (planilha antiga com
  `integracao@` passa a `judicial@` sozinha). `integracao@` é só a conta de sistemas que recebe acesso à pasta do Drive.
- Instalador de um arquivo: `instalador/INSTALAR.bat`, servido em `docs/downloads/Instalar-LexSuiteONE.zip` (botão do
  site). Baixa o pacote, confere o SHA-256 publicado, instala sem administrador, cria o atalho com o nome de
  `marca.json` e abre a tela. Rodar de novo atualiza. O pacote completo continua no site como plano B.
- Manual único: `paginas/manual.html` gera o do site e o do pacote.
- **Falta testar no Windows** (não há Windows na sessão de produto): o dono roda o instalador no computador dele antes
  de 12/Nov. Limite conhecido: o Windows pode pedir confirmação para `.bat` baixado; tirar de vez pede instalador `.exe`
  assinado com certificado de código (pago).

### Manual em inglês

O manual do site (`paginas/manual.html`) está só em português. Traduzir junto com a próxima mudança de conteúdo.

### Nome do produto como configuração (decisão do dono, 08/Nov)

O nome é uma configuração, não texto fixo: o dono decide (com maiúsculas e minúsculas exatas: "RADAR JUDICIAL" hoje,
"Lex One" amanhã) e a troca vale em todo lugar. Hoje se troca editando um arquivo; no futuro, num ajuste do RootifyONE.

- **Feito (site e e-mail):** `docs/marca.json` guarda `nome`, `curto` (como o texto chama o programa) e `destaque`
  (trecho em latão). Páginas em `paginas/` com marcações; `python ferramentas/marca.py` gera `docs/`; a automação do
  GitHub recusa `docs/` desatualizado. O `preencher.py` do e-mail lê o mesmo arquivo e mostra o assunto.
- **Feito no pacote (0.7.7 a 0.7.9):** o `marca.json` vai no pacote; a tela, o manual (gerado de `paginas/manual.html`),
  o atalho do instalador e o aviso do Windows ao fim da leitura leem dele; o manual já diz "o RADAR".
- **Falta (versão nova):** a planilha (aba Sobre, `compartilhar.py`) e o e-mail de aviso (`avisar.py`) ainda dizem
  "LexSuiteONE · JUDICIAL"; e a atualização ainda não traz o `marca.json` do site dentro do manifesto assinado (hoje o
  nome só muda nas instalações com uma versão nova).
- **Não mudam sozinhos:** nomes de arquivos e pastas (`LexSuiteONE-RADAR.zip`, `C:\LexSuiteONE`, `LexSuiteONE.xlsx`),
  porque trocar quebraria instalações. Se um dia for preciso, é uma migração à parte.
- **Futuro:** ajuste "Nome do produto" no RootifyONE que grava o mesmo `marca.json` (pelo GitHub), sem editar arquivo.

## Esperando o dono (Marcelo)

- Rodar `DIAGNOSTICO.bat` no computador no Brasil e mandar `diagnostico\radar-diagnostico.txt` (arrastar para o Drive).
  Sem ele a regra de "ação nova" fica frouxa: 6.816 ações num dia em TRT2+TRT15, esperado 1.500 a 2.000.
- Testar a v0.6.0: `INSTALAR-PYTHON.bat`, `ABRIR.bat`, escolher tribunais, "Salvar e atualizar agora", print da tela e da ficha.
- Rodar `teste-djen-supabase.sql` no SQL Editor do projeto solverone-app e mandar o resultado (decide se o coletor
  central pode viver no Supabase ou precisa de um servidor pequeno em São Paulo).
- Decidir o repositório público no GitHub (núcleo aberto, MIT ou Apache 2.0). Nada é criado sem esse sim.
- Criar a Conta Google `integracao@solverone.com.br` (sem Gmail; o apelido já existe no ImprovMX), para o cliente compartilhar o Drive.

## v0.6.1 (correções)

- Regra estrita de "ação nova" calibrada com o diagnóstico (pistas em `lexsuite/diagnostico.py`, `ESTRITA`).
- Achar o CNPJ pelo nome da empresa (o Diário traz CNPJ em ~1% dos casos): base pública da Receita no portal novo
  (SERPRO); índice compacto por UF para o robô local; tabela completa no SaaS.
- Ao apertar a regra, orientar: apagar `lexsuite.db` e rodar uma vez limpa.

## Feito na v0.7.0

- Tela com Configuração (escritório, pasta compartilhada detectada), 59 tribunais por ramo/região/estado, 24 TRTs por padrão.
- Planilha de controle (Preferências, Exclusões, Controle oculto) e planilha Radar (Log, Saúde, Sobre ocultas) na pasta do Drive.
- Atualização assinada (Ed25519 + SHA-256) pela pasta compartilhada ou endereço fixo; `ferramentas/publicar.py`.
- `AGENDAR.bat`, saúde sem IA, log de rodadas, `SEGURANCA.md`, `MANUTENCAO.md`, `ROTEIRO-INSTALACAO.md`.

## 0.7.42 (13/Nov, CNJ com o caderno fora; feita pela Operação com o "pode" do dono: "Já faça")

- Dia sem Diário por erro do CNJ: pula, volta até 10 dias úteis, anota o dia e lê sozinho quando o CNJ voltar.
- Fica para a Arquitetura: caminho alternativo pela consulta (`/api/v1/comunicacao`) quando o caderno cair; atenção ao
  limite de 10 mil resultados por consulta (um dia do TRT9 já chega nele): precisa dividir a consulta (por vara).

## 0.7.41 (13/Nov, correção urgente na instalação da KR Law; feita pela Operação com o "pode" do dono)

- O CNJ respondeu 500 ("Server Error") para o caderno do dia de hoje e a leitura inteira parava em todos os tribunais.
  `monitor.coletar_caderno` agora pula o dia de hoje nesse caso e lê até o dia anterior; 5xx em dia anterior continua falha.
- Continuam para a Produto (próxima versão): Empresas excluídas (CPF e sufixos), site com dois "pacote completo",
  instalador que tenta outra pasta quando o antivírus barra, leitura automática barrada pelo Bitdefender (`schtasks`).

## 0.7.40 (teste do dono na 0.7.39, 13/Nov; dono: "junte TODOS numa 0.7.40, sem deixar nenhum para trás") — pronta para revisão

- Feitos: itens 1 a 10 do pedido (lentidão e "Carregando", aspas, Empresas 5/10/15 e "Ver na lista", conferência de todos os
  "Ver na lista" em `testes/tela/ver_na_lista.js`, busca com a empresa procurada, Tipo de publicação, balões, etiqueta,
  mira, faixa da leitura, ressalvas da 0.7.39, imagens de fundo) e o interruptor "Último mês" (decisão do dono, 13/Nov).
- Fora, com o motivo: lista de varas mais larga (o dono ainda não decidiu); assinatura digital do instalador (preços
  levantados em 13/Nov; decisão do dono e da Arquitetura); envio de falso positivo ao Bitdefender (sugestão).
- Integração para RootifyONE, ArchONE e EaglePlanONE: nenhuma nova nem removida.

## 0.7.39 (teste do dono na 0.7.38, 13/Nov; "faça a 0.7.39 com tudo, antes da minha visita ao Leandro") — pronta para revisão

- Feitos: tracejado do período em andamento; título Estatísticas com (?); "Limpar filtros" coerente com as pizzas; "Ver na
  lista" em Faixas e Empresas; 5/10/15 empresas; excluídas (defeito do motivo longo, "Remover", colunas, ▸, ✎); faixa da
  leitura mais baixa.
- Onde "Ver na lista" não leva tudo: Faixas só leva "Acima de…" (o que ficou ligado é "daqui para cima") ou "Sem valor",
  porque a Lista não filtra "até" nem faixa no meio; Empresas só leva quando sobra uma empresa (pela busca); "Como o processo
  novo foi reconhecido" não tem "Ver na lista" (a Lista não filtra por sinal).
- Fica de fora: imagens de fundo (faltam os 4 arquivos); lista de varas mais larga (o dono ainda não decidiu).
- Integração para RootifyONE, ArchONE e EaglePlanONE: nenhuma nova nem removida.

## 0.7.38 (13/Nov) — pronta para revisão

- Pergunta 19 respondida pelo dono: "não couberam" em dourado. Ressalvas da revisão da 0.7.37: "✓ Acrescentada" sumia ao
  sair do campo (corrigido); o filtro de setor com um setor só não aparece (comportamento mantido: não há o que escolher;
  roteiro da 0.7.37 e manual explicam).
- Integração para RootifyONE, ArchONE e EaglePlanONE: nenhuma nova nem removida.

## 0.7.37 (teste do dono na 0.7.36, 13/Nov; dono: "pronto, o resto tá bom, pode corrigir isso?") — pronta para revisão

- Itens 1 a 5 de `documentacao/FEEDBACK-TESTE-0.7.36.md` (Painel com os filtros dos gráficos sempre à vista, Configurações sem
  o parágrafo de abertura e mais larga, busca das excluídas sem rótulo repetido).
- Ressalvas da publicação da 0.7.36 (1) e (2) e da terceira revisão (1) a (7) e (10). Ficam de fora, com o motivo: (8)
  contraste de botão desabilitado (estado desabilitado, isento no WCAG; sem mudança desde a 0.7.35); (9) cor dos avisos de
  perda parcial (pergunta ao dono no quadro, sem urgência); (11) documento interno; (12) o teste do Python 3.11 pula onde
  não há `python3.11` (de propósito); (13) testes novos em `test_v0737.py` para as mutações que sobreviveram nos pontos
  desta versão.
- Integração para RootifyONE, ArchONE e EaglePlanONE: nenhuma nova nem removida.

## 0.7.36 (teste do dono na 0.7.35, 12/Nov; dono: "pode codificar todas as correções e melhorias sem esquecer nada") — pronta para revisão

- Feito: os 34 itens de `documentacao/FEEDBACK-TESTE-0.7.35.md` (menos o 7, depois da visita), os itens 1 a 4b da lista da
  0.7.36 (`documentacao/LISTA-TESTE-DO-DONO-2026-11-12.md`) e as ressalvas (1) a (6) da segunda revisão da 0.7.35.
  Decisões usadas: A "Processos", B "Destaques e exclusões", C "Rotina de leitura"; cores da atualização (verde, azul,
  vermelho só para erro); rodapé sem "hoje"; pergunta D pela recomendação (nome sem CNPJ aceito, com aviso).
- Conferido (5 pontos): manual (Configurações, Licença e termos, Pasta das planilhas, Empresas excluídas, Painel, lupa,
  Leituras automáticas, Quando algo não funciona), Novidades PT/EN da 0.7.36, AssistONE (ajuda de Configurações, Painel e
  Histórico, tour sem a aba Histórico, busca com Histórico de leituras e Sair), termos sem mudança (a consulta do nome pelo
  CNPJ usa o mesmo cadastro público da ficha), e-mails sem menção ao que mudou.
- Revisões da Operação (12 e 13/Nov): as duas rodadas de bloqueios e médias corrigidas dentro da 0.7.36 (nada adiado), inclusive
  site e e-mail de boas-vindas com os nomes novos (com o "pode" do dono).
- Fica para depois: pasta antiga "Cópias" para dentro de "Cópias da planilha"; link para a Lista ao lado de cada valor dos
  gráficos (hoje há "Ver na lista →" por gráfico); o site ainda diz "ações novas" na descrição (texto público: só com o
  "pode" do dono); jornada do aceite por pessoa (Arquitetura).

## 0.7.35 (teste do dono na 0.7.33, 12/Nov; dono: "vamos corrigir tudo que a gente puder") — publicada em 12/Nov

- Feito: tela de abertura; "Conferir agora"; "Trocar licença" com o mesmo código confere; "Abrir a pasta no Windows" e
  título único na Pasta das planilhas; "Continuar à noite" com a busca parada; faixa da leitura compacta; Novidades largas e
  botões das janelas sempre à vista; mensagem ao encerrar; e-mail de boas-vindas (aceite em uma frase, "não recebe
  respostas" em linha própria). Termos continuam na versão 1.0 (decisão do dono, 12/Nov).
- Conferido (5 pontos): manual (Configurações, Licença e termos, Pasta, Sazonalidade), Novidades PT/EN, AssistONE (busca e
  ajuda de Configurações citam os blocos, sem mudança de caminho), termos sem mudança, e-mail revisado.
- Fica para depois da visita: janelas largas no RootifyONE; cabeçalho fixo com o ☰; lentidão com muitos processos (medir);
  pasta antiga "Cópias" para dentro de "Cópias da planilha"; termos dentro do programa (Arquitetura); canal de teste
  (Arquitetura); link para a Lista ao lado de cada valor dos gráficos (confirmar com o dono).

## 0.7.34 (teste do dono na 0.7.33, 12/Nov) — correção urgente antes da visita

- Defeito: depois do aceite dos termos na página, o programa continuava travado em "Falta aceitar os termos" (guardava a
  última resposta da nuvem e "Ler o Diário agora" só mostrava o aviso; só a leitura automática conferia de novo). Corrigido:
  `POST /conta/conferir` e a tela confere ao voltar para a janela, vigia por 10 min depois de abrir a página, confere antes
  de ler e tem "Já aceitei". "database is locked" (estatísticas e tela ao mesmo tempo): `timeout=30` no SQLite.
- Conferido (5 pontos): manual (Termos e aceite), Novidades 0.7.34 (PT e EN), AssistONE sem texto sobre isso (nada a
  mudar), termos sem mudança (fluxo, não dados), e-mail de boas-vindas continua certo ("aceitar agora ou depois de instalar").
- Fica para depois (lista no quadro): botão "Conferir de novo" em Licença e termos, mensagem certa quando a janela é fechada
  pelo DIAGNOSTICO, "Trocar licença" com o mesmo código.

## 0.7.33 (teste do dono na 0.7.31, 12/Nov; desenho da Arquitetura de 12/Nov) — pronta para publicar

Pacote: **46 arquivos no download completo e 45 na atualização** (novo `lexsuite/documento.py`).

- **CNPJ alfanumérico** (IN RFB 2.229/2024): `documento.py` (limpar, válido com ASCII − 48, formatar, extrair com DV e máscara ou
  contexto, CPF); extração nos Diários, exclusões, tela (máscara com letras) e consulta com as letras; 400/404 das duas fontes
  para CNPJ com letras = `fonte_sem_suporte` por 7 dias, ficha com "CNPJ novo (dados da Receita indisponíveis)".
- **Critérios da lista por pessoa, neste computador, por área** (decisão do dono, 12/Nov): `criterios.json` ao lado do
  `config.json` (gravação atômica, `.anterior`), migração única das abas Preferências e Exclusões, sem soma entre frentes;
  planilha compartilhada **completa** (90 dias e 60 mil linhas fixos), sem as duas abas, com a aba só de leitura "Critérios
  desta leitura". Tela: seletor de área, (?) "Estes critérios são seus, neste computador", "Copiar estes critérios para as
  outras áreas", valor vazio ou 0 = sem mínimo (rótulo "Destacar ações a partir de"), números com ponto e centavos,
  excluídas recolhidas com contagem e rolagem, CPF e CNPJ conferidos e formatados, **um Salvar só** na janela.
  "Dias na aba Arquivo" e "Limite de linhas" saíram da tela.
- **Chamados pelo AssistONE** (implementado e **escondido** na 0.7.33, decisão do dono): "Abrir um chamado" no balão e no menu Ajuda; assunto (7 categorias), mensagem, "Podem me
  responder por e-mail", prévia do que vai junto com "não enviar"; trilha só com ids; `POST /chamado` → `lex-conta` v17;
  sem internet, fila em `saida/chamados-pendentes.json` com o mesmo `cliente_id`; "Meus chamados" (`saida/chamados.json`).
  Anexo fica para a 0.7.34.
- **Painel**: sem a busca e sem os filtros que já estão nos gráficos (aparecem no alto só quando ligados, com ×); etiqueta
  grande ao passar o mouse. Lista e Arquivo: busca com dica em itálico "Procure por empresa, nº ou CNPJ".
- **Sazonalidade** (muda a decisão 10): "Buscar estatísticas" lê a fila inteira em lotes, com a pausa; barra com % e
  andamento por mês; Pausar; Continuar à noite (a leitura da noite termina a fila); "Ler o Diário agora" durante a busca
  pergunta (ver no Painel ou pausar e ler); (?) reescrito.
- **Menu**: Configurações com os mesmos nomes e a ordem da janela; grupo Ajuda (Novidades, Manual, Abrir um chamado, Abrir
  numa aba); janela "Configurações"; "Pasta das planilhas"; "Sobre este computador"; Novidades: "menu ☰ → Ajuda".
- Definition of done: manual (critérios, excluídas, planilha, Painel, sazonalidade, chamados, CNPJ, privacidade), AssistONE
  (ajuda de Configurações e Painel, tour, dica, busca: critérios, excluir empresa, chamado, CNPJ com letras), Novidades da
  0.7.33, termos sem mudança (o chamado manda só o que a pessoa vê e deixa marcado), e-mail e site com "Configurações" e
  "seus critérios, por área".
- Pedido à Arquitetura: `CLAUDE.md` com 46/45 arquivos e a linha "Para rever: menu ☰ → Ajuda → Novidades da versão".
- **Revisões A e B da Operação (12/Nov), atendidas**: migração com cópia "antes da 0.7.33" (recusa regravar se falhar),
  segundo computador migra da cópia (escolha (ii)), migração adiada com a pasta fora do ar ou planilha ilegível, registro em
  Saúde; decisão do dono: valores da trabalhista e soma das Exclusões em **todas as áreas**; `criterios.json` ilegível usa o
  `.anterior` (que só é renovado com arquivo bom) e não grava por cima; esconder excluídas e jurídico próprio por área;
  estatísticas da noite depois de terminar e avisar, com parada às 7h ou após 3 h; `criterios.json*` no `.gitignore` e no
  `PREPARAR-PARA-CLIENTE.bat`; **chamado implementado e escondido** (`app.CHAMADO_LIGADO = False`; nada do que a pessoa lê
  promete chamado; itens 1, 2, 9 e 13 das revisões ficam para quando ligar); textos sem as abas antigas (SEGURANCA,
  ROTEIRO, assistente, manual, Como usar); Painel redesenha o filtro ligado na hora; sazonalidade retoma a barra ao voltar ao
  Painel; Novidades uma linha por mudança (abas, termos renomeados, todas as áreas, 90 dias e 60 mil fixos); lupa e busca do
  AssistONE com os termos novos em PT e EN; trocar de área com mudança não salva pergunta; "Tirar" legível no escuro;
  "Configurações" nos caminhos; números (1234.56, 1,5, abc) lidos certo; aba "Critérios desta leitura" em PT e EN.
  Ficam para depois (baixa): topo da janela sem citar os critérios, "acima de R$ 0" no cabeçalho sem mínimo, anel de foco,
  Esc com o (?) aberto, dica do AssistONE em PT com tela em EN, etiqueta do gráfico por teclado, manual só em PT.

## 0.7.32 (dono, 11/Nov: "pode tudo") — pronta para publicar

Segunda revisão da Operação (12/Nov, `8e95fce`): 3 bloqueios corrigidos. (1) "Sem estado/setor/porte (sem CNPJ)" usa a
mesma chave da lista (`__nao__`) e se liga e desliga como os outros (antes, desligar outro item tirava as ações sem CNPJ
do total); `larguras.js` com 1 em cada 5 sem estado. (2) A lupa acha dias da semana, trocar licença, gráficos,
aparência e novidades, em PT e EN. (3) "Critérios da lista" em todo lugar (planilha, manual por função, mensagens do
servidor, `rg_mudou`, LEIA-ME, e-mail); manual: Configuração pelo menu em janela, Perfil só pelas iniciais, Aparência
nos dois lugares. Também: recusa do "Trocar licença" só em memória (nada gravado); Novidades e manual dizem que quem
já usava continua como estava; site, roteiro de instalação e ARQUITETURA com os dias; testes (mesmo código sem
internet, aceite e termos do antigo não passam ao novo, recusa não grava, XML de sábado e domingo); `servidor_aviso.py`
com a data de hoje; `lic_trocar_p` e "Digite o código novo e clique em Salvar"; Esc na edição do nome só cancela.

Revisão da Operação (11/Nov, `7086e6c`): 3 bloqueios corrigidos. (1) Painel: ligar e desligar usa a lista inteira do
gráfico (antes, só as linhas desenhadas: o que estava em "Outros" ou além das 8 barras saía do total); `larguras.js` com
12 estados confere. (2) "Trocar licença": código novo não herda a confirmação do antigo; recusado ou sem internet, o
código bom volta e nada é gravado (testes `Revisao0732`). (3) Definition of done: AssistONE (tela do Painel, dica,
Configuração e atalhos, tour com "Configurações", busca com dias da semana, trocar licença, gráficos, cores, aparência,
novidades), rodapé do Painel, manual (Painel, Trocar licença no FAQ, ordem real da Configuração), Novidades, "Salvar
critérios", "Critérios da lista" no lugar de "Regras do escritório". Médias e baixas: config antigo sem `dias` segue
"todo dia"; foco volta ao item do gráfico; contraste do item apagado, da fase e do placeholder; textos sem "leitura da
noite"; `AGENDAR.bat` e LEIA-ME com o padrão novo; testes das travas dos dias; barra sem animação com movimento
reduzido; um item só não esvazia o Painel; "1 ação" na faixa; lista só com valores inválidos não desliga; Esc com Perfil
e busca abertos fecha uma de cada vez.

Feito: gráficos do Painel (dica ao passar o mouse com número e %, liga e desliga pela legenda com o item apagado,
"Mostrar todos", "Ver na lista →", cor escolhida no quadradinho e "Cores originais"; filtros do Painel separados dos da
Lista); leitura automática por dias da semana (Dom a Sáb, padrão de segunda a sexta nas instalações novas; nenhum dia
desliga; desligar guarda os horários e confere a tarefa); Configuração reorganizada (A lista: Critérios da lista e
filtros salvos; Onde ficam as planilhas; Leitura: automática e armazenamento; Tela: onde abre, Aparência espelhada do
Perfil e o Assistente; Licença e termos com "Trocar licença"; Sobre e Ver registro no fim), menu "Configurações" na
mesma ordem; "Novidades da versão" com a linha "Para rever…"; ressalvas da revisão da 0.7.31 (320 px em inglês,
placeholder e fase no contraste, Esc na Configuração com o foco fora, manual sem `apple-touch-icon`, textos sem promessa
de leitura da noite, `cod_instalador`, "1 ação", "o último mês", motivos `dominio_nao_liberado` e `email_recusado`,
testes das travas do item 13). Regra do dono (11/Nov): toda mudança confere **manual, AssistONE e Novidades**, em PT e
EN; os testes `Novo0732` conferem as Novidades da versão atual, os alvos do AssistONE e o manual.

## 0.7.31 (teste do dono na 0.7.29/0.7.30, 11/Nov) — publicada em 11/Nov

Feito no ramo: faixa e janela do aceite curtas ("Falta aceitar os termos: abrir a página de aceite. Dúvidas: …", sem o
link por extenso nem o código); sem linha vermelha repetida quando o motivo é a licença; código travado e mascarado
quando a SolverONE o reconhece (também com o aceite pendente); Termos com uma linha e um botão (Aceitar os termos ou Ler
os termos); Sazonalidade com um botão ("Buscar estatísticas" já lê; "Continuar (mais 30 Diários)"), "Últimos N meses",
aviso de que só soma totais e legenda da cor dourada; "Publicado no Diário" no lugar de "Data do processo";
Configuração da leitura mais baixa (botões à esquerda, texto ao lado); setas que giram e mira e "Mais filtros" abrem e
fecham com movimento; Configuração e Perfil pelo menu em janela, rolando com a roda do mouse; (?) na frente da janela;
tirar o último horário pergunta e desliga a leitura automática, e a tela inicial avisa "Leitura automática desligada.
Configurar"; frase das 19h mais simples; manual genérico (sem o nome da pessoa nem do escritório), com ícone e logo
embutidos (antes apontava para arquivos do site e a imagem quebrava) e sem a fonte do site; "Perfil" só no botão das
iniciais (saiu do grupo Programa do menu); manual explica que o código fica travado depois de confirmado.

Proposto ao dono, esperando decisão:
- **0.7.32 (gráficos)**: dica ao passar o mouse (nome, número, %); filtrar no próprio gráfico clicando na legenda (os
  desligados ficam apagados, "Mostrar todos"); "Ver na lista →" por cartão; filtros do Painel separados dos da Lista;
  cor escolhida no quadradinho da legenda, com "Cores originais".
- **Configuração reorganizada**: menu "Programa" vira "Configurações", na ordem da janela; ordem: Critérios da lista (ou
  "Regras do escritório"), Onde ficam as planilhas, Leitura automática (com Filtros salvos perto), armazenamento,
  Assistente (AssistONE), Licença e termos no fim (código mascarado, "Trocar licença" com confirmação), Ver registro por
  último; texto dos critérios sem a frase "escrito à mão" (benchmark: Kaspersky, ESET, Office, JetBrains, ADVBOX).
- **Dias da semana na leitura automática**: chips Dom a Sáb (padrão Seg a Sex); sem dia = desligada; texto "Lê nos dias
  marcados às …"; mexe na tarefa do Windows (`agendar.py`: `ScheduleByWeek`/`/d` com a lista de dias) e na compensação.

Roadmap (dono, 11/Nov): **duas versões do manual conforme a licença** (nuvem ou instalada neste computador), quando
houver a modalidade em nuvem; hoje só existe a instalada.

## 0.7.30 (11/Nov) — pronta para publicar

Revisão da Operação (11/Nov, commit `1b8b691`): 2 bloqueios corrigidos. (1) Menu ☰ ilegível no modo escuro (também com
"Igual ao sistema" e o Windows no escuro): itens com a cor do texto do tema, "Sair" com a cor de erro do tema, títulos da
busca geral também; (2) celular de 360 a 640 px com "Mais filtros" aberto: a página não alarga mais (coluna da barra
com `minmax(0, 1fr)`). O `larguras.js` passa a cobrir os dois casos (falham na versão antiga) e mede o contraste de todo
texto da Lista, do Painel, da Configuração e do Perfil no claro e no escuro (74 verificações). Também: "último dia útil"
pula feriado nacional (Finados, Consciência Negra, Carnaval), no máximo 7 dias para trás; Esc fecha o Perfil com o foco
fora dele; impressão sempre no claro; data do Diário fora do formato vale como "quando foi lido"; contraste no escuro
(CSV, pasta, situação Novo, Sazonalidade, AssistONE) e o cinza secundário do claro (4,5:1); "1 processo" no singular;
busca e "Filtros salvos (0)" sem corte no notebook; e-mail cita o documento do escritório; manual diz "a cada 30
minutos"; "O autor da ação e as testemunhas não aparecem" também no aviso por e-mail e nas páginas antigas; testes das 8
ressalvas da 0.7.29 (cada um falha se a trava sair). Fica para depois: aviso de fim de leitura e `minimo_acoes` pela
data do Diário (abaixo).

Revisão interna (revisor): sem bloqueio. Feitas: memória dos períodos com o estado e a licença de agora (5 minutos; não
guarda resposta que chegou depois de uma gravação); "Ler o Diário agora" com tribunais marcados confere a licença antes
e mostra o motivo se o programa recusar; comentário sem nome de ferramenta de IA. Fica para depois: o aviso de fim de
leitura (`monitor.py`) ainda conta pela data em que o programa viu (a lista e o Painel contam pela data do Diário);
`robo/MANUTENCAO.md` cita nomes de ferramentas de IA desde antes (o dono decide).

O que entrou (barra de controles da lista e o resto do teste do dono, 11/Nov):

- Filtro de período pela DATA DO PROCESSO no Diário (não quando o programa leu); "Período" de hoje vira "período de
  leitura"; "último dia" = do último dia útil até agora (o dono pediu recomendação se ficar grande).
- "Tribunais: N de 24" e o "alterar" ao lado de "Ler o Diário agora" fazem a mesma coisa: juntar num lugar só.
- "Ordem de chegada" (quando o programa achou, agrupado por leitura) x "Mais recentes primeiro" (data do Diário):
  nomes confundem.
- Feito no ramo (0.7.30), a partir do protótipo do dono: três blocos. "Configuração da leitura" (o que o programa lê,
  "Alterar configuração" = um botão só para a mira, "Ler o Diário agora", última e próxima leitura); "Filtros da lista"
  (busca, Data do processo, Situação, Valor, "Mais filtros" que abre os menos usados, filtros salvos, Limpar) com a
  ordenação e o "Baixar a lista (.csv)" em dourado no mesmo bloco, fixo no alto no computador (no celular rola junto).
  "Data do processo" conta pela data no Diário (1 = do último dia útil até hoje; 3 a 90 dias); a 1ª carga da tela usa
  o período salvo (antes pedia sempre 1 dia).
- Ajustes do dono (11/Nov): filtros numa linha só no notebook ("Data: ..." dentro da opção, busca mais curta); filtros
  salvos sempre à vista ("Filtros salvos (nenhum ainda)") com o link "★ Salvar"; "Limpar filtros (n)" pílula branca e
  vermelha; ✕ no filtro ligado tira sem abrir; "Marcar todos" em cada lista de filtro; "Configuração da leitura" em uma
  faixa baixa; abas com destaque cinza e a barrinha dourada deslizando; Painel com "Tribunal: Todos | TRT2 | TRT15"
  (o mesmo filtro da barra) e o título "Filtros do painel".
- Modo escuro (dono, 11/Nov; pesquisa do `pesquisador`: Material 3, Apple HIG, WCAG 2.2 1.4.11): Perfil → Aparência
  "Claro | Escuro | Igual ao sistema" (padrão: o sistema), com miniaturas, sem sol e lua; marinho escuro (não preto),
  superfícies que clareiam com a elevação, latão clareado (#c8a45c) para não virar mostarda, selos e gráficos com tons
  próprios do escuro; cores fixas viraram variáveis. Faixa de versão nova: confere de novo a cada 30 minutos com a
  tela aberta (antes só ao abrir). Ressalvas da segunda revisão da 0.7.29: 2 (já feito), 3, 4, 5, 6, 7, 9 feitas; 1 e
  8 e 11 ficam para o fechamento da 0.7.30; 10 não se aplica mais (a 0.7.29 já saiu).
- Feito no ramo (0.7.30): marcar tribunais na mira e clicar "Ler o Diário agora" salva e lê o que está marcado (antes
  lia a mira antiga sem avisar); o texto ao lado do botão acompanha o marcado, com "(marcado, ainda não salvo)"; o
  "alterar" não é mais cortado pelas reticências; círculo girando ao lado da barra de progresso.

## 0.7.29 de novo (11/Nov): revisão da Operação + o que estava como 0.7.30

Revisão da 0.7.29 (Operação): bloqueio feito ("Encerrar o RADAR" só encerra à força o processo que a própria tela
informa, que é o do programa.pid, desta pasta e é o Python; a leitura noutro processo só recebe o pedido de parar e
nunca é encerrada à força; tela travada só se o netstat confirmar que é ela na porta, senão a mensagem manda ao
Gerenciador de Tarefas); 2 a 6 e 7, 8, 9, 10, 11, 12, 13 feitos (trava única `radar.TRAVA_REGRAVAR` para toda
regravação da planilha; fases em 2 colunas abaixo de 900 px e 768 px no `larguras.js`; Saúde só silencia quando todos
os tribunais estão ok; ao atualizar da 0.7.28 o programa novo passa a tela para o pythonw e a janela preta fecha
sozinha; registro sem repetir mensagem; diagnóstico sem e-mail nem nome da pasta do usuário; "Encerrar" só desta
pasta; nome digitado habilita "Salvar regras"; "Abrir o arquivo" sem registro avisa; stdin fechado nos subprocessos).
Fica: 14 (abaixo de 360 px, já era assim). Também: Painel com "Ver como: Barras | Pizza" (teste no `larguras.js`),
"Licença: ✓ ativa" no Perfil com cor por estado. Teste do dono: janela fechada no X e clique no atalho em seguida não
abria a tela (o programa ainda a achava aberta): a tela avisa ao fechar (`/tela-fechada`) e o segundo clique confere
em 13 s se a tela atendeu o "já estava aberto"; se não atendeu, abre de novo.

### Itens que eram da 0.7.30

- Dono corrigiu o pedido da 0.7.29: o filtro de tribunais é só para ver o que já está na lista; não acompanha a mira.
  Desfeito (o filtro volta a mostrar só o que tem na lista; tirar da mira não mexe no filtro). O lugar único do que a
  leitura lê é a mira ("Tribunais: N de 24" e o "alterar" ao lado de "Ler o Diário agora"); a Configuração ganhou a
  linha "Tribunais que a leitura lê: ... alterar", que leva à mira.
- Painel (dono): meses com letras (SET/2026) nos gráficos; "Buscar estatísticas" responde ali mesmo (entraram N na
  fila, ou nada novo porque já está lido ou na fila); faixa no alto do Painel dizendo de quando são os números (N ações,
  Diários de X a Y, filtros da lista) com o período (1, 3, 7, 15, 30 dias) no mesmo estilo.
- Achado: o período da lista e do Painel conta pela data em que o programa VIU a ação (`primeira_vez`), não pela data
  do Diário. A primeira leitura traz até 10 dias de Diários de uma vez, e tudo aparece como "último dia" (os 13.339).
  Proposta ao dono: contar pela data do Diário. Mexe na regra do que a lista mostra: esperar o "pode".

## 0.7.29 (11/Nov) — pronta no ramo

Feito: sem janela preta (opção a da Arquitetura, "pode" do dono em 11/Nov); ressalvas 1 a 7, 9 e 10 da segunda revisão
da 0.7.28 (a 8 é decisão do dono: clicar fora fecha); falso alarme da Saúde. Fica: conferir com o dono os "13.339
processos no último dia"; ícone perto do relógio (opção c) só se o escritório sentir falta; a ideia de mandar o
registro para a nuvem espera desenho da Arquitetura. Precisa do teste do dono no Windows: (1) depois de atualizar, abrir pelo
atalho uma vez (o atalho passa a abrir sem janela; a tarefa antiga do Agendador, que chamava o RODAR.bat, é recriada
para o pythonw: conferir no Agendador de Tarefas, "LexSuiteONE Radar", aba Ações); (2) clicar de novo no atalho; (3)
☰ → Sair; (4) leitura automática sem janela e o aviso no fim; (5) DIAGNOSTICO.bat, opção 2; (6) Configuração → Ver
registro. Revisão interna: migração pelo XML da tarefa (igual em qualquer idioma), "Encerrar" só mata o processo cujo
pid a própria tela informa, leitura e "Salvar regras" se excluem dentro da mesma trava.

## Anotado em 10/Nov à noite (para a 0.7.29)

- Saúde: com todos os cadernos "já conferido", "0 publicações lidas" vira `[atenção] DJEN` (falso alarme visto pelo dono
  na leitura atrasada das 20:00). `saude.avaliar` precisa saber que os cadernos já tinham sido lidos e dizer "ok, nada novo".
- Duas janelas pretas (dono, 10/Nov à noite): a leitura automática abre a sua e, ao abrir a tela, vem a do programa.
  Proposta, esperando o "pode": a leitura automática roda minimizada (só na barra de tarefas; `RODAR.bat --agendado`
  se reabre com `start /min`), avisa no fim como hoje, e a janela da tela diz que a leitura está na outra janela.
- Conferir com o dono os "13.339 processos no último dia" (TRT2 e TRT15) vistos na tela da 0.7.27: parece alto para um dia.
- Ideia do dono (regra zero, não implementar sem desenho da Arquitetura e "pode"): quando a leitura falha sem internet,
  guardar o registro e mandar para a nuvem quando a conexão voltar. Hoje o registro fica só no computador (aba
  "Histórico de leituras", banco local e abas Log/Saúde da planilha).

## 0.7.28 (10/Nov)

Teste do dono no Windows (0.7.27), tudo feito: mês em letras e fuso; critério da leitura compacto com "alterar";
cores de filtro e ordenação; Limpar filtros; filtros lembrados; ✕/Cancelar/clicar fora em toda janela; administração
dos filtros salvos (locais; nuvem depois); Regras do escritório na tela; aviso de "já está aberto" no segundo clique.
Em aberto: travar a digitação na planilha de consulta (proteção de aba), sem resposta do dono.
Revisão da Operação (bloqueio e itens 2 a 12), feita: a tela das Regras só aparece se a planilha foi lida, e o
salvamento leva a "marca" do que a tela leu (se a planilha mudou ou não se lê, recusa e nada se perde); cópia em
`Cópias de segurança/... - antes de salvar regras` (6 guardadas, à parte das outras); pedido malformado volta 400;
fechar a Configuração pergunta pelas regras não salvas; colar contatos recarrega ao fechar e não fecha ao soltar a
seleção fora; campo vazio e número fora do limite avisam; código do "editar no Excel" removido e a aba "Como usar"
aponta para a tela; Controle e exclusões das outras frentes valem logo depois de salvar; datas vazias ficam vazias;
`leu_ate` em ISO; nome pela marca no segundo clique; Cancelar na Configuração; foco volta ao botão de origem; Limpar
filtros à vista no celular; a busca não fica guardada. Último a salvar não ganha mais: quem salva depois de outra
mudança recebe "as regras mudaram, abra de novo".
Revisão (Produto, revisor): a tela mostra e regrava só as exclusões da planilha trabalhista (as das outras frentes seguem
somando na leitura); sem planilha criada, não diz "salvo"; números fora do limite avisam antes de salvar. Fica: gravar
pela tela reescreve a aba Preferências só com as linhas padrão (linha extra escrita à mão nessa aba se perde).

Ressalvas da revisão da 0.7.27 (Operação): 1, 2 (números) e 4 feitas; 3 parcial (testes de rota e de texto mais firmes;
o comportamento da tela fica com o script de tela da Operação, pedido no quadro para ir ao repositório). Campos de texto
com `Infinity` literal no `config.json` ficam para depois (só edição à mão).

## 0.7.27 (10/Nov)

Ressalvas da revisão da 0.7.26 (Operação): 1 a 5 e 7 feitas; 6 aceita (lacunas residuais da heurística). Incidente do
revisor (servidor fictício chamou o DJEN): `testes/tela/servidor_ficticio.py` não lê mais o Diário.

## 0.7.26 (10/Nov)

Ressalvas da revisão da 0.7.25 (Operação): 1 a 8 feitas; 9 sem ação. Pacote 45/44.

## 0.7.25 (10/Nov)

Ressalvas da 0.7.23 (5 baixas) e da 0.7.24 (2 médias, 5 baixas): feitas. Decisão registrada (0.7.23, item 3): o
`monitor.dias_para_tras` à mão fica limitado a 30 dias. Ficam só em PT alguns motivos raros de `app.py` (cadastro) e de
`conta.MOTIVOS` no cadastro; entram quando o cadastro for revisto. Cobertura que ficou para depois (revisão da 0.7.25):
teste de `radar.executar`, `monitor.rodar` e `_rodada` com config ruim e de `motivo_en` no POST /config.

## 0.7.24 (10/Nov, teste do dono no Windows)

Aviso da planilha também no link da última leitura; marca "somente leitura" ao abrir; lupa com as partes da
Configuração; critério embaixo do botão; nomes das opções de pasta. **Pedido à Arquitetura:** página dos termos em
modo leitura (`aceite.html?ler=1`) sem a coluna vazia da direita e com a busca.

## 0.7.23 (10/Nov)

Ressalvas da revisão da 0.7.22 (Operação), itens 1 a 8: feitas. Pacote 45/44.

## 0.7.22 (09/Nov, noite)

AssistONE 1.1.1 do RootifyONE embutido (pedido do dono: balão que "voa" no tour, personagem que fica). Pacote 45/44. O RootifyONE corrigiu no master (1.1.1) os botões do tour que saíam do balão no modo sem o módulo comum; a correção local saiu.

## 0.7.21 (09/Nov, noite; no ramo)

Teste do dono no Windows (0.7.20) e decisões dele em 09/Nov (pastas em duas opções, planilha forçada a só leitura,
grupo "Área logada"): feito. **Pedido ao RootifyONE (master do AssistONE):** balão do tour que "voa" de um passo ao
outro; o personagem não some no tour (só se cobrir o alvo) e o último passo aponta para ele visível; depois a Produto
troca o bloco embutido.

Ressalvas da revisão da 0.7.20 (Operação): 1, 2, 5, 6, 8 e 9 feitas na Produto. Ficam com a Arquitetura: versão em
`docs/recursos-do-app.json` (3) e cabeçalho "v12" da `lex-conta` (4). Item 7 (ícone e fonte do manual dão 404 no servidor
local; cai na fonte do sistema) fica como está.

## 0.7.20 (09/Nov, noite; no ramo, depois da 0.7.19 publicada)

Interruptor do AssistONE pelo RootifyONE (lex-conta v12, campo `recursos`) e link do aceite com `#` (a Arquitetura já publicou a
página e a função). Falta do lado do RootifyONE: item 3d do prompt (ler `recursos-do-app.json` do site do produto e
publicar `recursos/radar-judicial.json`); até lá vale o interruptor global.

## 0.7.19 (09/Nov, noite; ressalvas da 0.7.18 e feedback do dono, antes da visita)

Ressalvas da Operação (revisão da 0.7.18): reserva de cada Diário antigo, fila só depois de 3 falhas, mensagens em PT e
EN que ficam na tela, "Ler agora" também com erros, marca "rodando" nunca presa, cópia do banco com data e sem
arquivo pela metade, turma trabalhada de volta, código mascarado. Feedback do dono (prints): "Ainda não leu" depois de
reiniciar; Interromper como botão vermelho; termos com um link só e aceite já preenchido; pastas explicadas, caminho
inteiro, teste automático e janela do Windows na frente; menu em gaveta com hierarquia; lupa de busca; engrenagem
centrada; gráfico do sinal para calibrar a regra com o Leandro. **Pedido à Arquitetura:** página do aceite na largura toda.
**AssistONE** já nesta versão (decisão do dono, pergunta 15): embutido, sem IA e sem internet, para validar com o Leandro na visita. Pacote continua com 45/44 arquivos.

## 0.7.18 (09/Nov, noite; antes da visita, depois da 0.7.17)

Feedback do dono (prints da 0.7.16): estatísticas dos meses anteriores para levar ao Leandro (sazonalidade e picos) —
feitas com as decisões 10 a 14 (30 Diários por vez, padrão 3 meses e configurável, só totais, à noite ou "Ler agora");
engrenagem ⚙ ao lado do perfil; perfil com o mesmo visual da Configuração e com a licença; e-mail e escritório fixos
(segurança: quem sai do escritório não leva a licença trocando o e-mail); pelo menu ☰, página própria com "Voltar";
cópia com links; o que vem da área logada atualiza o painel (valor, contato e agora o estado). Os 20.699 do dono eram
da regra antiga: limpeza única, sem apagar. **Pacote: 45 arquivos no download completo e 44 na atualização** (novo
`lexsuite/historico.py`). Se o CNJ não entregar Diário antigo (pergunta 12), a fila marca "sem Diário" e segue.

## 0.7.17 (09/Nov, noite; para publicar antes da visita, depois da 0.7.16)

Feedback do dono sobre os filtros (print da 0.7.15): "Limpar filtros" não aparecia ao escolher numa lista (defeito da
0.7.14), filtros sem várias opções, contagem que não seguia os outros filtros (escolher vara e setor dava "nenhum
processo"). Agora: caixas de marcar com busca, contagem cruzada, opção com zero some. A lista trazia "10ª Turma -
Cadeira 3": recurso distribuído a turma não é ação nova; 2º grau fica de fora. Observações da Arquitetura sobre a
planilha grande: limpeza automática só com cópia, data do critério no Painel, aviso de cópias em pasta compartilhada
(tela e manual), decisão 14 (banco acima de 1 GB). Pacote igual ao da 0.7.16 (44 e 43 arquivos). Ressalvas da revisão da
0.7.16 (Operação): e-mail de boas-vindas sem o passo de compartilhar a pasta (A); site e manual dizem tudo o que vai à
SolverONE (B, C); limpeza automática no máximo uma vez a cada 24 h e a poda nunca apaga cópia feita à mão nem
exportação (D); "notifique-se a reclamada" mantido (vem da regra estrita do diagnóstico) com rótulo próprio (E); cópia
da planilha antiga antes da troca de nome; cópia pela metade apagada. **Antes do tributário (F)**: a regra de ação nova
não reconhece "cite-se" nem "citação do executado" da execução fiscal; desenhar a regra própria da frente tributária
antes de prometer essa frente.

## 0.7.16 (09/Nov, noite; tudo antes da visita de quinta, decisão do dono)

Itens 89 a 101 de `documentacao/FEEDBACK-TESTE-2026-11-09.md` e as ressalvas da terceira revisão da Operação. **Planilha
grande** (`documentacao/DESENHO-PLANILHA-GRANDE.md`, decisões 1 a 9, tomadas pela Produto por delegação do dono): uma
planilha por frente na mesma pasta (`LexSuiteONE - Trabalhista.xlsx`; a antiga muda de nome sozinha), leitura só das
abas editáveis (a planilha de 20 mil linhas dava "ValueError"), aba Arquivo com 90 dias + trabalhados, limite de 60 mil
linhas com aviso a 80% e limpeza com cópia a 100%, `Cópias de segurança` (6), Configuração → Armazenamento com o espaço
livre do disco. **Ação nova** mais estreita (lista de distribuição, audiência inicial, una ou de conciliação,
notificação inicial; saem "fica notificado", "designada audiência" e "citação" soltos), com a contagem por sinal na
janela preta para conferir com o Leandro. **Tela**: Configuração em janela própria (✕, Salvar só com mudança, pergunta ao
fechar), "Buscar na área logada" com `RESPOSTA PARA O RADAR v1` (qualquer extensão de IA), valor da causa e data de
ajuizamento no programa, ✓ ao salvar, "Sair do RADAR", janela preta que fecha 3 minutos depois da tela, carregamento ao
atualizar, termos das duas camadas na Configuração e caixa "Li e aceito os termos de uso" no cadastro (a trava da
pessoa, `suporta_aceite_uso`, **ainda não** é pedida: liga quando a página dos termos for publicada e o dono responder a
pergunta 13), nada compartilhado com a SolverONE. Pacote: **44 arquivos no download completo e 43 na atualização**
(novo `lexsuite/armazenamento.py`). Para a 0.7.17: atualizar dados que mudaram (item 92), "Atualizar estatísticas"
(itens 79 e 82, depois das perguntas 10 a 12), `pode(acao)`.

## 0.7.15 (09/Nov; pronta de novo depois da revisão da Operação: banco não trava ao interromper, textos honestos, aviso de atraso só na leitura agendada)

Itens 85 a 88 de `documentacao/FEEDBACK-TESTE-2026-11-09.md`: botão **Interromper** (a leitura para no próximo ponto
seguro: entre um Diário e outro ou entre uma consulta à Receita e outra; o que já foi gravado fica, o Diário
interrompido não é marcado como lido e a próxima leitura baixa de novo os Diários desta leitura; vale para a leitura agendada, pelo
`saida/parar.json`; registrado em `acoes` e no histórico); aviso **"Fazendo agora a leitura das 08h00, que não rodou na
hora porque o computador estava desligado ou em repouso"** (`agendar.horario_perdido`); a "próxima leitura" da tela se
atualiza sozinha quando o horário passa. A seguir, com o desenho da Arquitetura: termos por pessoa e "Atualizar
estatísticas" (itens 79 e 82).

## 0.7.14 (09/Nov, pacote; pronta para publicar com o "pode")

Itens 42 a 84 de `documentacao/FEEDBACK-TESTE-2026-11-09.md` (menos 79 e 82, que vão para a 0.7.15) e os contatos
(itens 40 e 41, desenho da Arquitetura). Tela: menu ☰ (Configuração saiu do alto), abas Painel · Lista · Arquivo ·
Histórico de leituras, um cartão por linha, ficha sem corte e com endereço, situação no cartão com (?) e "Visto"
sozinho ao abrir, seleção em lote com a barra "Com os selecionados" (total, confirmação, Desfazer), busca, filtros de
valor (faixas, outro, sem valor), situação, contato, frente e "Não informado", Limpar filtros, filtros salvos,
ordenação dupla, selo de contato com o motivo, preparar busca na área logada e colar contatos, aviso antes de abrir a
planilha, Gerar uma cópia, pasta em cartões, horários com um clique, "O que a SolverONE recebe", letra e gráficos que
crescem com a tela (teste permanente em 4 larguras: `robo/testes/tela/larguras.js`). Programa: situação no banco do
computador (migra a do navegador), Arquivo, retorno de totais na conferência da licença, estatísticas diárias, frente,
endereço completo da Receita, limpeza só do detalhe, planilha só para leitura, regravação sozinha quando o Excel
fechar, aviso vermelho na aba Radar (a proteção da aba saiu: o Excel não deixa ordenar com células bloqueadas), abas Arquivo, Contatos e "Histórico de leituras", página
"Retrato da última leitura". Pacote: 43 arquivos no download completo e 42 no de atualização (entram `contatos.py` e
`frentes.py`).

Ajustes antes de publicar (revisão da Operação e pedidos do dono, 09/Nov): leitura agendada visível na tela (barra de
progresso e "Ler o Diário agora" desligado enquanto a agenda do Windows lê, pelo arquivo `saida/leitura.json`; duas
leituras nunca rodam juntas); aceite dos termos (`aceite_pendente` com o link na faixa da tela, "Termos aceitos por… em…"
na Configuração, instalador avisa e continua); opção de abrir a tela numa aba do navegador (menu ☰ e Configuração);
textos sobre dados corrigidos (manual, `SEGURANCA.md`, e-mail de boas-vindas: só quantidades vão à SolverONE; depois de
12 meses o detalhe vira resumo); Desfazer limpa o motivo; CPF sem pontuação recusado pelo dígito verificador; registro do
retorno só quando enviado. Adiado para a 0.7.15: a função única `pode(acao)` (níveis de acesso, desenho de 08/Nov) e os
motivos de recusa da colagem e os avisos da planilha em inglês.

## 0.7.13 (09/Nov, correção; publicada)

Defeito achado pelo dono às 00:05 de segunda: o DJEN só libera o Diário do dia a partir das 3h e responde HTTP 403 antes
disso; o programa tratava como erro e parava a leitura inteira, com "RuntimeError" e endereço técnico na tela. Agora:
esse 403 é reconhecido pelo texto da resposta e vira aviso ("o Diário de hoje só sai às 3h; li até o último dia
publicado"); cada tribunal é tentado à parte e o que foi lido é salvo; as mensagens dizem a causa em PT e EN (site do
CNJ fora do ar, sem internet, fora do Brasil, erro do programa), com o detalhe técnico recolhido; histórico de leituras
na tela e na aba Log da planilha (visível), uma linha por tribunal, com hora local e fuso, origem, resposta, causa e o
que o programa fez. O pacote grande (situações, lote, Arquivo, Estatísticas, contatos) sai na 0.7.14.

## 0.7.12 (08/Nov, visual; publicada)

Itens 38 e 39 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`, com o "pode pra tudo" do dono: a tela ganha o Painel
(o desenho antigo de Cajamar: cartões de números, ações por dia, faixas de valor, setores, empresas, porte, tribunais
e estados, nas cores marinho e latão), agnóstico de frente e com os mesmos filtros da Lista; a planilha ganha
cabeçalho azul-marinho fixo, filtro em todas as colunas, R$, destaque do valor acima do mínimo e a aba "Como usar".
Testada no LibreOffice e no openpyxl; falta abrir no Excel e no Google Planilhas de verdade. Contatos (itens 40 e 41)
esperam o desenho da Arquitetura.

## 0.7.11 (08/Nov, feedback do teste do dono; publicada ou a publicar pela Operação)

Itens 19 a 26 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`: leitura conta os dias que tiveram Diário (feriado e
recesso); faixa de versão nova ao abrir, atualizar com um clique e reinício sozinho; uma tela só por computador (o
atalho traz a aberta); código só para ler em Configuração; Configuração na engrenagem do alto; "Ler o Diário agora";
aviso ao abrir a planilha; barra de progresso da leitura e atalhos no fim; versão no alto e na dica do atalho; textos velhos do pacote (ressalvas b e c da revisão
da 0.7.10). Também (itens 29 a 37): CNPJ só vale para a ficha se o nome na Receita bater com o da empresa
processada ("CNPJ a conferir" quando não bate, inclusive no que já estava guardado); "Intimação" e afins saem do fim do
nome; MEI aparece (decisão do dono); tela larga com duas colunas, lista de 10 em 10, filtros e ordens novas, data
"SEG, 06 NOV 2026" e cartões novos; aviso e "Gravar a planilha agora" quando o Excel trava a planilha; manual com o
Google Planilhas.

## 0.7.10 (08/Nov, feedback do teste de instalação do dono; publicada)

Detalhe item a item em `documentacao/FEEDBACK-TESTE-2026-11-08.md`. Feito:
- **Defeito corrigido:** a leitura conta dias úteis (`monitor.dias_uteis`): sábado e domingo leem a sexta; segunda de
  manhã não pula mais a sexta.
- **Assistente:** código vindo do instalador só para ler; função obrigatória com "Outra" (texto) e "Prefiro não
  informar", e a dica (i); passo 2 com três opções explicadas (Google Drive deste computador, outra pasta com
  "Escolher pasta…" do Windows e criação da pasta, só neste computador), só o Google Drive na lista (OneDrive "sob
  consulta"); passo 3 com a frente (Tributário e Cível "em breve") e a escolha dos tribunais ali mesmo; passo 4 mostra
  onde a planilha fica e, se estiver no Drive, o passo a passo para compartilhar com `integracao@`.
- **Planilha:** instalação nova usa a pasta "<produto> - planilha" (as antigas continuam "LexSuiteONE"); a cópia da tela
  se chama "Lista para abrir no celular.html"; "Testar pasta" não deixa pasta vazia para trás.
- **Tela:** abre numa janela própria do Chrome ou do Edge (sem barra de endereço); painel Tribunais com o nome inteiro
  (duas colunas, sem "…", nome completo ao passar o mouse).
- **Janela preta:** título "<produto> - não feche esta janela" e cada passo da leitura com a hora (pela tela e na
  leitura automática).
- **Fica para depois:** e-mail já preenchido vindo do e-mail de boas-vindas (item 4; nuvem, desenho da Arquitetura).

## Feito em 08/Nov (a, b, c do dono)

- **A (nuvem, já aplicado):** pessoa ativa ou inativa, última vez, histórico (cadastro, troca de pessoa, alteração,
  acesso por dia) e limite contando só pessoas ativas (`lex-conta` v3, `lex-licencas.sql`, `lex-admin.sql`).
- **B (programa 0.7.9, publicar só com o "pode" do dono):** perfil pelas iniciais no alto da tela, com um lápis ✏️ por
  dado (nome, e-mail, função, escritório); trocar o e-mail avisa que outra pessoa vai usar o computador; o topo não
  mostra mais o nome do escritório nem "Olá"; Configuração fica com código, pasta e leituras automáticas; no passo a
  passo, cada campo é guardado ao sair dele, e ele volta enquanto o cadastro (e-mail) não estiver feito.
- **Horário de leitura ajustável (0.7.9, pedido do dono 08/Nov):** em Configuração, Leitura automática: horários em
  pílulas (tirar ×, acrescentar até 6), "Todos os dias" ou "De segunda a sexta"; padrão novo **20h e 8h** (o Diário sai
  a partir das 19h; às 8h pega o que entrou tarde da noite); leitura perdida acontece quando o computador ligar; aviso
  se não houver horário depois das 19h; "Próxima leitura automática" na tela; aviso no canto da tela do Windows ao
  terminar (dá para desligar). "Atualizar agora" continua sendo o executar na hora.
- **Depois (0.8): e-mail ao terminar** a leitura para quem está cadastrado (dono, 08/Nov: não é imprescindível).
- **C (RootifyONE 0.18.13):** Clientes → Licenças do RADAR: lista, Criar licença (código para escritório novo), ficha
  com ativar/desativar, validade, limite e mensagem, pessoas, computadores, histórico e erros; aba "Erros sem código".

## v0.7.x (ainda do robô local)

- Privacidade: trocar o trecho de 600 caracteres guardado no banco por rótulos (assunto, rito), eliminando o único
  dado sensível possível; pre-commit com gitleaks e bandit; plano de incidente de uma página (ver SEGURANCA-REVISAO).
- GitHub: proteção do ramo `main`, Dependabot, 2FA, ações da CI fixadas por SHA.

- Preferências que faltam: porte, CNAE e valor da causa como filtros (dependem do CNPJ pelo nome e do valor digitado).
- Avisos por Telegram e e-mail só do que passa nas regras (reaproveitar `avisar.py`).
- Regra de "ação nova" nos TJs e TRFs (hoje marcada "a calibrar"); classe "execução fiscal" para a frente tributária.
- Endereço fixo de atualização (precisa do repositório público no GitHub).
- Integração de saída: webhook JSON (um POST por ação, com HMAC) e CSV importável; começar por EasyJur e ADVBOX (APIs
  documentadas) e pelo Astrea quando houver API; ver `docs/INTEGRACOES-MERCADO.md`.
- Wizard de um arquivo (`INSTALAR-LEXSUITE.bat`, para WhatsApp): cria a pasta, baixa pacote e Python, abre a tela.
  Depende de um endereço público de download (Drive "qualquer pessoa com o link" ou GitHub).
- Tela: mostrar a hora da próxima rodada agendada; botão "Abrir pasta de saída".

## v0.8 (cliente-servidor e conta na nuvem)

**Desenho completo em `documentacao/DESENHO-0.8.md` (versão 2, 08/Nov/2026, reescrita em cima da licença da 0.7.9),
com as decisões D1 a D9 do dono.** Nada de código antes de ele aprovar o conjunto; nenhum SQL roda sem a revisão dele.
Pendências da Arquitetura (lista inteira na seção 13 do desenho):

- **Bloqueante:** termo de tratamento de dados com a KR Law (a SolverONE guarda dados em nome do escritório) assinado
  antes de a 0.8 entrar no ar. ⏸ Aguardando o dono.
- **Revisão de segurança da nuvem das licenças** (`documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`): nota Baixo hoje,
  Médio se a 0.8 entrar sem a etapa 0. SQL de correção em `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`
  ⏸ aguardando o dono revisar e rodar; `lex-conta` v4 (limites, resposta genérica, limpeza de `mensagem`) 🟡 depois do "pode".
- Copiar `teste/sql-grants.js` do rootify-one para este repositório e ligar na CI. 🟡 Arquitetura.
- Para a 1.0: e-mail de entrada com a marca de cada suíte (Send Email Hook do Supabase Auth); na 0.8 o remetente é
  "SolverONE <nao-responda@solverone.com.br>".

Os itens abaixo são o texto original da 0.8 (07/Nov) e ficam como histórico; o que vale é o desenho.

- Conta na nuvem (`judicial.solverone.com.br`): o robô, se tiver internet, pergunta a cada abertura se a conta do
  escritório continua ativa e registra um batimento (versão, última rodada, contagens). Gestão no RootifyONE.
  Regra de queda: sem resposta da nuvem, vale a aba Controle da planilha; sem nenhuma das duas por 30 dias, avisa
  e continua (não trava, por ser instalação local). Tabelas `lex_contas` e `lex_batimentos` no Supabase (SQL
  entregue para revisão e execução pelo dono, regra C10); chave publicável no `config.json`, nunca secreta.
- Código de cliente: formato `LEX-XXXX-XXXX` (letras e números, sem 0/O/1/I para não confundir), gerado no
  RootifyONE, enviado no e-mail de boas-vindas (bloco opcional já previsto no modelo em `docs/email/`) e pedido
  pelo passo a passo na instalação. Identifica a conta; não é senha e não dá acesso a nada sozinho.
- Endereço fixo de atualização: `judicial.solverone.com.br/atualizacao/` (site do produto). Assinatura na nuvem desde 08/Nov
  (serviço `assinatura.solverone.com.br`; publicação por tag `vX.Y.Z`, ver `docs/PUBLICAR.md`).

- Log de cada rodada numa aba oculta de uma planilha Google do cliente (via Apps Script publicado na conta da SolverONE;
  o robô só faz POST com biblioteca padrão; chave por cliente no `config.json`, nunca no código).
- Aba "Radar" com o incremento do dia e aba "Preferências" editável pelos advogados (as mesmas regras da v0.7).
- Painel de auditoria do fornecedor: leitura das abas de log pelo conector do Drive.

## 1.0 (SaaS no RootifyONE)

- Coletor central no Brasil (Supabase pg_cron + pg_net para a consulta leve; servidor pequeno para o caderno de 150 MB),
  lendo cada TRT uma vez para todos os escritórios. Tabelas `lex_publicacoes`, `lex_acoes`, `lex_regras`, `lex_eventos`.
- Fila de eventos: cada ação que passa nas regras de um escritório vira evento; entrega por e-mail, WhatsApp,
  notificação no app (PWA) e webhook de saída para o sistema do escritório.
- Interruptores do RootifyONE (`data-recurso`, `recursos-do-app.json`), PT/EN, feedback 💬, trabalho em `Fundo`.
- Bandit e Gitleaks no GitHub Actions (sem IA). Revisão de segurança e LGPD trimestral com a skill existente.

## Ideias registradas (portfólio)

- Monitor de publicações dos processos do escritório (já existe em `monitor.py`; virar produto).
- Jurimetria da vara e do juiz (DataJud); raio-x trabalhista de um CNPJ (para empresas); radar cível nos TJs
  (o DJEN cobre todos os tribunais).
- IA opcional e trocável (resumo, peças) com chave do próprio escritório, nunca no caminho principal.
