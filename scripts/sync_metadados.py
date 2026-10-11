#!/usr/bin/env python3
"""
Sincroniza os metadados dos meus repositórios (descrição, site e tópicos)
a partir de data/repos.json e gera data/metadados-relatorio.md com o que
ainda falta em cada repo público.

Paula só edita data/repos.json e comita. O workflow roda este script.

Precisa do secret METADADOS_TOKEN (token fine-grained com acesso aos repos
e permissão "Administration: Read and write" + "Metadata: Read").

Rodar local sem mexer em nada (só mostra o que faria):
    METADADOS_TOKEN=... python scripts/sync_metadados.py --simular
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "repos.json"
RELATORIO = ROOT / "data" / "metadados-relatorio.md"
USUARIA = "paulapeclat"
API = "https://api.github.com"

TOPICO_VALIDO = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


def chamar(metodo: str, caminho: str, token: str, corpo=None):
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(API + caminho, data=dados, method=metodo)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if dados:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            texto = resp.read().decode("utf-8")
            return json.loads(texto) if texto else None
    except urllib.error.HTTPError as erro:
        msg = erro.read().decode("utf-8", "replace")
        print(f"Erro {erro.code} em {metodo} {caminho}: {msg}", file=sys.stderr)
        raise


def listar_repos(token: str) -> list:
    repos, pagina = [], 1
    while True:
        lote = chamar("GET", f"/users/{USUARIA}/repos?per_page=100&page={pagina}&type=owner", token)
        if not lote:
            return repos
        repos += lote
        pagina += 1


def limpar_topicos(topicos: list) -> list:
    vistos = []
    for t in topicos:
        t = t.strip().lower().replace(" ", "-")
        if not TOPICO_VALIDO.match(t):
            print(f"aviso: tópico ignorado (formato inválido): {t}", file=sys.stderr)
            continue
        if t not in vistos:
            vistos.append(t)
    return vistos[:20]  # o GitHub aceita no máximo 20


def aplicar(repo: dict, alvo: dict, padrao: dict, token: str, simular: bool) -> list:
    nome = repo["name"]
    mudancas = []

    campos = {}
    descricao = alvo.get("description")
    if descricao and descricao != (repo.get("description") or ""):
        campos["description"] = descricao
    site = alvo.get("homepage", padrao.get("homepage"))
    if site and site != (repo.get("homepage") or ""):
        campos["homepage"] = site
    if campos:
        mudancas.append(", ".join(campos))
        if not simular:
            chamar("PATCH", f"/repos/{USUARIA}/{nome}", token, campos)

    topicos = limpar_topicos(padrao.get("topics", []) + alvo.get("topics", []))
    if sorted(topicos) != sorted(repo.get("topics") or []):
        mudancas.append("topics")
        if not simular:
            chamar("PUT", f"/repos/{USUARIA}/{nome}/topics", token, {"names": topicos})

    return mudancas


def pendencias(repo: dict) -> list:
    falta = []
    if not repo.get("description"):
        falta.append("descrição")
    if not repo.get("topics"):
        falta.append("tópicos")
    if not repo.get("license"):
        falta.append("licença")
    if not repo.get("homepage"):
        falta.append("site")
    return falta


def escrever_relatorio(repos: list) -> None:
    publicos = [r for r in repos if not r["private"] and not r["fork"] and not r["archived"]]
    publicos.sort(key=lambda r: (-r["stargazers_count"], r["name"].lower()))
    linhas = [
        "# Metadados dos repositórios",
        "",
        "Gerado por `scripts/sync_metadados.py`. Repos com pendência aparecem primeiro na fila de arrumação.",
        "",
        "| repo | ⭐ | tópicos | pendências |",
        "|---|---:|---:|---|",
    ]
    for r in sorted(publicos, key=lambda r: -len(pendencias(r))):
        falta = pendencias(r)
        linhas.append(
            f"| [{r['name']}]({r['html_url']}) | {r['stargazers_count']} | "
            f"{len(r.get('topics') or [])} | {', '.join(falta) if falta else '✅ ok'} |"
        )
    linhas.append("")
    RELATORIO.write_text("\n".join(linhas), encoding="utf-8")
    print(f"{RELATORIO.name} atualizado ({len(publicos)} repos públicos).")


def main():
    simular = "--simular" in sys.argv
    token = os.environ.get("METADADOS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina METADADOS_TOKEN.", file=sys.stderr)
        sys.exit(1)

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    padrao = config.get("padrao", {})
    alvos = config.get("repos", {})

    repos = listar_repos(token)
    por_nome = {r["name"]: r for r in repos}

    for nome, alvo in alvos.items():
        repo = por_nome.get(nome)
        if not repo:
            print(f"aviso: {nome} não existe na conta, pulei.", file=sys.stderr)
            continue
        mudancas = aplicar(repo, alvo, padrao, token, simular)
        prefixo = "[simulação] " if simular else ""
        print(f"{prefixo}{nome}: {', '.join(mudancas) if mudancas else 'nada a mudar'}")

    # relê depois das mudanças pra o relatório refletir o estado atual
    escrever_relatorio(repos if simular else listar_repos(token))


if __name__ == "__main__":
    main()
