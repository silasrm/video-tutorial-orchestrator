# ROTEIRO · <SHOWCASE/TUTORIAL> · <módulo ou superfície> · <id-do-video>

> Preencha todos os campos `<...>`. Uma cena = um movimento do zoompan = uma legenda.
> Para TUTORIAIS: cada cena é UM PASSO de uso real (a captura mostra o estado DEPOIS da ação).
> Título: máx. 2 linhas (use `<br>`); destaque a palavra-chave com `<em>palavra</em>`.
> Dur: intro 3.5–4.5s · passo 4.0–5.0s · outro 4.5–5.5s. A soma deve bater com o ROADMAP.

## Ficha
- **Vídeo**: `<id>` · **Série**: <showcase/tutorial N/total> · **Duração alvo**: <XXs>
- **Objetivo**: <o que o espectador consegue fazer ao final>
- **Dispositivo da cena**: <browser 1084px / phone 450px> · **Capturas necessárias**: <N>

## Cenas

### 1. `abertura` — kind: intro — 4.0s
- **Ação na UI (para captura)**: <ex.: abrir /painel/pedidos e aguardar a fila carregar>
- **Captura**: `assets/tut-pedidos-capa.png`
- **Kicker**: `TUTORIAL · PAINEL — PEDIDOS`
- **Título**: `Aceite pedidos<br>sem <em>atraso</em>`
- **Desc**: <1 frase prometendo o que o vídeo ensina>
- **Chips**: `Módulo 2 de 9` · `Duração: 40s`

### 2. `p01` — kind: feature — 4.5s
- **Ação na UI**: <ex.: clicar no item "Pedidos" do menu lateral>
- **Captura**: `assets/tut-pedidos-p01.png` (estado DEPOIS da ação)
- **Side do dispositivo**: <left/right — ALTERNAR entre cenas>
- **Counter**: `01/08` · **URL na barra**: `pedidos` · **Bignum**: `P01`
- **Kicker**: `PASSO 1 · ABRIR O MÓDULO`
- **Título**: `Abra <em>Pedidos</em> no menu lateral`
- **Desc**: <o que a tela mostra e por que importa — 1–2 frases curtas>
- **Chips**: `<benefício 1>` · `<benefício 2>`

### 3. `p02` — kind: feature — 4.5s
- (mesma estrutura; side alternado em relação à cena anterior)

<!-- ...repita para cada passo... -->

### N. `encerramento` — kind: outro — 5.0s
- **Kicker**: `AGORA É COM VOCÊ`
- **Título**: `Pronto!<br>Você domina <em><módulo></em>`
- **Chips**: `Próximo: <módulo seguinte>`
- **CTA**: `<ação desejada>` · **Nota**: `<dica final ou gancho da série>`

## Legendas SRT (texto final por cena — o compose.py gera a partir do scenes/<video>.json)
1. [0.0–4.0] `<intro: kicker — título. desc>`
2. [4.0–8.5] `PASSO 1 · ...: <título>. <desc>`
<!-- ... -->

## Checklist antes de renderizar
- [ ] Soma das durações = duração alvo do ROADMAP
- [ ] Sides alternados (dispositivo esquerda/direita) para dar ritmo
- [ ] Todo `img` listado existe em `assets/`
- [ ] Kicker nunca passa de ~38 caracteres (estoura o pílula)
- [ ] Título com no máximo 2 linhas
