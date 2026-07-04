// scripts/render-3d-hero.js
//
// Renderiza uma cena Three.js surreal (paleta paulapeclat.com.br) em Chromium
// headless e captura frames determinísticos com loop perfeito — todas as
// rotações completam múltiplos inteiros de 2π ao longo do ciclo.
// Os frames viram um WebP animado num passo separado (ver workflow).

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUT_DIR = path.join(__dirname, '..', 'tmp-frames-hero');
const WIDTH = 900;
const HEIGHT = 300;
const FRAME_COUNT = 72; // a 12 fps = loop de 6s

const PAGE_HTML = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>html,body{margin:0;background:#000}</style></head>
<body>
<canvas id="cena" width="${WIDTH}" height="${HEIGHT}"></canvas>
<script type="module">
import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

const TAU = Math.PI * 2;
const canvas = document.getElementById('cena');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(${WIDTH}, ${HEIGHT});
renderer.setClearColor(0x000000);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x000000, 6, 12);

const camera = new THREE.PerspectiveCamera(45, ${WIDTH} / ${HEIGHT}, 0.1, 50);
camera.position.set(0, 0.4, 5.2);
camera.lookAt(0, 0, 0);

scene.add(new THREE.AmbientLight(0xffffff, 0.25));
const luzCyan = new THREE.PointLight(0x22c3d9, 60);
luzCyan.position.set(2.5, 2, 3);
scene.add(luzCyan);
const luzPink = new THREE.PointLight(0xf23d91, 50);
luzPink.position.set(-3, -1.5, 2.5);
scene.add(luzPink);

// núcleo: icosaedro com wireframe ciano
const nucleo = new THREE.Group();
const ico = new THREE.Mesh(
  new THREE.IcosahedronGeometry(1.05, 0),
  new THREE.MeshStandardMaterial({ color: 0x0a2a30, flatShading: true, emissive: 0x0b3a44, roughness: 0.4 })
);
nucleo.add(ico);
const arestas = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.06, 0)),
  new THREE.LineBasicMaterial({ color: 0x22c3d9 })
);
nucleo.add(arestas);
scene.add(nucleo);

// anel amarelo inclinado + lua orbitando
const anelGrupo = new THREE.Group();
anelGrupo.rotation.x = 1.25;
anelGrupo.rotation.z = -0.25;
const anel = new THREE.Mesh(
  new THREE.TorusGeometry(2.05, 0.035, 8, 96),
  new THREE.MeshBasicMaterial({ color: 0xecbe40, transparent: true, opacity: 0.85 })
);
anelGrupo.add(anel);
const lua = new THREE.Mesh(
  new THREE.SphereGeometry(0.11, 12, 12),
  new THREE.MeshBasicMaterial({ color: 0xf2a2c0 })
);
anelGrupo.add(lua);
scene.add(anelGrupo);

// ilhas flutuantes low-poly (cones invertidos)
function ilha(cor, x, z, escala) {
  const m = new THREE.Mesh(
    new THREE.ConeGeometry(0.5 * escala, 0.9 * escala, 5),
    new THREE.MeshStandardMaterial({ color: cor, flatShading: true, roughness: 0.6 })
  );
  m.rotation.x = Math.PI;
  m.position.set(x, 0, z);
  scene.add(m);
  return m;
}
const ilha1 = ilha(0xf23d91, -3.1, -1.0, 1.0);
const ilha2 = ilha(0x22c3d9, 3.1, -0.8, 0.8);

// campo de estrelas determinístico (LCG)
let seed = 20260703;
const rand = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
const posicoes = new Float32Array(220 * 3);
for (let i = 0; i < 220; i++) {
  posicoes[i * 3] = (rand() - 0.5) * 14;
  posicoes[i * 3 + 1] = (rand() - 0.5) * 6;
  posicoes[i * 3 + 2] = -2 - rand() * 6;
}
const estrelasGeo = new THREE.BufferGeometry();
estrelasGeo.setAttribute('position', new THREE.BufferAttribute(posicoes, 3));
scene.add(new THREE.Points(estrelasGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.03, sizeAttenuation: true })));

// t em [0,1) — todas as frequências são inteiras para o loop fechar
window.renderFrame = (frame, total) => {
  const t = frame / total;
  nucleo.rotation.y = TAU * t;
  nucleo.rotation.x = 0.35 + Math.sin(TAU * t) * 0.12;
  const ang = TAU * 2 * t;
  lua.position.set(Math.cos(ang) * 2.05, Math.sin(ang) * 2.05, 0);
  ilha1.position.y = 0.15 + Math.sin(TAU * t) * 0.18;
  ilha1.rotation.y = TAU * t;
  ilha2.position.y = -0.1 + Math.sin(TAU * t + Math.PI) * 0.15;
  ilha2.rotation.y = -TAU * t;
  renderer.render(scene, camera);
};

window.renderFrame(0, ${FRAME_COUNT});
window.sceneReady = true;
</script>
</body>
</html>`;

async function main() {
  fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--use-gl=angle',
      '--use-angle=swiftshader',
      '--enable-webgl',
      '--ignore-gpu-blocklist',
      '--disable-gpu-sandbox',
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 1 });
    page.on('console', (msg) => console.log('[página]', msg.text()));
    page.on('pageerror', (err) => console.warn('[erro na página]', err.message));

    console.log('Carregando cena Three.js...');
    await page.setContent(PAGE_HTML, { waitUntil: 'networkidle0', timeout: 60000 });
    await page.waitForFunction('window.sceneReady === true', { timeout: 30000 });

    const canvas = await page.$('#cena');
    console.log(`Capturando ${FRAME_COUNT} frames determinísticos...`);
    for (let i = 0; i < FRAME_COUNT; i++) {
      await page.evaluate((f, total) => window.renderFrame(f, total), i, FRAME_COUNT);
      await canvas.screenshot({ path: path.join(OUT_DIR, `frame-${String(i).padStart(3, '0')}.png`) });
    }
    console.log('Captura concluída com sucesso.');
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('Falha no render da cena 3D:', err);
  process.exit(1);
});
