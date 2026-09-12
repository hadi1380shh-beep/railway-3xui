// تست بدون مرورگر: کد بازی را همراه سه‌جیاس باندل می‌کند و در نود با استاب‌های DOM/WebGL اجرا می‌کند
// خروجی: اگر همه‌چیز درست باشد «HARNESS OK» چاپ می‌شود و exit-code صفر است.
import { build } from 'esbuild';
import { writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');

// ---------- DOM stubs ----------
function make2dCtx() {
  const store = {};
  const grad = () => ({ addColorStop() {} });
  return new Proxy({}, {
    get(t, p) {
      if (p === 'createLinearGradient' || p === 'createRadialGradient') return grad;
      if (p === 'canvas') return null;
      if (p in t) return t[p];
      return () => {};
    },
    set(t, p, v) { t[p] = v; return true; },
  });
}

function makeEl(tag) {
  const listeners = {};
  const el = {
    tagName: (tag || 'div').toUpperCase(),
    style: {},
    dataset: {},
    children: [],
    textContent: '',
    innerHTML: '',
    hidden: false,
    _listeners: listeners,
    _w: 300, _h: 150,
    classList: {
      _s: new Set(),
      add(...c) { c.forEach(x => el.classList._s.add(x)); },
      remove(...c) { c.forEach(x => el.classList._s.delete(x)); },
      contains(c) { return el.classList._s.has(c); },
      toggle(c, force) {
        if (force === undefined) { el.classList._s.has(c) ? el.classList._s.delete(c) : el.classList._s.add(c); }
        else if (force) el.classList._s.add(c);
        else el.classList._s.delete(c);
      },
    },
    addEventListener(t, cb) { (listeners[t] = listeners[t] || []).push(cb); },
    removeEventListener(t, cb) { const a = listeners[t]; if (a) { const i = a.indexOf(cb); if (i >= 0) a.splice(i, 1); } },
    remove() {},
    appendChild(c) { el.children.push(c); return c; },
    closest() { return null; },
    getContext(kind) { return kind === '2d' ? make2dCtx() : null; },
    get width() { return el._w; }, set width(v) { el._w = v; },
    get height() { return el._h; }, set height(v) { el._h = v; },
  };
  return el;
}

const byId = new Map();
function getEl(id) { if (!byId.has(id)) byId.set(id, makeEl('div')); return byId.get(id); }

globalThis.window = globalThis;
globalThis.self = globalThis;
globalThis.innerWidth = 800;
globalThis.innerHeight = 600;
globalThis.devicePixelRatio = 1;
globalThis.addEventListener = () => {};
globalThis.removeEventListener = () => {};
globalThis.AudioContext = undefined;
globalThis.webkitAudioContext = undefined;
globalThis.DeviceOrientationEvent = undefined;
globalThis.location = { search: '?debug' };
globalThis.rafQueue = [];
globalThis.requestAnimationFrame = cb => { globalThis.rafQueue.push(cb); return globalThis.rafQueue.length; };
globalThis.cancelAnimationFrame = () => {};

globalThis.document = {
  getElementById: id => getEl(id),
  createElement: tag => makeEl(tag),
  querySelector: () => makeEl('div'),
  querySelectorAll: () => [],
  addEventListener() {},
  removeEventListener() {},
  fonts: { load: async () => undefined, ready: Promise.resolve() },
  hidden: false,
  documentElement: { style: {} },
  body: makeEl('body'),
  createTextNode: () => ({}),
};

// ---------- bundle ----------
const result = await build({
  stdin: { contents: "import './game.js';", sourcefile: 'test-entry.js', loader: 'js', resolveDir: join(root, 'src') },
  bundle: true,
  minify: false,
  format: 'iife',
  platform: 'browser',
  target: ['es2019'],
  alias: {
    three: join(here, 'three-shim.js'),
    'three/addons': join(root, 'node_modules', 'three', 'examples', 'jsm'),
  },
  write: false,
});

const outPath = '/tmp/game-test.cjs';
writeFileSync(outPath, result.outputFiles[0].text);

const require = createRequire(import.meta.url);

function pumpFrames(n) {
  for (let i = 0; i < n; i++) {
    const q = globalThis.rafQueue.splice(0);
    if (!q.length) break;
    for (const cb of q) cb(performance.now() + i * 16.7);
  }
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

try {
  require(outPath);                       // اجرای boot()
  await sleep(50);                        // اجازهٔ تکمیل async boot
  if (getEl('loader').innerHTML) throw new Error('boot failed: ' + getEl('loader').innerHTML);

  pumpFrames(10);                         // چند فریم در حالت منو

  // شبیه‌سازی کلیک روی دکمهٔ شروع
  const startBtn = getEl('startBtn');
  (startBtn._listeners.click || []).forEach(cb => cb());

  // شبیه‌سازی ورودی: گاز + فرمان چپ
  const gas = getEl('btnGas');
  (gas._listeners.pointerdown || []).forEach(cb => cb({ preventDefault() {} }));
  const left = getEl('btnLeft');
  (left._listeners.pointerdown || []).forEach(cb => cb({ preventDefault() {} }));

  // گیم‌پلی با تشخیص فریم‌به‌فریم NaN
  let nanFrame = -1;
  for (let i = 0; i < 360; i++) {
    const q = globalThis.rafQueue.splice(0);
    for (const cb of q) cb(performance.now() + i * 16.7);
    if (i === 240) (left._listeners.pointerup || []).forEach(cb => cb({ preventDefault() {} }));
    const cp = globalThis.__gameDebug.camPos();
    if ([cp.x, cp.y, cp.z].some(v => !Number.isFinite(v))) { nanFrame = i; break; }
  }
  if (nanFrame >= 0) throw new Error('NaN in camera at frame ' + nanFrame);

  const scoreTxt = getEl('scoreVal').textContent;
  const speedTxt = getEl('speedVal').textContent;
  const livesTxt = getEl('lives').textContent;
  console.log('score:', scoreTxt, '| speed:', speedTxt, '| lives:', livesTxt);

  // بررسی NaN در تمام اشیای صحنه (نشانهٔ ریاضیات خراب)
  const dbg = globalThis.__gameDebug;
  if (!dbg) throw new Error('debug hook not found');
  let bad = [];
  const isBad = v => !Number.isFinite(v);
  dbg.scene.traverse(o => {
    if (o.position && (isBad(o.position.x) || isBad(o.position.y) || isBad(o.position.z))) bad.push(o.type || o.name || 'obj');
    if (o.rotation && (isBad(o.rotation.x) || isBad(o.rotation.y) || isBad(o.rotation.z))) bad.push(o.type || o.name || 'obj-rot');
  });
  const p = dbg.player().group.position;
  if (isBad(p.x) || isBad(p.y) || isBad(p.z)) bad.push('player');
  console.log('player heading:', dbg.player().heading, '| speed:', dbg.player().speed);
  console.log('camPos:', dbg.camPos().x, dbg.camPos().y, dbg.camPos().z);
  const cam = dbg.camera.position;
  if (isBad(cam.x) || isBad(cam.y) || isBad(cam.z)) bad.push('camera');
  if (bad.length) throw new Error('NaN detected in: ' + [...new Set(bad)].join(', '));

  console.log('scene objects:', dbg.scene.children.length, '| traffic:', dbg.traffic().length, '| coins:', dbg.coins().length);
  console.log('HARNESS OK');
  process.exit(0);
} catch (err) {
  console.error('HARNESS FAIL:', err && err.stack ? err.stack : err);
  process.exit(1);
}
