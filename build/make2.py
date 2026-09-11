# -*- coding: utf-8 -*-
"""ویراستِ «فقه زندگی» — ۲۸۰ پرسش: پرسش‌های نوجوانان (ادامۀ فصل ۱۳) + فصل ۲۱ (ارث، وصیت، سالمندان)

· متنِ کتاب (صفحات ۲ تا ۵۲۲) دست‌نخورده می‌ماند.
· دو بلوکِ تازه با همان موتور رندرِ فصل‌های ۱۸ تا ۲۰ ساخته و به پایانِ فایل افزوده می‌شود.
· شمارۀ صفحاتِ تازه، در ادامهٔ شمارۀ پیشین (۴۶۹ به بعد) درج می‌شود.
· سطرِ «دویست و پنجاه» در جلد به «دویست و هشتاد» تغییر می‌کند (تنها تغییرِ جلد).
· ردیفِ «۲۱. فقه ارث، وصیت و حقوق سالمندان» به فهرست مطالب افزوده می‌شود.
· یادداشتِ «نویسنده: هادی شبستانی» از صفحۀ آخرِ پیشین برداشته و در صفحۀ آخرِ تازه می‌نشیند.
"""
import sys
sys.path.insert(0, "/home/user/railway-3xui/build")
import pymupdf
from render import Book, fa, CSS, L, R, W, H, GOLD, TEAL
import ch13x, ch21

BASE = "/home/user/railway-3xui/Fiqh_Zendegi_final-1_edited.pdf"
OUT = "/home/user/railway-3xui/Fiqh_Zendegi_final-1_280.pdf"
BG = (12 / 255, 74 / 255, 74 / 255)      # رنگِ زمینهٔ جلد
GOLD_HEX = "#d8b35b"                      # رنگِ متنِ سطرِ زیرِ عنوانِ جلد
LAST_LABEL = 468                          # آخرین شمارۀ چاپیِ فایلِ پایه


def render_new_part():
    b = Book()
    b.pageno_label = 0                     # شمارۀ صفحه در مرحلۀ ادغام درج می‌شود
    # ---- فصل سیزدهم، پرسش200cهای ۲۵۱ تا ۲۶۵ ----
    ch, qs = ch13x.CHAPTER, ch13x.Q
    items = [(q["num"], q["title"]) for q in qs]
    b.chapter_opener(ch["num"], ch["ordinal"], ch["title"], ch["intro"], items)
    b.running = "فصل سیزدهم: پرسش‌های نوجوانان (صریح و صمیمی)"
    for q in qs:
        b.question(q["num"], q["title"])
        for p in q["body"]:
            b.para(p)
        for ar, tr, sr in q["quotes"]:
            b.quote(ar, tr, sr)
        b.menbar(q["menbar"])
    # ---- فصل بیست‌ویکم ----
    ch, qs = ch21.CHAPTER, ch21.Q
    items = [(q["num"], q["title"]) for q in qs]
    b.pageno_label = 0
    b.chapter_opener(ch["num"], ch["ordinal"], ch["title"], ch["intro"], items)
    b.running = "فصل بیست‌ویکم: فقه ارث، وصیت و حقوق سالمندان"
    for q in qs:
        b.question(q["num"], q["title"])
        for p in q["body"]:
            b.para(p)
        for ar, tr, sr in q["quotes"]:
            b.quote(ar, tr, sr)
        b.menbar(q["menbar"])
    colophon(b)
    return b.doc


def colophon(b):
    """صفحۀ پایانی: نامِ نویسنده."""
    b.new_page(running="")
    p = b.page
    p.draw_rect(pymupdf.Rect(120, 300, 475, 520), color=None, fill=(0.9490, 0.9647, 0.9608))
    p.draw_rect(pymupdf.Rect(120, 300, 475, 305), color=None, fill=GOLD)
    p.draw_rect(pymupdf.Rect(120, 515, 475, 520), color=None, fill=GOLD)
    b.html(pymupdf.Rect(120, 322, 475, 356),
           '<div dir="rtl" style="text-align:center;font-size:19px;font-weight:bold;'
           'color:#0d4f4f">فقه زندگی</div>')
    b.html(pymupdf.Rect(120, 358, 475, 382),
           '<div dir="rtl" style="text-align:center;font-size:11.5px;line-height:1.9;color:#5a6b64">'
           'دویست‌وهشتاد پرسشِ پاسخ‌داده‌شده در بیست‌ویک فصل</div>')
    p.draw_line(pymupdf.Point(230, 400), pymupdf.Point(283, 400), color=(0.7882, 0.7608, 0.6784), width=0.8)
    p.draw_line(pymupdf.Point(312, 400), pymupdf.Point(365, 400), color=(0.7882, 0.7608, 0.6784), width=0.8)
    p.draw_rect(pymupdf.Rect(294, 396.5, 301.5, 403.5), color=None, fill=GOLD)
    b.html(pymupdf.Rect(120, 414, 475, 452),
           '<div dir="rtl" style="text-align:center;font-size:18px;font-weight:bold;color:#b98a2e">'
           'نویسنده: هادی شبستانی</div>')
    b.html(pymupdf.Rect(120, 458, 475, 486),
           '<div dir="rtl" style="text-align:center;font-size:11px;color:#5a6b64">'
           'طبعه‌ای خادم در مکتب امام زمان (عج)</div>')
    b.html(pymupdf.Rect(120, 489, 475, 512),
           '<div dir="rtl" style="text-align:center;font-size:9.5px;color:#8a8a8a">'
           '«دغدغه نصیب هر کسی نمی‌شود» — شهید بهشتی</div>')


# ───────────────────────────────  جلد (صفحۀ ۱)  ───────────────────────────────
DPI = 300                                 # ریزنقشِ بازمصوَرِ جلد
PD = 200                                  # ریزنقشِ سنجشِ متنِ آزمایشی
COVER_JOBS = [
    dict(y0=425, y1=472,
         old="پاسخ\u200cهای مستدل و منبری به دویست و پنجاه پرسش روز",
         new="پاسخ\u200cهای مستدل و منبری به دویست و هشتاد پرسش روز"),
    dict(y0=472, y1=497, old="در بیست فصل", new="در بیست\u200cویک فصل"),
]


def _ink_light(pix, xa, xb, ya, yb, thr=110):
    """bbox و رنگِ میانگینِ جوهرِ روشن (متنِ طلاییِ جلد) روی زمینۀ تیره."""
    smp, W, H, n = pix.samples, pix.width, pix.height, pix.n
    xs, ys, cols = [], [], []
    for y in range(max(0, ya), min(H, yb)):
        for x in range(max(0, xa), min(W, xb)):
            o = (y * W + x) * n
            if (smp[o] * 30 + smp[o + 1] * 59 + smp[o + 2] * 11) // 100 > thr:
                xs.append(x); ys.append(y); cols.append((smp[o], smp[o + 1], smp[o + 2]))
    if not xs:
        return None
    cols.sort(key=lambda c: -(c[0] + c[1] + c[2]))
    m = max(1, len(cols) * 3 // 10)
    col = tuple(sum(c[i] for c in cols[:m]) // m for i in range(3))
    return min(xs), min(ys), max(xs), max(ys), col


def _ink_dark(pix, thr=235):
    from PIL import Image
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
    return im.point(lambda v: 255 if v < thr else 0).getbbox()


def _probe(text, size, color, arch, cx, rect_top=100.0, rect_h=80.0):
    """پهنا و جایِ جوهرِ یک سطر، در همان هندسۀ نشاندن روی جلد."""
    k = PD / 72.0
    t = pymupdf.open()
    p = t.new_page(width=W, height=300)
    p.insert_htmlbox(pymupdf.Rect(cx - 260, rect_top, cx + 260, rect_top + rect_h),
                     '<div dir="rtl" style="text-align:center;font-size:%gpx;font-weight:bold;'
                     'color:#%02x%02x%02x">%s</div>' % (size, color[0], color[1], color[2], text),
                     css=CSS, archive=arch, scale_low=1)
    bb = _ink_dark(p.get_pixmap(dpi=PD, clip=pymupdf.Rect(0, rect_top, W, rect_top + rect_h)))
    t.close()
    if not bb:
        return None
    return ((bb[2] - bb[0]) / k, (bb[3] - bb[1]) / k, (bb[1] + bb[3]) / 2 / k)


def _fit_size(text, color, arch, want_w, cx):
    """اندازۀ قلمی که پهناى همۀ سطرِ پیشین را می‌دهد."""
    best, bw, bo = 12.0, 0.0, 0.0
    s = 6.0
    while s <= 30.0:
        r = _probe(text, s, color, arch, cx)
        if r and abs(r[0] - want_w) < abs(bw - want_w):
            best, bw, bo = s, r[0], r[2]
        s += 0.5
    return best, bw, bo


def fix_cover(doc, base_path):
    """دو سطرِ زیرِ عنوانِ جلد: «دویست و پنجاه»←«دویست و هشتاد»، «بیست فصل»←«بیست‌ویک فصل».

    جلد نگاشتِ تمام‌صفحۀ تصویر است (متن درونِ تصویر است)، پس هر سطر:
      ۱) با بازمصوَرِ ۳۰۰dpi پیدا می‌شود؛ ۲) نواری به بلندیِ همان سطر با درون‌یابیِ
      ستونیِ زمینۀ پاکِ بالا و پایین پر می‌شود (بافت و گرادیان حفظ می‌شود)؛
      ۳) سطرِ تازه با همان قلمِ کتاب، همان رنگِ اندازه‌گیری‌شده و همان اندازۀ سطرِ پیشین
      (که با آزمونِ پهنا کالیبره شده) به‌صورتِ متنِ واقعی نوشته می‌شود.
    """
    from PIL import Image
    import io

    src = pymupdf.open(base_path)
    arch = pymupdf.Archive("/home/user/fonts")
    k = DPI / 72.0
    pix = src[0].get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGB")
    px = img.load()
    r = src[0].rect
    jobs = []
    for jb in COVER_JOBS:
        bb = _ink_light(pix, int(80 * k), int(515 * k), int(jb["y0"] * k), int(jb["y1"] * k))
        if not bb:
            print("  ! cover line not found:", jb["new"])
            continue
        x0, y0, x1, y1, col = bb
        cx, cy = (x0 + x1) / 2 / k, (y0 + y1) / 2 / k
        size, got, _off = _fit_size(jb["old"], col, arch, (x1 - x0) / k, cx)
        pr = _probe(jb["new"], size, col, arch, cx)
        print("  cover: '%s'→'%s'  size %.1fpx  ink %.1f→%.1f pt  colour #%02x%02x%02x"
              % (jb["old"][:12], jb["new"][:12], size, (x1 - x0) / k, pr[0], col[0], col[1], col[2]))
        bx0, bx1 = max(0, x0 - int(5 * k)), min(img.width - 1, x1 + int(5 * k))
        by0, by1 = max(0, y0 - int(4 * k)), min(img.height - 1, y1 + int(4 * k))
        top = [px[x, max(0, by0 - int(3 * k))] for x in range(bx0, bx1)]
        bot = [px[x, min(img.height - 1, by1 + int(3 * k))] for x in range(bx0, bx1)]
        n = max(1, by1 - by0)
        for j in range(by0, by1):
            t = (j - by0 + 1) / (n + 1)
            for i, x in enumerate(range(bx0, bx1)):
                a, b = top[i], bot[i]
                px[x, j] = tuple(int(a[c] + (b[c] - a[c]) * t) for c in range(3))
        jobs.append((cx, cy, size, col, jb["new"], pr[2]))
    src.close()

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    cov = pymupdf.open()
    pc = cov.new_page(width=r.width, height=r.height)
    pc.insert_image(pymupdf.Rect(0, 0, r.width, r.height), stream=buf.getvalue())
    for cx, cy, size, col, text, off in jobs:
        top = cy - off
        pc.insert_htmlbox(pymupdf.Rect(cx - 260, top, cx + 260, top + 80),
                          '<div dir="rtl" style="text-align:center;font-size:%gpx;font-weight:bold;'
                          'color:#%02x%02x%02x">%s</div>' % (size, col[0], col[1], col[2], text),
                          css=CSS, archive=arch, scale_low=1)
    cov[0].get_pixmap(dpi=200, clip=pymupdf.Rect(80, 380, 520, 520)).save("/home/user/work/cover_new.png")
    doc.delete_page(0)
    doc.insert_pdf(cov, from_page=0, to_page=0, start_at=0)
    cov.close()
    print("  cover: %d line(s) replaced (page 1)" % len(jobs))


# ───────────────────────────────  فهرست مطالب (صفحۀ ۳)  ──────────────────────────────
ROWS_TOP, ROWS_BOT = 138.6, 787.0        # خطِ نخست و خطِ آخرِ فهرست
IMG_IN, STRIP_W, STRIP_H = 1.6, 495.0, 25.0
DPR = 4                                 # پیکسل بر پوند (288dpi) — همان اندازۀ سطرهای خودِ کتاب
ROW_XREF0 = 75                          # xrefِ تصویرِ سطرِ نخست؛ سطرهای بعدی دو‌دو


def _row_png(doc, xref):
    """تصویرِ خودِ سطر را (با شفافیتِ اصلی‌اش) برمی‌دارد تا بی‌کم‌وکاست جا به جا شود."""
    base = pymupdf.Pixmap(doc, xref)
    if base.alpha:
        base = pymupdf.Pixmap(base, 0)
    s = doc.xref_get_key(xref, "SMask")
    if s[0] == "xref":
        m = pymupdf.Pixmap(doc, int(s[1].split()[0]))
        if m.alpha:
            m = pymupdf.Pixmap(m, 0)
        if (m.width, m.height) != (base.width, base.height):
            from PIL import Image
            g = Image.frombytes("L", (m.width, m.height), m.samples).resize((base.width, base.height))
            m = pymupdf.Pixmap(pymupdf.csGRAY, base.width, base.height, g.tobytes())
        base = pymupdf.Pixmap(base, m)
    return base.tobytes("png")


def _new_row_png(text, ink_top=7.6):
    """سطرِ تازه، با همان قلم/قطر/رنگِ سطرهای کتاب، روی نوارِ ۱۹۸۰×۱۰۰ پیکسلی."""
    from PIL import Image
    import io
    arch = pymupdf.Archive("/home/user/fonts")
    t = pymupdf.open()
    p = t.new_page(width=W, height=H)
    p.insert_htmlbox(pymupdf.Rect(L, 150, R, 200),
                     '<div dir="rtl" style="text-align:end;font-size:12px;font-weight:bold;'
                     'color:#2b2b2b">%s</div>' % text, css=CSS, archive=arch, scale_low=1)
    pix = p.get_pixmap(dpi=72 * DPR)
    t.close()
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    bb = im.convert("L").point(lambda v: 255 if v < 200 else 0).getbbox()
    ox = int(round(bb[2] - 1962))          # لبۀ راستِ متن، هم‌جای سطرهای دیگر
    oy = int(round(bb[1] - ink_top * DPR))
    cv = Image.new("RGB", (int(STRIP_W * DPR), int(STRIP_H * DPR)), (255, 255, 255))
    cv.paste(im, (-ox, -oy))
    buf = io.BytesIO()
    cv.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def fix_toc(doc, new_rows, replaced=None):
    """ردیف‌های فهرست مطالب را دست‌نخورده نگه می‌دارد و ردیف‌های نو را به پایان می‌افزاید.

    هر سطرِ فهرست در فایلِ پایه یک نوارِ تصویری است (نه متن)، پس همان تصویرِ خودِ
    سطر برداشته و با گامِ فشرده‌تر نشسته می‌شود؛ ردیف‌های نو — و ردیفِ سیزدهمی که در
    فایلِ پایه جابه‌جاییِ حروف داشت — با همان قلم و اندازۀ کتاب از نو ساخته می‌شوند.
    """
    p = doc[2]
    n = 20 + len(new_rows)
    pitch = (ROWS_BOT - ROWS_TOP) / n
    replaced = replaced or {}
    strips = [_new_row_png(replaced[i]) if i in replaced
              else _row_png(doc, ROW_XREF0 + 2 * i) for i in range(20)]
    strips += [_new_row_png(t) for t in new_rows]

    p.add_redact_annot(pymupdf.Rect(49.0, ROWS_TOP - 0.9, 546.0, ROWS_BOT + 0.9))
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                       graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                       text=pymupdf.PDF_REDACT_TEXT_NONE)

    for i, png in enumerate(strips):
        y0 = ROWS_TOP + i * pitch + IMG_IN
        p.insert_image(pymupdf.Rect(50.0, y0, 50.0 + STRIP_W, y0 + STRIP_H), stream=png)
    for i in range(n + 1):
        y = ROWS_TOP + i * pitch
        p.draw_line(pymupdf.Point(L, y), pymupdf.Point(R, y),
                    color=(0.7882, 0.7608, 0.6784), width=0.7)
    print("  toc: %d rows (pitch %.2f pt)" % (n, pitch))


def strip_old_signature(doc, last_idx):
    """یادداشتِ «نویسنده…」 را از صفحۀ آخرِ پیشین (که اکنون میانی است) برمی‌داریم.

    متنِ آن دو سطر با «حروفِ جدا»ی عربی (presentation forms) کدگذاری شده، پس
    مقایسه پس از NFKC انجام می‌شود.
    """
    p = doc[last_idx]
    band = None
    # ۱) کادرِ کشیده‌شدهٔ یادداشت
    for dr in p.get_drawings():
        r = dr["rect"]
        if r.y0 > 600 and r.y1 < 790:
            band = pymupdf.Rect(r) if band is None else (band | r)
    # ۲) هر متنی که در همان نوار است
    for bl in p.get_text("dict")["blocks"]:
        if bl["type"] != 0:
            continue
        for ln in bl["lines"]:
            for sp in ln["spans"]:
                x0, y0, x1, y1 = sp["bbox"]
                if 660 <= y0 <= 760:
                    band = pymupdf.Rect(x0, y0, x1, y1) if band is None else (band | pymupdf.Rect(x0, y0, x1, y1))
    if band is None:
        print("  ! no old signature found on page", last_idx + 1)
        return
    band = pymupdf.Rect(max(0, band.x0 - 3), max(0, band.y0 - 3),
                        min(W, band.x1 + 3), min(790, band.y1 + 3))
    p.add_redact_annot(band, fill=None)
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                       graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                       text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    print("  old signature removed from page %d at %s" % (last_idx + 1, [round(v, 1) for v in band]))


def main():
    base = pymupdf.open(BASE)
    n_old = base.page_count
    print("base pages:", n_old)

    strip_old_signature(base, n_old - 1)

    # ردیفِ فصل بیست‌ویکم به فهرست مطالب افزوده می‌شود
    fix_toc(base, ["۲۱. فقه ارث، وصیت و حقوق سالمندان"],
            replaced={12: "۱۳. پرسش\u200cهای نوجوانان (صریح و صمیمی)"})

    new = render_new_part()
    print("new pages:", new.page_count)
    base.insert_pdf(new)
    new.close()

    # شمارۀ صفحاتِ تازه، در ادامهٔ شمارۀ چاپیِ پیشین
    arch = pymupdf.Archive("/home/user/fonts")
    first_new = n_old
    for i in range(first_new, base.page_count):
        base[i].insert_htmlbox(pymupdf.Rect(250, 795, 345, 816),
                               '<div style="text-align:center;font-size:9px;font-weight:600;'
                               'color:#b98a2e">%d</div>' % (LAST_LABEL + 1 + (i - first_new)),
                               css=CSS, archive=arch)

    fix_cover(base, BASE)

    base.set_metadata({"title": "فقه زندگی — دویست‌وهشتاد پرسش در بیست‌ویک فصل",
                       "author": "هادی شبستانی",
                       "subject": "فقه کاربردی، مسائل مستحدثه، ارث و وصیت و حقوق سالمندان"})
    base.save(OUT, garbage=4, deflate=True)
    print("pages:", base.page_count, "->", OUT)
    print("questions: ۲۶۵ پرسشِ نوجوان + ۱۵ پرسشِ فصل ۲۱ = ۲۸۰")


if __name__ == "__main__":
    main()
