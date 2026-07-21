function renderApercu(){
  const data=getData();
  const page=document.getElementById("page-apercu");
  if(!data){page.querySelector(".page-subtitle").textContent="Données en cours de chargement...";return;}
  const ann=annual(data);
  const lastT=ann.tMean[ann.tMean.length-1];
  const firstT=ann.tMean[0];
  const hausse=(lastT-firstT).toFixed(1);
  const totalP=ann.precip.reduce((a,b)=>a+ +b,0);
  const moyP=(totalP/ann.precip.length).toFixed(0);
  const spiVals=spi(data.precip.filter((_,i)=>i<365));
  const spiMoy=(spiVals.reduce((a,b)=>a+b,0)/spiVals.length).toFixed(2);
  const spiClass=spiMoy<-1.5?"coral":spiMoy<-1?"amber":"teal";
  const spiLabel=spiMoy<-1.5?"Sécheresse sévère":spiMoy<-1?"Sécheresse modérée":"Conditions normales";

  page.innerHTML=`
  <div class="page-eyebrow">Vue d'ensemble</div>
  <h1 class="page-title">Aperçu <em>climatique</em></h1>
  <p class="page-subtitle">${STATE.commune} · Scénario ${STATE.scenario} · 2025–2050</p>

  <div class="metrics-row">
    <div class="metric-card">
      <div class="metric-val amber">${lastT}°C</div>
      <div class="metric-label">T° moyenne 2050</div>
    </div>
    <div class="metric-card">
      <div class="metric-val coral">+${hausse}°C</div>
      <div class="metric-label">Hausse projetée</div>
    </div>
    <div class="metric-card">
      <div class="metric-val blue">${moyP} mm</div>
      <div class="metric-label">Précip. moy. annuelle</div>
    </div>
    <div class="metric-card">
      <div class="metric-val ${spiClass}">${spiMoy}</div>
      <div class="metric-label">SPI actuel</div>
    </div>
  </div>

  <div class="alert-chip ${spiMoy<-1.5?"danger":spiMoy<-1?"warning":"ok"}">
    <div class="alert-dot-pulse"></div>
    <div>
      <strong>${spiLabel}</strong> — SPI ${spiMoy}<br>
      <span style="font-size:12px;color:var(--muted)">${STATE.commune} · ${STATE.scenario}</span>
    </div>
  </div>

  <div class="divider"></div>

  <div class="chart-card">
    <div class="chart-header">
      <div><div class="chart-title">Évolution des températures 2025–2050</div>
      <div class="chart-sub">${STATE.commune} · ${STATE.scenario}</div></div>
    </div>
    <canvas id="chart-apercu-temp" height="80"></canvas>
  </div>

  <div class="grid-2">
    <div class="chart-card">
      <div class="chart-header"><div class="chart-title">Précipitations annuelles</div></div>
      <canvas id="chart-apercu-precip" height="120"></canvas>
    </div>
    <div class="chart-card">
      <div class="chart-header"><div class="chart-title">Comparaison scénarios (T° moy.)</div></div>
      <canvas id="chart-apercu-sc" height="120"></canvas>
    </div>
  </div>`;

  // Chart températures annuelles
  STATE.charts.apercuTemp=new Chart(document.getElementById("chart-apercu-temp"),{
    type:"line",
    data:{labels:ann.labels,datasets:[
      {label:"T° max",data:ann.tMax,borderColor:"#FF6B6B",backgroundColor:"rgba(255,107,107,0.08)",tension:0.4,pointRadius:0},
      {label:"T° moyenne",data:ann.tMean,borderColor:"#F59E0B",backgroundColor:"rgba(245,158,11,0.08)",tension:0.4,pointRadius:0},
      {label:"T° min",data:ann.tMin,borderColor:"#00D4AA",backgroundColor:"rgba(0,212,170,0.08)",tension:0.4,pointRadius:0}
    ]},
    options:{responsive:true,plugins:{legend:{labels:{color:"rgba(240,244,255,0.6)",font:{size:11}}}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:10},grid:{color:"rgba(240,244,255,0.04)"}},y:{ticks:{color:"rgba(240,244,255,0.4)",callback:v=>v+"°C"},grid:{color:"rgba(240,244,255,0.04)"}}}}
  });

  // Chart précipitations
  STATE.charts.apercuPrecip=new Chart(document.getElementById("chart-apercu-precip"),{
    type:"bar",
    data:{labels:ann.labels,datasets:[{label:"Précip. (mm)",data:ann.precip,backgroundColor:"rgba(96,165,250,0.6)",borderColor:"#60A5FA",borderWidth:1}]},
    options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:8},grid:{display:false}},y:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{color:"rgba(240,244,255,0.04)"}}}}
  });

  // Chart comparaison scénarios
  if(STATE.projections){
    const sc1=annual(getData());
    STATE.scenario="SSP2";const sc2=annual(getData());
    STATE.scenario="SSP5";const sc3=annual(getData());
    STATE.scenario=document.getElementById("scenario-select").value||"SSP1";
    STATE.charts.apercuSc=new Chart(document.getElementById("chart-apercu-sc"),{
      type:"line",
      data:{labels:sc1.labels,datasets:[
        {label:"SSP1",data:sc1.tMean,borderColor:"#00D4AA",tension:0.4,pointRadius:0},
        {label:"SSP2",data:sc2.tMean,borderColor:"#F59E0B",tension:0.4,pointRadius:0},
        {label:"SSP5",data:sc3.tMean,borderColor:"#FF6B6B",tension:0.4,pointRadius:0}
      ]},
      options:{responsive:true,plugins:{legend:{labels:{color:"rgba(240,244,255,0.6)",font:{size:11}}}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:8},grid:{display:false}},y:{ticks:{color:"rgba(240,244,255,0.4)",callback:v=>v+"°C"},grid:{color:"rgba(240,244,255,0.04)"}}}}
    });
  }
}

function renderTemperature(){
  const data=getData();
  const page=document.getElementById("page-temperature");
  if(!data){return;}
  const ann=annual(data);
  page.innerHTML=`
  <div class="page-eyebrow">Températures</div>
  <h1 class="page-title">Température — <em>${STATE.commune}</em></h1>
  <p class="page-subtitle">Projections journalières 2025–2050 · ${STATE.scenario}</p>
  <div class="metrics-row">
    <div class="metric-card"><div class="metric-val coral">${Math.max(...ann.tMax).toFixed(1)}°C</div><div class="metric-label">T° max absolue</div></div>
    <div class="metric-card"><div class="metric-val amber">${(ann.tMean.reduce((a,b)=>a+b,0)/ann.tMean.length).toFixed(1)}°C</div><div class="metric-label">T° moyenne 2025-2050</div></div>
    <div class="metric-card"><div class="metric-val teal">${Math.min(...ann.tMin).toFixed(1)}°C</div><div class="metric-label">T° min absolue</div></div>
    <div class="metric-card"><div class="metric-val blue">+${(ann.tMean[ann.tMean.length-1]-ann.tMean[0]).toFixed(1)}°C</div><div class="metric-label">Hausse projetée</div></div>
  </div>
  <div class="chart-card">
    <div class="chart-header">
      <div><div class="chart-title">Évolution annuelle des températures</div><div class="chart-sub">${STATE.commune} · ${STATE.scenario}</div></div>
    </div>
    <canvas id="chart-temp-ann" height="80"></canvas>
  </div>
  <div class="chart-card">
    <div class="chart-header"><div class="chart-title">Températures mensuelles (dernière année)</div></div>
    <canvas id="chart-temp-mois" height="100"></canvas>
  </div>`;

  const MOIS=["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"];
  const last=byYear(data,2050);
  const mo=monthly(last);

  STATE.charts.tempAnn=new Chart(document.getElementById("chart-temp-ann"),{
    type:"line",
    data:{labels:ann.labels,datasets:[
      {label:"T° max",data:ann.tMax,borderColor:"#FF6B6B",tension:0.4,pointRadius:0,fill:false},
      {label:"T° moy",data:ann.tMean,borderColor:"#F59E0B",tension:0.4,pointRadius:0,fill:false},
      {label:"T° min",data:ann.tMin,borderColor:"#00D4AA",tension:0.4,pointRadius:0,fill:false}
    ]},
    options:{responsive:true,plugins:{legend:{labels:{color:"rgba(240,244,255,0.6)",font:{size:11}}}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:10},grid:{color:"rgba(240,244,255,0.04)"}},y:{ticks:{color:"rgba(240,244,255,0.4)",callback:v=>v+"°C"},grid:{color:"rgba(240,244,255,0.04)"}}}}
  });

  STATE.charts.tempMois=new Chart(document.getElementById("chart-temp-mois"),{
    type:"bar",
    data:{labels:mo.labels.map(l=>MOIS[parseInt(l.split("-")[1])-1]||l),datasets:[
      {label:"T° max",data:mo.tMax,backgroundColor:"rgba(255,107,107,0.7)"},
      {label:"T° moy",data:mo.tMean,backgroundColor:"rgba(245,158,11,0.7)"},
      {label:"T° min",data:mo.tMin,backgroundColor:"rgba(0,212,170,0.7)"}
    ]},
    options:{responsive:true,plugins:{legend:{labels:{color:"rgba(240,244,255,0.6)",font:{size:11}}}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{display:false}},y:{ticks:{color:"rgba(240,244,255,0.4)",callback:v=>v+"°C"},grid:{color:"rgba(240,244,255,0.04)"}}}}
  });
}

function renderPrecipitations(){
  const data=getData();
  const page=document.getElementById("page-precipitations");
  if(!data)return;
  const ann=annual(data);
  const moyAnn=(ann.precip.reduce((a,b)=>a+ +b,0)/ann.precip.length).toFixed(0);
  page.innerHTML=`
  <div class="page-eyebrow">Précipitations</div>
  <h1 class="page-title"><em>Pluies</em> & Vents</h1>
  <p class="page-subtitle">${STATE.commune} · ${STATE.scenario} · 2025–2050</p>
  <div class="metrics-row">
    <div class="metric-card"><div class="metric-val blue">${moyAnn} mm</div><div class="metric-label">Précip. moy. annuelle</div></div>
    <div class="metric-card"><div class="metric-val teal">${Math.max(...ann.precip.map(Number)).toFixed(0)} mm</div><div class="metric-label">Année la plus humide</div></div>
    <div class="metric-card"><div class="metric-val amber">${Math.min(...ann.precip.map(Number)).toFixed(0)} mm</div><div class="metric-label">Année la plus sèche</div></div>
    <div class="metric-card"><div class="metric-val coral">${(ann.wind.reduce((a,b)=>a+b,0)/ann.wind.length).toFixed(1)} km/h</div><div class="metric-label">Vent moyen</div></div>
  </div>
  <div class="chart-card">
    <div class="chart-header"><div class="chart-title">Précipitations annuelles 2025–2050</div></div>
    <canvas id="chart-precip-ann" height="90"></canvas>
  </div>
  <div class="chart-card">
    <div class="chart-header"><div class="chart-title">Répartition mensuelle (moyenne sur la période)</div></div>
    <canvas id="chart-precip-mois" height="100"></canvas>
  </div>`;

  STATE.charts.precipAnn=new Chart(document.getElementById("chart-precip-ann"),{
    type:"bar",
    data:{labels:ann.labels,datasets:[{label:"Précip. totale (mm)",data:ann.precip,backgroundColor:"rgba(96,165,250,0.6)",borderColor:"#60A5FA",borderWidth:1}]},
    options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:10},grid:{display:false}},y:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{color:"rgba(240,244,255,0.04)"}}}}
  });

  // Moyenne mensuelle sur toute la période
  const allMo=monthly(data);
  const byMonth=Array(12).fill(0).map(()=>[]);
  allMo.labels.forEach((l,i)=>{const m=parseInt(l.split("-")[1])-1;byMonth[m].push(+allMo.precip[i]);});
  const moyMois=byMonth.map(v=>v.length?+(v.reduce((a,b)=>a+b,0)/v.length).toFixed(1):0);
  const MOIS=["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"];

  STATE.charts.precipMois=new Chart(document.getElementById("chart-precip-mois"),{
    type:"bar",
    data:{labels:MOIS,datasets:[{label:"Précip. moy. (mm)",data:moyMois,backgroundColor:moyMois.map(v=>v>50?"rgba(96,165,250,0.8)":v>20?"rgba(96,165,250,0.5)":"rgba(245,158,11,0.5)"),borderWidth:0}]},
    options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{display:false}},y:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{color:"rgba(240,244,255,0.04)"}}}}
  });
}

function renderSecheresse(){
  const data=getData();
  const page=document.getElementById("page-secheresse");
  if(!data)return;
  const allMo=monthly(data);
  const spiVals=spi(allMo.precip.map(Number));
  const spiMoy=(spiVals.reduce((a,b)=>a+b,0)/spiVals.length).toFixed(2);
  const nSevere=spiVals.filter(v=>v<-1.5).length;
  const nExtreme=spiVals.filter(v=>v<-2).length;

  page.innerHTML=`
  <div class="page-eyebrow">Sécheresse</div>
  <h1 class="page-title">Indice <em>SPI</em></h1>
  <p class="page-subtitle">${STATE.commune} · ${STATE.scenario} · Standardized Precipitation Index</p>
  <div class="metrics-row">
    <div class="metric-card"><div class="metric-val ${spiMoy<-1.5?"coral":spiMoy<-1?"amber":"teal"}">${spiMoy}</div><div class="metric-label">SPI moyen</div></div>
    <div class="metric-card"><div class="metric-val amber">${nSevere}</div><div class="metric-label">Mois sévères (SPI&lt;-1.5)</div></div>
    <div class="metric-card"><div class="metric-val coral">${nExtreme}</div><div class="metric-label">Mois extrêmes (SPI&lt;-2)</div></div>
    <div class="metric-card"><div class="metric-val blue">${spiVals.filter(v=>v>1).length}</div><div class="metric-label">Mois excédentaires</div></div>
  </div>
  <div class="chart-card">
    <div class="chart-header"><div class="chart-title">Indice SPI mensuel 2025–2050</div><div class="chart-sub">Négatif = déficit · Positif = excédent</div></div>
    <canvas id="chart-spi" height="90"></canvas>
  </div>`;

  STATE.charts.spi=new Chart(document.getElementById("chart-spi"),{
    type:"bar",
    data:{labels:allMo.labels,datasets:[{label:"SPI",data:spiVals,backgroundColor:spiVals.map(v=>v<-2?"rgba(255,107,107,0.8)":v<-1.5?"rgba(255,107,107,0.5)":v<-1?"rgba(245,158,11,0.6)":v>1?"rgba(0,212,170,0.6)":"rgba(96,165,250,0.4)"),borderWidth:0}]},
    options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{ticks:{color:"rgba(240,244,255,0.3)",maxTicksLimit:12},grid:{display:false}},y:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{color:"rgba(240,244,255,0.04)"},suggestedMin:-3,suggestedMax:3}}}
  });
}

function renderAlertes(){
  const data=getData();
  const page=document.getElementById("page-alertes");
  if(!data)return;
  const today=new Date().toISOString().split("T")[0];
  const idx=data.dates.indexOf(today);
  const i=idx>=0?idx:0;
  const tmax=data.tMax[i]||35;
  const pluie=data.precip[i]||0;
  const alertT=tmax>=42?"danger":tmax>=38?"warning":"ok";
  const alertP=pluie>=20?"ok":pluie>=5?"ok":pluie>=1?"warning":"danger";

  const conseilT=tmax>=42?
    "🔴 CHALEUR EXTRÊME — Ne travaillez pas aux champs entre 10h et 18h. Hydratez-vous (3L/jour minimum). Mettez les animaux à l'ombre.":
    tmax>=38?"🟠 JOURNÉE TRÈS CHAUDE — Travaillez tôt le matin (6h-10h) ou en soirée. Arrosez matin et soir.":
    tmax>=35?"🟡 JOURNÉE CHAUDE — Conditions normales pour le Sénégal. Évitez les heures les plus chaudes (13h-15h).":
    "🟢 BONNE JOURNÉE — Excellentes conditions pour travailler aux champs.";

  const conseilP=pluie>=20?"🌧️ Forte pluie — Bonne journée pour les cultures. Pas besoin d'arroser.":
    pluie>=5?"🌦️ Pluie modérée — Les plantes seront bien arrosées naturellement.":
    pluie>=1?"🌂 Petite pluie — Insuffisant pour les cultures. Arrosage complémentaire conseillé.":
    "☀️ Pas de pluie — Pensez à arroser vos cultures.";

  page.innerHTML=`
  <div class="page-eyebrow">Alertes</div>
  <h1 class="page-title">Alertes & <em>Conseils</em></h1>
  <p class="page-subtitle">${STATE.commune} · Aujourd'hui ${today}</p>
  <div class="metrics-row">
    <div class="metric-card"><div class="metric-val coral">${tmax.toFixed(1)}°C</div><div class="metric-label">T° max aujourd'hui</div></div>
    <div class="metric-card"><div class="metric-val teal">${data.tMin[i]?.toFixed(1)||"--"}°C</div><div class="metric-label">T° min aujourd'hui</div></div>
    <div class="metric-card"><div class="metric-val blue">${pluie.toFixed(1)} mm</div><div class="metric-label">Pluie prévue</div></div>
    <div class="metric-card"><div class="metric-val amber">${data.wind[i]?.toFixed(0)||"--"} km/h</div><div class="metric-label">Vent max</div></div>
  </div>
  <div class="alert-chip ${alertT}"><div class="alert-dot-pulse"></div><div><strong>Température</strong><br><span style="font-size:13px">${conseilT}</span></div></div>
  <div class="alert-chip ${alertP}"><div class="alert-dot-pulse"></div><div><strong>Précipitations</strong><br><span style="font-size:13px">${conseilP}</span></div></div>
  <div class="divider"></div>
  <h3 style="font-size:16px;margin-bottom:16px">🌾 Conseils par culture</h3>
  <div class="grid-3">
    <div class="feature-card"><div class="feature-icon">🥜</div><div class="feature-title">Arachide</div><div class="feature-desc">${tmax>=38?"Stress hydrique élevé. Variétés résistantes recommandées.":"Conditions favorables pour la croissance."}</div></div>
    <div class="feature-card"><div class="feature-icon">🌾</div><div class="feature-title">Mil / Sorgho</div><div class="feature-desc">${tmax>=38?"Décaler les semis. Irrigation d'appoint si disponible.":"Bonne période de croissance."}</div></div>
    <div class="feature-card"><div class="feature-icon">🐄</div><div class="feature-title">Fourrage</div><div class="feature-desc">${pluie<1?"Pâturages sous pression. Stocks préventifs recommandés.":"Bonne disponibilité des pâturages."}</div></div>
  </div>`;
}

function renderScenarios(){
  const page=document.getElementById("page-scenarios");
  if(!STATE.projections)return;
  const prevSc=STATE.scenario;
  STATE.scenario="SSP1";const d1=annual(getData());
  STATE.scenario="SSP2";const d2=annual(getData());
  STATE.scenario="SSP5";const d3=annual(getData());
  STATE.scenario=prevSc;

  page.innerHTML=`
  <div class="page-eyebrow">Comparaison</div>
  <h1 class="page-title">Scénarios <em>SSP</em></h1>
  <p class="page-subtitle">${STATE.commune} · Comparaison SSP1 / SSP2 / SSP5</p>
  <div class="grid-3">
    <div class="feature-card"><div class="feature-icon" style="color:var(--teal)">🟢 SSP1-1.9</div><div class="feature-title">Développement durable</div><div class="feature-desc">T° 2050 : <strong>${d1.tMean[d1.tMean.length-1]}°C</strong><br>Hausse : +${(d1.tMean[d1.tMean.length-1]-d1.tMean[0]).toFixed(1)}°C</div></div>
    <div class="feature-card"><div class="feature-icon" style="color:var(--amber)">🟡 SSP2-4.5</div><div class="feature-title">Chemin actuel</div><div class="feature-desc">T° 2050 : <strong>${d2.tMean[d2.tMean.length-1]}°C</strong><br>Hausse : +${(d2.tMean[d2.tMean.length-1]-d2.tMean[0]).toFixed(1)}°C</div></div>
    <div class="feature-card"><div class="feature-icon" style="color:var(--coral)">🔴 SSP5-8.5</div><div class="feature-title">Émissions élevées</div><div class="feature-desc">T° 2050 : <strong>${d3.tMean[d3.tMean.length-1]}°C</strong><br>Hausse : +${(d3.tMean[d3.tMean.length-1]-d3.tMean[0]).toFixed(1)}°C</div></div>
  </div>
  <div class="chart-card" style="margin-top:20px">
    <div class="chart-header"><div class="chart-title">Températures moyennes par scénario</div></div>
    <canvas id="chart-sc-temp" height="80"></canvas>
  </div>
  <div class="chart-card">
    <div class="chart-header"><div class="chart-title">Précipitations par scénario</div></div>
    <canvas id="chart-sc-precip" height="80"></canvas>
  </div>`;

  STATE.charts.scTemp=new Chart(document.getElementById("chart-sc-temp"),{type:"line",data:{labels:d1.labels,datasets:[{label:"SSP1",data:d1.tMean,borderColor:"#00D4AA",tension:0.4,pointRadius:0},{label:"SSP2",data:d2.tMean,borderColor:"#F59E0B",tension:0.4,pointRadius:0},{label:"SSP5",data:d3.tMean,borderColor:"#FF6B6B",tension:0.4,pointRadius:0}]},options:{responsive:true,plugins:{legend:{labels:{color:"rgba(240,244,255,0.6)",font:{size:11}}}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:10},grid:{color:"rgba(240,244,255,0.04)"}},y:{ticks:{color:"rgba(240,244,255,0.4)",callback:v=>v+"°C"},grid:{color:"rgba(240,244,255,0.04)"}}}}});

  STATE.charts.scPrecip=new Chart(document.getElementById("chart-sc-precip"),{type:"line",data:{labels:d1.labels,datasets:[{label:"SSP1",data:d1.precip,borderColor:"#00D4AA",tension:0.4,pointRadius:0},{label:"SSP2",data:d2.precip,borderColor:"#F59E0B",tension:0.4,pointRadius:0},{label:"SSP5",data:d3.precip,borderColor:"#FF6B6B",tension:0.4,pointRadius:0}]},options:{responsive:true,plugins:{legend:{labels:{color:"rgba(240,244,255,0.6)",font:{size:11}}}},scales:{x:{ticks:{color:"rgba(240,244,255,0.4)",maxTicksLimit:10},grid:{color:"rgba(240,244,255,0.04)"}},y:{ticks:{color:"rgba(240,244,255,0.4)"},grid:{color:"rgba(240,244,255,0.04)"}}}}});
}

function renderCarte(){
  document.getElementById("page-carte").innerHTML=`
  <div class="page-eyebrow">Carte</div>
  <h1 class="page-title">Carte <em>Interactive</em></h1>
  <p class="page-subtitle">Carte des 46 départements — en cours de développement</p>
  <div class="chart-card" style="height:400px;display:flex;align-items:center;justify-content:center">
    <div style="text-align:center;color:var(--muted)">🗺️<br><br>Carte Leaflet + GeoJSON<br><span style="font-size:12px">Prochaine étape</span></div>
  </div>`;}

function renderEau(){
  document.getElementById("page-eau").innerHTML=`
  <div class="page-eyebrow">Ressources</div>
  <h1 class="page-title">Eau & <em>Forages</em></h1>
  <p class="page-subtitle">4 218 forages PNADT — en cours d'intégration</p>
  <div class="chart-card" style="height:300px;display:flex;align-items:center;justify-content:center">
    <div style="text-align:center;color:var(--muted)">💧<br><br>Carte hydraulique<br><span style="font-size:12px">Prochaine étape</span></div>
  </div>`;}

function renderSols(){
  document.getElementById("page-sols").innerHTML=`
  <div class="page-eyebrow">Agriculture</div>
  <h1 class="page-title">Sols & <em>Calendrier Cultural</em></h1>
  <p class="page-subtitle">Recommandations agricoles par saison</p>
  <div class="table-wrap"><table>
  <tr><th>Mois</th><th>Saison</th><th>Arachide</th><th>Mil</th><th>Sorgho</th></tr>
  <tr><td>Jan–Mar</td><td>Saison sèche froide</td><td>—</td><td>—</td><td>—</td></tr>
  <tr><td>Avr–Jun</td><td>Saison sèche chaude</td><td>Préparation sol</td><td>Préparation</td><td>Préparation</td></tr>
  <tr><td>Jul–Sep</td><td>🌧️ Hivernage</td><td>✅ Semis & croissance</td><td>✅ Semis</td><td>✅ Semis</td></tr>
  <tr><td>Oct–Nov</td><td>Fin hivernage</td><td>✅ Récolte</td><td>✅ Récolte</td><td>✅ Récolte</td></tr>
  <tr><td>Déc</td><td>Saison sèche</td><td>Stockage</td><td>Stockage</td><td>Stockage</td></tr>
  </table></div>`;}

function renderExport(){
  const page=document.getElementById("page-export");
  page.innerHTML=`
  <div class="page-eyebrow">Export</div>
  <h1 class="page-title">Exporter les <em>données</em></h1>
  <p class="page-subtitle">${STATE.commune} · ${STATE.scenario}</p>
  <div class="grid-2">
    <div class="feature-card"><div class="feature-icon">🌡️</div><div class="feature-title">Températures CSV</div><div class="feature-desc">Export journalier 2025–2050 — T° min, max, moyenne</div><br><button class="btn btn-primary" onclick="exportCSV('temp')">Télécharger CSV</button></div>
    <div class="feature-card"><div class="feature-icon">🌧️</div><div class="feature-title">Précipitations CSV</div><div class="feature-desc">Export journalier 2025–2050 — précipitations & vent</div><br><button class="btn btn-primary" onclick="exportCSV('precip')">Télécharger CSV</button></div>
  </div>`;
}

function exportCSV(type){
  const data=getData();if(!data)return;
  let csv,filename;
  if(type==="temp"){
    csv="date,t_mean,t_max,t_min\n"+data.dates.map((d,i)=>`${d},${data.tMean[i]},${data.tMax[i]},${data.tMin[i]}`).join("\n");
    filename=`temperature_${STATE.commune}_${STATE.scenario}.csv`;
  }else{
    csv="date,precipitation,vent\n"+data.dates.map((d,i)=>`${d},${data.precip[i]},${data.wind[i]||0}`).join("\n");
    filename=`precipitation_${STATE.commune}_${STATE.scenario}.csv`;
  }
  const blob=new Blob([csv],{type:"text/csv"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=filename;a.click();
}
