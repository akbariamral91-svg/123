# -*- coding: utf-8 -*-
import os, sys, unittest
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from quickadd import parse

T = date(2026, 11, 16)          # دوشنبه

class TestQuickAdd(unittest.TestCase):
    def test_full_sentence(self):
        q = parse("فردا ساعت ۱۶:۳۰ حل تمرین فیزیک ۴۵ دقیقه مهم", T)
        self.assertEqual((q["title"], q["date"], q["time"], q["minutes"], q["priority"]), ("حل تمرین فیزیک", "2026-11-17", "16:30", 45, 2))
    def test_plain_text_untouched(self):
        q = parse("خرید نان", T); self.assertEqual((q["title"], q["date"], q["time"], q["minutes"], q["priority"]), ("خرید نان", "", "", 0, 1))
    def test_weekday_and_pm_period(self):
        q = parse("جمعه آزمون شیمی ساعت ۴ عصر", T); self.assertEqual((q["title"], q["date"], q["time"]), ("آزمون شیمی", "2026-11-20", "16:00"))
    def test_weekday_is_next_future_not_today(self):
        self.assertEqual(parse("دوشنبه کلاس", T)["date"], "2026-11-23")
    def test_relative_days_and_duration_units(self):
        self.assertEqual(parse("۳ روز دیگه مرور زیست", T)["date"], "2026-11-19")
        self.assertEqual(parse("۲ ساعت ریاضی", T)["minutes"], 120); self.assertEqual(parse("نیم ساعت مطالعه", T)["minutes"], 30)
    def test_hour_word_is_time_not_duration(self):
        q = parse("ساعت ۸ صبح ورزش", T); self.assertEqual((q["time"], q["minutes"], q["title"]), ("08:00", 0, "ورزش"))
    def test_invalid_hour_ignored_and_exclamation_priority(self):
        self.assertEqual(parse("ساعت 25 تست", T)["time"], ""); self.assertEqual(parse("تمرین!", T)["priority"], 2)
    def test_only_keywords_keeps_something_as_title(self):
        self.assertTrue(parse("فردا", T)["title"])

    def test_title_keeps_half_space_and_persian_digits(self):
        """باگ ۴٫۱٫۲: عنوان نیم‌فاصله را حذف می‌کرد («پیام‌های» → «پیامهای») و ارقام فارسی را لاتین می‌کرد."""
        q = parse("مرور پیام\u200cهای آسمانی فردا", T); self.assertEqual((q["title"], q["date"]), ("مرور پیام\u200cهای آسمانی", "2026-11-17"))
        q = parse("حل تمرین ۱۲ ریاضی ساعت ۱۶:۳۰ مهم", T); self.assertEqual((q["title"], q["time"], q["priority"]), ("حل تمرین ۱۲ ریاضی", "16:30", 2))
        self.assertEqual(parse("می\u200cخوانم کتاب ۳", T)["title"], "می\u200cخوانم کتاب ۳")

if __name__ == "__main__": unittest.main()
