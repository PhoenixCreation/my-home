// Run with: node tests/check_layouts.mjs (no dependencies).
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const module = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
const names = ['captureFurnitureState', 'saveFurniture', 'restoreFurniture', 'allFinishSections', 'exportLayout', 'validateLayout', 'importLayout', 'applySectionColor', 'setFinishTexture', 'applyWallColor', 'applyWallFinish', 'syncWallReset', 'applyCeilingColor', 'resetItem', 'configureItem', 'isMoved'];
const source = names.map(name => {
  const match = new RegExp(`    (?:async )?function ${name}\\(`).exec(module);
  assert.ok(match, name);
  return module.slice(match.index, module.indexOf('\n    }', match.index) + 6);
}).join('\n');
const context = vm.createContext({assert});
await vm.runInContext(`(async () => {
class Color {
  constructor(value = '#eeeeee') { this.value = value; }
  set(value) { this.value = typeof value === 'number' ? '#ffffff' : value; }
  copy(value) { this.value = value.value; }
  getHexString() { return this.value.slice(1); }
}
const section = key => ({material: {color: new Color()}, original: new Color(), textureKey: key});
const chair = {key: 'chair', root: {position: {x: 1, z: -1}, rotation: {y: 0}}, home: {x: 1, z: -1, r: 0}, sections: new Map([['Wood', section('chair-wood')]]), mirror: [], fixed: false};
const bed = {key: 'bed', root: {position: {x: 2, z: -2}, rotation: {y: 0}}, home: {x: 2, z: -2, r: 0}, sections: new Map([['Fabric', section('bed-fabric')]]), mirror: [{mesh: {position: {x: 0}}, homeX: 0}]};
const furniture = [chair, bed];
let furnitureVisible = true, wallColor, ceilingColor, mode = 'orbit', yaw = 1, pitch = 0, introDismissed = true;
let drag = null, tap = null;
const wall = {color: new Color()};
const wallMaterials = new Map([[wall, new Color()]]);
const wallFinishes = new Map([['master_north', {materials: new Map([[wall, new Color()]])}]]);
const ceilingFinish = section('ceiling');
const doorFinishes = new Map([['door', section('door')]]);
const BOUNDS = {minX: -0.4, maxX: 8.6, minZ: -9.6, maxZ: 0.4};
const STORE_KEY = 'state';
const storage = new Map([['unrelated', 'keep']]);
let failWrite = false;
const localStorage = {
  getItem: key => storage.get(key) ?? null,
  removeItem: key => storage.delete(key),
  setItem(key, value) { if (failWrite) { failWrite = false; throw Error('quota'); } storage.set(key, value); },
};
const elements = new Map();
const $ = id => { if (!elements.has(id)) elements.set(id, {}); return elements.get(id); };
const showWallColors = () => {}, showDoorColors = () => {}, select = () => {}, resetJoystick = () => {}, showLayoutPanel = () => {}, updateLook = () => {}, syncRoom = () => {};
const keys = new Set();
const setFurnitureVisible = value => furnitureVisible = value;
const setMode = value => mode = value;
const vec = () => ({values: [1, 2, 3], toArray() {return [...this.values]}, fromArray(v) {this.values = [...v]}});
const camera = {position: vec()}, orbit = {target: vec(), update() {}};
const isColor = value => typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value);
let textureError = false, disposed = 0;
const loadFinishTexture = async url => { if (textureError) throw Error('bad image'); return {image: {src: url}, dispose() {disposed++}}; };
${source}
// Populate every category, export, and serialize as an actual downloaded file would.
chair.root.position.x = 4; chair.root.rotation.y = 1.57;
configureItem(bed, true);
applySectionColor(chair.sections.get('Wood'), '#112233');
applyWallColor('#223344');
applyWallFinish(wallFinishes.get('master_north'), '#334455');
applyCeilingColor('#445566');
applySectionColor(doorFinishes.get('door'), '#556677');
setFurnitureVisible(false);
const image = 'data:image/png;base64,aGVsbG8=';
setFinishTexture(chair.sections.get('Wood'), await loadFinishTexture(image), image);
const snapshot = JSON.parse(JSON.stringify(exportLayout()));
assert.equal(snapshot.textures['chair-wood'], image);
// Dirty an otherwise default item/section to verify replacement rather than merging.
bed.root.position.x = 5;
applySectionColor(bed.sections.get('Fabric'), '#ff0000');
setFinishTexture(bed.sections.get('Fabric'), await loadFinishTexture(image), image);
await importLayout(snapshot);
assert.deepEqual(JSON.parse(JSON.stringify(exportLayout())), snapshot, 'full JSON round trip');
assert.equal(bed.root.position.x, 2, 'unsaved movement reset');
assert.equal(bed.sections.get('Fabric').value, undefined);
assert.equal(bed.sections.get('Fabric').texture, null);
assert.equal(bed.deployed, true);
assert.equal(chair.root.rotation.y, 1.57);
assert.equal(wall.color.value, '#334455');
assert.equal(ceilingFinish.material.color.value, '#445566');
assert.equal(storage.get('chair-wood'), image);
assert.equal(storage.has('bed-fabric'), false);
assert.equal(storage.get('unrelated'), 'keep');
const before = JSON.stringify(exportLayout()), beforeStorage = JSON.stringify([...storage]);
for (const mutate of [
  data => data.version = 99,
  data => data.state.items.chair = [Infinity, 0, 0],
  data => data.state.items.chair = [100, 0, 0],
  data => data.state.wallColors.master_north = 'invalid',
  data => data.state.finishes.chair.Unknown = '#000000',
  data => data.textures['chair-wood'] = 'https://example.com/image.png',
  data => data.state.deployed.push('unknown'),
  data => data.view.mode = 'invalid',
]) {
  const invalid = JSON.parse(JSON.stringify(snapshot)); mutate(invalid);
  await assert.rejects(importLayout(invalid));
  assert.equal(JSON.stringify(exportLayout()), before, 'invalid input cannot change scene');
  assert.equal(JSON.stringify([...storage]), beforeStorage);
}
textureError = true;
await assert.rejects(importLayout(snapshot), /texture/);
textureError = false;
assert.equal(JSON.stringify(exportLayout()), before);
assert.equal(JSON.stringify([...storage]), beforeStorage);
failWrite = true;
await assert.rejects(importLayout(snapshot), /storage/);
assert.equal(JSON.stringify(exportLayout()), before, 'storage failure cannot change scene');
assert.deepEqual([...storage].sort(), JSON.parse(beforeStorage).sort(), 'storage rolled back');
chair.sections.get('Wood').upload = Symbol();
assert.throws(exportLayout, /uploads/);
await assert.rejects(importLayout(snapshot), /uploads/);
chair.sections.get('Wood').upload = null;
assert.ok(disposed > 0);
})()`, context);
console.log('PASS: full layout/texture/view round trip, replace defaults, malformed input, texture failures, storage rollback, pending uploads');
