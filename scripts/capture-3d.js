// scripts/capture-3d.js
//
// Abre paulapeclat.com.br em Chromium headless, espera a cena Three.js
// carregar e estabilizar, e captura uma sequência de frames do <canvas id="canvas3d">.
// Os frames viram um WebP animado num passo separado (ver workflow).

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const URL = 'https://paulapeclat.com.br';
const OUT_DIR = path.join(__dirname, '..', 'tmp-frames');
const FRAME_COUNT = 20;       // ~3s de loop a 150ms por frame
const FRAME_INTERVAL_MS = 150;
const SETTLE_MS = 3000;       // tempo extra pra cena estabilizar após o loader sumir
const NAV_TIMEOUT_MS = 60000;
const LOADER_TIMEOUT_MS = 15000;

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
    await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 1 });

    page.on('console', (msg) => console.log('[página]', msg.text()));
    page.on('pageerror', (err) => console.warn('[erro na página]', err.message));

    console.log(`Navegando até ${URL} ...`);
    await page.goto(URL, { waitUntil: 'networkidle0', timeout: NAV_TIMEOUT_MS });

    console.log('Aguardando o loader sumir...');
    try {
      await page.waitForSelector('#loader.hidden', { timeout: LOADER_TIMEOUT_MS });
    } catch (e) {
      console.warn('Loader não sumiu no tempo esperado — seguindo mesmo assim.');
    }

    console.log(`Aguardando ${SETTLE_MS}ms extras pra cena 3D estabilizar...`);
    await new Promise((r) => setTimeout(r, SETTLE_MS));

    const canvas = await page.$('#canvas3d');
    if (!canvas) {
      throw new Error('Elemento #canvas3d não encontrado na página. A estrutura do site pode ter mudado.');
    }

    console.log(`Capturando ${FRAME_COUNT} frames...`);
    for (let i = 0; i < FRAME_COUNT; i++) {
      const framePath = path.join(OUT_DIR, `frame-${String(i).padStart(3, '0')}.png`);
      await canvas.screenshot({ path: framePath });
      await new Promise((r) => setTimeout(r, FRAME_INTERVAL_MS));
    }

    console.log('Captura concluída com sucesso.');
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('Falha na captura da cena 3D:', err);
  process.exit(1);
});
