# Optional rhwp text CLI

The previous rhwp-edit skill's text insertion/deletion and direct engine CLI operations
are available from this single skill. Use them only when the bundled raw patch editor does
not cover an operation. This path may reserialize complex files; visually inspect the output.

```sh
npx --yes k-skill-rhwp info input.hwp
npx --yes k-skill-rhwp list-paragraphs input.hwp
npx --yes k-skill-rhwp search input.hwp --query "Example"
npx --yes k-skill-rhwp insert-text input.hwp output.hwp --section 0 --paragraph 1 --offset 0 --text "Example"
npx --yes k-skill-rhwp delete-text input.hwp output.hwp --section 0 --paragraph 1 --offset 0 --length 7
npx --yes k-skill-rhwp replace-all input.hwp output.hwp --query "old" --replacement "new"
npx --yes k-skill-rhwp create-table input.hwp output.hwp --section 0 --paragraph 1 --offset 0 --rows 3 --cols 4
npx --yes k-skill-rhwp set-cell-text input.hwp output.hwp --section 0 --parent-paragraph 1 --control 0 --cell 0 --text "Example"
npx --yes k-skill-rhwp create-blank output.hwp
npx --yes k-skill-rhwp render input.hwp --page 0 --format svg
```

Check the installed CLI's `--help` for options before using it; interfaces can change.
`search`/`replace-all` operate on body paragraphs, not cells, headers, or footnotes.
Newlines in replace-all are rejected; case folding that changes UTF-16 length requires
case-sensitive matching. Do not accidentally save an HWPX input as a differently encoded
`.hwpx`: verify the actual format and select an HWPX-native editing path.

Upstream advanced parsing/rendering APIs are documented in [rhwp-api.md](rhwp-api.md)
and [hwp-internals.md](hwp-internals.md). The bundled engine supports inspecting and
rendering without installing a standalone rhwp-advanced skill.

Primary source: [edwardkim/rhwp](https://github.com/edwardkim/rhwp).
