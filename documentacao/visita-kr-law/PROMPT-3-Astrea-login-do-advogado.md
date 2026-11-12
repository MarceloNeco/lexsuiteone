# Prompt 3 · Astrea (sistema de gestão do escritório)

Cópia do prompt de [`docs/VISITA-KR-LAW.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/docs/VISITA-KR-LAW.md)
(revisão de 12/Nov/2026), que é a fonte. Precisa do login do advogado.

| | |
|---|---|
| Onde roda | Janela B, ao mesmo tempo que o 1A, no perfil "Visita SolverONE" do Chrome do Leandro, extensão Claude in Chrome |
| Login | Leandro, com o login dele no Astrea, quando aparecer `PAUSA PARA LOGIN` |
| Trocar no texto | nada (ela abre até 2 processos e 2 contatos de exemplo) |
| Antes de colar | Conversa nova na extensão; modo "Skip all approvals"; modelo Sonnet, se aparecer a escolha |
| Quanto tempo | Até 45 minutos; ela para sozinha e escreve `RELATÓRIO FINAL` |
| Única interação | O login (e, se pedir, confirmar o download de 1 arquivo); depois do login, digitar `continue` |
| Onde fica o resultado | Na conversa, no claude.ai da conta do dono (celular ou computador) |

Para copiar: botão de copiar no canto do bloco cinza abaixo.

## O prompt: Prompt 3 · Astrea, da página inicial à área logada (na visita, com o login do advogado)

Como usar: na janela da extensão, abra uma conversa nova e cole o texto. A extensão abre a página inicial do Astrea, mapeia o caminho até a tela de entrada e escreve `PAUSA PARA LOGIN`; o Leandro faz o login nessa aba e escreve "continue". Modo da extensão: "Skip all approvals". Roda em paralelo com o Prompt 1A, cada um na sua janela. Serve para desenhar como o JUDICIAL vai entregar as ações novas e as fichas de canais dentro do sistema que o escritório já usa.

```
Comece abrindo, nesta aba, a página inicial do Astrea, o sistema de gestão do escritório: https://www.astrea.net.br (se redirecionar, anote para onde). Parte A, sem login: mapeie o caminho até a tela de entrada. Parte B, depois que o advogado fizer o login: mapeie, somente lendo, como o sistema organiza processos, publicações, contatos e clientes, e por onde dados podem entrar e sair, para que um outro sistema possa alimentá-lo depois. Nada aqui deve ser criado, alterado ou excluído.

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui. Se faltar uma informação, anote "faltou: ..." e siga.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga.
- Se se perder, volte à tela inicial do Astrea e continue do passo em que parou.
- Telas: você não entrega imagens. Quando uma tela importar para quem vai construir a integração, registre-a em texto, num bloco que comece com TELA e um número, neste formato: TELA 01 — nome-curto — URL: ... | Título: ... | Caminho de menu: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações: ... Numere em sequência. Não registre tela de login, senha ou token, e não copie nomes de pessoas físicas: em listas de clientes ou contatos, descreva as colunas, não as linhas.
- Bloqueio: se o sistema pedir login, senha ou token, não tente resolver. Escreva BLOQUEIO, diga em que passo estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome do passo em que parou.
- Pare depois de 60 ações ou 45 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto, marcando o que faltou.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco em Markdown, citando as telas pelo número.

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token ou qualquer credencial.
- Somente leitura: não crie processo, cliente, contato, oportunidade, tarefa ou anotação; não altere campo; não clique em "salvar", "enviar", "excluir", "importar", "exportar", "converter em cliente" ou outro botão que grave ou dispare algo. Anote o nome do botão e siga. Telas de importação podem ser abertas só para ler os campos: pare antes de escolher arquivo.
- Não copie dados de pessoas físicas (clientes pessoa física, contatos pessoa física, partes, testemunhas): escreva "pessoa física". Empresas podem ser citadas. Não abra mais do que 2 processos e 2 contatos de exemplo; prefira os que forem pessoa jurídica.
- Uma ação por vez, uma aba só. Nada é enviado a ninguém.

Parte A · Da página inicial até o login (sem login):
A1. Registre a TELA da página inicial e o caminho até a tela de entrada do sistema (links "Entrar", "Login", "Acessar"), com endereços.
A2. Liste as formas de entrada que aparecem (e-mail e senha, Google, outra), com o texto exato dos botões, sem clicar e sem tocar nos campos.
A3. Escreva exatamente: PAUSA PARA LOGIN — Leandro, faça o login nesta aba. Quando a tela inicial do Astrea aparecer, escreva continue. Depois disso, não faça nada até alguém escrever "continue". Não leia nem registre o que for digitado na tela de login.

Parte B · Depois do login (somente leitura), nessa ordem:
1. Menu principal: liste os módulos (processos, clientes, contatos, atendimentos, prospecção ou oportunidades, publicações/intimações, agenda, financeiro, relatórios, configurações) com o nome exato de cada um. Registre a TELA do menu.
2. Cadastro de processo: abra um processo de exemplo e liste os campos (número CNJ, tribunal, vara, juiz ou relator, classe, partes e papéis, valor, responsável, etiquetas, situação) com o rótulo exato de cada um. Veja se há campo para "origem" ou "como chegou" o caso. Registre a TELA do processo.
3. Publicações e intimações: onde aparecem, como o sistema as capta (há configuração de OAB? de diários? de DJEN? do Domicílio Judicial Eletrônico? aviso por e-mail?), se cada publicação mostra de qual diário ou fonte veio, e como uma publicação vira tarefa ou prazo. Registre a TELA de publicações e a TELA da configuração de captura, se existir.
4. Prospecção, contatos e CRM: existe módulo de prospecção, oportunidades, funil, leads, atendimentos ou CRM (com qualquer um desses nomes)? Se existir, descreva as etapas e os campos. Abra um contato pessoa jurídica de exemplo e liste os campos com o rótulo exato: razão social, CNPJ, telefone (quantos), e-mail (quantos), site, redes sociais (quais), endereço, pessoa de contato e cargo, origem do contato, etiquetas, responsável, observações. Anote quais são obrigatórios. Registre a TELA do cadastro do contato pessoa jurídica.
5. Importação de contatos: há importação de contatos ou clientes por planilha (CSV, Excel)? Que modelo ou colunas pede? Aceita telefone, e-mail e redes? Trata duplicados (por CNPJ ou nome)? Abra a tela só para ler e pare antes de escolher arquivo. Registre a TELA de importação.
6. De contato a cliente: contato e cliente são o mesmo cadastro com um tipo, ou cadastros separados? Há botão ou etapa para transformar um contato em cliente? O que muda (campos, contrato, honorários)? Como um processo é ligado ao cliente?
7. Entrada de dados em lote em geral: procure "importar" (planilha, CSV), "integrações", "API", "webhooks" ou "aplicativos" nas configurações. Anote o que existe, que formatos aceita e que campos pede, sem executar nada. Se houver link para documentação de API, anote o endereço. Registre a TELA de integrações.
8. Saída de dados: procure "exportar" e "relatórios"; anote formatos disponíveis.

Antes de entregar, confira e corrija o que falhar: nada foi criado, alterado ou importado; nenhum nome de pessoa física ou de magistrado foi copiado; cada campo listado tem o rótulo exato que você leu na tela; o que você não achou está como "não encontrei".

RELATÓRIO FINAL:
- Mapa dos módulos e caminhos de menu, com o número da TELA quando houver.
- Tabela de campos do processo: campo | rótulo | obrigatório? | formato.
- Prospecção, contatos e CRM: existe? onde? etapas e como funciona.
- Tabela de campos do contato pessoa jurídica: campo | rótulo | obrigatório? | formato (incluindo telefone, e-mail, site e redes).
- Importação de contatos: formatos, colunas do modelo, tratamento de duplicados.
- De contato a cliente: o caminho, passo a passo, com os nomes dos botões (sem clicar).
- Como entram publicações hoje e o que falta para entrar uma "ação nova contra empresa" vinda de fora.
- Portas de entrada e saída (importação, API, webhook, exportação) com o que cada uma aceita e o endereço da documentação, se houver.
- Mapa técnico para quem vai construir a integração: endereços (URLs) de cada tela; nomes exatos de menus, campos e botões; ordem de cliques; formatos de arquivo aceitos; onde a sessão pede login de novo.
- Dificuldades que você teve navegando.
- Sugestão em 5 linhas: o caminho mais simples para o JUDICIAL entregar as ações novas e as fichas de canais dentro do Astrea (por exemplo, como contato pessoa jurídica com origem "JUDICIAL"), e o que ficaria com a pessoa.
- Lista das telas registradas: número, nome curto e o que mostra.
```
