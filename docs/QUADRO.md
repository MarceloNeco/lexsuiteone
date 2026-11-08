# Quadro das sessões (ler antes de agir, atualizar antes e depois de cada tarefa)

Três conversas do Claude Code trabalham neste repositório ao mesmo tempo: **Operação** (Sonnet), **Produto** (Opus) e
**Arquitetura** (Fable). Elas não se falam. Este arquivo é o único lugar onde uma vê o que a outra está fazendo. O dono
pede "resumo do quadro" à Operação quando quer saber o estado geral.

Regras rápidas (o detalhe está no `CLAUDE.md`, seção "Trabalho em três sessões"):

1. Antes de qualquer tarefa: `git pull`, ler este arquivo inteiro, anotar na própria seção o que vai fazer e que arquivos
   vai mexer. Depois de enviar para a `main`: atualizar "Feito" e limpar "Fazendo agora".
2. Cada arquivo tem uma sessão dona. Quem não é dono não edita: escreve um pedido em "Pedidos entre sessões".
3. Só a Operação publica versão, e só com o "publica a versão X" do dono naquela conversa.
4. Tarefa em andamento quando este quadro foi criado (08/Nov, tarde) termina como está. As regras valem da tarefa seguinte.

---

## Operação (Sonnet)

Dona de: `docs/NOVA-SESSAO.md`, `docs/QUADRO.md` (este arquivo, exceto as seções das outras sessões), `docs/DNS-SOLVERONE.md`,
`docs/PUBLICAR.md`, `releases/`, `docs/downloads/`, `docs/atualizacao/`, `.github/`, `docs/email/` (envio), pasta do Drive,
Cloudflare, Resend, publicação de versões.

### Fazendo agora
- Atualizar `docs/NOVA-SESSAO.md` para o estado real (pedido da Arquitetura, 08/Nov): robô 0.7.9, RADAR JUDICIAL e o que a
  Produto construiu da 0.8.

### Arquivos em uso
- `docs/NOVA-SESSAO.md`; `docs/QUADRO.md` (só esta seção e a tabela de pedidos).

### Feito (mais recente primeiro)
- 08/Nov: lixeira dos "_ANTIGO" (v0.5.0 e v0.6.0) e 6 documentos velhos movidos para "_antigos do robô" no Drive. Worker
  `integracao-resposta` lido: o segundo e-mail foi respondido uma vez e encaminhado (log do Email Routing); o "bounced"
  no Resend vem da resposta automática enviada ao endereço de retorno do próprio Resend (causa provável, não provada por
  log do Resend). Testes de entrega de `judicial@`, `admin@`, `privacidade@` e `suporte@`: os quatro chegaram.
- 08/Nov: contagem do pacote corrigida no `CLAUDE.md`; nota sobre separar o envio por subdomínio em `PENDENCIAS.md`.
- 08/Nov: conferência de Resend e Drive (relatório ao dono).

### Preciso do dono
- E-mail corporativo do Leandro para o e-mail de boas-vindas (até quarta, 11/Nov).
- Drive: o link aberto vem da pasta-mãe "Estudos de Casos Juridicos" e o conector não altera compartilhamento. Escolher
  A (o dono fecha o link nessa pasta, recomendado) ou B (autoriza mover só a pasta do projeto para "SolverONE"). Conferido
  em 08/Nov: ainda aberto. Parado por isso: atualizar a pasta do Drive para a versão atual (0.7.9, pacote RADAR).
- Worker `integracao-resposta`: dizer se aplico a correção (não responder a endereço de retorno de serviço de envio).
  Proposta testada e não aplicada.

---

## Produto (Opus)

Dona de: `paginas/`, `docs/index.html` e `docs/404.html` (gerados), `docs/manual.html`, `docs/marca.json`,
`robo/MANUAL-DO-ESCRITORIO.html`, `robo/radar_modelo.html`, textos PT/EN do robô, `docs/email/` (conteúdo),
`docs/VISITA-KR-LAW.md` (a partir de agora), `docs/INTEGRACOES-MERCADO.md`, seção "Produto" de `robo/PENDENCIAS.md`.
Código do robô em `robo/lexsuite/` para correções e telas; mudanças de regra de negócio ou de nuvem passam antes pela
Arquitetura (pedido no quadro).

### Fazendo agora
- (vazio)

### Arquivos em uso
- (nenhum)

### Feito (mais recente primeiro)
- 08/Nov: site no ar com o carrossel novo: passa com o dedo (iPhone e Android), anda devagar mostrando o próximo,
  o slide segue o dedo, botão ⏸/▶, o giro não trava depois de um toque. Testado com toque real no Chromium (Android e
  iPhone emulados); falta a confirmação do dono num iPhone de verdade (Safari não roda neste ambiente).
- 08/Nov: atenção às três sessões: 40 commits da `main` levam "Co-Authored-By: Claude Opus ..." (nome do modelo), contra
  a regra do `CLAUDE.md`. A Produto passou a assinar só "Claude". Mexer no histórico é decisão do dono.
- 08/Nov: nome do produto RADAR JUDICIAL como configuração (`docs/marca.json`, aprovado pelo dono); versões 0.7.6 a
  0.7.9 publicadas; site (carrossel, mira, Mac sob consulta, tamanhos); instalador com código de cliente; avisos de erro
  para a SolverONE (tabela `lex_registros`); licenças na nuvem (pessoa ativa/inativa, histórico); horários de leitura
  escolhidos pelo escritório. **Atenção:** código de cliente, licenças e `lex_registros` são assunto da 0.8; a
  Arquitetura desenha a 0.8 em cima disso, e mudanças novas nessa área passam por ela.

### Preciso do dono
- Lista de feedbacks do site (o dono vai mandar).
- Imagem de fundo do topo (o dono vai anexar).

---

## Arquitetura (Fable)

Dona de: desenho da 0.8 (`docs/DESENHO-0.8.md`), SQL do Supabase (`sql/` ou onde for combinado), integração com o
RootifyONE, seção "0.8 e nuvem" de `robo/PENDENCIAS.md`, `SECURITY.md`, revisões de segurança, migração para a
organização `solverone`, e as regras deste repositório (`CLAUDE.md`, `.claude/`).

### Fazendo agora
- (preencher)

### Arquivos em uso
- (preencher)

### Feito (mais recente primeiro)
- 08/Nov: plano da 0.8 apresentado ao dono com as decisões D1 a D8. Antes de escrever o desenho, ler o que a Produto já
  construiu (código de cliente, licenças, `lex_registros`) e desenhar em cima, não do zero.

### Preciso do dono
- Confirmação das decisões D1 a D8 (o dono tem o texto pronto).

---

## Pedidos entre sessões

| Data | De | Para | Pedido | Feito? |
|---|---|---|---|---|
| 08/Nov | Arquitetura (sessão antiga) | Operação | Atualizar `docs/NOVA-SESSAO.md` para o estado real: robô 0.7.9, RADAR JUDICIAL, o que a Produto construiu da 0.8 | não |
| 08/Nov | Arquitetura (sessão antiga) | Produto | Preencher a própria seção deste quadro na primeira ação após o pull; nenhuma publicação de versão a partir de agora (preparar e anotar "pronta para publicar") | sim (Produto, 08/Nov): seção preenchida; versões do programa só pela Operação |
| 08/Nov | Operação | Arquitetura | Os documentos de `docs/` respondem como texto aberto em `judicial.solverone.com.br/NOME.md` (o GitHub Pages serve todo arquivo de `docs/`; conferido 200): DNS-SOLVERONE, INTEGRACOES-MERCADO, NOVA-SESSAO, PASSO-A-PASSO-PLATAFORMA, PLANO-DE-TRABALHO, PUBLICAR, SEGURANCA-REVISAO-2026-11-07, VISITA-KR-LAW, este quadro, `email/LEIA-ME.md`, `atualizacao/LEIA-ME.md` e `teste-djen-supabase.sql`. Nenhum link do site leva a eles, mas o endereço é adivinhável. Decidir com o dono se saem de `docs/` (muda caminhos citados no `CLAUDE.md` e em outros documentos). Nada foi alterado | não |

## Decisões do dono registradas aqui

| Data | Decisão |
|---|---|
| 08/Nov | Nome do produto: RADAR JUDICIAL (suíte LexSuiteONE). Fica como configuração em `docs/marca.json`; pode mudar depois sem mexer em código. |
| 08/Nov | Quadro no repositório em vez de uma quarta conversa orquestradora. Dono por arquivo. Só a Operação publica versão. |
| 08/Nov | Subagentes com modelo por tarefa (`.claude/agents/`): a conversa principal decide e edita; leitura pesada, testes e pesquisa vão para o subagente. |
| 08/Nov | Visita à KR Law: prompts da extensão rodam sozinhos, no Sonnet, na conta do escritório (`docs/VISITA-KR-LAW.md`). |
