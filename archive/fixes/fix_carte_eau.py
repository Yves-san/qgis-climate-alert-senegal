with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    st.markdown("### 🎨 Légende types d eau")
    col1,col2,col3,col4 = st.columns(4)
    col1.markdown("🔵 Mer / Océan (salée)")
    col1.markdown("🟦 Fleuve / Rivière (douce courante)")'''

new = '''    st.markdown("### 🗺️ Carte des types d eau par commune")
    st.caption("Chaque commune est colorée selon son type d eau principal")

    import plotly.graph_objects as go
    COULEURS_EAU = {
        "eau salée":       "#0D47A1",
        "eau douce courante": "#1E88E5",
        "eau douce stagnante": "#26A69A",
        "eau saisonnière": "#66BB6A",
        "eau irriguée":    "#FDD835",
        "eau souterraine": "#8D6E63",
        "eau saumâtre":    "#FF7043",
        "eau de pluie":    "#90CAF9",
    }

    def get_type_principal(eau_types):
        for eau in eau_types:
            if any(x in eau for x in ["Mer","Atlantique","salée"]): return "eau salée"
            if any(x in eau for x in ["Fleuve","Rivière","fleuve"]): return "eau douce courante"
            if any(x in eau for x in ["Lac","lac"]): return "eau douce stagnante"
            if any(x in eau for x in ["Marigot","marigot","saisonnier"]): return "eau saisonnière"
            if any(x in eau for x in ["Canal","SAED","irrigation"]): return "eau irriguée"
            if any(x in eau for x in ["souterraine","nappe","puits","Eau ville"]): return "eau souterraine"
            if any(x in eau for x in ["saumâtre","Mangrove"]): return "eau saumâtre"
        return "eau de pluie"

    fig_types = go.Figure()
    groupes = {}
    for c, d in HYDRAULIQUE.items():
        t = get_type_principal(d["eau_types"])
        if t not in groupes:
            groupes[t] = {"lats":[],"lons":[],"noms":[],"infos":[]}
        groupes[t]["lats"].append(d["lat"])
        groupes[t]["lons"].append(d["lon"])
        groupes[t]["noms"].append(c)
        groupes[t]["infos"].append(
            f"{c}<br>Type: {t}<br>Forages: {d['forages']}<br>Puits: {d['puits']}<br>Acces: {d['acces_eau']}<br>Risque: {d['risque_penurie']}"
        )

    EMOJIS = {
        "eau salée": "🔵",
        "eau douce courante": "🟦",
        "eau douce stagnante": "🟩",
        "eau saisonnière": "🟢",
        "eau irriguée": "🟡",
        "eau souterraine": "🟤",
        "eau saumâtre": "🟠",
        "eau de pluie": "💧",
    }

    for t, g in groupes.items():
        fig_types.add_trace(go.Scattermapbox(
            lat=g["lats"], lon=g["lons"],
            mode="markers",
            name=f"{EMOJIS.get(t,'')} {t} ({len(g['lats'])})",
            marker=dict(size=14, color=COULEURS_EAU.get(t,"#fff"), opacity=0.85),
            text=g["infos"],
            hovertemplate="%{text}<extra></extra>",
        ))

    fig_types.update_layout(
        mapbox=dict(style="open-street-map", center={"lat":14.5,"lon":-14.5}, zoom=5.5),
        title="Types d eau disponibles par commune — Sénégal",
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1,
                   title=dict(text="Type d eau principal")),
    )
    st.plotly_chart(fig_types, use_container_width=True)

    st.markdown("### 🎨 Légende types d eau")
    col1,col2,col3,col4 = st.columns(4)
    col1.markdown("🔵 Mer / Océan (salée)")
    col1.markdown("🟦 Fleuve / Rivière (douce courante)")'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
