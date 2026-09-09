# -*- coding: utf-8 -*-
"""Apply a list of block-level edits to the QA HTML.
edits file: JSON list of {"num": <new number>, "mode": "full"|"re"|"append", ...}
  full  : {"body_html": "..."}  -> replace inner HTML of <div class="a">
  re    : {"pat": "...", "repl": "...", "flags":""}  -> one regex sub inside the block
  append: {"after_pat": "...", "text": "..."}      -> insert text right after the match
All patterns are regex over the block substring; Persian may appear inside them.
"""
import re, json, sys, os
SRC=sys.argv[1]; EDITS=sys.argv[2]; DST=sys.argv[3]
h=open(SRC,encoding='utf-8').read()
P=''.join(chr(0x06F0+k) for k in range(10))
A='0123456789'
TR=str.maketrans(P,A)
ANCHOR='<span class="qn">'
i0=h.find(ANCHOR); e0=h.find('</span>',i0)
QN=h[i0+len(ANCHOR):e0].split(' ')[0]
QN_RE=re.compile(re.escape(ANCHOR+QN)+r'\s*(['+P+']+)</span>')
OPEN=re.compile(r'<details class="qa[^"]*">')
CLOSE='</details>'
spans=[];pos=0
while True:
    m=OPEN.search(h,pos)
    if not m: break
    c=h.find(CLOSE,m.end()); last=c+len(CLOSE)
    spans.append([m.start(),last]); pos=last
assert len(spans)==379, len(spans)
numof=[]
for a,b in spans:
    mm=QN_RE.search(h[a:b]); numof.append(int(mm.group(1).translate(TR)))
assert numof==list(range(1,380))
by_num={n:k for k,n in enumerate(numof)}

edits=json.load(open(EDITS,encoding='utf-8'))
SKIPPED=[]
# process blocks, collecting replacements, from last to first to keep offsets
for ed in edits:
    n=ed['num']
    if n not in by_num:
        print('!! missing block', n); continue
    k=by_num[n]; a,b=spans[k]
    seg=h[a:b]
    mode=ed.get('mode','re')
    if mode in ('re','block') and 'old_txt' in ed and 'pat' not in ed: mode='lit' if mode=='re' else mode
    if mode=='full':
        m=re.search(r'(<div class="a">)(.*?)(</div>)', seg, re.S)
        assert m, 'no .a div in %d'%n
        body=ed.get('body_html') or ed.get('answer') or ''
        body=body.lstrip()
        for pref in ('<span class="lbl">','<span class="lbl" >'):
            pass
        m2=re.match(r'<span class="lbl">[^<]*</span>\s*<br\s*/?>', body)
        if m2: body=body[m2.end():]
        seg2=seg[:m.start(2)]+ed.get('prefix','')+'<span class="lbl">پاسخ</span><br/>'+body+seg[m.end(2):]
    elif mode=='block':
        seg2=seg.replace(ed['old_txt'], ed['new_txt'], 1)
        if seg2==seg:
            print('~~ Q%d block-literal not found: %r'%(n,ed['old_txt'][:48])); SKIPPED.append(ed)
    elif mode=='lit':
        seg2=seg.replace(ed['old_txt'], ed['new_txt'], 1)
        if seg2==seg:
            print('~~ Q%d literal already-superseded/skipped: %r'%(n,ed['old_txt'][:48])); SKIPPED.append(ed)
    elif mode=='re':
        flags=0
        for f in ed.get('flags',''):
            flags |= {'s':re.S,'i':re.I,'m':re.M}[f]
        pat=ed['pat']
        if ed.get('fa'):   # convert ascii digits in pattern groups? not needed
            pass
        seg2,c=2,[None][0]
        seg2,c=re.subn(pat, ed['repl'], seg, count=ed.get('count',1), flags=flags)
        if c!=1:
            print('!! Q%d re applied %d times: %r'%(n,c,pat[:70])); sys.exit(3)
    elif mode=='append':
        flags=0
        for f in ed.get('flags',''):
            flags |= {'s':re.S,'i':re.I,'m':re.M}[f]
        m=re.search(ed['after_pat'], seg, flags)
        assert m, 'anchor not found in %d'%n
        seg2=seg[:m.end()]+ed['text']+seg[m.end():]
    else:
        raise SystemExit('bad mode')
    delta=len(seg2)-len(seg)
    h=h[:a]+seg2+h[b:]
    # shift all later spans
    for j in range(k+1,len(spans)):
        spans[j][0]+=delta; spans[j][1]+=delta
    spans[k][1]+=delta
    print('ok Q%d (%s) delta %+d'%(n,mode,delta))
json.dump(SKIPPED, open(DST+'.skipped.json','w'), ensure_ascii=False, indent=1)
open(DST,'w',encoding='utf-8').write(h)
print('WROTE',DST,'len',len(h))
