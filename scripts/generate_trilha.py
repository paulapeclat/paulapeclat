#!/usr/bin/env python3
"""
Gera assets/trilha-rpg.svg a partir de data/trilha.json.

A trilha é uma serpentina de 3 linhas; as estações são distribuídas
automaticamente e a personagem caminha parando em cada uma (animateMotion
com keyPoints calculados por comprimento de arco).

Paula só edita data/trilha.json (nomes e qual estação é a atual) e comita —
o workflow update-map.yml regenera a trilha automaticamente.

Uso local: python scripts/generate_trilha.py
"""
import base64
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "trilha.json"
OUT_FILE = ROOT / "assets" / "trilha-rpg.svg"
OBJETOS = ROOT / "assets" / "objetos"  # PNGs renderizados por scripts/render_objetos.py


def objeto(nome: str) -> str:
    """PNG do objeto 3D em base64 (SVG usado como imagem no README não carrega arquivo externo)"""
    arquivo = OBJETOS / f"{nome}.png"
    if not arquivo.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(arquivo.read_bytes()).decode("ascii")

CYAN = "#22C3D9"
PINK = "#F23D91"
PINK_LIGHT = "#F2A2C0"
YELLOW = "#ECBE40"
COLOR_CYCLE = [CYAN, YELLOW, PINK]

W, H = 1000, 640
# serpentina: 3 linhas horizontais ligadas por curvas
Y1, Y2, Y3 = 510, 360, 210
PATH_D = (
    f"M 80 {Y1} L 830 {Y1} "
    f"Q 905 {Y1} 905 {(Y1 + Y2) // 2} Q 905 {Y2} 825 {Y2} "
    f"L 175 {Y2} "
    f"Q 95 {Y2} 95 {(Y2 + Y3) // 2} Q 95 {Y3} 175 {Y3} "
    f"L 860 {Y3}"
)
FIM = (860, Y3)  # o "???" fica no fim do caminho


def quad_len(p0, c, p1, steps=60):
    total, prev = 0.0, p0
    for i in range(1, steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t**2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t**2 * p1[1]
        total += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y)
    return total


# comprimentos dos segmentos (na mesma ordem do PATH_D)
L1 = 830 - 80
Q2 = quad_len((830, Y1), (905, Y1), (905, (Y1 + Y2) / 2))
Q3 = quad_len((905, (Y1 + Y2) / 2), (905, Y2), (825, Y2))
L4 = 825 - 175
Q5 = quad_len((175, Y2), (95, Y2), (95, (Y2 + Y3) / 2))
Q6 = quad_len((95, (Y2 + Y3) / 2), (95, Y3), (175, Y3))
L7 = 860 - 175
TOTAL = L1 + Q2 + Q3 + L4 + Q5 + Q6 + L7


def linspace(a, b, n):
    if n == 1:
        return [(a + b) / 2]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def slots(n):
    """Distribui n estações nas 3 linhas e devolve [(x, y, arc_len), ...]."""
    base, extra = n // 3, n % 3
    counts = [base + (1 if i < extra else 0) for i in range(3)]
    out = []
    for x in linspace(130, 700, counts[0]):
        out.append((x, Y1, x - 80))
    for x in linspace(740, 200, counts[1]):
        out.append((x, Y2, L1 + Q2 + Q3 + (825 - x)))
    for x in linspace(280, 660, counts[2]):
        out.append((x, Y3, L1 + Q2 + Q3 + L4 + Q5 + Q6 + (x - 175)))
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def motion_keys(stop_fracs, move_s=2.2, pause_s=1.2):
    """keyPoints/keyTimes com parada em cada estação; devolve (dur, kps, kts)."""
    dur = len(stop_fracs) * (move_s + pause_s)
    kps, kts = ["0"], [0.0]
    t = 0.0
    for frac in stop_fracs:
        t += move_s / dur
        kps.append(fmt(frac))
        kts.append(t)
        t += pause_s / dur
        kps.append(fmt(frac))
        kts.append(t)
    kts[-1] = 1.0
    return dur, ";".join(kps), ";".join(fmt(v) for v in kts)


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    estacoes = data["estacoes"]
    n = len(estacoes)
    pos = slots(n)

    stop_fracs = [arc / TOTAL for _, _, arc in pos] + [1.0]
    dur, kps, kts = motion_keys(stop_fracs)

    motion = (
        f'<animateMotion dur="{dur:g}s" repeatCount="indefinite" rotate="0" calcMode="linear"\n'
        f'      keyPoints="{kps}"\n      keyTimes="{kts}">\n'
        f'      <mpath xlink:href="#trail"/>\n    </animateMotion>'
    )

    ilhas, nos = [], []
    for i, (est, (x, y, _)) in enumerate(zip(estacoes, pos)):
        cor = COLOR_CYCLE[i % 3]
        nome = esc(est["nome"])
        acima = i % 2 == 1
        ly = y - 34 if acima else y + 44
        ilhas.append(f'    <ellipse cx="{x:g}" cy="{y + 16}" rx="30" ry="8"/>')

        if est.get("atual"):
            nos.append(f'''  <g>
    <circle cx="{x:g}" cy="{y}" r="13" fill="none" stroke="{PINK}" stroke-width="2">
      <animate attributeName="r" values="13;30" dur="2.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x:g}" cy="{y}" r="13" fill="none" stroke="{PINK}" stroke-width="2">
      <animate attributeName="r" values="13;30" dur="2.2s" begin="1.1s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0" dur="2.2s" begin="1.1s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{x:g}" cy="{y}" r="18" fill="{PINK}" opacity="0.2"/>
    <circle cx="{x:g}" cy="{y}" r="13" fill="{PINK}"/>
    <text x="{x:g}" y="{y + 5.5}" font-size="13" font-weight="700" fill="#06090C" text-anchor="middle">★</text>
    <text x="{x:g}" y="{ly}" font-size="12.5" font-weight="700" fill="{PINK_LIGHT}" text-anchor="middle">{nome}</text>
    <text x="{x + 38:g}" y="{y - 15}" font-size="12" font-weight="700" fill="{YELLOW}" text-anchor="middle" opacity="0">
      +10 XP
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -20" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;0" keyTimes="0;0.3;1" dur="3s" repeatCount="indefinite"/>
    </text>
  </g>''')
        else:
            nos.append(f'''  <g>
    <circle cx="{x:g}" cy="{y}" r="16" fill="{cor}" opacity="0.15"/>
    <circle cx="{x:g}" cy="{y}" r="11" fill="{cor}"/>
    <use href="#check" x="{x:g}" y="{y}"/>
    <text x="{x:g}" y="{ly}" font-size="12.5" font-weight="600" fill="#ffffff" text-anchor="middle">{nome}</text>
  </g>''')

    fx, fy = FIM
    futuro = f'''  <g>
    <circle cx="{fx}" cy="{fy}" r="11" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="2" stroke-dasharray="4 5">
      <animateTransform attributeName="transform" type="rotate" values="0 {fx} {fy};360 {fx} {fy}" dur="14s" repeatCount="indefinite"/>
    </circle>
    <text x="{fx}" y="{fy + 5}" font-size="12" font-weight="700" fill="rgba(255,255,255,0.55)" text-anchor="middle">?</text>
    <text x="{fx}" y="{fy - 26}" font-size="12" font-weight="600" fill="rgba(255,255,255,0.45)" text-anchor="middle">próximo nível</text>
  </g>'''

    svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="Trilha da jornada de Paula Peclat, estilo mapa de jogo, com personagem caminhando entre {n} estações, da Pedagogia ao Mestrado">
  <defs>
    <linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2f86e6"/>
      <stop offset="65%" stop-color="#6cb8f2"/>
      <stop offset="100%" stop-color="#a9dcfb"/>
    </linearGradient>
    <radialGradient id="sol" cx="8%" cy="6%" r="38%">
      <stop offset="0%" stop-color="#fff6c8" stop-opacity="0.9"/>
      <stop offset="35%" stop-color="#ffe9a0" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ffe9a0" stop-opacity="0"/>
    </radialGradient>
    <g id="nuvem">
      <ellipse cx="0" cy="0" rx="46" ry="15"/>
      <ellipse cx="-20" cy="-9" rx="22" ry="17"/>
      <ellipse cx="12" cy="-14" rx="26" ry="21"/>
    </g>
    <linearGradient id="heroGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#8CD9E6"/>
      <stop offset="100%" stop-color="{CYAN}"/>
    </linearGradient>
    <g id="check">
      <path d="M -4.5 0.5 L -1.5 3.5 L 5 -4.5" fill="none" stroke="#06090C" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    <style>
      text {{ font-family: 'Segoe UI', 'Arial', sans-serif; paint-order: stroke; stroke: rgba(10,52,110,0.55); stroke-width: 3px; stroke-linejoin: round; }}
      @keyframes deriva {{ from {{ transform: translateX(0) }} to {{ transform: translateX(1150px) }} }}
      .nuvens use {{ animation: deriva linear infinite }}
      @keyframes voo {{ 0%, 100% {{ transform: translate(0, 0) rotate(0deg) }} 50% {{ transform: translate(6px, -10px) rotate(-3deg) }} }}
      .foguete {{ animation: voo 5s ease-in-out infinite; transform-box: fill-box; transform-origin: center }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#ceu)"/>
  <rect width="{W}" height="{H}" fill="url(#sol)"/>

  <!-- nuvens passando devagar, cada uma num ritmo -->
  <g class="nuvens" fill="#ffffff">
    <use href="#nuvem" x="-80" y="130" opacity="0.85" style="animation-duration:95s; animation-delay:-20s"/>
    <use href="#nuvem" x="-80" y="290" opacity="0.6" transform="scale(0.8)" style="animation-duration:120s; animation-delay:-70s"/>
    <use href="#nuvem" x="-80" y="440" opacity="0.7" style="animation-duration:105s; animation-delay:-45s"/>
    <use href="#nuvem" x="-80" y="600" opacity="0.8" style="animation-duration:85s; animation-delay:-5s"/>
    <use href="#nuvem" x="-80" y="70" opacity="0.5" transform="scale(0.7)" style="animation-duration:140s; animation-delay:-100s"/>
  </g>

  <!-- foguete (modelo Smooth Voxels renderizado com three.js) -->
  {f'<image class="foguete" href="{objeto("foguete")}" x="575" y="12" width="118" height="118"/>' if objeto("foguete") else ""}

  <!-- titulo -->
  <text x="40" y="54" font-size="26" font-weight="800" fill="#FFFFFF" letter-spacing="1">A TRILHA</text>
  <text x="40" y="78" font-size="13" fill="rgba(255,255,255,0.92)">do concreto ao abstrato · do lúdico ao formal · uma jornada em construção</text>

  <!-- chip XP -->
  <rect x="790" y="30" width="176" height="30" rx="15" fill="rgba(10,52,110,0.45)" stroke="rgba(255,255,255,0.6)"/>
  <text x="878" y="49" font-size="12" font-weight="600" fill="#ffffff" text-anchor="middle" letter-spacing="0.5">XP: +∞ curiosidade</text>

  <!-- trilha: leito, linha-guia e fluxo de pontos -->
  <path id="trail" d="{PATH_D}" fill="none" stroke="rgba(10,52,110,0.28)" stroke-width="16" stroke-linecap="round"/>
  <use href="#trail" stroke="rgba(255,255,255,0.45)" stroke-width="2" stroke-dasharray="6 10"/>
  <path d="{PATH_D}" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-dasharray="0.1 16" opacity="0.95">
    <animate attributeName="stroke-dashoffset" values="0;-16.1" dur="1.2s" repeatCount="indefinite"/>
  </path>

  <!-- ilhas flutuantes sob as estações -->
  <g fill="rgba(255,255,255,0.75)">
{chr(10).join(ilhas)}
  </g>

  <!-- estações -->
{chr(10).join(nos)}

{futuro}

  <!-- faísca companheira (segue a heroína com atraso) -->
  <g>
    {motion.replace('repeatCount="indefinite" rotate="0"', f'repeatCount="indefinite" rotate="0" begin="-{dur - 1.6:g}s"')}
    <circle cy="-14" r="5" fill="{PINK_LIGHT}" opacity="0.25"/>
    <circle cy="-14" r="2.2" fill="{PINK_LIGHT}">
      <animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- a heroína -->
  <g>
    {motion}
    <ellipse cx="0" cy="1" rx="9" ry="2.6" fill="#000000" opacity="0.55"/>
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 -2;0 -6;0 -2" dur="1.4s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="-3" rx="6.5" ry="3" fill="{CYAN}" opacity="0.45">
        <animate attributeName="opacity" values="0.45;0.12;0.45" dur="0.7s" repeatCount="indefinite"/>
      </ellipse>
      <rect x="-10" y="-32" width="20" height="23" rx="8" fill="url(#heroGrad)" stroke="rgba(255,255,255,0.55)" stroke-width="1"/>
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

  <!-- legenda -->
  <text x="40" y="618" font-size="11" fill="rgba(255,255,255,0.9)">▣ concluído&#160;&#160;&#160;★ em andamento&#160;&#160;&#160;? em breve · a personagem caminha sozinha, espere e veja</text>
</svg>
'''
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"Trilha gerada: {OUT_FILE} ({n} estações, ciclo de {dur:g}s)")


if __name__ == "__main__":
    main()
