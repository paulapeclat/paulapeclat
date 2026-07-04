#!/usr/bin/env python3
"""
Atualiza a seção "Recurso do dia" no README.md e README.en.md com um item
da lista curada awesome-educacao-midiatica, rotacionando por dia do ano.

Roda diariamente via .github/workflows/recurso-do-dia.yml.

Uso local: python scripts/recurso_do_dia.py
"""
import datetime
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTE = "https://raw.githubusercontent.com/paulapeclat/awesome-educacao-midiatica/main/README.md"

START = "<!--RECURSO-START-->"
END = "<!--RECURSO-END-->"
PATTERN = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
ENTRADA = re.compile(r"^- \[(.+?)\]\((https?://[^\s)]+)\) — (.+?)\.?\s*$", re.MULTILINE)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with urllib.request.urlopen(FONTE, timeout=30) as r:
        lista = r.read().decode("utf-8")

    recursos = ENTRADA.findall(lista)
    if not recursos:
        raise SystemExit("erro: nenhum recurso encontrado na lista curada")

    nome, url, desc = recursos[datetime.date.today().toordinal() % len(recursos)]
    print(f"Recurso de hoje: {nome} ({len(recursos)} na rotação)")

    for readme, texto in [
        (ROOT / "README.md", f"🎯 **[{nome}]({url})** — {desc}."),
        (ROOT / "README.en.md", f"🎯 **[{nome}]({url})** — {desc}. <sub>(PT)</sub>"),
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
