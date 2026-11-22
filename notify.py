# -*- coding: utf-8 -*-
"""ارسال اعلان سیستمی (اختیاری و فقط اگر بستهٔ flet-local-notifications را خودت نصب کرده باشی).

نکتهٔ مهم (۴٫۱٫۲): در حالت عادی هیچ بستهٔ اعلانی در برنامه نیست و فقط پیام داخل برنامه نشان داده می‌شود.
بستهٔ بیرونی هرگز هنگام import این ماژول بارگذاری نمی‌شود (قبلاً در لحظهٔ شروع import می‌شد و روی اندروید می‌توانست برنامه را
همان ثانیهٔ اول بکشد)؛ فقط هنگام ساختن Notifier و داخل try/except سخت‌گیرانه بارگذاری می‌شود.
منطق «چه چیزی و کی» در store.reminders_due است؛ اینجا فقط تحویل پیام انجام می‌شود."""
import importlib, importlib.util

def _installed():
    try: return importlib.util.find_spec("flet_local_notifications") is not None
    except Exception: return False

AVAILABLE = _installed()                           # فقط وجود بسته را می‌سنجد؛ کدی از آن اجرا نمی‌شود

class Notifier:
    def __init__(self, page, on_error=None):
        self.page, self.on_error, self.n, self.ready = page, on_error or (lambda *a: None), None, False
        self.cfg = None
        if not AVAILABLE: return
        try:
            mod = importlib.import_module("flet_local_notifications")
            self.cfg = (mod.AndroidNotificationConfig, mod.DesktopNotificationConfig)
            self.n = mod.FletLocalNotification(page); self.ready = True
        except BaseException as ex:                # حتی خطای غیرمعمول هم نباید شروع برنامه را خراب کند
            if isinstance(ex, (KeyboardInterrupt, GeneratorExit)): raise
            self.n, self.ready = None, False
            try: self.on_error("notifier init", ex if isinstance(ex, Exception) else Exception(repr(ex)))
            except Exception: pass

    def send(self, title, body):
        """اعلان سیستمی را همین الان نشان می‌دهد؛ True اگر ارسال شروع شد."""
        if not self.ready: return False
        Android, Desktop = self.cfg
        async def go():
            try:
                await self.n.send(Android(title=title, message=body), Desktop(title=title, message=body, app_name="Get Better"))
            except Exception as ex: self.on_error("notify send", ex)
        try: self.page.run_task(go); return True
        except Exception as ex: self.on_error("notify run_task", ex); return False
