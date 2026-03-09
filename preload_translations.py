"""
preload_translations.py — One-time language pre-caching script
═══════════════════════════════════════════════════════════════════
Run this script ONCE before launching the Climate Simulator to translate
all 11 languages and save the results to `.translation_cache.json`.

After this script finishes, switching languages in the app will be INSTANT
because every translation is already stored on disk.

Usage:
    python preload_translations.py

This script will skip any language that is already in the cache.
"""

import sys
import time
sys.stdout.reconfigure(encoding="utf-8")
from translations import LANGUAGES, get_ui_strings, get_missions, get_choices

SKIP_LANGS = {"en"}   # English is always instant, no API needed

def main():
    langs = {label: code for label, code in LANGUAGES.items() if code not in SKIP_LANGS}
    total = len(langs)
    print("=" * 55)
    print("  Climate Simulator -- Translation Preloader")
    print("=" * 55)
    print(f"  Will translate into {total} languages.\n")

    for i, (label, code) in enumerate(langs.items(), 1):
        print(f"[{i}/{total}] {label.encode('ascii', 'replace').decode()} ({code})  ", end="", flush=True)
        t0 = time.time()
        try:
            get_ui_strings(code)
            get_missions(code)
            get_choices(code)
            elapsed = time.time() - t0
            print(f"OK  ({elapsed:.1f}s)")
        except Exception as e:
            print(f"FAILED  ({e})")

    print("\n[DONE] All languages cached!")
    print("       Language switching is now instant in the app.")
    print("       Cache file: .translation_cache.json\n")

if __name__ == "__main__":
    main()

