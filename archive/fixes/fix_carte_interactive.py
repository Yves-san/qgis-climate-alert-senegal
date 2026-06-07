with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''elif page == "🗺️ Carte Interactive":
    st.markdown("# 🗺️ Carte Interactive")
    c1,c2 = st.columns(2)
    with c1: year = st.slider("Année",2025,2055,2030)
    with c2: variable = st.selectbox("Variable",["temp_mean","temp_max","precip_total","drought","heat_stress"],format_func=lambda x:{"temp_mean":"🌡️ T° moyenne","temp_max":"🔥 T° max","precip_total":"🌧️ Précipitations","drought":"🏜️ Sécheresse","heat_stress":"⚡ Stress thermique"}[x])
    df_map = get_all_map(selected_scenario, year)
    if not df_map.empty:
        cscales = {"temp_mean":"Reds","temp_max":"hot","precip_total":"Blues","drought":"YlOrRd","heat_stress":"Oranges"}
        labels  = {"temp_mean":"T° moy (°C)","temp_max":"T° max (°C)","precip_total":"Précip (mm)","drought":"Sécheresse","heat_stress":"Stress"}
        fig = px.scatter_mapbox(df_map,lat="latitude",lon="longitude",hover_name="commune_name",hover_data={"region":True,variable:True,"latitude":False,"longitude":False},color=variable,color_continuous_scale=cscales[variable],size_max=18,zoom=5.5,center={"lat":14.5,"lon":-14.5},mapbox_style="open-street-map",title=f"{labels[variable]} - {year} - {selected_scenario}")
        fig.update_layout(height=600,margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig,use_container_width=True)'''

new = '''elif page == "🗺️ Carte Interactive":
    st.markdown("# 🗺️ Carte Climatique du Sénégal")

    # Mapping DB → GeoJSON
    NOM_MAP = {
        'Thies': 'Thiès', 'Kebemer': 'Kébémer', 'Kedougou': 'Kédougou',
        'Linguere': 'Linguère', 'Mbacke': 'Mbacké', 'Sedhiou': 'Sédhiou',
        'Guediawaye': 'Guédiawaye', 'Medina Yoro Fula': 'Médina Yoro Foulah',
        'Velingara': 'Vélingara', 'Ranérou': 'Ranérou',
        'Bargny': 'Rufisque', 'Khombole': 'Thiès',
        'Mekhe': 'Tivaouane', 'Richard-Toll': 'Dagana',
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        variable = st.selectbox("Variable", ["temp_mean","temp_max","precip_total","drought","heat_stress"],
            format_func=lambda x: {"temp_mean":"🌡️ T° moyenne","temp_max":"🔥 T° max",
            "precip_total":"🌧️ Précipitations","drought":"🏜️ Sécheresse","heat_stress":"⚡ Stress thermique"}[x])
    with c2:
        fond_ci = st.selectbox("🗺️ Fond de carte", ["🗺️ OpenStreetMap","🌙 Sombre","⬜ Clair","🔵 Blanc"],
            key="fond_ci")
        style_ci = {"🗺️ OpenStreetMap":"open-street-map","🌙 Sombre":"carto-darkmatter",
                    "⬜ Clair":"carto-positron","🔵 Blanc":"white-bg"}[fond_ci]
    with c3:
        year = st.slider("📅 Année", 2025, 2055, 2030)

    df_map = get_all_map(selected_scenario, year)

    if not df_map.empty:
        import json as _json
        with open(os.path.join(os.path.dirname(__file__), "data", "senegal_communes.geojson"), encoding="utf-8") as _f:
            geojson = _json.load(_f)

        # Appliquer le mapping des noms
        df_map["geo_name"] = df_map["commune_name"].apply(lambda x: NOM_MAP.get(x, x))

        cscales = {"temp_mean":[[0,"#ffffb2"],[0.25,"#fecc5c"],[0.5,"#fd8d3c"],[0.75,"#f03b20"],[1,"#bd0026"]],
                   "temp_max":[[0,"#fff7bc"],[0.5,"#ff7f00"],[1,"#a50f15"]],
                   "precip_total":[[0,"#f7fbff"],[0.5,"#6baed6"],[1,"#08306b"]],
                   "drought":[[0,"#ffffcc"],[0.5,"#fd8d3c"],[1,"#800026"]],
                   "heat_stress":[[0,"#ffeda0"],[0.5,"#feb24c"],[1,"#b10026"]]}
        labels = {"temp_mean":"T° moyenne (°C)","temp_max":"T° max (°C)",
                  "precip_total":"Précipitations (mm)","drought":"Indice Sécheresse","heat_stress":"Stress thermique"}

        fig = px.choropleth_mapbox(
            df_map,
            geojson=geojson,
            locations="geo_name",
            featureidkey="properties.name",
            color=variable,
            color_continuous_scale=cscales[variable],
            mapbox_style=style_ci,
            zoom=5.5,
            center={"lat": 14.5, "lon": -14.5},
            opacity=0.75,
            hover_name="commune_name",
            hover_data={variable: True, "geo_name": False},
            title=f"{labels[variable]} — {year} — {selected_scenario}",
            labels={variable: labels[variable]},
        )
        fig.update_layout(
            height=650,
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor="#0a0f1e",
            font_color="#e8f4fd",
            coloraxis_colorbar=dict(
                title=labels[variable],
                thickness=15, len=0.6,
                bgcolor="#0d1527",
                bordercolor="#2a4a7f",
                tickfont=dict(color="#e8f4fd"),
                titlefont=dict(color="#e8f4fd"),
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

        # Stats rapides
        st.markdown("---")
        c1,c2,c3 = st.columns(3)
        c1.metric(f"🔥 Max {labels[variable]}", f"{df_map[variable].max():.1f}", delta=None)
        c2.metric(f"❄️ Min {labels[variable]}", f"{df_map[variable].min():.1f}", delta=None)
        c3.metric(f"📊 Moyenne nationale", f"{df_map[variable].mean():.1f}", delta=None)'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
