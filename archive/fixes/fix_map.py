"""Script pour corriger la section carte dans dashboard/app.py"""
import json, os

with open('dashboard/app.py', encoding='utf-8') as f:
    content = f.read()

# Nouvelle section carte qui lit directement le GeoJSON
new_map = '''# ── PAGE : Carte ──────────────────────────────────────────────────────────────
elif page == "🗺️ Carte des Communes":
    st.markdown("# 🗺️ Carte des Communes du Sénégal")

    import json as _j, os as _o
    geojson_path = _o.path.join("data", "communes", "senegal_communes.geojson")
    rows = []
    if _o.path.exists(geojson_path):
        with open(geojson_path, encoding="utf-8") as _f:
            gj = _j.load(_f)
        for feat in gj.get("features", []):
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [0, 0])
            rows.append({
                "commune": props.get("name", ""),
                "region": props.get("region", ""),
                "lat": float(coords[1]),
                "lon": float(coords[0]),
                "population": props.get("population", 0),
            })
    df_map = pd.DataFrame(rows)
    if not df_map.empty:
        df_map = df_map[df_map["lat"] != 0]
        fig = px.scatter_mapbox(
            df_map, lat="lat", lon="lon",
            hover_name="commune",
            hover_data=["region", "population"],
            color="region",
            zoom=5.5,
            center={"lat": 14.5, "lon": -14.5},
            mapbox_style="carto-darkmatter",
            title="Communes du Sénégal",
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="#0a0f1e",
            font_color="#e8f4fd",
            height=600,
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 📋 Liste des communes")
        st.dataframe(df_map, use_container_width=True)
    else:
        st.error(f"Fichier GeoJSON introuvable : {geojson_path}")'''

# Trouver et remplacer la section carte
start = content.find('# ── PAGE : Carte')
end = content.find('# ── PAGE : Alertes')

if start != -1 and end != -1:
    content = content[:start] + new_map + '\n\n' + content[end:]
    with open('dashboard/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Correction appliquée avec succès !")
    print("geojson in content:", "geojson" in content)
else:
    print("❌ Section non trouvée")
    print("start:", start, "end:", end)
