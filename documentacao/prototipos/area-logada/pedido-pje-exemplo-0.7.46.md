# Pedido de dados ao PJe (14/11/2026) · RADAR JUDICIAL · lote 1 de 2

> Protótipo do que o botão "Preparar busca" vai gerar na 0.7.46 (dados fictícios, marcados). O advogado só copia e cola este
> texto inteiro na ferramenta de navegação (Claude in Chrome, Codex do OpenAI, Gemini no Chrome ou outra), com o PJe aberto e
> logado. A ferramenta trabalha sozinha e devolve o bloco do fim. Filtro de origem: TRT2 · setor Comércio · últimos 30 dias · 48
> processos escolhidos → 2 lotes de 25.

Você está numa aba do PJe do TRT da 2ª Região, 1º grau, já logado como advogado (painel "Meu Painel - PJE"). Trabalhe SÓ nesta
aba, SÓ LEITURA, nos processos da tabela "Processos" abaixo, um de cada vez, e devolva no fim o bloco "RESPOSTA PARA O RADAR v1 ·
lote 1 de 2". Procure SÓ os dados da coluna "falta", SÓ da empresa ré indicada (confira pelo CNPJ).

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
1. No painel, campo "Entre com o número do processo para consulta": digite o número CNJ e Enter. Lista vazia = processo fora
   do acervo do advogado: devolva as linhas dele como tentar_depois, observação "fora do acervo", e passe ao próximo (não use
   "Consulta Processos de Terceiros").
2. Clique no número do processo (abre https://pje.trt2.jus.br/pjekz/processo/<id>/detalhe em nova janela; pode abrir esse
   endereço nesta mesma aba). Nunca volte pelo histórico para a tela de login.
3. Cabeçalho: "Valor da causa:" → valor_causa; "Distribuído:" → data_ajuizamento (aaaa-mm-dd). Fonte "PJe dados do processo".
4. Clique no número no cabeçalho → "Dados do processo" → em "Polo Passivo", a empresa com o CNPJ da lista: a linha depois do
   CNPJ é o endereço (endereco); "(email: …)" é o e-mail (email). Fonte "PJe dados do processo". Ignore o Polo Ativo e os
   blocos dos advogados. Feche (×).
5. Se ainda faltar telefone, e-mail, site ou endereço: linha do tempo em ordem ascendente → primeiro documento, "Petição
   Inicial". Se abrir como texto, leia só o parágrafo que qualifica a empresa ré (fonte "PJe petição inicial"; endereço daqui
   com observação "a conferir"). Se abrir como PDF sem texto selecionável, não baixe: tentar_depois, observação "petição em
   PDF". Sócio ou administrador DA EMPRESA citado com telefone ou e-mail → socio_contato ("Nome: canal"); nunca CPF.
6. Se ainda faltar endereço: segundo documento, "Notificação" → campo "DESTINATÁRIO:" (fonte "PJe citação"). Não clique no
   envelope "Visualizar Expedientes".
7. Volte ao painel por "Meu Painel" e passe ao próximo. Ritmo: um processo por vez, sem abrir várias janelas.

SE APARECER "Acesso Negado", "É preciso logar" ou "SJT-004": pare, devolva o que já tem e marque o resto como tentar_depois,
observação "sessão expirou".

RESPOSTA: ao terminar os 25 processos deste lote, devolva SÓ o bloco abaixo, uma linha para cada dado da coluna "falta" de cada
processo (nunca invente; "nao_consta" quando leu o lugar certo e não havia). Se a sua ferramenta oferecer "baixar como arquivo",
salve o bloco como `resposta-radar-lote-1.md`; senão, deixe o bloco inteiro na tela para copiar.

RESPOSTA PARA O RADAR v1 · lote 1 de 2
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|

- dado: valor_causa, data_ajuizamento, telefone, email, site, endereco, socio_contato, outro
- resultado: encontrado, nao_consta ou tentar_depois
- fonte: PJe dados do processo, PJe petição inicial, PJe citação ou outro
- data: aaaa-mm-dd de hoje · valor_causa só números com vírgula (105000,00) · data_ajuizamento aaaa-mm-dd

## Processos (25 de 48; lote 1 de 2)

| processo | tribunal | empresa ré | CNPJ | falta |
|---|---|---|---|---|
| 0000001-11.2026.5.02.0001 | TRT2 | Empresa Exemplo Um Ltda (fictícia) | 11.222.333/0001-81 | valor_causa, email, telefone |
| 0000002-22.2026.5.02.0002 | TRT2 | Comércio Exemplo Dois S.A. (fictícia) | 12.ABC.345/01DE-35 | valor_causa, data_ajuizamento, endereco |
| 0000003-33.2026.5.02.0003 | TRT2 | Loja Exemplo Três ME (fictícia) | 11.222.333/0001-81 | telefone, email, site |
| … (mais 22 linhas) | | | | |
