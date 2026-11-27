# Release pipeline used to produce public/ and src/ from the original single-file game (kept privately, not in this repo).
# Paths are those of the machine that ran it; adjust SRC/OUT before re-running.
# Split built site/index.html into src/index.template.html + src/game/game-NN.js (exact bytes), never inside the protection region.
import re,os,hashlib,json
B='/workspace/ashgrove-build'; h=open(B+'/site/index.html','rb').read()
# locate main inline script = longest inline script
best=None
for m in re.finditer(rb'<script>(.*?)</script>',h,re.S):
    if best is None or len(m.group(1))>len(best.group(1)): best=m
main=best.group(1); MARK=b'/*@@ASHGROVE_GAME_SCRIPT@@*/'
assert MARK not in h
tpl=h[:best.start(1)]+MARK+h[best.end(1):]
lines=main.split(b'\n'); 
# protection region line range (inside main), keep in one part
def li(sub): return next(i for i,l in enumerate(lines) if sub in l)
p0=li(b'// 133ab (user): more tripwires'); p1=li(b'const bait=(o,k)=>')+40
hashl=li(b'{let A=[...document.scripts].reduce(')
TARGET=2_500_000; parts=[]; cur=[]; size=0; protect_part=None
for i,l in enumerate(lines):
    cur.append(l); size+=len(l)+1
    if size>=TARGET and not (p0-5<=i<=p1) and i<len(lines)-1:
        parts.append(cur); cur=[]; size=0
parts.append(cur)
os.makedirs(B+'/repo/src/game',exist_ok=True)
names=[]; idx=0; meta=[]
for n,c in enumerate(parts):
    data=b'\n'.join(c)+(b'\n' if n<len(parts)-1 else b'')
    fn=f'src/game/game-{n+1:02d}.js'; open(B+'/repo/'+fn,'wb').write(data); names.append(fn)
    meta.append({'file':fn,'first_line':idx+1,'last_line':idx+len(c),'bytes':len(data),
                 'contains_protection': idx<=p0<idx+len(c), 'contains_modified_file_hash': idx<=hashl<idx+len(c)})
    idx+=len(c)
assert b''.join(open(B+'/repo/'+f,'rb').read() for f in names)==main
open(B+'/repo/src/index.template.html','wb').write(tpl)
json.dump({'parts':names,'game_script_sha256':hashlib.sha256(main).hexdigest(),'index_html_sha256':hashlib.sha256(h).hexdigest(),'detail':meta},open(B+'/repo/src/game/manifest.json','w'),indent=1)
for m in meta: print(m)
print('p0,p1,hash lines',p0,p1,hashl)
