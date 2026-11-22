# -*- coding: utf-8 -*-
"""رگرسیون «پرش اول برنامه روی اندروید» (۴٫۱٫۲): هیچ بستهٔ بومی/آزمایشی نباید در مسیر شروع APK باشد و خطای شروع باید دیده شود."""
import os, sys, unittest, importlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f: return f.read()

class TestAndroidStartup(unittest.TestCase):
    def test_no_experimental_native_packages_in_apk(self):
        py = read("pyproject.toml")
        dep = next(l for l in py.splitlines() if l.startswith("dependencies"))
        self.assertEqual(dep.replace(" ", ""), 'dependencies=["flet==0.28.3"]')
        self.assertNotIn("notification", py.lower())
        self.assertEqual(read("requirements.txt").strip(), "flet==0.28.3")

    def test_ci_has_no_bytecode_flags(self):
        for f in (".github/workflows/build.yml", "WORKFLOW_build.yml.txt"):
            try: ci = read(*f.split("/"))
            except OSError: continue
            self.assertNotIn("$FAST_ARGS", ci); self.assertNotIn("--compile-packages\\)", ci)

    def test_notify_import_runs_no_foreign_code(self):
        sys.modules.pop("flet_local_notifications", None)
        import notify; importlib.reload(notify)
        self.assertNotIn("flet_local_notifications", sys.modules)         # فقط find_spec؛ هیچ کدی از بستهٔ بیرونی اجرا نمی‌شود
        self.assertFalse(notify.AVAILABLE)
        n = notify.Notifier(object()); self.assertFalse(n.ready); self.assertFalse(n.send("a", "b"))

    def test_notify_survives_exploding_package(self):
        import types, notify
        bad = types.ModuleType("flet_local_notifications")
        def boom(name):
            raise SystemExit("native init failed")
        bad.__getattr__ = boom
        sys.modules["flet_local_notifications"] = bad
        old = notify.AVAILABLE; notify.AVAILABLE = True; errs = []
        try:
            n = notify.Notifier(object(), lambda w, e=None: errs.append(w))
            self.assertFalse(n.ready); self.assertFalse(n.send("a", "b")); self.assertTrue(errs)
        finally:
            notify.AVAILABLE = old; sys.modules.pop("flet_local_notifications", None)

    def test_startup_error_is_shown_not_silent(self):
        import tempfile, fake_flet as F
        F.install()
        import main as app
        tmp = tempfile.TemporaryDirectory(); os.environ["FLET_APP_STORAGE_DATA"] = tmp.name
        page = F.Page(); orig = app.main
        def broken(p): raise RuntimeError("boom-startup")
        app.main = broken
        try: app.safe_main(page)
        finally: app.main = orig; tmp.cleanup()
        shown = " ".join(F.all_text(c) for c in page.controls)
        self.assertIn("boom-startup", shown)

if __name__ == "__main__": unittest.main()
