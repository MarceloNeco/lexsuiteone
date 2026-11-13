# Visita à KR Law (13/Nov/2026): resumo por sistema e caminhos de integração com o RADAR JUDICIAL

Arquitetura, 13/Nov. Fontes: os dois relatórios desta pasta (PJe TRT2, prompt 1A; Astrea, prompt 3), feitos pela extensão Claude in
Chrome na sessão logada do Leandro, só leitura. **Desenho, sem código; nada é implementado sem o "pode" do dono (regra zero).**
Os prints citados (TELA NN) estão nos `.zip` do dono, fora deste repositório (ver `LEIA-ME.md`).

## 1. PJe do TRT da 2ª Região (1º grau, painel do advogado)

**Caminho até cada tela.** `trt2.jus.br` → atalho "PJe" → página "Processo Judicial Eletrônico" → "Acesso ao PJe de 1º grau"
(`pje.trt2.jus.br/primeirograu/login.seam`, nova aba) → login **"Entrar com PDPJ"** → painel `/pjekz/painel/usuario-externo`
(cartões Acervo Geral 68, Meus Expedientes 7, Arquivados 140) → Acervo Geral (abas por foro, filtros por classe, fase, parte) →
busca pelo número CNJ (campo do painel, vira filtro) → clique no número abre **nova janela** `/pjekz/processo/<id interno>/detalhe`
→ cabeçalho (classe, número, vara, **valor da causa**, distribuído, autuado) → clique no número abre "Dados do processo" (polo ativo
e passivo, com CNPJ, endereço e e-mail cadastrados) → linha do tempo (172 documentos, ordem invertível, filtros) → menu ☰ (baixar
processo completo, por instância, expedientes, cálculos, peticionar…). Intimações: painel → Meus Expedientes.

**Sem login.** Só a consulta pública (`/consultaprocessual`, Consulta Cidadão, pautas), não testada na visita. **Com login.**
Tudo acima: os processos em que o advogado atua, documentos, expedientes, downloads; "Consulta Processos de Terceiros" existe no menu.

**Onde entram certificado e token.** Só no login: PDPJ com PJeOffice (certificado A1/A3) ou, oculto, o login antigo por
certificado/Shodo. Depois disso a sessão é por cookie; durou mais de 11 minutos e **caiu ao abrir a tela de login com a sessão
ativa** (erro SJT-004). Nada de certificado dentro das telas.

**O que dá para ler e exportar.** Valor da causa, data de distribuição e autuação, vara, assuntos, prioridade, justiça gratuita;
polo passivo com razão social, **CNPJ, endereço e e-mail da empresa** (quando alguém cadastrou); petição inicial em HTML com texto
nos processos antigos (endereço da ré no 1º parágrafo, frase varia por advogado) e em **PDF dentro de iframe** nos novos (texto não
sai pela página); expedientes da notificação (meio: Correios, datas, prazo, rastreio); assinaturas e validação por QR. Downloads:
"Baixar processo completo" **começa sem confirmação** e gera o arquivo no navegador (blob); download individual pelo ícone do
documento. No processo de referência, o RADAR recebeu: valor 105.000,00, data 11/07/2016, e-mail e dois endereços da ré; telefone,
site e sócio: não constam.

**Limites e riscos.** (1) **Dado de pessoa física em toda tela**: reclamante com CPF e endereço, advogados com CPF e e-mail; o
RADAR nunca pode guardar isso (CLAUDE.md, termos seção 4), e os prints mostram tudo. (2) Advogado só vê os processos em que atua;
processos de terceiros têm acesso limitado e **bloqueio por excesso** (hipótese registrada: TRT6 bloqueia acima de 1.500 em 30 dias).
(3) Abrir um expediente pode **registrar ciência** e disparar prazo. (4) Download pesado acidental. (5) Termos do PDPJ e do PJe:
a credencial é pessoal; automação com a credencial do advogado é responsabilidade dele (termos 1.0, seção 5). (6) Fase processual
não tem rótulo; o id interno do processo só se descobre pela lista.

## 2. Astrea (Aurum), gestão do escritório

**Caminho até cada tela.** `astrea.net.br`, aplicativo de página única (rotas após `#`): Área de trabalho · Gestão kanban · Agenda
· Workflows · **Contatos** · Atendimentos · **Processos e casos** · **Publicações** · Financeiro · Peças e Jurisprudência (IA JUX) ·
Documentos · Indicadores. Barra: Adicionar (+) · Resultados de buscas · Administração (Escritório, Equipe, Acesso, Publicações,
Modelos, **Integrações**, Certificado Digital, Segurança) · Meu plano.

**Sem login.** Nada: é um serviço por assinatura. **Com login.** Tudo, conforme o perfil do usuário.

**Onde entram certificado e token.** Administração → Certificado Digital (peticionar) e **Intimações eletrônicas** (o Astrea guarda o
login do advogado em cada tribunal para capturar intimações; as três estavam com erro no dia). Nada disso toca o RADAR.

**O que dá para ler e exportar.** Saída: "Exportar os dados do Astrea" (arquivo único, Excel, link por e-mail); Contatos → exportar,
extrair e-mails, fichas; Processos e Financeiro em Excel; Publicações → exportar. Entrada: **não há importação por planilha, API nem
webhook**; "Integrações" só tem WhatsApp (desligado); boletos via Asaas; "Migração de dados" é serviço pago da Aurum. Entrada
automática que existe: busca de processo por número CNJ e **busca em lote pela OAB** (170 de 1000 créditos), e as publicações, que
já vêm do **DJEN** (a mesma fonte do RADAR). Processo tem Valor da causa, Distribuído em, Juízo, Ação, Objeto; o contato pessoa
jurídica tem Empresa (único obrigatório), Nome fantasia, CNPJ, telefones com tipo (inclusive WhatsApp), e-mails, sites, endereços,
etiquetas, Comentários e, só com Perfil = Cliente, **"Origem do cliente"**. Duplicado é avisado por CNPJ e mesclado à mão.

**Limites e riscos.** (1) Sem porta de entrada: tudo é digitado (pessoa ou extensão na sessão do usuário). (2) Termos de uso do
Astrea sobre automação na interface: não lidos; perguntar à Aurum. (3) Plano: 1.000 processos, 10 usuários, 5 nomes de publicação.
(4) O Astrea tem clientes pessoa física e dados financeiros: **o RADAR não lê o Astrea**, só poderia receber uma lista de CNPJs. (5)
Sobreposição: publicações do DJEN já chegam ao Astrea por nome de advogado; o RADAR entrega outra coisa (ações contra empresas que
não são clientes), e a Produto já decidiu não competir com Astrea/Projuris (quadro).

## 3. Caminhos de integração

| | A. PJe → RADAR (valor e contatos da empresa) | B. RADAR → Astrea (empresa escolhida vira contato) | C. Astrea → RADAR (clientes como excluídas) |
|---|---|---|---|
| Como | O caminho que já existe no RADAR ("Trazer dados da área logada": o programa prepara o pedido só com o que falta, o advogado roda a extensão na sessão dele, cola a resposta no formato v1). A visita provou os campos e os rótulos fixos ("Dados do processo"). Ajustar o prompt com o mapa real (ir direto a `/pjekz/processo/<id>/detalhe`, nunca abrir `login.seam`, nunca "Baixar processo completo", nunca abrir expediente) | O RADAR gera, para as ações marcadas "em contato"/"virou cliente", uma **planilha no formato do contato PJ do Astrea** (Empresa, Nome fantasia, CNPJ, telefones com tipo, e-mails, sites, endereço, etiqueta JUDICIAL, Comentários com número CNJ e tribunal). Entrada no Astrea: (i) a equipe digita; (ii) a extensão, na sessão do Leandro, digita seguindo o mapa; (iii) Aurum (migração paga ou API, se existir) | O Leandro exporta os contatos do Astrea (Excel) de tempos em tempos; o RADAR lê **só a coluna CNPJ** (descarta tudo de pessoa física) e marca essas empresas como excluídas com motivo "cliente do escritório", nos critérios da pessoa (0.7.33) |
| Prós | Nada sai do computador; nenhuma credencial no robô; termos 1.0 seção 5 já cobrem; formato v1 já implementado | Fecha o ciclo comercial sem o RADAR virar CRM; "Origem do cliente = JUDICIAL" mede o resultado; nada do Astrea entra no RADAR | Evita prospectar cliente atual (ou parte contrária de cliente); barato; melhora a lista já na 0.7.34 |
| Contras | Depende do advogado rodar; 30 processos por dia; petições novas em PDF não dão texto; e-mail/telefone raros (1 em 1 no teste) | Sem API nem importação: digitação; duplicados; limites do plano | Exportação manual por e-mail; precisa de disciplina (mensal) |
| Riscos jurídicos e LGPD | Ciência acidental de intimação; bloqueio por excesso em processos de terceiros; **PF nas telas**: o prompt e o formato v1 já excluem; prints não podem ser guardados | Automação na interface pode ferir os termos do Astrea; contato PJ só (CNPJ, dados públicos ou dos autos); o Leandro é o controlador do que entra no Astrea | O arquivo exportado tem PF e financeiro: o RADAR lê só CNPJ e não guarda o arquivo; a lista de excluídas fica no computador da pessoa |
| Esforço | Pequeno: prompt revisado (Arquitetura) + ajustes no formato v1 se faltar campo (Produto, 0.7.34) | Médio: exportação no formato do Astrea (Produto, 1 versão) + prompt de digitação (Arquitetura); API: depende da Aurum | Pequeno: importar CSV/XLSX filtrando CNPJ (Produto; `openpyxl` não é padrão: ler CSV exportado ou a aba em XML, a decidir) |
| Depende do Leandro | Autorizar, rodar os prompts, dizer se quer processos de terceiros | Aceitar a etiqueta JUDICIAL e a digitação pela extensão; perguntar à Aurum sobre API | Exportar os contatos e entregar o arquivo (ou rodar a importação ele mesmo) |

**Recomendação.** Fazer **A e C na 0.7.34** (os dois são pequenos, protegem o escritório e não dependem de ninguém de fora) e deixar
**B em duas etapas**: já a planilha no formato do Astrea (a equipe digita ou a extensão digita, a critério do Leandro) e, só depois da
resposta da Aurum sobre API ou importação, qualquer automação de entrada. **Não recomendado**: o robô entrar no PJe com a credencial
do advogado (contra os termos 1.0, risco de bloqueio e de ciência indevida) e qualquer leitura do Astrea pelo RADAR além da lista de
CNPJs.

## 4. Mudanças que isso pede (quando vier o "pode")

- Prompts da visita: versão 2 do prompt 1 com o mapa real do PJe (id interno, proibições) e um prompt novo para digitar no Astrea (B).
- RADAR (Produto): formato v1 confere com o relatório (valor, data, endereço, e-mail, telefone, site, sócio); importação de CNPJs
  excluídos (C); exportação no formato do Astrea (B); manual, AssistONE, Novidades conforme a Definition of done.
- Termos: A e C cabem na 1.0 (seção 5 e seção 4). B não muda os termos (nada novo é coletado pela SolverONE). Nada de novo aceite.
- Nuvem: nada. RootifyONE, ArchONE e EaglePlanONE: nenhuma integração nova; itens de roadmap "integração PJe (via extensão)" e
  "integração Astrea (planilha)" podem ser registrados quando o dono decidir.

## 5. Perguntas (também na seção "Perguntas ao dono" do quadro, nº 21 a 28)

Para o Leandro: 21 autoriza a extensão a rodar o prompt do PJe nos próprios autos, até 30 processos por dia? 22 precisa de
processos de terceiros (onde a KR Law não atua), sabendo do risco de bloqueio? 23 aceita receber no Astrea as empresas escolhidas
como contato PJ com etiqueta JUDICIAL, digitadas pela extensão na sessão dele, ou prefere a planilha para a equipe digitar? 24 exporta
os contatos do Astrea de tempos em tempos para o RADAR marcar os clientes como excluídos? 25 pergunta à Aurum (como cliente) se há
API ou importação de contatos e o que os termos dizem sobre automação na tela?
Para o Marcelo: 26 ordem na 0.7.34: A e C primeiro, B depois (recomendação)? 27 os prints da visita ficam só na sua pasta restrita,
e os do PJe com CPF são apagados depois do desenho? 28 a petição inicial em HTML pode ser fonte do endereço da ré mesmo variando a
frase por advogado (o v1 marca "a conferir")?
