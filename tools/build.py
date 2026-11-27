# Release pipeline used to produce public/ and src/ from the original single-file game (kept privately, not in this repo).
# Paths are those of the machine that ran it; adjust SRC/OUT before re-running.
import re,os,json,hashlib,base64,subprocess,shutil,sys
SRC='/workspace/ashgrove-src/original.html'; OUT='/workspace/ashgrove-build/site'; TMP='/workspace/ashgrove-build/tmp'
os.makedirs(TMP,exist_ok=True)
raw=open(SRC,'rb').read(); t=raw.decode('utf-8')
assert len(raw)==262186278
def find_all(p): return [m for m in re.finditer(p,t)]
# --- locate regions (character offsets) ---
st_open=[m.start() for m in re.finditer(r'<style>',t)]; st_close=[m.start() for m in re.finditer(r'</style>',t)]
s1,s2,s4=st_open[0],st_open[1],st_open[2]
e1,e2,e4=st_close[0],st_close[1],st_close[2]
assert s1<e1<s2<e2<s4<e4
assert t[e1+8:s2].strip()==''
e3=e2
head_css=t[s1+7:e1]+'\n'+t[s2+7:e2]
load_css=t[s4+7:e4]
ld_s=t.index('<script>',e4); ld_e=t.index('</script>',ld_s)
mn_s=t.index('<script>',ld_e); mn_e=t.rindex('</script>')
loader=t[ld_s+8:ld_e]; main=t[mn_s+8:mn_e]
print('main chars',len(main),'loader chars',len(loader))
# --- loader: jpeg data URIs -> files ---
os.makedirs(OUT+'/assets/loading',exist_ok=True)
manifest={'loading':[], 'data':[]}
def loader_rep(m):
    key=m.group(1); mime=m.group(2); b=base64.b64decode(m.group(3))
    ext={'image/jpeg':'jpg','image/png':'png'}[mime]
    fn=f'assets/loading/{key}.{ext}'; open(OUT+'/'+fn,'wb').write(b)
    manifest['loading'].append({'key':key,'file':fn,'bytes':len(b)})
    return f'"{key}": "{fn}"'
loader2,nl=re.subn(r'"(\w+)":\s*"data:(image/(?:jpeg|png));base64,([A-Za-z0-9+/=]+)"',loader_rep,loader)
assert 'base64,' not in loader2, 'loader still has data uri'
print('loader images',nl,'loader chars now',len(loader2))
# --- main: tokenise big data ---
vals=[]
def tok(v):
    vals.append(v); return f'@@T{len(vals)-1}@@'
m1=re.sub(r'data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=]{1000,}',lambda m:tok(m.group(0)),main)
m2=re.sub(r'(?<![A-Za-z0-9+/=@])[A-Za-z0-9+/=]{1000,}(?![A-Za-z0-9+/=@])',lambda m:tok(m.group(0)),m1)
assert '@@T' not in main
open(TMP+'/main_tok.js','w').write(m2)
print('tokens',len(vals),'tokenised chars',len(m2))
r=subprocess.run(['node','--max-old-space-size=8192','/workspace/ashgrove-build/tools/ast_edits.js',TMP+'/main_tok.js',TMP+'/edits.json'],capture_output=True,text=True)
print(r.stdout,r.stderr); assert r.returncode==0
ed=json.load(open(TMP+'/edits.json')); handled=set(ed['handled'])
m3=open(TMP+'/edits.json.js',encoding='utf-8').read()
# restore any unhandled tokens inline
unh=[i for i in range(len(vals)) if i not in handled]
m4=re.sub(r'@@T(\d+)@@',lambda m:vals[int(m.group(1))],m3)
print('unhandled tokens restored inline:',len(unh),'bytes',sum(len(vals[i]) for i in unh))
# --- data chunks ---
os.makedirs(OUT+'/assets/data',exist_ok=True)
CH=7*1000*1000; chunks=[];cur=[];size=0
for i in sorted(handled):
    v=vals[i]; assert re.fullmatch(r'[A-Za-z0-9+/=:;,.\-a-z]+',v)
    line=f'__ASG[{i}]="{v}";\n'
    if size+len(line)>CH and cur: chunks.append(cur);cur=[];size=0
    cur.append(line);size+=len(line)
    mm=re.match(r'data:([^;]+);base64,',v)
    manifest['data'].append({'id':i,'kind':mm.group(1) if mm else ('image/png (raw base64)' if v.startswith('iVBORw0K') else 'binary buffer (raw base64)'),'chars':len(v)})
if cur: chunks.append(cur)
names=[]
for n,c in enumerate(chunks):
    fn=f'assets/data/asg-{n+1:02d}.js'; names.append(fn)
    with open(OUT+'/'+fn,'w') as f:
        f.write('/* Ashgrove: Undead Siege by Evan - embedded game data (textures, audio, meshes), moved out of index.html unchanged. */\n')
        f.write('var __ASG=window.__ASG||(window.__ASG=[]);\n'); f.writelines(c)
# --- css ---
os.makedirs(OUT+'/css',exist_ok=True)
open(OUT+'/css/styles.css','w').write(head_css); open(OUT+'/css/loading.css','w').write(load_css)
# --- index.html ---
notice_end=t.index('-->')+3
pre_head=t[:s1]; between=t[e3+8:s4]; after_load_css=t[e4+8:ld_s]; body_mid=t[ld_e+9:mn_s]; tail=t[mn_e+9:]
assert pre_head.startswith('<!doctype html>\n<!--')
credit='\n<meta name="author" content="Evan">'
pre_head2=pre_head.replace('<meta charset="utf-8">','<meta charset="utf-8">'+credit,1)
tags=''.join(f'<script src="{n}"></script>\n' for n in names)
html=(pre_head2+'<link rel="stylesheet" href="css/styles.css">'+between+'<link rel="stylesheet" href="css/loading.css">'+after_load_css
      +'<script>'+loader2+'</script>'+body_mid.rstrip('\n')+'\n'+tags+'<script>'+m4+'</script>'+tail)
open(OUT+'/index.html','w').write(html)
json.dump({'source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'data_files':names,**manifest},open(OUT+'/assets/manifest.json','w'),indent=1)
print('index.html bytes',len(html.encode()))
