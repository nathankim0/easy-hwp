# Forms, native Windows support, and templates

The former analyze/fill/template capabilities are part of the single `hwp` skill.

## Analyze and fill

Use the bundled inspector for binary HWP or HWPX; macOS/Linux are no longer limited to HWPX.
HWPX is a ZIP package with `Contents/header.xml` and `Contents/section*.xml`; inspect all
sections. Preserve namespaces, run formatting, and cell spans. A label is not necessarily
the first column and a value is not necessarily the second, especially in merged forms.
Use explicit coordinates or unambiguous labels. Ask only for materially ambiguous mapping;
do not ask again for already authorized filling. For private profiles use secure-fill.

On Windows with native Hancom available, pyhwpx is an optional native path:

```python
from pyhwpx import Hwp
hwp = Hwp()
try:
    hwp.open("input.hwp")
    # get_field_list(), get_field_text(), put_field_text() use native form fields.
    hwp.put_field_text("과제명", "사용자가 제공한 제목")
    hwp.save_as("output.hwp")
finally:
    hwp.quit()
```

Do not install it on macOS or treat it as a required dependency for the bundled editor.

## Project templates

Store templates in the user's selected project `templates/` directory, with `index.json`
recording name, file, fields, and creation date. Preserve the input's `.hwp` or `.hwpx`
extension. Support save/list/info/delete by normal file operations; validate names to prevent
path traversal. Reuse a saved template without changing the source. Existing unrelated
templates must not be overwritten or deleted without that scope being authorized.
Keep private forms out of Git, and do not store personal field values in metadata.

This workflow replaces the former separate analyze/fill/template skills. Binary HWP is
supported on macOS/Linux, and merged-cell mappings are resolved explicitly.
