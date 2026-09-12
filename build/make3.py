# -*- coding: utf-8 -*-
"""«فقه زندگی» — ۲۸۰ پرسش، چاپِ دومِ این ویراست.

فرقِ این ساخت با ساختارِ پیشین:
· پانزده پرسشِ نوجوانان دیگر به پایانِ فایل افزوده نمی‌شود، بلکه درمیانهٔ خودِ
  فصل سیزدهم (بلافاصله پس از پرسشِ ۱۸۰) می‌نشیند و شماره‌اش ۱۸۱ تا ۱۹۵ است.
· برای همین، شمارهٔ پرسش‌های فصل‌های ۱۴ تا ۲۰ پانزده تا جلو می‌رود (۱۸۱→۱۹۶ … ۲۵۰→۲۶۵)
  و برچسب‌های «ادامۀ پاسخ …» و فهرست پرسش‌های سرِ فصل‌ها هم همان‌قدر جابه‌جا می‌شود.
· شمارۀ چاپیِ صفحاتِ پس از جایِ درج‌شده هم به اندازۀ صفحاتِ تازه جلو می‌رود.
· فهرست پرسش‌های سرِ فصل سیزدهم (صفحۀ ۳۵) با ۲۸ ردیف از نو چیده می‌شود.
· جلد (دو سطر)، فهرست مطالب (ردیف ۲۱)، فصل ۲۱ و صفحۀ پایانی مانند پیش.
"""
import sys
sys.path.insert(0, "/home/user/railway-3xui/build")
import pymupdf
import unicodedata
import re

from render import Book, fa, CSS, L, R, W, H, GOLD, TEAL, GOLD_L
import ch13x, ch21
import make2

BASE = make2.BASE
OUT = "/home/user/railway-3xui/Fiqh_Zendegi_final-1_280.pdf"
HEAD13 = "فصل سیزدهم: پرسشهای نوجوانان (صریح و صمیمی)"     # عینِ سربرگِ خودِ کتاب
Q13_FIRST = 181                                            # نخستین پرسشِ افزوده‌شده به فصل ۱۳
FOLIO13 = 362                                              # شمارۀ چاپیِ نخستین صفحۀ بلوک
SHIFT = 15
TAU = (13 / 255, 79 / 255, 79 / 255)

# ─────────────────────────────  سنجشِ جایِ متن  ─────────────────────────────
_ARCH = pymupdf.Archive("/home/user/fonts")
_cal = {}


def _nfkc(s):
    s = unicodedata.normalize("NFKC", s)
    return "".join(str(unicodedata.digit(c)) if (unicodedata.category(c) == "Nd"
                   and 0x0660 <= ord(c) <= 0x06F9) else c for c in s)


def _box(pix, mode):
    """bboxِ جوهر در تصویرِ pix (mode: 'dark' روی زمینۀ روشن، 'light' روی زمینۀ تیره)."""
    from PIL import Image
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
    if mode == "dark":
        g = im.point(lambda v: 255 if v < 200 else 0)
    else:
        g = im.point(lambda v: 255 if v > 200 else 0)
    return g.getbbox()


def _css_for(weight):
    return ('<div dir="rtl" style="text-align:%s;font-size:%gpx;font-weight:%s;color:%s;'
            'line-height:1">%s</div>')


def probe(align, size, weight, color, text, wide=460.0):
    """جايِ نشستنِ جوهر نسبت به جعبه، برای همين سبکِ نوشتن (يک‌بار اندازه می‌گیرد)."""
    key = (align, round(size, 2), weight, color, text, round(wide))
    if key in _cal:
        return _cal[key]
    t = pymupdf.open()
    p = t.new_page(width=W, height=H)
    ry = 300.0
    # رنگِ متن در اندازه‌گیری فرقی نمی‌کند؛ سیاه می‌نویسیم تا جوهر روی کاغذِ سفید پیدا باشد
    p.insert_htmlbox(pymupdf.Rect(60, ry, 60 + wide, ry + size * 3),
                     _css_for(align) % (align, size, weight, "#111111", text),
                     css=CSS, archive=_ARCH, scale_low=1)
    b = _box(p.get_pixmap(dpi=144, clip=pymupdf.Rect(40, ry - 10, 100 + wide, ry + size * 3 + 12)), "dark")
    t.close()
    k = 2.0                                     # 144dpi = 2 پیکسل بر پوند
    out = (b[1] / k - 10.0, (b[3] - b[1]) / k, b[2] / k + 40.0 - (60 + wide))
    _cal[key] = out
    return out                                  # (افتِ جوهر از بالای جعبه، ارتفاع، رانشِ لبۀ راست)


_boxcal = {}


def _span_cal(size, weight, text, wide):
    """اختلافِ جعبۀ spanِ نو با جعبۀ خواسته (برای همان قلم/اندازه/متن)."""
    key = (round(size, 2), weight, text, round(wide, 1))
    if key in _boxcal:
        return _boxcal[key]
    t = pymupdf.open()
    p = t.new_page(width=W, height=H)
    ry = 300.0
    rect = pymupdf.Rect(60, ry, 60 + wide, ry + size * 3)
    p.insert_htmlbox(rect, _css_for("center") % ("center", size, weight, "#111111", text),
                     css=CSS, archive=_ARCH, scale_low=1)
    sb = None
    for bl in p.get_text("dict")["blocks"]:
        if bl["type"] != 0:
            continue
        for ln in bl["lines"]:
            for sp in ln["spans"]:
                sb = sp["bbox"] if sb is None else [min(sb[0], sp["bbox"][0]), min(sb[1], sp["bbox"][1]),
                                                     max(sb[2], sp["bbox"][2]), max(sb[3], sp["bbox"][3])]
    t.close()
    out = (0.0, 0.0) if sb is None else (sb[1] - ry, (sb[0] + sb[2]) / 2 - (rect.x0 + rect.x1) / 2)
    _boxcal[key] = out
    return out


def place_span(page, want, text, size, weight, color):
    """رقم‌ها را دقیقاً روی جعبۀ قلمِ رقم‌های کهنه می‌نشیناند (وسط‌چین روی مرکزِ کهنه)."""
    x0, y0, x1, y1 = want
    wide = max(60.0, (x1 - x0) * 5)
    dy, dxc = _span_cal(size, weight, text, wide)
    cx = (x0 + x1) / 2 - dxc
    rect = pymupdf.Rect(cx - wide / 2, y0 - dy, cx + wide / 2, y0 - dy + size * 3)
    page.insert_htmlbox(rect, _css_for("center") % ("center", size, weight, color, text),
                        css=CSS, archive=_ARCH, scale_low=1)
    return rect


def place(page, want, text, align, size, weight, color, wide=None, erase=None):
    """مي‌نويسد؛ want = bboxِ متنِ کهنه، تا جُهر دقیقاً همان‌جا بنشیند."""
    x0, y0, x1, y1 = want
    wide = wide or max(120.0, (x1 - x0) * 6)
    dy, _h, dxe = probe(align, size, weight, color, text, wide=wide)
    if align == "center":
        cx = (x0 + x1) / 2
        rect = pymupdf.Rect(cx - wide / 2, y0 - dy, cx + wide / 2, y0 - dy + size * 3)
    else:
        rx1 = x1 - dxe
        rect = pymupdf.Rect(rx1 - wide, y0 - dy, rx1, y0 - dy + size * 3)
    if erase is not None:
        page.add_redact_annot(erase)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                              text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    page.insert_htmlbox(rect, _css_for(align) % (align, size, weight, color, text),
                        css=CSS, archive=_ARCH, scale_low=1)
    return rect


# ─────────────────────────  رندرِ بلوکِ فصل سیزدهم  ─────────────────────────
class Book13(Book):
    """هم‌اندازۀ خودِ صفحاتِ فصل ۱۳: نوارِ کرم پشتِ عنوان، شمارۀ ۱۶پیکسلی، سربرگ و شمارۀ صفحۀ کتاب."""

    def new_page(self, running=None):
        self.page = self.doc.new_page(width=W, height=H)
        self.pageno += 1
        head = self.running if running is None else running
        if head:
            self.html(pymupdf.Rect(L, 14, R, 40),
                      '<div dir="rtl" style="text-align:center;font-size:8.5px;font-weight:500;'
                      'color:#0d4f4f">&#xAB;%s&#xBB;</div>' % head, scale=False)
        self.footer()
        self.y = 59.5
        return self.page

    def html(self, rect, body, css=CSS, scale=True):
        return self.page.insert_htmlbox(rect, body, css=css, archive=self.arch,
                                        scale_low=0.55 if scale else 1)

    def _head_fix(self):
        """سربرگ را ۹٫۲pt پایین‌تر می‌برد (جایِ خودِ کتاب)."""
        p = self.page
        for bl in p.get_text("dict")["blocks"]:
            if bl["type"] != 0:
                continue
            for ln in bl["lines"]:
                for sp in ln["spans"]:
                    if sp["bbox"][1] < 30 and sp["size"] < 10:
                        return pymupdf.Rect(sp["bbox"])
        return None

    def footer(self, num=True):
        p = self.page
        p.insert_htmlbox(pymupdf.Rect(L, 802.4, L + 40, 823),
                         '<div style="font-family:am;font-size:9px;color:#d9b45c">&#xFD3E;&#xFD3F;</div>',
                         css=CSS, archive=self.arch)
        p.insert_htmlbox(pymupdf.Rect(R - 40, 802.4, R, 823),
                         '<div style="text-align:right;font-family:am;font-size:9px;color:#d9b45c">'
                         '&#xFD3E;&#xFD3F;</div>', css=CSS, archive=self.arch)

    def question(self, num, title):
        self.new_page()
        p = self.page
        p.draw_rect(pymupdf.Rect(L, 59.5, R, 100.0), color=None, fill=GOLD_L)
        p.draw_rect(pymupdf.Rect(509.9, 59.5, 541.4, 91.0), color=None, fill=TEAL)
        self.html(pymupdf.Rect(509.9, 65, 541.4, 90),
                  '<div dir="rtl" style="text-align:center;font-size:16px;font-weight:bold;'
                  'color:#fdf8ea">%s</div>' % fa(num), scale=False)
        self.html(pymupdf.Rect(L, 60.4, 502, 99),
                  '<div dir="rtl" style="text-align:end;font-size:14.5px;font-weight:bold;'
                  'color:#0d4f4f;line-height:1.25">%s</div>' % title, scale=False)
        self.y = 110.4


def render_block13():
    b = Book13()
    b.pageno_label = 0
    b.running = HEAD13
    for k, q in enumerate(ch13x.Q):
        num = Q13_FIRST + k
        b.question(num, q["title"])
        for p in q["body"]:
            b.para(p)
        for ar, tr, sr in q["quotes"]:
            b.quote(ar, tr, sr)
        b.menbar(q["menbar"])
    return b.doc


def render_tail(first_folio):
    """فصل ۲۱ و صفحۀ پایانی (همان سبکِ فصل‌های ۱۸ تا ۲۰)."""
    b = Book()
    b.pageno_label = 0
    ch, qs = ch21.CHAPTER, ch21.Q
    items = [(q["num"], q["title"]) for q in qs]
    b.chapter_opener(ch["num"], ch["ordinal"], ch["title"], ch["intro"], items)
    b.running = "فصل بیست‌ویکم: فقه ارث، وصیت و حقوق سالمندان"
    for q in qs:
        b.question(q["num"], q["title"])
        for p in q["body"]:
            b.para(p)
        for ar, tr, sr in q["quotes"]:
            b.quote(ar, tr, sr)
        b.menbar(q["menbar"])
    make2.colophon(b)
    return b.doc


# ─────────────────────────  جابه‌جاییِ شمارۀ پرسش‌ها و صفحه‌ها  ─────────────────────────
BADGE = re.compile(r"^\d{1,3}$")
LABEL = re.compile(r"^ادامۀ پاسخ\s*(\d{1,3})$")
W_FONT = {"Vazirmatn": "normal", "Vazirmatn-Regular": "normal", "Vazirmatn-Medium": "500",
          "Vazirmatn-Semi-Bold": "600", "Vazirmatn-Bold": "bold", "Vazirmatn-SemiBold": "600"}
HEX = lambda c: "#%06x" % c


def _runs(p, dnum, dfolio):
    """هر گروهِ رقمیِ هدف را با کادرِ دقیقِ همان رقم‌ها برمی‌گرداند: [(rect, متن_نو, سبک)]"""
    out = []
    for bl in p.get_text("rawdict")["blocks"]:
        if bl["type"] != 0:
            continue
        for ln in bl["lines"]:
            spans = ln["spans"]
            ltxt = "".join(unicodedata.normalize("NFKC", "".join(c["c"] for c in sp["chars"]))
                           for sp in spans)
            is_label = ("ادام" in ltxt and "پاسخ" in ltxt)          # «ادامۀ پاسخ ۱۹»
            for sp in spans:
                chars = sp["chars"]
                if not chars:
                    continue
                txt = "".join(unicodedata.normalize("NFKC", c["c"]) for c in chars)
                t = txt.strip()
                y0 = sp["bbox"][1]
                whole = bool(re.fullmatch(r"\d{1,3}", t))
                for m in re.finditer(r"\d{1,3}", txt):
                    v = int(m.group())
                    if is_label:
                        if not (181 <= v <= 250):
                            continue
                        rep = _fa(v + dnum)
                    elif whole:
                        if y0 > 786 and 200 <= v <= 500:
                            nv = v + dfolio
                            rep = _fa(nv) if not m.group().isascii() else str(nv)
                        elif y0 < 96 and 14 <= sp["size"] <= 17.5 and 181 <= v <= 250:
                            rep = _fa(v + dnum)
                        elif 250 < y0 < 760 and 10 <= sp["size"] <= 11.5 \
                                and 181 <= v <= 250 and sp["color"] in (0x0D4F4F, 0xD4F4F):
                            rep = _fa(v + dnum)
                        else:
                            continue
                    else:
                        continue
                    cs = chars[m.start():m.end()]
                    out.append((pymupdf.Rect(min(c["bbox"][0] for c in cs), sp["bbox"][1],
                                             max(c["bbox"][2] for c in cs), sp["bbox"][3]),
                                rep, sp))
    return out


def shift_numbers(doc, first_idx, last_idx, dnum, dfolio):
    """شمارۀ پرسش‌ها را dnum و شمارۀ چاپیِ صفحه را dfolio جلو می‌برد.

    تنها خودِ رقم‌ها پاک و از نو نوشته می‌شوند (کادرِ همان رقم‌ها، نه کلِ سطر)، پس هیچ
    واژۀ دیگری از متنِ صفحه نمی‌افتد؛ سبک، قلم، اندازه و رنگ از همان رقم‌های کهنه
    برداشته می‌شود تا دísِ کار درنیاید.
    """
    touched = 0
    for i in range(first_idx, last_idx + 1):
        p = doc[i]
        jobs = _runs(p, dnum, dfolio)
        if not jobs:
            continue
        for r, _rep, _sp in jobs:
            p.add_redact_annot(pymupdf.Rect(r.x0 - 0.5, r.y0 - 0.5, r.x1 + 0.5, r.y1 + 0.5))
        p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                           graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                           text=pymupdf.PDF_REDACT_TEXT_REMOVE)
        for r, rep, sp in jobs:
            place_span(p, (r.x0, r.y0, r.x1, r.y1), rep, round(sp["size"], 2),
                       W_FONT.get(sp["font"], "normal"), HEX(sp["color"]))
        touched += 1
    print("  renumbered pages:", touched)


def _fa(n):
    return "".join("۰۱۲۳۴۵۶۷۸۹"[int(c)] for c in str(n))


def rebuild_ch13_index(doc, new_titles):
    """فهرست پرسش‌های سرِ فصل ۱۳ را با ۲۸ ردیف از نو می‌چیند (۱۶۸ تا ۱۹۵)."""
    p = doc[349]
    old = []
    for bl in p.get_text("dict")["blocks"]:
        if bl["type"] != 0:
            continue
        for ln in bl["lines"]:
            for sp in ln["spans"]:
                y0 = sp["bbox"][1]
                if 344 < y0 < 670:
                    t = _nfkc(sp["text"]).strip()
                    if BADGE.fullmatch(t):
                        old.append(("num", int(t), sp["bbox"]))
                    elif len(t) > 6:
                        old.append(("txt", unicodedata.normalize("NFKC", sp["text"]), sp["bbox"]))
    old.sort(key=lambda r: (round(r[2][1], 1), r[2][0]))
    titles = [t for k, t, _ in old if k == "txt"]
    nums = [n for k, n, _ in old if k == "num"]
    print("  ch13 index: %d old rows, nums %d..%d" % (len(titles), min(nums), max(nums)))
    rows = list(zip(nums, titles)) + [(Q13_FIRST + i, t) for i, t in enumerate(new_titles)]
    top, bottom = 344.0, 782.0
    pitch = (bottom - top) / len(rows)
    p.add_redact_annot(pymupdf.Rect(L, 343.0, R, 672.0))
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                       graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                       text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    size = round(min(10.5, pitch * 0.66), 2)
    for i, (n, t) in enumerate(rows):
        y = top + i * pitch
        place(p, (R - 34, y, R, y + 14), _fa(n), "end", size, "bold", "#0d4f4f", wide=40)
        place(p, (L, y, R - 34, y + 14), unicodedata.normalize("NFKC", t), "end", size,
               "normal", "#262626", wide=R - L - 34)
    print("  ch13 index: %d rows, pitch %.2f, size %g" % (len(rows), pitch, size))


# ─────────────────────────────────  ساخت  ─────────────────────────────────
def main():
    base = pymupdf.open(BASE)
    last = base.page_count - 1
    make2.strip_old_signature(base, last)
    make2.fix_toc(base, ["۲۱. فقه ارث، وصیت و حقوق سالمندان"],
                  replaced={12: "۱۳. پرسش\u200cهای نوجوانان (صریح و صمیمی)"})

    block = render_block13()
    n = block.page_count
    print("block pages:", n)

    shift_numbers(base, 376, last, SHIFT, n)              # صفحات ۳۷۷ تا ۵۲۳
    rebuild_ch13_index(base, [q["title"] for q in ch13x.Q])

    base.insert_pdf(block, start_at=376)
    block.close()
    arch = _ARCH
    for i in range(376, 376 + n):                          # شمارۀ چاپیِ صفحاتِ میانی
        base[i].insert_htmlbox(pymupdf.Rect(250, 802.4, 345, 823),
                               '<div dir="rtl" style="text-align:center;font-size:9px;'
                               'font-weight:600;color:#b98a2e">%d</div>' % (FOLIO13 + (i - 376)),
                               css=CSS, archive=arch)

    tail = render_tail(469 + n)
    tn = tail.page_count
    base.insert_pdf(tail)
    tail.close()
    for i in range(base.page_count - tn, base.page_count):
        base[i].insert_htmlbox(pymupdf.Rect(250, 795, 345, 816),
                               '<div dir="rtl" style="text-align:center;font-size:9px;'
                               'font-weight:600;color:#b98a2e">%d</div>' % (468 + n + 1 + (i - (base.page_count - tn))),
                               css=CSS, archive=arch)

    make2.fix_cover(base, BASE)
    base.set_metadata({"title": "فقه زندگی — دویست‌وهشتاد پرسش در بیست‌ویک فصل",
                       "author": "هادی شبستانی",
                       "subject": "فقه کاربردی، مسائل مستحدثه، ارث و وصیت و حقوق سالمندان"})
    base.save(OUT, garbage=4, deflate=True)
    print("pages:", base.page_count, "->", OUT)


if __name__ == "__main__":
    main()
