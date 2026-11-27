// Reads tokenized main script, emits JSON edit list. Tokens: @@T<n>@@
const fs=require('fs');const acorn=require('acorn');const walk=require('acorn-walk');
const src=fs.readFileSync(process.argv[2],'utf8');
const ast=acorn.parse(src,{ecmaVersion:'latest',sourceType:'script',allowHashBang:true});
const TOK=/@@T(\d+)@@/g;const edits=[];const handled=new Set();
const parents=new Map();
walk.fullAncestor(ast,(node,state,anc)=>{
  if(node.type==='Literal'&&typeof node.value==='string'&&TOK.test(node.raw)){TOK.lastIndex=0;
    const par=anc[anc.length-2];
    if(par&&(par.type==='Property'||par.type==='MethodDefinition'||par.type==='PropertyDefinition')&&par.key===node&&!par.computed)return;
    if(par&&(par.type==='ImportDeclaration'||par.type==='ExportNamedDeclaration'||par.type==='ExpressionStatement'&&par.directive))return;
    const raw=node.raw,q=raw[0];const body=raw.slice(1,-1);
    const parts=[];let last=0,m;TOK.lastIndex=0;
    while((m=TOK.exec(body))){if(m.index>last)parts.push(q+body.slice(last,m.index)+q);parts.push('__ASG['+m[1]+']');handled.add(+m[1]);last=m.index+m[0].length}
    if(last<body.length)parts.push(q+body.slice(last)+q);
    const rep=parts.length===1?parts[0]:'('+parts.join('+')+')';
    edits.push([node.start,node.end,rep]);
  } else if(node.type==='TemplateLiteral'){
    const par=anc[anc.length-2];if(par&&par.type==='TaggedTemplateExpression'&&par.quasi===node)return;
    for(const q of node.quasis){const raw=src.slice(q.start,q.end);TOK.lastIndex=0;if(!TOK.test(raw))continue;TOK.lastIndex=0;
      const rep=raw.replace(TOK,(s,n)=>{handled.add(+n);return '${__ASG['+n+']}'});edits.push([q.start,q.end,rep]);}
  }
});
for(const e of edits){if(/[A-Za-z0-9_$]/.test(src[e[0]-1]||'')&&!/^["'`]/.test(e[2]))e[2]=' '+e[2]}
edits.sort((a,b)=>a[0]-b[0]);let out=[],pos=0;for(const[s0,e0,r]of edits){if(s0<pos)throw new Error('overlap');out.push(src.slice(pos,s0),r);pos=e0}out.push(src.slice(pos));
fs.writeFileSync(process.argv[3],JSON.stringify({handled:[...handled]}));fs.writeFileSync(process.argv[3]+'.js',out.join(''));
console.log('edits',edits.length,'tokens handled',handled.size);
