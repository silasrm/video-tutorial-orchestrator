---
name: video-orchestrator
description: Orquestrador de produção de vídeos de produto (showcase e tutoriais por módulo) — gera ROADMAP, roteiros individuais, captura telas reais do app/painel com interação, monta cenas HTML com legendas e renderiza MP4 16:9 + SRT + roteiro via ffmpeg. Use quando o usuário pedir "vídeos de showcase", "vídeos de demonstração", "tutoriais em vídeo por módulo/tela/funcionalidade", com legenda, para um app ou painel web.
---

# VIDEO ORCHESTRATOR — Showcase & Tutoriais de produto

Você (agente) é o **produtor de vídeo**. Este skill transforma um app/painel web em uma série de vídeos MP4 16:9 (1920×1080, 30fps) com legendas embutidas na cena + arquivos SRT. Nenhum editor humano é necessário: você escreve o plano, captura as telas, gera as cenas e renderiza com ffmpeg.

**Dois tipos de vídeo suportados:**

| | SHOWCASE | TUTORIAL |
|---|---|---|
| Granularidade | 1 vídeo por **superfície** (app inteiro / painel inteiro) | 1 vídeo por **item de menu / módulo** |
| Tom | Marketing, benefícios | Ensino, passo a passo de uso real |
| Cenas | Tela estática de cada funcionalidade | Estado **depois** de cada ação do usuário (clique, cadastro, edição) |
| Kicker | Nome da funcionalidade (`CARDÁPIO`) | `PASSO N · ação` (`PASSO 3 · ACEITAR PEDIDO`) |
| Duração típica | 40–65s | 30–60s por módulo |
| Estrutura | intro + features + outro | abertura + passos + encerramento (próximo módulo) |

Os dois tipos usam **o mesmo pipeline** de 9 fases abaixo.

---

## FASE 0 — Bootstrap (faça primeiro, sempre)

1. **Copie os templates** para o diretório de trabalho do projeto:
   ```bash
   mkdir -p scripts/video/{assets,scenes,fonts,stills,work}
   cp <pasta-da-skill>/templates/gen_scenes.py scripts/video/
   cp <pasta-da-skill>/templates/compose.py scripts/video/
   cp <pasta-da-skill>/templates/render_stills.sh scripts/video/
   cp <pasta-da-skill>/templates/capture_screen.sh scripts/video/
   cp <pasta-da-skill>/fonts/*.ttf scripts/video/fonts/
   cp scripts/video/fonts/*.ttf scripts/video/assets/   # gen_scenes resolve ../assets
   chmod +x scripts/video/*.sh
   cp <pasta-da-skill>/templates/project.example.json scripts/video/project.json
   ```
2. **Verifique as dependências** (falhou? instale antes de prosseguir):
   ```bash
   ffmpeg -version | head -1            # >= 6.0
   agent-browser --help >/dev/null && echo browser-automation OK
   python3 --version                    # >= 3.8
   ```
   *Fallback sem agent-browser:* use Playwright (`chromium.launch(headless=True)`, `page.set_viewport_size`, `page.goto`, `page.screenshot`) — o contrato é o mesmo: viewport 2560×1440 para cenas, viewport do produto para capturas.
3. **Preencha `project.json`**: marca, paleta (brand/dark/cream/muted/green), `outputs.dir` (caminho ABSOLUTO em `download/`, ex.: `/home/…/download/videos-tutoriais-painel`), `outputs.prefix` (`showcase` ou `tutorial`), e `captures` com viewport e URL base de cada superfície.
4. **Confirme que o app alvo responde**: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/painel` → 200. Se não estiver no ar, suba o dev server antes de qualquer captura.

**GATE 0:** templates no lugar, dependências OK, `project.json` preenchido, app respondendo.

---

## FASE 1 — Mapeamento do produto (descoberta)

Abra o produto no browser headless e construa um mapa de telas/fluxos. Exemplo com agent-browser:

```bash
agent-browser set viewport 1440 900
agent-browser open "http://localhost:3000/painel"
agent-browser wait 2
agent-browser snapshot -i -c          # refs @eNN do menu lateral e dos botões
agent-browser eval "document.querySelector('h1')?.textContent"
```

Registre em `scripts/video/MAPA.md`:
- **Lista exata dos itens do menu lateral** (ordem = ordem dos tutoriais);
- Para cada módulo: rota (URL), ação principal (ex.: "clique no pedido → modal abre"), botões de confirmação, estados resultantes;
- Fluxos com formulário: campos, labels, valores de teste realistas para preencher.

**GATE 1:** você sabe listar todos os módulos e descrever, para cada um, a sequência cliques→resultado que um usuário faria.

---

## FASE 2 — ROADMAP (plano-mestre)

Copie `templates/ROADMAP.template.md` → `download/<conjunto>/ROADMAP.md` e preencha:
- 1 linha por vídeo (showcase: 1 por superfície; tutorial: 1 por item de menu);
- Colunas: `#`, `id do vídeo`, `módulo`, "o que o usuário aprende", nº de passos, duração alvo, status;
- Ordem dos tutoriais = ordem do menu lateral;
- Status tem 5 estágios: planejado → roteirizado → capturado → renderizado → **entregue**.

**GATE 2:** ROADMAP completo; se a série for grande (>6 vídeos), mostre o plano ao usuário antes de produzir.

---

## FASE 3 — Roteiros individuais (1 por vídeo)

Copie `templates/ROTEIRO.template.md` → `download/<conjunto>/roteiros/roteiro-<id>.md` e escreva a **narrativa real** (nada de lorem ipsum — use nomes, números e produtos do próprio projeto):

- **Tutoriais**: cada cena = 1 passo executável. O texto da legenda responde "o que eu faço agora?" — verbo no imperativo, concreto: "Clique no pedido #1024 para abrir o detalhe".
- **Showcase**: cada cena = 1 funcionalidade com benefício de negócio: "Nenhum pedido passa batido".
- `title`: máx. 2 linhas (`<br>`), palavra-chave em `<em>`; `desc`: 1–2 frases; `chips`: 2–3 selos curtos;
- **Alterne `side` do dispositivo entre cenas** (right, left, right…) — dá ritmo ao zoompan;
- Durações: intro 3.5–4.5s · passo 4.0–5.0s · encerramento 4.5–5.5s. Soma = duração alvo.

**GATE 3:** todo vídeo do ROADMAP tem roteiro com tempos somados e capturas listadas.

---

## FASE 4 — Captura das telas (o passo que define a qualidade)

### 4a. Telas estáticas (showcase, aberturas)
```bash
scripts/video/capture_screen.sh "http://localhost:3000/painel/pedidos" \
  scripts/video/assets/tut-pedidos-capa.png "h1" 1440 900
```
O script já faz **polling do seletor** (até ~14s) — obrigatório porque animações de entrada (framer-motion/CSS) deixam o screenshot esmaecido se tirado cedo demais.

### 4b. Interação real (tutoriais — um PNG por passo)
Para cada passo do roteiro, execute a ação e capture o estado resultante:
```bash
agent-browser set viewport 1440 900
agent-browser open "http://localhost:3000/painel/pedidos"
agent-browser wait 2
agent-browser snapshot -i -c                      # mapeia refs @eNN
agent-browser click @e142                         # ex.: abrir o pedido
agent-browser wait 1.5                            # transição abrir
agent-browser eval "document.querySelector('h1,h2')?.textContent || document.body.innerText.slice(0,80)"
agent-browser screenshot scripts/video/assets/tut-pedidos-p02.png
```
Regras de captura:
1. **Estado DEPOIS da ação** (a legenda descreve a ação; a imagem prova o resultado);
2. Dados visíveis e realistas (pedido preenchido, modal aberto, item salvo na lista);
3. Sem overlays transitórios (toasts de loading, spinners) — espere eles sumirem;
4. Nomes previsíveis: `<video>-p<NN>.png` e `<video>-capa.png`;
5. Se a ação altera dados (cadastro/edição), prefira um item de teste e desfaça/ignore depois — nunca corrompa dados reais;
6. **QA imediato**: leia cada PNG assim que capturar. Reprovar se: tela esmaecida, texto cortado, modal vazio, notificação cobrindo o conteúdo, resolução errada.

**GATE 4:** todo `img` citado nos roteiros existe em `assets/` e passou no QA visual.

---

## FASE 5 — scenes/<video>.json (roteiro → dados)

Para cada vídeo, escreva `scripts/video/scenes/<id>.json` no schema do `templates/scenes.example.json`:
- `_meta.label` (ex.: `TUTORIAL · PAINEL — PEDIDOS`);
- Cenas `intro` / `feature` / `outro` com `id, dur, kicker, title, desc, chips, device, img, side, counter, url, bignum`;
- `counter` em features: `"01/08"` sequencial; `bignum`: sigla do passo (ex.: `P01`) ou nome curto do módulo.

Valide: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('scripts/video/scenes/*.json')]" && echo JSON OK`

---

## FASE 6 — Cenas HTML (gen_scenes.py)

```bash
cd scripts/video && python3 gen_scenes.py <video>
```
Gera `scenes/<video>-<cena>.html` (legenda embutida no HTML — **nunca overlay de imagem**, pois screenshots são opacos) + `manifest.json`.

**GATE 6:** todos os HTMLs gerados; abra 1 deles renderizado (fase 7) e confira: legenda no lado oposto ao dispositivo, título ≤2 linhas, chips não colidem com o aparelho.

---

## FASE 7 — Render (stills → MP4 por cena → concat)

```bash
cd scripts/video
./render_stills.sh <video>                       # PNG 2560×1440 por cena
python3 compose.py render <video> 0 3            # LOTES de 2–4 cenas por vez
python3 compose.py render <video> 3 6
python3 compose.py render <video> 6 99
python3 compose.py audit <video>                 # ffprobe: duração de cada MP4
python3 compose.py concat <video>                # final + SRT + roteiro.txt
```
- `render`: zoompan 1.05 **alternado** (cena par aproxima, ímpar afasta) + fade in/out 0,35s para o escuro da marca + `yuv420p veryfast crf18` 1920×1080 30fps;
- `concat`: **concat demuxer com `-c copy -movflags +faststart`** — os fades fazem as emendas. NÃO use `xfade`: trava em CPU limitada.

### ⚠️ Regras de sobrevivência do render (CPU instável)
1. Renderize em **lotes pequenos** (2–4 cenas); nunca dispare tudo de uma vez;
2. Timeout do comando pode estourar MESMO COM o ffmpeg completando — **sempre verifique com `compose.py audit <video>` ou `ls -la work/` antes de re-renderizar**; não confie no exit code;
3. Se um MP4 do work estiver truncado (audit marca CURTO), re-renderize só aquele índice;
4. Rode `audit` antes de cada `concat`; se faltar cena, complete os lotes.

**GATE 7:** `audit` mostra todas as cenas OK + FINAL existente.

---

## FASE 8 — QA final e entrega

1. **Inspecione o MP4 visualmente** (extraia frames baixos, não leia o vídeo direto):
   ```bash
   ffmpeg -y -i "download/<conjunto>/<prefix>-<video>-16x9.mp4" \
     -vf "fps=1/6,scale=480:-1" /tmp/render/qa-<video>-%02d.jpg
   ```
   Leia 4–6 frames. Reprovar se: texto cortado, legenda sob o dispositivo, tela preta além do fade, cena repetida, placeholder visível.
2. **Confira o SRT**: abra `legendas-<video>.srt`, tempos crescentes, texto igual ao roteiro.
3. **Arquivos entregues por vídeo** em `outputs.dir`:
   - `<prefix>-<video>-16x9.mp4`
   - `legendas-<video>.srt`
   - `roteiro-<video>.txt`
4. Atualize o status no ROADMAP (☐ entregue) e siga para o próximo vídeo.

**DEFINITION OF DONE da série:** todos os vídeos do ROADMAP com os 3 arquivos + QA visual aprovado + ROADMAP 100% entregue.

---

## Armadilhas conhecidas (aprendidas em produção)

| Sintoma | Causa | Correção |
|---|---|---|
| Screenshot esmaecido/lavado | animação de entrada em andamento | polling do seletor (`capture_screen.sh`) antes do screenshot |
| Legenda com fundo branco sobre a cena | tentar overlay PNG transparente | legendas embutidas no HTML da cena (screenshots são opacos) |
| Legenda colidindo com o aparelho | lados iguais | `side` do dispositivo define o lado OPOSTO da legenda (automático) |
| Render trava no fim sem terminar | xfade chain + CPU limitada | fade in/out por cena + concat `-c copy` |
| Comando ffmpeg "falha" mas arquivo OK | wrapper expira antes do processo | verificar com `audit`/`ls`; re-renderizar só o faltante |
| Vídeo final com 1 cena ou não abre | concat nunca rodou / MP4 truncado | `audit` antes do `concat`; render em lotes pequenos |
| Fonte não aplica nas cenas | caminho relativo quebrado | convenção `fonts/` e `assets/` dentro de `scripts/video/`; paths absolutos no bash |
| `file://` não abre a cena | caminho relativo no `open` | sempre `file://$ROOT/scenes/arquivo.html` com ROOT absoluto |
| Motion sickness / estático demais | zoom sempre na mesma direção | zoompan alternado par/ímpar (já no compose.py) |

## Estrutura de arquivos esperada

```
scripts/video/
├── project.json          # config do projeto (paleta, marca, saída, capturas)
├── gen_scenes.py         # roteiro -> cenas HTML
├── render_stills.sh      # cenas HTML -> stills 2560×1440
├── compose.py            # stills -> MP4 por cena -> final + SRT + roteiro
├── capture_screen.sh     # app -> PNG com polling de seletor
├── assets/               # capturas do produto + fontes .ttf
├── scenes/               # <video>.json (fonte da verdade) + HTMLs + manifest
├── stills/ work/         # intermediários
download/<conjunto>/
├── ROADMAP.md  roteiros/*.md
├── <prefix>-<video>-16x9.mp4  legendas-<video>.srt  roteiro-<video>.txt
```

## Cheat sheet de comando por fase

```bash
# 0 setup       cp templates + fonts -> scripts/video/ ; editar project.json
# 1 mapeamento  agent-browser open <url> && snapshot -i -c
# 2-3 planos    ROADMAP.md + roteiros/*.md
# 4 captura     capture_screen.sh <url> <png> "h1" 1440 900   (ou clique+screenshot por passo)
# 5 dados       scenes/<video>.json
# 6 cenas       python3 gen_scenes.py <video>
# 7 render      ./render_stills.sh <video> ; compose.py render em lotes ; audit ; concat
# 8 qa          ffmpeg fps=1/6 scale=480 -> ler frames ; conferir SRT ; atualizar ROADMAP
```
