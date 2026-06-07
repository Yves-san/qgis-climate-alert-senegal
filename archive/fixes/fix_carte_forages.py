with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    st.markdown("### 🗺️ Carte réseau hydraulique — 46 communes")

    variable_carte = st.selectbox("Afficher sur la carte",["Forages","Puits","Périmètre irrigué (ha)"])

    map_rows = []
    for c,d in HYDRAULIQUE.items():
        map_rows.append({
            "commune":c,"lat":d["lat"],"lon":d["lon"],
            "Forages":d["forages"],"Puits":d["puits"],
            "Périmètre irrigué (ha)":d["perimetre_irrigue_ha"],
            "Accès eau":d["acces_eau"],"Risque":d["risque_penurie"],
            "Fleuves":d["fleuves"],"Nappe":d["nappe"],
        })
    df_map = pd.DataFrame(map_rows)

    cscale = {"Forages":"Blues","Puits":"Greens","Périmètre irrigué (ha)":"YlOrBr"}

    fig_map = px.scatter_mapbox(
        df_map, lat="lat", lon="lon",
        hover_name="commune",
        hover_data={"Forages":True,"Puits":True,"Périmètre irrigué (ha)":True,"Accès eau":True,"Risque":True,"lat":False,"lon":False},
        color=variable_carte,
        size=variable_carte,
        size_max=25,
        color_continuous_scale=cscale[variable_carte],
        zoom=5.5,
        center={"lat":14.5,"lon":-14.5},
        mapbox_style="open-street-map",
        title=f"Réseau hydraulique Sénégal - {variable_carte}",
    )
    fig_map.update_layout(height=600,margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map,use_container_width=True)'''

new = '''    st.markdown("### 🗺️ Carte des 4218 forages officiels du Sénégal")
    st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")
    afficher_carte_forages()'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
