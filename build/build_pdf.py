# -*- coding: utf-8 -*-
"""ساخت PDF «اصول فقه — ۳۷۹ پرسش و پاسخ» از فایل HTML (فشرده، با قلم Vazirmatn)."""
import re, sys, html
sys.path.insert(0, '/home/user/railway-3xui/build')
import pymupdf

FONTDIR = '/home/user/railway-3xui/build/fonts'
FA = ''.join(chr(0x06F0 + k) for k in range(10))
def fa(n):
    return ''.join(FA[int(c)] for c in str(n))

W, H = 595.2756, 841.8898
L, R = 53.8583, 541.4174
TEAL = (0.0509, 0.3098, 0.3098)
GOLD = (0.7255, 0.5412, 0.1804)
GOLD_L = (0.8510, 0.7059, 0.3608)
BOXBG = (0.9490, 0.9647, 0.9608)
BOTTOM = 780
CSS = """
@font-face{font-family:vz;src:url(Vazirmatn-Regular.ttf);}
@font-face{font-family:vz;font-weight:500;src:url(Vazirmatn-Medium.ttf);}
@font-face{font-family:vz;font-weight:600;src:url(Vazirmatn-SemiBold.ttf);}
@font-face{font-family:vz;font-weight:bold;src:url(Vazirmatn-Bold.ttf);}
*{font-family:vz;margin:0;padding:0;}
"""
ARCH = pymupdf.Archive(FONTDIR)


def measure(body, width):
    tmp = pymupdf.open()
    p = tmp.new_page(width=W, height=6000)
    rc = p.insert_htmlbox(pymupdf.Rect(0, 0, width, 5990), body, css=CSS, archive=ARCH)
    h = 5990 - rc[0]
    tmp.close()
    return h


def div(text, size=10.6, lh=1.72, color="#232323", weight="normal", align="justify",
         indent=0):
    st = 'text-align:%s;font-size:%gpx;line-height:%g;color:%s;font-weight:%s;' % (
        align, size, lh, color, weight)
    if indent:
        st += 'padding-right:%gpx;' % indent
    return '<div dir="rtl" style="%s">%s</div>' % (st, text)


class Doc:
    def __init__(self):
        self.doc = pymupdf.open()
        self.page = None
        self.y = 0
        self.pageno = 0
        self.running = ""

    def new_page(self, running=None):
        self.page = self.doc.new_page(width=W, height=H)
        self.pageno += 1
        run = self.running if running is None else running
        if self.pageno > 1:
            if run:
                self.page.insert_htmlbox(pymupdf.Rect(L, 16, R, 40),
                                         div('%s' % run, 8.4, 1.4, '#0d4f4f', '500', 'center'),
                                         css=CSS, archive=ARCH)
            self.page.insert_htmlbox(pymupdf.Rect(250, 793, 345, 816),
                                     div(fa(self.pageno - 1), 9, 1.2, '#b98a2e', '600', 'center'),
                                     css=CSS, archive=ARCH)
        self.y = 56
        return self.page

    def box(self, body, need=None, gap=6.0):
        h = need if need is not None else measure(body, R - L)
        if self.y + h > BOTTOM and self.y > 70:
            self.new_page()
        self.page.insert_htmlbox(pymupdf.Rect(L, self.y, R, self.y + h + 6), body,
                                 css=CSS, archive=ARCH)
        self.y += h + gap

    def cover(self, chapter_lines, npage, nchap):
        self.new_page(running="")
        p = self.page
        p.draw_rect(pymupdf.Rect(L, 54, R, 788), color=GOLD_L, width=1.1)
        p.draw_rect(pymupdf.Rect(L + 6, 60, R - 6, 782), color=TEAL, width=0.5)
        self.y = 120
        self.box(div('اُصُولُ  الفِقه', 28, 1.4, '#0d4f4f', 'bold', 'center'), 48, 12)
        self.box(div('%s پرسش و پاسخِ تشریحی در %s فصل' % (fa(npage), fa(nchap)),
                     12.5, 1.9, '#2b2b2b', '500', 'center'), 26, 6)
        self.box(div('بر پایۀ «اصول فقه» محقّق مظفر، «رسائل» شیخ انصاری و «کفایةالاُصول» آخوند خراسانی',
                     10, 1.9, '#5a5a5a', 'normal', 'center'), 32, 4)
        p.draw_line(pymupdf.Point(210, 262), pymupdf.Point(386, 262), color=GOLD, width=0.9)
        self.y = 278
        self.box(div('فهرست فصل‌ها', 11.5, 1.6, '#b98a2e', 'bold', 'center'), 22, 5)
        for ch in chapter_lines:
            self.box(div(ch, 9.4, 1.62, '#3a3a3a', 'normal', 'center'), None, 1)
        self.box(div('تهیۀ و ویراستاری: هادی شبستانی', 9.4, 1.6, '#7a7a7a', 'normal', 'center'),
                 None, 0)

    def chapter(self, num, title, sub, count, qsum=None):
        self.new_page(running="")
        p = self.page
        p.draw_rect(pymupdf.Rect(258, 250, 337, 328), color=None, fill=BOXBG)
        p.draw_rect(pymupdf.Rect(258, 250, 337, 328), color=GOLD, width=1.2)
        p.insert_htmlbox(pymupdf.Rect(258, 268, 337, 310),
                         div(fa(num), 26, 1.2, '#b98a2e', 'bold', 'center'), css=CSS, archive=ARCH)
        self.y = 350
        self.box(div('فصل %s' % fa(num), 11.5, 1.5, '#0d4f4f', '600', 'center'), 20, 4)
        self.box(div(title, 17, 1.6, '#123c3c', 'bold', 'center'), None, 8)
        p.draw_line(pymupdf.Point(226, self.y - 8), pymupdf.Point(369, self.y - 8),
                    color=GOLD_L, width=0.8)
        self.y += 6
        self.box(div(sub, 10.4, 1.8, '#6b7771', 'normal', 'center'), None, 6)
        self.box(div('%s پرسش' % fa(count), 9.6, 1.6, '#b98a2e', '600', 'center'), None, 0)
        if qsum:
            self.box(div(qsum, 8.6, 1.6, '#9a9a9a', 'normal', 'center'), None, 0)

        self.running = 'فصل %s: %s' % (fa(num), title)
        self.y = 520

    def question(self, num, title):
        head = ('<div dir="rtl" style="text-align:right;font-size:12.2px;line-height:1.55;'
                'color:#0d4f4f;font-weight:bold"><span style="color:#b98a2e">سؤال %s</span>'
                '  —  %s</div>' % (fa(num), title))
        h = measure(head, R - L) + 14
        if self.y + h > BOTTOM:
            self.new_page()
        top = self.y
        self.page.insert_htmlbox(pymupdf.Rect(L, top, R, top + h), head, css=CSS, archive=ARCH)
        self.page.draw_line(pymupdf.Point(L, top + h - 7), pymupdf.Point(R, top + h - 7),
                            color=(0.88, 0.91, 0.90), width=0.5)
        self.y = top + h

    def para(self, text, size=10.6, indent=0, gap=5.0, color="#232323", weight="normal"):
        self.box(div(text, size, 1.74, color, weight, 'justify', indent), None, gap)

    def note(self, text):
        body = div(text, 9.7, 1.7, '#33413c', 'normal', 'justify')
        w = R - L - 24
        h = measure(body, w)
        if self.y + h + 16 > BOTTOM:
            self.new_page()
        top = self.y
        self.page.draw_rect(pymupdf.Rect(L, top, R, top + h + 16), color=None,
                            fill=(0.962, 0.973, 0.968))
        self.page.draw_rect(pymupdf.Rect(R - 3, top, R, top + h + 16), color=None, fill=GOLD)
        self.page.insert_htmlbox(pymupdf.Rect(L + 12, top + 8, R - 12, top + h + 14), body,
                                 css=CSS, archive=ARCH)
        self.y = top + h + 20


# ---------------- HTML -> structured content ----------------
TAG = re.compile(r'<[^>]+>')
def esc(t):
    return html.escape(t, quote=False)


def parse(path):
    h = open(path, encoding='utf-8').read()
    OPEN = re.compile(r'<details class="qa[^"]*">')
    ANCHOR = '<span class="qn">'
    i = h.find(ANCHOR)
    QN = h[i + len(ANCHOR):h.find('</span>', i)].split(' ')[0]
    QN_RE = re.compile(re.escape(ANCHOR + QN) + r'\s*([' + FA + r']+)</span>')
    heads = [m for m in re.finditer(
        r'<div class="chapter-head"><div class="cn">([^<]*)</div>'
        r'<h1>([^<]*)</h1><div class="cs">([^<]*)</div></div>', h)]
    chapters = [dict(cn=m.group(1).strip(), title=m.group(2).strip(), sub=m.group(3).strip(),
                     start=m.end(), qs=[]) for m in heads]
    bounds = [c['start'] for c in chapters] + [10 ** 12]
    spans, pos = [], 0
    while True:
        mm = OPEN.search(h, pos)
        if not mm:
            break
        last = h.find('</details>', mm.end()) + len('</details>')
        spans.append((mm.start(), last))
        pos = last
    for a, b in spans:
        s = h[a:b]
        n = int(QN_RE.search(s[:700]).group(1).translate(str.maketrans(FA, '0123456789')))
        t = re.search(r'<span class="qt">(.*?)</span>', s, re.S).group(1)
        an = re.search(r'<div class="a">(.*?)</div>\s*(?=<div class="expert|</details>)', s, re.S)
        answer = an.group(1) if an else ''
        answer = re.sub(r'^\s*<span class="lbl">[^<]*</span>\s*<br\s*/?>', '', answer)
        extra = []
        for m2 in re.finditer(r'<span class="lbl2">([^<]*)</span>(.*?)(?=</div>\s*</details>|\Z)',
                              s, re.S):
            body = re.sub(r'^\s*<br\s*/?>', '', m2.group(2))
            body = TAG.sub(' ', body)
            body = re.sub(r'\s+', ' ', body).strip()
            extra.append((body, m2.group(1).strip()))
        idx = max(j for j in range(len(bounds) - 1) if bounds[j] <= a)
        chapters[idx]['qs'].append(dict(num=n, title=re.sub(r'\s+', ' ', TAG.sub('', t)).strip(),
                                        answer=answer, extra=extra))
    return chapters


def segments(answer):
    a = re.sub(r'<br\s*/?>\s*(?=<span class="enum">)', '', answer)
    a = re.sub(r'</div>\s*<div class="expert-addition">.*', '', a, flags=re.S)
    parts = re.split(r'(<span class="enum">[^<]*</span>)', a)
    raw = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            raw.append(('mark', TAG.sub('', p).strip()))
        else:
            txt = re.sub(r'\s+', ' ', TAG.sub(' ', p)).strip()
            if txt:
                raw.append(('p', txt))
    merged, j = [], 0
    while j < len(raw):
        k, t = raw[j]
        if k == 'mark':
            if j + 1 < len(raw) and raw[j + 1][0] == 'p':
                merged.append(('e', t + ' ' + raw[j + 1][1]))
                j += 2
                continue
            merged.append(('e', t))
        else:
            merged.append(('p', t))
        j += 1
    return merged


def build(src, out, only_first=None, total_q=379):
    chapters = parse(src)
    d = Doc()
    for ch in chapters:
        ch['first'] = ch['qs'][0]['num'] if ch['qs'] else 0
        ch['last'] = ch['qs'][-1]['num'] if ch['qs'] else 0
    d.cover(['<b style="color:#0d4f4f">%s</b>  %s' % (c['cn'], c['title']) for c in chapters],
            sum(len(c['qs']) for c in chapters), len(chapters))
    for k, ch in enumerate(chapters, 1):
        rng = ('%s تا %s' % (fa(ch['qs'][0]['num']), fa(ch['qs'][-1]['num']))) if ch['qs'] else None
        d.chapter(k, ch['title'], ch['sub'], len(ch['qs']),
                  ('شمارۀ پرسش‌ها: ' + rng) if rng else None)
        for q in ch['qs']:
            d.question(q['num'], esc(q['title']))
            for kind, t in segments(q['answer']):
                t = esc(t)
                if kind == 'e':
                    d.para(t, 10.35, indent=13, gap=3.4)
                else:
                    d.para(t, 10.6, gap=4.4)
            for body, lbl in q['extra']:
                if body:
                    d.note('<b style="color:#a8761f">%s</b> &nbsp; %s' % (esc(lbl), esc(body)))
            d.y += 3
        if only_first and k >= only_first:
            break
    d.doc.set_metadata({'title': 'اصول فقه — %s پرسش و پاسخ' % fa(total_q),
                        'author': 'هادی شبستانی',
                        'subject': 'مباحث الفاظ، حجّت، اصول عملیه، تعادل و تراجیح، اجتهاد و تقلید'})
    d.doc.save(out, garbage=4, deflate=True, deflate_fonts=True, clean=True)
    print('pages:', d.doc.page_count, '->', out)


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else '/home/user/railway-3xui/osol_fagheh.html'
    out = sys.argv[2] if len(sys.argv) > 2 else '/home/user/work/osol_fagheh.pdf'
    n = int(sys.argv[3]) if len(sys.argv) > 3 else None
    build(src, out, n)
