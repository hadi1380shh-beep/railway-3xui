# -*- coding: utf-8 -*-
"""ویراستِ تازهٔ «فقه زندگی»: افزودن ۱۵ پرسش به فصل ۱۳ + فصل ۲۱ (ارث، وصیت، سالمندان)

· متنِ کتاب (صفحات ۲ تا ۵۲۲) دست‌نخورده می‌ماند.
· دو بلوکِ تازه با همان موتور رندرِ فصل‌های ۱۸ تا ۲۰ ساخته و به پایانِ فایل افزوده می‌شود.
· شمارۀ صفحاتِ تازه، در ادامهٔ شمارۀ پیشین (۴۶۹ به بعد) درج می‌شود.
· سطرِ «دویست و پنجاه» در جلد به «دویست و هشتاد» تغییر می‌کند (تنها تغییرِ جلد).
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
    # ---- افزونۀ فصل سیزدهم ----
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
           '<div dir="rtl" style="text-align:center;font-size:16px;font-weight:bold;color:#b98a2e">'
           'قلمِ هادی شبستانی</div>')
    b.html(pymupdf.Rect(120, 456, 475, 486),
           '<div dir="rtl" style="text-align:center;font-size:10.5px;color:#5a6b64">'
           'طبعه‌ای خادم در مکتب امام زمان (عج) · ۱۴۵</div>')
    b.html(pymupdf.Rect(120, 489, 475, 512),
           '<div dir="rtl" style="text-align:center;font-size:9.5px;color:#8a8a8a">'
           '«دغدغه نصیب هر کسی نمی‌شود» — شهید بهشتی</div>')


def _page_image_arrays(pix, dpi):
    """آرایۀ سادهٔ روشنایی، برای پیداکردنِ خطِ متن در جلد."""
    W, H, NC = pix.width, pix.height, pix.n
    smp = pix.samples
    def lum(x, y):
        o = (y * W + x) * NC
        return (smp[o] * 30 + smp[o + 1] * 59 + smp[o + 2] * 11) // 100
    return W, H, lum


def _find_line(pix, y_from, y_to, x_from, x_to, thr=120):
    """bboxِ خطِ روشنِ متن (بر حسب پیکسلِ تصویرِ pix) در نوارِ داده‌شده."""
    W, H, lum = _page_image_arrays(pix, None)
    ys, xs = [], []
    for y in range(y_from, y_to):
        hit = [x for x in range(x_from, x_to, 2) if lum(x, y) > thr]
        if hit:
            ys.append(y)
            xs += [x for x in range(x_from, x_to) if lum(x, y) > thr]
    if not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _measure_text(doc_page, needle):
    """bboxِ متنی که همین حالا با insert_htmlbox نوشته‌ایم."""
    for bl in doc_page.get_text("dict")["blocks"]:
        if bl["type"] != 0:
            continue
        for ln in bl["lines"]:
            for sp in ln["spans"]:
                if needle in sp["text"]:
                    return pymupdf.Rect(sp["bbox"])
    return None


def fix_cover(doc, base_path):
    """سطرِ جلد: «دویست و پنجاه» ← «دویست و هشتاد».

    جلد، نگاشتِ تمام‌صفحه است (متن درونِ تصویر است)، پس:
      ۱) صفحۀ جلد با همان رزولیوشن بازمصوَر می‌شود؛
      ۲) نوارِ باریکِ سطرِ هدف، با تکه‌ای از زمینۀ پاکِ بالایِ همان سطر پر می‌شود
         (گرادیان و بافتِ زمینۀ جلد حفظ می‌شود)؛
      ۳) سطرِ تازه با همان قلمِ کتاب، همان رنگِ طلایی و همان اندازۀ خطِ پیشین
         به‌صورتِ متنِ واقعی نوشته می‌شود.
    """
    from PIL import Image
    import io

    NEW_LINE = "پاسخ‌های مستدل و منبری به دویست و هشتاد پرسش روز"
    OLD_MARK = "پاسخ"            # برای سنجشِ جابه‌جاییِ خطِ تازه
    src = pymupdf.open(base_path)
    DPI = 300
    k = DPI / 72.0
    pix = src[0].get_pixmap(dpi=DPI)

    # ── ۱) پیداکردنِ خودکارِ خطِ هدف (سطرِ زیرِ عنوان) ─────────────────
    ln = _find_line(pix, int(430 * k), int(470 * k), int(110 * k), int(490 * k))
    if ln is None:
        print("  ! cover line not found")
        src.close()
        return
    px0, py0, px1, py1 = ln
    band = pymupdf.Rect(px0 / k - 4.5, py0 / k - 4.5, px1 / k + 4.5, py1 / k + 4.5)
    ink_h_pt = (py1 - py0) / k
    ink_w_pt = (px1 - px0) / k
    print("  cover line bbox (pt):", [round(v, 1) for v in band],
          "| ink %.1f x %.1f" % (ink_w_pt, ink_h_pt))

    # ── ۲) پرکردنِ نوار با زمینۀ پاکِ بالای سطر ────────────────────────
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    bx0, bx1 = int(band.x0 * k), int(band.x1 * k)
    by0, by1 = int(band.y0 * k), int(band.y1 * k)
    ay, be = by0 - int(4 * k), by1 + int(4 * k)
    px_ = img.load()
    top_row = [px_[x, ay] for x in range(bx0, bx1)]
    bot_row = [px_[x, be] for x in range(bx0, bx1)]
    n = max(1, by1 - by0)
    for j in range(by0, by1):
        t = (j - by0 + 1) / (n + 1)
        for i, x in enumerate(range(bx0, bx1)):
            a, b = top_row[i], bot_row[i]
            px_[x, j] = (int(a[0] + (b[0] - a[0]) * t),
                         int(a[1] + (b[1] - a[1]) * t),
                         int(a[2] + (b[2] - a[2]) * t))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=94)
    jpg = buf.getvalue()

    # ── ۳)اندازۀ قلم: هم‌سان‌سازیِ پهنای خط با خطِ پیشین ────────────────
    r = src[0].rect
    arch = pymupdf.Archive("/home/user/fonts")
    best = 16.5
    for size in (13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0):
        t = pymupdf.open()
        tp = t.new_page(width=r.width, height=r.height)
        tp.insert_htmlbox(pymupdf.Rect(0, 60, r.width, 120),
                          '<div dir="rtl" style="text-align:center;font-size:%gpx;'
                          'font-weight:bold;color:%s">%s</div>' % (size, GOLD_HEX, NEW_LINE),
                          css=CSS, archive=arch)
        bb = _measure_text(tp, OLD_MARK)
        w = bb.width if bb else 0
        t.close()
        if w and abs(w - ink_w_pt) < abs(best - ink_w_pt):
            pass
        if w:
            best = size
            if w >= ink_w_pt:
                break
    print("  cover font size:", best, "(target width %.1f pt)" % ink_w_pt)

    cov = pymupdf.open()
    pc = cov.new_page(width=r.width, height=r.height)
    pc.insert_image(pymupdf.Rect(0, 0, r.width, r.height), stream=jpg)
    rect = pymupdf.Rect(band.x0 - 20, band.y0 - 1.5, band.x1 + 20, band.y1 + 6)
    pc.insert_htmlbox(rect,
                      '<div dir="rtl" style="text-align:center;font-size:%gpx;font-weight:bold;'
                      'color:%s">%s</div>' % (best, GOLD_HEX, NEW_LINE),
                      css=CSS, archive=arch)
    bb = _measure_text(pc, OLD_MARK)
    if bb:      # تنظیمِ عمودیِ نهایی: مرکزِ خطِ تازه = مرکزِ خطِ پیشین
        want_c = (band.y0 + band.y1) / 2 + 1.5
        dy = want_c - (bb.y0 + bb.y1) / 2
        if abs(dy) > 1.2:
            pc.insert_htmlbox(pymupdf.Rect(rect.x0, rect.y0 + dy, rect.x1, rect.y1 + dy),
                              '<div dir="rtl" style="text-align:center;font-size:%gpx;'
                              'font-weight:bold;color:%s">%s</div>' % (best, GOLD_HEX, NEW_LINE),
                              css=CSS, archive=arch)
    cov[0].get_pixmap(dpi=120).save("/home/user/work/cover_new.png")

    doc.delete_page(0)
    doc.insert_pdf(cov, from_page=0, to_page=0, start_at=0)
    cov.close()
    src.close()
    print("  cover line replaced (page 1)")


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
    print("questions: ۲۵ + ۱۵ (افزونۀ فصل ۱۳) + ۱۵ (فصل ۲۱) = ۲۸۰")


if __name__ == "__main__":
    main()
