# Prompt para a conversa do RootifyONE (colar inteiro) · interruptores por licença · 14/Nov/2026

```
Pedido do dono (14/Nov), vindo da Arquitetura do LexSuiteONE: interruptores de recurso POR LICENÇA do RADAR JUDICIAL, começando
pela "Área logada" (trazer dados do PJe pela extensão de IA), que fica desligada para um escritório até o dono ligar.
Faça só a parte da tela; a nuvem (coluna, lex-conta) é da Arquitetura do LexSuiteONE e entra com o "pode aplicar" do dono.
Não aplique SQL; se precisar de função nova, escreva no seu repositório e me devolva o caminho.

COMO FUNCIONA (desenho: lexsuiteone/documentacao/DESENHO-AREA-LOGADA-V2-2026-11-14.md, seções 2c e 2d)
- Hoje já existem os interruptores GLOBAIS (Controle dos apps → arquivos recursos/global.json e recursos/radar-judicial.json
  em solverone-dados). A lex-conta lê esses arquivos e devolve ao programa `recursos` {id: ligado}; o programa esconde o que
  tem data-recurso desligado.
- Novo: a licença ganha `lex_contas.recursos` (jsonb {id: true|false}); a lex-conta aplica a licença POR CIMA do global. Quem
  mexe é a ficha da licença no RootifyONE.
- Ids válidos: os declarados em lexsuiteone/docs/recursos-do-app.json (hoje `assistone`; a Arquitetura acrescenta `area-logada`
  e, depois, `chamados`). Só [a-z0-9.-], até 40 caracteres.
- O programa recebe o estado ao abrir, ao clicar em F5/Atualizar e, com a tela aberta, a cada 30 minutos (0.7.47); sem internet,
  vale o último estado conhecido. Ligar na ficha = o escritório vê em até 30 min ou ao reabrir.

O QUE FAZER NA TELA
1. Ficha da licença (Licenças do RADAR): bloco "Recursos desta licença" com um interruptor por recurso declarado, três estados
   visíveis: "segue o global (ligado/desligado)", "ligado nesta licença", "desligado nesta licença". Salvar por
   admin_lex_salvar({codigo, recursos: {...}, motivo}); ler de admin_lex_listar (campo `recursos`, que a Arquitetura acrescenta;
   até lá, trate ausência como {}).
2. Lista de licenças: etiqueta pequena quando algum recurso está forçado na licença (ex.: "área logada: desligada").
3. Controle dos apps (global): ao lado de cada recurso, "licenças com exceção: N" (a partir de admin_lex_listar).
4. Histórico: cada mudança vira evento licenca_alterada "recurso area-logada: ligado/desligado" (a função admin_lex_salvar já
   grava; mostre na linha do tempo da ficha).
5. Manual, AssistONE (ajuda, tour, busca: "recursos da licença", "área logada"), Novidades formais; termos e e-mails sem mudança.

CUIDADO COM SOBREPOSIÇÃO: a conversa da Produto do LexSuiteONE só marca os elementos do RADAR com data-recurso="area-logada" e
faz a conferência a cada 30 min; a Arquitetura faz a coluna, a lex-conta v19 e o recursos-do-app.json. Você faz só o RootifyONE.

Ao terminar, me devolva em até 10 linhas: versão publicada, o que entrou, e o caminho de qualquer SQL novo.
```
