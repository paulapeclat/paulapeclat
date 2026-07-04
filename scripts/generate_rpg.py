#!/usr/bin/env python3
"""
Gera assets/rpg-card.svg a partir de data/rpg.json.

A ficha de jogadora mostra a barra de XP do mestrado, as barras de
habilidade e as conquistas desbloqueadas. Paula só edita data/rpg.json
(percentual de XP, habilidades com valor 0-100, conquistas com emoji) e
comita — o workflow update-map.yml regenera a ficha automaticamente.

O layout se adapta: mais de 4 habilidades ou mais de 4 conquistas
aumentam a altura/comprimem o espaçamento sem quebrar o card.

Uso local: python scripts/generate_rpg.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "rpg.json"
OUT_FILE = ROOT / "assets" / "rpg-card.svg"

CYAN = "#22C3D9"
PINK = "#F23D91"
PINK_LIGHT = "#F2A2C0"
YELLOW = "#ECBE40"
SKILL_CYCLE = [PINK, CYAN, YELLOW, PINK_LIGHT]

W = 520
XP_X, XP_W = 24, 472          # barra de XP
BAR_X, BAR_W = 150, 280       # barras de habilidade
SKILL_Y0, SKILL_DY = 136, 30  # primeira barra e espaçamento vertical


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rgba(hex_color, a):
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{a})"


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    nome = esc(data["nome"])
    classe = esc(data["classe"])
    xp = data["xp"]
    pct = max(0, min(100, xp["percentual"]))
    habilidades = data["habilidades"]
    conquistas = data["conquistas"]

    # altura cresce com habilidades além das 4 originais
    extra = max(0, len(habilidades) - 4) * SKILL_DY
    h = 340 + extra
    conq_title_y = 270 + extra
    conq_cy = 296 + extra
    conq_label_y = 328 + extra

    xp_fill = round(XP_W * pct / 100)

    barras = []
    for i, hab in enumerate(habilidades):
        cor = SKILL_CYCLE[i % len(SKILL_CYCLE)]
        valor = max(0, min(100, hab["valor"]))
        largura = round(BAR_W * valor / 100)
        y = SKILL_Y0 + i * SKILL_DY
        begin = 0.2 + i * 0.2
        barras.append(f'''  <rect x="{BAR_X}" y="{y}" width="{BAR_W}" height="10" rx="5" fill="rgba(255,255,255,0.08)"/>
  <rect x="{BAR_X}" y="{y}" width="{largura}" height="10" rx="5" fill="{cor}">
    <animate attributeName="width" from="0" to="{largura}" dur="1.3s" begin="{begin:g}s" fill="freeze"/>
  </rect>
  <text x="496" y="{y + 9}" font-size="11" font-weight="700" fill="{cor}" text-anchor="end">{valor}</text>''')

    rotulos = "\n".join(
        f'    <text x="24" y="{SKILL_Y0 + i * SKILL_DY + 10}">{esc(h["nome"])}</text>'
        for i, h in enumerate(habilidades)
    )

    # conquistas + slot "em breve"; comprime o espaçamento se não couberem
    n_slots = len(conquistas) + 1
    espaco = 92 if 48 + (n_slots - 1) * 92 <= 480 else (480 - 48) / (n_slots - 1)
    slots = []
    for i, c in enumerate(conquistas):
        cor = SKILL_CYCLE[i % len(SKILL_CYCLE)]
        cx = round(48 + i * espaco)
        slots.append(f'''    <circle cx="{cx}" cy="{conq_cy}" r="16" fill="{rgba(cor, 0.10)}" stroke="{rgba(cor, 0.5)}" stroke-width="1.2"/>
    <text x="{cx}" y="{conq_cy + 6}" font-size="15" text-anchor="middle">{esc(c["emoji"])}</text>
    <text x="{cx}" y="{conq_label_y}" font-size="9.5" fill="rgba(255,255,255,0.5)" text-anchor="middle">{esc(c["rotulo"])}</text>''')

    fx = round(48 + len(conquistas) * espaco)
    slots.append(f'''    <circle cx="{fx}" cy="{conq_cy}" r="16" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="1.2" stroke-dasharray="4 4">
      <animateTransform attributeName="transform" type="rotate" values="0 {fx} {conq_cy};360 {fx} {conq_cy}" dur="16s" repeatCount="indefinite"/>
    </circle>
    <text x="{fx}" y="{conq_cy + 5}" font-size="13" font-weight="700" fill="rgba(255,255,255,0.4)" text-anchor="middle">?</text>
    <text x="{fx}" y="{conq_label_y}" font-size="9.5" fill="rgba(255,255,255,0.35)" text-anchor="middle">em breve</text>''')

    svg = f'''<svg viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ficha de jogadora de {nome}: barras de habilidade, XP do mestrado e conquistas desbloqueadas">
  <defs>
    <radialGradient id="cGlow" cx="18%" cy="12%" r="70%">
      <stop offset="0%" stop-color="{PINK}" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="xpGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PINK}"/>
      <stop offset="100%" stop-color="{PINK_LIGHT}"/>
    </linearGradient>
    <clipPath id="xpClip">
      <rect x="{XP_X}" y="96" width="{XP_W}" height="14" rx="7"/>
    </clipPath>
    <style>
      text {{ font-family: 'Segoe UI', 'Arial', sans-serif; }}
    </style>
  </defs>

  <rect width="{W}" height="{h}" rx="16" fill="#000000"/>
  <rect width="{W}" height="{h}" rx="16" fill="url(#cGlow)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="16" fill="none" stroke="rgba(255,255,255,0.08)"/>

  <!-- header -->
  <text x="24" y="34" font-size="11" font-weight="600" letter-spacing="2" fill="rgba(255,255,255,0.5)">FICHA DE JOGADORA</text>
  <text x="24" y="60" font-size="21" font-weight="800" fill="#FFFFFF">{nome}</text>

  <rect x="380" y="30" width="116" height="30" rx="15" fill="{rgba(CYAN, 0.12)}" stroke="{rgba(CYAN, 0.4)}"/>
  <text x="438" y="49" font-size="12" font-weight="700" fill="{CYAN}" text-anchor="middle">{classe}</text>

  <!-- XP principal -->
  <text x="24" y="88" font-size="12" fill="rgba(255,255,255,0.65)">{esc(xp["rotulo"])}</text>
  <text x="496" y="88" font-size="12" font-weight="700" fill="{PINK}" text-anchor="end">{pct}%</text>
  <rect x="{XP_X}" y="96" width="{XP_W}" height="14" rx="7" fill="rgba(255,255,255,0.08)"/>
  <rect x="{XP_X}" y="96" width="{xp_fill}" height="14" rx="7" fill="url(#xpGrad)">
    <animate attributeName="width" from="0" to="{xp_fill}" dur="1.8s" fill="freeze"/>
  </rect>
  <g clip-path="url(#xpClip)">
    <rect x="-90" y="96" width="60" height="14" fill="#FFFFFF" opacity="0.22" transform="skewX(-20)">
      <animate attributeName="x" values="-90;560" dur="2.8s" begin="1.9s" repeatCount="indefinite"/>
    </rect>
  </g>

  <!-- habilidades -->
  <g font-size="13" fill="rgba(255,255,255,0.65)">
{rotulos}
  </g>

{chr(10).join(barras)}

  <!-- conquistas -->
  <text x="24" y="{conq_title_y}" font-size="11" font-weight="600" letter-spacing="2" fill="rgba(255,255,255,0.5)">CONQUISTAS</text>

  <g>
{chr(10).join(slots)}
  </g>

  <!-- faísca -->
  <circle cx="486" cy="{conq_cy - 8}" r="2.2" fill="{YELLOW}">
    <animate attributeName="opacity" values="0.2;1;0.2" dur="2.4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="474" cy="{conq_cy + 8}" r="1.5" fill="{PINK_LIGHT}">
    <animate attributeName="opacity" values="1;0.2;1" dur="3s" begin="0.8s" repeatCount="indefinite"/>
  </circle>
</svg>
'''
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(
        f"Ficha gerada: {OUT_FILE} "
        f"(XP {pct}%, {len(habilidades)} habilidades, {len(conquistas)} conquistas)"
    )


if __name__ == "__main__":
    main()
