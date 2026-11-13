# Como usar este orquestrador

Esta pasta é uma **skill portátil**: um agente de IA (Claude Code, Z.ai, Cursor, windsurf, etc.)
segue o `SKILL.md` e produz sozinho os vídeos de showcase e tutoriais do seu produto.

## O que há aqui

| Arquivo | Papel |
|---|---|
| `SKILL.md` | O orquestrador: 9 fases, gates de qualidade, armadilhas e comandos exatos |
| `templates/gen_scenes.py` | Gera as cenas HTML (legenda embutida) a partir de `scenes/<video>.json` |
| `templates/compose.py` | Renderiza MP4 por cena (zoompan+fade) e concatena + SRT + roteiro |
| `templates/render_stills.sh` | Transforma cada cena HTML em PNG 2560×1440 |
| `templates/capture_screen.sh` | Captura telas do app/painel com polling anti-animação |
| `templates/project.example.json` | Config do projeto (marca, paleta, saída, capturas) |
| `templates/scenes.example.json` | Schema de roteiro em JSON (tutorial de exemplo) |
| `templates/ROADMAP.template.md` | Plano-mestre da série de vídeos |
| `templates/ROTEIRO.template.md` | Roteiro individual por vídeo |
| `fonts/*.ttf` | Anton, Archivo Black, Inter (SIL OFL — uso livre) |

## Instalação em cada harness

### Jeito fácil: o instalador (recomendado)

Extraia o ZIP inteiro e rode na pasta extraída:

```bash
python3 install.py                 # menu interativo (detecta e lista os destinos)
python3 install.py --list          # só mostra as pastas detectadas
python3 install.py --all --yes     # instala em todas as detectadas, sem perguntar
python3 install.py --dest ~/.claude/skills --yes   # destino específico
python3 install.py --uninstall     # remove a skill dos destinos detectados
```

O instalador procura pastas de skills do Claude Code (projeto e global), Z.ai, Windsurf,
Cursor, Codex CLI e agentes genéricos (`.agents/skills`). Se nenhuma for detectada,
ele pede um caminho — e `--dest` sempre funciona. Sem dependências externas.

### Manual (alternativa)

- **Claude Code / Claude Skills**: copie a pasta para `.claude/skills/video-orchestrator/`
  (ou `~/.claude/skills/video-orchestrator/` para valer em todo projeto).
- **Z.ai (este ambiente)**: copie para `/home/z/my-project/skills/video-orchestrator/`.
- **Outros agentes (Cursor, Aider, etc.)**: deixe a pasta no repositório e referencie o
  caminho do `SKILL.md` no seu prompt/arquivo de regras (ex.: `AGENTS.md`, `.cursorrules`).

## Prompt pronto para colar no harness

> Use a skill em <caminho>/video-orchestrator/SKILL.md para produzir os vídeos do meu produto.
> App: <URL local> (app de pedidos) e <URL local>/painel (painel admin).
> Quero: [ ] 1 showcase por superfície [ ] 1 tutorial por item do menu do painel.
> Siga todas as fases (0–8) com os gates. Entregue em download/ os MP4 16:9 + SRT + roteiro,
> e mantenha o ROADMAP atualizado vídeo a vídeo. Produza UM vídeo completo por vez,
> só parta para o próximo depois do QA visual aprovado.

## Regras que o agente não pode pular (resumo)

1. Captura com polling do seletor (fades de animação estragam screenshot);
2. Legendas embutidas no HTML da cena — nunca overlay sobre o PNG;
3. Render em lotes de 2–4 cenas e conferir com `compose.py audit` antes de concatenar;
4. `concat` sempre com `-c copy` (xfade trava em máquina lenta);
5. QA visual por frames extraídos antes de marcar "entregue" no ROADMAP.
