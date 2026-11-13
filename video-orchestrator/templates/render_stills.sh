#!/bin/bash
# TEMPLATE · Renderiza cada cena HTML em PNG 2560x1440 (body zoom 1.3333 => layout lógico 1920x1080).
# Uso: ./render_stills.sh            (todas as cenas)
#      ./render_stills.sh <video>    (só um vídeo)
set -e
shopt -s nullglob
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p "$ROOT/stills"
ONLY="${1:-}"
VW=$(${PYTHON:-python3} -c "import json;p=json.load(open('$ROOT/project.json')).get('render',{});print(p.get('still_vw',2560))")
VH=$(${PYTHON:-python3} -c "import json;p=json.load(open('$ROOT/project.json')).get('render',{});print(p.get('still_vh',1440))")
agent-browser set viewport "$VW" "$VH" >/dev/null
for f in "$ROOT"/scenes/*.html; do
  name=$(basename "$f" .html)
  [ -n "$ONLY" ] && case "$name" in "$ONLY"-*) ;; *) continue;; esac
  agent-browser open "file://$f" >/dev/null
  agent-browser wait 1 >/dev/null
  agent-browser screenshot "$ROOT/stills/${name}.png" >/dev/null
  echo "ok $name"
done
agent-browser close >/dev/null 2>&1 || true
echo "STILLS DONE"
