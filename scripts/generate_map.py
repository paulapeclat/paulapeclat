#!/usr/bin/env python3
"""
Gera assets/mapa-alcance.svg a partir de data/alcance.json.

Os contornos de cada estado vêm da malha real das UFs (data/brasil-ufs.json)
e Portugal é projetado de coordenadas reais do litoral e da fronteira.

Paula só edita data/alcance.json (base, lista de estados, textos) e comita.
O workflow regenera o mapa automaticamente.

Uso local: python scripts/generate_map.py
"""
import json
import sys
from pathlib import Path
from paleta import AMARELO, AZUL, AZUL_FORTE, BRANCO, PRETO, ROSA, ROSA_CLARO, ROXO, VERDE, VERDE_AGUA, rgba  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "alcance.json"
OUT_FILE = ROOT / "assets" / "mapa-alcance.svg"

# Paleta real de paulapeclat.com.br

# ---------------------------------------------------------------- BRASIL
# Contornos reais de cada UF (lon, lat), simplificados a partir da malha do
# IBGE e guardados em data/brasil-ufs.json. Cada UF pode ter mais de um anel
# (ilhas grandes, como Marajó no PA).
UFS_FILE = ROOT / "data" / "brasil-ufs.json"

# tom de cada região, na paleta do site
REGIOES = {
    "Norte": (["AC", "AM", "AP", "PA", "RO", "RR", "TO"], AZUL),
    "Nordeste": (["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], ROSA),
    "Centro-Oeste": (["DF", "GO", "MS", "MT"], AMARELO),
    "Sudeste": (["ES", "MG", "RJ", "SP"], ROXO),
    "Sul": (["PR", "RS", "SC"], VERDE),
}
COR_UF = {uf: cor for ufs, cor in REGIOES.values() for uf in ufs}

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


def render_ufs(estados):
    ufs = json.loads(UFS_FILE.read_text(encoding="utf-8"))
    parts = ['    <g stroke="{PRETO}" stroke-width="0.9" stroke-linejoin="round">']
    for uf, aneis in ufs.items():
        ativo = uf in estados
        cor = COR_UF.get(uf, AZUL)
        d = " ".join(polygon(anel, br) for anel in aneis)
        parts.append(
            f'      <path d="{d}" fill="{cor}" fill-opacity="{0.55 if ativo else 0.12}"><title>{uf}</title></path>'
        )
    parts.append("    </g>")
    contorno = " ".join(polygon(anel, br) for aneis in ufs.values() for anel in aneis)
    return "\n".join(parts), contorno


def render_dots(estados, base):
    parts = ['    <g fill="' + BRANCO + '" stroke="' + PRETO + '" stroke-width="0.8">']
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
    return f'''    <circle cx="{x:g}" cy="{y:g}" r="14" fill="none" stroke="{ROSA}" stroke-width="1.6">
      <animate attributeName="r" values="6;22" dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x:g}" cy="{y:g}" r="14" fill="none" stroke="{ROSA}" stroke-width="1.6">
      <animate attributeName="r" values="6;22" dur="2.4s" begin="1.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.4s" begin="1.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x:g}" cy="{y:g}" r="5.5" fill="{ROSA}" stroke="#FFFFFF" stroke-width="1.2"/>
    <text x="{x + 16:g}" y="{y - 2:g}" font-size="11" font-weight="700" fill="{ROSA}">{base} · base</text>'''


def render_chips(chips):
    parts = ["  <g>"]
    x = 40
    for text, color in chips:
        width = round(len(text) * 6.3) + 32
        cx = x + width / 2
        rgba = {
            AZUL: ("rgba(18,169,219,0.10)", "rgba(18,169,219,0.4)"),
            ROSA: ("rgba(225,68,137,0.10)", "rgba(225,68,137,0.4)"),
            AMARELO: ("rgba(246,181,13,0.10)", "rgba(246,181,13,0.4)"),
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

    ufs_svg, _ = render_ufs(estados)
    portugal_path = polygon(PT_OUTLINE, pt)

    svg = f'''<svg viewBox="0 0 1000 520" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="Mapa de alcance com geografia real: {caption}, Portugal e Nova York, com rotas animadas partindo da base {base}">
  <defs>
    <radialGradient id="mGlowCyan" cx="18%" cy="75%" r="60%">
      <stop offset="0%" stop-color="{AZUL}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{AZUL}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="mGlowPink" cx="80%" cy="20%" r="55%">
      <stop offset="0%" stop-color="{ROSA}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{ROSA}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="mGlowYellow" cx="50%" cy="0%" r="55%">
      <stop offset="0%" stop-color="{AMARELO}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="{AMARELO}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="arcGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{ROSA}"/>
      <stop offset="100%" stop-color="{AMARELO}"/>
    </linearGradient>
    <linearGradient id="arcGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{ROSA}"/>
      <stop offset="100%" stop-color="{AZUL}"/>
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

  <rect width="1000" height="520" fill="{PRETO}"/>
  <rect width="1000" height="520" fill="url(#mGlowCyan)"/>
  <rect width="1000" height="520" fill="url(#mGlowPink)"/>
  <rect width="1000" height="520" fill="url(#mGlowYellow)"/>
  <rect width="1000" height="520" filter="url(#mGrain)" opacity="0.5"/>

  <g>
    <circle cx="80" cy="70" r="2" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.2s" repeatCount="indefinite"/></circle>
    <circle cx="200" cy="120" r="1.6" fill="{AZUL}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.6s" begin="0.7s" repeatCount="indefinite"/></circle>
    <circle cx="400" cy="60" r="2.2" fill="{ROSA_CLARO}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.8s" begin="1.2s" repeatCount="indefinite"/></circle>
    <circle cx="430" cy="200" r="1.4" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.8;0.3" dur="5s" begin="2s" repeatCount="indefinite"/></circle>
    <circle cx="560" cy="260" r="1.8" fill="{AMARELO}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4s" begin="0.4s" repeatCount="indefinite"/></circle>
    <circle cx="620" cy="100" r="1.5" fill="{AZUL}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.8s" begin="1.6s" repeatCount="indefinite"/></circle>
    <circle cx="700" cy="320" r="2" fill="{ROSA_CLARO}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.4s" begin="0.9s" repeatCount="indefinite"/></circle>
    <circle cx="850" cy="280" r="1.7" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="5.4s" begin="2.4s" repeatCount="indefinite"/></circle>
    <circle cx="900" cy="400" r="2.2" fill="{AZUL}"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.6s" begin="0.2s" repeatCount="indefinite"/></circle>
    <circle cx="520" cy="410" r="1.5" fill="{AMARELO}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="3.9s" begin="1.1s" repeatCount="indefinite"/></circle>
    <circle cx="60" cy="440" r="1.8" fill="{ROSA}"><animate attributeName="opacity" values="0.3;0.9;0.3" dur="4.7s" begin="1.9s" repeatCount="indefinite"/></circle>
    <circle cx="760" cy="440" r="1.5" fill="#FFFFFF"><animate attributeName="opacity" values="0.3;0.8;0.3" dur="5.1s" begin="0.6s" repeatCount="indefinite"/></circle>
  </g>

  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="10s" repeatCount="indefinite"/>
    <circle cx="925" cy="72" r="15" fill="{ROSA}" opacity="0.8"/>
    <circle cx="921" cy="67" r="4" fill="{ROSA_CLARO}" opacity="0.6"/>
    <ellipse cx="925" cy="72" rx="26" ry="6.5" fill="none" stroke="{AMARELO}" stroke-width="1.8" opacity="0.65" transform="rotate(-16 925 72)"/>
  </g>

  <text x="40" y="56" font-size="24" font-weight="800" fill="#FFFFFF" letter-spacing="1">MAPA DE ALCANCE</text>
  <text x="40" y="80" font-size="13" fill="rgba(255,255,255,0.6)">aulas, alunos e pesquisa · do Rio de Janeiro para o mundo</text>

  <!-- ================= BRASIL (contorno real projetado) ================= -->
  <g transform="translate({BR_ORIGIN[0]},{BR_ORIGIN[1]})">
{ufs_svg}

{render_dots(estados, base)}

{render_base(base)}

  </g>

  <!-- ================= ILHA NOVA YORK ================= -->
  <g transform="translate(455,60)">
    <animateTransform attributeName="transform" type="translate" values="455 60;455 54;455 60" dur="7s" repeatCount="indefinite"/>
    <ellipse cx="40" cy="46" rx="48" ry="10" fill="rgba(246,181,13,0.10)" stroke="rgba(246,181,13,0.45)" stroke-width="1.4"/>
    <g fill="rgba(246,181,13,0.28)" stroke="{AMARELO}" stroke-width="1">
      <rect x="14" y="16" width="8" height="30"/>
      <rect x="26" y="6" width="9" height="40"/>
      <rect x="39" y="18" width="8" height="28"/>
      <rect x="51" y="10" width="9" height="36"/>
      <rect x="64" y="24" width="7" height="22"/>
    </g>
    <circle cx="30.5" cy="14" r="1" fill="{AMARELO}"><animate attributeName="opacity" values="1;0.2;1" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="55.5" cy="18" r="1" fill="{AMARELO}"><animate attributeName="opacity" values="0.2;1;0.2" dur="2.8s" repeatCount="indefinite"/></circle>
    <circle cx="30.5" cy="26" r="1" fill="{AMARELO}"><animate attributeName="opacity" values="1;0.3;1" dur="3.2s" begin="0.6s" repeatCount="indefinite"/></circle>
    <circle cx="40" cy="-8" r="10" fill="none" stroke="{AMARELO}" stroke-width="1.4">
      <animate attributeName="r" values="4;16" dur="2.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <circle cx="40" cy="-8" r="4.5" fill="{AMARELO}" stroke="#FFFFFF" stroke-width="1"/>
    <text x="40" y="74" font-size="13" font-weight="700" fill="rgba(255,255,255,0.85)" text-anchor="middle">Nova York</text>
  </g>

  <!-- ================= PORTUGAL (contorno real projetado) ================= -->
  <g transform="translate({PT_ORIGIN[0]},{PT_ORIGIN[1]})">
    <animateTransform attributeName="transform" type="translate" values="{PT_ORIGIN[0]} {PT_ORIGIN[1]};{PT_ORIGIN[0]} {PT_ORIGIN[1] - 6};{PT_ORIGIN[0]} {PT_ORIGIN[1]}" dur="8s" repeatCount="indefinite"/>
    <ellipse cx="15" cy="66" rx="36" ry="8.5" fill="rgba(18,169,219,0.08)" stroke="rgba(18,169,219,0.35)" stroke-width="1.2"/>
    <path d="{portugal_path}"
      fill="rgba(18,169,219,0.12)" stroke="{AZUL}" stroke-width="1.5" stroke-linejoin="round"/>
    <circle cx="15" cy="-6" r="10" fill="none" stroke="{AZUL}" stroke-width="1.4">
      <animate attributeName="r" values="4;16" dur="2.6s" begin="0.8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.6s" begin="0.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="15" cy="-6" r="4.5" fill="{AZUL}" stroke="#FFFFFF" stroke-width="1"/>
    <text x="15" y="90" font-size="13" font-weight="700" fill="rgba(255,255,255,0.85)" text-anchor="middle">Portugal</text>
    <text x="15" y="106" font-size="10.5" font-weight="600" fill="{AZUL}" text-anchor="middle" opacity="0.85">aulas online</text>
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
    <circle r="5.5" fill="{AMARELO}" opacity="0.25"/>
    <circle r="2.6" fill="#FFFFFF"/>
    <rect x="-14" y="-1" width="12" height="2" rx="1" fill="{AMARELO}" opacity="0.5"/>
  </g>
  <g>
    <animateMotion dur="7s" begin="1.4s" repeatCount="indefinite" rotate="auto">
      <mpath xlink:href="#rota-pt"/>
    </animateMotion>
    <circle r="5.5" fill="{AZUL}" opacity="0.25"/>
    <circle r="2.6" fill="#FFFFFF"/>
    <rect x="-14" y="-1" width="12" height="2" rx="1" fill="{AZUL}" opacity="0.5"/>
  </g>

  <!-- ================= LEGENDA ================= -->
{render_chips([(chip_brasil, AZUL), (chip_mundo, ROSA), (chip_modo, AMARELO)])}
</svg>
'''
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"Mapa gerado: {OUT_FILE} ({n} estados, base {base}, contornos de 27 UFs)")


if __name__ == "__main__":
    main()
