# UI Targeting

Use the narrowest reliable target and fall back in this order:

1. Match text or content description with `find_text()` or `tap_text()`.
2. Match a stable resource ID in `ui_tree()`, then use `tap_element()`. If only
   serialized bounds are available, use `tap(*bounds_center(bounds))`. A
   redacted page-info snapshot preserves resource IDs, classes, and bounds when
   text should not enter logs.
3. Inspect a screenshot when the UI tree is missing, stale, or ambiguous.
4. Tap stable screen coordinates only after checking the screenshot and screen
   size.
5. Use the optional host-side OCR plugin when readable screenshot text is not
   exposed by the UI tree.

For broad inspection, start with:

```bash
android-harness snapshot --page-info --summary
```

Use `--redact-text` for structural details without visible text and
`--redact-all` for share-safe artifacts. Full `page_info()` output is appropriate
when the current app and screen are already scoped and semantic labels are
required, but it can include unrelated visible account or search-history text.

`ui_tree()` and `page_info()` rely on UiAutomator XML. That XML can be incomplete
for WebView, games, canvas, and custom-rendered UI, so screenshots remain the
primary fallback.
