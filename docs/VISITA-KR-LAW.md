# Visita à KR Law (quinta, 12/Nov/2026): roteiro e prompts do Claude in Chrome

Complementa `robo/ROTEIRO-INSTALACAO.md` (instalação do robô). Aqui ficam os três prompts para usar no **Claude in Chrome**
no computador do Leandro, com o consentimento dele, para aprender como os sistemas funcionam e planejar as integrações.
Nada aqui produz efeito nos sistemas: é leitura e anotação. Os textos originais estão também nos Google Docs "Prompt 1"
e "Prompt 2" do projeto; este arquivo é a cópia de referência no repositório.

## Ordem do dia (quinta 12/Nov)

Links para abrir no celular, todos sem login: este arquivo; instalação em
[`robo/ROTEIRO-INSTALACAO.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/robo/ROTEIRO-INSTALACAO.md);
manual em https://judicial.solverone.com.br/manual.html; pacote em https://judicial.solverone.com.br/downloads/LexSuiteONE-robo.zip.

**Antes, em casa (até quarta).** Ensaio da instalação no PC do dono com a segunda conta Google, `DIAGNOSTICO.bat` e uma
rodada real; e-mail de boas-vindas já enviado ao Leandro (sessão de operação). Confirmar com o Leandro: certificado digital
em mãos para o PJe; qual conta Google do escritório recebe a planilha; se o escritório tem conta Claude com a extensão
Claude in Chrome. Se não tiver, a extensão roda num perfil novo do Chrome dele ("Visita SolverONE") com a conta do dono,
e o perfil é apagado no fim. O notebook do dono não recebe login nem certificado de ninguém.

1. **Chegada (15 min).** Explicar o que vai acontecer e pedir o OK: instalar o robô e três observações só de leitura com a
   extensão, sem senhas. Combinar um processo de referência no TRT2 e um no TRT15. Preparar o Chrome (perfil, extensão,
   modelo Sonnet).
2. **Instalar o robô (45 a 60 min).** Seguir o `ROTEIRO-INSTALACAO.md`: baixar o pacote do site, `DIAGNOSTICO.bat`,
   configurar, ligar a planilha ao Drive do escritório e compartilhar com `integracao@solverone.com.br`, agendar a rodada
   diária e iniciar a primeira rodada agora (demora: deixar rodando).
3. **Enquanto roda: Prompt 3, Astrea (20 a 30 min).** O Leandro entra no Astrea; depois a extensão entra na aba.
4. **Prompt 1, PJe (30 a 45 min).** TRT2 e depois TRT15. O Leandro faz o login com o certificado; a extensão para sempre
   que o site pedir token ou certificado.
5. **Lista do dia pronta.** Mostrar na tela local e na planilha; validar 3 ou 4 itens com o Leandro (é ação nova? é
   empresa? a comarca interessa?); anotar as regras que ele quer ajustar. Escolher 3 empresas para o Prompt 2, que pode
   rodar em casa.
6. **Fechamento (15 min).** Conferir: rodada agendada, planilha compartilhada, Leandro sabe abrir a tela e a planilha,
   manual e `judicial@solverone.com.br` como contato. Apagar o perfil do Chrome se usou a conta do dono. Guardar os
   relatórios dos prompts (sem dado de pessoa física). Anotar feedbacks e dizer o que vem na 0.8.

Depois: relatórios e feedbacks vão para a sessão de Produto; dúvidas de instalação e e-mail, para a sessão de Operação.

## Regras que valem para os três prompts

- **Nunca pedir, digitar, copiar, fotografar ou anotar senha, token, código de certificado ou qualquer credencial.** O
  advogado faz o login sozinho, com a extensão fechada ou pausada; só depois a extensão entra na aba já logada. Se o site
  pedir login, captcha, token ou certificado no meio do caminho, a extensão **para e pede ao advogado**.
- Somente leitura: não cadastrar, peticionar, assinar, marcar como lido, alterar campo, nem clicar em "enviar",
  "assinar", "protocolar", "excluir" ou similares. Se um botão parecer gravar algo, não clica e anota o nome.
- Uma ação por vez, sem pressa, uma aba só. Não copiar dados de pessoas físicas (reclamantes, testemunhas) para o
  relatório: escrever "pessoa física" no lugar do nome. Empresas (razão social, CNPJ) podem ser citadas.
- Ignorar processos de outros clientes que apareçam na tela; abrir só o de referência.
- Modelo da extensão: Sonnet. O relatório final de cada prompt é colado na sessão de Produto para virar desenho de integração.

## Prompt 1 · PJe com o login do advogado (consulta e download, somente leitura)

Como usar: o advogado faz o login no PJe do tribunal na aba do Chrome. Com a aba aberta e logada, cole o texto abaixo no
Claude in Chrome. Troque o número do processo e o tribunal.

```
Você está numa aba do PJe do TRT2 (https://pje.trt2.jus.br) onde um advogado já fez login com as credenciais dele. Sua tarefa é mapear, somente lendo, como se consulta um processo e como se baixam os documentos dele, e registrar cada passo para que isso possa ser automatizado depois. Processo de referência: 0000000-00.0000.5.02.0000 (troque pelo número real).

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial. Se a sessão expirar ou o site pedir login, captcha ou token, pare e peça ao advogado para fazer isso; depois continue.
- Somente leitura: não cadastre, não peticione, não assine, não marque como lido, não altere nenhum campo, não clique em "enviar", "assinar", "protocolar", "excluir" ou similares. Se um botão parecer que grava algo, não clique e anote o nome dele.
- Uma ação por vez, sem pressa. Não abra várias abas do PJe ao mesmo tempo. Se o sistema mostrar erro ou lentidão, espere e tente uma única vez.
- Não navegue para fora do PJe. Não copie dados de pessoas físicas (reclamantes, testemunhas) para o relatório: cite apenas "pessoa física" no lugar do nome. Empresas (razão social e CNPJ) podem ser citadas.
- Se a tela do advogado mostrar processos de outros clientes, ignore-os: só abra o processo de referência.

O que fazer, nessa ordem:
1. Localizar a consulta. A partir do painel do advogado, encontre a função de consulta de processo por número (menu, atalho ou campo de busca). Anote: caminho de menu, URL da tela, nome do campo e formato que o número precisa ter.
2. Abrir o processo de referência. Anote a URL que abre e se ela contém um identificador interno (um número que não é o número CNJ).
3. Mapear os dados do processo. Na tela do processo, liste os blocos que existem e quais campos cada um mostra. Procure especialmente: classe, assunto(s), data de distribuição (ou autuação), valor da causa, órgão julgador (vara), partes do polo passivo com CNPJ, advogados das partes, situação atual, última movimentação. Para cada campo, anote o rótulo exato e em qual aba ou seção ele está.
4. Mapear as movimentações e os documentos. Encontre a lista de movimentações e a lista de documentos (petição inicial, decisões, atas). Anote como a lista é organizada (ordem, paginação, filtros) e que tipos de documento aparecem.
5. Baixar. Procure as opções de download: documento individual, "autos completos" ou "download do processo" (PDF único ou vários). Baixe a petição inicial e, se existir, o PDF dos autos completos, para a pasta padrão de downloads do Chrome. Anote: nome do botão, formato, tamanho aproximado, tempo e se pediu confirmação. Não baixe mais de 3 arquivos.
6. Verificar o que pediu intervenção humana. Liste cada momento em que o site exigiu captcha, token, certificado ou nova autenticação.

Relatório final, neste formato:
- Mapa do fluxo: passos numerados, cada um com "tela → ação → resultado", incluindo URLs e nomes exatos de menus, botões e campos.
- Tabela de campos: campo | rótulo na tela | aba ou seção | exemplo (mascarado se for pessoa física).
- Downloads: o que baixou, formato, tamanho e onde ficou.
- Barreiras: onde exigiu captcha, token ou certificado, e o que mais pode impedir um robô (limite de tempo da sessão, mensagens de erro).
- Sugestão: em 5 linhas, qual seria o caminho mais curto para um robô fazer o mesmo com o advogado logado, e o que teria de ficar com a pessoa.

Repita o mesmo roteiro no TRT15 (https://pje.trt15.jus.br) com um processo de lá, e diga o que é diferente entre os dois.
```

## Prompt 2 · Como chegar às empresas processadas e como os escritórios anunciam (fontes públicas)

Como usar: aba nova no Chrome, sem login em nada. Troque as três empresas de exemplo por empresas reais da lista do
JUDICIAL (razão social e cidade). Nenhuma mensagem é enviada a ninguém. O uso do que for encontrado é decisão do
compliance do escritório.

```
Preciso de um levantamento só em fontes públicas, sem enviar mensagem a ninguém, sem seguir perfis, sem criar conta e sem burlar nenhum login. Duas perguntas:
A) Para uma empresa que acabou de receber uma ação trabalhista, quais canais públicos levam até quem decide sobre contratar advogado (sócio-administrador, diretor, RH, jurídico interno)?
B) Como os escritórios de advocacia trabalhista empresarial (que defendem empresas) anunciam hoje para esse público, e com que mensagens?

Regras:
- Fontes públicas apenas: site institucional da empresa, página "fale conosco", perfil público da empresa no LinkedIn e no Instagram, ficha da empresa no Google, cadastro público do CNPJ, Biblioteca de Anúncios da Meta, Central de Transparência de Anúncios do Google, páginas públicas de escritórios.
- Não colete e-mail ou telefone pessoal de ninguém. Contato de empresa (telefone geral, e-mail comercial, formulário) pode. De pessoas, anote no máximo nome e cargo que já são públicos na página da própria empresa ou no perfil profissional público.
- Não use ferramenta de raspagem, não faça buscas em massa, não visite mais de 10 páginas por empresa. Não tente entrar em área logada.
- Se um site pedir login, captcha ou cookie de rastreamento obrigatório, pule e anote.

Parte A: canais até o decisor. Empresas: [Razão social 1, cidade]; [Razão social 2, cidade]; [Razão social 3, cidade]. Para cada uma, procure nesta ordem e anote o que existe: (1) site oficial e página de contato; (2) perfil da empresa no LinkedIn: tamanho, se lista alguém de RH, jurídico ou sócios com cargo público; (3) Instagram comercial e se responde comentários; (4) ficha no Google com telefone e horário; (5) cadastro público do CNPJ (telefone e e-mail cadastrados, sócios e administradores com qualificação). Diga qual canal parece o caminho mais natural para um contato institucional e por quê.

Parte B: como os escritórios anunciam.
- Na Biblioteca de Anúncios da Meta (facebook.com/ads/library), país Brasil, categoria "todos os anúncios", pesquise: "sua empresa foi processada", "reclamação trabalhista empresa", "defesa trabalhista para empresas", "advocacia empresarial trabalhista", "recebeu uma notificação do TRT". Para os 5 anúncios mais relevantes, anote: anunciante, texto principal, promessa, chamada para ação, formato, desde quando roda, e o link do anúncio na biblioteca.
- Na Central de Transparência de Anúncios do Google (adstransparency.google.com), repita com 3 termos e anote os anunciantes.
- No Instagram, abra 3 perfis públicos de escritórios trabalhistas empresariais e descreva o tipo de conteúdo que usam para empresas: temas, frequência, chamada para ação, se usam conteúdo direcionado ou educativo.
- Diga o que não é permitido ou não é recomendável pelas regras da OAB sobre publicidade (Provimento 205/2021): tipo de anúncio, promessa de resultado, captação direta. Cite a fonte.

Relatório final:
- Tabela 1 (Parte A): empresa | canal | o que existe | esforço | dado de empresa ou de pessoa.
- Tabela 2 (Parte B): anunciante | canal | mensagem resumida | chamada para ação | link.
- Cinco conclusões em frases curtas: quais canais funcionam de forma passiva, quais são ativos e quais ficam fora pela regra da OAB ou pela LGPD.
- Uma lista do que não conseguiu abrir e por quê.
```

## Prompt 3 · Astrea, o sistema do escritório (mapear para integrar, somente leitura)

Como usar: o advogado faz o login no Astrea na aba do Chrome. Com a aba logada, cole o texto. Serve para desenhar como o
JUDICIAL vai entregar as ações novas dentro do sistema que o escritório já usa.

```
Você está numa aba do Astrea (sistema de gestão do escritório) onde um advogado já fez login. Sua tarefa é mapear, somente lendo, como o sistema organiza processos e publicações e por onde dados podem entrar e sair, para que um outro sistema possa alimentá-lo depois. Nada aqui deve ser criado, alterado ou excluído.

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token ou qualquer credencial. Se o sistema pedir login de novo, pare e peça ao advogado.
- Somente leitura: não crie processo, cliente, tarefa ou anotação; não altere campo; não clique em "salvar", "enviar", "excluir", "importar" ou "exportar" que grave ou dispare algo. Anote o nome do botão e siga.
- Não copie dados de pessoas físicas (clientes pessoa física, partes, testemunhas): escreva "pessoa física". Empresas podem ser citadas. Não abra mais do que 2 processos de exemplo.
- Uma ação por vez, uma aba só.

O que mapear, nessa ordem:
1. Menu principal: liste os módulos (processos, clientes, publicações/intimações, agenda, financeiro, relatórios, configurações) com o nome exato de cada um.
2. Cadastro de processo: abra um processo de exemplo e liste os campos (número CNJ, tribunal, vara, classe, partes e papéis, valor, responsável, etiquetas, situação) com o rótulo exato de cada um. Veja se há campo para "origem" ou "como chegou" o caso.
3. Publicações e intimações: onde aparecem, como o sistema as capta (há configuração de OAB? de diários? aviso por e-mail?), e como uma publicação vira tarefa ou prazo.
4. Entrada de dados em lote: procure "importar" (planilha, CSV), "integrações", "API", "webhooks" ou "aplicativos" nas configurações. Anote o que existe, que formatos aceita e que campos pede, sem executar nada.
5. Saída de dados: procure "exportar" e "relatórios"; anote formatos disponíveis.
6. Clientes: como um cliente pessoa jurídica é cadastrado (campos, CNPJ) e como um processo é ligado a ele.

Relatório final:
- Mapa dos módulos e caminhos de menu.
- Tabela de campos do processo: campo | rótulo | obrigatório? | formato.
- Como entram publicações hoje e o que falta para entrar uma "ação nova contra empresa" vinda de fora.
- Portas de entrada e saída (importação, API, webhook, exportação) com o que cada uma aceita.
- Sugestão em 5 linhas: o caminho mais simples para o JUDICIAL entregar as ações novas dentro do Astrea, e o que ficaria com a pessoa.
```

## Depois da visita

Os três relatórios vão para a sessão de Produto, que os transforma em desenho de integração (`docs/INTEGRACOES-MERCADO.md`)
e em pendências. Nenhum dado de pessoa física entra no repositório.
