with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    for nom in sorted(noms):\n        st.markdown(f"- {nom}")\n\n\nimport json as _json'

new = '''    for nom in sorted(noms):
        st.markdown(f"- {nom}")

    st.markdown("---")
    st.markdown("### Carte superposee — Reseau hydraulique et forages")
    st.caption("Traits bleus = cours d eau. Points = 4218 forages officiels PNADT")
    import json as __json2
    import os as __os2
    chemin_forages = __os2.path.join(__os2.path.dirname(__file__), "data", "forages_senegal.geojson")
    if __os2.path.exists(chemin_forages):
        with open(chemin_forages, encoding="utf-8") as __f2:
            forages_gj = __json2.load(__f2)
        fig_sup = go.Figure()
        for feat in gj_hydro["features"]:
            geom = feat["geometry"]
            props = feat["properties"]
            type_cours = props.get("type","")
            couleur = "#1565C0" if "Main" in type_cours else "#42A5F5" if "Canal" in type_cours else "#90CAF9"
            if geom["type"] == "LineString":
                lons = [c[0] for c in geom["coordinates"]]
                lats = [c[1] for c in geom["coordinates"]]
                fig_sup.add_trace(go.Scattermapbox(
                    lon=lons, lat=lats, mode="lines",
                    line=dict(color=couleur, width=2),
                    showlegend=False, hoverinfo="skip",
                ))
        COULEURS_NAPPE = {
            "Maastrichtien":"#0D47A1","Eocene":"#1565C0",
            "Socle paleocene":"#1976D2","Paleocene":"#1E88E5",
            "Continental":"#42A5F5","Quaternaire":"#90CAF9",
            "Oligo-miocene":"#0097A7","Infrabasalt":"#00695C",
        }
        groupes_f = {}
        for feat in forages_gj["features"]:
            p = feat["properties"]
            nappe = p.get("nappe","Autre")
            lon = feat["geometry"]["coordinates"][0]
            lat = feat["geometry"]["coordinates"][1]
            if nappe not in groupes_f:
                groupes_f[nappe] = {"lons":[],"lats":[],"noms":[]}
            groupes_f[nappe]["lons"].append(lon)
            groupes_f[nappe]["lats"].append(lat)
            groupes_f[nappe]["noms"].append(p.get("nom",""))
        for nappe, d in sorted(groupes_f.items()):
            fig_sup.add_trace(go.Scattermapbox(
                lon=d["lons"], lat=d["lats"], mode="markers",
                name=f"{nappe} ({len(d['lons'])})",
                marker=dict(size=4, color=COULEURS_NAPPE.get(nappe,"#4db8ff"), opacity=0.7),
                text=d["noms"],
                hovertemplate="<b>%{text}</b><br>" + nappe + "<extra></extra>",
            ))
        fig_sup.update_layout(
            mapbox=dict(style="open-street-map", center={"lat":14.5,"lon":-14.5}, zoom=5.8),
            title="Reseau hydraulique + 4218 forages PNADT — Senegal",
            height=700, margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor="#0a0f1e", font_color="#e8f4fd",
            legend=dict(bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1),
        )
        st.plotly_chart(fig_sup, use_container_width=True)
    else:
        st.warning("Fichier forages non trouve")


import json as _json'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
