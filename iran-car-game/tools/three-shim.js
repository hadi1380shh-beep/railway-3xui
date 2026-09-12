// شیم سه‌جیاس برای تست بدون مرورگر: تمام خروجی‌های واقعی three را نگه می‌دارد،
// فقط WebGLRenderer را با یک نسخهٔ صوری (بدون نیاز به کارت گرافیک) جایگزین می‌کند.
export * from '../node_modules/three/build/three.module.js';
import { Clock as RealClock } from '../node_modules/three/build/three.module.js';

// در تست، دلتای ثابت ۱/۶۰ ثانیه برمی‌گردانیم تا شبیه‌سازی واقعی اجرا شود
export class Clock extends RealClock {
  getDelta() { return 1 / 60; }
}

function fakeCanvas() {
  return {
    width: 300,
    height: 150,
    style: {},
    addEventListener() {},
    removeEventListener() {},
    getContext() { return null; },
  };
}

export class WebGLRenderer {
  constructor() {
    this.domElement = fakeCanvas();
    this.shadowMap = { enabled: false, type: 0 };
    this.toneMapping = 0;
    this.toneMappingExposure = 1;
    this.outputColorSpace = '';
    this._calls = 0;
  }
  setPixelRatio() {}
  setSize() {}
  render() { this._calls++; }
  setClearColor() {}
  setScissorTest() {}
  getContext() { return null; }
  dispose() {}
}
