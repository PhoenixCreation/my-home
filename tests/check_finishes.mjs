// Run with: node tests/check_finishes.mjs (no dependencies).
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const module = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
const functions = ['applyWallColor', 'syncWallReset', 'applyWallFinish', 'applyCeilingColor', 'saveFurniture', 'restoreFurniture'];
const source = functions.map(name => {
  const start = module.indexOf(`    function ${name}(`);
  const end = module.indexOf('\n    }', start) + 6;
  assert.ok(start > 0 && end > start, name);
  return module.slice(start, end);
}).join('\n');
const context = vm.createContext({ assert });
vm.runInContext(`
class Color {
  constructor(value) { this.value = value; }
  set(value) { this.value = value; }
  copy(other) { this.value = other.value; }
  getHexString() { return this.value.slice(1); }
}
const material = () => ({color: new Color('#eeeeee')});
const a = material(), b = material(), outside = material();
const original = new Color('#eeeeee');
const wallMaterials = new Map([[a, original], [b, original], [outside, original]]);
const wallFinishes = new Map([
  ['master_north', {materials: new Map([[a, original]])}],
  ['small_south', {materials: new Map([[b, original]])}],
]);
let wallColor, ceilingColor;
const ceilingFinish = {material: material(), original};
const elements = new Map();
const $ = id => { if (!elements.has(id)) elements.set(id, {}); return elements.get(id); };
const showWallColors = () => {};
const furniture = [], doorFinishes = new Map();
let furnitureVisible = true;
const STORE_KEY = 'test';
let stored;
const localStorage = {setItem: (key, value) => stored = value, getItem: () => stored};
const isColor = value => typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value);
function applySectionColor(section, value) {
  section.value = value;
  if (value) section.material.color.set(value); else section.material.color.copy(section.original);
}
${source}
applyWallColor('#112233');
assert.equal(a.color.value, '#112233');
assert.equal(ceilingFinish.material.color.value, '#112233');
applyWallFinish(wallFinishes.get('master_north'), '#ff0000');
assert.equal(a.color.value, '#ff0000');
assert.equal(b.color.value, '#112233', 'other side of partition stays independent');
saveFurniture();
const saved = JSON.parse(stored);
assert.equal(saved.wallColors.master_north, '#ff0000');
applyWallColor();
assert.equal(a.color.value, '#eeeeee');
restoreFurniture();
applyWallColor(wallColor, false);
for (const section of wallFinishes.values()) applyWallFinish(section, section.value);
assert.equal(a.color.value, '#ff0000', 'restore per-wall overrides after global finish');
assert.equal(b.color.value, '#112233');
applyCeilingColor('#abcdef');
applyWallColor('#334455');
assert.equal(a.color.value, '#334455', 'global paint clears overrides');
assert.equal(ceilingFinish.material.color.value, '#abcdef', 'explicit ceiling stays independent');
applyWallFinish(wallFinishes.get('master_north'), '#000000');
applyWallFinish(wallFinishes.get('master_north'));
assert.equal(a.color.value, '#334455', 'room reset inherits global paint');
stored = JSON.stringify({wallColor: '#123456', wallColors: {master_north: 'bad'}});
applyWallColor();
restoreFurniture();
assert.equal(wallColor, '#123456', 'old saved finishes remain supported');
assert.equal(wallFinishes.get('master_north').value, undefined, 'ignore invalid colors');
applyWallColor();
assert.equal($('wall-reset').disabled, true);
`, context);
assert.ok(html.includes("Het's Home"));
assert.ok(!html.includes('SUN FOOTPRINTS'));
console.log('PASS: independent walls, save/restore, legacy saves, global/room resets, ceiling, branding');
