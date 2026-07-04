#!/usr/bin/env python3
"""
Gera assets/mapa-alcance.svg a partir de data/alcance.json.

Paula só edita data/alcance.json (base, lista de estados, textos dos chips)
e comita — o workflow update-map.yml regenera o mapa automaticamente.

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

# Posição aproximada de cada UF dentro da ilha low-poly do Brasil
# (coordenadas locais do grupo transladado para (120,150))
UF_COORDS = {
    "AC": (14, 105), "AL": (176, 84), "AP": (105, 22), "AM": (48, 58),
    "BA": (152, 96), "CE": (168, 52), "DF": (112, 106), "ES": (155, 138),
    "GO": (105, 118), "MA": (135, 55), "MT": (75, 100), "MS": (78, 140),
    "MG": (133, 126), "PA": (105, 52), "PB": (184, 68), "PR": (103, 182),
    "PE": (178, 74), "PI": (148, 70), "RJ": (147, 147), "RN": (182, 60),
    "RS": (76, 218), "RO": (35, 90), "RR": (55, 22), "SC": (90, 196),
    "SE": (168, 92), "SP": (122, 158), "TO": (118, 85),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_dots(estados, base):
    """Pontinhos pulsantes de alunos por estado (a base ganha marcador especial)."""
    parts = ['    <g fill="' + PINK_LIGHT + '">']
    delay = 0.0
    for uf in estados:
        if uf == base:
            continue
        if uf not in UF_COORDS:
            print(f"aviso: UF desconhecida '{uf}' — ignorada", file=sys.stderr)
            continue
        x, y = UF_COORDS[uf]
        parts.append(
            f'      <circle cx="{x}" cy="{y}" r="3">'
            f'<animate attributeName="opacity" values="0.5;1;0.5" dur="2.6s" begin="{delay:g}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
        delay = round(delay + 0.3, 2)
    parts.append("    </g>")
    return "\n".join(parts)


def render_base(base):
    if base not in UF_COORDS:
        raise SystemExit(f"erro: base '{base}' não é uma UF conhecida")
    x, y = UF_COORDS[base]
    return f'''    <circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{PINK}" stroke-width="1.6">
      <animate attributeName="r" values="6;22" dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{PINK}" stroke-width="1.6">
      <animate attributeName="r" values="6;22" dur="2.4s" begin="1.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.4s" begin="1.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x}" cy="{y}" r="5.5" fill="{PINK}" stroke="#FFFFFF" stroke-width="1.2"/>
    <text x="{x + 16}" y="{y - 2}" font-size="11" font-weight="700" fill="{PINK}">{base} · base</text>'''


def render_chips(chips):
    """Chips da legenda com largura proporcional ao texto."""
    parts = ["  <g>"]
    x = 40
    for text, color in chips:
        width = round(len(text) * 6.3) + 32
        cx = x + width / 2
        rgba = {
            CYAN: "rgba(34,195,217,0.10)|rgba(34,195,217,0.4)",
            PINK: "rgba(242,61,145,0.10)|rgba(242,61,145,0.4)",
            YELLOW: "rgba(236,190,64,0.10)|rgba(236,190,64,0.4)",
        }[color]
        fill, stroke = rgba.split("|")
        parts.append(f'    <rect x="{x}" y="458" width="{width}" height="30" rx="15" fill="{fill}" stroke="{stroke}"/>')
        parts.append(
            f'    <text x="{cx:g}" y="477" font-size="12" font-weight="600" fill="{color}" text-anchor="middle">{esc(text)}</text>'
        )
        x += width + 20
    parts.append("  </g>")
    return "\n".join(parts)


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    base = data.get("base", "RJ")
    estados = list(dict.fromkeys(data.get("estados", [])))  # únicos, ordem preservada
    if base not in estados:
        estados.insert(0, base)
    n = len(estados)

    caption = f"alunos em {n} estados"
    chip_brasil = f"alunos de {n} estados do Brasil"
    chip_mundo = data.get("chip_mundo", "3 países · 3 continentes")
    chip_modo = data.get("chip_modo", "aulas online e presenciais")

    svg = f'''<svg viewBox="0 0 1000 520" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="Mapa surreal de alcance: alunos em {n} estados do Brasil, Portugal e Nova York, com rotas animadas partindo da base {base}">
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
    <circle cx="350" cy="50" r="2.2" fill="{PINK_LIGHT}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.8s" begin="1.2s" repeatCount="indefinite"/></circle>
    <circle cx="430" cy="180" r="1.4" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.8;0.3" dur="5s" begin="2s" repeatCount="indefinite"/></circle>
    <circle cx="560" cy="240" r="1.8" fill="{YELLOW}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4s" begin="0.4s" repeatCount="indefinite"/></circle>
    <circle cx="620" cy="90" r="1.5" fill="{CYAN}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.8s" begin="1.6s" repeatCount="indefinite"/></circle>
    <circle cx="700" cy="300" r="2" fill="{PINK_LIGHT}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.4s" begin="0.9s" repeatCount="indefinite"/></circle>
    <circle cx="850" cy="260" r="1.7" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="5.4s" begin="2.4s" repeatCount="indefinite"/></circle>
    <circle cx="900" cy="400" r="2.2" fill="{CYAN}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.6s" begin="0.2s" repeatCount="indefinite"/></circle>
    <circle cx="520" cy="400" r="1.5" fill="{YELLOW}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="3.9s" begin="1.1s" repeatCount="indefinite"/></circle>
    <circle cx="150" cy="440" r="1.8" fill="{PINK}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.7s" begin="1.9s" repeatCount="indefinite"/></circle>
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

  <!-- ================= ILHA BRASIL ================= -->
  <g transform="translate(120,150)">
    <ellipse cx="100" cy="252" rx="120" ry="16" fill="{CYAN}" opacity="0.07"/>
    <path d="M 60 0 L 110 10 L 130 32 L 185 58 L 195 85 L 162 130 L 150 152 L 122 166 L 96 200 L 80 236 L 56 200 L 32 162 L 2 120 L 10 62 L 34 20 Z"
      fill="rgba(34,195,217,0.10)" stroke="{CYAN}" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="46" cy="246" r="3.4" fill="rgba(34,195,217,0.4)"><animate attributeName="cy" values="246;238;246" dur="6s" repeatCount="indefinite"/></circle>
    <circle cx="140" cy="230" r="2.4" fill="rgba(34,195,217,0.3)"><animate attributeName="cy" values="230;223;230" dur="7s" begin="1s" repeatCount="indefinite"/></circle>
    <circle cx="100" cy="260" r="2" fill="rgba(255,255,255,0.25)"><animate attributeName="cy" values="260;254;260" dur="5.4s" begin="0.5s" repeatCount="indefinite"/></circle>

{render_dots(estados, base)}

{render_base(base)}

    <text x="98" y="262" font-size="12" font-weight="600" fill="{CYAN}" text-anchor="middle" opacity="0.9">{caption}</text>
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

  <!-- ================= ILHA PORTUGAL ================= -->
  <g transform="translate(760,120)">
    <animateTransform attributeName="transform" type="translate" values="760 120;760 114;760 120" dur="8s" repeatCount="indefinite"/>
    <ellipse cx="24" cy="64" rx="36" ry="8.5" fill="rgba(34,195,217,0.08)" stroke="rgba(34,195,217,0.35)" stroke-width="1.2"/>
    <path d="M 20 0 L 34 4 L 32 26 L 38 40 L 30 58 L 14 60 L 10 38 L 16 20 Z"
      fill="rgba(34,195,217,0.12)" stroke="{CYAN}" stroke-width="1.5" stroke-linejoin="round"/>
    <circle cx="22" cy="-4" r="10" fill="none" stroke="{CYAN}" stroke-width="1.4">
      <animate attributeName="r" values="4;16" dur="2.6s" begin="0.8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.6s" begin="0.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="22" cy="-4" r="4.5" fill="{CYAN}" stroke="#FFFFFF" stroke-width="1"/>
    <text x="24" y="90" font-size="13" font-weight="700" fill="rgba(255,255,255,0.85)" text-anchor="middle">Portugal</text>
  </g>

  <!-- ================= ROTAS ================= -->
  <path id="rota-ny" d="M 267 297 Q 340 40 495 60" fill="none" stroke="url(#arcGrad1)" stroke-width="2" stroke-dasharray="3 9" opacity="0.8">
    <animate attributeName="stroke-dashoffset" values="0;-12" dur="0.9s" repeatCount="indefinite"/>
  </path>
  <path id="rota-pt" d="M 267 297 Q 560 10 782 116" fill="none" stroke="url(#arcGrad2)" stroke-width="2" stroke-dasharray="3 9" opacity="0.8">
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
    print(f"Mapa gerado: {OUT_FILE} ({n} estados, base {base})")


if __name__ == "__main__":
    main()
