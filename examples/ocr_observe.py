"""Optional OCR observation example.

Run only on authorized devices and environments where collecting visible screen
text is appropriate.
"""

from plugins.ocr_plugin import ocr_lines, ocr_status


status = ocr_status()
print({"ocr_status": status})

if status["available"]:
    lines = ocr_lines()
    print({"ocr_line_count": len(lines), "sample_ocr_lines": lines[:10]})
else:
    print({"ocr_line_count": 0, "sample_ocr_lines": []})
