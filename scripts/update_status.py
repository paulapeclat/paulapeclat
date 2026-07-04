#!/usr/bin/env python3
"""
Lê status.json e substitui o conteúdo entre os marcadores
<!--STATUS-START--> e <!--STATUS-END--> no README.md e no README.en.md.

Paula só edita status.json (emoji + texto; "text_en" é opcional para a
versão em inglês) e comita. O workflow roda este script automaticamente.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = ROOT / "status.json"

START_MARKER = "<!--STATUS-START-->"
END_MARKER = "<!--STATUS-END-->"

PATTERN = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)


def atualizar(readme: Path, emoji: str, text: str) -> bool:
    if not readme.exists():
        return False
    conteudo = readme.read_text(encoding="utf-8")
    if not PATTERN.search(conteudo):
        print(f"Erro: marcadores STATUS não encontrados em {readme.name}", file=sys.stderr)
        sys.exit(1)
    novo = PATTERN.sub(f"{START_MARKER}\n{emoji} {text}\n{END_MARKER}", conteudo)
    if novo != conteudo:
        readme.write_text(novo, encoding="utf-8")
        print(f"{readme.name} atualizado com novo status.")
        return True
    print(f"{readme.name}: nenhuma mudança necessária.")
    return False


def main():
    if not STATUS_FILE.exists():
        print(f"Erro: {STATUS_FILE} não encontrado.", file=sys.stderr)
        sys.exit(1)

    status = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    emoji = status.get("emoji", "🟢")
    text = status.get("text", "")
    text_en = status.get("text_en") or text  # cai no texto em PT se não houver tradução

    atualizar(ROOT / "README.md", emoji, text)
    atualizar(ROOT / "README.en.md", emoji, text_en)


if __name__ == "__main__":
    main()
