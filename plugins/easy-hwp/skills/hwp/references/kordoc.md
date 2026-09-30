# Structured conversion with kordoc

Optional alternate parser for HWP, HWPX, and HWPML: Markdown, JSON blocks/metadata,
fields, comparison, batch conversion, watch, and Markdown-to-HWPX creation.
It is not the preserve-format binary editor; use `edit.mjs` for existing documents.

The distributed CLI may import PDF support even for HWP inputs, so include both packages:

```sh
npx --yes --package kordoc --package pdfjs-dist kordoc input.hwp -o output.md
npx --yes --package kordoc --package pdfjs-dist kordoc input.hwpx --format json
npx --yes --package kordoc --package pdfjs-dist kordoc input.hwp --pages 1-3
npx --yes --package kordoc --package pdfjs-dist kordoc ./documents/* -d ./converted
npx --yes --package kordoc --package pdfjs-dist kordoc watch ./documents
```

For repeated Node API use, install `kordoc pdfjs-dist` in a selected local project.
Global module resolution is not interchangeable with project-local ESM imports.

```js
import { parse, compare, extractFormFields, markdownToHwpx } from 'kordoc';
import { readFileSync, writeFileSync } from 'node:fs';
const parsed = await parse('input.hwpx');
if (!parsed.success) throw new Error(parsed.error);
const fields = extractFormFields(parsed.blocks);
const diff = await compare(readFileSync('before.hwp'), readFileSync('after.hwp'));
const result = await markdownToHwpx('# Example\n\nBody');
writeFileSync('new.hwpx', Buffer.from(result));
```

Check success, output blocks, expected fields, and comparison stats. Markdown reverse
conversion creates a new layout; it cannot preserve an existing template's formatting.
Do not use a missing OCR provider, password, or unsupported encrypted file as a reason to
silently substitute an incomplete output. This optional parser does not require installing
another HWP skill or running an unrelated global skill updater.

Primary source: [nathankim0/kordoc](https://github.com/nathankim0/kordoc).
