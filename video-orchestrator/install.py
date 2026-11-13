#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALL.PY · Instalador da skill video-orchestrator
====================================================
Detecta as pastas de skills dos principais harnesss (Claude Code, Z.ai, Cursor,
Windsurf, Codex CLI, agentes genéricos), mostra um menu e copia a skill para lá.

Uso:
  python3 install.py                 # modo interativo (menu)
  python3 install.py --list          # só lista as pastas detectadas
  python3 install.py --all           # instala em TODAS as pastas detectadas
  python3 install.py --dest CAMINHO  # instala num caminho específico
  python3 install.py --all --yes     # sem confirmações (overwrite silencioso)
  python3 install.py --uninstall     # remove a skill (com --dest ou --all)
  python3 install.py --name outro    # instala com outro nome de pasta

Sem dependências externas (apenas stdlib). Funciona em Linux, macOS e Windows.
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SKILL_NAME = "video-orchestrator"
HERE = Path(__file__).resolve().parent

# Padrões de pastas de skills por harness (nome amigável, padrão relativo, global?)
CANDIDATES = [
    ("Claude Code (projeto atual)", ".claude/skills", False),
    ("Claude Code (global)", "~/.claude/skills", True),
    ("Z.ai (projeto atual)", "skills", False),
    ("Windsurf", "~/.windsurf/skills", True),
    ("Cursor", "~/.cursor/skills", True),
    ("Codex CLI", "~/.codex/skills", True),
    ("Agentes genéricos (projeto)", ".agents/skills", False),
]

# Arquivos que NÃO vão junto na instalação
IGNORE = shutil.ignore_patterns("install.py", "__pycache__", "*.zip", "*.pyc")


def detect():
    """Retorna lista (rótulo, caminho-resolvido) de pastas de skills existentes."""
    found, seen = [], set()
    # 1) sobe da pasta atual até a raiz procurando padrões de projeto
    for base in [Path.cwd(), *Path.cwd().parents]:
        for label, pat, _ in CANDIDATES:
            if pat.startswith("~"):
                continue
            p = base / pat
            key = str(p.resolve())
            if key not in seen and p.is_dir():
                seen.add(key)
                found.append((f"{label}  [projeto: {base.name}]", p.resolve()))
        # não precisa subir mais que 5 níveis
        if len(list(base.parents)) > 8:
            break
    # 2) globais no HOME (existentes ou criáveis)
    for label, pat, is_global in CANDIDATES:
        if not is_global:
            continue
        p = Path(os.path.expanduser(pat))
        key = str(p.resolve())
        if key not in seen and p.is_dir():
            seen.add(key)
            found.append((label, p.resolve()))
    return found


def check_source():
    """Confere que este install.py está junto da skill completa."""
    need = ["SKILL.md", "templates", "fonts"]
    missing = [n for n in need if not (HERE / n).exists()]
    if missing:
        sys.exit(f"[X] Arquivos faltando ao lado de install.py: {', '.join(missing)}\n"
                 f"    Extraia o ZIP inteiro antes de rodar o instalador.")
    return True


def install_into(dest_root: Path, skill_name: str, assume_yes: bool):
    target = dest_root / skill_name
    if target.exists():
        if not assume_yes:
            try:
                a = input(f"    '{target}' já existe. Sobrescrever? [s/N] ").strip().lower()
            except EOFError:
                a = ""
            if a not in ("s", "si", "sim", "y", "yes"):
                print("    -> pulado.")
                return False
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for item in HERE.iterdir():
        if item.name == "install.py" or item.name.startswith("__"):
            continue
        if item.is_dir():
            shutil.copytree(item, target / item.name, ignore=IGNORE, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target / item.name)
    print(f"    [OK] instalado em: {target}")
    return True


def show_menu(found):
    print("\nPastas de skills detectadas:")
    for i, (label, path) in enumerate(found, 1):
        print(f"  {i}) {label}\n     {path}")
    print("\n  a) instalar em TODAS as acima")
    print("  c) informar outro caminho")
    print("  q) sair sem instalar")
    try:
        return input("\nEscolha (número, a, c ou q): ").strip().lower()
    except EOFError:
        return "q"


def main():
    ap = argparse.ArgumentParser(description="Instalador da skill video-orchestrator")
    ap.add_argument("--list", action="store_true", help="lista pastas detectadas e sai")
    ap.add_argument("--all", action="store_true", help="instala em todas as pastas detectadas")
    ap.add_argument("--dest", metavar="CAMINHO", help="instala num caminho específico")
    ap.add_argument("--uninstall", action="store_true", help="remove a skill instalada")
    ap.add_argument("--yes", "-y", action="store_true", help="não pede confirmação")
    ap.add_argument("--name", default=SKILL_NAME, help=f"nome da pasta (padrão: {SKILL_NAME})")
    args = ap.parse_args()

    check_source()
    found = detect()

    print("=" * 58)
    print(f" INSTALADOR DA SKILL · {args.name}")
    print("=" * 58)

    # ---- modo lista ----
    if args.list:
        if not found:
            print("Nenhuma pasta de skills detectada. Use --dest CAMINHO.")
        for label, path in found:
            print(f"  {label}: {path}")
        return

    # ---- uninstall ----
    if args.uninstall:
        targets = []
        if args.dest:
            targets = [Path(args.dest).expanduser().resolve() / args.name]
        else:
            targets = [p / args.name for _, p in found]
        if not targets:
            sys.exit("Nada para remover: nenhuma pasta detectada e sem --dest.")
        for t in targets:
            if t.exists():
                shutil.rmtree(t)
                print(f"[OK] removido: {t}")
            else:
                print(f"[--] não encontrado: {t}")
        return

    # ---- escolha dos destinos ----
    chosen = []
    if args.dest:
        d = Path(args.dest).expanduser().resolve()
        chosen = [("informado via --dest", d)]
    elif args.all:
        chosen = found
        if not chosen:
            sys.exit("Nenhuma pasta detectada. Use --dest CAMINHO ou rode interativamente.")
    else:
        if not found:
            d = input("Nenhuma pasta detectada. Caminho onde instalar (vazio=pasta atual/skills): ").strip()
            d = Path(d).expanduser().resolve() if d else (Path.cwd() / "skills").resolve()
            chosen = [("informado manualmente", d)]
        else:
            pick = show_menu(found)
            if pick == "q":
                print("Instalação cancelada.")
                return
            if pick == "c":
                d = input("Caminho completo: ").strip()
                chosen = [("informado manualmente", Path(d).expanduser().resolve())]
            elif pick == "a":
                chosen = found
            else:
                try:
                    chosen = [found[int(pick) - 1]]
                except (ValueError, IndexError):
                    sys.exit("Opção inválida.")

    # ---- instala ----
    print()
    ok = 0
    for label, path in chosen:
        print(f"-> Instalando em {path}  ({label})")
        path.mkdir(parents=True, exist_ok=True)
        if install_into(path, args.name, args.yes):
            ok += 1

    # ---- resumo ----
    print("\n" + "=" * 58)
    print(f" CONCLUÍDO · {ok} instalação(ões).")
    print("=" * 58)
    print("""
Próximos passos:
  1. Abra o harness no projeto desejado.
  2. Peça: "Use a skill video-orchestrator (SKILL.md) para produzir os
     vídeos do meu produto" — o agente segue as 9 fases sozinho.
  3. Se o harness não ler a pasta automaticamente, aponte o caminho do
     SKILL.md no seu arquivo de regras (CLAUDE.md, AGENTS.md, .cursorrules).
""")


if __name__ == "__main__":
    main()
