# Visita à KR Law (quinta, 12/Nov/2026): roteiro e prompts do Claude in Chrome

Complementa `robo/ROTEIRO-INSTALACAO.md` (instalação do robô). Aqui ficam os três prompts para usar no **Claude in Chrome**
no computador do Leandro, com o consentimento dele, para aprender como os sistemas funcionam e planejar as integrações.
Nada aqui produz efeito nos sistemas: é leitura e anotação. Esta é a versão revisada em 08/Nov/2026 (foco na ficha de
canais); os Google Docs "Prompt 1" e "Prompt 2" do projeto ficam com a versão anterior até o dono pedir a atualização.

## Foco da visita: a ficha de canais da empresa processada

O Leandro apontou o diferencial do produto: **levantar e confirmar os canais de contato da empresa processada**, para o
time de compliance do escritório analisar e decidir se e como agir. O JUDICIAL e a extensão **não enviam nada a
ninguém**: não ligam, não mandam e-mail nem mensagem, não seguem perfis, não preenchem formulário.

O que pode entrar na ficha e o que nunca entra:

| Pode | Só com condição | Nunca |
|---|---|---|
| Dados da empresa: telefone geral, e-mail comercial, formulário de contato, site, LinkedIn e Instagram **da empresa**, endereço, e nomes e cargos públicos de sócios e administradores, sempre com a fonte | Celular ou e-mail de uma pessoa, **só se a própria empresa o publica como contato comercial** (no site, na página ou no perfil da empresa), anotando onde | Qualquer dado do reclamante e de outras pessoas físicas (testemunhas, advogados da parte contrária, familiares): no relatório, escrever "pessoa física" no lugar |

## Regras que valem para os três prompts

- **Nunca pedir, digitar, copiar, fotografar ou anotar senha, token, código de certificado ou qualquer credencial.** O
  advogado faz o login sozinho, com a extensão fechada ou pausada; só depois a extensão entra na aba já logada. Se o site
  pedir login, captcha, token ou certificado no meio do caminho, a extensão **para e pede ao advogado**.
- Somente leitura: não cadastrar, peticionar, assinar, marcar como lido, alterar campo, nem clicar em "enviar",
  "assinar", "protocolar", "excluir", "importar", "converter" ou similares. Se um botão parecer gravar algo, não clica e
  anota o nome.
- Nada é enviado a ninguém: nenhuma ligação, e-mail, mensagem, comentário, convite, curtida ou formulário.
- Uma ação por vez, sem pressa, uma aba só. Dados de pessoas físicas seguem a tabela acima: "pessoa física" no lugar do
  nome. Empresas (razão social, CNPJ e os canais da empresa) podem ser citadas.
- Ignorar processos de outros clientes que apareçam na tela; abrir só o de referência.
- Modelo da extensão: Sonnet. O relatório final de cada prompt é colado na sessão de Produto para virar desenho de integração.

## Prompt 1 · PJe com o login do advogado (consulta, download e contatos da ré nos autos, somente leitura)

Como usar: o advogado faz o login no PJe do tribunal na aba do Chrome. Com a aba aberta e logada, cole o texto abaixo no
Claude in Chrome. Troque o número do processo e o tribunal.

```
Você está numa aba do PJe do TRT2 (https://pje.trt2.jus.br) onde um advogado já fez login com as credenciais dele. Sua tarefa é mapear, somente lendo, como se consulta um processo e como se baixam os documentos dele, e anotar onde aparecem os dados de contato da empresa ré (endereço, e-mail e telefone), para que isso possa ser automatizado depois. Processo de referência: 0000000-00.0000.5.02.0000 (troque pelo número real).

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial. Se a sessão expirar ou o site pedir login, captcha ou token, pare e peça ao advogado para fazer isso; depois continue.
- Somente leitura: não cadastre, não peticione, não assine, não marque como lido, não altere nenhum campo, não clique em "enviar", "assinar", "protocolar", "excluir" ou similares. Se um botão parecer que grava algo, não clique e anote o nome dele.
- Uma ação por vez, sem pressa. Não abra várias abas do PJe ao mesmo tempo. Se o sistema mostrar erro ou lentidão, espere e tente uma única vez.
- Não navegue para fora do PJe. Nada é enviado a ninguém.
- Dados da empresa ré (razão social, CNPJ, endereço, e-mail, telefone) podem ser anotados. Dados do reclamante e de qualquer outra pessoa física (testemunhas, advogados, prepostos), nunca: escreva "pessoa física" no lugar. A qualificação da petição inicial traz os dados do reclamante logo ao lado dos da empresa: anote só a parte da empresa.
- Se a tela do advogado mostrar processos de outros clientes, ignore-os: só abra o processo de referência. Se o advogado indicar um segundo processo para comparar, use só esse.

O que fazer, nessa ordem:
1. Localizar a consulta. A partir do painel do advogado, encontre a função de consulta de processo por número (menu, atalho ou campo de busca). Anote: caminho de menu, URL da tela, nome do campo e formato que o número precisa ter.
2. Abrir o processo de referência. Anote a URL que abre e se ela contém um identificador interno (um número que não é o número CNJ).
3. Mapear os dados do processo. Na tela do processo, liste os blocos que existem e quais campos cada um mostra. Procure especialmente: classe, assunto(s), data de distribuição (ou autuação), valor da causa, órgão julgador (vara), partes do polo passivo com CNPJ e endereço, advogados das partes, situação atual, última movimentação. Para cada campo, anote o rótulo exato e em qual aba ou seção ele está. Veja se o cadastro da parte ré (clicando no nome dela, se o PJe permitir só visualizar) mostra endereço, e-mail ou telefone.
4. Mapear as movimentações e os documentos. Encontre a lista de movimentações e a lista de documentos (petição inicial, notificação ou citação inicial, decisões, atas). Anote como a lista é organizada (ordem, paginação, filtros) e que tipos de documento aparecem.
5. Baixar. Procure as opções de download: documento individual, "autos completos" ou "download do processo" (PDF único ou vários). Baixe a petição inicial e, se existir, o PDF dos autos completos, para a pasta padrão de downloads do Chrome. Anote: nome do botão, formato, tamanho aproximado, tempo e se pediu confirmação. Não baixe mais de 3 arquivos.
6. Contatos da empresa ré nos autos. Abra no visualizador do PJe (sem baixar outro arquivo):
   a) A petição inicial. Ache a qualificação da reclamada (normalmente no primeiro parágrafo, depois dos dados do reclamante, com expressões como "em face de", "pessoa jurídica de direito privado", "inscrita no CNPJ", "com sede na", "endereço eletrônico", "e-mail", "telefone"). Anote em que página e em que trecho aparecem o endereço, o e-mail e o telefone da empresa, e qual expressão vem antes de cada um.
   b) A notificação ou citação inicial da ré (aba de expedientes, intimações ou documentos; anote o nome exato). Anote para qual endereço ou meio ela foi expedida (Correios, oficial de justiça, Domicílio Judicial Eletrônico, e-mail) e se há aviso de recebimento ou certidão dizendo se a empresa foi encontrada naquele endereço.
   c) Para cada documento: o texto é selecionável (PDF de texto) ou é imagem escaneada? Os dados estão sempre no mesmo lugar e com as mesmas expressões?
   d) Se o advogado indicar um segundo processo, repita os itens a, b e c nele e compare.
7. Verificar o que pediu intervenção humana. Liste cada momento em que o site exigiu captcha, token, certificado ou nova autenticação.

Relatório final, neste formato:
- Mapa do fluxo: passos numerados, cada um com "tela → ação → resultado", incluindo URLs e nomes exatos de menus, botões e campos.
- Tabela de campos: campo | rótulo na tela | aba ou seção | exemplo (mascarado se for pessoa física).
- Downloads: o que baixou, formato, tamanho e onde ficou.
- Contatos da ré nos autos: documento | dado (endereço, e-mail ou telefone) | aparece? | página e trecho | expressão que vem antes | texto ou imagem | valor encontrado (só da empresa).
- Extração repetível: para cada dado, "sim", "parcial" ou "não", com o motivo (mesmo lugar e mesmas expressões em todo processo? texto selecionável? depende de alguém ter digitado certo?). Diga também se esses dados só aparecem com o login do advogado.
- Barreiras: onde exigiu captcha, token ou certificado, e o que mais pode impedir um robô (limite de tempo da sessão, mensagens de erro).
- Sugestão: em 5 linhas, qual seria o caminho mais curto para um robô fazer o mesmo com o advogado logado, e o que teria de ficar com a pessoa.

Repita o mesmo roteiro no TRT15 (https://pje.trt15.jus.br) com um processo de lá, e diga o que é diferente entre os dois.
```

## Prompt 2 · Ficha de canais da empresa processada (fontes públicas, para o compliance)

Como usar: aba nova no Chrome, sem login em nada. Troque as três empresas de exemplo por empresas reais da lista do
JUDICIAL (razão social, CNPJ e cidade; se a linha do JUDICIAL já trouxer telefone, e-mail e sócios, cole junto, que a
extensão usa como ponto de partida e confere). Nenhuma mensagem é enviada a ninguém. O uso do que for encontrado é
decisão do compliance do escritório.

```
Preciso de uma "ficha de canais" de cada empresa abaixo, feita só em fontes públicas, para o time de compliance de um escritório de advocacia analisar e decidir se e como agir. Você não envia nada a ninguém: não liga, não manda e-mail nem mensagem, não preenche formulário, não segue perfis, não comenta, não cria conta e não burla nenhum login.

Empresas (razão social, CNPJ, cidade, e o que o JUDICIAL já trouxe, se houver):
1. [Razão social 1], [CNPJ], [cidade]
2. [Razão social 2], [CNPJ], [cidade]
3. [Razão social 3], [CNPJ], [cidade]

O que pode entrar na ficha:
- Dados da empresa: telefone geral, e-mail comercial, formulário de contato, site oficial, perfil da empresa no LinkedIn e no Instagram, ficha da empresa no Google, endereço da sede e das filiais, e nomes e cargos públicos de sócios e administradores. Sempre com a fonte.
- Celular ou e-mail de uma pessoa só entra se a própria empresa o publica como contato comercial (no site, na página ou no perfil da empresa). Anote exatamente onde está publicado. Se o único contato de uma pessoa estiver fora dos canais da empresa, não anote.
- Perfil profissional público de um sócio ou administrador pode ser aberto só para confirmar nome e cargo atual. Não anote mais nada dele.
- Nunca: dados do reclamante e de outras pessoas físicas. Não procure o processo nem quem processou.

Regras de navegação:
- Fontes públicas apenas: site institucional da empresa, página "fale conosco", perfil público da empresa no LinkedIn e no Instagram, ficha da empresa no Google, cadastro público do CNPJ (Receita Federal ou consulta pública equivalente).
- Não use ferramenta de raspagem, não faça buscas em massa, não visite mais de 10 páginas por empresa. Não tente entrar em área logada.
- Se um site pedir login, captcha ou cookie de rastreamento obrigatório, pule e anote.
- Não teste se um e-mail ou telefone funciona (nada de ligar, enviar ou usar serviço de verificação). "Confirmar" aqui é cruzar fontes.

Como confirmar cada canal (cruzamento de fontes):
- O site é mesmo da empresa? Procure o CNPJ ou a razão social no rodapé, na política de privacidade ou na página de contato.
- O e-mail comercial usa o domínio do site? O telefone é o mesmo no site, na ficha do Google e no cadastro do CNPJ?
- O perfil do LinkedIn e o do Instagram apontam para o mesmo site? Têm atividade recente?
- O e-mail do cadastro do CNPJ é de outro domínio (por exemplo, de um escritório de contabilidade)? Se for, anote "provável contato do contador".
- O endereço do cadastro do CNPJ bate com o do site e com o da ficha do Google?

Grau de confiança de cada linha:
- Alta: publicado pela própria empresa num canal oficial (site, perfil da empresa) e confirmado por mais uma fonte.
- Média: uma fonte só, oficial (site da empresa ou cadastro do CNPJ), sem confirmação.
- Baixa: só em fonte de terceiros (diretório, agregador), divergente entre fontes ou com sinal de estar desatualizado.

Parte B, contexto para o compliance (curta): diga o que não é permitido ou não é recomendável pelas regras da OAB sobre publicidade e captação de clientela (Provimento 205/2021 e Código de Ética e Disciplina), e o que a LGPD exige para usar dados de contato de empresa e de sócios. Cite a fonte de cada ponto. Se der tempo, na Biblioteca de Anúncios da Meta (facebook.com/ads/library), país Brasil, pesquise "defesa trabalhista para empresas" e "sua empresa foi processada" e anote os 3 anúncios mais relevantes: anunciante, mensagem resumida, chamada para ação e link.

Relatório final, pronto para o compliance:
- Uma ficha por empresa, com o cabeçalho "Razão social · CNPJ · cidade · data do levantamento" e esta tabela:
  canal | dado encontrado | fonte (endereço da página ou nome da fonte) | data da consulta | confiança (alta, média ou baixa) | confirmado por | observação
  Linhas, nesta ordem: site oficial; página de contato ou formulário; telefone geral; e-mail comercial; endereço da sede; filiais; LinkedIn da empresa; Instagram da empresa; ficha no Google; sócios e administradores (uma linha por pessoa: nome e cargo); contato de pessoa publicado pela empresa (se houver); outros.
  Se um canal não foi encontrado, escreva "não encontrado" e onde procurou.
- Divergências: o que não bate entre as fontes (telefone, endereço, e-mail).
- Observações para o compliance, em até 3 linhas por empresa: quais canais são institucionais da empresa e quais pedem cautela (e-mail do contador, celular, perfil sem atividade). Não recomende abordagem: a decisão é do compliance.
- Tabela da Parte B: regra | o que diz | fonte; e, se houver, anunciante | mensagem resumida | chamada para ação | link.
- Lista do que não conseguiu abrir e por quê.
```

## Prompt 3 · Astrea, o sistema do escritório (mapear para integrar, somente leitura)

Como usar: o advogado faz o login no Astrea na aba do Chrome. Com a aba logada, cole o texto. Serve para desenhar como o
JUDICIAL vai entregar as ações novas e as fichas de canais dentro do sistema que o escritório já usa.

```
Você está numa aba do Astrea (sistema de gestão do escritório) onde um advogado já fez login. Sua tarefa é mapear, somente lendo, como o sistema organiza processos, publicações, contatos e clientes, e por onde dados podem entrar e sair, para que um outro sistema possa alimentá-lo depois. Nada aqui deve ser criado, alterado ou excluído.

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token ou qualquer credencial. Se o sistema pedir login de novo, pare e peça ao advogado.
- Somente leitura: não crie processo, cliente, contato, oportunidade, tarefa ou anotação; não altere campo; não clique em "salvar", "enviar", "excluir", "importar", "exportar", "converter em cliente" ou outro botão que grave ou dispare algo. Anote o nome do botão e siga. Telas de importação podem ser abertas só para ler os campos: pare antes de escolher arquivo.
- Não copie dados de pessoas físicas (clientes pessoa física, contatos pessoa física, partes, testemunhas): escreva "pessoa física". Empresas podem ser citadas. Não abra mais do que 2 processos e 2 contatos de exemplo.
- Uma ação por vez, uma aba só. Nada é enviado a ninguém.

O que mapear, nessa ordem:
1. Menu principal: liste os módulos (processos, clientes, contatos, atendimentos, prospecção ou oportunidades, publicações/intimações, agenda, financeiro, relatórios, configurações) com o nome exato de cada um.
2. Cadastro de processo: abra um processo de exemplo e liste os campos (número CNJ, tribunal, vara, classe, partes e papéis, valor, responsável, etiquetas, situação) com o rótulo exato de cada um. Veja se há campo para "origem" ou "como chegou" o caso.
3. Publicações e intimações: onde aparecem, como o sistema as capta (há configuração de OAB? de diários? aviso por e-mail?), e como uma publicação vira tarefa ou prazo.
4. Prospecção, contatos e CRM: existe módulo de prospecção, oportunidades, funil, leads, atendimentos ou CRM (com qualquer um desses nomes)? Se existir, descreva as etapas e os campos. Abra um contato pessoa jurídica de exemplo e liste os campos com o rótulo exato: razão social, CNPJ, telefone (quantos), e-mail (quantos), site, redes sociais (quais), endereço, pessoa de contato e cargo, origem do contato, etiquetas, responsável, observações. Anote quais são obrigatórios.
5. Importação de contatos: há importação de contatos ou clientes por planilha (CSV, Excel)? Que modelo ou colunas pede? Aceita telefone, e-mail e redes? Trata duplicados (por CNPJ ou nome)? Abra a tela só para ler e pare antes de escolher arquivo.
6. De contato a cliente: contato e cliente são o mesmo cadastro com um tipo, ou cadastros separados? Há botão ou etapa para transformar um contato em cliente? O que muda (campos, contrato, honorários)? Como um processo é ligado ao cliente?
7. Entrada de dados em lote em geral: procure "importar" (planilha, CSV), "integrações", "API", "webhooks" ou "aplicativos" nas configurações. Anote o que existe, que formatos aceita e que campos pede, sem executar nada.
8. Saída de dados: procure "exportar" e "relatórios"; anote formatos disponíveis.

Relatório final:
- Mapa dos módulos e caminhos de menu.
- Tabela de campos do processo: campo | rótulo | obrigatório? | formato.
- Prospecção, contatos e CRM: existe? onde? etapas e como funciona.
- Tabela de campos do contato pessoa jurídica: campo | rótulo | obrigatório? | formato (incluindo telefone, e-mail, site e redes).
- Importação de contatos: formatos, colunas do modelo, tratamento de duplicados.
- De contato a cliente: o caminho, passo a passo, com os nomes dos botões (sem clicar).
- Como entram publicações hoje e o que falta para entrar uma "ação nova contra empresa" vinda de fora.
- Portas de entrada e saída (importação, API, webhook, exportação) com o que cada uma aceita.
- Sugestão em 5 linhas: o caminho mais simples para o JUDICIAL entregar as ações novas e as fichas de canais dentro do Astrea (por exemplo, como contato pessoa jurídica com origem "JUDICIAL"), e o que ficaria com a pessoa.
```

## Depois da visita

Os três relatórios vão para a sessão de Produto, que os transforma em desenho de integração (`docs/INTEGRACOES-MERCADO.md`),
no desenho da ficha de canais (`robo/PENDENCIAS.md`) e em pendências. Nenhum dado de pessoa física entra no repositório,
e nenhum dado real de empresa cliente entra no repositório: as fichas reais ficam com o escritório.
