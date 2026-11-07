# Integrações do mercado: sistemas de gestão jurídica no Brasil

Levantamento feito em 07-nov-2026 por busca na web. Regra: cada afirmação tem uma URL; o que não foi achado está escrito "não encontrado". Muitas páginas de fornecedores são marketing e podem estar desatualizadas; fontes de terceiros (B2BStack, SoftwareFinder, Reclame Aqui, Glama) estão marcadas como **[terceiro]** e valem menos. Preços de lista mudam; confirmar antes de decidir.

## Tabela-resumo

| Sistema | Fornecedor | API pública | Webhooks | Zapier/Make | Monitora publicações | Preço de referência |
|---|---|---|---|---|---|---|
| Astrea | Aurum | Não encontrada (site oficial não cita; Reclame Aqui [terceiro] diz que não há) | Não encontrado | Não encontrado | Sim (OAB / nº do processo) | Smart: a partir de R$ 439/mês (mensal); Light grátis 1 ano |
| Themis | Aurum | Sim, "API aberta" citada pela Aurum; doc técnica não encontrada | Não encontrado | Não encontrado | Não confirmado | Não encontrado (demonstração) |
| ADVBOX | ADVBOX | Sim, REST, doc em api.softwareadvbox.com.br/docs; acesso aprovado pelo fornecedor | Não encontrado | Não encontrado | Sim, endpoint "Publicações" na API | API para escritórios a partir de R$ 280/mês; parceiros a partir de R$ 3.500/mês |
| Projuris ADV | Projuris | Sim, REST; planos Premium ou contratação adicional; 480 req/min | Citado só por terceiro (Glama); oficial não encontrado | Não nativo encontrado | Sim (monitoramento e busca de intimações) | Solo a partir de R$ 79/mês; Compartilhado a partir de R$ 349/mês |
| SAJ ADV | Softplan | Sim, REST (Migalhas); doc em docs.sajadv.com.br (citada pela Projuris, não aberta por mim) | Não encontrado | Não encontrado | Não confirmado | Não encontrado |
| CPJ-3C | Preâmbulo Tech | "Conexão via API" citada; doc pública não encontrada | Não encontrado | Não encontrado | Sim (diários oficiais e DJEN) | Não divulgado (demonstração) |
| EasyJur OS | EasyJur | Sim, REST, OpenAPI 3.1, OAuth 2.0, 200+ endpoints | Sim | Sim (Zapier, Make, n8n) | Sim (captura de intimações e andamentos) | OS a partir de R$ 229/mês; API como add-on de R$ 70 a R$ 799/mês |
| Legal One | Thomson Reuters | Sim, REST/Swagger no portal de desenvolvedores | Não encontrado | Não encontrado | Sim (módulo DJE / Portal do Advogado) | Não divulgado (demonstração) |
| Jusbrasil Soluções | Jusbrasil | Sim (API de dados processuais e intimações) | Sim (entrega de diários via webhook) | Não encontrado | Sim (é um monitor; concorre) | API a partir de R$ 1.000/mês |
| Kurier Meridio | Kurier | Não encontrado | Não encontrado | Não encontrado | Não confirmado | Não encontrado |
| Integra | Promad | Não encontrado | Não encontrado | Não encontrado | Sim (módulo Publicações, com ChatGPT) | Não encontrado |
| Advwin | TWT Info | Não encontrado | Não encontrado | Não encontrado | Não encontrado | Não encontrado |
| TORIX (provável "Torex") | Não informado no site | Não encontrada | Não encontrado | Não encontrado | Sim (DJEN por OAB) | R$ 49,99 / 99,99 / 149 por mês |
| Lawsystem, Juris | n/d | Não encontrado | Não encontrado | Não encontrado | Não encontrado | Não encontrado |

---

## O que é "Torex"

Não achei nenhum sistema jurídico chamado "Torex" (a busca por "Torex sistema jurídico advogados" só trouxe a mineradora canadense Torex Gold, sem relação com software jurídico). O nome mais parecido que existe é **TORIX**, "Sistema Jurídico" para advogados: https://www.torix.com.br/ . O site não informa razão social, CNPJ nem cidade (contato por WhatsApp). Faz: processos, prazos, agenda, intimações do DJEN por OAB, portal do cliente, financeiro, gerador de documentos e "ATA TORIX" (transcrição e ata de audiência por IA). Planos: Solo R$ 49,99, Escritório R$ 99,99, Banca R$ 149 por mês, 14 dias grátis. API pública e webhooks: não mencionados; única integração citada é Google Agenda. Hipótese: o anúncio visto no Instagram era do TORIX. Não confirmado; peça ao dono o print do anúncio. Nenhum "Torex Jurídico" foi encontrado.

---

## Fichas

### Astrea (Aurum)
- **Fornecedor:** Aurum. **Público:** autônomos e escritórios pequenos e médios; acima de 30 advogados a Aurum indica o Themis.
- **Faz:** gestão de processos, prazos, tarefas, clientes e finanças em nuvem, com IA (agente Jux para jurisprudência e peças).
- **API pública:** não encontrada. A página oficial não cita API; um comparativo da Aurum lista só Google Drive, Google Calendar, Apple Calendar e Outlook. Reclame Aqui **[terceiro]** afirma que não há API aberta.
- **Webhooks / Zapier / MCP:** não encontrados. **Planilha:** não encontrado.
- **Monitora publicações:** sim, por OAB ou número do processo; transforma publicações em atividades. Smart inclui 500 processos monitorados e 3 nomes para captura.
- **Preço:** Smart a partir de R$ 439/mês no mensal; Light grátis por 1 ano; promoção anual até 50% (Novembro Black 2026). Valores divergem entre páginas.
- **Fontes:** https://www.aurum.com.br/astrea/ ; https://www.aurum.com.br/astrea/planos-e-precos/ ; https://www.aurum.com.br/blog/aurum-e-clieent-crm/ ; https://www.reclameaqui.com.br/aurum/decepcao-com-o-astrea-promessa-comercial-nao-cumpre-a-realidade-suporte-ruim-e-limitacoes-graves-na-plataforma_ZLyD4iACrsk48yYh/

### Themis (Aurum)
- **Público:** departamentos jurídicos e escritórios grandes. **Faz:** gestão jurídica corporativa, contratos, eSocial.
- **API:** a Aurum descreve "API aberta" que consulta e altera cadastros; documentação técnica, autenticação e limites: não encontrados.
- **Webhooks, Zapier, MCP, planilha, monitoramento, preço:** não encontrados (acesso por demonstração).
- **Fontes:** https://www.aurum.com.br/themis/ ; https://www.aurum.com.br/themis-para-departamento-juridico/

### ADVBOX
- **Fornecedor:** ADVBOX. **Público:** escritórios (pequenos a médios), segundo o foco do site; sem classificação oficial lida.
- **API:** REST, base `https://app.advbox.com.br/api/v1`, 22 endpoints em 7 grupos: clientes, processos, tarefas, publicações, financeiro, documentos, configurações. Autenticação por Bearer Token emitido pela ADVBOX a parceiros/escritórios aprovados. Limites: GET 30/min; POST 500/dia por rota; PUT 500/dia.
- **Webhooks:** não encontrados. **Zapier/Make/Pluga:** não encontrados. **MCP:** não encontrado. **Planilha:** não encontrado.
- **Monitora publicações:** a API tem o grupo "Publicações" (movimentações e andamentos).
- **Preço da API:** escritórios a partir de R$ 280/mês (consulta de clientes, processos, intimações, movimentações; BI e low-code); parceiros homologados a partir de R$ 3.500/mês. Preço do sistema em si: não encontrado.
- **Fontes:** https://advbox.com.br/api ; https://api.softwareadvbox.com.br/docs ; https://api.softwareadvbox.com.br/docs/autenticacao

### Projuris ADV (Projuris; "ProJuris" e "Projuris ADV" são o mesmo produto de escritórios)
- **Público:** ADV Start para 1 a 5 usuários; Projuris ADV para 6+ usuários ou várias unidades. (Projuris Empresas é a linha para departamentos jurídicos.)
- **API:** REST. Disponível nos planos Premium ou como serviço adicional; limite de 480 requisições por minuto; endpoints documentados em docs.sajadv.com.br e páginas Confluence (processos, pessoas, tarefas, arquivos etc.); há endpoint para token de usuário. O blog recomenda ter um desenvolvedor. A página comercial é contraditória sobre qual plano inclui API.
- **Webhooks:** o blog oficial não cita; um conector de terceiros **[terceiro]** menciona criação de webhooks por API. Confirmar.
- **Zapier/Make:** conector nativo não encontrado; há demanda de freelancer usando Make com Projuris ADV (workana, indício apenas).
- **MCP:** existe um servidor MCP de terceiros listado no Glama **[terceiro]**; não é oficial.
- **Monitora publicações:** sim (monitoramento de processos e busca de intimações). **Planilha:** não encontrado.
- **Preço:** Solo a partir de R$ 79/mês; Compartilhado a partir de R$ 349/mês; ADV completo sob consulta; API a partir de R$ 100/mês segundo diretório **[terceiro]**.
- **Fontes:** https://www.projuris.com.br/adv/ ; https://www.projuris.com.br/blog/como-integrar-outras-plataformas-no-projuris-adv-software-juridico/ ; https://glama.ai/mcp/servers/mcp-dir/projuris-mcp/tree ; https://www.getapp.ca/software/2036755/projuris

### SAJ ADV (Softplan)
- **Fornecedor:** Softplan (spin-off de 2013). **Público/preço/webhooks/Zapier/monitoramento:** não encontrados.
- **API:** Migalhas diz que permite extração por API REST; a Projuris cita a documentação em docs.sajadv.com.br. Não consegui abrir essa documentação; confirmar.
- **Fontes:** https://www.migalhas.com.br/quentes/352073/como-integrar-diferentes-plataformas-ao-seu-sistema-de-gestao ; https://www.baguete.com.br/noticias/softplan-tem-sistema-para-advogados

### CPJ-3C (Preâmbulo Tech)
- **Público:** grandes escritórios e departamentos jurídicos. **Faz:** processos, prazos, publicações e intimações, workflow, financeiro, protocolo de peças, portal do cliente, IA para classificar publicações.
- **API:** "conexão via API" citada; documentação pública não encontrada. Integrações listadas: LawVision, Cria.AI, Contraktor, CPJ-Cobrança, Preâmbulo Pay, Acordo Fechado.
- **Monitora publicações:** sim, diários oficiais e DJEN com comparação entre fontes (competidor direto). **Preço:** não divulgado.
- **Fonte:** https://preambulo.com.br/cpj-3c/

### EasyJur
- **Público:** pequeno ao grande (planos de 2 a 30+ usuários), e departamentos jurídicos.
- **API:** REST, 200+ endpoints, OpenAPI 3.1, OAuth 2.0 com escopos, SDKs Python/Node/PHP, playground em developers.easyjur.com. Limite 100 mil req/mês no Professional, ilimitado no Enterprise.
- **Webhooks:** sim, em tempo real com retry. **Zapier/Make/n8n:** sim.
- **MCP/IA:** sim, EasyJur Work conecta via MCP a Claude, ChatGPT, Gemini, Gmail, Drive, Slack, Notion; agentes de IA vendidos por execução.
- **Monitora publicações:** captura intimações e andamentos (PJe, e-SAJ, Projudi, e-Proc, STJ, STF, TST, INSS) com cálculo de prazo. **Planilha:** não encontrado.
- **Preço:** OS Start R$ 229/mês (2 usuários), Premium R$ 499 (5), Standard R$ 990 (10), Growth R$ 2.290 (15), Growth+ R$ 3.790 (30+); Work a partir de R$ 720/mês; API add-on R$ 70 a R$ 799/mês; teste de 7 dias.
- **Fontes:** https://easyjur.com/easyjur-os-api-e-integracoes/ ; https://easyjur.com/planos-e-precos ; https://easyjur.com/easyjur-os-integracoes/

### Legal One (Thomson Reuters)
- **Público:** escritórios (por estágio) e departamentos jurídicos (Corporate e Firms).
- **API:** REST com Swagger no portal de desenvolvedores para "Legal One Corporate Brazil" e "Firms Brazil". Autenticação e campos obrigatórios não descritos na página; webhooks não mencionados.
- **Monitora publicações:** add-on que liga o Legal One ao DJE e ao Portal do Advogado (white paper). **Preço:** não divulgado. Zapier/MCP: não encontrados.
- **Fontes:** https://developerportal.thomsonreuters.com/node/270 ; https://developerportal.thomsonreuters.com/node/271 ; https://www.thomsonreuters.com.br/content/dam/ewp-m/documents/brazil/pt/pdf/white-papers/ppc-legal-one-dje-5846949.pdf ; https://www.thomsonreuters.com.br/pt/juridico/legal-one.html
- **Legal Tracker:** é o produto global de gestão de despesas jurídicas da TR; há API de matters no portal global (https://lawnext.com/2024/04/thomson-reuters-launches-developer-portal-giving-access-to-over-100-apis-for-legal-tax-risk-and-fraud.html). Uso no Brasil: não encontrado.

### Jusbrasil (monitoramento e API)
- **Faz:** Jus IA Monitora é gratuito, busca no DJEN por OAB e avisa por e-mail (uma OAB por conta); Acompanhamento de processos é pago; Jusbrasil Soluções vende API.
- **API:** consulta processual (CPF, CNPJ, nome, CNJ), monitoramento de movimentações e novas distribuições, busca por OAB, API de intimações, 550+ diários com **entrega por webhook**; autenticação não descrita na página (remete à doc e a sandbox).
- **Preço API:** Legal e Risco a partir de R$ 1.000/mês (mínimo + cobrança por chamada). Zapier/MCP: não encontrados.
- **Relevância:** é concorrente de monitoramento e também possível fonte de dados.
- **Fontes:** https://conteudo.jusbrasil.com.br/api ; https://ia.jusbrasil.com.br/jusia-monitora ; https://suporte.jusbrasil.com.br/hc/pt-br/articles/7820826460308-Qual-a-diferen%C3%A7a-entre-o-Jus-IA-Monitora-Monitoramento-de-OAB-e-o-Acompanhamento-de-Processos

### Kurier Meridio
- Fornecedor Kurier, fundada em 1994 **[terceiro]**, site informado por diretório: https://kuriertecnologia.com.br/ (não verificado). API, webhooks, Zapier, preço, monitoramento: não encontrados. Fontes: https://www.b2bstack.com.br/product/kurier-meridio ; https://www.krowdbase.com/software/kurier-meridio

### Integra (Promad)
- Integrou ChatGPT ao módulo de Publicações em nov/2024. API, preço, Zapier: não encontrados. Fonte: https://www.em.com.br/mundo-corporativo/2024/11/6986906-promad-apresenta-integracao-com-ia-dentro-do-software-de-gestao-juridica.html

### Advwin (TWT Info)
- Versão jurídica corporativa para departamentos jurídicos. API: não encontrada (SoftwareFinder diz que o fornecedor não especifica). Fontes: https://www.migalhas.com.br/quentes/141851/twt-info-inova-com-software-empresarial-juridico ; https://www.b2bstack.com.br/product/advwin-juridico

### Lawsystem, Juris, Promad (além do Integra)
- Nenhuma fonte encontrada. Não incluir sem nova busca.

### Outro sistema que apareceu: TORIX
- Ver seção "O que é Torex" acima.

### Fonte pública de publicações: DJEN
- O DJEN é a fonte oficial de publicações desde a Resolução CNJ 569/2024 (segundo o Jusbrasil e o TJES). Portal público: https://comunica.pje.jus.br/ (citado pelo CNJ, via busca). Um dataset de terceiros diz que os dados vêm de `comunicaapi.pje.jus.br/api/v1/caderno`: https://huggingface.co/datasets/Symmetris-labs/djen-comunicacoes . Documentação oficial da API: não consegui abrir (403). O próprio Torix, o CPJ-3C e o Astrea já leem o DJEN, então "monitorar o DJEN" sozinho não diferencia o LexSuiteONE.
- Alternativa comercial de API processual com webhook: Judit (material do próprio fornecedor): https://judit.io/blog/apis-dados-juridicos-integracoes/webhooks-monitoramento-processual-alertas-tempo-real-api/

---

## Como o LexSuiteONE se encaixa

O que os sistemas acima já fazem bem é receber publicações de um processo que o escritório já tem. Nenhum dos que li promete o que o LexSuiteONE faz: achar ação nova contra uma empresa e entregar como oportunidade antes de o escritório ser contratado. Esse é o espaço livre, e é inteligência que se soma ao sistema, não substitui.

Melhores pontos de partida por API documentada: **EasyJur** (REST, OAuth, webhooks, Zapier/Make/n8n, MCP), **ADVBOX** (REST com Bearer Token, doc aberta, com limites baixos de escrita) e **Projuris ADV** (REST, mas exige plano Premium ou contratação). **Legal One** tem Swagger no portal da Thomson Reuters, porém sem detalhes públicos de autenticação. Themis e CPJ-3C dizem ter API, mas não achei documentação aberta; exigem contato comercial.

Astrea, o mais citado, não tem API pública que eu tenha encontrado. Para ele, e para Kurier, Integra, Advwin e SAJ ADV (doc não verificada), a entrega tem de funcionar sem API: um arquivo CSV importável, um e-mail diário com a lista e um link para baixar. Nada disso depende de aceite do fornecedor.

Quanto à escrita: a API do ADVBOX limita POST a 500 por dia por rota e a do Projuris a 480 requisições por minuto. Isso basta para criar dezenas de oportunidades por dia por escritório, mas não para despejar o catálogo inteiro. Por isso o envio deve ser por lotes pequenos e idempotentes, e deve existir um modo "só leitura do catálogo".

Formato de webhook de saída que cobre a maioria: um POST JSON por oportunidade, com identificador estável, número CNJ, tribunal, data da publicação, classe/assunto, polo ativo e passivo, CNPJ e razão social da empresa ré, resumo curto, link para o catálogo e versão do esquema. Assinatura HMAC no cabeçalho e novas tentativas automáticas, como o EasyJur faz. Esse mesmo JSON entra em Zapier, Make, n8n e Pluga sem código, que é o caminho para sistemas sem API própria.

Planilha como plano B universal: CSV em UTF-8 com as mesmas colunas do webhook, separador ponto e vírgula, datas em dd/mm/aaaa. A importação de planilha nos sistemas não foi confirmada nas páginas que li (nenhuma fala disso), então cada importador precisa ser testado. Para Zapier/Make, o app do LexSuiteONE deve oferecer gatilho "nova oportunidade" e ação opcional "marcar como contatada".

Riscos a decidir com o dono: (1) Jusbrasil, CPJ-3C, EasyJur e Astrea já monitoram publicações, então o discurso comercial deve falar de "ações novas contra empresas" e não de "monitorar diário"; (2) o dono precisa de acordo comercial ou conta de cliente para obter token do ADVBOX, do Projuris e do Legal One; (3) dados de partes são pessoais, o que pede cuidado com LGPD; (4) integrar via MCP só vale para EasyJur, único com MCP oficial achado.

Próximo passo sugerido: pedir sandbox ao EasyJur e ao ADVBOX, solicitar a documentação do Themis e CPJ-3C, e definir o JSON e o CSV acima antes de qualquer conector.
