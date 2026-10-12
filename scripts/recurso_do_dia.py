#!/usr/bin/env python3
"""
Atualiza a seção "Recurso do dia" no README.md e README.en.md com um item
da lista curada awesome-educacao-midiatica, rotacionando por dia do ano.

Mostra dois recursos por dia, cada um com a sua rotação:
  🇧🇷 Brasil: sites com domínio .br, mais as iniciativas brasileiras que usam
     outro domínio (lista BRASILEIROS_SEM_BR)
  🌍 Mundo: todo o resto da lista

Roda diariamente via .github/workflows/recurso-do-dia.yml.

Uso local: python scripts/recurso_do_dia.py
"""
import datetime
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTE = "https://raw.githubusercontent.com/paulapeclat/awesome-educacao-midiatica/main/README.md"

START = "<!--RECURSO-START-->"
END = "<!--RECURSO-END-->"
PATTERN = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
BRASILEIROS_SEM_BR = {"aosfatos.org"}
ENTRADA = re.compile(r"^- \[(.+?)\]\((https?://[^\s)]+)\) — (.+?)\.?\s*$", re.MULTILINE)


def eh_brasileiro(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ""
    host = host.removeprefix("www.")
    return host.endswith(".br") or host in BRASILEIROS_SEM_BR


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with urllib.request.urlopen(FONTE, timeout=30) as r:
        lista = r.read().decode("utf-8")

    todos = ENTRADA.findall(lista)
    brasil = [r for r in todos if eh_brasileiro(r[1])]
    mundo = [r for r in todos if not eh_brasileiro(r[1])]
    if not brasil or not mundo:
        raise SystemExit("erro: a lista precisa ter recursos brasileiros e internacionais")

    hoje = datetime.date.today().toordinal()
    br_nome, br_url, br_desc = brasil[hoje % len(brasil)]
    mu_nome, mu_url, mu_desc = mundo[hoje % len(mundo)]
    print(f"Brasil: {br_nome} ({len(brasil)} na rotação) | Mundo: {mu_nome} ({len(mundo)} na rotação)")

    pt = (
        f"🇧🇷 **Brasil** · [{br_nome}]({br_url}): {br_desc}.\n\n"
        f"🌍 **Mundo** · [{mu_nome}]({mu_url}): {mu_desc}."
    )
    en = (
        f"🇧🇷 **Brazil** · [{br_nome}]({br_url}): {br_desc}. <sub>(PT)</sub>\n\n"
        f"🌍 **World** · [{mu_nome}]({mu_url}): {mu_desc}. <sub>(PT)</sub>"
    )

    for readme, texto in [
        (ROOT / "README.md", pt),
        (ROOT / "README.en.md", en),
    ]:
        if not readme.exists():
            continue
        conteudo = readme.read_text(encoding="utf-8")
        if not PATTERN.search(conteudo):
            print(f"aviso: marcadores RECURSO não encontrados em {readme.name}", file=sys.stderr)
            continue
        novo = PATTERN.sub(f"{START}\n{texto}\n{END}", conteudo)
        if novo != conteudo:
            readme.write_text(novo, encoding="utf-8")
            print(f"{readme.name} atualizado.")
        else:
            print(f"{readme.name}: sem mudança (mesmo recurso).")


if __name__ == "__main__":
    main()
