# Desenho: (1) leitura quando o CNJ cai e (2) instalação com antivírus (Arquitetura, 14/Nov/2026)

Pedido do dono (14/Nov) sobre `documentacao/DOSSIE-ANTIVIRUS-2026-11-13.md` (Operação) e as 20 fotos de 13/Nov (com o dono; vistas
como evidência, nada delas entra no produto). Regra do dono: **detectar, explicar e orientar; nunca contornar o antivírus**.
Conferido no código em 14/Nov: `rede.py` guarda só código, URL e 2.000 caracteres do corpo (sem cabeçalhos nem tempo); `causas.py`
classifica 404 / 429 e 5xx / 403 das 3h / sem internet; `agendar.py` cria a tarefa por `schtasks /create /xml` com XML na pasta
temporária, chamado pelo `pythonw` (o que o Bitdefender marcou); o instalador testa escrita, baixa com `curl`, descompacta com `tar`
e `Expand-Archive`, não cria a tarefa; o `ROTEIRO-INSTALACAO.md` linha 38 ainda sugere **desligar** a Defesa contra Ameaças
durante a instalação (contra a regra; corrigir). Nenhum código lê o antivírus instalado.

Ordem resumida (detalhe no fim): **0.7.47 (rápida, Produto)** = evidência e diagnóstico da falha do CNJ, antivírus detectado e
mensagens orientadas, tarefa criada às claras na instalação, checagem antes de instalar; **Arquitetura junto** = `lex-conta` v19
(estado do CNJ para o programa, campos novos do registro técnico), alerta do observador; **0.7.48** = leitura pela consulta
quando o caderno cai; **decisões do dono** = certificado de assinatura, página de antivírus no site e e-mail, aviso geral no RootifyONE.

---

## PROBLEMA 1 · a leitura quando o CNJ falha

### 1.1 Causa identificada: evidência que separa "é do CNJ" de "é deste computador"

O que o RADAR passa a guardar em cada tentativa (`rede.py` → `ErroHTTP`/`ErroRede` → `monitor.tentativas` → "Detalhes técnicos"):

| Campo | Para quê |
|---|---|
| hora UTC e Brasília, URL sem consulta, método | linha do tempo |
| código HTTP e **cabeçalhos** `date`, `server`, `via`, `x-cache`, `x-amz-cf-pop`, `x-amz-cf-id`, `content-type`, `retry-after` | de onde veio a resposta |
| corpo: primeiros 300 caracteres | `{"message":"Server Error"}` = a aplicação do CNJ; HTML com "CloudFront" e "Request ID" = a borda da Amazon |
| tempo de resposta (ms), tentativas, DNS resolvido (IP) | lentidão, falha de rede, proxy |
| **duas sondas de controle** quando o CNJ falha: `https://judicial.solverone.com.br/versao.json` (internet do escritório) e um segundo serviço do CNJ (`comunicaapi…/api/v1/comunicacao?…itensPorPagina=5`) | triangular |

Classificação (nova coluna `origem` em `causas.classificar`), em palavras para a tela:

| Sinais | Diagnóstico mostrado |
|---|---|
| 5xx com corpo JSON do CNJ, `server: CloudFront`, sonda da SolverONE ok | **"O servidor do CNJ respondeu erro (aplicação). Sua internet está normal. Não é problema deste computador."** |
| 5xx/504 com HTML da CloudFront ("Error from cloudfront") | "A rede do CNJ (borda) não alcançou o servidor. Geral, não é daqui." |
| caderno 5xx e consulta ok | "O serviço de caderno do CNJ está fora; a consulta funciona" (gatilho do caminho alternativo, 1.3) |
| DNS falha / tempo esgotado / TLS inválido / 403 sem "block access", e a sonda da SolverONE também falha | "Este computador está sem internet ou com a rede bloqueada." |
| sonda da SolverONE ok, só os endereços do CNJ e da Receita falham com reset/timeout/certificado estranho | **"Algo neste computador (antivírus, firewall ou proxy) está barrando só os nossos endereços"** → orienta (Problema 2) |
| 403 "block access from your country" | "O CNJ bloqueia acesso de fora do Brasil (VPN?)" |

Mais: **confirmação pela SolverONE**. A `lex-conta` ganha a ação `estado_cnj` (anon, leve, 1 por 5 min por instalação) que devolve a
última rodada do observador (seção 1.2): `{hora, ok: 23, fora: ["TRT9"], desde: "13:30"}`. A tela escreve: "A SolverONE também vê o
CNJ fora desde 13h30 (23 de 24 tribunais)". Esse é o jeito de o advogado saber que é geral, sem precisar ligar.

**Aviso oficial do CNJ** ("prazos suspensos em 12 e 13/11"): não há endereço oficial estável para um programa ler (pesquisa de
14/Nov: cada tribunal publica no seu portal, o CNJ em notícia; o DJEN não tem lista de indisponibilidades consultável). Nada de
raspar site. Proposta: tabela `lex_avisos_gerais (texto, link_oficial, inicio, fim, tipo)` escrita pela equipe no RootifyONE quando
o CNJ publicar (com o link da fonte oficial), devolvida pela `lex-conta` em `verificar` e em `estado_cnj`, mostrada na faixa da
leitura com o link. Depende do "pode" do dono (nuvem + tela do RootifyONE).

### 1.2 Observador no Brasil (já existe desde 13/Nov) e o que falta

O observador é a função `lex-saude` em São Paulo (Supabase `sa-east-1`, IP brasileiro, 24 TRTs a cada 15 min, tabela
`lex_saude_diarios`): em 14/Nov já tinha 21 rodadas e 504 conferências (72 ms em média). **Não precisa da Oracle para isso**; a Oracle
fica como executor de testes (staging, seção 7b) e plano B se o Supabase for bloqueado. Falta:

1. **Alerta à SolverONE**: na `lex-saude`, quando 6 ou mais tribunais estiverem "fora" em duas rodadas seguidas (ou 1 tribunal por
   4 rodadas), e-mail `[CNJ] caderno fora: 23 de 24 tribunais desde 13:30` para `judicial@` (Resend, no máximo 1 por hora) e outro
   na volta. A Central mostra a aba Diários já hoje.
2. **Aos clientes**: pela própria tela (1.1, `estado_cnj`), sem e-mail. E-mail ao escritório só em queda longa (acima de 4 horas em
   dia útil), se o dono quiser (pergunta 35).
3. **Sonda do caderno e da consulta**: a `lex-saude` passa a testar também a consulta (`comunicacao?itensPorPagina=5`) num tribunal
   por rodada, para a Central e o programa saberem se o caminho alternativo está de pé.

### 1.3 Caminho alternativo pela consulta pública quando o caderno cai

- Gatilho: caderno do dia com 5xx (como 13/Nov) e consulta respondendo; só para os dias pendentes (0.7.42 já guarda a lista).
- Como: `GET /api/v1/comunicacao?siglaTribunal=TRTn&dataDisponibilizacaoInicio=D&dataDisponibilizacaoFim=D&itensPorPagina=100&pagina=k`,
  1 pedido por segundo, 15 s de limite, 1 nova tentativa só em timeout e 5xx, parar depois de 3 timeouts seguidos (a consulta devolve
  500 sob rajada, não 429). Se `count` chegar a 10.000, **dividir por vara** (`orgaoId`): a lista de varas de cada tribunal o programa
  monta sozinho a partir dos cadernos que já leu (campo `orgaoId`/`nomeOrgao` de cada comunicação) e guarda no banco; varas novas
  entram quando aparecem. Para o TRT2 (o maior) isso pode levar 20 a 40 minutos; a tela mostra "lendo pela consulta, vara por vara".
- O que entra: as mesmas comunicações (mesmo formato JSON do caderno), marcadas `fonte: consulta` e `caderno_pendente: sim`; quando
  o caderno voltar, o RADAR relê o dia pelo caderno e completa o que faltou (sem duplicar: chave da comunicação). O manual explica
  que, pela consulta, a leitura pode levar mais tempo e ser completada depois.
- Nunca sobrecarregar: por padrão só com a leitura automática (noite) ou a pedido ("Ler pela consulta agora"), uma vez por dia
  pendente; respeita o observador: se a SolverONE vê a consulta fora também, nem tenta.
- Limite da API em `itensPorPagina` (50 ou 100) e páginas vazias no meio: a Produto confirma na prática nos primeiros testes.

---

## PROBLEMA 2 · instalação com antivírus, firewall ou bloqueio (o mais importante)

### 2.1 O instalador reconhece o bloqueio e orienta

**Detectar o antivírus** (Windows 10 e 11, sem administrador): PowerShell
`Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select displayName, productState`. Se o namespace não
existir (Windows Server), "não identificado" e orientação genérica. O `productState` diz se está ligado (0x41000 ligado e
atualizado, 0x40000 desligado; leitura de comunidade, não oficial). O `wmic` está obsoleto; usar PowerShell. Também `FirewallProduct`.

**Sinais genéricos** (os do dossiê, 1B), cada um com a mensagem no lugar de "erro":

| Sinal | Como o instalador percebe | Mensagem (resumo) |
|---|---|---|
| rodando de dentro do .zip | pasta atual dentro de `%TEMP%` e caminho com `.zip` | "Extraia o zip antes (botão direito → Extrair tudo) e rode o INSTALAR.bat de dentro da pasta extraída." Para e espera. |
| arquivo não pode ser criado ou some | teste de escrita ok, mas depois do `tar` falta `lexsuite_robo.py` ou `python\python.exe` | "O <antivírus> bloqueou a criação dos arquivos do programa em C:\LexSuiteONE." + passos de exceção |
| processo morre | `pythonw`/`python` não está rodando 5 s depois de iniciar (`tasklist`) | "O <antivírus> encerrou o programa ao abrir." + passos (Defesa contra Ameaças / comportamento) |
| tarefa não criada ou nunca roda | `schtasks /create` devolve erro, ou `/query` não acha, ou "Última execução" nunca muda | "O <antivírus> impediu a leitura automática." + passos; o programa (0.7.45) já lê sozinho com a tela aberta |
| rede recusada só para os nossos endereços | `curl` em `judicial.solverone.com.br` falha mas `curl` em um site neutro passa (ou o contrário) | "A proteção de rede do <antivírus> ou o firewall está barrando os endereços do RADAR" + lista de endereços para a TI |
| aviso "fornecedor desconhecido" / SmartScreen | arquivo com marca da internet (`Zone.Identifier`) | não é bloqueio: "clique em Executar; o programa não tem assinatura digital ainda" |

Cada mensagem traz: o que aconteceu, o antivírus encontrado, **o passo a passo daquele antivírus** (quando conhecido) e um **texto
pronto para a TI** (pastas `C:\LexSuiteONE` e `%LOCALAPPDATA%\LexSuiteONE`; arquivos `python\python.exe`, `python\pythonw.exe`,
`lexsuite_robo.py`; tarefa "LexSuiteONE Radar"; endereços `judicial.solverone.com.br`, `comunicaapi.pje.jus.br`,
`qvdvkqydhnadhewcidia.supabase.co`, `brasilapi.com.br`, `minhareceita.org`). Nunca "desligue o antivírus".

Passos por antivírus (o que está confirmado em fonte oficial ou nas fotos; o resto vai para a página do site com a ressalva
"confira na sua versão"): **Bitdefender** (fotos 05 a 09): Proteção → Defesa contra Ameaças → Configurações → Administrar exceções →
`C:\LexSuiteONE\` **sem asterisco**, ligar Antivírus (Verificação ao acessar, Análise a-pedido, Scripts incorporados) e Defesa contra
Ameaças → Salvar; se já houve bloqueio, Notificações → **Reiniciar** antes de instalar de novo. **Microsoft Defender** (oficial):
Segurança do Windows → Proteção contra vírus e ameaças → Gerenciar configurações → Exclusões → pasta; e, se "Acesso controlado a
pastas" estiver ligado, "Permitir um aplicativo" para `python.exe`. **Kaspersky, ESET, Avast, Norton, Sophos**: caminhos levantados em
14/Nov (doc oficial para Kaspersky, ESET, Avast, Sophos; comunidade para Norton); **McAfee e Trend Micro**: sem fonte oficial, "fale
com o suporte do fabricante ou a TI". Fontes listadas na página do site (2.5).

### 2.2 Checagem antes de instalar

Passo 0 do `INSTALAR.bat`, antes de baixar: (a) está dentro do zip?; (b) antivírus e firewall encontrados; (c) pasta de destino
gravável; (d) saída para os nossos endereços (`curl` leve); (e) aviso: "Antivírus encontrado: <nome>. Programas novos costumam ser
barrados por ele. **Antes de continuar**, cadastre a exceção da pasta C:\LexSuiteONE (passos abaixo) ou peça à TI. Depois aperte
Enter." Com Defender puro, a orientação é só "se aparecer aviso, clique em Executar". O `ROTEIRO-INSTALACAO.md` e o `VISITA-KR-LAW.md`
ganham a mesma lista como checklist (e perdem a linha que manda desligar a Defesa contra Ameaças).

### 2.3 O que volta à SolverONE e o que muda nos termos

O registro técnico (`lex-conta`, ação `registro`, já existente) ganha três campos opcionais: `antivirus` (só o `displayName`, ex.:
"Bitdefender Antivirus"), `antivirus_ligado` (sim/não) e `sinal` (um de: `zip_temp`, `bloqueio_gravacao`, `processo_morto`,
`tarefa_falhou`, `rede_recusada`, `smartscreen`); `lex_registros` ganha as colunas (SQL datado). Nada identifica pessoa: nome de
produto e o que falhou. O RootifyONE mostra na ficha e num painel "quais antivírus aparecem e quanto bloqueiam".
**Termos**: a seção 6.2 (c) já cobre "registros técnicos de erro, sem conteúdo de processos"; o nome do antivírus é dado do
computador, não da pessoa, logo **não é mudança material**: entra como esclarecimento editorial na próxima versão 1.1 ("registros
técnicos de erro, inclusive o sistema e o antivírus do computador"), sem novo aceite. LGPD: sem dado pessoal novo.

### 2.4 O programa instalado

Configuração → "Este computador": antivírus e firewall encontrados (lidos uma vez por dia), ligados ou não, e o link "Como liberar o
RADAR no <antivírus>" (manual e site). Nos erros do programa: leitura automática não criada ou não executada; arquivo que sumiu
(`python.exe`, `lexsuite.db`, planilha não gravada); rede recusada só para os nossos endereços (1.1): a mensagem nomeia o antivírus
e aponta os passos. O painel de saúde (`saude`) registra o sinal para o histórico de leituras.

### 2.5 Site e e-mail

`paginas/antivirus.html` (→ `docs/antivirus.html`, gerada pelo `marca.py`, sem pedido externo): uma seção por antivírus, com os
passos, uma imagem **recortada** da janela do Bitdefender (só a janela, sem nada do cliente) e o link da fonte oficial de cada um; a
seção "Para a TI" com o texto pronto. Manual: link para a página. E-mail de boas-vindas: uma linha "Se o antivírus bloquear, veja
judicial.solverone.com.br/antivirus". Site e e-mail são coisa que o cliente vê: **"pode" do dono** (pergunta 36).

### 2.6 Menos falso positivo, sem esconder nada

1. **Leitura automática às claras (0.7.47)**: a tarefa "LexSuiteONE Radar" passa a ser criada **durante a instalação**, na janela
   visível, por `schtasks /create /sc daily /st HH:MM /tr "C:\LexSuiteONE\python\pythonw.exe …"` **sem XML na pasta temporária**;
   quando precisar de XML (dias da semana, vários horários), o XML fica em `C:\LexSuiteONE\tarefa.xml`, com `Author` e `Description`
   "SolverONE · LexSuiteONE · RADAR JUDICIAL". A tela continua podendo alterar horários (mesmo caminho). É o que removeu o gatilho
   exato da foto 04. O `pythonw` (sem janela) fica, porque o dono decidiu sem "janelas pretas".
2. **Falso positivo aos fabricantes** (Operação, a cada versão grande): Microsoft (`microsoft.com/wdsi/filesubmission`) e
   Bitdefender (formulário de falso positivo do suporte), com o pacote e o instalador; depois Kaspersky, ESET, Avast, Norton se
   aparecerem em clientes. Prazo de resposta varia (dias a semanas); registrar no quadro a data e o protocolo.
3. **Assinatura de código** (pesquisa de 14/Nov): o `.bat` **não se assina**; precisaria de um instalador `.exe`/`.msi` assinado (ou
   um lançador `.exe` assinado que chame um `.ps1` assinado). Opções: (a) **Azure Artifact Signing** (US$ 9,99/mês), hoje **não aceita
   organizações do Brasil** para certificado público (lista de países de 08/Out/2026); (b) certificado **OV** de AC comercial (Sectigo
   US$ 220 a 322/ano, DigiCert ~US$ 438/ano) + chave em token ou HSM na nuvem (obrigatório desde 2023), validação da empresa pelo
   CNPJ, 1 a 20 dias; (c) EV (US$ 290 a 685/ano) não dá mais vantagem no SmartScreen desde 2024. Efeito real: o aviso "fornecedor
   desconhecido" passa a mostrar **"SolverONE"**; o SmartScreen só para de avisar com reputação acumulada (semanas e centenas de
   instalações com a mesma identidade); antivírus por comportamento (Bitdefender) **continuam olhando o que o programa faz**, então
   a assinatura ajuda, mas o item 1 é o que resolve o caso da KR Law. Recomendação: **adiar o certificado** até haver 3 ou mais
   escritórios; fazer 1 e 2 agora (pergunta 34).
4. **Pacote menos "suspeito" sem esconder**: manter tudo em `C:\LexSuiteONE` (ou `%LOCALAPPDATA%\LexSuiteONE`), nunca em pasta
   temporária depois da instalação; nomes claros (tarefa, atalho, pasta); o instalador avisa antes de cada ação "agora vou criar a
   leitura automática"; nada de ocultar janela do instalador.

---

## Ordem de execução

| Quando | O quê | Quem | Precisa do dono? |
|---|---|---|---|
| **0.7.47 (rápida)** | 1.1 cabeçalhos, sondas de controle, `origem` e a linha de diagnóstico em "Detalhes técnicos"; 2.1 e 2.2 (detecção, sinais, mensagens, passo 0, zip); 2.6.1 (tarefa criada na instalação, sem XML em %TEMP%); 2.4; `ROTEIRO` sem "desligar"; manual, AssistONE, Novidades | Produto | não (correção e orientação) |
| junto | `lex-conta` v19: ação `estado_cnj`, campos `antivirus`, `antivirus_ligado`, `sinal` no `registro`; SQL `lex_registros` + colunas; `lex-saude` com alerta por e-mail e sonda da consulta | Arquitetura | "pode aplicar" (nuvem) |
| **0.7.48** | 1.3 leitura pela consulta, vara por vara, com a lista de varas montada dos cadernos | Produto | pergunta 37 (padrão ligado?) |
| decisão | 2.5 página de antivírus no site + linha no e-mail de boas-vindas | Arquitetura (página) e Produto (manual/e-mail) | **sim**, pergunta 36 |
| decisão | aviso geral do CNJ (tabela + tela do RootifyONE + faixa no programa) | Arquitetura + RootifyONE | pergunta 38 |
| decisão | certificado OV de assinatura e instalador `.exe` | Arquitetura (desenho), dono (compra) | pergunta 34 |
| contínuo | falso positivo aos fabricantes a cada versão grande | Operação | pergunta 39 |

## Decisões do dono (14/Nov, em chat; registradas no quadro)

- 34 **Sem certificado de assinatura por enquanto.** Sai da ordem; fica o item 2.6.1 (tarefa às claras) e o 2.6.4.
- 35 **Só a faixa**, mais uma **opção em Configuração: "Avisar por e-mail quando o CNJ ficar fora por mais de 4 horas"**, no e-mail
  cadastrado para aquela instalação. Como: o programa manda a preferência na `verificar` (`avisar_cnj: true`), a `lex-conta` grava em
  `lex_instalacoes.avisar_cnj`; a `lex-saude`, ao detectar queda longa em dia útil, manda um e-mail por instalação marcada (Resend, 1
  por queda e 1 na volta). Termos: aviso de serviço ao e-mail já cadastrado, dentro da finalidade "prestar o serviço" (6.3); sem mudança.
- 36 **Página de antivírus no site e linha no e-mail de boas-vindas: sim**, cobrindo **todos os principais antivírus do mercado**
  (Microsoft Defender, Bitdefender, Kaspersky, ESET, Avast, AVG, Norton, McAfee, Trend Micro, Sophos, Panda, Malwarebytes, Avira),
  cada um com fonte oficial e data; onde não houver fonte oficial, a página diz "confira com o fabricante ou a TI".
- 37 **Leitura pela consulta quando o caderno cai: sim**, por padrão, só na leitura automática e a pedido (0.7.48).
- 38 **Aviso geral do CNJ: deixar preparado** (tabela, resposta da `lex-conta` e faixa), sem equipe para alimentar agora.
- 39 **Falso positivo aos fabricantes: aguardar** por enquanto.

Ordem revista: 0.7.47 (Produto) = 1.1, 2.1, 2.2, 2.4, 2.6.1, opção de e-mail (35) e textos; Arquitetura junto = `lex-conta` v19
(`estado_cnj`, campos do registro, `avisar_cnj`), SQL (`lex_registros`, `lex_instalacoes`), `lex-saude` com alerta à SolverONE e aos
que marcaram; página `antivirus.html` (36) com a pesquisa oficial por fabricante; 0.7.48 = 1.3; preparado sem uso = 38.

## Perguntas ao dono (na lista única do quadro, 34 a 39; respondidas)

34. Certificado de assinatura (OV, ~US$ 300/ano + token, mais um instalador .exe): comprar agora ou adiar até 3 escritórios? Recomendo adiar.
35. Queda longa do CNJ (mais de 4 h em dia útil): mandar e-mail ao escritório, ou só a faixa na tela? Recomendo só a faixa.
36. Página de antivírus no site e a linha no e-mail de boas-vindas: pode publicar? Recomendo sim.
37. Leitura pela consulta quando o caderno cai: ligada por padrão para todos? Recomendo sim, só na leitura automática e a pedido.
38. Aviso geral do CNJ escrito pela equipe no RootifyONE (com link oficial) e mostrado no programa: pode? Recomendo sim.
39. Falso positivo aos fabricantes: a Operação envia a cada versão grande, em nome da SolverONE? Recomendo sim.
