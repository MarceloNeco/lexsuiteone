# Testes de tela (dados fictícios)

- `larguras.js` + `servidor_ficticio.py`: a tela em 4 larguras, sem sobra nas laterais nem texto cortado (`PORTA=8781 python servidor_ficticio.py pronto &` e `node larguras.js 8781 pasta-dos-prints`); "Ler o Diário agora" é desligado nesse servidor.
- `aviso_e_lupa.sh` (usa `aviso_e_lupa.js`, `servidor_aviso.py` e `guarda_rede.py`): aviso de planilha em uso (com e sem Excel, marcas RADAR e ZETA), lupa no app e na página offline, `/dados` com `Infinity` e `NaN` no `config.json`. Rode `bash robo/testes/tela/aviso_e_lupa.sh [pasta-dos-prints]` antes de cada envio que mexa em `radar_modelo.html`.
- Tudo com dados fictícios: os servidores sobem com o guarda de rede (`guarda_rede.py`) e o navegador só fala com 127.0.0.1; o roteiro falha se algo tentar sair. Se um texto de planilha em uso ou da lupa mudar, ajuste as expressões no começo de `aviso_e_lupa.js`.
- `fluxos.js` (0.7.42, regressão pedida pelo dono): o uso do dia a dia na tela de verdade, com a rede lenta de propósito:
  salvar e reabrir as Configurações (o que foi salvo aparece na hora; o Salvar gira; mudar só o aviso não regrava pasta nem
  agendamento), busca da Lista (1 letra não filtra, sem acento acha com acento, apagar volta tudo), período trocado duas
  vezes seguidas, Painel com riscos e "Limpar filtros". Uso: `PORTA=8781 python3 -B guarda_rede.py servidor_ficticio.py pronto &`
  e `node fluxos.js`. Cada defeito achado pelo dono vira uma conferência nova aqui.
- `rodar_tudo.sh`: TODOS os testes de uma vez (unittest, `fluxos.js`, `ver_na_lista.js`, `larguras.js`, `aviso_e_lupa.sh`),
  com o guarda de rede. `bash robo/testes/tela/rodar_tudo.sh [pasta-dos-prints]`. Obrigatório antes de cada
  "pronta para revisão" (Produto) e na revisão (Operação); termina com "TUDO OK" ou "HÁ FALHAS".

