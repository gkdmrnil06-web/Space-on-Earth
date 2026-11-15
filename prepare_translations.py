"""Optional: generate persistent translation cache using Cloud Translation API.
Usage: python prepare_translations.py fr ja vi de es ar ...
Requires GOOGLE_TRANSLATE_API_KEY environment variable.
"""
import ast
import sys
from pathlib import Path
from cloud_translation import translate, configured

def collect_strings():
    strings = set()
    for path in Path(__file__).parent.glob("*.py"):
        if path.name in ("prepare_translations.py", "cloud_translation.py"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("t", "ui_text"):
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    strings.add(node.args[0].value)
    return sorted(strings)

if __name__ == "__main__":
    if not configured():
        raise SystemExit("Set GOOGLE_TRANSLATE_API_KEY first.")
    langs = sys.argv[1:]
    if not langs:
        raise SystemExit("Pass language codes, e.g. fr ja vi de es ar.")
    strings = collect_strings()
    for lang in langs:
        errors = 0
        for i, source in enumerate(strings, 1):
            try:
                translate(source, lang)
            except Exception as exc:
                errors += 1
                print(f"{lang} {i}/{len(strings)}: {type(exc).__name__}: {exc}")
        print(f"{lang}: {len(strings)-errors}/{len(strings)} prepared")
