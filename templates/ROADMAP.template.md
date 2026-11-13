# ROADMAP — Vídeos [SHOWCASE / TUTORIAIS] · <Nome do Produto>

> Preencha todos os campos `<...>`. Este arquivo é o plano-mestre: um vídeo por linha.
> Regra de ouro: 1 vídeo = 1 superfície (showcase) OU 1 item de menu/módulo (tutorial).
> Produza e valide UM vídeo completo antes de partir para o próximo (não deixe lotes pela metade).

## Contexto
- **Produto**: <nome> — <1 linha do que é>
- **Superfícies**: <app mobile (URL base) / painel web (URL base)>
- **Objetivo da série**: <ex.: ensinar a operação do dia a dia / vender o produto>
- **Público**: <ex.: dono de restaurante sem experiência com sistemas>
- **Formato fixo**: 16:9 · 1920×1080 · 30fps · zoompan 1.05 alternado · fade 0,35s
- **Diretório de saída**: <caminho absoluto download/...>

## Série SHOWCASE (opcional — 1 vídeo por superfície)
| # | id do vídeo | Superfície | Duração alvo | Cenas | Status |
|---|---|---|---|---|---|
| S1 | `app` | App de pedidos | 40–50s | intro + 7 features + outro | ☐ planejado ☐ roteirizado ☐ capturado ☐ renderizado ☐ entregue |
| S2 | `painel` | Painel administrativo | 55–65s | intro + 10 features + outro | ☐ planejado ☐ roteirizado ☐ capturado ☐ renderizado ☐ entregue |

## Série TUTORIAIS (1 vídeo por item do menu / módulo)
| # | id do vídeo | Módulo do menu | O que o usuário aprende | Passos (cenas) | Duração alvo | Status |
|---|---|---|---|---|---|---|
| T1 | `tut-<modulo1>` | <ex.: Pedidos> | <ex.: aceitar, detalhar e cancelar um pedido> | <6–8> | 35–55s | ☐ planejado ☐ roteirizado ☐ capturado ☐ renderizado ☐ entregue |
| T2 | `tut-<modulo2>` | <ex.: Cozinha (KDS)> | <ex.: mover pedido pelas colunas até pronto> | <5–7> | 30–45s | ☐ ... |
| T3 | `tut-<modulo3>` | <...> | <...> | <...> | ... | ☐ ... |

> Ordem sugerida dos tutoriais: siga a ordem do menu lateral (o que o usuário vê primeiro primeiro).
> Cada vídeo termina apontando o próximo módulo da série (engancha a playlist).

## Convenções de nome de arquivo
- Capturas do produto: `assets/<video>-<passo>.png` (ex.: `tut-pedidos-p03.png`)
- Cenas HTML / stills / work: gerados automaticamente com o `id` da cena
- Entrega: `<outdir>/<prefix>-<video>-16x9.mp4` + `legendas-<video>.srt` + `roteiro-<video>.txt`

## Checklist de conclusão de CADA vídeo (só marque "entregue" se todos passarem)
- [ ] Roteiro individual escrito e revisado (tempos somam a duração alvo)
- [ ] Todas as capturas nítidas (sem fade de animação, dados visíveis, sem poluição visual)
- [ ] `compose.py audit <video>`: todas as cenas OK e final existente
- [ ] SRT confere com as cenas (abrir e ler)
- [ ] Frames extraídos do MP4 final inspecionados visualmente (sem texto cortado/colidindo)
