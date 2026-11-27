# Release pipeline used to produce public/ and src/ from the original single-file game (kept privately, not in this repo).
# Paths are those of the machine that ran it; adjust B before re-running.
# Split built site/index.html into src/index.template.html + src/game/game-NN.js (exact bytes; parts are plain byte
# slices that tools/assemble.mjs concatenates back), never cutting inside the protection region.
import re,os,sys,hashlib,json,glob
B='/workspace/ashgrove-build'; h=open(B+'/site/index.html','rb').read()
MAX=int(sys.argv[1]) if len(sys.argv)>1 else 4_000_000
best=None
for m in re.finditer(rb'<script>(.*?)</script>',h,re.S):
    if best is None or len(m.group(1))>len(best.group(1)): best=m
main=best.group(1); MARK=b'/*@@ASHGROVE_GAME_SCRIPT@@*/'
assert MARK not in h
tpl=h[:best.start(1)]+MARK+h[best.end(1):]
P0=main.index(b'// 133ab (user): more tripwires'); 
P1=main.index(b'\n',main.index(b'const bait=(o,k)=>'))
for _ in range(40): P1=main.index(b'\n',P1+1)
HASH=main.index(b'{let A=[...document.scripts].reduce(')
cuts=[0]; pos=0
while len(main)-pos>MAX:
    end=pos+MAX
    nl=main.rfind(b'\n',pos+MAX//2,end)
    c=nl+1 if nl!=-1 else None
    if c is None:  # inside one huge line: cut at an ASCII byte (never mid UTF-8 sequence)
        c=end
        while main[c]>=0x80 or main[c-1]>=0x80: c-=1
    if P0-200<=c<=P1+1: c=main.rfind(b'\n',pos+1,P0-200)+1
    assert c>pos; cuts.append(c); pos=c
cuts.append(len(main))
for f in glob.glob(B+'/repo/src/game/game-*.js'): os.remove(f)
names=[];meta=[]
for n in range(len(cuts)-1):
    a,b=cuts[n],cuts[n+1]; data=main[a:b]
    fn=f'src/game/game-{n+1:02d}.js'; open(B+'/repo/'+fn,'wb').write(data); names.append(fn)
    meta.append({'file':fn,'byte_start':a,'bytes':len(data),'contains_protection':a<=P0<b and P1<=b,'contains_modified_file_hash':a<=HASH<b})
assert b''.join(open(B+'/repo/'+f,'rb').read() for f in names)==main
assert sum(m['contains_protection'] for m in meta)==1
open(B+'/repo/src/index.template.html','wb').write(tpl)
json.dump({'parts':names,'game_script_sha256':hashlib.sha256(main).hexdigest(),'index_html_sha256':hashlib.sha256(h).hexdigest(),'detail':meta},open(B+'/repo/src/game/manifest.json','w'),indent=1)
for m in meta: print(m)
