#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEMPLATE · Gerador de cenas HTML (1920x1080 lógico) — data-driven.

Lê:
  ./project.json          -> marca, paleta, fontes, saída
  ./scenes/<video>.json   -> lista de cenas (intro/feature/outro)

Escreve:
  ./scenes/<video>-<id>.html  (um HTML por cena)
  ./scenes/manifest.json      (índice id/dur/kind/kicker/title/desc)

Uso:
  python3 gen_scenes.py                # gera todos os vídeos
  python3 gen_scenes.py <video>        # gera só um vídeo

Cena (scenes/<video>.json) — campos aceitos:
  _meta.label     título do vídeo para roteiro/SRT
  kind: "intro" | "feature" | "outro"
  id, dur (segundos), kicker, title (aceita <br> e <em>), desc, chips[]
  device: "browser" | "phone" | null        (intro/feature)
  img: "<arquivo>.png" em ./assets/          (intro/feature)
  side: "left" | "right"                     (lado do DISPOSITIVO; legenda vai no oposto)
  counter: "01/08"                           (feature; omitir p/ esconder)
  url: "rota-mostrada-na-barra"              (browser)
  bignum: "PEDIDOS"                          (texto gigante vazado; default = id)
  floats: [{ "style": "right:520px; top:150px", "text": "...", "color": "green"|"brand" }]
  cta, note                                  (outro)
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "scenes")
os.makedirs(OUT, exist_ok=True)

P = json.load(open(os.path.join(BASE, "project.json")))
PAL = P["palette"]
FONTS = P.get("fonts", {"anton": "Anton.ttf", "archivo": "ArchivoBlack.ttf", "inter": "Inter.ttf"})
ASSETS = "../assets"  # relativo a OUT (convenção: BASE/assets e BASE/scenes)

BASE_CSS = f"""
@font-face {{ font-family:'Anton'; src:url('{ASSETS}/{FONTS["anton"]}') format('truetype'); font-weight:400; }}
@font-face {{ font-family:'Archivo Black'; src:url('{ASSETS}/{FONTS["archivo"]}') format('truetype'); }}
@font-face {{ font-family:'Inter'; src:url('{ASSETS}/{FONTS["inter"]}') format('truetype'); font-weight:400; }}
@font-face {{ font-family:'Inter'; src:url('{ASSETS}/{FONTS["inter"]}') format('truetype'); font-weight:700; }}
:root {{
  --brand:{PAL["brand"]}; --dark:{PAL["dark"]}; --cream:{PAL["cream"]};
  --muted:{PAL["muted"]}; --green:{PAL["green"]}; --line:{PAL["line"]};
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#000; zoom:1.3333333; }}
.stage {{ width:1920px; height:1080px; position:relative; overflow:hidden;
  background:var(--dark); font-family:'Inter',sans-serif; }}
.grid {{ position:absolute; inset:0;
  background-image:linear-gradient(rgba(255,246,238,.032) 1px, transparent 1px),
                   linear-gradient(90deg, rgba(255,246,238,.032) 1px, transparent 1px);
  background-size:120px 120px; }}
.glow {{ position:absolute; width:1050px; height:1050px; border-radius:50%;
  background:radial-gradient(closest-side, rgba(232,85,45,.17), transparent 72%); }}
.glow.g2 {{ background:radial-gradient(closest-side, rgba(232,85,45,.09), transparent 70%); }}
.bignum {{ position:absolute; font-family:'Anton'; font-size:470px; line-height:1; color:transparent;
  -webkit-text-stroke:2.5px rgba(232,85,45,.15); letter-spacing:.02em; user-select:none; }}
.brandbar {{ position:absolute; left:64px; bottom:44px; display:flex; align-items:center; gap:14px; z-index:8; }}
.logomark {{ width:44px; height:44px; border-radius:12px; background:var(--brand); color:#fff;
  font-family:'Archivo Black'; font-size:19px; display:flex; align-items:center; justify-content:center; }}
.brandname {{ color:var(--cream); font-weight:700; font-size:17px; letter-spacing:.02em; }}
.brandtag {{ color:var(--muted); font-size:14.5px; }}
.count {{ position:absolute; left:64px; bottom:110px; z-index:8; font-family:'Archivo Black';
  font-size:14px; letter-spacing:.18em; color:#8A7F73; }}
.phone {{ position:absolute; z-index:6; filter:drop-shadow(0 46px 70px rgba(0,0,0,.62)); }}
.phone .body {{ width:476px; border-radius:58px; border:13px solid #0B0908; background:#0B0908;
  box-shadow:0 0 0 2px rgba(232,85,45,.35), inset 0 0 0 2px rgba(255,246,238,.06); overflow:hidden; }}
.phone img {{ display:block; width:450px; height:auto; }}
.phone .notch {{ position:absolute; top:24px; left:50%; transform:translateX(-50%);
  width:132px; height:24px; background:#0B0908; border-radius:999px; z-index:9; }}
.browser {{ position:absolute; z-index:6; width:1084px; border-radius:18px; overflow:hidden;
  background:#1E1913; border:1.5px solid #3A322B;
  box-shadow:0 46px 80px rgba(0,0,0,.6), 0 0 0 2px rgba(232,85,45,.28); }}
.browser .bar {{ height:52px; display:flex; align-items:center; gap:8px; padding:0 18px; background:#221C16; }}
.browser .dot {{ width:13px; height:13px; border-radius:50%; }}
.browser .url {{ flex:1; margin-left:12px; height:30px; border-radius:8px; background:#15110D;
  border:1px solid #3A322B; display:flex; align-items:center; padding:0 14px; gap:8px;
  color:#8A7F73; font-size:13.5px; font-family:'Inter'; }}
.browser .url b {{ color:#E8D9CB; font-weight:600; }}
.browser img {{ display:block; width:1084px; height:auto; }}
.floatchip {{ position:absolute; z-index:9; background:#0F0C0A; border:1.5px solid #3A322B;
  border-radius:14px; padding:12px 18px; display:flex; align-items:center; gap:10px;
  box-shadow:0 18px 40px rgba(0,0,0,.55); }}
.floatchip .dotl {{ width:11px; height:11px; border-radius:50%; }}
.floatchip span {{ color:var(--cream); font-size:15px; font-weight:700; letter-spacing:.01em; }}
"""

CAP_CSS = f"""
@font-face {{ font-family:'Anton'; src:url('{ASSETS}/{FONTS["anton"]}') format('truetype'); font-weight:400; }}
@font-face {{ font-family:'Archivo Black'; src:url('{ASSETS}/{FONTS["archivo"]}') format('truetype'); }}
@font-face {{ font-family:'Inter'; src:url('{ASSETS}/{FONTS["inter"]}') format('truetype'); font-weight:400; }}
@font-face {{ font-family:'Inter'; src:url('{ASSETS}/{FONTS["inter"]}') format('truetype'); font-weight:700; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; zoom:1.3333333; }}
.stage {{ width:1920px; height:1080px; position:relative; font-family:'Inter',sans-serif; }}
.capblock {{ position:absolute; top:242px; left:128px; width:700px; }}
.capblock.right {{ left:1196px; width:640px; }}
.kicker {{ display:inline-flex; align-items:center; gap:10px; background:var(--brand); color:#fff;
  font-family:'Archivo Black'; font-size:15px; letter-spacing:.16em; padding:12px 20px; border-radius:999px; }}
.kicker .kdot {{ width:8px; height:8px; border-radius:50%; background:#fff; opacity:.85; }}
h2 {{ font-family:'Anton'; font-weight:400; color:var(--cream); font-size:76px; line-height:1.05;
  text-transform:uppercase; letter-spacing:.005em; margin-top:26px; }}
h2 em {{ font-style:normal; color:var(--brand); }}
.desc {{ margin-top:24px; color:var(--muted); font-size:23.5px; line-height:1.56; max-width:640px; }}
.chips {{ margin-top:30px; display:flex; flex-wrap:wrap; gap:12px; max-width:680px; }}
.chip {{ display:inline-flex; align-items:center; gap:9px; border:1.5px solid #3D342C; border-radius:999px;
  padding:11px 19px; color:#E8D9CB; font-size:15.5px; font-weight:600; background:rgba(255,246,238,.03); }}
.chip .cdot {{ width:9px; height:9px; border-radius:50%; }}
.chip .cdot.g {{ background:var(--green); }} .chip .cdot.o {{ background:var(--brand); }}
"""


def html(doc_css, inner):
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{doc_css}</style></head><body>{inner}</body></html>"


def device_block(s):
    img, side = s["img"], s.get("side", "right")
    floats = "".join(
        f"<div class='floatchip' style='{f['style']}'>"
        f"<span class='dotl' style='background:var(--{'green' if f.get('color') == 'green' else 'brand'})'></span>"
        f"<span>{f['text']}</span></div>"
        for f in s.get("floats", []))
    if s.get("device") == "phone":
        pos = "left:66px" if side == "left" else "right:66px"
        glow_x = "right:-190px" if side == "right" else "left:-190px"
        return (f"<div class='grid'></div>"
                f"<div class='glow' style='{glow_x}; top:-40px'></div>"
                f"{device_deco(side, s)}{floats}"
                f"<div class='phone' style='{pos}; top:{s.get('top', 54)}px'>"
                f"<div class='body'><img src='{ASSETS}/{img}'></div><div class='notch'></div></div>")
    pos = "left:66px" if side == "left" else "right:66px"
    glow_x = "right:-190px" if side == "right" else "left:-190px"
    site = P.get("brand", {}).get("site", "meusite.com")
    return (f"<div class='grid'></div>"
            f"<div class='glow' style='{glow_x}; top:-30px'></div>"
            f"{device_deco(side, s)}{floats}"
            f"<div class='browser' style='{pos}; top:{s.get('top', 96)}px'>"
            f"<div class='bar'>"
            f"<span class='dot' style='background:#E5484D'></span>"
            f"<span class='dot' style='background:#D99425'></span>"
            f"<span class='dot' style='background:#2FBF71'></span>"
            f"<div class='url'><span style='color:#2FBF71'>●</span> <b>{site}</b>/{s.get('url', '')}</div>"
            f"</div><img src='{ASSETS}/{img}'></div>")


def device_deco(side, s):
    """Glows secundárias + bignum do lado do dispositivo (legenda fica no oposto)."""
    g2x = "left:170px" if side == "right" else "right:170px"
    num_x = "right:110px" if side == "right" else "left:100px"
    big = s.get("bignum") or s["id"]
    return (f"<div class='glow g2' style='{g2x}; bottom:-330px'></div>"
            f"<div class='bignum' style='{num_x}; bottom:-64px'>{str(big).upper()}</div>")


def chips_html(chips):
    dots = ["o", "g", "o"]
    return "".join(
        f"<span class='chip'><span class='cdot {dots[i % 3]}'></span>{c}</span>"
        for i, c in enumerate(chips or []))


def cap_block(n_total, idx, s, big=False):
    side_cls = " right" if s.get("side", "right") == "left" else ""
    size = "font-size:104px" if big else ""
    return (f"<div class='capblock{side_cls}'>"
            f"<div class='kicker'><span class='kdot'></span> {s.get('kicker', '')}</div>"
            f"<h2 style='{size}'>{s.get('title', '')}</h2>"
            f"<p class='desc'>{s.get('desc', '')}</p>"
            f"<div class='chips'>{chips_html(s.get('chips'))}</div></div>")


def brandbar():
    b = P.get("brand", {})
    return (f"<div class='brandbar'><div class='logomark'>{b.get('initials', '')}</div>"
            f"<div><div class='brandname'>{b.get('name', '')}</div>"
            f"<div class='brandtag'>{b.get('tagline', '')}</div></div></div>")


def scene_html(s, n_features, idx):
    kind = s["kind"]
    if kind == "outro":
        inner = (f"<div class='grid'></div>"
                 f"<div class='glow' style='left:435px; top:-40px'></div>"
                 f"<div class='glow g2' style='left:535px; bottom:-420px'></div>"
                 f"<div style='position:absolute; inset:0; display:flex; flex-direction:column;"
                 f"align-items:center; justify-content:center; text-align:center; z-index:7'>"
                 f"<div class='kicker'><span class='kdot'></span> {s.get('kicker', '')}</div>"
                 f"<h2 style='font-size:112px; margin-top:34px'>{s.get('title', '')}</h2>"
                 f"<div class='chips' style='justify-content:center; margin-top:40px'>{chips_html(s.get('chips'))}</div>"
                 f"<div style='margin-top:52px; display:inline-flex; align-items:center; gap:14px;"
                 f"background:var(--brand); color:#fff; font-family:\"Archivo Black\"; font-size:22px;"
                 f"letter-spacing:.06em; padding:24px 44px; border-radius:999px;"
                 f"box-shadow:0 24px 60px rgba(232,85,45,.35)'>{s.get('cta', 'Começar agora')} →</div>"
                 f"<p style='margin-top:40px; color:var(--muted); font-size:19px'>{s.get('note', '')}</p>"
                 f"</div>{brandbar()}")
        return html(f"<style>{BASE_CSS}{CAP_CSS}</style>", f"<div class='stage'>{inner}</div>")
    if kind == "intro":
        dev = device_block(s) if s.get("img") else "<div class='grid'></div>"
        cap = cap_block(n_features, 0, s, big=True)
        counter = f"<div class='count'>{s['counter']}</div>" if s.get("counter") else ""
        return html(f"<style>{BASE_CSS}{CAP_CSS}</style>",
                    f"<div class='stage'>{dev}{cap}{brandbar()}{counter}</div>")
    # feature
    dev = device_block(s)
    cap = cap_block(n_features, idx, s)
    counter = f"<div class='count'>{s['counter']}</div>" if s.get("counter") else ""
    return html(f"<style>{BASE_CSS}{CAP_CSS}</style>",
                f"<div class='stage'>{dev}{cap}{brandbar()}{counter}</div>")


def gen_video(video):
    data = json.load(open(os.path.join(BASE, "scenes", f"{video}.json")))
    scenes = data["scenes"]
    features = [s for s in scenes if s["kind"] == "feature"]
    fi = 0
    for s in scenes:
        if s["kind"] == "intro":
            content = scene_html(s, len(features), 0)
        elif s["kind"] == "outro":
            content = scene_html(s, len(features), len(features) + 1)
        else:
            fi += 1
            content = scene_html(s, len(features), fi)
        path = f"{OUT}/{video}-{s['id']}.html"
        with open(path, "w") as f:
            f.write(content)
        print(f"  cena {path}", flush=True)
    manifest_path = f"{OUT}/manifest.json"
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    manifest[video] = [{"id": s["id"], "dur": s["dur"], "kind": s["kind"],
                        "kicker": s.get("kicker", ""), "title": s.get("title", ""),
                        "desc": s.get("desc", ""), "chips": s.get("chips", [])}
                       for s in scenes]
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    return len(scenes)


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = {}
    for vf in sorted(os.listdir(os.path.join(BASE, "scenes"))):
        if vf.endswith(".json") and not vf.startswith("_") and vf != "manifest.json":
            v = vf[:-5]
            if only and v != only:
                continue
            total[v] = gen_video(v)
    print(f"Cenas geradas: {total}", flush=True)
