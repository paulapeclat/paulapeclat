#!/usr/bin/env python3
"""
Gera assets/mapa-alcance.svg a partir de data/alcance.json.

Os contornos do Brasil e de Portugal são projetados de coordenadas
geográficas reais (longitude/latitude do litoral e das fronteiras), e os
estados usam o centroide real de cada UF — o mapa é fidedigno, não um
polígono à mão livre.

Paula só edita data/alcance.json (base, lista de estados, textos) e comita —
o workflow regenera o mapa automaticamente.

Uso local: python scripts/generate_map.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "alcance.json"
OUT_FILE = ROOT / "assets" / "mapa-alcance.svg"

# Paleta real de paulapeclat.com.br
CYAN = "#22C3D9"
PINK = "#F23D91"
PINK_LIGHT = "#F2A2C0"
YELLOW = "#ECBE40"

# ---------------------------------------------------------------- BRASIL
# Contorno simplificado do Brasil (lon, lat) — litoral e fronteiras reais,
# sentido horário a partir do Monte Caburaí/RR (ponto mais ao norte).
BRASIL_OUTLINE = [
    (-60.20, 5.27), (-59.50, 4.40), (-56.50, 1.90), (-54.60, 2.30),
    (-52.60, 2.50), (-51.60, 4.20), (-51.00, 1.80), (-49.90, 1.10),
    (-48.40, -0.70), (-44.30, -2.40), (-41.80, -2.90), (-38.50, -3.70),
    (-35.50, -5.11), (-34.79, -7.15), (-35.00, -9.00), (-36.40, -10.50),
    (-38.50, -13.00), (-39.00, -16.30), (-39.70, -18.30), (-40.30, -20.30),
    (-41.90, -22.90), (-43.20, -23.05), (-45.00, -23.80), (-46.40, -24.00),
    (-48.00, -25.40), (-48.60, -26.70), (-48.60, -28.50), (-50.20, -30.00),
    (-51.50, -31.80), (-52.40, -32.60), (-53.37, -33.74),
    # fronteira oeste, do Chuí para o norte
    (-55.60, -30.80), (-57.60, -30.20), (-56.00, -28.50), (-54.70, -26.60),
    (-54.60, -25.50), (-54.30, -24.00), (-55.80, -22.30), (-56.50, -21.50),
    (-57.80, -20.70), (-57.70, -19.00), (-58.40, -17.30), (-60.20, -16.27),
    (-63.10, -12.50), (-65.30, -10.70), (-66.60, -9.90), (-69.60, -10.95),
    (-70.60, -9.80), (-72.20, -9.40), (-73.60, -8.50), (-73.99, -7.35),
    (-72.90, -5.10), (-69.90, -4.20), (-69.40, -1.50), (-69.80, 0.60),
    (-67.10, 1.70), (-66.90, 3.60), (-64.70, 4.20), (-63.40, 3.90),
    (-61.30, 4.50),
]

# Centroide aproximado de cada UF (lon, lat)
UF_COORDS = {
    "AC": (-70.5, -9.2), "AL": (-36.6, -9.5), "AP": (-52.0, 1.4),
    "AM": (-64.7, -4.2), "BA": (-41.7, -12.5), "CE": (-39.6, -5.1),
    "DF": (-47.8, -15.8), "ES": (-40.7, -19.6), "GO": (-49.6, -16.0),
    "MA": (-45.3, -5.1), "MT": (-55.9, -12.9), "MS": (-54.8, -20.3),
    "MG": (-44.7, -18.5), "PA": (-52.3, -3.8), "PB": (-36.8, -7.1),
    "PR": (-51.6, -24.6), "PE": (-37.6, -8.3), "PI": (-42.9, -7.4),
    "RJ": (-42.65, -22.2), "RN": (-36.7, -5.8), "RS": (-53.3, -29.7),
    "RO": (-62.8, -10.9), "RR": (-61.4, 2.1), "SC": (-50.5, -27.2),
    "SE": (-37.4, -10.6), "SP": (-48.7, -22.3), "TO": (-48.3, -10.2),
}

# projeção equiretangular com correção de longitude (cos da lat média ~15°S)
BR_SX, BR_SY = 6.3 * 0.96, 6.3
BR_ORIGIN = (112, 132)  # translate do grupo no canvas


def br(lon, lat):
    return round((lon + 74.0) * BR_SX, 1), round((5.3 - lat) * BR_SY, 1)


# --------------------------------------------------------------- PORTUGAL
# Contorno simplificado de Portugal continental (lon, lat), sentido horário
# a partir da foz do rio Minho.
PT_OUTLINE = [
    (-8.87, 41.87), (-8.75, 41.40), (-8.66, 41.10), (-8.78, 40.60),
    (-8.90, 40.15), (-9.08, 39.75), (-9.37, 39.36), (-9.50, 38.78),
    (-9.18, 38.68), (-9.00, 38.43), (-8.87, 38.00), (-8.82, 37.55),
    (-8.99, 37.02), (-8.50, 37.07), (-7.90, 37.00), (-7.40, 37.17),
    (-7.45, 37.60), (-7.10, 38.20), (-7.15, 38.88), (-6.95, 39.40),
    (-7.00, 39.67), (-6.86, 40.00), (-6.80, 40.36), (-6.85, 40.85),
    (-6.20, 41.35), (-6.55, 41.70), (-6.55, 41.94), (-7.20, 41.87),
    (-7.90, 41.85), (-8.20, 42.15), (-8.75, 41.94),
]
PT_SX, PT_SY = 8.9, 11.5
PT_ORIGIN = (765, 118)


def pt(lon, lat):
    return round((lon + 9.55) * PT_SX, 1), round((42.15 - lat) * PT_SY, 1)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def polygon(points, proj):
    coords = [proj(lon, lat) for lon, lat in points]
    return "M " + " L ".join(f"{x:g} {y:g}" for x, y in coords) + " Z"


def render_dots(estados, base):
    parts = ['    <g fill="' + PINK_LIGHT + '">']
    for i, uf in enumerate(estados):
        if uf == base:
            continue
        if uf not in UF_COORDS:
            print(f"aviso: UF desconhecida '{uf}' — ignorada", file=sys.stderr)
            continue
        x, y = br(*UF_COORDS[uf])
        parts.append(
            f'      <circle cx="{x:g}" cy="{y:g}" r="3">'
            f'<animate attributeName="opacity" values="0.5;1;0.5" dur="2.6s" begin="-{(i * 0.35) % 2.6:.2f}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    parts.append("    </g>")
    return "\n".join(parts)


def render_base(base):
    if base not in UF_COORDS:
        raise SystemExit(f"erro: base '{base}' não é uma UF conhecida")
    x, y = br(*UF_COORDS[base])
    return f'''    <circle cx="{x:g}" cy="{y:g}" r="14" fill="none" stroke="{PINK}" stroke-width="1.6">
      <animate attributeName="r" values="6;22" dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x:g}" cy="{y:g}" r="14" fill="none" stroke="{PINK}" stroke-width="1.6">
      <animate attributeName="r" values="6;22" dur="2.4s" begin="1.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.4s" begin="1.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x:g}" cy="{y:g}" r="5.5" fill="{PINK}" stroke="#FFFFFF" stroke-width="1.2"/>
    <text x="{x + 16:g}" y="{y - 2:g}" font-size="11" font-weight="700" fill="{PINK}">{base} · base</text>'''


def render_chips(chips):
    parts = ["  <g>"]
    x = 40
    for text, color in chips:
        width = round(len(text) * 6.3) + 32
        cx = x + width / 2
        rgba = {
            CYAN: ("rgba(34,195,217,0.10)", "rgba(34,195,217,0.4)"),
            PINK: ("rgba(242,61,145,0.10)", "rgba(242,61,145,0.4)"),
            YELLOW: ("rgba(236,190,64,0.10)", "rgba(236,190,64,0.4)"),
        }[color]
        parts.append(f'    <rect x="{x}" y="458" width="{width}" height="30" rx="15" fill="{rgba[0]}" stroke="{rgba[1]}"/>')
        parts.append(
            f'    <text x="{cx:g}" y="477" font-size="12" font-weight="600" fill="{color}" text-anchor="middle">{esc(text)}</text>'
        )
        x += width + 20
    parts.append("  </g>")
    return "\n".join(parts)


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    base = data.get("base", "RJ")
    estados = list(dict.fromkeys(data.get("estados", [])))
    if base not in estados:
        estados.insert(0, base)
    n = len(estados)
    todos = n >= len(UF_COORDS)

    caption = "alunos de todos os 27 estados" if todos else f"alunos em {n} estados"
    chip_brasil = "alunos de todos os 27 estados do Brasil" if todos else f"alunos de {n} estados do Brasil"
    chip_mundo = data.get("chip_mundo", "3 países · 3 continentes")
    chip_modo = data.get("chip_modo", "aulas online e presenciais")

    bx = BR_ORIGIN[0] + br(*UF_COORDS[base])[0]
    by = BR_ORIGIN[1] + br(*UF_COORDS[base])[1]

    # rotas: base → Nova York (pin abs ~495,58) e base → Portugal (pin abs ~780,112)
    rota_ny = f"M {bx:g} {by:g} Q {bx + (495 - bx) * 0.45:.0f} 28 495 58"
    rota_pt = f"M {bx:g} {by:g} Q {bx + (780 - bx) * 0.55:.0f} 2 780 112"

    brasil_path = polygon(BRASIL_OUTLINE, br)
    portugal_path = polygon(PT_OUTLINE, pt)

    svg = f'''<svg viewBox="0 0 1000 520" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="Mapa de alcance com geografia real: {caption}, Portugal e Nova York, com rotas animadas partindo da base {base}">
  <defs>
    <radialGradient id="mGlowCyan" cx="18%" cy="75%" r="60%">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="mGlowPink" cx="80%" cy="20%" r="55%">
      <stop offset="0%" stop-color="{PINK}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="mGlowYellow" cx="50%" cy="0%" r="55%">
      <stop offset="0%" stop-color="{YELLOW}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="{YELLOW}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="arcGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PINK}"/>
      <stop offset="100%" stop-color="{YELLOW}"/>
    </linearGradient>
    <linearGradient id="arcGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PINK}"/>
      <stop offset="100%" stop-color="{CYAN}"/>
    </linearGradient>
    <filter id="mGrain">
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

  <rect width="1000" height="520" fill="#000000"/>
  <rect width="1000" height="520" fill="url(#mGlowCyan)"/>
  <rect width="1000" height="520" fill="url(#mGlowPink)"/>
  <rect width="1000" height="520" fill="url(#mGlowYellow)"/>
  <rect width="1000" height="520" filter="url(#mGrain)" opacity="0.5"/>

  <g>
    <circle cx="80" cy="70" r="2" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.2s" repeatCount="indefinite"/></circle>
    <circle cx="200" cy="120" r="1.6" fill="{CYAN}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.6s" begin="0.7s" repeatCount="indefinite"/></circle>
    <circle cx="400" cy="60" r="2.2" fill="{PINK_LIGHT}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.8s" begin="1.2s" repeatCount="indefinite"/></circle>
    <circle cx="430" cy="200" r="1.4" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.8;0.3" dur="5s" begin="2s" repeatCount="indefinite"/></circle>
    <circle cx="560" cy="260" r="1.8" fill="{YELLOW}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4s" begin="0.4s" repeatCount="indefinite"/></circle>
    <circle cx="620" cy="100" r="1.5" fill="{CYAN}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.8s" begin="1.6s" repeatCount="indefinite"/></circle>
    <circle cx="700" cy="320" r="2" fill="{PINK_LIGHT}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.4s" begin="0.9s" repeatCount="indefinite"/></circle>
    <circle cx="850" cy="280" r="1.7" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="5.4s" begin="2.4s" repeatCount="indefinite"/></circle>
    <circle cx="900" cy="400" r="2.2" fill="{CYAN}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.6s" begin="0.2s" repeatCount="indefinite"/></circle>
    <circle cx="520" cy="410" r="1.5" fill="{YELLOW}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="3.9s" begin="1.1s" repeatCount="indefinite"/></circle>
    <circle cx="60" cy="440" r="1.8" fill="{PINK}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.7s" begin="1.9s" repeatCount="indefinite"/></circle>
    <circle cx="760" cy="440" r="1.5" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.8;0.3" dur="5.1s" begin="0.6s" repeatCount="indefinite"/></circle>
  </g>

  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="10s" repeatCount="indefinite"/>
    <circle cx="925" cy="72" r="15" fill="{PINK}" opacity="0.8"/>
    <circle cx="921" cy="67" r="4" fill="{PINK_LIGHT}" opacity="0.6"/>
    <ellipse cx="925" cy="72" rx="26" ry="6.5" fill="none" stroke="{YELLOW}" stroke-width="1.8" opacity="0.65" transform="rotate(-16 925 72)"/>
  </g>

  <text x="40" y="56" font-size="24" font-weight="800" fill="#FFFFFF" letter-spacing="1">MAPA DE ALCANCE</text>
  <text x="40" y="80" font-size="13" fill="rgba(255,255,255,0.6)">aulas, alunos e pesquisa — do Rio de Janeiro para o mundo</text>

  <!-- ================= BRASIL (contorno real projetado) ================= -->
  <g transform="translate({BR_ORIGIN[0]},{BR_ORIGIN[1]})">
    <ellipse cx="118" cy="262" rx="125" ry="15" fill="{CYAN}" opacity="0.07"/>
    <path d="{brasil_path}"
      fill="rgba(34,195,217,0.10)" stroke="{CYAN}" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="60" cy="256" r="3.4" fill="rgba(34,195,217,0.4)"><animate attributeName="cy" values="256;248;256" dur="6s" repeatCount="indefinite"/></circle>
    <circle cx="160" cy="240" r="2.4" fill="rgba(34,195,217,0.3)"><animate attributeName="cy" values="240;233;240" dur="7s" begin="1s" repeatCount="indefinite"/></circle>
    <circle cx="115" cy="268" r="2" fill="rgba(255,255,255,0.25)"><animate attributeName="cy" values="268;262;268" dur="5.4s" begin="0.5s" repeatCount="indefinite"/></circle>

{render_dots(estados, base)}

{render_base(base)}

    <text x="118" y="278" font-size="12" font-weight="600" fill="{CYAN}" text-anchor="middle" opacity="0.9">{caption}</text>
  </g>

  <!-- ================= ILHA NOVA YORK ================= -->
  <g transform="translate(455,60)">
    <animateTransform attributeName="transform" type="translate" values="455 60;455 54;455 60" dur="7s" repeatCount="indefinite"/>
    <ellipse cx="40" cy="46" rx="48" ry="10" fill="rgba(236,190,64,0.10)" stroke="rgba(236,190,64,0.45)" stroke-width="1.4"/>
    <g fill="rgba(236,190,64,0.28)" stroke="{YELLOW}" stroke-width="1">
      <rect x="14" y="16" width="8" height="30"/>
      <rect x="26" y="6" width="9" height="40"/>
      <rect x="39" y="18" width="8" height="28"/>
      <rect x="51" y="10" width="9" height="36"/>
      <rect x="64" y="24" width="7" height="22"/>
    </g>
    <circle cx="30.5" cy="14" r="1" fill="{YELLOW}"><animate attributeName="opacity" values="1;0.2;1" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="55.5" cy="18" r="1" fill="{YELLOW}"><animate attributeName="opacity" values="0.2;1;0.2" dur="2.8s" repeatCount="indefinite"/></circle>
    <circle cx="30.5" cy="26" r="1" fill="{YELLOW}"><animate attributeName="opacity" values="1;0.3;1" dur="3.2s" begin="0.6s" repeatCount="indefinite"/></circle>
    <circle cx="40" cy="-8" r="10" fill="none" stroke="{YELLOW}" stroke-width="1.4">
      <animate attributeName="r" values="4;16" dur="2.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <circle cx="40" cy="-8" r="4.5" fill="{YELLOW}" stroke="#FFFFFF" stroke-width="1"/>
    <text x="40" y="74" font-size="13" font-weight="700" fill="rgba(255,255,255,0.85)" text-anchor="middle">Nova York</text>
  </g>

  <!-- ================= PORTUGAL (contorno real projetado) ================= -->
  <g transform="translate({PT_ORIGIN[0]},{PT_ORIGIN[1]})">
    <animateTransform attributeName="transform" type="translate" values="{PT_ORIGIN[0]} {PT_ORIGIN[1]};{PT_ORIGIN[0]} {PT_ORIGIN[1] - 6};{PT_ORIGIN[0]} {PT_ORIGIN[1]}" dur="8s" repeatCount="indefinite"/>
    <ellipse cx="15" cy="66" rx="36" ry="8.5" fill="rgba(34,195,217,0.08)" stroke="rgba(34,195,217,0.35)" stroke-width="1.2"/>
    <path d="{portugal_path}"
      fill="rgba(34,195,217,0.12)" stroke="{CYAN}" stroke-width="1.5" stroke-linejoin="round"/>
    <circle cx="15" cy="-6" r="10" fill="none" stroke="{CYAN}" stroke-width="1.4">
      <animate attributeName="r" values="4;16" dur="2.6s" begin="0.8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.6s" begin="0.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="15" cy="-6" r="4.5" fill="{CYAN}" stroke="#FFFFFF" stroke-width="1"/>
    <text x="15" y="90" font-size="13" font-weight="700" fill="rgba(255,255,255,0.85)" text-anchor="middle">Portugal</text>
    <text x="15" y="106" font-size="10.5" font-weight="600" fill="{CYAN}" text-anchor="middle" opacity="0.85">aulas online</text>
  </g>

  <!-- ================= ROTAS ================= -->
  <path id="rota-ny" d="{rota_ny}" fill="none" stroke="url(#arcGrad1)" stroke-width="2" stroke-dasharray="3 9" opacity="0.8">
    <animate attributeName="stroke-dashoffset" values="0;-12" dur="0.9s" repeatCount="indefinite"/>
  </path>
  <path id="rota-pt" d="{rota_pt}" fill="none" stroke="url(#arcGrad2)" stroke-width="2" stroke-dasharray="3 9" opacity="0.8">
    <animate attributeName="stroke-dashoffset" values="0;-12" dur="0.9s" begin="0.45s" repeatCount="indefinite"/>
  </path>

  <g>
    <animateMotion dur="5.5s" repeatCount="indefinite" rotate="auto">
      <mpath xlink:href="#rota-ny"/>
    </animateMotion>
    <circle r="5.5" fill="{YELLOW}" opacity="0.25"/>
    <circle r="2.6" fill="#FFFFFF"/>
    <rect x="-14" y="-1" width="12" height="2" rx="1" fill="{YELLOW}" opacity="0.5"/>
  </g>
  <g>
    <animateMotion dur="7s" begin="1.4s" repeatCount="indefinite" rotate="auto">
      <mpath xlink:href="#rota-pt"/>
    </animateMotion>
    <circle r="5.5" fill="{CYAN}" opacity="0.25"/>
    <circle r="2.6" fill="#FFFFFF"/>
    <rect x="-14" y="-1" width="12" height="2" rx="1" fill="{CYAN}" opacity="0.5"/>
  </g>

  <!-- ================= LEGENDA ================= -->
{render_chips([(chip_brasil, CYAN), (chip_mundo, PINK), (chip_modo, YELLOW)])}
</svg>
'''
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"Mapa gerado: {OUT_FILE} ({n} estados, base {base}, contorno com {len(BRASIL_OUTLINE)} pontos)")


if __name__ == "__main__":
    main()
