# LexSuiteONE — Plano de trabalho v1 (22/Out/2026)

Para: Marcelo (SolverONE). Piloto: KR Law (Leandro Rodrigues). Foco inicial: trabalhista.
Junto com este plano: a planilha de degustação (Cajamar/TRT2), o painel, o robô v0.1.0 e o relatório de pesquisa.

---

## 1. Resumo em um minuto

**O que já existe hoje (feito e testado):**

- **Degustação real** da Vara do Trabalho de Cajamar (TRT2), a vara de 1º grau com mais ações novas no TRT2. A planilha
  tem 78 ações reais contra empresas, com audiência marcada até 04/Nov, mais o raio-x da vara:
  - 20,8 ações novas por dia útil;
  - 35% terminam em acordo;
  - 64% de procedência quando há sentença;
  - 104 dias até o desfecho, na mediana.
- **Robô v0.1.0** em Python, que não usa IA nem gasta token. Ele gera a planilha, o painel e o e-mail. Fontes: DataJud,
  DJEN e a pauta pública do PJe. Já tem o modo **carteira de clientes**.
- **Pesquisa profunda** em seis frentes: fontes de dados, ética e LGPD, mercado, arquitetura, jurimetria e
  peticionamento, e os insumos (vídeo e planos das outras IAs).

**Três descobertas que mudam o rumo:**

1. **Ética da OAB.** Do jeito que foi pedido ("pegar as empresas recém-processadas e abordar"), o modelo bate em
   quatro regras:
   - o Estatuto, art. 34, IV, proíbe captar causas "com ou sem a intervenção de terceiros", discreto ou não;
   - o Código de Ética, art. 7º, proíbe a captação direta ou indireta;
   - o Provimento 205/2021, art. 6º, proíbe usar caso concreto para oferecer serviço;
   - o Tribunal de Ética da OAB-SP já tratou como captação o caso de quem identifica réus e repassa ao advogado
     (E-3.563/2008; E-2.030/99).

   Pagar "êxito" a você é o caso clássico de agenciador de causas (art. 34, III). Em 2026 a OAB foi à Justiça contra
   empresas de tecnologia que fazem essa ponte. **O risco é do escritório e também da LexSuiteONE.**
2. **Dados.** São três limitações:
   - O **DJEN só responde a computadores no Brasil**. Testei: fora daqui ele bloqueia.
   - O **DataJud** atrasa cerca de 7 semanas, não traz partes nem valor da causa e é de **uso não comercial**.
     A Portaria CNJ 374/2026 deve trazer o polo passivo pessoa jurídica com atualização diária até por volta de
     fev/2027, mas reforça a proibição de exploração comercial. Isso precisa ser confirmado no texto oficial.
   - O **valor da causa** não sai em fonte aberta sem captcha. O rito dá a faixa: ordinário é causa acima de 40 salários mínimos.
3. **Mercado.** O produto mais defensável não é "vender leads". É:
   - **monitorar a carteira de clientes do escritório**, avisando no mesmo dia que o cliente foi processado;
   - **Radar de Contingência** vendido às próprias empresas, para que monitorem os seus CNPJs e os dos fornecedores.
     A dor é real: a citação pelo Domicílio Judicial Eletrônico dá 3 dias úteis de ciência;
   - **raio-x da vara** (jurimetria);
   - **assistente de peças** com revisão humana.

**Recomendação:** seguir com a KR Law no **modo carteira + inteligência de vara**. Deixar a "abordagem de réus novos"
só para depois de um parecer formal: consulta "em tese" ao Tribunal de Ética da OAB-SP e um advogado independente,
porque o Leandro tem interesse direto no resultado. Cobrar **assinatura fixa**, nunca êxito.

---

## 2. Decisões que preciso de você (e do Leandro)

| # | Decisão | Minha recomendação |
|---|---|---|
| D1 | Como cobrar da KR Law | Assinatura/licença mensal fixa + taxa de implantação. **Nunca** % de honorários nem valor por cliente fechado (art. 34, III). |
| D2 | Para que a KR Law usa o radar | Carteira de clientes, inteligência de vara e conteúdo por setor. Abordar réus novos só com parecer de ética por escrito. |
| D3 | Nome | **"LexSuite" tem conflito**: é marca ativa de software jurídico no Uruguai (lexsuite.app, desde 2018, presente na América Latina), e lexsuite.com.br foi registrado por outra pessoa em 2025. "JudicialONE" e "AdvocacIA" não mostraram conflito (o INPI ficou fora do ar na pesquisa). Sugestão: **JudicialONE** como plataforma, com módulos "Radar Trabalhista", "Raio-x da Vara" e "AdvocacIA" (assistente de peças). Ou manter LexSuiteONE depois de uma busca no INPI. Antes de investir na marca, fazer a busca no INPI (classes 9, 42 e 45). |
| D4 | Onde o robô roda na fase 2 | Começar no **seu PC** (R$ 0). Para a KR Law: **AWS Lambda em São Paulo** (grátis no volume do piloto) ou **VM Magalu/Lightsail** (R$ 35–45/mês). A opção dentro do Supabase da plataforma (já em São Paulo) precisa de um teste de 5 minutos, que só faço com sua autorização. |
| D5 | Quais TRTs e varas no piloto | Onde a KR Law atua. Preciso da cidade e da lista de clientes (CNPJ e nome) para o modo carteira. |
| D6 | Dados de empresa (CNPJ) | Para achar o CNPJ pelo nome: base aberta da Receita (cerca de 60 GB, numa VPS) ou serviço pago. O piloto pode começar sem. |

---

## 3. Fase 1 — Degustação (entregue hoje)

**O que levar ao Leandro:**

1. **Planilha** "Radar Trabalhista — Degustação Vara do Trabalho de Cajamar (TRT2)", no Drive, com 4 abas:
   - Leads (empresas): 78 ações reais com nota e motivo;
   - Raio-x da vara;
   - Ações recentes;
   - Como usar.
2. **Painel** `painel.html`: o "sistema moderno". Abre no navegador e no celular, tem PT/EN, tema claro e escuro e filtros.
3. **Mensagem certa:** "o radar avisa no dia quando um cliente seu é processado e mostra como cada vara funciona".
   Os números do raio-x são o argumento: acordo em 35% dos casos, cerca de 78 dias até o acordo, assuntos que mais
   aparecem e fatia de terceirização.

**Roteiro de 15 minutos com o Leandro:**

1. Raio-x de Cajamar.
2. Lista de empresas (mostrar que pessoa física nunca aparece).
3. Modo carteira: pedir a lista de clientes para o teste da semana que vem.
4. Combinar as decisões D1, D2 e D5.

**Para você fazer (passo a passo no LEIA-ME do robô):**

1. Instalar o Python no seu PC (10 minutos).
2. Rodar `python lexsuite_robo.py djen --tribunal TRT2 --vara "Vara do Trabalho de Cajamar" --dias 3`.
   No Brasil, isso traz as ações **do dia** pelo DJEN ("Lista de distribuição").
3. Se der erro, rodar com `--diagnostico` e me mandar o arquivo da pasta `diagnostico`. Ele não contém senha.

Limites desta amostra, já escritos na planilha:

- a pauta mostra a ação semanas ou meses depois do ajuizamento;
- sem CNPJ não há porte;
- sem fonte aberta não há valor da causa.

---

## 4. Fase 2 — Robô ad hoc para a KR Law (2 a 4 semanas depois do "sim")

**Como funciona (sem IA na rotina):**

```
06:00  Coletor no Brasil (seu PC → depois Lambda/VM em São Paulo)
        ├─ DJEN: baixa o "caderno" do dia de cada TRT (1 arquivo por TRT/dia, sem estourar limite)
        ├─ filtra: varas do escritório + "Lista de distribuição" + 1ª publicação de processo do ano
        ├─ separa empresa × pessoa física (pessoa física é descartada)
        ├─ cruza com a carteira de clientes (nota 100 = cliente processado)
        ├─ completa a empresa pela Receita (porte, atividade, cidade) quando houver CNPJ
        └─ grava no banco (sem repetir aviso)
07:00  Entrega: planilha Google compartilhada + e-mail resumo + painel (+ Telegram, se quiserem)
Semanal: raio-x das varas pelo DataJud
```

**Monitor dos processos do escritório (pedido do Leandro, já no robô v0.3.0):**

O DJEN não tem webhook. O robô faz o papel dele: pergunta ao DJEN várias vezes à noite e avisa na hora só o que
é novo, com o prazo estimado.

```
19:15–23:15 (a cada 30 min)  busca rápida pela OAB dos advogados, pelos processos e pelos clientes
                              → aviso no Telegram/e-mail: tipo do ato, urgência, cliente, prazo estimado, link
07:00                         caderno do dia de cada TRT (rede de segurança: nada escapa)
```

- O tribunal envia até 17h e o DJEN libera a partir das 19h (dia D). A publicação conta em D+1 útil e o prazo
  começa em D+2 útil. Com o monitor, o escritório sabe na noite de D.
- Tipos reconhecidos sem IA: penhora/bloqueio, ação nova contra cliente, citação, sentença, acórdão,
  tutela/liminar, audiência (designada/redesignada/cancelada), pauta de julgamento, acordo, alvará, decisão, despacho.
- Não chega pelo DJEN: citação de empresa pelo Domicílio Judicial Eletrônico, ato sem intimação, pautas e
  atas que alguns TRTs ainda publicam só no DEJT.

**Entregáveis e aceite:**

| Item | Critério de aceite |
|---|---|
| Monitor: publicação nos processos do escritório | aviso até 1 hora depois de o DJEN liberar (noite de D) |
| Monitor: sem aviso repetido | a mesma publicação nunca chega duas vezes |
| Alerta de cliente da carteira processado | chega até D+1 útil da publicação |
| Cobertura | ≥ 90% das ações novas da vara comparando com a pauta pública |
| Precisão "é empresa" | ≥ 95% (conferência manual de 100 linhas) |
| Privacidade | zero pessoa física em planilha, painel ou e-mail |
| Operação | robô roda sozinho 10 dias úteis seguidos; falha avisa por e-mail |

**Custos de infraestrutura:**

| Opção | Custo/mês |
|---|---|
| A: seu PC | R$ 0 (precisa estar ligado às 6h) |
| B: Lambda São Paulo + Supabase grátis + e-mail Resend grátis | R$ 0 a 30 |
| B': VM em São Paulo (Magalu/Lightsail) | R$ 35 a 45 |
| Base da Receita para CNPJ por nome | + disco de cerca de 60 GB na VM |

**Preço sugerido para a KR Law** (pela pesquisa de mercado, a validar):

- piloto de 90 dias: 30 dias grátis, depois 50% do preço;
- depois, **R$ 490 a R$ 1.490/mês**, conforme o número de varas/TRTs e de usuários, mais uma implantação única.

---

## 5. Fase 3 — Serviço da plataforma (SaaS no RootifyONE)

**Desenho**, seguindo as diretrizes da SolverONE:

- **App novo** (repositório próprio, PWA em `solverone.com.br/<app>`), com o módulo comum: PT/EN, botões de Início, Inbox e Configurações no topo, menu ☰,
  AssistONE, botão de opinião (feedback), `Fundo` para trabalhos demorados, versões e entrega em .zip.
- **Conta SolverONE** (Google ou e-mail) e **papéis por escritório**: sócio, advogado, comercial e leitura.
  As regras ficam no banco (Supabase `solverone-app`, São Paulo, tabelas com RLS por escritório).
- **Coletor central** em São Paulo, que lê o DJEN uma vez para todos os clientes. Cada escritório só vê as suas varas e a sua carteira.
- **Interruptores no RootifyONE** (`recursos-do-app.json`): `radar`, `carteira`, `raio-x`, `ia`, `notificacoes`, `assistente-pecas`.
- **IA com a chave do cliente** (cofre do navegador). Atenção: a assinatura Gemini/Workspace que a KR Law paga **não
  é** uma chave de API. A chave sai do AI Studio, com faturamento ligado, porque no plano grátis o Google usa o
  conteúdo para treinar. Rotina sem IA. A IA entra só em resumo e minuta, a cerca de US$ 0,28 por mil resumos ou US$ 0,08 por minuta.
- **Celular:**
  - iPhone: PWA instalado na tela inicial (avisos só funcionam assim, iOS 16.4+);
  - Android: APK pela loja, publicado com conta de **empresa (CNPJ)**, que dispensa os 12 testadores por 14 dias;
  - e-mail e Telegram como reserva.

**Antes de abrir para outros escritórios (bloqueios):**

1. Parecer sobre o uso comercial de dados do DataJud, ou autorização do CNJ. A alternativa é usar só DJEN e pauta.
2. Termos de uso, política de privacidade, registro de tratamento e teste de legítimo interesse (LGPD), e contrato de
   operador com cada escritório.
3. Consulta ao Tribunal de Ética da OAB-SP sobre o produto. A OAB está agindo contra plataformas de "ponte".

**Regra zero:** quando formos criar o app, listo os requisitos das diretrizes que ele ainda não tem e você confirma o que entra.

---

## 6. Fase 4 — Portfólio (módulos)

| Módulo | O que faz | Dados | Risco | Quando |
|---|---|---|---|---|
| **Radar da Carteira** (escritórios) | avisa no dia que um cliente foi processado | DJEN | baixo | fase 2 |
| **Raio-x da Vara** | volume, pedidos, acordos, procedência e tempos por vara | DataJud | baixo (citar a fonte; uso comercial a validar) | já existe |
| **Radar de Contingência** (empresas) | a empresa monitora os próprios CNPJs e os de fornecedores (terceirização) | DJEN + Domicílio | baixo (não é advocacia) | fase 3 |
| **Panorama setorial** (conteúdo) | relatórios agregados ("polo logístico de Cajamar"), que trazem o cliente até o escritório | DataJud | baixo | fase 2–3 |
| **AdvocacIA** (assistente de peças) | minuta no estilo do escritório (RAG), citando **só** fontes oficiais, com verificador automático de citações e revisão humana obrigatória | acervo do escritório + tribunais | médio: já há multas por jurisprudência inventada (TST, RR 0000284-92.2024.5.06.0351, 2026) | fase 3 |
| **Pacote de protocolo** | monta a petição e os anexos; o advogado protocola no PJe | — | baixo | fase 3 |
| Download assistido de autos | um clique do advogado, na sessão dele | PJe | **alto** se for automático: TRTs proíbem robôs, e o TRT-11 bloqueia acima de 2 mil consultas/mês e proíbe entregar senha ou certificado a terceiros | fase 4 |
| Histórico por magistrado | consulta interna e descritiva, **sem ranking** | sentenças | médio (reputação; a Res. CNJ 615/2025 veda ranquear pessoas no Judiciário) | fase 4 |
| Outras áreas | tributário (execuções fiscais), cível (TJSP), penal | DataJud/DJEN | varia | fase 4 |

**Peticionamento 100% automático: não recomendo.** Não há canal oficial para advogados (o MNI não é oferecido a
advogados no TRT-3), os tribunais proíbem robôs e guardar o certificado do advogado viola as regras dos TRTs e as da SolverONE.

---

## 7. Cronograma sugerido

| Semana | O quê |
|---|---|
| 0 (agora) | Degustação entregue. Reunião com o Leandro: D1, D2 e D5. Você roda o DJEN no seu PC. |
| 1 | Carteira da KR Law no robô; ajuste de varas e TRTs; e-mail diário ligado. |
| 2–3 | Coletor em São Paulo (Lambda ou VM) + banco + planilha compartilhada; 10 dias de operação "sombra" (alertas internos, sem contato externo). |
| 4 | Avaliação do piloto pelas métricas da seção 4; decisão sobre o SaaS; consulta ao Tribunal de Ética e parecer sobre o DataJud. |
| 5–10 | App na plataforma (fase 3), começando pelo Radar da Carteira + Raio-x. |
| depois | AdvocacIA, Radar de Contingência para empresas, outras áreas. |

---

## 8. Riscos principais

| Risco | Como tratamos |
|---|---|
| Captação de clientela (OAB) | modo carteira por padrão; sem lista de "réus para abordar" sem parecer; preço fixo; telas com "Uso responsável" |
| Uso comercial do DataJud | parecer ou autorização do CNJ; plano B só com DJEN e pauta |
| DJEN bloqueia fora do Brasil ou muda o formato | coletor em São Paulo; modo `--diagnostico`; pauta como segunda fonte |
| Trabalhador exposto (lista suja) | pessoa física descartada na coleta; nenhuma busca por nome de reclamante |
| Nome com conflito de marca | busca no INPI antes de investir (D3) |
| Dependência de um PC ligado | migrar para Lambda/VM na semana 2–3 |
| IA inventar jurisprudência | citações só de fontes oficiais + verificador + revisão humana |

---

## 9. Pendências e observações

- O link do "INSIGHT do YouTube" na sua mensagem aponta para o mesmo documento da conversa com o Leandro. Pode mandar o link certo?
- O vídeo 2 (aula do Dr. Douglas Vilar, 02/10/2026) não teve a transcrição acessível daqui: o YouTube bloqueou. O
  resumo saiu da descrição, dos capítulos e dos slides. Se quiser o trecho de 29:35 literal, abra "Mostrar transcrição"
  no YouTube e cole de 29:35 a 31:35.
- Sobre os planos das outras IAs: o do Grok foi o mais sólido. Os do DeepSeek e do Perplexity erram ao dizer que o
  DataJud traz o réu no dia. O do Gemini sugere práticas de captação disfarçada, que devem ser descartadas.

*Este plano não é parecer jurídico. As conclusões de ética e LGPD precisam ser validadas por advogado.*
