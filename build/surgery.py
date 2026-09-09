# -*- coding: utf-8 -*-
import re, json
SRC='/home/user/railway-3xui/osol_fagheh.html'
DST='/home/user/work/tmp1.html'
h=open(SRC,encoding='utf-8').read()
orig_len=len(h)

ANCHOR='<span class="qn">'
i=h.find(ANCHOR)
e=h.find('</span>', i)
inner=h[i+len(ANCHOR):e]                      # "<word> <digits>"
QN_TXT=inner.split(' ')[0]
d0=inner.split(' ')[-1][0]
base=ord(d0)-1
assert 0x06F0 <= base <= 0x06F1, hex(base)
P=''.join(chr(base+k) for k in range(10))
assert len(set(P))==10 and all(0x06F0<=ord(c)<=0x06F9 for c in P), [hex(ord(c)) for c in P]
print('QN codepoints', [hex(ord(c)) for c in QN_TXT], 'P', [hex(ord(c)) for c in P])

def to_fa(n):
    return ''.join(P[int(d)] for d in str(n))
def to_en(s):
    return s.translate(str.maketrans(P,'0123456789'))

QN_RE=re.compile(re.escape(ANCHOR+QN_TXT)+r'\s*(['+P+']+)</span>')
OPEN=re.compile(r'<details class="qa[^"]*">')
CLOSE='</details>'

DEL=set(json.load(open('/home/user/work/del.json'))['del'])
print('DEL count', len(DEL))

spans=[]; pos=0
while True:
    m=OPEN.search(h,pos)
    if not m: break
    c=h.find(CLOSE,m.end()); assert c>0
    last=c+len(CLOSE)
    nxt=OPEN.search(h,last)
    assert (nxt is None) or h.find(CLOSE,last,nxt.start())<0
    spans.append((m.start(),last)); pos=last
assert len(spans)==400, len(spans)

nums=[]
for a,b in spans:
    mm=QN_RE.search(h[a:b])
    assert mm, ('NOQ',a,b)
    nums.append(int(to_en(mm.group(1))))
assert nums==list(range(1,401)), nums[:12]

keep=[k for k in range(400) if nums[k] not in DEL]
newnum={nums[k]:n for n,k in enumerate(keep,start=1)}
assert len(keep)==379 and max(newnum.values())==379

pieces=[]; prev=0; keepset=set(keep)
for k,(a,b) in enumerate(spans):
    pieces.append(h[prev:a])
    if k in keepset: pieces.append(('B',a,b,nums[k]))
    prev=b
pieces.append(h[prev:])

out=[]; nsub=0
for p in pieces:
    if isinstance(p,tuple):
        _,a,b,old=p
        seg=h[a:b]; nn=newnum[old]
        def rep(m): return m.group(0).replace(m.group(1), to_fa(nn))
        seg2,cnt=QN_RE.subn(rep,seg,count=1)
        assert cnt==1,(old,nn)
        nsub+=cnt; out.append(seg2)
    else:
        out.append(p)
h=''.join(out)
print('renumbered',nsub,'| len',len(h),'delta',len(h)-orig_len)

sites=[]
for m in re.finditer(re.escape(to_fa(400)),h):
    sites.append((m.start(), h[max(0,m.start()-130):m.end()+90].replace('\n',' ')))
print('occurrences of "400":',len(sites))
for s,ctx in sites: print('  @%d %s'%(s, ctx.encode('unicode_escape').decode()[:300]))
open(DST,'w',encoding='utf-8').write(h)
print('WROTE',DST)
