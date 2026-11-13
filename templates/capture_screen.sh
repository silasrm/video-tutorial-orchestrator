#!/bin/bash
# TEMPLATE · Captura UMA tela do app/painel em PNG, com polling do seletor
# (resolve fades de framer-motion/animacoes de entrada que deixam o still esmaecido).
#
# Uso:
#   ./capture_screen.sh <URL> <SAIDA.png> [SELETOR] [LARGURA] [ALTURA] [ESPERA_POS]
# Exemplos:
#   ./capture_screen.sh "http://localhost:3000/painel/pedidos" assets/painel-pedidos.png "h1" 1440 900
#   ./capture_screen.sh "http://localhost:3000/menu"           assets/app-menu.png     "h1" 390 844  0.8
set -e
URL="$1"; OUT="$2"; SEL="${3:-h1}"; VW="${4:-1440}"; VH="${5:-900}"; POS="${6:-0.6}"
agent-browser set viewport "$VW" "$VH" >/dev/null
agent-browser open "$URL" >/dev/null
# polling: espera o conteudo real carregar (ate 12x1.2s ~ 14s) e a animacao de entrada terminar
for i in $(seq 1 12); do
  TXT=$(agent-browser eval "document.querySelector('$SEL')?.textContent || ''" 2>/dev/null || true)
  [ -n "$TXT" ] && break
  agent-browser wait 1.2 >/dev/null
done
agent-browser wait "$POS" >/dev/null
mkdir -p "$(dirname "$OUT")"
agent-browser screenshot "$OUT" >/dev/null
echo "capturado: $OUT"
