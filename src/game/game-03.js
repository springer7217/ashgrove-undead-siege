// ---------- r134 (Lee, Nov 2026): aim down sights with every gun ----------
// Right mouse (LT on a controller) only zoomed scoped / ACOG guns before; on every other gun it did nothing, though the
// Controls page says "Right mouse: Aim down sights". Now every firearm aims: the game's own ADS path does the smooth FOV zoom,
// lower sensitivity (Options > ADS sensitivity), less recoil and the zoom sound, as it already did for scoped guns. Guns
// without an optic zoom a little (x1.28), red dots / holos keep their optic zoom, scoped guns keep their scope overlay.
// While aiming without a scope a small precise crosshair shows (the normal one hides while aiming). Guns that never had an
// ADS spread keep their hip spread while aiming, so no gun's accuracy changes. Melee and tactical items don't aim.
// The held gun stays near its hip position while aiming (gun models have no sight on the screen centre).
// Options > "Aim with every gun" turns it off (back to scoped guns only). Also: letting go of the window (Alt-Tab) or the
// pointer lock now releases held mouse buttons, so the gun no longer keeps firing / aiming on its own when you come back.
{const K="ashgrove_adsAll",ON=()=>localStorage.getItem(K)!=="0";let VM=0;const A0=__acogOn;
 const bare=o=>!o||o==="iron"; // no sight attachment (gun models report optic "iron")
 const iron=w=>{let d=v[w];return!!d&&!d.scope&&!d.tactical&&!d.attrs?.melee};
 __acogOn=function(w){if(A0(w))return!0;if(VM||!ON()||!iron(w))return!1;let d=v[w];typeof d.ads!=="number"&&(d.ads=d.spread);return!0};
 // the gun models have no sight lined up with the screen centre, so for guns without an optic the held gun only shifts a
 // little toward the middle (instead of filling the screen) and the arms stay on it; the precise crosshair below does the aiming
 const P=qB.prototype,UV=P.updateViewmodel;P.updateViewmodel=function(){let a=this.ads,lo=this===h.player&&a>0&&ON()&&iron(this.wid)&&!A0(this.wid)&&bare(this.gunInfo?.optic);
  VM++;lo&&(this.ads=a*.3);try{return UV.apply(this,arguments)}finally{VM--;lo&&(this.ads=a)}};
 const ZN=P.zoomNow;P.zoomNow=function(){let z=ZN.apply(this,arguments);return ON()&&iron(this.wid)&&bare(this.gunInfo?.optic)&&!iB(this.wid,this.wup,"zoom")?Math.min(z,.78):z};
 const rel=()=>{let p=h.player;if(!p?.mouse)return;p.mouse.l=!1;p.mouse.r=!1;p.adsLatched=!1};
 addEventListener("blur",rel);document.addEventListener("pointerlockchange",()=>{document.pointerLockElement||rel()});
 // precise crosshair while aiming without a scope
 let st=document.createElement("style");st.textContent="#adsX{position:fixed;left:50%;top:50%;width:0;height:0;pointer-events:none;z-index:36;opacity:0}#adsX svg{position:absolute;left:-16px;top:-16px;overflow:visible;filter:drop-shadow(0 0 1px #000) drop-shadow(0 0 1px #000)}";document.head.appendChild(st);
 let X=document.createElement("div");X.id="adsX";X.innerHTML='<svg width="32" height="32" viewBox="-16 -16 32 32"><g stroke="#fff" stroke-width="1.6" stroke-linecap="square"><path d="M-11 0H-4M4 0H11M0 -11V-4M0 4V11"/></g><circle r="1.4" fill="#ff3b3b"/></svg>';document.body.appendChild(X);
 let o=-1;(function T(){requestAnimationFrame(T);let p=h.player,a=0;if(p&&h.running&&!p.dead&&!p.scoped&&!h.paused&&ON())a=Math.max(0,Math.min(1,((p.ads||0)-.35)/.5));a=+a.toFixed(2);a!==o&&(o=a,X.style.opacity=a)})();
 // Options: "Aim with every gun"
 let addOpt=()=>{let m=document.getElementById("optAdsMode");if(!m)return setTimeout(addOpt,1e3);if(document.getElementById("optAdsAll"))return;
  let l=document.createElement("label");l.className="row";l.innerHTML='Aim with every gun <select id="optAdsAll"><option value="1">On</option><option value="0">Scoped guns only</option></select>';
  let s=l.querySelector("select");s.value=ON()?"1":"0";s.addEventListener("change",()=>localStorage.setItem(K,s.value));(m.closest("label")||m).after(l)};addOpt()}

})();
