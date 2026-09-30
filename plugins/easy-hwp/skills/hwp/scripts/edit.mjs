#!/usr/bin/env node
// Ordered edits on a disposable copy; the original survives failed operations.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { editBodyLayoutInPlace } from './cell-patch.js';

const [input, output, operationsFile] = process.argv.slice(2);
const here = path.dirname(fileURLToPath(import.meta.url));
let folder;
try {
  if (!input || !output || !operationsFile) throw new Error('usage: node edit.mjs input.hwp output.hwp operations.json');
  for (const p of [input, output, operationsFile]) if (/[\r\n\0]/.test(p)) throw new Error('document paths must not contain CR, LF, or NUL');
  const source = fs.realpathSync(input), destination = path.resolve(output);
  const ext = path.extname(destination).toLowerCase();
  if (!['.hwp', '.hwpx'].includes(ext) || path.extname(source).toLowerCase() !== ext) throw new Error('editing must preserve the .hwp/.hwpx format; use a conversion command explicitly');
  const data = JSON.parse(fs.readFileSync(operationsFile, 'utf8'));
  const operations = Array.isArray(data) ? data : data.operations;
  if (!Array.isArray(operations) || !operations.length || operations.some(o => !o || typeof o.type !== 'string')) throw new Error('operations must be a nonempty array of typed operations');
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  folder = fs.mkdtempSync(path.join(path.dirname(destination), '.hwp-edit-'));
  const working = path.join(folder, 'working' + ext);
  fs.copyFileSync(source, working);
  const run = (name, args, payload) => {
    const result = spawnSync(process.execPath, [path.join(here, name), ...args], { input: payload, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
    if (result.error) throw result.error;
    if (result.status !== 0) throw new Error(result.stderr || result.stdout || `${name} failed`);
    const response = JSON.parse(result.stdout);
    if (response.status === 'error' || response.isError || response.ok === false) throw new Error(response.message || `${name} rejected edit`);
    return response;
  };
  // Batch adjacent operations of the same type; preserve dependencies between types.
  for (let i = 0; i < operations.length;) {
    let end = i + 1;
    while (end < operations.length && operations[end].type === operations[i].type) end++;
    const stage = operations.slice(i, end);
    if (['split_body_paragraph', 'start_section_page'].includes(stage[0].type)) {
      if (ext !== '.hwp') throw new Error('body layout operations currently support binary HWP only; use native HWPX paragraph operations');
      await editBodyLayoutInPlace(working, stage);
    } else {
      run(ext === '.hwp' ? 'create.js' : 'hwpx-edit.js', [], JSON.stringify({ path: working, operations: stage }));
    }
    i = end;
  }
  const inspection = run('extract_text.js', ['--inspect', working]);
  fs.renameSync(working, destination);
  console.log(JSON.stringify({ status: 'success', path: destination, ops_applied: operations.length, verify: inspection }));
} catch (error) {
  console.error(JSON.stringify({ status: 'error', message: error.message }));
  process.exitCode = 1;
} finally {
  if (folder) fs.rmSync(folder, { recursive: true, force: true });
}
