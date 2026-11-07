# LexSuiteONE na plataforma SolverONE: caminho das pedras (v1, 22/Out/2026)

Objetivo: transformar o robô e o dashboard de hoje num **produto modular da SolverONE**, vendido como serviço
(SaaS). Cada escritório entra com a conta SolverONE, vê só as suas varas e a sua carteira, recebe avisos e
paga um plano.

## 0. Como as peças se encaixam

| Peça | Onde mora | O que faz |
|---|---|---|
| **App LexSuiteONE** | repositório `lexsuite-one` no GitHub, publicado em **solverone.com.br/lexsuite-one/** | as telas: dashboard, ações, empresas, raio-x, configurações, login |
| **Banco** | Supabase `solverone-app` (São Paulo), tabelas com prefixo `lex_` | contas, escritórios, varas monitoradas, carteira, ações, alertas |
| **Coletor (o robô)** | um computador ou servidor **no Brasil** | lê DJEN, pauta e DataJud todo dia e grava no banco |
| **RootifyONE** | o admin que já existe | catálogo do app, planos, liga e desliga funções, usuários, feedback |
| **solverone-dados** | arquivos master publicados pelo RootifyONE | `apps.json`, `servicos/lexsuite-one.json`, `recursos/lexsuite-one.json` |

**Identidade do app** (segue o contrato de dados da plataforma):

| Item | Valor |
|---|---|
| Código do app | `lexsuite-one` |
| Prefixo das tabelas | `lex_` |
| Repositório | `lexsuite-one` |
| Endereço | `https://solverone.com.br/lexsuite-one/` |
| Nome do pacote | `LEXSUITE-ONE vX.Y.Z dd-Mmm-aaaa HHhMMm.zip` |

O domínio já está configurado no repositório do Portal. Por isso, qualquer repositório novo com Pages ligado
aparece sozinho em `solverone.com.br/<nome-do-repositório>/`.

---

## 1. Criar o repositório e publicar (uns 15 minutos)

**Caminho mais fácil:** você me autoriza e eu crio o repositório `lexsuite-one` no seu GitHub e subo a
estrutura inicial. Você só confere.

**Se preferir fazer você mesmo:**

1. Entre em **github.com/new**.
2. Repository name: `lexsuite-one`. Marque **Public** (o GitHub Pages grátis exige repositório público). Marque
   **Add a README file**. Clique em **Create repository**.
3. **Sobre subir um .zip:** o GitHub **não descompacta** o zip. Faça assim:
   1. Descompacte o zip no seu computador.
   2. No repositório, clique em **Add file → Upload files**.
   3. Arraste o **conteúdo** da pasta descompactada (os arquivos e subpastas, não a pasta de fora).
   4. Clique em **Commit changes**.
   O limite é de 100 arquivos por vez e 25 MB por arquivo.
4. Ligue o site: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: main /
   (root) → Save**. Em 1 ou 2 minutos o endereço `solverone.com.br/lexsuite-one/` passa a responder.

**O que NUNCA sobe para o repositório**, porque ele é público:

- `config.json` (pode ter e-mail e configurações);
- `carteira.csv` (a lista de clientes de um escritório é confidencial);
- `lexsuite.db`;
- a pasta `saida/` com dados de clientes;
- qualquer senha, chave ou token.

O pacote inicial já vem com um `.gitignore` que bloqueia esses arquivos.

---

## 2. Estrutura do repositório

```
lexsuite-one/
  index.html  app.js  estilos.css          ← o app (telas)
  diretrizes.js  diretrizes-config.js      ← módulo comum da SolverONE (cópias dos masters do rootify-one)
  janela.js  cofre.js  assistone.js  recursos.js
  sw.js  manifest.json  icone-192.png  icone-512.png
  versoes.json  recursos-do-app.json  servicos.json
  ARQUITETURA.md  PENDENCIAS.md  LICENSE  CREDITOS.md  .gitignore
  coletor/                                 ← o robô (Python), roda no Brasil
    lexsuite_robo.py  lexsuite/  testes/  LEIA-ME.md
  supabase/                                ← SQL das tabelas lex_* (revisado antes de rodar)
    2026-xx-xx-lexsuite-one.sql
```

O dashboard de hoje vira a tela principal do app. Ele passa a ler do banco em vez de ler os dados embutidos
no arquivo.

---

## 3. Banco de dados (Supabase `solverone-app`)

Segue o contrato v1 da plataforma (`PLATAFORMA-DADOS.md` no rootify-one).

**3.1 Registrar o app.** No RootifyONE: **Usuários → Plataforma (Supabase) → Apps da plataforma → + App novo**.
Código `lexsuite-one`, nome LexSuiteONE. O próprio SQL do app também faz esse registro.

**3.2 Escritório = grupo da plataforma.** Cada escritório é um grupo (`sol_grupos`), com governança
`lexsuite-one`. Mapeamento de papéis:

| Papel da plataforma | Papel no escritório |
|---|---|
| chefe | sócio administrador (paga e convida) |
| responsável | advogado |
| membro | equipe e leitura |

Hoje o tipo de grupo previsto é "familia". Criar o tipo "escritorio" é uma decisão sua: uma linha no SQL.

**3.3 Tabelas do app (prefixo `lex_`):**

| Tabela | Quem vê | Conteúdo |
|---|---|---|
| `lex_acoes` | todos os escritórios que monitoram a vara (por função) | processo, tribunal, vara, rito, faixa de valor, ajuizamento, audiência, empresas (só pessoa jurídica), setor, terceirização, fonte |
| `lex_varas_raiox` | idem | o raio-x de cada vara (volume, pedidos, desfechos) |
| `lex_monitor` | membros do escritório | quais TRTs e varas o escritório acompanha |
| `lex_carteira` | membros do escritório | clientes do escritório (CNPJ e nome). **Confidencial** |
| `lex_alertas` | membros do escritório | cada ação que interessa ao escritório: nota, status, responsável, observações (um CRM leve) |
| `lex_coletas` | equipe SolverONE | registro de cada rodada do coletor (para saber se falhou) |

**3.4 Regras do contrato:**

- RLS em todas as tabelas.
- O app só escreve por funções, nunca por INSERT direto.
- A coleta é feita **uma vez por tribunal por dia**, para todos os clientes, então o custo não cresce com o
  número de escritórios.
- `lex_anonimizar(uid)` cuida da LGPD, e nada é apagado por DELETE.
- **O SQL é escrito por mim, revisado e só depois rodado por você** no SQL Editor do Supabase, como manda o
  contrato.

**3.5 Plano do Supabase.** O plano grátis tem 500 MB e pausa depois de 7 dias sem uso. Com o primeiro
escritório pagante, passe para o Pro (US$ 25/mês, com backup diário).

---

## 4. Coletor no Brasil (o robô rodando sozinho)

O DJEN só responde a computadores no Brasil, então o coletor precisa rodar daqui.

| Fase | Onde | Custo/mês | Passo a passo |
|---|---|---|---|
| Agora | seu PC, com o Agendador de Tarefas do Windows | R$ 0 | já está no LEIA-ME do robô |
| Piloto pago | AWS Lambda em São Paulo, agendado 1x por dia | ~R$ 0 | eu preparo o pacote; você cria a conta AWS e cola uma chave de acesso |
| Escala (24 TRTs) | VM em São Paulo (Magalu Cloud ou AWS Lightsail) | R$ 35 a 45 | eu deixo o script de instalação pronto |
| Alternativa | dentro do próprio Supabase, em São Paulo | ~R$ 0 | depende de um teste de 5 minutos que só faço com sua autorização |

O coletor grava no banco com a **chave de serviço** do Supabase. Essa chave fica só no servidor do coletor,
como "segredo" dele, e **nunca** no código, no repositório ou no chat.

**Avisos:**

- e-mail: Resend, grátis até 3.000 por mês;
- Telegram: grátis, bom para celular;
- notificação do app: Web Push. No iPhone, só funciona com o app instalado na tela inicial.

---

## 5. Registrar no RootifyONE e nos arquivos master

Tudo pelas telas do RootifyONE, com o botão **Publicar** no fim.

1. **Catálogo:** novo app LexSuiteONE (código `lexsuite-one`, estado alpha, endereço do item 1).
2. **Serviços e planos** (`servicos/lexsuite-one.json`): cada função do app ligada a um plano. Sugestão inicial:

   | Plano | Valor | O que inclui |
   |---|---|---|
   | Essencial | R$ 490/mês | 1 TRT, carteira, painel, 3 usuários |
   | Profissional | R$ 1.490/mês | até 5 TRTs, ranking, exportação, avisos |
   | Nacional | R$ 3.990/mês | 24 TRTs, API |

   Enquanto não houver cobrança automática, você libera o plano de cada escritório à mão no RootifyONE.
3. **Interruptores** (`recursos/lexsuite-one.json`): `radar`, `carteira`, `raio-x`, `empresas`, `exportar-csv`,
   `notificacoes` e `ia`. Assim você liga e desliga cada função de qualquer escritório sem mexer no código.
4. **Feedback:** já funciona pelo módulo comum (botão de opinião em toda tela) e cai na Central de feedback do RootifyONE.

---

## 6. O app seguindo as diretrizes (regra zero: confirme o que entra na v0.1)

| # | Requisito das diretrizes | Recomendação para a v0.1 |
|---|---|---|
| 1 | Módulo comum (diretrizes, janela, cofre, AssistONE) | entra |
| 2 | Conta SolverONE (Google ou e-mail), sessão que não cai ao recarregar | entra |
| 3 | PT/EN, cabeçalho padrão (Início, Inbox, Configurações, conta), menu lateral | entra |
| 4 | `recursos-do-app.json` + interruptores do RootifyONE | entra |
| 5 | Feedback dos usuários (opinião em toda tela) | entra; pergunta do dia só para quem estiver no piloto |
| 6 | Trabalho demorado em segundo plano (`Fundo`) | entra (exportações e, depois, IA) |
| 7 | Instalar como app (PWA), atalho na tela inicial, uso sem internet (última cópia) | entra |
| 8 | Cofre de chaves de IA (chave Gemini do próprio escritório) | fase 2 |
| 9 | Anúncios | **não** (produto pago B2B) |
| 10 | `versoes.json`, `PENDENCIAS.md`, `ARQUITETURA.md`, `LICENSE`, `CREDITOS.md` | entra |
| 11 | Entrega em .zip com nome e hora padrão | entra |

---

## 7. Celular

- **iPhone:** abrir solverone.com.br/lexsuite-one no Safari → Compartilhar → **Adicionar à Tela de Início**.
  Os avisos só funcionam assim (iOS 16.4 ou mais novo).
- **Android (APK):** o PWABuilder (pwabuilder.com) empacota o app como APK.
  - Para poucos aparelhos no piloto, basta enviar o APK direto.
  - Para vender na Play Store, use uma conta de **organização com o CNPJ**. Contas pessoais novas precisam de
    12 testadores por 14 dias antes de publicar; a dispensa para empresas aparece em fontes não oficiais, então
    confirme no cadastro.

---

## 8. Do piloto ao SaaS

1. **Piloto KR Law (90 dias):**
   - coletor no seu PC;
   - painel e planilha diários;
   - uma ou duas varas;
   - métricas: cobertura, atraso do aviso, uso semanal.
2. **App v0.1 na plataforma:** login, escritório, varas monitoradas, carteira, dashboard lendo do banco.
3. **Coletor em São Paulo** (Lambda ou VM) + avisos por e-mail e Telegram.
4. **Comercial:**
   - termos de uso e política de privacidade (o agente de políticas do RootifyONE escreve o rascunho);
   - contrato de operador de dados com cada escritório;
   - planos publicados.
5. **Cobrança automática:** gateway de pagamento (Asaas, Pagar.me ou Stripe), quando houver o 3º ou 4º cliente.
6. **Novos módulos:** assistente de peças com a chave de IA do escritório, outras áreas (tributário, cível),
   outros TRTs.

---

## 9. O que eu posso fazer agora, com a sua autorização

1. **Criar o repositório `lexsuite-one`** no seu GitHub e subir a estrutura inicial: app com o dashboard, coletor,
   `.gitignore`, documentos e SQL em rascunho.
2. **Escrever o SQL** das tabelas `lex_*`, para você revisar e rodar.
3. **Registrar o app** no catálogo do RootifyONE e nos arquivos master, por pull request nos repositórios
   `rootify-one` e `solverone-dados`, para você aprovar.
4. **Testar o coletor dentro do Supabase** em São Paulo: uma função de teste de 5 minutos, removida em seguida.

Pela regra da plataforma, nada disso é criado ou publicado sem o seu "pode fazer".


## Adendo (23/Out/2026): onde fica o coletor, e o que precisa estar no Brasil

O único pedaço que precisa estar no Brasil é **quem chama o DJEN**. Os dados já moram em São Paulo
(Supabase `solverone-app`, região `sa-east-1`, confirmado) e o GitHub Pages só guarda o código da página, que
roda no navegador de quem usa. Três casas possíveis para o coletor, da mais simples à mais robusta:

1. **O navegador do usuário**: a página "O dia nos tribunais" tem o modo "Ao vivo", que pergunta ao DJEN
   direto do computador de quem abriu. Depende de o CNJ aceitar chamadas vindas de página (teste de 1 minuto,
   no Brasil). Custo zero, mas só funciona com a página aberta.
2. **O próprio Supabase**: o projeto já tem `pg_cron` ligado; a extensão `pg_net` (chamadas HTTP feitas pelo
   banco, de São Paulo) está disponível. Teste em `teste-djen-supabase.sql` (revisar, rodar no SQL Editor,
   me mandar o resultado). Se passar, o SaaS não precisa de servidor extra: um `cron.schedule` a cada 30 min
   à noite grava as publicações em `lex_publicacoes`, e o aviso (app, e-mail, Telegram) sai dali.
3. **Uma máquina pequena em São Paulo** (R$ 35 a 45/mês) rodando o robô Python, se 1 e 2 falharem.
