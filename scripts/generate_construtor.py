#!/usr/bin/env python3
"""
Gera assets/construtor.svg, o construtor que entra no perfil, monta os blocos
da APedê e anuncia que está chegando. Animação 100% em CSS dentro do SVG,
então roda no README sem JavaScript.

Pra trocar as letras ou o balão, é só mudar LETRAS e BALAO e rodar o script.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAIDA = ROOT / "assets" / "construtor.svg"

LETRAS = ["A", "P", "E", "D", "Ê"]
CORES = ["#a855f7", "#fbbf24", "#38bdf8", "#ec4899", "#84cc16"]
TITULO = "em construção"
SUBTITULO = "tudo o que aprendi em sala, virando produto"
BALAO = "tá quase pronta! 🧱"

W, H = 1280, 240
CHAO = 200
CICLO = 13.0  # segundos
BLOCO, GAP, X0 = 72, 14, 420
X_CONSTRUTOR = X0 + len(LETRAS) * (BLOCO + GAP) + 40
ENTRADA = 2.2  # segundos andando até o lugar


def pct(seg: float) -> str:
    return f"{seg / CICLO * 100:.2f}%"


def keyframes_caminhada() -> str:
    """pernas e braço esquerdo balançam só enquanto ele anda"""
    passos = [f"0% {{ transform: rotate(0deg) }}"]
    t, lado = 0.0, 1
    while t < ENTRADA:
        t += 0.22
        passos.append(f"{pct(min(t, ENTRADA))} {{ transform: rotate({24 * lado}deg) }}")
        lado *= -1
    passos.append(f"{pct(ENTRADA + 0.15)} {{ transform: rotate(0deg) }}")
    passos.append("100% { transform: rotate(0deg) }")
    return "\n    ".join(passos)


def keyframes_martelo(inicio: float, fim: float) -> str:
    passos = ["0% { transform: rotate(0deg) }", f"{pct(inicio)} {{ transform: rotate(0deg) }}"]
    t, cima = inicio, True
    while t < fim:
        t += 0.18
        passos.append(f"{pct(t)} {{ transform: rotate({-75 if cima else 10}deg) }}")
        cima = not cima
    passos.append(f"{pct(fim + 0.2)} {{ transform: rotate(0deg) }}")
    passos.append("100% { transform: rotate(0deg) }")
    return "\n    ".join(passos)


def keyframes_bloco(chega: float) -> str:
    return "\n    ".join([
        "0% { transform: translateY(-220px); opacity: 0 }",
        f"{pct(chega - 0.01)} {{ transform: translateY(-220px); opacity: 0 }}",
        f"{pct(chega)} {{ transform: translateY(-220px); opacity: 1 }}",
        f"{pct(chega + 0.32)} {{ transform: translateY(0); opacity: 1 }}",
        f"{pct(chega + 0.42)} {{ transform: translateY(-14px); opacity: 1 }}",
        f"{pct(chega + 0.52)} {{ transform: translateY(0); opacity: 1 }}",
        f"{pct(CICLO - 1.2)} {{ transform: translateY(0); opacity: 1 }}",
        f"{pct(CICLO - 0.6)} {{ transform: translateY(0); opacity: 0 }}",
        "100% { transform: translateY(0); opacity: 0 }",
    ])


def keyframes_poeira(chega: float) -> str:
    c = chega + 0.32
    return "\n    ".join([
        "0% { opacity: 0; transform: scale(.3) }",
        f"{pct(c)} {{ opacity: 0; transform: scale(.3) }}",
        f"{pct(c + 0.05)} {{ opacity: .9; transform: scale(.6) }}",
        f"{pct(c + 0.5)} {{ opacity: 0; transform: scale(1.4) }}",
        "100% { opacity: 0; transform: scale(1.4) }",
    ])


def personagem() -> str:
    """mesmo boneco de blocos do site da Dev Academy, agora de capacete e martelo"""
    return f'''
  <g class="construtor">
    <g class="perna esq"><rect x="40" y="118" width="16" height="48" rx="4" fill="#ECBE40"/><rect x="38" y="158" width="20" height="10" rx="3" fill="#3f3f46"/></g>
    <g class="perna dir"><rect x="64" y="118" width="16" height="48" rx="4" fill="#ECBE40"/><rect x="62" y="158" width="20" height="10" rx="3" fill="#3f3f46"/></g>
    <g class="braco esq"><rect x="16" y="68" width="13" height="42" rx="6" fill="#F2A2C0"/></g>
    <rect x="30" y="64" width="60" height="56" rx="5" fill="#22C3D9"/>
    <rect x="30" y="64" width="60" height="56" rx="5" fill="url(#brilho)"/>
    <rect x="30" y="98" width="60" height="7" fill="#fbbf24"/>
    <rect x="52" y="98" width="7" height="7" fill="#3f3f46"/>
    <rect x="46" y="72" width="28" height="3" rx="1.5" fill="#fff" opacity=".35"/>
    <rect x="36" y="10" width="48" height="48" rx="6" fill="#F2A2C0"/>
    <circle cx="51" cy="34" r="4.5" fill="#18181b"/><circle cx="69" cy="34" r="4.5" fill="#18181b"/>
    <circle cx="52.5" cy="32.5" r="1.4" fill="#fff"/><circle cx="70.5" cy="32.5" r="1.4" fill="#fff"/>
    <path d="M50 45 Q60 52 70 45" stroke="#18181b" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="44" cy="44" r="3.5" fill="#ec4899" opacity=".45"/><circle cx="76" cy="44" r="3.5" fill="#ec4899" opacity=".45"/>
    <path d="M30 18 Q30 -4 60 -4 Q90 -4 90 18 Z" fill="#fbbf24"/>
    <rect x="26" y="15" width="68" height="7" rx="3.5" fill="#f59e0b"/>
    <rect x="56" y="-4" width="8" height="20" rx="3" fill="#f59e0b"/>
    <g class="braco dir martelo">
      <rect x="91" y="68" width="13" height="42" rx="6" fill="#F2A2C0"/>
      <rect x="95" y="94" width="6" height="40" rx="2" fill="#a16207" transform="rotate(-90 97.5 106)"/>
      <rect x="118" y="92" width="14" height="28" rx="3" fill="#a1a1aa" transform="rotate(-90 125 106)"/>
    </g>
  </g>'''


def gerar() -> str:
    chegadas = [ENTRADA + 0.5 + i * 0.85 for i in range(len(LETRAS))]
    martelo_fim = chegadas[-1] + 0.5
    balao_em = martelo_fim + 0.3

    css_blocos, svg_blocos = [], []
    for i, (letra, cor) in enumerate(zip(LETRAS, CORES)):
        x = X0 + i * (BLOCO + GAP)
        css_blocos.append(f"@keyframes cai{i} {{\n    {keyframes_bloco(chegadas[i])}\n  }}")
        css_blocos.append(f"@keyframes poeira{i} {{\n    {keyframes_poeira(chegadas[i])}\n  }}")
        css_blocos.append(f".b{i} {{ animation: cai{i} {CICLO}s linear infinite }}")
        css_blocos.append(f".p{i} {{ animation: poeira{i} {CICLO}s ease-out infinite; transform-box: fill-box; transform-origin: center }}")
        svg_blocos.append(f'''
  <g class="b{i}">
    <rect x="{x}" y="{CHAO - BLOCO}" width="{BLOCO}" height="{BLOCO}" rx="12" fill="{cor}"/>
    <rect x="{x}" y="{CHAO - BLOCO}" width="{BLOCO}" height="{BLOCO}" rx="12" fill="url(#brilho)"/>
    <rect x="{x + 6}" y="{CHAO - BLOCO + 6}" width="{BLOCO - 12}" height="8" rx="4" fill="#fff" opacity=".28"/>
    <text x="{x + BLOCO / 2}" y="{CHAO - BLOCO / 2 + 13}" text-anchor="middle" class="letra">{letra}</text>
  </g>
  <g class="p{i}"><ellipse cx="{x + 10}" cy="{CHAO - 2}" rx="9" ry="4" fill="#d4d4d8" opacity=".5"/><ellipse cx="{x + BLOCO - 10}" cy="{CHAO - 2}" rx="9" ry="4" fill="#d4d4d8" opacity=".5"/></g>''')

    escala = 0.78
    y_personagem = CHAO - 168 * escala
    bx = X_CONSTRUTOR + 40

    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Animação de um construtor de blocos de capacete que entra andando e monta, bloco por bloco, as letras {''.join(LETRAS)}">
<defs>
  <linearGradient id="fundo" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0b0b12"/><stop offset="1" stop-color="#120a1a"/>
  </linearGradient>
  <linearGradient id="brilho" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".18"/>
  </linearGradient>
  <radialGradient id="luz" cx=".75" cy=".2" r=".6"><stop offset="0" stop-color="#a855f7" stop-opacity=".22"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></radialGradient>
</defs>
<style>
  text {{ font-family: Poppins, "Segoe UI", Helvetica, Arial, sans-serif }}
  .letra {{ font-size: 38px; font-weight: 800; fill: #fff }}
  .kicker {{ font-size: 13px; letter-spacing: .3em; fill: #a1a1aa; font-weight: 600 }}
  .titulo {{ font-size: 30px; font-weight: 800; fill: #f4f4f5 }}
  .sub {{ font-size: 15px; fill: #d4d4d8 }}
  .balao-txt {{ font-size: 15px; font-weight: 700; fill: #18181b }}

  @keyframes entra {{
    0% {{ transform: translate({-260}px, {y_personagem:.1f}px) scale({escala}) }}
    {pct(ENTRADA)} {{ transform: translate({X_CONSTRUTOR}px, {y_personagem:.1f}px) scale({escala}) }}
    {pct(CICLO - 1.2)} {{ transform: translate({X_CONSTRUTOR}px, {y_personagem:.1f}px) scale({escala}); opacity: 1 }}
    {pct(CICLO - 0.6)} {{ transform: translate({X_CONSTRUTOR}px, {y_personagem:.1f}px) scale({escala}); opacity: 0 }}
    100% {{ transform: translate({X_CONSTRUTOR}px, {y_personagem:.1f}px) scale({escala}); opacity: 0 }}
  }}
  @keyframes passo {{
    {keyframes_caminhada()}
  }}
  @keyframes passo-inv {{
    {keyframes_caminhada().replace("rotate(", "rotate(-").replace("rotate(-0deg", "rotate(0deg").replace("rotate(--", "rotate(")}
  }}
  @keyframes martela {{
    {keyframes_martelo(chegadas[0] - 0.4, martelo_fim)}
  }}
  @keyframes balao {{
    0% {{ opacity: 0; transform: scale(.4) }}
    {pct(balao_em)} {{ opacity: 0; transform: scale(.4) }}
    {pct(balao_em + 0.25)} {{ opacity: 1; transform: scale(1.06) }}
    {pct(balao_em + 0.4)} {{ opacity: 1; transform: scale(1) }}
    {pct(CICLO - 1.2)} {{ opacity: 1; transform: scale(1) }}
    {pct(CICLO - 0.6)} {{ opacity: 0; transform: scale(1) }}
    100% {{ opacity: 0 }}
  }}
  @keyframes pisca {{ 0%, 100% {{ opacity: .25 }} 50% {{ opacity: 1 }} }}

  .construtor {{ animation: entra {CICLO}s cubic-bezier(.3,.7,.4,1) infinite }}
  .perna, .braco {{ transform-box: fill-box; transform-origin: 50% 8% }}
  .perna.esq, .braco.dir {{ animation: passo {CICLO}s linear infinite }}
  .perna.dir, .braco.esq {{ animation: passo-inv {CICLO}s linear infinite }}
  .braco.dir.martelo {{ animation: martela {CICLO}s linear infinite }}
  .balao {{ animation: balao {CICLO}s ease-out infinite; transform-box: fill-box; transform-origin: 15% 100% }}
  .estrela {{ animation: pisca 2.4s ease-in-out infinite }}
  .estrela.d1 {{ animation-delay: .8s }} .estrela.d2 {{ animation-delay: 1.6s }}
  {chr(10).join("  " + c for c in css_blocos)}

  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important }}
    .construtor {{ transform: translate({X_CONSTRUTOR}px, {y_personagem:.1f}px) scale({escala}) }}
  }}
</style>

<rect width="{W}" height="{H}" rx="18" fill="url(#fundo)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#luz)"/>
<circle class="estrela" cx="1180" cy="40" r="3" fill="#fbbf24"/>
<circle class="estrela d1" cx="1230" cy="150" r="4" fill="#ec4899"/>
<circle class="estrela d2" cx="360" cy="40" r="2.5" fill="#38bdf8"/>
<line x1="40" y1="{CHAO}" x2="{W - 40}" y2="{CHAO}" stroke="#3f3f46" stroke-width="2" stroke-dasharray="2 10" stroke-linecap="round"/>

<text x="60" y="88" class="kicker">&lt;/&gt; {TITULO.upper()}</text>
<text x="60" y="128" class="titulo">APedê Digital</text>
<text x="60" y="156" class="sub">{SUBTITULO}</text>
{''.join(svg_blocos)}
{personagem()}

<g class="balao">
  <rect x="{bx}" y="14" width="186" height="40" rx="20" fill="#fafafa"/>
  <path d="M{bx + 26} 52 L{bx + 18} 66 L{bx + 42} 52 Z" fill="#fafafa"/>
  <text x="{bx + 93}" y="40" text-anchor="middle" class="balao-txt">{BALAO}</text>
</g>
</svg>
'''


def main():
    SAIDA.write_text(gerar(), encoding="utf-8")
    print(f"{SAIDA.relative_to(ROOT)} gerado.")


if __name__ == "__main__":
    main()
