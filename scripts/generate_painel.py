#!/usr/bin/env python3
"""
Gera assets/painel.svg, um painel no estilo dos Learning Analytics Dashboards
(LADs) com as minhas competências e habilidades no desenvolvimento das aulas.

Paula só edita data/painel.json (competências 0-100, ordem do currículo,
progresso do mestrado) e comita. O número de estados vem de data/alcance.json
e os anos de sala são contados a partir de "inicio_docencia".

Uso local: python scripts/generate_painel.py
"""
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "painel.json"
ALCANCE_FILE = ROOT / "data" / "alcance.json"
OUT_FILE = ROOT / "assets" / "painel.svg"

from paleta import AMARELO, AZUL, BRANCO, PRETO, RAMPA_ROXO as RAMPA, ROSA, ROXO, VERDE

CYAN = AZUL
CYAN_CLARO = AZUL
PINK = ROSA
AMBER = AMARELO
PURPLE = ROXO

TEXTO = BRANCO
TEXTO_2 = "#a1a1aa"
TEXTO_3 = "#71717a"
LINHA = "rgba(255,255,255,0.08)"
CARTAO = "rgba(255,255,255,0.035)"

W, H = 1000, 600


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kpis(itens) -> str:
    x, w, gap = 30, 223, 15
    partes = []
    for valor, rotulo, cor in itens:
        partes.append(f'''
  <g>
    <rect x="{x}" y="96" width="{w}" height="78" rx="12" fill="{CARTAO}" stroke="{LINHA}"/>
    <rect x="{x}" y="112" width="3" height="46" rx="1.5" fill="{cor}"/>
    <text x="{x + 20}" y="140" class="kpi">{esc(str(valor))}</text>
    <text x="{x + 20}" y="160" class="rot">{esc(rotulo)}</text>
  </g>''')
        x += w + gap
    return "".join(partes)


def radar(competencias, cx=257, cy=415, r=100) -> str:
    n = len(competencias)
    ang = [-math.pi / 2 + i * 2 * math.pi / n for i in range(n)]
    partes = []
    for nivel in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{cx + r * nivel * math.cos(a):.1f},{cy + r * nivel * math.sin(a):.1f}" for a in ang)
        partes.append(f'<polygon points="{pts}" fill="none" stroke="{LINHA}" stroke-width="1"/>')
    for a in ang:
        partes.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a):.1f}" y2="{cy + r * math.sin(a):.1f}" stroke="{LINHA}"/>')

    vals = [max(0, min(100, c["valor"])) / 100 for c in competencias]
    pts = " ".join(f"{cx + r * v * math.cos(a):.1f},{cy + r * v * math.sin(a):.1f}" for v, a in zip(vals, ang))
    partes.append(f'<polygon class="area" points="{pts}" fill="{CYAN_CLARO}" fill-opacity=".18" stroke="{CYAN_CLARO}" stroke-width="2" stroke-linejoin="round"/>')

    for c, v, a in zip(competencias, vals, ang):
        px, py = cx + r * v * math.cos(a), cy + r * v * math.sin(a)
        partes.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{CYAN_CLARO}" stroke="{PRETO}" stroke-width="2"><title>{esc(c["nome"])}: {c["valor"]}</title></circle>')
        lx, ly = cx + (r + 22) * math.cos(a), cy + (r + 22) * math.sin(a)
        ancora = "middle" if abs(math.cos(a)) < 0.3 else ("start" if math.cos(a) > 0 else "end")
        dy = -6 if math.sin(a) < -0.9 else (14 if math.sin(a) > 0.9 else 4)
        palavras = c["nome"].split()
        if len(c["nome"]) > 12 and len(palavras) > 1:
            meio = (len(palavras) + 1) // 2
            linhas = [" ".join(palavras[:meio]), " ".join(palavras[meio:])]
        else:
            linhas = [c["nome"]]
        topo = ly + dy - (14 if len(linhas) > 1 and math.sin(a) <= 0.9 else 0)
        spans = "".join(
            f'<tspan x="{lx:.1f}" dy="{0 if k == 0 else 14}">{esc(l)}</tspan>' for k, l in enumerate(linhas)
        )
        partes.append(f'<text x="{lx:.1f}" y="{topo:.1f}" text-anchor="{ancora}" class="eixo">{spans}<tspan class="val"> {c["valor"]}</tspan></text>')
    return "\n    ".join(partes)


def escada(curriculo, x0=520, y0=262, largura=225, altura_linha=31) -> str:
    n = len(curriculo)
    partes = []
    for i, item in enumerate(curriculo):
        y = y0 + i * altura_linha
        w = largura * (i + 1) / n
        cor = RAMPA[min(i, len(RAMPA) - 1)]
        partes.append(f'<text x="{x0 + 118}" y="{y + 16}" text-anchor="end" class="eixo">{esc(item["ferramenta"])}</text>')
        partes.append(f'<rect x="{x0 + 128}" y="{y + 3}" width="{w:.1f}" height="19" rx="4" fill="{cor}"><title>{esc(item["ferramenta"])}: {esc(item["tipo"])}</title></rect>')
        partes.append(f'<text x="{x0 + 136 + w:.1f}" y="{y + 16}" class="tipo">{esc(item["tipo"])}</text>')
    yb = y0 + n * altura_linha + 6
    partes.append(f'<line x1="{x0 + 128}" y1="{yb}" x2="{x0 + 128 + largura}" y2="{yb}" stroke="{LINHA}"/>')
    partes.append(f'<text x="{x0 + 128}" y="{yb + 16}" class="mini">concreto</text>')
    partes.append(f'<text x="{x0 + 128 + largura}" y="{yb + 16}" text-anchor="end" class="mini">abstrato →</text>')
    return "\n    ".join(partes)


def medidor(rotulo, pct, x=520, y=540, w=440) -> str:
    pct = max(0, min(100, pct))
    return f'''<text x="{x}" y="{y}" class="eixo">{esc(rotulo)}</text>
    <text x="{x + w}" y="{y}" text-anchor="end" class="val">{pct}%</text>
    <rect x="{x}" y="{y + 10}" width="{w}" height="8" rx="4" fill="rgba(255,255,255,0.08)"/>
    <rect x="{x}" y="{y + 10}" width="{w * pct / 100:.1f}" height="8" rx="4" fill="{PINK}"/>'''


def main():
    d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    alcance = json.loads(ALCANCE_FILE.read_text(encoding="utf-8"))
    n_estados = len(set(alcance.get("estados", [])) | {alcance.get("base", "RJ")})
    anos = date.today().year - d["inicio_docencia"]

    tiles = kpis([
        (anos, f"anos em sala de aula, desde {d['inicio_docencia']}", ROXO),
        (n_estados, "estados com alunos meus", AZUL),
        (d.get("paises", 1), "países com aulas", VERDE),
        (len(d["curriculo"]), "ferramentas no currículo", AMARELO),
    ])

    svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Painel de competências da Educação Tecnológica Paula Peclat: {anos} anos em sala de aula, alunos em {n_estados} estados, gráfico radar de competências docentes e escada do currículo do concreto ao abstrato">
  <defs>
    <radialGradient id="pGlow1" cx="12%" cy="90%" r="60%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
    <radialGradient id="pGlow2" cx="90%" cy="8%" r="55%"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".18"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
    <style>
      text {{ font-family: 'Segoe UI', 'Arial', sans-serif }}
      .h1 {{ font-size: 24px; font-weight: 800; fill: {TEXTO}; letter-spacing: 1px }}
      .sub {{ font-size: 13px; fill: {TEXTO_2} }}
      .kpi {{ font-size: 28px; font-weight: 800; fill: {TEXTO} }}
      .rot {{ font-size: 11.5px; fill: {TEXTO_2} }}
      .h2 {{ font-size: 13px; font-weight: 700; fill: {TEXTO}; letter-spacing: .5px }}
      .h2s {{ font-size: 11px; fill: {TEXTO_3} }}
      .eixo {{ font-size: 12px; fill: {TEXTO_2} }}
      .val {{ font-size: 12px; font-weight: 700; fill: {TEXTO} }}
      .tipo {{ font-size: 11px; fill: {TEXTO_3} }}
      .mini {{ font-size: 10.5px; fill: {TEXTO_3} }}
      @keyframes cresce {{ from {{ transform: scale(.2); opacity: 0 }} to {{ transform: scale(1); opacity: 1 }} }}
      .area {{ transform-box: view-box; transform-origin: 257px 415px; animation: cresce 1.4s cubic-bezier(.2,.8,.2,1) both }}
      @media (prefers-reduced-motion: reduce) {{ .area {{ animation: none }} }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" rx="18" fill="{PRETO}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#pGlow1)"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#pGlow2)"/>

  <text x="30" y="52" class="h1">{esc(d["titulo"])}</text>
  <text x="30" y="74" class="sub">{esc(d["subtitulo"])}</text>
{tiles}

  <rect x="30" y="192" width="455" height="384" rx="14" fill="{CARTAO}" stroke="{LINHA}"/>
  <text x="50" y="222" class="h2">COMPETÊNCIAS DOCENTES</text>
  <text x="50" y="239" class="h2s">autoavaliação, escala 0 a 100</text>
  <g>
    {radar(d["competencias"])}
  </g>

  <rect x="500" y="192" width="470" height="384" rx="14" fill="{CARTAO}" stroke="{LINHA}"/>
  <text x="520" y="222" class="h2">TRILHA DO CURRÍCULO</text>
  <text x="520" y="239" class="h2s">a ordem em que ensino, do concreto ao abstrato</text>
  <g>
    {escada(d["curriculo"])}
  </g>
  <g>
    {medidor(d["mestrado"]["rotulo"], d["mestrado"]["percentual"])}
  </g>
</svg>
'''
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"Painel gerado: {OUT_FILE.relative_to(ROOT)} ({len(d['competencias'])} competências, {len(d['curriculo'])} ferramentas)")


if __name__ == "__main__":
    main()
