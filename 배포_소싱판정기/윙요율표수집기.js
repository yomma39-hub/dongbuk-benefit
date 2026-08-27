/* 쿠팡 윙 입출고배송비 요율표 수집기 v1
   - 읽기 전용: 네트워크 요청 0건, fetch/XHR 미변경
   - 윙 요금표 페이지 콘솔에 붙여넣고 실행 → 우하단 패널 등장
   - 카테고리를 손으로 바꾼 뒤 [이 표 저장] 클릭, 반복
   - 다 모으면 [JSON 내보내기]
*/
(()=>{
if(document.getElementById('wg-panel')){document.getElementById('wg-panel').style.display='block';return '패널 다시 표시'}
const KEY='wingFeeGrab_v1';
const load=()=>{try{return JSON.parse(localStorage.getItem(KEY))||[]}catch(e){return[]}};
const save=d=>localStorage.setItem(KEY,JSON.stringify(d));
const n=el=>el?parseInt(el.textContent.replace(/[^\d]/g,''),10):null;

const findTable=()=>[...document.querySelectorAll('table')].find(t=>t.rows[1]&&
  [...t.rows[1].cells].map(c=>c.innerText.trim()).join().includes('극소형'));

function cell(td){
  const q=s=>td.querySelector('[class*="'+s+'"]');
  if(td.querySelector('[class*="_not-discount-container_"]')) return [n(td.querySelector('span')),null,null];
  const o=n(q('_origin_'));
  if(td.querySelector('[class*="_discount-3-depth-container_"]')) return [o,n(q('_middle_')),n(q('_gray-final_'))];
  return [o,n(q('_blue-final_')),null];
}
function band(t){
  const s=t.replace(/\s/g,''),p=x=>parseInt(x.replace(/,/g,''),10);
  const a=s.match(/([\d,]+)원이상/),b=s.match(/([\d,]+)원미만/);
  return {min:a?p(a[1]):0,max:b?p(b[1]):null};
}
function crumb(){
  const c=[...document.querySelectorAll('div,span,p')].filter(e=>{
    const t=(e.innerText||'').replace(/\s+/g,'');return t.endsWith('재선택')&&t.length>6&&t.length<120});
  const el=c[c.length-1]; if(!el) return {raw:'',parts:[]};
  const parts=[...el.children].map(x=>(x.innerText||'').trim()).filter(x=>x&&x!=='재선택');
  return {raw:(el.innerText||'').replace(/\s+/g,' ').replace(/재선택\s*$/,'').trim(),parts};
}
function grab(){
  const t=findTable(); if(!t) return {err:'요율표를 못 찾았습니다 — 카테고리가 선택돼 있는지 확인하세요'};
  const rows=[...t.rows].filter(r=>r.cells.length===7)
    .map(r=>({...band(r.cells[0].innerText),c:[...r.cells].slice(1).map(cell)}));
  if(!rows.length) return {err:'데이터 행을 못 읽었습니다'};
  const bad=rows.filter(r=>r.c.some(x=>x[0]==null)).length;
  const cr=crumb();
  return {name:cr.parts.length?cr.parts.join(' > '):(cr.raw||'이름없음'),
          crumb:cr.raw, bandCount:rows.length, bad, rows, sig:JSON.stringify(rows)};
}
const P=document.createElement('div');P.id='wg-panel';
P.style.cssText='position:fixed;right:16px;bottom:16px;z-index:2147483647;width:260px;background:#fff;'+
 'border:1px solid #cbd5e1;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.18);'+
 'font:13px/1.5 -apple-system,BlinkMacSystemFont,"Malgun Gothic",sans-serif;color:#0f172a;padding:12px';
const B='display:block;width:100%;margin-top:6px;padding:8px;border-radius:6px;border:1px solid #cbd5e1;'+
 'background:#f8fafc;cursor:pointer;font-size:13px';
P.innerHTML='<div style="font-weight:700;margin-bottom:8px">요율표 수집기'+
 '<span id="wg-x" style="float:right;cursor:pointer;color:#94a3b8">✕</span></div>'+
 '<div id="wg-s" style="font-size:12px;color:#475569;min-height:34px"></div>'+
 '<button id="wg-save" style="'+B+';background:#2563eb;color:#fff;border-color:#2563eb;font-weight:600">이 표 저장</button>'+
 '<button id="wg-exp" style="'+B+'">JSON 내보내기</button>'+
 '<button id="wg-list" style="'+B+'">목록 보기</button>'+
 '<button id="wg-clr" style="'+B+';color:#b91c1c">전부 비우기</button>';
document.body.appendChild(P);
const S=document.getElementById('wg-s');
const stat=m=>{const d=load();S.innerHTML=(m?m+'<br>':'')+'<b>'+d.length+'</b>개 저장됨';};
stat('');
document.getElementById('wg-x').onclick=()=>P.style.display='none';
function put(g){
  const d=load(); const dup=d.find(x=>x.sig===g.sig);
  if(dup){
    if(g.name===dup.name){ stat('이미 저장돼 있습니다 — <b>'+dup.name+'</b>'); return }
    if(!dup.alias.includes(g.name)){ dup.alias.push(g.name); save(d); }
    stat('중복 — <b>'+dup.name+'</b> 에 경로만 추가'); return;
  }
  if(d.some(x=>x.name===g.name)){stat('<span style="color:#b45309">같은 이름이 이미 있습니다</span>');return}
  d.push({name:g.name,crumb:g.crumb,alias:[],rows:g.rows,sig:g.sig,at:new Date().toISOString().slice(0,10)});
  save(d); stat('저장: <b>'+g.name+'</b> ('+g.bandCount+'구간'+(g.bad?', 빈칸 '+g.bad:'')+')');
}
document.getElementById('wg-save').onclick=()=>{
  const g=grab(); if(g.err){stat('<span style="color:#b91c1c">'+g.err+'</span>');return}
  /* 정상 요율표는 11구간 또는 18구간입니다. 그보다 적으면 표가 덜 그려진 것일 수 있어
     바로 저장하지 않고 다시 확인하게 합니다. */
  if(g.bandCount<11){
    S.innerHTML='<span style="color:#b91c1c">구간이 '+g.bandCount+'개뿐입니다.</span>'
      +'<br>표가 아직 다 안 그려졌을 수 있습니다. 잠깐 뒤 [이 표 저장]을 다시 누르세요.'
      +'<br>화면에 정말 이 줄만 있으면 아래로 저장하세요.'
      +'<br><button id="wg-force" style="margin-top:5px;padding:4px 8px;font-size:11px;cursor:pointer">그래도 저장</button>';
    document.getElementById('wg-force').onclick=()=>put(g);
    return;
  }
  put(g);
};
document.getElementById('wg-list').onclick=()=>{
  const d=load(); if(!d.length){stat('비어 있습니다');return}
  S.innerHTML='<b>'+d.length+'</b>개<div style="max-height:150px;overflow:auto;margin-top:4px;font-size:11px">'+
    d.map((x,i)=>(i+1)+'. '+x.name+(x.alias.length?' <span style="color:#94a3b8">+'+x.alias.length+'</span>':'')).join('<br>')+'</div>';
};
document.getElementById('wg-exp').onclick=()=>{
  const d=load(); if(!d.length){stat('비어 있습니다');return}
  const out={source:'wing-fee-grab',version:1,grabbedAt:new Date().toISOString().slice(0,10),
    sizes:['극소형','소형','중형','대형1','대형2','특대형'],
    tiers:['정상가','할인가','전용할인가'],
    tables:d.map(x=>({name:x.name,crumb:x.crumb,alias:x.alias,at:x.at,rows:x.rows}))};
  const txt=JSON.stringify(out,null,1);
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([txt],{type:'application/json'}));
  a.download='wing_fee_'+out.grabbedAt+'.json'; a.click();
  stat('<b>'+d.length+'</b>개 파일로 저장했습니다');
};
document.getElementById('wg-clr').onclick=()=>{
  if(!confirm('저장된 요율표를 전부 지웁니다. 계속할까요?'))return;
  save([]); stat('비웠습니다');
};
return '수집기 준비 완료 — 우하단 패널을 쓰세요';
})()
