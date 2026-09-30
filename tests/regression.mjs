import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { inflateRawSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const scripts = path.join(root, 'plugins/easy-hwp/skills/hwp/scripts');
const require = createRequire(import.meta.url);
const CFB = require(path.join(scripts, 'vendor/cfb/cfb.js'));
const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'easy-hwp-test-'));
const source = path.join(folder, '한글 example.hwp'), output = path.join(folder, 'result.hwp');
const run = (name, args = [], payload, ok = true) => {
  const r = spawnSync(process.execPath, [path.join(scripts, name), ...args], { input: payload && JSON.stringify(payload), encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 });
  if (ok) assert.equal(r.status, 0, r.stdout + r.stderr);
  return r;
};
const inspect = file => JSON.parse(run('extract_text.js', ['--inspect', '--with-cell-text', file]).stdout);
function records(file, streamName) {
  const cfb = CFB.read(fs.readFileSync(file), { type: 'buffer' });
  const stream = cfb.FileIndex.find(x => x.name === streamName);
  assert(stream, streamName);
  const raw = inflateRawSync(stream.content), result = [];
  for (let off = 0; off < raw.length;) {
    const n = raw.readUInt32LE(off); off += 4;
    let size = n >>> 20;
    if (size === 4095) { size = raw.readUInt32LE(off); off += 4; }
    result.push({ tag: n & 1023, level: (n >>> 10) & 1023, body: raw.subarray(off, off + size) });
    off += size;
  }
  return result;
}
const edit = operations => {
  const file = path.join(folder, 'operations.json');
  fs.writeFileSync(file, JSON.stringify(operations));
  const result = run('edit.mjs', [source, output, file]);
  assert.equal(JSON.parse(result.stdout).status, 'success');
  return file;
};

try {
  const created = run('create.js', [], { path: source, operations: [
    { type: 'setup_document', page_size: 'a4', margin_mm: 20 },
    { type: 'append_paragraph', text: 'Synthetic fixture' },
    { type: 'append_paragraph', text: 'Notice|Account' },
    { type: 'append_heading', level: 1, text: 'Section heading' },
    { type: 'append_paragraph', text: 'Section content' },
    { type: 'append_table', headers: ['Role', 'Notes'], rows: [['', ''], ['', '']] },
  ] });
  assert.equal(JSON.parse(created.stdout).status, 'success');
  const table = inspect(source).tables[0];
  assert(table);
  const at = (row, col) => ({ section: table.sec, para: table.para, control: table.ctrl, row, col });
  const sourceHash = fs.readFileSync(source);
  edit([
    { type: 'set_cell_text', ...at(1, 1), text: '첫 줄\n둘째 줄' },
    { type: 'set_cell_background', ...at(0, 1), background_color: '#AABBFF' },
    { type: 'set_cell_background', ...at(1, 1), background_color: '#FFFFFF' },
    { type: 'split_cell', ...at(1, 1), into_rows: 2 },
    { type: 'set_cell_border', ...at(1, 1), sides: 'all', width_mm: 0.12 },
    { type: 'set_cell_property', ...at(1, 1), height_mm: 16, valign: 'center' },
  ]);
  assert.deepEqual(fs.readFileSync(source), sourceHash, 'editing overwrote input');
  const section = records(output, 'Section0');
  const cellHeaders = section.filter(r => r.tag === 0x48 && r.level === 2);
  const cell = (row, col) => cellHeaders.find(r => r.body.readUInt16LE(8) === col && r.body.readUInt16LE(10) === row);
  assert.equal(cell(1, 1).body.readUInt16LE(32), cell(2, 1).body.readUInt16LE(32), 'split borrowed the header fill');
  assert.notEqual(cell(0, 1).body.readUInt16LE(32), cell(2, 1).body.readUInt16LE(32));
  const borderFills = records(output, 'DocInfo').filter(r => r.tag === 20);
  const border = borderFills[cell(1, 1).body.readUInt16LE(32) - 1].body;
  for (const offset of [2, 8, 14, 20]) assert.equal(border[offset + 1], 1, 'physical border width was not converted to preset');
  fs.copyFileSync(output, path.join(folder, 'multiline.hwp'));
  const cells = inspect(output).tables[0].cells;
  assert.equal(cells.find(c => c.row === 1 && c.col === 1).text, '첫 줄\n둘째 줄');
  let activeText, segmentsAfterText = 0;
  for (const r of section) {
    if (r.tag === 0x42) activeText = undefined;
    if (r.tag === 0x43) activeText = r.body.toString('utf16le');
    if (r.tag === 0x45 && activeText?.includes('첫 줄')) segmentsAfterText++;
  }
  assert.equal(segmentsAfterText, 0, 'newlines kept stale line layout');

  edit([
    { type: 'split_body_paragraph', target: 'Notice', separator: '|' },
    { type: 'start_section_page', target: 'Section heading', gap_pt: 18 },
    { type: 'start_section_page', target: 'Section heading', gap_pt: 24 },
    { type: 'apply_paragraph_style', target: 'Section heading', spacing_after_pt: 6, keep_with_next: true },
  ]);
  const body = records(output, 'Section0');
  const headers = body.filter(r => r.tag === 0x42 && r.level === 0);
  assert.equal(headers.filter(r => r.body[11] & 4).length, 1, 'repeated section page added another break');
  const texts = body.filter(r => r.tag === 0x43 && r.level === 1).map(r => r.body.toString('utf16le'));
  assert(texts.includes('Notice\r') && texts.includes('Account\r'));
  const heading = body.findIndex(r => r.tag === 0x43 && r.body.toString('utf16le') === 'Section heading\r');
  const paraHeader = body.slice(0, heading).findLast(r => r.tag === 0x42 && r.level === 0);
  const paraShapeId = paraHeader.body.readUInt16LE(8);
  const shapes = records(output, 'DocInfo').filter(r => r.tag === 25);
  assert.equal(shapes[paraShapeId].body.readInt32LE(20), 600, 'point units were treated as HWPUNIT');
  assert(shapes[paraShapeId].body.readUInt32LE(0) & (1 << 17), 'keep-with-next bit incorrect');

  const opsFile = path.join(folder, 'failure.json');
  fs.writeFileSync(opsFile, JSON.stringify([{ type: 'set_cell_text', ...at(1, 0), text: 'changed' }, { type: 'set_cell_text', ...at(999, 0), text: 'invalid' }]));
  const beforeFailure = fs.readFileSync(output);
  assert.notEqual(run('edit.mjs', [source, output, opsFile], null, false).status, 0);
  assert.deepEqual(fs.readFileSync(output), beforeFailure, 'failed stage damaged output');
  assert.notEqual(run('edit.mjs', [source + '\n', output, opsFile], null, false).status, 0);
  console.log('PASS: multiline reflow, split styles, paragraph splitting, repeatable page spacing, units, and atomic failure');
} finally {
  if (process.env.KEEP_HWP_TEST_ARTIFACTS) console.log('Synthetic test artifacts:', folder);
  else fs.rmSync(folder, { recursive: true, force: true });
}
