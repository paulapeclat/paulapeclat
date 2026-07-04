#!/usr/bin/env python3
"""
Gera assets/stats.svg com dados reais da API do GitHub (REST, sem GraphQL —
evita exigir escopos extras além do GITHUB_TOKEN padrão do Actions).

Uso no workflow: o nome de usuário vem de $GITHUB_REPOSITORY_OWNER.
Uso local/teste: passe o usuário como argumento, ex.: python generate_stats.py octocat
"""
import os
import sys
import requests

API = "https://api.github.com"


def get_username():
    if len(sys.argv) > 1:
        return sys.argv[1]
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER")
    if owner:
        return owner
    raise SystemExit("Defina GITHUB_REPOSITORY_OWNER ou passe o usuário como argumento.")


def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_all_repos(username, headers):
    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"{API}/users/{username}/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "type": "owner"},
            timeout=20,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
        if len(batch) < 100:
            break
    return repos


def compute_stats(repos):
    total_repos = len(repos)
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)

    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    top_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_repos": total_repos,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "top_langs": top_langs,
    }


# Paleta real de paulapeclat.com.br
COLORS = {
    "bg": "#000000",
    "cyan": "#22C3D9",
    "pink": "#F23D91",
    "pink_light": "#F2A2C0",
    "yellow": "#ECBE40",
    "text": "#FFFFFF",
    "text_secondary": "rgba(255,255,255,0.65)",
}

LANG_COLOR_CYCLE = [COLORS["cyan"], COLORS["pink"], COLORS["yellow"], COLORS["pink_light"], "#8CD9E6"]


def render_svg(stats):
    width, height = 480, 260
    lang_max = max((count for _, count in stats["top_langs"]), default=1)

    lang_rows = []
    row_y = 150
    for i, (lang, count) in enumerate(stats["top_langs"]):
        bar_width = int(240 * (count / lang_max))
        color = LANG_COLOR_CYCLE[i % len(LANG_COLOR_CYCLE)]
        lang_rows.append(f'''
    <text x="24" y="{row_y}" font-size="13" fill="{COLORS['text_secondary']}">{lang}</text>
    <rect x="140" y="{row_y - 12}" width="240" height="10" rx="5" fill="rgba(255,255,255,0.08)"/>
    <rect x="140" y="{row_y - 12}" width="{bar_width}" height="10" rx="5" fill="{color}"/>
        ''')
        row_y += 26

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="glow" cx="20%" cy="15%" r="60%">
      <stop offset="0%" stop-color="{COLORS['cyan']}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{COLORS['cyan']}" stop-opacity="0"/>
    </radialGradient>
    <style>
      text {{ font-family: 'Segoe UI', 'Arial', sans-serif; }}
    </style>
  </defs>

  <rect width="{width}" height="{height}" rx="16" fill="{COLORS['bg']}"/>
  <rect width="{width}" height="{height}" rx="16" fill="url(#glow)"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="none" stroke="rgba(255,255,255,0.08)"/>

  <text x="24" y="38" font-size="16" font-weight="700" fill="{COLORS['text']}">GitHub — atividade</text>

  <text x="24" y="78" font-size="28" font-weight="800" fill="{COLORS['cyan']}">{stats['total_repos']}</text>
  <text x="24" y="96" font-size="11" fill="{COLORS['text_secondary']}">REPOSITÓRIOS</text>

  <text x="170" y="78" font-size="28" font-weight="800" fill="{COLORS['pink']}">{stats['total_stars']}</text>
  <text x="170" y="96" font-size="11" fill="{COLORS['text_secondary']}">ESTRELAS</text>

  <text x="316" y="78" font-size="28" font-weight="800" fill="{COLORS['yellow']}">{stats['total_forks']}</text>
  <text x="316" y="96" font-size="11" fill="{COLORS['text_secondary']}">FORKS</text>

  <text x="24" y="128" font-size="12" font-weight="600" letter-spacing="0.05em" fill="{COLORS['text_secondary']}">LINGUAGENS PRINCIPAIS</text>
  {''.join(lang_rows)}
</svg>'''
    return svg


def main():
    username = get_username()
    headers = get_headers()

    print(f"Buscando repositórios de {username}...")
    repos = fetch_all_repos(username, headers)
    stats = compute_stats(repos)
    print(f"Repos: {stats['total_repos']} | Estrelas: {stats['total_stars']} | Forks: {stats['total_forks']}")
    print(f"Top linguagens: {stats['top_langs']}")

    svg = render_svg(stats)

    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Salvo em {out_path}")


if __name__ == "__main__":
    main()
