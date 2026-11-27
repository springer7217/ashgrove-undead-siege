/* Ashgrove: Undead Siege by Evan - loading-screen progress bar.
   Shows real download progress for the embedded-data chunks (sizes from asset-index.js, completion from the browser's
   Resource Timing entries, so nothing is downloaded twice), then the start-up stages. Runs before the data <script> tags;
   it only reads timing data and updates its own two elements inside #loading. It is an external file on purpose: the game
   expects exactly two large inline scripts on the page. */
(function(){
  var X=window.__ASGIDX||[],L=document.getElementById("loading");if(!L||!X.length||!window.performance)return;
  var tot=0,size={},done={},nDone=0,bytes=0,stage="",rank=0;
  for(var i=0;i<X.length;i++){tot+=X[i][1];size[X[i][0]]=X[i][1]}
  var box=document.createElement("div");box.className="lsP";
  box.innerHTML='<div class="lsPT">Loading game data...</div><div class="lsPB"><i></i></div>';L.appendChild(box);
  var T=box.firstChild,F=box.lastChild.firstChild,lsL=L.querySelector(".lsL");lsL&&(lsL.style.visibility="hidden");
  function mb(b){return Math.round(b/1e6)}
  function paint(){
    if(stage){T.textContent=stage;F.style.width="100%";box.classList.add("lsPS");return}
    var cur=X.length-1;for(var i=0;i<X.length;i++)if(!done[X[i][0]]){cur=i;break}
    var p=bytes/tot;F.style.width=(p*100).toFixed(1)+"%";
    T.textContent="Loading "+X[cur][2]+": chunk "+(cur+1)+"/"+X.length+" \u00b7 "+Math.floor(p*100)+"% \u00b7 "+mb(bytes)+"/"+mb(tot)+" MB";
  }
  function seen(name){var j=name.indexOf("assets/data/");if(j<0)return;var k=name.slice(j).split(/[?#]/)[0];
    if(k in size&&!done[k]){done[k]=1;nDone++;bytes+=size[k]}}
  function scan(list){for(var i=0;i<list.length;i++)list[i].responseEnd>0&&seen(list[i].name);
    nDone===X.length&&go(1,"Unpacking game data...");paint()}
  // start-up stages only move forward (the game can finish starting before DOMContentLoaded fires)
  function go(r,s){if(r>rank){rank=r;stage=s;paint()}}
  try{new PerformanceObserver(function(l){scan(l.getEntries())}).observe({type:"resource",buffered:true})}catch(e){}
  var iv=setInterval(function(){scan(performance.getEntriesByType("resource"));L.style.display==="none"&&clearInterval(iv)},250);
  document.addEventListener("DOMContentLoaded",function(){go(2,"Decoding audio and textures...")});
  var H=window.__lsHide;window.__lsHide=function(){go(3,"Starting game...");return H&&H.apply(this,arguments)};
  // the loading-screen artwork is a CSS background and would otherwise queue behind 250 MB of data: fetch it first
  var m=/url\(["']?([^"')]+)/.exec(L.style.backgroundImage||"");if(m){var im=new Image();im.fetchPriority="high";im.src=m[1]}
  paint();
})();
