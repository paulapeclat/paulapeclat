#!/usr/bin/env python3
"""
Expedição Estelar — jogo interativo do perfil.

Visitantes movem a exploradora abrindo issues com título
`expedicao|mover|<direcao>`; o workflow expedicao.yml chama este script,
que atualiza data/expedicao.json, regenera assets/expedicao.svg e imprime
a mensagem de resposta (usada como comentário na issue).

Uso:
  python scripts/expedicao.py render                  # só redesenha o SVG
  python scripts/expedicao.py move <direcao> <user>   # aplica movimento
Direções: norte, sul, leste, oeste
"""
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "data" / "expedicao.json"
OUT_FILE = ROOT / "assets" / "expedicao.svg"

COLS, ROWS = 13, 5
CELL = 60
BOARD_X, BOARD_Y = 110, 130

CYAN = "#22C3D9"
PINK = "#F23D91"
PINK_LIGHT = "#F2A2C0"
YELLOW = "#ECBE40"

DIRECOES = {
    "norte": (0, -1),
    "sul": (0, 1),
    "leste": (1, 0),
    "oeste": (-1, 0),
}

DEFAULT_STATE = {
    "pos": [6, 2],
    "estrela_pos": [10, 1],
    "estrelas": 0,
    "movimentos": 0,
    "ultimos": [],
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def cell_center(col: int, row: int):
    return BOARD_X + col * CELL + CELL // 2, BOARD_Y + row * CELL + CELL // 2


def star_path(cx: float, cy: float, r_out: float, r_in: float) -> str:
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        ang = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + r * math.cos(ang):.1f} {cy + r * math.sin(ang):.1f}")
    return "M " + " L ".join(pts) + " Z"


def load_state() -> dict:
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {**DEFAULT_STATE, **state}
    return dict(DEFAULT_STATE)


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def respawn_star(state: dict) -> None:
    livres = [
        [c, r]
        for c in range(COLS)
        for r in range(ROWS)
        if [c, r] != state["pos"] and [c, r] != state["estrela_pos"]
    ]
    state["estrela_pos"] = random.choice(livres)


def render(state: dict) -> None:
    px, py = cell_center(*state["pos"])
    sx, sy = cell_center(*state["estrela_pos"])

    dots = []
    for c in range(COLS):
        for r in range(ROWS):
            x, y = cell_center(c, r)
            dots.append(f'<circle cx="{x}" cy="{y}" r="1.5" fill="rgba(255,255,255,0.13)"/>')
    grid = "\n    ".join(dots)

    if state["ultimos"]:
        ultimos = "últimos exploradores: " + ", ".join("@" + esc(u) for u in state["ultimos"])
    else:
        ultimos = "seja a primeira pessoa a explorar este mapa!"

    chip_text = f"★ estrelas coletadas: {state['estrelas']}"
    chip_w = round(len(chip_text) * 6.5) + 34
    chip_x = 960 - chip_w

    svg = f'''<svg viewBox="0 0 1000 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Expedição Estelar — jogo interativo: exploradora na posição {state['pos'][0]},{state['pos'][1]}, {state['estrelas']} estrelas coletadas">
  <defs>
    <radialGradient id="eGlowCyan" cx="10%" cy="10%" r="60%">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="eGlowPink" cx="90%" cy="90%" r="60%">
      <stop offset="0%" stop-color="{PINK}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="eHeroGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#8CD9E6"/>
      <stop offset="100%" stop-color="{CYAN}"/>
    </linearGradient>
    <filter id="eGrain">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" result="noise"/>
      <feColorMatrix in="noise" type="matrix"
        values="0 0 0 0 1
                0 0 0 0 1
                0 0 0 0 1
                0 0 0 0.03 0"/>
    </filter>
    <style>
      text {{ font-family: 'Segoe UI', 'Arial', sans-serif; }}
    </style>
  </defs>

  <rect width="1000" height="560" fill="#000000"/>
  <rect width="1000" height="560" fill="url(#eGlowCyan)"/>
  <rect width="1000" height="560" fill="url(#eGlowPink)"/>
  <rect width="1000" height="560" filter="url(#eGrain)" opacity="0.5"/>

  <!-- estrelas do céu -->
  <circle cx="70" cy="90" r="2" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.4s" repeatCount="indefinite"/></circle>
  <circle cx="300" cy="60" r="1.7" fill="{CYAN}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.8s" begin="0.9s" repeatCount="indefinite"/></circle>
  <circle cx="560" cy="80" r="2.1" fill="{PINK_LIGHT}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.9s" begin="1.5s" repeatCount="indefinite"/></circle>
  <circle cx="880" cy="100" r="1.6" fill="{YELLOW}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.1s" begin="0.3s" repeatCount="indefinite"/></circle>
  <circle cx="950" cy="500" r="1.9" fill="{CYAN}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.6s" begin="2s" repeatCount="indefinite"/></circle>
  <circle cx="50" cy="510" r="1.6" fill="{PINK}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="5.2s" begin="1.1s" repeatCount="indefinite"/></circle>

  <text x="40" y="56" font-size="24" font-weight="800" fill="#FFFFFF" letter-spacing="1">EXPEDIÇÃO ESTELAR</text>
  <text x="40" y="80" font-size="13" fill="rgba(255,255,255,0.6)">um jogo coletivo — qualquer visitante move a exploradora abrindo uma issue</text>

  <rect x="{chip_x}" y="34" width="{chip_w}" height="30" rx="15" fill="rgba(236,190,64,0.12)" stroke="rgba(236,190,64,0.45)"/>
  <text x="{chip_x + chip_w / 2:g}" y="53" font-size="12.5" font-weight="700" fill="{YELLOW}" text-anchor="middle">{chip_text}</text>

  <!-- tabuleiro -->
  <rect x="{BOARD_X - 20}" y="{BOARD_Y - 20}" width="{COLS * CELL + 40}" height="{ROWS * CELL + 40}" rx="18" fill="rgba(255,255,255,0.025)" stroke="rgba(255,255,255,0.09)"/>
  <g>
    {grid}
  </g>

  <!-- estrela a coletar -->
  <g>
    <circle cx="{sx}" cy="{sy}" r="16" fill="{YELLOW}" opacity="0.14">
      <animate attributeName="r" values="14;20;14" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <path d="{star_path(sx, sy, 11, 4.6)}" fill="{YELLOW}" stroke="#FFF3CC" stroke-width="1" stroke-linejoin="round">
      <animate attributeName="opacity" values="1;0.55;1" dur="2.4s" repeatCount="indefinite"/>
    </path>
  </g>

  <!-- a exploradora -->
  <g transform="translate({px},{py + 14})">
    <ellipse cx="0" cy="1" rx="9" ry="2.6" fill="#000000" opacity="0.55"/>
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 -2;0 -6;0 -2" dur="1.4s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="-3" rx="6.5" ry="3" fill="{CYAN}" opacity="0.45">
        <animate attributeName="opacity" values="0.45;0.12;0.45" dur="0.7s" repeatCount="indefinite"/>
      </ellipse>
      <rect x="-10" y="-32" width="20" height="23" rx="8" fill="url(#eHeroGrad)" stroke="rgba(255,255,255,0.55)" stroke-width="1"/>
      <rect x="-13.5" y="-21" width="4" height="8" rx="2" fill="#1795A8"/>
      <rect x="9.5" y="-21" width="4" height="8" rx="2" fill="#1795A8"/>
      <rect x="-7" y="-28" width="14" height="9.5" rx="4.75" fill="#06090C"/>
      <g>
        <animate attributeName="opacity" values="1;1;0.1;1" keyTimes="0;0.9;0.94;1" dur="3.6s" repeatCount="indefinite"/>
        <circle cx="-3" cy="-23.2" r="1.7" fill="#7FF3FF"/>
        <circle cx="3" cy="-23.2" r="1.7" fill="#7FF3FF"/>
      </g>
      <line x1="0" y1="-32" x2="0" y2="-38" stroke="rgba(255,255,255,0.6)" stroke-width="1.4"/>
      <circle cx="0" cy="-40" r="2.6" fill="{PINK}">
        <animate attributeName="opacity" values="1;0.35;1" dur="1.2s" repeatCount="indefinite"/>
      </circle>
    </g>
  </g>

  <!-- rodapé -->
  <text x="40" y="496" font-size="12.5" fill="rgba(255,255,255,0.6)">{ultimos}</text>
  <text x="960" y="496" font-size="12.5" fill="rgba(255,255,255,0.4)" text-anchor="end">movimentos: {state['movimentos']}</text>
  <text x="40" y="522" font-size="11.5" fill="rgba(255,255,255,0.35)">colete a ★ — use as setas abaixo do mapa; o robô processa sua jogada em ~30s</text>
</svg>
'''
    OUT_FILE.write_text(svg, encoding="utf-8")


def move(direcao: str, user: str) -> str:
    state = load_state()
    direcao = direcao.strip().lower()
    user = user.strip().lstrip("@")[:39]  # limite de username do GitHub

    if direcao not in DIRECOES:
        render(state)
        return (
            f"❓ Direção `{direcao}` inválida — use **norte**, **sul**, **leste** ou **oeste**. "
            "Volte ao perfil e clique numa das setas!"
        )

    dx, dy = DIRECOES[direcao]
    nx, ny = state["pos"][0] + dx, state["pos"][1] + dy

    if not (0 <= nx < COLS and 0 <= ny < ROWS):
        render(state)
        return (
            f"🧱 Opa, @{user} — a exploradora bateu na borda do mapa! "
            "O movimento não foi aplicado. Tente outra direção."
        )

    state["pos"] = [nx, ny]
    state["movimentos"] += 1
    state["ultimos"] = ([user] + [u for u in state["ultimos"] if u != user])[:5]

    if state["pos"] == state["estrela_pos"]:
        state["estrelas"] += 1
        respawn_star(state)
        msg = (
            f"⭐ **@{user} coletou uma estrela!** Total: **{state['estrelas']}**. "
            "Uma nova estrela apareceu no mapa — obrigada por jogar! "
            "O tabuleiro no perfil atualiza em instantes."
        )
    else:
        msg = (
            f"🚀 @{user} moveu a exploradora para **{direcao}**! "
            f"Posição atual: ({nx}, {ny}). O tabuleiro no perfil atualiza em instantes."
        )

    save_state(state)
    render(state)
    return msg


def main():
    # console do Windows usa cp1252 por padrão — força UTF-8 para os emojis
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2 or sys.argv[1] not in ("render", "move"):
        raise SystemExit(__doc__)

    if sys.argv[1] == "render":
        state = load_state()
        save_state(state)
        render(state)
        print(f"Tabuleiro gerado: {OUT_FILE}")
        return

    if len(sys.argv) < 4:
        raise SystemExit("uso: expedicao.py move <direcao> <usuario>")
    print(move(sys.argv[2], sys.argv[3]))


if __name__ == "__main__":
    main()
