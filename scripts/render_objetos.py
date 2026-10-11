#!/usr/bin/env python3
"""
Renderiza os modelos Smooth Voxels de data/modelos/*.svox em PNG com fundo
transparente (assets/objetos/<nome>.png), usando three.js + Smooth Voxels
num Chromium headless. A trilha embute esses PNGs no SVG.

Pra pôr um objeto novo, é só salvar o .svox em data/modelos/ e comitar.

Uso local: python scripts/render_objetos.py
(precisa de: pip install playwright && playwright install chromium)
"""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MODELOS = ROOT / "data" / "modelos"
SAIDA = ROOT / "assets" / "objetos"
TAMANHO = 512  # px do PNG final (quadrado)

THREE = "https://cdn.jsdelivr.net/npm/three@0.164.0/"
SVOX = "https://cdn.jsdelivr.net/gh/SamuelVanEgmond/Smooth-Voxels@v2.4.0/dist/smoothvoxels.three.min.js"

PAGINA = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:transparent}canvas{display:block}</style>
<script type="importmap">{"imports":{"three":"%(three)sbuild/three.module.min.js","three/addons/":"%(three)sexamples/jsm/"}}</script>
<script src="%(svox)s"></script>
</head><body>
<script type="module">
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
window.THREE = THREE;

const N = %(n)d;
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setSize(N, N);
renderer.setClearColor(0x000000, 0);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
// céu de dia: luz azulada de cima, quente de baixo, e o sol pela esquerda
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
scene.add(new THREE.HemisphereLight(0xcfe8ff, 0xffe2b8, 1.4));
const sol = new THREE.DirectionalLight(0xffffff, 2.6);
sol.position.set(-3, 5, 4);
scene.add(sol);

const mesh = await SmoothVoxels.createMesh(window.MODELO, 'objeto', false);
scene.add(mesh);

// enquadra o objeto inteiro com uma folguinha
const caixa = new THREE.Box3().setFromObject(mesh);
const centro = caixa.getCenter(new THREE.Vector3());
const raio = caixa.getBoundingSphere(new THREE.Sphere()).radius;
const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 100);
const dist = raio / Math.sin(THREE.MathUtils.degToRad(15)) * 1.05;
camera.position.copy(centro).add(new THREE.Vector3(0.35, 0.25, 1).normalize().multiplyScalar(dist));
camera.lookAt(centro);

renderer.render(scene, camera);
window.PRONTO = true;
</script></body></html>"""


def main():
    modelos = sorted(MODELOS.glob("*.svox"))
    if not modelos:
        print("nenhum modelo em data/modelos/")
        return
    SAIDA.mkdir(parents=True, exist_ok=True)
    pagina = PAGINA % {"three": THREE, "svox": SVOX, "n": TAMANHO}

    # pra rodar sem internet: OBJETOS_LIBS=<pasta com three/ e smoothvoxels.three.js>
    libs = os.environ.get("OBJETOS_LIBS")

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for arquivo in modelos:
            aba = navegador.new_page(viewport={"width": TAMANHO, "height": TAMANHO})
            aba.on("pageerror", lambda e: print(f"erro na página: {e}", file=sys.stderr))
            if libs:
                base = Path(libs)
                aba.route(THREE + "**", lambda r: r.fulfill(path=str(base / "three" / r.request.url[len(THREE):])))
                aba.route(SVOX, lambda r: r.fulfill(path=str(base / "smoothvoxels.three.js")))
            aba.route("https://objetos.local/", lambda r: r.fulfill(body=pagina, content_type="text/html"))
            aba.add_init_script(f"window.MODELO = {json.dumps(arquivo.read_text(encoding='utf-8'))};")
            aba.goto("https://objetos.local/")
            aba.wait_for_function("window.PRONTO === true", timeout=60000)
            destino = SAIDA / f"{arquivo.stem}.png"
            aba.locator("canvas").screenshot(path=str(destino), omit_background=True)
            print(f"{arquivo.name} → {destino.relative_to(ROOT)}")
            aba.close()
        navegador.close()


if __name__ == "__main__":
    main()
