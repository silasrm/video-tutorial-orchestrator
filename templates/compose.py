#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEMPLATE · Renderizador de vídeo (estratégia robusta para CPU limitada):
zoompan 1.05 alternado + fade in/out para o escuro da marca em cada cena
-> concat em stream-copy (xfade trava em sandboxes lentas — NÃO usar).

Lê: ./project.json, ./scenes/<video>.json, ./stills/<video>-<id>.png
Escreve: ./work/<video>-<id>.mp4, <outdir>/<prefixo>-<video>-16x9.mp4,
         <outdir>/legendas-<video>.srt, <outdir>/roteiro-<video>.txt

Uso:
  python3 compose.py render <video> <inicio> <fim>   # cenas [inicio, fim) — use LOTES de 2-4
  python3 compose.py concat <video>                  # concatena + SRT + roteiro
  python3 compose.py audit <video>                   # ffprobe dos MP4s (work + final)
"""
import json, os, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
STILLS = os.path.join(BASE, "stills")
WORK = os.path.join(BASE, "work")
os.makedirs(WORK, exist_ok=True)

P = json.load(open(os.path.join(BASE, "project.json")))
OUTDIR = P["outputs"]["dir"]
PREFIX = P["outputs"].get("prefix", "video")
FPS = P.get("render", {}).get("fps", 30)
FADE = P.get("render", {}).get("fade", 0.35)
ZOOM = P.get("render", {}).get("zoom", 0.05)
FADE_COLOR = P.get("palette", {}).get("fade_color", "0x141010")
os.makedirs(OUTDIR, exist_ok=True)


def load(video):
    return json.load(open(os.path.join(BASE, "scenes", f"{video}.json")))["scenes"]


def run(cmd):
    r = subprocess.run(cmd + " > " + f"{WORK}/last-ffmpeg.log 2>&1", shell=True)
    if r.returncode != 0:
        tail = open(f"{WORK}/last-ffmpeg.log").read()[-800:]
        raise RuntimeError(f"FALHA ({r.returncode}): {cmd}\n{tail}")


def tconv(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def plain(s):
    for a, b in (("<br>", " "), ("<em>", ""), ("</em>", ""), ("&amp;", "&")):
        s = s.replace(a, b)
    return s


def render(video, i0, i1):
    scenes = load(video)
    for i, sc in enumerate(scenes):
        if not (i0 <= i < i1):
            continue
        still = f"{STILLS}/{video}-{sc['id']}.png"
        if not os.path.exists(still):
            raise SystemExit(f"SEM STILL: {still} — rode render_stills.sh antes.")
        D = round(sc["dur"] * FPS)
        out = f"{WORK}/{video}-{sc['id']}.mp4"
        if i % 2 == 0:
            z = f"min(1+{ZOOM}*on/{D-1},1+{ZOOM}+0.005)"
        else:
            z = f"max(1+{ZOOM}+0.005-{ZOOM}*on/{D-1},1.0)"
        fade_out_st = sc["dur"] - FADE
        vf = (f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
              f":d={D}:s=1920x1080:fps={FPS},"
              f"fade=t=in:st=0:d={FADE}:color={FADE_COLOR},"
              f"fade=t=out:st={fade_out_st:.3f}:d={FADE}:color={FADE_COLOR},"
              f"format=yuv420p")
        print(f"render {video}-{sc['id']} ({sc['dur']}s)...", flush=True)
        run(f'ffmpeg -nostdin -y -loglevel error -i "{still}" -filter_complex "{vf}" '
            f'-c:v libx264 -preset veryfast -crf 18 -r {FPS} "{out}"')
        print(f"  ok {out}", flush=True)


def concat(video):
    scenes = load(video)
    meta = json.load(open(os.path.join(BASE, "scenes", f"{video}.json"))).get("_meta", {})
    lst = f"{WORK}/{video}-list.txt"
    with open(lst, "w") as f:
        for sc in scenes:
            f.write(f"file '{WORK}/{video}-{sc['id']}.mp4'\n")
    final = f"{OUTDIR}/{PREFIX}-{video}-16x9.mp4"
    run(f'ffmpeg -y -loglevel error -f concat -safe 0 -i "{lst}" '
        f'-c copy -movflags +faststart "{final}"')
    total = sum(sc["dur"] for sc in scenes)
    print(f"FINAL: {final} (~{total:.1f}s)", flush=True)

    # SRT: uma legenda por cena (os fades cobrem as emendas)
    lines = []
    t0 = 0.0
    for i, sc in enumerate(scenes):
        start = t0 + (FADE if i > 0 else 0.0)
        end = t0 + sc["dur"] - (FADE if i < len(scenes) - 1 else 0.0)
        kick = sc.get("kicker", "")
        title = plain(sc.get("title", ""))
        desc = plain(sc.get("desc", ""))
        if sc["kind"] in ("intro",):
            txt = f"{kick} — {title}. {desc}"
        elif sc["kind"] == "outro":
            txt = f"{title} {sc.get('note', '')}".strip()
        else:
            txt = f"{kick}: {title}. {desc}"
        lines.append(f"{i + 1}\n{tconv(start)} --> {tconv(end)}\n{txt}\n")
        t0 += sc["dur"]
    with open(f"{OUTDIR}/legendas-{video}.srt", "w") as f:
        f.write("\n".join(lines))

    with open(f"{OUTDIR}/roteiro-{video}.txt", "w") as f:
        f.write(f"ROTEIRO · {meta.get('label', video.upper())} (16:9 · 1920x1080 · {FPS}fps)\n")
        f.write(f"Duração total: {total:.1f}s · {len(scenes)} cenas · fade {FADE}s nas emendas\n\n")
        t0 = 0.0
        for sc in scenes:
            f.write(f"[{t0:5.1f}s] {sc['id'].upper():14s} · {sc['dur']}s · {plain(sc.get('kicker', '')).upper()}\n")
            if sc.get("title"):
                f.write(f"        TÍTULO: {plain(sc.get('title', ''))}\n")
            if sc.get("desc"):
                f.write(f"        DESC:   {plain(sc.get('desc', ''))}\n")
            if sc.get("chips"):
                f.write(f"        CHIPS:  {' · '.join(sc['chips'])}\n")
            f.write("\n")
            t0 += sc["dur"]
    print(f"SRT + roteiro escritos em {OUTDIR}", flush=True)


def audit(video):
    scenes = load(video)
    for sc in scenes:
        f = f"{WORK}/{video}-{sc['id']}.mp4"
        if not os.path.exists(f):
            print(f"FALTANDO {f}", flush=True)
            continue
        r = subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"',
                           shell=True, capture_output=True, text=True)
        d = float(r.stdout.strip() or 0)
        ok = "OK " if abs(d - sc["dur"]) < 0.4 else "CURTO/TRUNCADO"
        print(f"{ok} {os.path.basename(f)} {d:.2f}s (esperado {sc['dur']}s)", flush=True)
    final = f"{OUTDIR}/{PREFIX}-{video}-16x9.mp4"
    if os.path.exists(final):
        r = subprocess.run(f'ffprobe -v error -show_entries format=duration,size -of csv=p=0 "{final}"',
                           shell=True, capture_output=True, text=True)
        print(f"FINAL {final} -> {r.stdout.strip()}", flush=True)
    else:
        print(f"FINAL AUSENTE: {final}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "concat":
        concat(sys.argv[2])
    elif cmd == "audit":
        audit(sys.argv[2])
    else:
        raise SystemExit(__doc__)
    print("OK", flush=True)
