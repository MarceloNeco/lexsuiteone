#!/bin/bash
# 0.7.41 (dono, 13/Nov: "tem que ter um regression"): TODOS os testes de uma vez, antes de cada "pronta para revisão".
# 1) testes do programa (unittest); 2) a tela de verdade no navegador, com dados FICTÍCIOS e guarda de rede:
#    fluxos.js (o uso do dia a dia: salvar e reabrir as Configurações, busca, período, Painel/Lista, Limpar filtros, com a
#    rede lenta de propósito), ver_na_lista.js (o total de cada cartão bate com a Lista), larguras.js (4 larguras, sem
#    texto cortado) e aviso_e_lupa.sh (planilha em uso, lupa offline, config.json estragado).
# Uso: bash robo/testes/tela/rodar_tudo.sh [pasta-dos-prints]     Termina com código 0 só se tudo passar.
AQUI=$(cd "$(dirname "$0")" && pwd)
ROBO=$(cd "$AQUI/../.." && pwd)
OUT=${1:-$(mktemp -d)/prints}; mkdir -p "$OUT"
W=$(mktemp -d); RC=0; RES=()
export PORTA=${PORTA:-8781}   # outra porta se a 8781 estiver ocupada: PORTA=8791 bash rodar_tudo.sh
passo() { local nome=$1; shift; echo "=== $nome"; if "$@" > "$W/$nome.txt" 2>&1; then RES+=("OK      $nome"); else RES+=("FALHOU  $nome (detalhe: $W/$nome.txt)"); RC=1; fi; tail -5 "$W/$nome.txt"; }
passo unittest bash -c "cd '$ROBO' && python3 -m unittest discover -s testes"
export GUARDA_LOG=$W/guarda.log; : > "$GUARDA_LOG"
if (exec 3<>/dev/tcp/127.0.0.1/$PORTA) 2>/dev/null; then echo "A porta $PORTA já está em uso (outro servidor de teste?). Feche-o ou use PORTA=8791."; exit 2; fi
cd "$AQUI"; python3 -B guarda_rede.py servidor_ficticio.py pronto > "$W/srv.log" 2>&1 & SRV=$!; cd - > /dev/null   # sem subshell: o kill pega o servidor certo
trap 'kill $SRV 2>/dev/null' EXIT
for i in $(seq 1 60); do grep -q '^pronto' "$W/srv.log" && break; sleep 0.5; done
passo fluxos node "$AQUI/fluxos.js"
passo ver_na_lista node "$AQUI/ver_na_lista.js"
passo larguras node "$AQUI/larguras.js" $PORTA "$OUT"
kill $SRV 2>/dev/null; wait $SRV 2>/dev/null
passo aviso_e_lupa bash "$AQUI/aviso_e_lupa.sh" "$OUT"
if grep -v "guarda ativa" "$GUARDA_LOG" | grep -q .; then RES+=("FALHOU  guarda de rede: algo tentou sair do computador"); RC=1; fi
echo; printf '%s\n' "${RES[@]}"; echo "prints em: $OUT"
[ $RC = 0 ] && echo "TUDO OK" || echo "HÁ FALHAS"
exit $RC
