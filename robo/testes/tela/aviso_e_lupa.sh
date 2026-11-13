#!/bin/bash
# Roteiro de tela do aviso de planilha em uso, da lupa offline e do /dados com Infinity e NaN (revisão da 0.7.27).
# Dados FICTÍCIOS; nada sai do computador (os servidores rodam com guarda de rede e o navegador só fala com 127.0.0.1).
# Uso:  bash robo/testes/tela/aviso_e_lupa.sh [pasta-dos-prints]      (precisa de node + playwright + Chromium, como o larguras.js)
# Termina com código 0 só se "TUDO OK" e se o guarda de rede não registrou nenhuma tentativa de sair do computador.
AQUI=$(cd "$(dirname "$0")" && pwd)
ROBO=${ROBO:-$(cd "$AQUI/../.." && pwd)}
W=${W:-$(mktemp -d)}
OUT=${1:-$W/prints}
mkdir -p "$OUT" "$W/tmp"; : > "$W/guarda.log"; : > "$W/srv.log"
export TMPDIR=$W/tmp GUARDA_LOG=$W/guarda.log
PIDS=()
trap 'kill "${PIDS[@]}" 2>/dev/null' EXIT
sobe() { local p=$1; shift; env "$@" python3 -B "$AQUI/guarda_rede.py" "$AQUI/servidor_aviso.py" "$ROBO" "$W" "$p" >> "$W/srv.log" 2>&1 & PIDS+=($!); }
sobe 8801 SAIDA=1                                   # tudo normal (e grava a página offline)
sobe 8802 EM_USO=1                                  # planilha aberta em outro lugar, com Excel
sobe 8803 EM_USO=1 SEM_EXCEL=1                      # idem, sem Excel
sobe 8804 EM_USO=1 CURTO=ZETA                       # idem, outra marca
sobe 8805 EM_USO=1 SEM_EXCEL=1 CURTO=ZETA
sobe 8806 'RADAR_RAW="valor_minimo": Infinity, "dias_na_pagina": NaN, "teto_capital_gigante": -Infinity'
sobe 8807 'RADAR_RAW="valor_minimo": 1000.5, "dias_na_pagina": 3, "teto_capital_gigante": 5000000'
cd "$AQUI"; PORTA=8781 python3 -B guarda_rede.py servidor_ficticio.py pronto >> "$W/srv.log" 2>&1 & PIDS+=($!); cd - > /dev/null  # 0.7.43: sem subshell, para o kill do fim pegar o servidor (antes ficava aberto)   # o servidor das larguras (a leitura do Diário é desligada nele)
for i in $(seq 1 60); do [ "$(grep -c '^pronto' "$W/srv.log")" -ge 8 ] && break; sleep 0.5; done
cat "$W/srv.log"
node "$AQUI/aviso_e_lupa.js" 8801 8802 8803 8804 8805 "$OUT" "$W/prog_8801/saida/radar/radar.html" 8806 8807 8781 2>&1 | tee "$W/saida.txt"
RC=${PIPESTATUS[0]}
if grep -v "guarda ativa" "$W/guarda.log" | grep -q .; then echo "--- O GUARDA DE REDE REGISTROU TENTATIVA DE SAIR DO COMPUTADOR:"; grep -v "guarda ativa" "$W/guarda.log"; RC=1; fi
echo "prints em: $OUT | registros em: $W"
exit $RC
