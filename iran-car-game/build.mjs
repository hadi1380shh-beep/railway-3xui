// ساخت بازی به‌صورت یک فایل HTML مستقل (بدون نیاز به اینترنت)
// خروجی: index.html (کنار همین پوشه)
import { build } from 'esbuild';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, 'src', 'game.js'), 'utf8');
const template = readFileSync(join(here, 'index.template.html'), 'utf8');

const result = await build({
  stdin: { contents: src, sourcefile: 'game.js', loader: 'js', resolveDir: here },
  bundle: true,
  minify: true,
  format: 'iife',
  target: ['es2019'],
  platform: 'browser',
  charset: 'utf8',
  write: false,
});

const out = result.outputFiles[0].text;
const html = template.replace('/*__BUNDLE__*/', () => out);
writeFileSync(join(here, 'index.html'), html);
console.log('✔ built index.html (' + (html.length / 1024).toFixed(1) + ' KB)');
