# Testes de tela (dados fictícios)

- `larguras.js` + `servidor_ficticio.py`: a tela em 4 larguras, sem sobra nas laterais nem texto cortado (`PORTA=8781 python servidor_ficticio.py pronto &` e `node larguras.js 8781 pasta-dos-prints`); "Ler o Diário agora" é desligado nesse servidor.
- `aviso_e_lupa.sh` (usa `aviso_e_lupa.js`, `servidor_aviso.py` e `guarda_rede.py`): aviso de planilha em uso (com e sem Excel, marcas RADAR e ZETA), lupa no app e na página offline, `/dados` com `Infinity` e `NaN` no `config.json`. Rode `bash robo/testes/tela/aviso_e_lupa.sh [pasta-dos-prints]` antes de cada envio que mexa em `radar_modelo.html`.
- Tudo com dados fictícios: os servidores sobem com o guarda de rede (`guarda_rede.py`) e o navegador só fala com 127.0.0.1; o roteiro falha se algo tentar sair. Se um texto de planilha em uso ou da lupa mudar, ajuste as expressões no começo de `aviso_e_lupa.js`.
