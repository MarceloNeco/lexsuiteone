# Prompt 4B · TJSP (Justiça estadual de São Paulo, e-SAJ), opcional

Cópia do prompt de [`docs/VISITA-KR-LAW.md`](https://github.com/MarceloNeco/lexsuiteone/blob/main/docs/VISITA-KR-LAW.md)
(revisão de 12/Nov/2026), que é a fonte. Precisa do login do advogado.

| | |
|---|---|
| Onde roda | Janela B, depois do 3, se o Leandro quiser, no perfil "Visita SolverONE" do Chrome do Leandro, extensão Claude in Chrome |
| Login | Leandro, com o certificado digital, quando aparecer `PAUSA PARA LOGIN` |
| Trocar no texto | o número de um processo do escritório no TJSP, se houver |
| Antes de colar | Conversa nova na extensão; modo "Skip all approvals"; modelo Sonnet, se aparecer a escolha |
| Quanto tempo | Até 45 minutos; ela para sozinha e escreve `RELATÓRIO FINAL` |
| Única interação | O login (e, se pedir, confirmar o download de 1 arquivo); depois do login, digitar `continue` |
| Onde fica o resultado | Na conversa, no claude.ai da conta do dono (celular ou computador) |

Para copiar: botão de copiar no canto do bloco cinza abaixo.

## O prompt: Prompt 4B · TJSP, da página inicial à área logada (na visita, se o Leandro quiser)

Como usar: na visita, depois do 1A, numa janela da extensão. A extensão abre a página inicial do TJSP, mapeia o caminho até a entrada do advogado e escreve `PAUSA PARA LOGIN`; o Leandro faz o login com o certificado e escreve "continue". Modo da extensão: "Skip all approvals". O DJEN não tem área logada: fica todo no 4A.

```
Comece abrindo, nesta aba, a página inicial do Tribunal de Justiça de São Paulo: https://www.tjsp.jus.br. Sua tarefa tem duas partes. Parte A, sem login: mapear o caminho da página inicial até a entrada do advogado no e-SAJ (Portal de Serviços) ou no sistema que o tribunal indicar. Parte B, depois que o advogado fizer o login: mapear, somente lendo, o painel do advogado (intimações, processos, prazos) e o que muda em relação à consulta pública. Processo de referência do TJSP: [número], se o escritório tiver um; se não, use um da lista de intimações dele, sem abrir mais de 2.

Como trabalhar (você roda numa extensão do navegador, sozinho, e não salva arquivos):
- Ninguém acompanha você. Não faça perguntas no meio do caminho: decida sozinho pelas regras daqui.
- Antes de cada ação, diga em uma linha o que está vendo e o que vai fazer. Uma ação por vez. Se não achar algo em 3 tentativas, anote "não encontrei" e siga.
- Telas: você não entrega imagens. Quando uma tela importar, registre-a em texto, num bloco que comece com TELA e um número: TELA 01 — nome-curto — URL: ... | Título: ... | Campos (rótulo, tipo, obrigatório?): ... | Botões e links (texto exato): ... | O que acontece ao clicar: ... | Observações: ... Numere em sequência. Não registre tela de login, senha, token, certificado ou captcha, e não copie nomes de pessoas físicas.
- Captcha: descreva em palavras (tipo, em que momento aparece), mas não tente resolver nem contornar. Se ele impedir de seguir, trate como bloqueio.
- Bloqueio: se o site pedir login, senha, token, certificado ou captcha para seguir, escreva BLOQUEIO, diga em que passo estava, entregue o RELATÓRIO FINAL com o que já tem e espere. Se alguém resolver e escrever "continue", retome.
- Pare depois de 45 ações ou 30 minutos, o que vier primeiro, e entregue o relatório mesmo incompleto.
- Ao terminar, escreva RELATÓRIO FINAL e, abaixo, o relatório completo num único bloco em Markdown, citando as telas pelo número.

Regras que não se negociam:
- Nunca peça, digite, copie ou anote senha, token, código de certificado ou qualquer credencial.
- Somente leitura. Nada é enviado a ninguém. Não baixe mais de 1 arquivo.
- Dados de empresas podem ser anotados. Dados de pessoas físicas, nunca: escreva "pessoa física". Nome de magistrado vira "magistrado 1", "magistrado 2".
- Só vale o que você leu na tela nesta sessão. Não deduza qual diário vale para prazo: anote só o aviso que o próprio site mostrar, com o endereço.

Parte A · Da página inicial até o login (sem login):
A1. Registre a TELA da página inicial e o caminho até a entrada do advogado (links como "e-SAJ", "Portal de Serviços", "Peticionamento", "Advogados"), com textos exatos e endereços. Se o site avisar que a área do advogado mudou de sistema (por exemplo, para o eproc), siga o caminho indicado e anote o aviso.
A2. Liste as formas de login que aparecem (certificado digital, usuário e senha, outra), com o texto exato dos botões, sem clicar e sem tocar nos campos.
A3. Escreva exatamente: PAUSA PARA LOGIN — Leandro, faça o login nesta aba. Quando o painel do advogado aparecer, escreva continue. Depois disso, não faça nada até alguém escrever "continue". Não leia nem registre o que for digitado na tela de login.

Parte B · Depois do login (somente leitura), nessa ordem:
B1. Painel do advogado: onde ficam intimações, processos e prazos; nomes exatos de menus e abas. Registre as TELAS.
B2. Abra o processo de referência: o que aparece a mais do que na consulta pública (documentos, download dos autos, dados das partes, quem assinou as decisões, como "magistrado N")?
B3. Baixe no máximo 1 documento de exemplo e anote formato, tamanho e como foi o download.
B4. Intimações: como chegam, se mostram de qual diário vieram e como o prazo aparece. Não marque ciência de nada.

Antes de entregar, confira: nada foi assinado, peticionado ou marcado como lido; nenhum nome de pessoa física ou de magistrado; cada afirmação tem a TELA ou o endereço; o que não viu está como "não encontrei".

RELATÓRIO FINAL:
- Jornada pública: da página inicial ao login, com endereços e as formas de login oferecidas.
- Mapa do fluxo logado, com URLs, nomes exatos de campos e botões, e os números das telas.
- Tabela: o que aparece | consulta pública | painel do advogado.
- Download: como é, formato, tamanho.
- Mapa técnico para quem vai construir o robô: endereços, ordem de cliques, onde entram certificado e token, quanto tempo a sessão durou sem pedir login de novo.
- Barreiras e dificuldades.
- Sugestão em 5 linhas: o que só dá para fazer com o advogado logado e o que um robô poderia fazer com ele logado.
- Lista das telas registradas.
```
