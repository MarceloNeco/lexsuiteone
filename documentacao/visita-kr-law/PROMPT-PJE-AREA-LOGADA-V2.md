# Prompt v2 · PJe → RADAR JUDICIAL (área logada do advogado) · 13/Nov/2026

Para que serve: o RADAR lê o Diário (DJEN), que quase não traz valor da causa nem contatos da empresa ré. O advogado, logado no
PJe com a credencial dele (token/certificado), tem direito de ler os autos; este prompt faz a extensão Claude in Chrome fazer essa
leitura por ele, com eficiência, só leitura, e devolver a tabela que o RADAR lê sem IA ("Trazer dados da área logada").
Construído sobre o mapa real do PJe do TRT2 (relatório do prompt 1A, 13/Nov). O PJe do TRT15 usa a mesma interface ("pjekz").

## Como usar (Leandro)

1. No RADAR: menu ☰ → Área logada → **Preparar pedido ao PJe**. O programa grava `saida/contatos/pedido-pje-AAAA-MM-DD.md`
   com até 30 processos e, em cada um, só o que falta (valor, data, telefone, e-mail, endereço).
2. No Chrome, com o PJe do TRT2 (1º grau) **já logado** (painel "Meu Painel - PJE"), abra o Claude in Chrome, cole o prompt
   abaixo e, logo depois, o conteúdo do arquivo do passo 1.
3. Quando terminar, copie o bloco "RESPOSTA PARA O RADAR v1" e cole no RADAR: ☰ → Área logada → Trazer dados da área logada.

## Prompt (colar inteiro)

```
Você está na aba do PJe do TRT da 2ª Região, 1º grau, já logado como advogado (painel "Meu Painel - PJE"). Trabalhe SÓ nesta
aba, SÓ LEITURA, no máximo 30 processos nesta sessão, um de cada vez, e devolva no fim a tabela "RESPOSTA PARA O RADAR v1".
A lista de processos e o que falta em cada um vêm no arquivo colado depois deste texto (tabela "Processos", colunas processo,
tribunal, empresa ré, CNPJ, falta). Procure SÓ os dados da coluna "falta", SÓ da empresa ré indicada (confira pelo CNPJ).

NUNCA (cada um destes anula o trabalho):
- abrir https://pje.trt2.jus.br/primeirograu/login.seam nem qualquer tela de login (derruba a sessão);
- clicar em "Baixar processo completo", "Baixar processo por instância" ou "Baixar documentos filtrados";
- abrir "Meus Expedientes", "Visualizar Expediente", "Detalhar Expediente" nem o ícone de envelope de uma intimação (pode
  registrar ciência e abrir prazo);
- clicar em Peticionar, Responder, Apresentação de Renúncia, Solicitação de Habilitação, Novo Processo ou em qualquer botão
  que grave, assine ou envie;
- anotar dado do reclamante, de testemunha, de perito, de preposto ou de advogado (de qualquer lado); anotar CPF; anotar
  dado de outra empresa que não a da lista.

ROTEIRO POR PROCESSO:
1. No painel, campo "Entre com o número do processo para consulta": digite o número CNJ (0000000-00.0000.5.02.0000) e Enter.
   Se a lista ficar vazia, o processo não está no acervo do advogado: devolva todas as linhas dele como tentar_depois, com
   observação "fora do acervo", e passe ao próximo (não use "Consulta Processos de Terceiros").
2. Clique no número do processo (abre em nova janela/aba o endereço https://pje.trt2.jus.br/pjekz/processo/<id>/detalhe).
   Pode abrir esse endereço nesta mesma aba. Nunca volte pelo histórico para a tela de login.
3. No cabeçalho do processo leia "Valor da causa:" (dado valor_causa; fonte "PJe dados do processo") e "Distribuído:"
   (dado data_ajuizamento, formato aaaa-mm-dd; mesma fonte).
4. Clique no número do processo no cabeçalho: abre "Dados do processo". Em "Polo Passivo", ache a empresa com o CNPJ da
   lista. Na linha depois do CNPJ está o endereço cadastrado (dado endereco) e, entre parênteses "(email: …)", o e-mail
   (dado email). Fonte: "PJe dados do processo". Ignore tudo em "Polo Ativo" e os blocos dos advogados. Feche a janela (×).
5. Se ainda faltar telefone, e-mail, site ou endereço: na linha do tempo, ative a ordenação ascendente (ícone de setas) e abra
   o PRIMEIRO documento, "Petição Inicial". Se ele abrir como texto (HTML), leia só o parágrafo que qualifica a empresa ré
   ("em face de … inscrita no CNPJ … requerendo seja notificada na …"): endereço, telefone, e-mail, site da EMPRESA
   (fonte "PJe petição inicial"; para endereço vindo daqui, observação "a conferir"). Se o documento abrir como PDF dentro da
   página e o texto não for selecionável, não baixe: devolva os dados que faltam como tentar_depois, observação "petição
   em PDF". Se a inicial citar sócio ou administrador DA EMPRESA com telefone ou e-mail, devolva como socio_contato
   (valor = "Nome do sócio: canal"); nunca CPF.
6. Se ainda faltar endereço: abra o segundo documento, "Notificação" (da ré), e leia o campo "DESTINATÁRIO:" (fonte "PJe
   citação"). Não clique no ícone de envelope "Visualizar Expedientes".
7. Volte ao painel pelo menu lateral "Meu Painel" (nunca pelo endereço de login) e passe ao próximo processo.

SE A TELA MOSTRAR "Acesso Negado", "É preciso logar" ou "SJT-004": pare. Devolva o que já tem e marque o resto como
tentar_depois, observação "sessão expirou".

RESPOSTA: no fim, devolva SÓ este bloco, uma linha para cada dado da coluna "falta" de cada processo (nunca invente;
"nao_consta" quando leu o lugar certo e não havia):

RESPOSTA PARA O RADAR v1
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|

- dado: valor_causa, data_ajuizamento, telefone, email, site, endereco, socio_contato, outro
- resultado: encontrado, nao_consta ou tentar_depois
- fonte: PJe dados do processo, PJe petição inicial, PJe citação ou outro
- data: aaaa-mm-dd de hoje · valor_causa só números com vírgula (105000,00) · data_ajuizamento aaaa-mm-dd
```

## O que muda no RADAR para este prompt render tudo (pedido à Produto, no quadro)

1. Embutir este prompt no arquivo que "Preparar pedido ao PJe" gera (`contatos.PEDIDO_V1`), no lugar do texto genérico.
2. Aceitar a fonte **"PJe dados do processo"** em `colar_v1` (hoje só petição inicial, citação, site da empresa, outro): é a
   fonte mais confiável (rótulo fixo) e foi de onde vieram valor, data, endereço e e-mail no teste real.
3. Texto da janela "Trazer dados da área logada": a tabela v1 tem **7 colunas**, não 8 (a de 8 é o formato antigo de contatos).
4. Endereço com observação "a conferir" (vindo da petição) entra marcado assim na ficha; o do cadastro da parte tem prioridade.
5. Porte e setor continuam vindo do cadastro CNPJ (Receita), não do PJe; o prompt não os pede.
