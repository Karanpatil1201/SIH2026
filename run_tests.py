import sys
import os
import glob
import importlib.util

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

test_files = sorted(glob.glob("tests/test_*.py"))
passed = 0
failed = 0

print("=" * 60)
print("RUNNING VARUNA SIH 2026 TEST SUITE")
print("=" * 60)

for tf in test_files:
    mod_name = os.path.basename(tf)[:-3]
    try:
        spec = importlib.util.spec_from_file_location(mod_name, tf)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            if attr.startswith("test_") and callable(getattr(mod, attr)):
                try:
                    getattr(mod, attr)()
                    print(f"  [PASS] {mod_name}.{attr}")
                    passed += 1
                except Exception as e:
                    print(f"  [FAIL] {mod_name}.{attr} -> {e}")
                    failed += 1
    except Exception as e:
        print(f"  [ERR] loading {mod_name}: {e}")
        failed += 1

print("=" * 60)
print(f"TEST RESULTS: {passed} PASSED, {failed} FAILED")
print("=" * 60)
if failed > 0:
    sys.exit(1)
