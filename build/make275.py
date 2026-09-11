# -*- coding: utf-8 -*-
"""ویراست نهایی «فقه زندگی» — ۲۹۰ پرسش در ۲۱ فصل.

- درج ۲۰ پرسشِ تازهٔ فصل سیزدهم (۲۵۱–۲۷۰) در ادامهٔ همان فصل
- افزودن فصل بیست و یکم «فقه ارث، وصیت، حقوق سالمندان» (۲۷۱–۲۹۰) در پایان کتاب
- شماره‌گذاری پیوستهٔ صفحات + اصلاح پیشگفتار + جلد به‌روزشده (۲۹۰ / ۲۱ فصل)
"""
import sys, re
sys.path.insert(0, "/home/user/railway-3xui/build")
sys.path.insert(0, "/home/user/work")
import pymupdf
from render import Book, fa, CSS, L, R, W, H, GOLD_L, GOLD, TEAL
import ch13new_a, ch13new_b, ch13new_c, ch13new_d
import ch21_a, ch21_b, ch21_c, ch21_d

SRC = "/home/user/railway-3xui/Fiqh_Zendegi_final-1.pdf"
OUT = "/home/user/railway-3xui/Fiqh_Zendegi_final-1_edited.pdf"
COVER = "/home/user/work/cover/final_cover_275_4x.png"

CH13_RUNNING = "فصل سیزدهم: پرسش‌های نوجوانان (صریح و صمیمی)"
CH21 = dict(num=21, ordinal="بیست و یکم",
            title="فقه ارث، وصیت، حقوق سالمندان",
            intro=("این فصل، باب تازه‌ای از کتاب است و به سه موضوع مهم و پرمبتلای زندگی هر خانواده می‌پردازد: "
                   "احکام ارث و تقسیم ترکه؛ وصیت و تنظیم اموال پیش از مرگ؛ و حقوق سالمندان. هدف آن است که خواننده "
                   "با ترتیبِ شرعیِ پرداخت دیون و مهریه و سهام، قاعده‌های تقسیم ارث میان طبقات وارثان، حدود اختیار "
                   "انسان در وصیت، و نیز تکلیف بازماندگان نسبت به پدر و مادرِ پیر، همسرِ داغ‌دیده و فرزندانِ صغیر "
                   "آشنا شود؛ تا هم حقِ شرعی هر کس به‌دقت ادا گردد و هم کانون خانواده از نزاع‌های مالی در امان بماند. "
                   "در پایان هر پاسخ، «سخن منبری»ای آمده است تا مبلّغ گرامی بتواند همین معارف را با زبان خطابه "
                   "به مردم برساند."))

ITEMS_21 = [
    "ترتیب ترکه: تجهیز، دیون، وصیت و سپس ارث",
    "طبقات وارثان و قاعدهٔ طبقهٔ نزدیک‌تر",
    "ارث همسر، والدین و فرزند در کنار هم",
    "چرا سهم پسر دو برابر دختر است؟",
    "روش محاسبهٔ سهم فرزندان؛ پسر دو برابر دختر",
    "سرنوشت سهم وارثی که پیش از تقسیم فوت می‌کند",
    "ارث کودکان صغیر و مدیریت اموال آنان",
    "وقتی ترکه کفاف بدهی‌ها را نمی‌دهد",
    "مهریهٔ پرداخت‌نشده و اولویت آن بر تقسیم ارث",
    "آیا می‌توان با وصیت، وارثی را محروم کرد؟",
    "حدود اختیار در وصیت و حکم وصیت بیش از ثلث",
    "وصیت‌نامهٔ مخالف احکام ارث؛ چه بخشی معتبر است؟",
    "بخشش به یکی از فرزندان در زمان حیات",
    "ملک مشترک و مخالفت یکی از ورثه با فروش",
    "تصرف در اموال مشترک متوفی بدون اجازه",
    "سرنوشت روح پس از مرگ و عالم برزخ",
    "ارث اموال دیجیتال و رمزارزها",
    "انصاف و رضایت در تقسیم ارث و اجرای وصیت",
    "حقوق همسر، فرزندان صغیر و والدینِ متوفی",
    "تنظیم شرعی و عادلانهٔ اموال پیش از مرگ",
]


def build_supplement():
    """پرسش‌های ۲۵۱–۲۷۰ در ادامهٔ فصل سیزدهم."""
    b = Book()
    b.running = CH13_RUNNING
    qs = ch13new_a.Q + ch13new_b.Q + ch13new_c.Q + ch13new_d.Q
    for q in qs:
        b.question(q["num"], q["title"])
        for p in q["body"]:
            b.para(p)
        for ar, tr, sr in q["quotes"]:
            b.quote(ar, tr, sr)
        b.menbar(q["menbar"])
    return b.doc


def chapter21_opener(b, items):
    """صفحهٔ افتتاح فصل ۲۱ با فهرست دوستونهٔ ۲۰ پرسش."""
    ch = CH21
    b.running = "فصل %s: %s" % (ch["ordinal"], ch["title"])
    b.new_page(running="")
    p = b.page
    p.draw_rect(pymupdf.Rect(273.6, 93.5, 321.6, 141.5), color=GOLD, width=1.4)
    b.html(pymupdf.Rect(273.6, 100, 321.6, 140),
           '<div dir="rtl" style="text-align:center;font-size:26px;font-weight:bold;'
           'color:#b98a2e">%s</div>' % fa(ch["num"]))
    b.html(pymupdf.Rect(L, 152, R, 200),
           '<div dir="rtl" style="text-align:center;font-size:20px;font-weight:bold;'
           'color:#0d4f4f">فصل %s: %s</div>' % (ch["ordinal"], ch["title"]))
    p.draw_line(pymupdf.Point(226, 206.5), pymupdf.Point(283, 206.5), color=(0, 0, 0), width=0.65)
    p.draw_line(pymupdf.Point(312, 206.5), pymupdf.Point(369, 206.5), color=(0, 0, 0), width=0.65)
    p.draw_rect(pymupdf.Rect(292.5, 202, 302.8, 211.1), color=None, fill=(0, 0, 0))
    p.draw_rect(pymupdf.Rect(287.3, 205.2, 289.9, 207.8), color=None, fill=(0, 0, 0))
    p.draw_rect(pymupdf.Rect(305.4, 205.2, 308.0, 207.8), color=None, fill=(0, 0, 0))
    b.html(pymupdf.Rect(96, 218, R - 42, 305),
           '<div dir="rtl" style="text-align:justify;font-size:11px;line-height:2.05;'
           'color:#6b7771">%s</div>' % ch["intro"])
    b.html(pymupdf.Rect(L, 310, R, 334),
           '<div dir="rtl" style="text-align:right;font-size:12.5px;font-weight:bold;'
           'color:#b98a2e">فهرست پرسش‌های این فصل</div>')
    p.draw_line(pymupdf.Point(L, 345.5), pymupdf.Point(R, 345.5), color=GOLD_L, width=0.8)
    half = (R - L) / 2.0
    mid = L + half
    y = 350
    step = 41.5
    for i, t in enumerate(items):
        n = 271 + i
        if i < 10:  # ستون راست
            t_rect = pymupdf.Rect(mid + 8, y, R - 34, y + 40)
            n_rect = pymupdf.Rect(R - 30, y, R, y + 22)
        else:       # ستون چپ
            t_rect = pymupdf.Rect(L, y, mid - 8, y + 40)
            n_rect = pymupdf.Rect(mid - 30, y, mid, y + 22)
            if i == 10:
                y = 350
        b.html(t_rect,
               '<div dir="rtl" style="text-align:right;font-size:10.5px;line-height:1.9;'
               'color:#26262f">%s</div>' % t)
        b.html(n_rect,
               '<div dir="rtl" style="text-align:left;font-size:10.5px;font-weight:bold;'
               'color:#0d4f4f">%s</div>' % fa(n))
        y += step


def build_ch21():
    b = Book()
    chapter21_opener(b, ITEMS_21)
    qs = ch21_a.Q + ch21_b.Q + ch21_c.Q + ch21_d.Q
    for q in qs:
        b.question(q["num"], q["title"])
        for p in q["body"]:
            b.para(p)
        for ar, tr, sr in q["quotes"]:
            b.quote(ar, tr, sr)
        b.menbar(q["menbar"])
    return b.doc


def stamp_number(page, num, rect):
    page.insert_htmlbox(rect,
                        '<div style="text-align:center;font-size:9px;font-weight:600;'
                        'color:#b98a2e">%d</div>' % num,
                        css=CSS, archive=ARCH)


def shift_footer_numbers(doc, start_idx, delta, end_idx):
    """شمارهٔ پایین صفحه‌های اصلیِ بعد از محل درج را delta واحد جلو می‌برد."""
    done = 0
    for i in range(start_idx, end_idx):
        p = doc[i]
        span = None
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    t = s["text"].strip()
                    if t.isdigit() and s["bbox"][1] > 790 and s["size"] < 10.5:
                        span = s
        if span is None:
            continue
        newnum = int(span["text"]) + delta
        x0, y0, x1, y1 = span["bbox"]
        p.add_redact_annot(pymupdf.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=None)
        p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
        weight = ("bold" if "Bold" in span["font"]
                  else ("600" if "Semi" in span["font"]
                        else ("500" if "Medium" in span["font"] else "normal")))
        color = "#%06x" % span["color"]
        p.insert_htmlbox(pymupdf.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2),
                         '<div style="text-align:center;font-size:9px;font-weight:%s;'
                         'color:%s">%d</div>' % (weight, color, newnum),
                         css=CSS, archive=ARCH)
        done += 1
    return done


def fix_preface(doc):
    p = doc[1]
    targets = []
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"]
                if "صد و" in t and "هشتاد" not in t and "پرسش" not in t:
                    targets.append(("line1", s))
                elif "هشتاد پرسش" in t:
                    targets.append(("line2", s))
                elif t.strip() == "۲۰" and s["bbox"][1] > 225:
                    targets.append(("toc20", s))

    # ۱) متن کامل دو سطر، پیش از پاک‌سازی (از راست به چپ)
    allspans = []
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if 175 < s["bbox"][1] < 230:
                    allspans.append(s)
    line1 = line2 = None
    y1s = y2s = None
    for kind, s in targets:
        if kind == "line1":
            y1s = s["bbox"][1]
        elif kind == "line2":
            y2s = s["bbox"][1]
    for yref, key in ((y1s, "line1"), (y2s, "line2")):
        if yref is None:
            continue
        same = [s for s in allspans if abs(s["bbox"][1] - yref) < 4]
        same.sort(key=lambda s: -s["bbox"][0])   # راست به چپ
        txt = "".join(s["text"] for s in same)
        if key == "line1":
            line1 = txt.replace("به صد و", "به دویست")
        else:
            line2 = txt.replace("هشتاد", "و نود")

    # ۲) پاک‌سازی
    for kind, s in targets:
        x0, y0, x1, y1 = s["bbox"]
        if kind == "toc20":
            p.add_redact_annot(pymupdf.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=None)
        else:
            p.add_redact_annot(pymupdf.Rect(L - 2, y0 - 3, R + 2, y1 + 3), fill=None)
        p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)

    # ۳) بازنویسی
    style = ('<div dir="rtl" style="text-align:justify;font-size:11px;line-height:1.56;'
             'color:#262626">')
    for kind, s in targets:
        x0, y0, x1, y1 = s["bbox"]
        if kind == "toc20":
            p.insert_htmlbox(pymupdf.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2),
                             '<div style="text-align:center;font-size:11px;color:#262626">۲۱</div>',
                             css=CSS, archive=ARCH)
    if line1 and line2:
        p.insert_htmlbox(pymupdf.Rect(L, y1s - 4, R, y1s + 19), style + line1 + "</div>",
                         css=CSS, archive=ARCH)
        p.insert_htmlbox(pymupdf.Rect(L, y2s - 4, R, y2s + 19), style + line2 + "</div>",
                         css=CSS, archive=ARCH)
    return len(targets)


ARCH = pymupdf.Archive("/home/user/fonts")


def main():
    src = pymupdf.open(SRC)
    supp = build_supplement()
    ch21 = build_ch21()
    N = supp.page_count
    len_ch21 = ch21.page_count

    out = pymupdf.open()
    out.insert_pdf(src)
    out.insert_pdf(supp, start_at=376)   # بعد از صفحهٔ ۳۷۶ (پایان فصل ۱۳)
    out.insert_pdf(ch21)                  # فصل ۲۱ در پایان کتاب

    # شمارهٔ صفحات بخشِ الحاقی (ادامهٔ شمارهٔ ۳۶۱ِ صفحهٔ پایانی فصل ۱۳)
    for i in range(376, 376 + N):
        stamp_number(out[i], i - 376 + 362, pymupdf.Rect(250, 795, 345, 816))

    # جابه‌جایی شمارهٔ صفحات اصلیِ پس از درج
    done = shift_footer_numbers(out, 376 + N, N, 523 + N)

    # شمارهٔ صفحات فصل ۲۱ (ادامهٔ آخرین شمارهٔ اصلی = ۴۶۸)
    base = 468 + N
    start = 523 + N
    for i in range(start, start + len_ch21):
        stamp_number(out[i], base + (i - start) + 1, pymupdf.Rect(250, 795, 345, 816))

    # اصلاح پیشگفتار
    n = fix_preface(out)

    # جلد به‌روز
    out.delete_page(0)
    cov = out.new_page(pno=0, width=595.2756, height=841.8898)
    cov.insert_image(pymupdf.Rect(0, 0, 595.2756, 841.8898), filename=COVER)

    out.set_metadata({"title": "فقه زندگی — ۲۹۰ پرسش در ۲۱ فصل",
                      "author": "", "subject": "فقه کاربردی و مسائل مستحدثه"})
    out.save(OUT, garbage=4, deflate=True)
    print("supplement pages:", N, " ch21 pages:", len_ch21,
          " shifted:", done, " preface fixes:", n)
    print("pages:", out.page_count, "->", OUT)


if __name__ == "__main__":
    main()
