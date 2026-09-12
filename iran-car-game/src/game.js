
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

/* ============================================================
   ماشین بازی ایرانی — Iranian Car Game
   ============================================================ */

// ---------------- Config ----------------
const CITY = { blocks: 5, roadW: 10, blockW: 26 };
const S = CITY.blockW + CITY.roadW;          // spacing between road lines
const M = CITY.blocks + 1;                   // number of road lines per axis
const HALF = (M - 1) * S / 2;                // city half-extent

const roadX = [], roadZ = [];
for (let i = 0; i < M; i++) { roadX.push((i - (M - 1) / 2) * S); roadZ.push((i - (M - 1) / 2) * S); }

const CAR_DEFS = {
  peykan: {
    name: 'پیکان', paint: 0xe8e2d0, paint2: 0xbfa86a,
    len: 4.05, wid: 1.62, bodyH: 0.62, cabinH: 0.50, cabinD: 1.85,
    maxSpeed: 40, accel: 13, turn: 2.35
  },
  pride: {
    name: 'پراید', paint: 0xf4f4f4, paint2: 0xd84b4b,
    len: 3.75, wid: 1.56, bodyH: 0.66, cabinH: 0.52, cabinD: 1.95,
    maxSpeed: 42, accel: 14, turn: 2.55
  },
  samand: {
    name: 'سمند', paint: 0x2b3a4d, paint2: 0x8f9dad,
    len: 4.35, wid: 1.70, bodyH: 0.60, cabinH: 0.50, cabinD: 1.90,
    maxSpeed: 46, accel: 14.5, turn: 2.3
  }
};

const BUILDING_COLORS = [0xd8c9a3, 0xcbb9a0, 0xe3d5b8, 0xb9a98a, 0xcfc0ae, 0xe8dcc3, 0xa8b8c8, 0xd9a97c, 0xc47e5f, 0x9fb0bd];
const TRAFFIC_COLORS = [0xd8d8d8, 0x9aa0a6, 0x6b3f2a, 0x27486b, 0x8a2f2f, 0x3f5c3a, 0xd9b23b, 0xffffff];

// ---------------- Globals ----------------
let renderer, scene, camera;
const clock = new THREE.Clock();
let state = 'menu';              // menu | playing | paused | gameover
let selectedCar = 'peykan';
let score = 0, coins = 0, lives = 3, distM = 0, invuln = 0, shake = 0;
let player = null;
let traffic = [];
let coinSprites = [];
let colliders = [];
let particles = [];
let sunDir = new THREE.Vector3(0.55, 0.85, 0.35).normalize();
let tiltEnabled = false;

const el = id => document.getElementById(id);
const hud = { score: el('scoreVal'), coin: el('coinVal'), speed: el('speedVal'), lives: el('lives') };

// ---------------- Audio ----------------
class AudioEngine {
  constructor() {
    this.ctx = null; this.muted = false; this.ready = false;
    this.engineGain = null; this.master = null; this.filter = null;
    this.osc1 = null; this.osc2 = null; this.noiseBuf = null;
  }
  ensure() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      this.ctx = new AC();
      this.master = this.ctx.createGain();
      this.master.gain.value = this.muted ? 0 : 0.9;
      this.master.connect(this.ctx.destination);

      this.filter = this.ctx.createBiquadFilter();
      this.filter.type = 'lowpass'; this.filter.frequency.value = 900;

      this.osc1 = this.ctx.createOscillator(); this.osc1.type = 'sawtooth';
      this.osc2 = this.ctx.createOscillator(); this.osc2.type = 'square';
      this.osc2.detune.value = 8;
      this.engineGain = this.ctx.createGain(); this.engineGain.gain.value = 0;
      this.osc1.connect(this.filter); this.osc2.connect(this.filter);
      this.filter.connect(this.engineGain); this.engineGain.connect(this.master);
      this.osc1.start(); this.osc2.start();

      const len = this.ctx.sampleRate * 0.6;
      this.noiseBuf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
      const d = this.noiseBuf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 1.5);
      this.ready = true;
    }
    if (this.ctx.state === 'suspended') this.ctx.resume();
  }
  engine(speed, throttle) {
    if (!this.ready) return;
    const f = 55 + Math.abs(speed) * 5.2 + throttle * 12;
    this.osc1.frequency.setTargetAtTime(f, this.ctx.currentTime, 0.05);
    this.osc2.frequency.setTargetAtTime(f * 0.5, this.ctx.currentTime, 0.05);
    const g = 0.045 + throttle * 0.12 + Math.min(Math.abs(speed) / 45, 1) * 0.06;
    this.engineGain.gain.setTargetAtTime(g, this.ctx.currentTime, 0.08);
  }
  coin() {
    if (!this.ready) return;
    const t = this.ctx.currentTime;
    [[880, 0], [1320, 0.09]].forEach(([f, off]) => {
      const o = this.ctx.createOscillator(); const g = this.ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, t + off);
      g.gain.exponentialRampToValueAtTime(0.25, t + off + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + off + 0.16);
      o.connect(g); g.connect(this.master);
      o.start(t + off); o.stop(t + off + 0.2);
    });
  }
  crash() {
    if (!this.ready) return;
    const t = this.ctx.currentTime;
    const src = this.ctx.createBufferSource(); src.buffer = this.noiseBuf;
    const lp = this.ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 650;
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.7, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.55);
    src.connect(lp); lp.connect(g); g.connect(this.master);
    src.start(t); src.stop(t + 0.6);
  }
  toggleMute() {
    this.muted = !this.muted;
    if (this.master) this.master.gain.value = this.muted ? 0 : 0.9;
    return this.muted;
  }
}
const audio = new AudioEngine();

// ---------------- Canvas texture helpers ----------------
function canvasTex(w, h, draw, repeat = null) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
  return t;
}

function asphaltTexture() {
  return canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#2e2e30'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 2600; i++) {
      const v = 34 + Math.random() * 26 | 0;
      g.fillStyle = `rgb(${v},${v},${v + 2})`;
      g.fillRect(Math.random() * w, Math.random() * h, 1.6, 1.6);
    }
  }, [26, 26]);
}

function windowTexture() {
  return canvasTex(128, 128, (g, w, h) => {
    g.fillStyle = '#3d3b36'; g.fillRect(0, 0, w, h);
    const cols = 4, rows = 4, pad = 8, gap = 6;
    const cw = (w - pad * 2 - gap * (cols - 1)) / cols;
    const ch = (h - pad * 2 - gap * (rows - 1)) / rows;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      const x = pad + i * (cw + gap), y = pad + j * (ch + gap);
      const lit = Math.random() < 0.28;
      g.fillStyle = lit ? '#ffd98a' : (Math.random() < 0.5 ? '#2f343c' : '#454d58');
      g.fillRect(x, y, cw, ch);
      if (lit) { g.fillStyle = 'rgba(255,240,200,0.25)'; g.fillRect(x, y, cw, ch); }
    }
  }, [3, 5]);
}

function signTexture(text, bg) {
  return canvasTex(512, 160, (g, w, h) => {
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(255,255,255,0.85)'; g.lineWidth = 8; g.strokeRect(6, 6, w - 12, h - 12);
    g.fillStyle = '#fff'; g.font = '700 72px "Vazirmatn", Tahoma, sans-serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(text, w / 2, h / 2 + 4);
  });
}

function coinTexture() {
  return canvasTex(128, 128, (g, w, h) => {
    const cx = w / 2, cy = h / 2, r = 52;
    const grd = g.createRadialGradient(cx - 14, cy - 14, 8, cx, cy, r);
    grd.addColorStop(0, '#fff3b0'); grd.addColorStop(0.55, '#ffd23f'); grd.addColorStop(1, '#c98a00');
    g.fillStyle = grd; g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2); g.fill();
    g.strokeStyle = '#a96e00'; g.lineWidth = 6; g.stroke();
    g.strokeStyle = '#fff2b8'; g.lineWidth = 3; g.beginPath(); g.arc(cx, cy, r - 12, 0, Math.PI * 2); g.stroke();
    g.fillStyle = '#8a5a00'; g.font = '900 64px "Vazirmatn", Tahoma, sans-serif';
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('★', cx, cy + 4);
  });
}

function skyTexture() {
  return canvasTex(4, 512, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, 0, h);
    grd.addColorStop(0.0, '#2a6fd6');
    grd.addColorStop(0.45, '#6ea8ea');
    grd.addColorStop(0.72, '#b7d9f4');
    grd.addColorStop(1.0, '#dcecf9');
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
  });
}

function sunTexture() {
  return canvasTex(128, 128, (g, w, h) => {
    const grd = g.createRadialGradient(w / 2, h / 2, 6, w / 2, h / 2, 60);
    grd.addColorStop(0, 'rgba(255,250,230,1)');
    grd.addColorStop(0.35, 'rgba(255,240,190,0.85)');
    grd.addColorStop(1, 'rgba(255,235,180,0)');
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
  });
}

// ---------------- Three.js setup ----------------
function setupRenderer() {
  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  el('game').appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0xcfe2f5, 55, 300);

  camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 800);
  camera.position.set(0, 30, 40);
}

function setupLights() {
  const hemi = new THREE.HemisphereLight(0xbcd9ff, 0x8a7a5c, 0.95);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff2dd, 2.6);
  sun.position.copy(sunDir).multiplyScalar(90);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -60; sun.shadow.camera.right = 60;
  sun.shadow.camera.top = 60; sun.shadow.camera.bottom = -60;
  sun.shadow.camera.near = 10; sun.shadow.camera.far = 260;
  sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
  sun.shadow.camera.updateProjectionMatrix();
  scene.add(sun); scene.add(sun.target);
  scene.userData.sun = sun;
}

function setupSky() {
  const sky = new THREE.Mesh(
    new THREE.SphereGeometry(400, 24, 16),
    new THREE.MeshBasicMaterial({ map: skyTexture(), side: THREE.BackSide, fog: false, depthWrite: false })
  );
  sky.renderOrder = -10;
  scene.add(sky);
  scene.userData.sky = sky;

  const sunSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: sunTexture(), fog: false, depthWrite: false, transparent: true }));
  sunSprite.position.copy(sunDir).multiplyScalar(330);
  sunSprite.scale.set(140, 140, 1);
  scene.add(sunSprite);
  scene.userData.sunSprite = sunSprite;

  // distant Alborz-style mountains
  const mtnMat = new THREE.MeshStandardMaterial({ color: 0x7f93ad, roughness: 1, flatShading: true });
  const mtnGroup = new THREE.Group();
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * Math.PI * 2 + 0.3;
    const r = 190 + Math.random() * 70;
    const h = 55 + Math.random() * 80;
    const w = 60 + Math.random() * 70;
    const m = new THREE.Mesh(new THREE.ConeGeometry(w, h, 5), mtnMat);
    m.position.set(Math.cos(a) * r, h / 2 - 8, Math.sin(a) * r);
    m.rotation.y = Math.random() * Math.PI;
    mtnGroup.add(m);
  }
  scene.add(mtnGroup);
}

function setupGround() {
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(HALF * 2 + 160, HALF * 2 + 160),
    new THREE.MeshStandardMaterial({ map: asphaltTexture(), roughness: 0.95, metalness: 0 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);
}

// ---------------- City construction ----------------
function buildCity() {
  const winTex = windowTexture();

  // sidewalk platforms (blocks)
  const sidewalkGeo = new THREE.BoxGeometry(CITY.blockW, 0.22, CITY.blockW);
  const sidewalkMat = new THREE.MeshStandardMaterial({ color: 0xb9b4aa, roughness: 0.9 });
  const sidewalks = new THREE.InstancedMesh(sidewalkGeo, sidewalkMat, CITY.blocks * CITY.blocks);
  sidewalks.receiveShadow = true;

  // buildings
  const bGeo = new THREE.BoxGeometry(1, 1, 1);
  const bMat = new THREE.MeshStandardMaterial({ map: winTex, roughness: 0.85, metalness: 0.05 });
  const buildings = new THREE.InstancedMesh(bGeo, bMat, CITY.blocks * CITY.blocks * 4);
  buildings.castShadow = true; buildings.receiveShadow = true;

  const dummy = new THREE.Object3D();
  const color = new THREE.Color();
  let si = 0, bi = 0;

  const parkI = Math.floor(CITY.blocks / 2), parkJ = Math.floor(CITY.blocks / 2);
  const signTexts = ['سوپرمارکت', 'نانوایی', 'کتاب‌فروشی', 'رستوران', 'داروخانه', 'پوشاک', 'قصابی', 'آجیل'];
  const signBgs = ['#c0392b', '#b9770e', '#1f618d', '#6c3483', '#148f77', '#ca6f1e', '#7b241c', '#1a5276'];

  for (let i = 0; i < CITY.blocks; i++) {
    for (let j = 0; j < CITY.blocks; j++) {
      const cx = (i - (CITY.blocks - 1) / 2) * S;
      const cz = (j - (CITY.blocks - 1) / 2) * S;

      dummy.position.set(cx, 0.11, cz);
      dummy.scale.setScalar(1);
      dummy.updateMatrix();
      sidewalks.setMatrixAt(si++, dummy.matrix);

      if (i === parkI && j === parkJ) {
        buildAzadi(cx, cz);
        buildFountain(cx, cz);
        continue;
      }

      // buildings inside the block
      const n = 3 + ((i * 7 + j * 13) % 2);
      for (let k = 0; k < n; k++) {
        const bw = 7 + Math.random() * 9;
        const bd = 7 + Math.random() * 9;
        const bh = 6 + Math.random() * 16;
        const ox = (Math.random() - 0.5) * (CITY.blockW - bw - 2);
        const oz = (Math.random() - 0.5) * (CITY.blockW - bd - 2);
        dummy.position.set(cx + ox, 0.22 + bh / 2, cz + oz);
        dummy.scale.set(bw, bh, bd);
        dummy.rotation.y = 0;
        dummy.updateMatrix();
        buildings.setMatrixAt(bi, dummy.matrix);
        color.set(BUILDING_COLORS[(i + j + k) % BUILDING_COLORS.length]);
        buildings.setColorAt(bi, color);
        bi++;
        colliders.push({ minX: cx + ox - bw / 2, maxX: cx + ox + bw / 2, minZ: cz + oz - bd / 2, maxZ: cz + oz + bd / 2 });

        // a shop sign on the street-facing side
        if (k === 0 && (i + j) % 3 !== 0) {
          const sign = new THREE.Mesh(
            new THREE.PlaneGeometry(5, 1.4),
            new THREE.MeshBasicMaterial({ map: signTexture(signTexts[(i + j) % signTexts.length], signBgs[(i + j) % signBgs.length]) })
          );
          sign.position.set(cx + ox, 3.4, cz + oz + bd / 2 + 0.05);
          sign.rotation.y = 0;
          scene.add(sign);
        }
      }
    }
  }
  buildings.count = bi;
  buildings.instanceMatrix.needsUpdate = true;
  buildings.instanceColor.needsUpdate = true;
  scene.add(sidewalks, buildings);

  buildRoadMarkings();
  buildTrees();
  buildLamps();
}

function buildRoadMarkings() {
  const dashGeo = new THREE.BoxGeometry(0.16, 0.02, 3.2);
  const dashMat = new THREE.MeshStandardMaterial({ color: 0xf5f2e8, roughness: 0.7 });
  const crossGeo = new THREE.BoxGeometry(0.5, 0.02, CITY.roadW - 2.4);
  const crossMat = new THREE.MeshStandardMaterial({ color: 0xe8e4d8, roughness: 0.7 });

  const dashItems = [];
  const crossItems = [];
  const step = 9;

  // dashed center lines: horizontal roads run along z, vertical roads run along x
  for (let i = 0; i < M; i++) {
    for (let j = 0; j < M - 1; j++) {
      const z0 = roadZ[j] + CITY.roadW / 2 + 2.5;
      const z1 = roadZ[j + 1] - CITY.roadW / 2 - 2.5;
      for (let z = z0; z < z1; z += step) dashItems.push({ x: roadX[i], z: Math.min(z, z1 - 1.6), ry: 0 });
      const x0 = roadX[j] + CITY.roadW / 2 + 2.5;
      const x1 = roadX[j + 1] - CITY.roadW / 2 - 2.5;
      for (let x = x0; x < x1; x += step) dashItems.push({ x: Math.min(x, x1 - 1.6), z: roadZ[i], ry: Math.PI / 2 });
    }
  }
  // crosswalks at every intersection
  const off = CITY.roadW / 2 - 1.4;
  for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) {
    crossItems.push({ x: roadX[i] + off, z: roadZ[j], ry: 0 });
    crossItems.push({ x: roadX[i] - off, z: roadZ[j], ry: 0 });
    crossItems.push({ x: roadX[i], z: roadZ[j] + off, ry: Math.PI / 2 });
    crossItems.push({ x: roadX[i], z: roadZ[j] - off, ry: Math.PI / 2 });
  }

  addInstanced(dashGeo, dashMat, dashItems);
  addInstanced(crossGeo, crossMat, crossItems);
}

function addInstanced(geo, mat, items) {
  const mesh = new THREE.InstancedMesh(geo, mat, items.length);
  const dummy = new THREE.Object3D();
  items.forEach((it, i) => {
    dummy.position.set(it.x, 0.02, it.z);
    dummy.rotation.set(0, it.ry || 0, 0);
    dummy.scale.setScalar(1);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
  });
  mesh.receiveShadow = true;
  scene.add(mesh);
  return mesh;
}

function buildTrees() {
  const trunkGeo = new THREE.CylinderGeometry(0.14, 0.2, 1.6, 6);
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x6b4a2b, roughness: 0.9 });
  const leafGeo = new THREE.SphereGeometry(1.25, 8, 7);
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x3e7a33, roughness: 0.8 });

  const positions = [];
  // trees along block edges
  for (let i = 0; i < CITY.blocks; i++) for (let j = 0; j < CITY.blocks; j++) {
    const cx = (i - (CITY.blocks - 1) / 2) * S;
    const cz = (j - (CITY.blocks - 1) / 2) * S;
    const e = CITY.blockW / 2 - 1.2;
    const spots = [
      [cx - e, cz - e], [cx + e, cz - e], [cx - e, cz + e], [cx + e, cz + e],
      [cx, cz - e], [cx, cz + e], [cx - e, cz], [cx + e, cz]
    ];
    for (const [x, z] of spots) {
      if (Math.random() < 0.75) positions.push([x, z]);
      if (Math.random() < 0.35) positions.push([x + (Math.random() - .5) * 3, z + (Math.random() - .5) * 3]);
    }
  }

  const trunks = new THREE.InstancedMesh(trunkGeo, trunkMat, positions.length);
  const leaves = new THREE.InstancedMesh(leafGeo, leafMat, positions.length);
  const dummy = new THREE.Object3D();
  const c = new THREE.Color();
  positions.forEach((p, idx) => {
    const h = 0.8 + Math.random() * 0.6;
    dummy.position.set(p[0], h, p[1]);
    dummy.scale.setScalar(1);
    dummy.updateMatrix();
    trunks.setMatrixAt(idx, dummy.matrix);
    dummy.position.set(p[0], h + 1.4, p[1]);
    dummy.scale.set(1, 0.85 + Math.random() * 0.4, 1);
    dummy.updateMatrix();
    leaves.setMatrixAt(idx, dummy.matrix);
    c.setHSL(0.30 + Math.random() * 0.06, 0.45, 0.26 + Math.random() * 0.1);
    leaves.setColorAt(idx, c);
  });
  trunks.castShadow = true; leaves.castShadow = true;
  scene.add(trunks, leaves);
}

function buildLamps() {
  const poleGeo = new THREE.CylinderGeometry(0.08, 0.1, 5.4, 6);
  const poleMat = new THREE.MeshStandardMaterial({ color: 0x3a3f46, roughness: 0.6, metalness: 0.6 });
  const headGeo = new THREE.BoxGeometry(0.7, 0.14, 0.3);
  const headMat = new THREE.MeshStandardMaterial({ color: 0x2c3138, roughness: 0.5, metalness: 0.5 });
  const bulbMat = new THREE.MeshStandardMaterial({ color: 0xfff2c0, emissive: 0xffd980, emissiveIntensity: 0.9 });

  const spots = [];
  for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) {
    if ((i + j) % 2) continue;
    const ox = CITY.roadW / 2 + 0.6, oz = CITY.roadW / 2 + 0.6;
    spots.push([roadX[i] + ox, roadZ[j] + oz]);
    spots.push([roadX[i] - ox, roadZ[j] - oz]);
  }
  const poles = new THREE.InstancedMesh(poleGeo, poleMat, spots.length);
  const heads = new THREE.InstancedMesh(headGeo, headMat, spots.length);
  const bulbs = new THREE.InstancedMesh(new THREE.BoxGeometry(0.5, 0.06, 0.16), bulbMat, spots.length);
  const dummy = new THREE.Object3D();
  spots.forEach((p, idx) => {
    dummy.position.set(p[0], 2.7, p[1]);
    dummy.rotation.set(0, 0, 0); dummy.scale.setScalar(1); dummy.updateMatrix();
    poles.setMatrixAt(idx, dummy.matrix);
    dummy.position.set(p[0] + 0.5, 5.5, p[1]);
    dummy.updateMatrix();
    heads.setMatrixAt(idx, dummy.matrix);
    dummy.position.set(p[0] + 0.55, 5.44, p[1]);
    dummy.updateMatrix();
    bulbs.setMatrixAt(idx, dummy.matrix);
  });
  poles.castShadow = true; heads.castShadow = true;
  scene.add(poles, heads, bulbs);
}

function buildAzadi(cx, cz) {
  const mat = new THREE.MeshStandardMaterial({ color: 0xe8e0cf, roughness: 0.6, metalness: 0.05 });
  const g = new THREE.Group();
  const box = (w, h, d, x, y, z, ry = 0) => {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 2, 0.3), mat);
    m.position.set(x, y, z); m.rotation.y = ry; m.castShadow = true; m.receiveShadow = true;
    g.add(m); return m;
  };
  // platform
  const plat = new THREE.Mesh(new THREE.CylinderGeometry(14, 15, 0.8, 32), new THREE.MeshStandardMaterial({ color: 0xcfc6b0, roughness: 0.85 }));
  plat.position.set(cx, 0.55, cz); plat.receiveShadow = true; plat.castShadow = true;
  scene.add(plat);
  g.position.set(cx, 0.95, cz);
  // central tower
  box(5.5, 20, 4.5, 0, 10, 0);
  box(7, 5, 6, 0, 18, 0);
  // two side wings
  box(3, 14, 4, -6.5, 7.5, 0, -0.28);
  box(3, 14, 4, 6.5, 7.5, 0, 0.28);
  // cross beam
  box(11, 3, 3.6, 0, 12.5, 0);
  // arch opening (darker)
  const arch = new THREE.Mesh(new RoundedBoxGeometry(3.4, 9, 4.6, 2, 0.3), new THREE.MeshStandardMaterial({ color: 0x8d8574, roughness: 0.7 }));
  arch.position.set(0, 5, 0.1);
  g.add(arch);
  scene.add(g);
}

function buildFountain(cx, cz) {
  const water = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 4.5, 0.3, 32), new THREE.MeshStandardMaterial({ color: 0x6fc7e8, roughness: 0.15, metalness: 0.1 }));
  water.position.set(cx - 12, 0.6, cz + 10); water.receiveShadow = true;
  scene.add(water);
  const jet = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 2.2, 8), new THREE.MeshStandardMaterial({ color: 0xbfe9f7, roughness: 0.1 }));
  jet.position.set(cx - 12, 1.7, cz + 10);
  scene.add(jet);
}

// ---------------- Car builder ----------------
const tireGeo = new THREE.CylinderGeometry(0.33, 0.33, 0.26, 20);
const tireMat = new THREE.MeshStandardMaterial({ color: 0x141414, roughness: 0.9 });
const hubGeo = new THREE.CylinderGeometry(0.17, 0.17, 0.28, 12);
const hubMat = new THREE.MeshStandardMaterial({ color: 0xcfd4da, roughness: 0.3, metalness: 0.85 });
const glassMat = new THREE.MeshStandardMaterial({ color: 0x1b2733, roughness: 0.12, metalness: 0.4 });
const chromeMat = new THREE.MeshStandardMaterial({ color: 0xc7ccd2, roughness: 0.25, metalness: 0.9 });
const headMat = new THREE.MeshStandardMaterial({ color: 0xfffbe0, emissive: 0xfff3b8, emissiveIntensity: 1.4 });
const tailMat = new THREE.MeshStandardMaterial({ color: 0xd40f0f, emissive: 0xa80000, emissiveIntensity: 1.2 });

function buildCar(type, paintHex, paint2Hex) {
  const def = CAR_DEFS[type];
  const g = new THREE.Group();
  const paint = new THREE.MeshStandardMaterial({ color: paintHex, roughness: 0.32, metalness: 0.55 });
  const paint2 = new THREE.MeshStandardMaterial({ color: paint2Hex, roughness: 0.32, metalness: 0.55 });
  const L = def.len, W = def.wid;

  // lower body
  const body = new THREE.Mesh(new RoundedBoxGeometry(W, def.bodyH, L, 3, 0.16), paint);
  body.position.y = 0.52 + def.bodyH / 2; body.castShadow = true; g.add(body);

  // cabin / glass band
  const glass = new THREE.Mesh(new RoundedBoxGeometry(W * 0.9, def.cabinH, def.cabinD, 3, 0.22), glassMat);
  glass.position.set(0, 0.52 + def.bodyH + def.cabinH / 2 - 0.06, -L * 0.06);
  glass.castShadow = true; g.add(glass);

  // roof
  const roof = new THREE.Mesh(new RoundedBoxGeometry(W * 0.92, 0.12, def.cabinD + 0.2, 3, 0.1), paint);
  roof.position.set(0, 0.52 + def.bodyH + def.cabinH - 0.02, -L * 0.06);
  roof.castShadow = true; g.add(roof);

  // hood + trunk accents (two-tone)
  const hood = new THREE.Mesh(new RoundedBoxGeometry(W * 0.96, 0.1, L * 0.36, 2, 0.08), paint2);
  hood.position.set(0, 0.52 + def.bodyH - 0.02, -L * 0.28); hood.castShadow = true; g.add(hood);
  const trunk = new THREE.Mesh(new RoundedBoxGeometry(W * 0.96, 0.1, L * 0.3, 2, 0.08), paint2);
  trunk.position.set(0, 0.52 + def.bodyH - 0.02, L * 0.3); trunk.castShadow = true; g.add(trunk);

  // bumpers
  const bumpMat = new THREE.MeshStandardMaterial({ color: 0x2a2a2c, roughness: 0.7 });
  const fb = new THREE.Mesh(new RoundedBoxGeometry(W * 0.95, 0.22, 0.3, 2, 0.06), bumpMat);
  fb.position.set(0, 0.34, -L / 2 + 0.02); g.add(fb);
  const rb = fb.clone(); rb.position.set(0, 0.34, L / 2 - 0.02); g.add(rb);

  // grille
  const grille = new THREE.Mesh(new RoundedBoxGeometry(W * 0.55, 0.22, 0.08, 2, 0.02), chromeMat);
  grille.position.set(0, 0.52, -L / 2 + 0.02); g.add(grille);

  // headlights
  const hl = new THREE.Mesh(new RoundedBoxGeometry(0.34, 0.16, 0.1, 2, 0.04), headMat);
  hl.position.set(-W * 0.3, 0.6, -L / 2 + 0.02); g.add(hl);
  const hr = hl.clone(); hr.position.x = W * 0.3; g.add(hr);

  // taillights
  const tl = new THREE.Mesh(new RoundedBoxGeometry(0.4, 0.16, 0.1, 2, 0.04), tailMat);
  tl.position.set(-W * 0.32, 0.6, L / 2 - 0.02); g.add(tl);
  const tr = tl.clone(); tr.position.x = W * 0.32; g.add(tr);

  // mirrors
  const mm = new THREE.Mesh(new RoundedBoxGeometry(0.14, 0.1, 0.18, 1, 0.03), paint);
  mm.position.set(-W / 2 - 0.08, 0.95, -L * 0.24); g.add(mm);
  const mm2 = mm.clone(); mm2.position.x = W / 2 + 0.08; g.add(mm2);

  // wheels
  const wheels = { front: [], tire: [] };
  const axleY = 0.33;
  // rear wheels (non-steering)
  [W * 0.42, -W * 0.42].forEach(wx => {
    const wg = new THREE.Group();
    wg.position.set(wx, axleY, L * 0.32);
    wg.rotation.z = Math.PI / 2;
    const tire = new THREE.Mesh(tireGeo, tireMat); tire.castShadow = true;
    const hub = new THREE.Mesh(hubGeo, hubMat);
    wg.add(tire, hub);
    g.add(wg);
    wheels.tire.push(tire);
  });
  // front wheels (steerable)
  [W * 0.42, -W * 0.42].forEach(wx => {
    const sg = new THREE.Group(); sg.position.set(wx, axleY, -L * 0.32);
    const wg = new THREE.Group(); wg.rotation.z = Math.PI / 2;
    const tire = new THREE.Mesh(tireGeo, tireMat); tire.castShadow = true;
    const hub = new THREE.Mesh(hubGeo, hubMat);
    wg.add(tire, hub);
    sg.add(wg);
    g.add(sg);
    wheels.front.push(sg);
    wheels.tire.push(tire);
  });

  g.userData.wheels = wheels;
  g.userData.def = def;
  return g;
}

// ---------------- Player ----------------
function spawnPlayer(type) {
  if (player) { scene.remove(player.group); }
  const def = CAR_DEFS[type];
  const group = buildCar(type, def.paint, def.paint2);
  group.position.set(roadX[2], 0, roadZ[2]);
  group.rotation.y = 0;
  scene.add(group);
  camPos.set(group.position.x, 3.4, group.position.z + 7.2);
  player = { group, type, speed: 0, steer: 0, heading: 0, def };
}

function spawnTraffic() {
  traffic.forEach(t => scene.remove(t.group));
  traffic = [];
  for (let i = 0; i < 14; i++) {
    const type = ['peykan', 'pride', 'samand'][i % 3];
    const color = TRAFFIC_COLORS[i % TRAFFIC_COLORS.length];
    const group = buildCar(type, color, 0xffffff);
    const heading = [0, Math.PI / 2, Math.PI, -Math.PI / 2][i % 4];
    const lane = i % 2 === 0 ? -1 : 1;
    const ri = 1 + (i * 3) % (M - 1);
    let x = 0, z = 0;
    if (heading === 0 || heading === Math.PI) { x = roadX[ri] + lane * 2.5; z = (Math.random() - 0.5) * HALF * 2; }
    else { z = roadZ[ri] + lane * 2.5; x = (Math.random() - 0.5) * HALF * 2; }
    group.position.set(x, 0, z);
    group.rotation.y = heading;
    scene.add(group);
    traffic.push({ group, type, heading, speed: 7 + Math.random() * 5, lane });
  }
}

function spawnCoins() {
  coinSprites.forEach(c => scene.remove(c));
  coinSprites = [];
  const tex = coinTexture();
  const n = 60;
  for (let i = 0; i < n; i++) {
    const spr = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true }));
    const ri = (i * 5 + 2) % (M - 1);
    const axis = i % 2;
    let x, z;
    if (axis === 0) { x = roadX[ri] + (Math.random() - 0.5) * 5; z = -HALF + 8 + Math.random() * (HALF * 2 - 16); }
    else { z = roadZ[ri] + (Math.random() - 0.5) * 5; x = -HALF + 8 + Math.random() * (HALF * 2 - 16); }
    spr.position.set(x, 1.2, z);
    spr.scale.set(1.5, 1.5, 1);
    spr.userData = { base: 1.2, phase: Math.random() * Math.PI * 2 };
    scene.add(spr);
    coinSprites.push(spr);
  }
}

function clearParticles() {
  particles.forEach(p => scene.remove(p.mesh));
  particles = [];
}

function spawnParticles(pos, color, n, power) {
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(
      new THREE.SphereGeometry(0.12 + Math.random() * 0.14, 6, 5),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 1 })
    );
    m.position.copy(pos);
    const v = new THREE.Vector3((Math.random() - 0.5), Math.random() * 0.9 + 0.3, (Math.random() - 0.5)).multiplyScalar(power);
    scene.add(m);
    particles.push({ mesh: m, vel: v, life: 0.7 + Math.random() * 0.5 });
  }
}

// ---------------- Collision ----------------
function resolvePlayerCollisions(dt) {
  const p = player.group.position;
  const r = 1.05;
  // buildings
  for (const c of colliders) {
    const nx = Math.max(c.minX, Math.min(p.x, c.maxX));
    const nz = Math.max(c.minZ, Math.min(p.z, c.maxZ));
    const dx = p.x - nx, dz = p.z - nz;
    const d2 = dx * dx + dz * dz;
    if (d2 < r * r) {
      const d = Math.sqrt(d2) || 0.0001;
      p.x = nx + (dx / d) * r;
      p.z = nz + (dz / d) * r;
      player.speed *= 0.5;
      if (Math.abs(player.speed) < 1.5) player.speed = 0;
    }
  }
  // city bounds
  const lim = HALF + 6;
  if (p.x > lim) { p.x = lim; player.speed *= 0.5; }
  if (p.x < -lim) { p.x = -lim; player.speed *= 0.5; }
  if (p.z > lim) { p.z = lim; player.speed *= 0.5; }
  if (p.z < -lim) { p.z = -lim; player.speed *= 0.5; }
}

// ---------------- Game flow ----------------
function startGame() {
  score = 0; coins = 0; lives = 3; distM = 0; invuln = 0; shake = 0;
  clearParticles();
  spawnPlayer(selectedCar);
  spawnTraffic();
  spawnCoins();
  updateHUD();
  setState('playing');
}

function setState(s) {
  state = s;
  el('menu').classList.toggle('hidden', s !== 'menu');
  el('pauseMenu').classList.toggle('hidden', s !== 'paused');
  el('gameover').classList.toggle('hidden', s !== 'gameover');
  el('hud').style.display = (s === 'playing' || s === 'paused') ? 'block' : 'none';
  if (s !== 'playing' && audio.ready) audio.engineGain.gain.setTargetAtTime(0, audio.ctx.currentTime, 0.1);
}

function endGame() {
  audio.crash();
  el('finalScore').textContent = score.toLocaleString('fa-IR');
  el('finalCoins').textContent = coins.toLocaleString('fa-IR');
  el('finalDist').textContent = Math.round(distM).toLocaleString('fa-IR');
  setState('gameover');
}

function updateHUD() {
  hud.score.textContent = score.toLocaleString('fa-IR');
  hud.coin.textContent = coins.toLocaleString('fa-IR');
  hud.speed.textContent = Math.round(Math.abs(player ? player.speed * 3.6 : 0));
  hud.lives.textContent = '❤️'.repeat(Math.max(0, lives));
}

function floatScore(txt) {
  const d = document.createElement('div');
  d.className = 'float';
  d.textContent = txt;
  el('floatScores').appendChild(d);
  setTimeout(() => d.remove(), 1000);
}

// ---------------- Update ----------------
function update(dt) {
  if (state !== 'playing') return;
  const p = player;
  const def = p.def;

  // ---- input ----
  let steer = 0, throttle = 0, brake = 0;
  if (tiltEnabled) steer = clamp(tiltSteer, -1, 1);
  else steer = (keys.left ? 1 : 0) + (keys.right ? -1 : 0) + (touch.steer);
  steer = clamp(steer, -1, 1);
  if (keys.up || touch.gas) throttle = 1;
  if (keys.down || touch.brake) brake = 1;

  // ---- physics ----
  const sign = p.speed >= 0 ? 1 : -1;
  if (throttle) p.speed += def.accel * dt;
  else if (brake) p.speed -= 22 * dt;
  else p.speed -= (p.speed * 0.55 + Math.sign(p.speed) * 0.6) * dt;

  if (brake && Math.abs(p.speed) < 0.5) p.speed = 0;
  const maxV = def.maxSpeed, minV = -8;
  if (p.speed > maxV) p.speed = maxV;
  if (p.speed < minV) p.speed = minV;

  const steerPower = (Math.min(Math.abs(p.speed) / 6, 1) * 0.85 + 0.15);
  p.heading += steer * def.turn * steerPower * sign * dt;
  p.steer = THREE.MathUtils.lerp(p.steer, steer, 0.15);

  const fwd = new THREE.Vector3(-Math.sin(p.heading), 0, -Math.cos(p.heading));
  p.group.position.addScaledVector(fwd, p.speed * dt);
  p.group.rotation.y = p.heading;

  // wheels
  const wheels = p.group.userData.wheels;
  wheels.tire.forEach(t => t.rotation.y -= (p.speed / 0.33) * dt);
  wheels.front.forEach(sg => sg.rotation.y = p.steer * 0.45);

  // distance + score
  distM += Math.abs(p.speed) * dt;
  score += Math.abs(p.speed) * dt * 0.5;
  invuln = Math.max(0, invuln - dt);
  if (invuln > 0) {
    const blink = Math.floor(clock.elapsedTime * 12) % 2 === 0;
    p.group.visible = blink;
  } else p.group.visible = true;

  resolvePlayerCollisions(dt);

  // ---- traffic ----
  for (const t of traffic) {
    const dir = new THREE.Vector3(-Math.sin(t.heading), 0, -Math.cos(t.heading));
    t.group.position.addScaledVector(dir, t.speed * dt);
    t.group.rotation.y = t.heading;
    // wrap
    const lim = HALF + 5;
    if (t.group.position.x > lim) t.group.position.x = -lim;
    if (t.group.position.x < -lim) t.group.position.x = lim;
    if (t.group.position.z > lim) t.group.position.z = -lim;
    if (t.group.position.z < -lim) t.group.position.z = lim;

    // collision with player
    if (invuln <= 0) {
      const dx = t.group.position.x - p.group.position.x;
      const dz = t.group.position.z - p.group.position.z;
      if (dx * dx + dz * dz < 2.6 * 2.6) {
        crash();
      }
    }
  }

  // ---- coins ----
  for (const c of coinSprites) {
    if (!c.visible) continue;
    c.userData.phase += dt * 3;
    c.position.y = c.userData.base + Math.sin(c.userData.phase) * 0.35;
    const dx = c.position.x - p.group.position.x;
    const dz = c.position.z - p.group.position.z;
    if (dx * dx + dz * dz < 2.2 * 2.2) {
      c.visible = false;
      coins++; score += 50;
      audio.coin();
      floatScore('+۵۰');
      spawnParticles(c.position, 0xffd23f, 7, 4);
      updateHUD();
    }
  }

  // ---- particles ----
  for (let i = particles.length - 1; i >= 0; i--) {
    const pt = particles[i];
    pt.life -= dt;
    pt.vel.y -= 9.8 * dt;
    pt.mesh.position.addScaledVector(pt.vel, dt);
    pt.mesh.material.opacity = Math.max(0, pt.life / 0.8);
    if (pt.life <= 0) { scene.remove(pt.mesh); particles.splice(i, 1); }
  }

  updateCamera(dt);
  updateHUD();
  audio.engine(p.speed, throttle);
}

function crash() {
  lives--;
  invuln = 2.5;
  player.speed *= -0.35;
  shake = 0.6;
  audio.crash();
  spawnParticles(player.group.position.clone().add(new THREE.Vector3(0, 0.5, 0)), 0xff6b3d, 12, 7);
  const flash = el('crashFlash');
  flash.style.opacity = 1;
  setTimeout(() => flash.style.opacity = 0, 60);
  updateHUD();
  if (lives <= 0) endGame();
}

let camPos = new THREE.Vector3();
function updateCamera(dt) {
  const pos = player.group.position;
  const fwd = new THREE.Vector3(-Math.sin(player.heading), 0, -Math.cos(player.heading));
  const target = pos.clone().addScaledVector(fwd, -7.2).add(new THREE.Vector3(0, 3.4, 0));
  const k = 1 - Math.pow(0.0015, dt);
  camPos.lerp(target, k);
  if (shake > 0.001) {
    camPos.x += (Math.random() - 0.5) * shake;
    camPos.y += (Math.random() - 0.5) * shake;
    camPos.z += (Math.random() - 0.5) * shake;
    shake *= Math.pow(0.001, dt);
  }
  camera.position.copy(camPos);
  const look = pos.clone().addScaledVector(fwd, 5).add(new THREE.Vector3(0, 1.1, 0));
  camera.lookAt(look);

  // follow light + sky + sun sprite
  const sun = scene.userData.sun;
  sun.position.copy(pos).addScaledVector(sunDir, 90);
  sun.target.position.copy(pos);
  scene.userData.sky.position.copy(pos);
  scene.userData.sunSprite.position.copy(pos).addScaledVector(sunDir, 330);
}

// ---------------- Input ----------------
const keys = {};
const touch = { steer: 0, gas: false, brake: false };
let tiltSteer = 0;

function bindKeys() {
  addEventListener('keydown', e => {
    audio.ensure();
    const k = e.key.toLowerCase();
    if (['arrowup', 'w'].includes(k)) keys.up = true;
    if (['arrowdown', 's'].includes(k)) keys.down = true;
    if (['arrowleft', 'a'].includes(k)) keys.left = true;
    if (['arrowright', 'd'].includes(k)) keys.right = true;
    if (k === 'p' || k === 'escape') togglePause();
    if ([' ', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(e.key.toLowerCase())) e.preventDefault();
  });
  addEventListener('keyup', e => {
    const k = e.key.toLowerCase();
    if (['arrowup', 'w'].includes(k)) keys.up = false;
    if (['arrowdown', 's'].includes(k)) keys.down = false;
    if (['arrowleft', 'a'].includes(k)) keys.left = false;
    if (['arrowright', 'd'].includes(k)) keys.right = false;
  });
}

function bindButtons() {
  const steerBtn = (id, val) => {
    const b = el(id);
    const on = e => { e.preventDefault(); audio.ensure(); touch.steer = val; };
    const off = e => { e.preventDefault(); touch.steer = 0; };
    b.addEventListener('pointerdown', on);
    b.addEventListener('pointerup', off);
    b.addEventListener('pointercancel', off);
    b.addEventListener('pointerleave', off);
  };
  steerBtn('btnLeft', 1);
  steerBtn('btnRight', -1);

  const pedal = (id, key) => {
    const b = el(id);
    const on = e => { e.preventDefault(); audio.ensure(); touch[key] = true; };
    const off = e => { e.preventDefault(); touch[key] = false; };
    b.addEventListener('pointerdown', on);
    b.addEventListener('pointerup', off);
    b.addEventListener('pointercancel', off);
    b.addEventListener('pointerleave', off);
  };
  pedal('btnGas', 'gas');
  pedal('btnBrake', 'brake');
}

function bindTilt() {
  const btn = el('tiltBtn');
  btn.addEventListener('click', async () => {
    audio.ensure();
    if (!tiltEnabled) {
      let ok = true;
      if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
        try { await DeviceOrientationEvent.requestPermission(); } catch (e) { ok = false; }
      }
      tiltEnabled = ok;
      if (ok) btn.style.background = '#ffc93c'; else btn.style.background = '';
      if (ok) floatScore('فرمان چرخشی فعال شد 📱');
    } else {
      tiltEnabled = false;
      btn.style.background = '';
    }
  });
  addEventListener('deviceorientation', e => {
    if (!tiltEnabled) return;
    const gamma = e.gamma || 0;
    tiltSteer = clamp(-gamma / 22, -1, 1);
  });
}

function togglePause() {
  if (state === 'playing') setState('paused');
  else if (state === 'paused') setState('playing');
}

// ---------------- UI wiring ----------------
function wireUI() {
  document.querySelectorAll('.car-card').forEach(card => {
    card.addEventListener('click', () => {
      selectedCar = card.dataset.car;
      document.querySelectorAll('.car-card').forEach(c => c.classList.toggle('sel', c === card));
      audio.ensure();
    });
  });
  document.querySelector('.car-card[data-car="peykan"]').classList.add('sel');

  el('startBtn').addEventListener('click', () => { audio.ensure(); startGame(); });
  el('retryBtn').addEventListener('click', () => startGame());
  el('resumeBtn').addEventListener('click', () => setState('playing'));
  el('pauseBtn').addEventListener('click', togglePause);
  el('menuBtn').addEventListener('click', () => { clearParticles(); setState('menu'); });
  el('menuBtn2').addEventListener('click', () => { clearParticles(); setState('menu'); });
  el('muteBtn').addEventListener('click', () => { audio.ensure(); const m = audio.toggleMute(); el('muteBtn').textContent = m ? '🔇' : '🔊'; });

  addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && state === 'playing') setState('paused'); });

  // block scroll/gestures on the game surface (but allow overlay menus to scroll)
  document.addEventListener('touchmove', e => {
    if (e.target.closest && e.target.closest('.overlay')) return;
    e.preventDefault();
  }, { passive: false });
  document.addEventListener('contextmenu', e => e.preventDefault());
}

// ---------------- Main loop ----------------
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  update(dt);
  renderer.render(scene, camera);
}

// ---------------- Boot ----------------
async function boot() {
  try { await document.fonts.load('700 40px "Vazirmatn"'); } catch (e) {}
  try { await document.fonts.load('400 40px "Vazirmatn"'); } catch (e) {}
  try { await document.fonts.ready; } catch (e) {}

  setupRenderer();
  setupLights();
  setupSky();
  setupGround();
  buildCity();
  bindKeys();
  bindButtons();
  bindTilt();
  wireUI();
  setState('menu');
  el('loader').remove();

  // دسترسی عیب‌یابی (فقط با ?debug در آدرس فعال می‌شود)
  if (typeof window !== 'undefined' && /[?&]debug\b/.test(window.location && window.location.search || '')) {
    window.__gameDebug = {
      scene, camera, camPos: () => camPos,
      player: () => player, traffic: () => traffic, coins: () => coinSprites,
    };
  }
  animate();
}

function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

boot().catch(err => {
  el('loader').innerHTML = '<div style="font-size:18px;color:#ff8a8a">خطا در بارگذاری بازی 😢<br/>مرورگرت WebGL را پشتیبانی نمی‌کند.</div>' + err.message;
});
