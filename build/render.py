# -*- coding: utf-8 -*-
"""موتور رندر فصل‌های جدید کتاب «فقه زندگی» — منطبق بر سبک اصلی."""
import pymupdf

FONTS = "/home/user/fonts"
W, H = 595.2756, 841.8898
L, R = 53.8583, 541.4174          # margins
TEAL = (0.0509, 0.3098, 0.3098)   # #0d4f4f
GOLD = (0.7255, 0.5412, 0.1804)   # #b98a2e
GOLD_L = (0.8510, 0.7059, 0.3608)
BOXBG = (0.9490, 0.9647, 0.9608)
MENBG = (0.9804, 0.9647, 0.9255)
FA = "۰۱۲۳۴۵۶۷۸۹"


def fa(n):
    return "".join(FA[int(c)] for c in str(n))


CSS = """
@font-face{font-family:vz;src:url(Vazirmatn-Regular.ttf);}
@font-face{font-family:vz;font-weight:500;src:url(Vazirmatn-Medium.ttf);}
@font-face{font-family:vz;font-weight:600;src:url(Vazirmatn-SemiBold.ttf);}
@font-face{font-family:vz;font-weight:bold;src:url(Vazirmatn-Bold.ttf);}
@font-face{font-family:am;src:url(Amiri-Regular.ttf);}
*{font-family:vz;margin:0;padding:0;}
"""


class Book:
    def __init__(self):
        self.doc = pymupdf.open()
        self.arch = pymupdf.Archive(FONTS)
        self.pageno = 0
        self.running = ""

    # ---------- low level ----------
    def html(self, rect, body, css=CSS, scale=True):
        page = self.page
        return page.insert_htmlbox(rect, body, css=css, archive=self.arch,
                                   scale_low=0.55 if scale else 1)

    def measure(self, body, width, css=CSS):
        """ارتفاع مورد نیاز متن را اندازه می‌گیرد."""
        tmp = pymupdf.open()
        p = tmp.new_page(width=W, height=4000)
        rc = p.insert_htmlbox(pymupdf.Rect(0, 0, width, 3990), body,
                              css=css, archive=self.arch)
        # insert_htmlbox -> (spare_height, scale)
        h = 3990 - rc[0]
        tmp.close()
        return h

    def new_page(self, running=None):
        self.page = self.doc.new_page(width=W, height=H)
        self.pageno += 1
        if running is None:
            running = self.running
        if running:
            self.html(pymupdf.Rect(L, 14, R, 40),
                      '<div dir="rtl" style="text-align:center;font-size:8.5px;'
                      'font-weight:500;color:#0d4f4f">&#xAB;%s&#xBB;</div>' % running)
        self.footer()
        self.y = 59.5
        return self.page

    def footer(self, num=True):
        p = self.page
        p.insert_htmlbox(pymupdf.Rect(L, 794, L + 40, 815),
                         '<div style="font-family:am;font-size:9px;color:#d9b45c">&#xFD3E;&#xFD3F;</div>',
                         css=CSS, archive=self.arch)
        p.insert_htmlbox(pymupdf.Rect(R - 40, 794, R, 815),
                         '<div style="text-align:right;font-family:am;font-size:9px;color:#d9b45c">&#xFD3E;&#xFD3F;</div>',
                         css=CSS, archive=self.arch)
        if num and getattr(self, 'pageno_label', 0):
            p.insert_htmlbox(pymupdf.Rect(250, 795, 345, 816),
                             '<div style="text-align:center;font-size:9px;font-weight:600;'
                             'color:#b98a2e">%d</div>' % self.pageno_label,
                             css=CSS, archive=self.arch)

    # ---------- blocks ----------
    def space(self, need):
        """اگر جا نبود، صفحه جدید."""
        if self.y + need > 780:
            self.new_page()
            return True
        return False

    def para(self, text, size=11, color="#262626", lh=2.05, gap=7.5,
             align="justify", weight="normal", font="vz"):
        body = ('<div dir="rtl" style="text-align:%s;font-size:%gpx;line-height:%g;'
                'color:%s;font-weight:%s;font-family:%s">%s</div>'
                % (align, size, lh, color, weight, font, text))
        h = self.measure(body, R - L)
        self.space(h)
        self.html(pymupdf.Rect(L, self.y, R, min(self.y + h + 6, 800)), body)
        self.y += h + gap

    def quote(self, arabic, trans, src):
        inner = 18
        body_ar = ('<div dir="rtl" style="text-align:center;font-family:am;font-size:15px;'
                   'line-height:1.9;color:#0a3030">&#xFD3F;&nbsp;%s&nbsp;&#xFD3E;</div>' % arabic)
        body_tr = ('<div dir="rtl" style="text-align:center;font-size:10px;line-height:1.9;'
                   'color:#4a4a4a">%s</div>' % trans)
        body_sr = ('<div dir="rtl" style="text-align:center;font-size:9px;font-weight:600;'
                   'color:#b98a2e">(%s)</div>' % src)
        wid = R - L - 2 * inner
        h = (self.measure(body_ar, wid) + self.measure(body_tr, wid)
             + self.measure(body_sr, wid) + 34)
        self.space(h + 12)
        top = self.y
        self.page.draw_rect(pymupdf.Rect(L, top, R, top + h), color=None, fill=BOXBG)
        self.page.draw_rect(pymupdf.Rect(R - 4, top, R, top + h), color=None, fill=TEAL)
        yy = top + 12
        for b in (body_ar, body_tr, body_sr):
            hh = self.measure(b, wid)
            self.html(pymupdf.Rect(L + inner, yy, R - inner, yy + hh + 4), b)
            yy += hh + 5
        self.y = top + h + 13

    def menbar(self, text):
        inner = 14
        body = ('<div dir="rtl" style="text-align:justify;font-size:10.8px;line-height:2.05;'
                'color:#3d3a2e">%s</div>' % text)
        wid = R - L - 2 * inner
        h = self.measure(body, wid) + 52
        self.space(h + 10)
        top = self.y
        self.page.draw_rect(pymupdf.Rect(L, top, R, top + h), color=None, fill=MENBG)
        self.page.draw_rect(pymupdf.Rect(R - 4, top, R, top + h), color=None, fill=GOLD)
        self.page.draw_rect(pymupdf.Rect(R - 84, top + 10, R - 20, top + 31),
                            color=None, fill=GOLD)
        self.html(pymupdf.Rect(R - 84, top + 12, R - 20, top + 32),
                  '<div dir="rtl" style="text-align:center;font-size:9.5px;font-weight:bold;'
                  'color:#fffdf5">سخن منبری</div>')
        self.html(pymupdf.Rect(L + inner, top + 36, R - inner, top + h), body)
        self.y = top + h + 14

    # ---------- structural ----------
    def chapter_opener(self, num, ordinal, title, intro, items):
        self.running = "فصل %s: %s" % (ordinal, title)
        self.new_page(running="")
        p = self.page
        p.draw_rect(pymupdf.Rect(273.6, 93.5, 321.6, 141.5), color=GOLD, width=1.4)
        self.html(pymupdf.Rect(273.6, 100, 321.6, 140),
                  '<div dir="rtl" style="text-align:center;font-size:26px;font-weight:bold;'
                  'color:#b98a2e">%s</div>' % fa(num))
        self.html(pymupdf.Rect(L, 152, R, 200),
                  '<div dir="rtl" style="text-align:center;font-size:20px;font-weight:bold;'
                  'color:#0d4f4f">فصل %s: %s</div>' % (ordinal, title))
        p.draw_line(pymupdf.Point(226, 206.5), pymupdf.Point(283, 206.5), color=(0, 0, 0), width=0.65)
        p.draw_line(pymupdf.Point(312, 206.5), pymupdf.Point(369, 206.5), color=(0, 0, 0), width=0.65)
        p.draw_rect(pymupdf.Rect(292.5, 202, 302.8, 211.1), color=None, fill=(0, 0, 0))
        p.draw_rect(pymupdf.Rect(287.3, 205.2, 289.9, 207.8), color=None, fill=(0, 0, 0))
        p.draw_rect(pymupdf.Rect(305.4, 205.2, 308.0, 207.8), color=None, fill=(0, 0, 0))
        self.html(pymupdf.Rect(96, 218, R - 42, 300),
                  '<div dir="rtl" style="text-align:justify;font-size:11px;line-height:2.05;'
                  'color:#6b7771">%s</div>' % intro)
        self.html(pymupdf.Rect(L, 306, R, 330),
                  '<div dir="rtl" style="text-align:right;font-size:12.5px;font-weight:bold;'
                  'color:#b98a2e">فهرست پرسش‌های این فصل</div>')
        p.draw_line(pymupdf.Point(L, 341.5), pymupdf.Point(R, 341.5), color=GOLD_L, width=0.8)
        y = 344
        for i, (n, t) in enumerate(items):
            self.html(pymupdf.Rect(R - 30, y, R, y + 22),
                      '<div dir="rtl" style="text-align:left;font-size:10.5px;font-weight:bold;'
                      'color:#0d4f4f">%s</div>' % fa(n))
            self.html(pymupdf.Rect(L, y, R - 34, y + 22),
                      '<div dir="rtl" style="text-align:right;font-size:10.5px;'
                      'color:#26262f">%s</div>' % t)
            y += 24.4

    def question(self, num, title):
        self.new_page()
        p = self.page
        p.draw_rect(pymupdf.Rect(509.9, 59.5, 541.4, 91.0), color=None, fill=TEAL)
        self.html(pymupdf.Rect(509.9, 65, 541.4, 90),
                  '<div dir="rtl" style="text-align:center;font-size:15px;font-weight:bold;'
                  'color:#fdf8ea">%s</div>' % fa(num))
        self.html(pymupdf.Rect(L, 60, 502, 95),
                  '<div dir="rtl" style="text-align:right;font-size:14.5px;font-weight:bold;'
                  'color:#0d4f4f">%s</div>' % title)
        p.draw_line(pymupdf.Point(L, 100), pymupdf.Point(R, 100), color=GOLD_L, width=0.9)
        self.y = 112
