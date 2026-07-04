#!/usr/bin/env python3
"""
Lê status.json e substitui o conteúdo entre os marcadores
<!--STATUS-START--> e <!--STATUS-END--> no README.md.

Paula só edita status.json (emoji + texto) e comita.
O workflow do GitHub Actions roda este script automaticamente.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = ROOT / "status.json"
README_FILE = ROOT / "README.md"

START_MARKER = "<!--STATUS-START-->"
END_MARKER = "<!--STATUS-END-->"


def main():
    if not STATUS_FILE.exists():
        print(f"Erro: {STATUS_FILE} não encontrado.", file=sys.stderr)
        sys.exit(1)

    status = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    emoji = status.get("emoji", "🟢")
    text = status.get("text", "")

    readme = README_FILE.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )

    if not pattern.search(readme):
        print("Erro: marcadores STATUS-START/STATUS-END não encontrados no README.md", file=sys.stderr)
        sys.exit(1)

    replacement = f"{START_MARKER}\n{emoji} {text}\n{END_MARKER}"
    new_readme = pattern.sub(replacement, readme)

    if new_readme != readme:
        README_FILE.write_text(new_readme, encoding="utf-8")
        print("README.md atualizado com novo status.")
    else:
        print("Nenhuma mudança necessária.")


if __name__ == "__main__":
    main()
