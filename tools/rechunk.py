# Release pipeline used to produce public/ and src/ from the original single-file game (kept privately, not in this repo).
# Paths are those of the machine that ran it; adjust B before re-running.
# Regroup the embedded-data chunks (public/assets/data) to at most CH bytes each, content-hashed names, values unchanged.
import re,os,sys,json,hashlib
B='/workspace/ashgrove-build/site'; CH=int(sys.argv[1]) if len(sys.argv)>1 else 4_800_000
man=json.load(open(B+'/assets/manifest.json'))
old=re.findall(r'<script src="(assets/data/[^"]+)"></script>',open(B+'/index.html',encoding='utf-8').read())
HDR=None; lines=[]
for fn in old:
    t=open(B+'/'+fn,encoding='utf-8').read().split('\n')
    hdr='\n'.join(t[:2])+'\n'; HDR=HDR or hdr; assert hdr==HDR
    lines+= [l+'\n' for l in t[2:] if l]
assert all(re.fullmatch(r'__ASG\[\d+\]\+?="[^"\\]*";\n',l) for l in lines)
# a single value longer than a chunk is written as __ASG[i]="part1"; __ASG[i]+="part2"; ... (same final string)
LIM=CH-len(HDR)-64; out=[]
for l in lines:
    if len(l)<=LIM: out.append(l); continue
    m=re.fullmatch(r'(__ASG\[\d+\])(\+?)="([^"]*)";\n',l); k,op,v=m.groups(); first=True
    for a in range(0,len(v),LIM-40):
        out.append(f'{k}{op if first else "+"}="{v[a:a+LIM-40]}";\n'); first=False
lines=out
chunks=[];cur=[];size=len(HDR)
for l in lines:
    if size+len(l)>CH and cur: chunks.append(cur);cur=[];size=len(HDR)
    cur.append(l);size+=len(l)
chunks.append(cur)
names=[]
for n,c in enumerate(chunks):
    data=(HDR+''.join(c)).encode(); h=hashlib.sha256(data).hexdigest()[:10]
    fn=f'assets/data/asg-{n+1:02d}.{h}.js'; open(B+'/'+fn,'wb').write(data); names.append(fn)
for fn in old:
    if fn not in names: os.remove(B+'/'+fn)
html=open(B+'/index.html',encoding='utf-8').read()
oldtags=''.join(f'<script src="{n}"></script>\n' for n in old); assert html.count(oldtags)==1
html=html.replace(oldtags,''.join(f'<script src="{n}"></script>\n' for n in names))
open(B+'/index.html','w',encoding='utf-8').write(html)
man['data_files']=names; json.dump(man,open(B+'/assets/manifest.json','w'),indent=1)
print(len(names),'chunks, max',max(os.path.getsize(B+'/'+n) for n in names))
