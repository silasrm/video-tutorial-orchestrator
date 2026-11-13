# Video Orchestrator

**Skill portátil que transforma agentes de IA em produtores de vídeo** — showcase de produto e tutoriais por módulo — para apps e painéis web. O agente escreve o plano, captura as telas reais da aplicação, monta as cenas com legendas e renderiza os MP4s finais com ffmpeg. Sem editor de vídeo, sem intervenção humana em cada etapa.

```
App/Painel web ──► ROADMAP ──► Roteiros ──► Capturas (browser headless)
                                                        │
MP4 + SRT + Roteiro ◄── concat ffmpeg ◄── zoompan ◄── Cenas HTML com legenda
```

## O que este repositório produz

| Tipo de vídeo | Granularidade | Tom | Estrutura |
|---|---|---|---|
| **Showcase** | 1 vídeo por superfície (app, painel) | Marketing, benefícios | intro + funcionalidades + CTA |
| **Tutorial** | 1 vídeo por item de menu/módulo | Ensino, passo a passo | abertura + passos numerados + encerramento |

Formato fixo: **16:9 · 1920×1080 · 30fps**, legenda embutida na cena + arquivo `.srt` + roteiro `.txt`.

Cada vídeo entregue vem com 3 arquivos:

```
download/<conjunto>/
├── <prefix>-<video>-16x9.mp4    # vídeo final
├── legendas-<video>.srt         # legendas (1 bloco por cena)
└── roteiro-<video>.txt          # roteiro com timestamps
```

## Estrutura do repositório

```
video-orchestrator/
├── README.md                   # este arquivo
├── SKILL.md                    # o orquestrador: 9 fases, gates de qualidade, armadilhas
├── INSTRUCOES-DE-USO.md        # guia de instalação e invocação
├── install.py                  # instalador (detecta pastas de skills dos harnesss)
├── templates/
│   ├── gen_scenes.py           # roteiro JSON -> cenas HTML (legenda embutida)
│   ├── compose.py              # stills -> MP4 (zoompan+fade) -> concat + SRT + roteiro
│   ├── render_stills.sh        # cenas HTML -> PNG 2560×1440
│   ├── capture_screen.sh       # captura de tela do app com polling anti-animação
│   ├── project.example.json    # config do projeto (marca, paleta, saídas, capturas)
│   ├── scenes.example.json     # schema de roteiro JSON (tutorial de exemplo)
│   ├── ROADMAP.template.md     # plano-mestre da série
│   └── ROTEIRO.template.md     # roteiro individual por vídeo
└── fonts/
    ├── Anton.ttf               # títulos
    ├── ArchivoBlack.ttf        # kickers e selos
    └── Inter.ttf               # corpo e descrições
```

## Instalação

**Opção 1 — instalador interativo** (recomendado):

```bash
python3 install.py                 # detecta pastas de skills e instala pelo menu
python3 install.py --all --yes     # instala em todas as detectadas
python3 install.py --dest ~/.claude/skills --yes
python3 install.py --list          # só lista os destinos detectados
python3 install.py --uninstall     # remove a skill
```

**Opção 2 — instalador tudo-em-um** (um único `.py` com todos os arquivos embutidos; ideal quando não há como baixar pastas/zip):

```bash
python3 video-orchestrator-instalador.py                # extrai + menu de instalação
python3 video-orchestrator-instalador.py --extract-only # só extrai ./video-orchestrator/
```

**Opção 3 — manual:** copie a pasta para o diretório de skills do seu harness:

| Harness | Caminho |
|---|---|
| Claude Code (projeto) | `.claude/skills/video-orchestrator/` |
| Claude Code (global) | `~/.claude/skills/video-orchestrator/` |
| Z.ai | `skills/video-orchestrator/` (na raiz do projeto) |
| Cursor / Aider / outros | qualquer pasta do repo, referenciada no `AGENTS.md`/`.cursorrules` |

Requisitos do ambiente onde os vídeos serão produzidos: **ffmpeg ≥ 6.0**, **Python ≥ 3.8** e automação de browser (agent-browser ou Playwright). O instalador é 100% stdlib — funciona em Linux, macOS e Windows.

## Como usar

Com a skill instalada, peça ao agente do seu harness:

> Use a skill video-orchestrator (SKILL.md) para produzir os vídeos do meu produto.
> App: http://localhost:3000 (app de pedidos) e http://localhost:3000/painel (painel admin).
> Quero: 1 tutorial por item do menu do painel, com legenda.
> Siga todas as fases (0–8) com os gates. Entregue em download/ os MP4 16:9 + SRT + roteiro,
> e mantenha o ROADMAP atualizado vídeo a vídeo. Produza UM vídeo completo por vez,
> só parta para o próximo depois do QA visual aprovado.

O agente conduz sozinho as 9 fases: **bootstrap → mapeamento → ROADMAP → roteiros → captura (com interação real: cliques, cadastros, edições) → cenas JSON → cenas HTML → render em lotes → QA visual e entrega**. Cada fase tem um gate de qualidade antes da seguinte.

## Garantias de qualidade embutidas

- **Captura com polling**: screenshots só depois do conteúdo realmente carregar (evita telas esmaecidas por animações de entrada);
- **Legendas no HTML da cena**: nunca overlay sobre PNG (screenshots são opacos);
- **Lado da legenda automático**: sempre oposto ao dispositivo da cena;
- **Render em lotes de 2–4 cenas** com auditoria `ffprobe` antes de concatenar (tolera CPU instável);
- **Concat com stream-copy** (`-c copy` + fades por cena) em vez de `xfade` (que trava em máquinas lentas);
- **Zoompan alternado** (aproxima/afasta) para dar ritmo;
- **QA visual por frames extraídos** antes de qualquer vídeo ser marcado como entregue.

A tabela completa de sintomas → causas → correções está no `SKILL.md` (seção "Armadilhas conhecidas").

## Fontes e licença

Fontes Anton, Archivo Black e Inter — SIL Open Font License, uso livre em projetos comerciais. Os demais arquivos: use, modifique e redistribua livremente nos seus projetos.

## Solução de problemas rápidos

| Problema | Solução |
|---|---|
| Vídeo final não abre / tem 1 cena | rode `python3 compose.py audit <video>` e re-renderize as cenas marcadas antes do `concat` |
| Comando ffmpeg "falha" mas o arquivo existe | verifique com `audit`/`ls`; em CPU limitada o exit code mente |
| Screenshot saiu lavado/esmaecido | use `capture_screen.sh` (polling) em vez de screenshot direto |
| Legenda pisca fundo branco | a legenda deve estar no HTML da cena, nunca como imagem transparente sobreposta |
| Fonte não aplica nas cenas | confira que os `.ttf` estão em `scripts/video/assets/` (o CSS resolve `../assets/`) |
