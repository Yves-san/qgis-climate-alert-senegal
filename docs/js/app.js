const COMMUNES=["Dakar","Pikine","Guediawaye","Rufisque","Thiès","Mbour","Tivaouane","Diourbel","Bambey","Mbacké","Saint-Louis","Dagana","Podor","Fatick","Foundiougne","Gossas","Kaolack","Guinguinéo","Nioro du Rip","Kaffrine","Birkelane","Malem-Hodar","Koungheul","Louga","Kebemer","Linguere","Tambacounda","Bakel","Goudiry","Koumpentoum","Kolda","Velingara","Medina Yoro Foulah","Ziguinchor","Bignona","Oussouye","Matam","Kanel","Ranerou","Kedougou","Salemata","Saraya","Sedhiou","Bounkiling","Goudomp"];

let STATE={commune:"Kaolack",scenario:"SSP1",projections:null,charts:{}};

async function loadData(){
  try{
    const res=await fetch("https://raw.githubusercontent.com/Yves-san/qgis-climate-alert-senegal/main/dashboard/projections_2025_2055.json");
    STATE.projections=await res.json();
    console.log("✅ Données chargées:",Object.keys(STATE.projections).length,"communes");
  }catch(e){
    console.warn("Fallback données démo");
    STATE.projections=generateDemo();
  }
  updateAll();
}

function generateDemo(){
  const d={};
  COMMUNES.forEach(c=>{
    const sc={};
    ["SSP1","SSP2","SSP5"].forEach(s=>{
      const n=9496,times=[],tMean=[],tMax=[],tMin=[],precip=[],eto=[],wind=[];
      let dt=new Date("2025-01-01");
      const w=s==="SSP1"?0.03:s==="SSP2"?0.05:0.09;
      for(let i=0;i<n;i++){
        const yr=(dt-new Date("2025-01-01"))/(365.25*24*3600*1000);
        const mo=dt.getMonth();
        const base=26+w*yr+Math.sin((mo-3)*Math.PI/6)*4+(Math.random()-.5)*3;
        tMean.push(+base.toFixed(1));
        tMax.push(+(base+4+Math.random()*2).toFixed(1));
        tMin.push(+(base-4-Math.random()*2).toFixed(1));
        precip.push(mo>=6&&mo<=9?+(Math.random()*15).toFixed(1):0);
        eto.push(+(3+Math.random()*4).toFixed(1));
        wind.push(+(10+Math.random()*20).toFixed(1));
        times.push(dt.toISOString().split("T")[0]);
        dt.setDate(dt.getDate()+1);
      }
      sc[s]={time:times,time_precipitation:times,temperature_2m_mean:tMean,temperature_2m_max:tMax,temperature_2m_min:tMin,precipitation_sum:precip,et0_fao_evapotranspiration:eto,windspeed_10m_max:wind};
    });
    d[c]={lat:14.5,lon:-14.5,scenarios:sc};
  });
  return d;
}

function getData(){
  if(!STATE.projections)return null;
  const c=STATE.projections[STATE.commune]||STATE.projections[Object.keys(STATE.projections)[0]];
  if(!c)return null;
  const sc=c.scenarios[STATE.scenario]||c.scenarios[Object.keys(c.scenarios)[0]];
  if(!sc)return null;
  const times=sc.time_precipitation||sc.time;
  const n=Math.min(times.length,sc.precipitation_sum.length);
  return{dates:times.slice(0,n),tMean:sc.temperature_2m_mean.slice(0,n),tMax:sc.temperature_2m_max.slice(0,n),tMin:sc.temperature_2m_min.slice(0,n),precip:sc.precipitation_sum.slice(0,n),eto:(sc.et0_fao_evapotranspiration||[]).slice(0,n),wind:(sc.windspeed_10m_max||[]).slice(0,n)};
}

function byYear(data,year){
  const idx=data.dates.reduce((a,d,i)=>{if(d.startsWith(String(year)))a.push(i);return a;},[]);
  return{dates:idx.map(i=>data.dates[i]),tMean:idx.map(i=>data.tMean[i]),tMax:idx.map(i=>data.tMax[i]),tMin:idx.map(i=>data.tMin[i]),precip:idx.map(i=>data.precip[i]),eto:idx.map(i=>data.eto[i]),wind:idx.map(i=>data.wind[i])};
}

function monthly(data){
  const m={};
  data.dates.forEach((d,i)=>{const k=d.slice(0,7);if(!m[k])m[k]={tMean:[],tMax:[],tMin:[],precip:[],wind:[]};m[k].tMean.push(data.tMean[i]);m[k].tMax.push(data.tMax[i]);m[k].tMin.push(data.tMin[i]);m[k].precip.push(data.precip[i]);m[k].wind.push(data.wind[i]||0);});
  const labels=[],tMean=[],tMax=[],tMin=[],precip=[],wind=[];
  Object.keys(m).sort().forEach(k=>{const v=m[k];labels.push(k);tMean.push(+(v.tMean.reduce((a,b)=>a+b,0)/v.tMean.length).toFixed(1));tMax.push(+(Math.max(...v.tMax)).toFixed(1));tMin.push(+(Math.min(...v.tMin)).toFixed(1));precip.push(+(v.precip.reduce((a,b)=>a+b,0)).toFixed(1));wind.push(+(v.wind.reduce((a,b)=>a+b,0)/v.wind.length).toFixed(1));});
  return{labels,tMean,tMax,tMin,precip,wind};
}

function annual(data){
  const y={};
  data.dates.forEach((d,i)=>{const k=d.slice(0,4);if(!y[k])y[k]={tMean:[],tMax:[],tMin:[],precip:[],wind:[]};y[k].tMean.push(data.tMean[i]);y[k].tMax.push(data.tMax[i]);y[k].tMin.push(data.tMin[i]);y[k].precip.push(data.precip[i]);y[k].wind.push(data.wind[i]||0);});
  const labels=[],tMean=[],tMax=[],tMin=[],precip=[],wind=[];
  Object.keys(y).sort().forEach(k=>{const v=y[k];labels.push(k);tMean.push(+(v.tMean.reduce((a,b)=>a+b,0)/v.tMean.length).toFixed(1));tMax.push(+(v.tMax.reduce((a,b)=>a+b,0)/v.tMax.length).toFixed(1));tMin.push(+(v.tMin.reduce((a,b)=>a+b,0)/v.tMin.length).toFixed(1));precip.push(+(v.precip.reduce((a,b)=>a+b,0)).toFixed(0));wind.push(+(v.wind.reduce((a,b)=>a+b,0)/v.wind.length).toFixed(1));});
  return{labels,tMean,tMax,tMin,precip,wind};
}

function spi(precip){
  const pos=precip.filter(v=>v>0);
  if(pos.length<6)return precip.map(()=>0);
  const mean=pos.reduce((a,b)=>a+b,0)/pos.length;
  const std=Math.sqrt(pos.map(v=>(v-mean)**2).reduce((a,b)=>a+b,0)/pos.length);
  return std===0?precip.map(()=>0):precip.map(v=>v===0?-2:+((v-mean)/std).toFixed(2));
}

function navigate(pageId){
  document.querySelectorAll(".main").forEach(m=>m.classList.remove("active"));
  document.querySelectorAll(".sidebar-item").forEach(i=>i.classList.remove("active"));
  const page=document.getElementById("page-"+pageId);
  if(page){page.classList.add("active");renderPage(pageId);}
  const item=document.querySelector(`[data-page="${pageId}"]`);
  if(item)item.classList.add("active");
  window.scrollTo(0,0);
}

function renderPage(id){
  const fns={apercu:renderApercu,temperature:renderTemperature,precipitations:renderPrecipitations,secheresse:renderSecheresse,alertes:renderAlertes,scenarios:renderScenarios,export:renderExport,carte:renderCarte,eau:renderEau,sols:renderSols};
  if(fns[id])fns[id]();
}

function updateAll(){
  const el=document.getElementById("nav-commune");
  if(el)el.textContent=STATE.commune;
  const active=document.querySelector(".sidebar-item.active");
  if(active)renderPage(active.dataset.page);
}

function destroyCharts(){Object.values(STATE.charts).forEach(ch=>{try{ch.destroy();}catch(e){}});STATE.charts={};}

document.addEventListener("DOMContentLoaded",()=>{
  const sel=document.getElementById("commune-select");
  if(sel){COMMUNES.forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=c;if(c===STATE.commune)o.selected=true;sel.appendChild(o);});sel.addEventListener("change",e=>{STATE.commune=e.target.value;destroyCharts();updateAll();});}
  const scSel=document.getElementById("scenario-select");
  if(scSel){scSel.addEventListener("change",e=>{STATE.scenario=e.target.value;destroyCharts();updateAll();});}
  document.querySelectorAll(".sidebar-item[data-page]").forEach(item=>{item.addEventListener("click",()=>navigate(item.dataset.page));});
  navigate("apercu");
  loadData();
});
