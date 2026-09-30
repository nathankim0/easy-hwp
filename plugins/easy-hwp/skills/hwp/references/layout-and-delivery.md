# Layout repairs and release checks

## Cell text and body paragraphs

HWP stores `PARA_LINE_SEG` caches separately from text. A replacement that retains old
segments can show a new name at an old position or ignore an inserted line break.
The engine now clears the affected nonempty paragraph's layout records and line count.
Empty cells retain their native empty-paragraph shape, and inline objects are guarded.
Do not remove every cache in a document: that can reflow unrelated pages.

For independent numbered body items, use:

```json
{"type":"split_body_paragraph","target":"가. 공지","separator":"\n"}
```

This splits one plain text paragraph at the existing separator while retaining its styles.
It rejects paragraphs with fields/objects and does not invent missing items.

## Page heading spacing

```json
{"type":"start_section_page","target":"8. 준비 사항","gap_pt":18}
```

This moves the break to a single empty spacer immediately before the heading. Reapplying
updates the spacer instead of inserting another. The heading's own page-break bit is cleared
to prevent a double break. The gap applies at page start; many HWP renderers suppress normal
paragraph `spacing_before` at the top of a page. Inspect the native file and exported PDF.

Ordinary formatting uses explicit units:

```json
{"type":"apply_paragraph_style","target":"제목","keep_with_next":true,"spacing_after_pt":6}
```

100 HWPUNIT = 1 pt. Cell width/height/margins use mm. Font size uses pt. Border `width`
uses an index into 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5 mm, etc.; prefer `width_mm`.

Binary layout flags and units follow Hancom's
[HWP 5.0 revision 1.3 specification](https://cdn.hancom.com/link/docs/%ED%95%9C%EA%B8%80%EB%AC%B8%EC%84%9C%ED%8C%8C%EC%9D%BC%ED%98%95%EC%8B%9D_5.0_revision1.3.pdf).

## Borders and unknown values

Use actual cells from `--inspect --with-cell-text`, not every rectangular grid slot. A merged
cell is one cell. Set all four sides of every cell to the requested width, preserving fill
and diagonal. Adjacent cells with different shared-edge widths create uneven internal lines.
Merge consecutive unknown cells horizontally within a role row, never different role rows.
A user asking for two separate unknown testimony slots overrides general merging advice.

## Role, dates, and names

Maintain one explicit change list for the latest request. Search body and tables and align
summary text, service assignments, and supply responsibilities where they describe the same
task. Do not globally replace a person when only one assignment changes. Shift preparation
dates only when requested, verify weekdays, and leave unrelated intentional dates alone.
Do not copy old dates, speakers, places, gifts, or programs from a reference document without
authorization. Never use a prior draft as the base when an approved newer one exists.

## Final file paths and delivery

Use `Path.resolve(strict=True)` / `realpathSync` on the actual discovered file. Pass process
arguments as arrays; do not paste a visually wrapped filename into a shell command. Reject
CR/LF in document paths, and check the final extension. Stage and hash both HWP and PDF after
all edits, then send those exact paths through the user's existing authorized bot account.
Do not print bot tokens or chat IDs. A message ID or explicit recipient confirmation proves
delivery; an installed bot, accepted file path, or successful export does not.
