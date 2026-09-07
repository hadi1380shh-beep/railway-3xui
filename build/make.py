# -*- coding: utf-8 -*-
"""ساخت نسخهٔ ویراست چهارم کتاب «فقه زندگی» — ۲۵۰ پرسش در ۲۰ فصل."""
import sys, re
sys.path.insert(0, "/home/user/railway-3xui/build")
import pymupdf
from render import Book, fa, CSS, L, R, W, H, GOLD_L
import ch18, ch19, ch20

SRC = "/home/user/railway-3xui/فقه زندگی.pdf"
OUT = "/home/user/railway-3xui/فقه زندگی - ویراست چهارم (۲۵۰ پرسش).pdf"


def build_chapters():
    b = Book()
    b.pageno_label = 0  # شماره‌گذاری در مرحلهٔ ادغام انجام می‌شود
    pages_start = []
    for mod in (ch18, ch19, ch20):
        ch, qs = mod.CHAPTER, mod.Q
        items = [(q["num"], q["title"]) for q in qs]
        b.pageno_label = 0  # شماره‌گذاری در مرحلهٔ ادغام انجام می‌شود
        b.chapter_opener(ch["num"], ch["ordinal"], ch["title"], ch["intro"], items)
        for q in qs:
            b.question(q["num"], q["title"])
            for p in q["body"]:
                b.para(p)
            for ar, tr, sr in q["quotes"]:
                b.quote(ar, tr, sr)
            b.menbar(q["menbar"])
    return b.doc


def main():
    src = pymupdf.open(SRC)
    new = build_chapters()

    out = pymupdf.open()
    out.insert_pdf(src)          # ۴۰۵ صفحهٔ اصلی، دست‌نخورده
    out.insert_pdf(new)          # فصل‌های ۱۸ تا ۲۰

    # --- شماره‌گذاری صفحاتِ بخش جدید، در ادامهٔ کتاب ---
    arch = pymupdf.Archive("/home/user/fonts")
    start = src.page_count
    for i in range(start, out.page_count):
        p = out[i]
        p.insert_htmlbox(pymupdf.Rect(250, 795, 345, 816),
                         '<div style="text-align:center;font-size:9px;font-weight:600;'
                         'color:#b98a2e">%d</div>' % (i + 1),
                         css=CSS, archive=arch)

    # --- اصلاح صفحهٔ پیشگفتار: «دویست و بیست» و «هفده فصل» ---
    fix_preface(out, arch)
    # --- افزودن سه ردیف به فهرست مطالب ---
    fix_toc(out, arch)

    out.set_metadata({"title": "فقه زندگی — ویراست چهارم؛ ۲۵۰ پرسش در ۲۰ فصل",
                      "author": "", "subject": "فقه کاربردی و مسائل مستحدثه"})
    out.save(OUT, garbage=4, deflate=True)
    print("pages:", out.page_count, "->", OUT)


def replace_line(page, marker, old, new, arch, align="justify"):
    """کلّ سطرِ حاوی marker را پاک و با متنِ اصلاح‌شده بازنویسی می‌کند."""
    target = None
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if marker in s["text"]:
                    target = s
    if target is None:
        print("  ! line not found:", marker)
        return False
    x0, y0, x1, y1 = target["bbox"]
    page.add_redact_annot(pymupdf.Rect(L - 2, y0 - 3, R + 2, y1 + 3), fill=None)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    txt = target["text"].replace(old, new)
    page.insert_htmlbox(
        pymupdf.Rect(L, y0 - 5, R, y1 + 8),
        '<div dir="rtl" style="text-align:%s;font-size:11px;line-height:1.56;'
        'color:#262626">%s</div>' % (align, txt),
        css=CSS, archive=arch)
    return True


def fix_preface(doc, arch):
    p = doc[1]
    ok1 = replace_line(p, "هفده فصل", "هفده فصل", "۲۰ فصل", arch, "justify")
    ok2 = replace_line(p, "دویست و بیست", "دویست و بیست", "دویست و پنجاه", arch, "right")
    print("preface:", ok1, ok2)


TOC_ROWS = [
    "طهارت و عبادات در دنیای مدرن",
    "نماز و روزه در شرایط خاص",
    "فقه پزشکی و مسائل مستحدثه",
    "فقه خانواده و روابط",
    "خمس، زکات و اقتصاد اسلامی",
    "بازارهای مالی و معاملات نوین",
    "فقه حکمرانی و اجتماع",
    "اخلاق و تربیت در عصر دیجیتال",
    "ورزش، هنر و ادبیات",
    "سیاست، جنگ و دیپلماسی",
    "کلام قدیم و جدید",
    "مشاوره، تبلیغ و مهارت‌های روحانیت",
    "پرسش‌های نوجوانان (صریح و صمیمی)",
    "احکام بانوان؛ عبادات و احکام اختصاصی",
    "حج، عمره و زیارت در دنیای امروز",
    "فقه تغذیه و صنایع غذایی",
    "مسجد، نماز جمعه و مناسک جمعی",
    "فقه کار، کسب‌وکار و حقوق شغلی",
    "فقه هوش مصنوعی و فناوری‌های نوظهور",
    "فقه سبک زندگی، محیط زیست و مسئولیت اجتماعی",
]


def fix_toc(doc, arch):
    """صفحهٔ فهرست را با هر بیست فصل، در همان سبکِ اصلی بازسازی می‌کند."""
    p = doc[2]
    p.add_redact_annot(pymupdf.Rect(L - 4, 130, R + 4, 792), fill=None)
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)

    top0, bottom = 138.6, 787.0
    h = (bottom - top0) / len(TOC_ROWS)
    for i, t in enumerate(TOC_ROWS):
        top = top0 + i * h
        p.draw_line(pymupdf.Point(L, top), pymupdf.Point(R, top),
                    color=(0.7882, 0.7608, 0.6784), width=0.7)
        p.insert_htmlbox(pymupdf.Rect(L, top + 5, R - 2, top + h + 4),
                         '<div dir="rtl" style="text-align:right;font-size:11px;'
                         'font-weight:500;color:#262626">%s. %s</div>' % (fa(i + 1), t),
                         css=CSS, archive=arch)
    p.draw_line(pymupdf.Point(L, bottom), pymupdf.Point(R, bottom),
                color=(0.7882, 0.7608, 0.6784), width=0.7)


if __name__ == "__main__":
    main()
