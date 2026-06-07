with open('dashboard/app.py', 'r') as f:
    content = f.read()

NOUVELLE_FONCTION = '''
@st.cache_data(ttl=3600)
def get_bbox_commune(commune_name):
    import json, os
    path = os.path.join(os.path.dirname(__file__), "..", "data", "communes", "senegal_communes.geojson")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        communes = json.load(f)
    for feat in communes["features"]:
        if feat["properties"]["name"] == commune_name:
            coords = feat["geometry"]["coordinates"]
            geom_type = feat["geometry"]["type"]
            all_coords = []
            if geom_type == "Polygon":
                for ring in coords:
                    all_coords.extend(ring)
            elif geom_type == "MultiPolygon":
                for poly in coords:
                    for ring in poly:
                        all_coords.extend(ring)
            if all_coords:
                lons = [c[0] for c in all_coords]
                lats = [c[1] for c in all_coords]
                return {
                    "minlon": min(lons), "maxlon": max(lons),
                    "minlat": min(lats), "maxlat": max(lats),
                    "centerlon": sum(lons)/len(lons),
                    "centerlat": sum(lats)/len(lats),
                    "coords": all_coords
                }
    return None

def afficher_carte_commune_eau(commune_name):
    import plotly.graph_objects as go
    bbox = get_bbox_commune(commune_name)
    if bbox is None:
        st.warning("Geometrie non disponible pour " + commune_name)
        return

    marge = 0.3
    minlon = bbox["minlon"] - marge
    maxlon = bbox["maxlon"] + marge
    minlat = bbox["minlat"] - marge
    maxlat = bbox["maxlat"] + marge

    hydro = charger_hydrographie()
    forages = charger_forages()

    fig = go.Figure()

    if hydro:
        COULEURS_HYDRO = {
            "Main river": "#1565C0",
            "Secondary river": "#42A5F5",
            "Lake": "#26A69A",
            "Canal": "#FDD835",
            "Reservoir": "#0097A7",
        }
        for feat in hydro["features"]:
            geom = feat["geometry"]
            props = feat["properties"]
            type_eau = props.get("type", "")
            nom_eau = props.get("name", "")
            couleur = COULEURS_HYDRO.get(type_eau, "#90CAF9")
            if geom["type"] == "LineString":
                lons = [c[0] for c in geom["coordinates"]]
                lats = [c[1] for c in geom["coordinates"]]
                if any(minlon <= lo <= maxlon and minlat <= la <= maxlat for lo, la in zip(lons, lats)):
                    fig.add_trace(go.Scattermapbox(
                        lon=lons, lat=lats, mode="lines",
                        line=dict(color=couleur, width=3),
                        name=nom_eau if nom_eau else type_eau,
                        hoverinfo="name",
                        showlegend=bool(nom_eau),
                    ))
            elif geom["type"] == "Point":
                lo, la = geom["coordinates"]
                if minlon <= lo <= maxlon and minlat <= la <= maxlat:
                    fig.add_trace(go.Scattermapbox(
                        lon=[lo], lat=[la], mode="markers",
                        marker=dict(size=10, color=couleur),
                        name=nom_eau, hoverinfo="name",
                    ))

    if forages:
        COULEURS_NAPPE = {
            "Maastrichtien": "#0D47A1",
            "Eocene": "#1565C0",
            "Socle paleocene": "#1976D2",
            "Paleocene": "#1E88E5",
            "Continental": "#42A5F5",
            "Quaternaire": "#90CAF9",
            "Oligo-miocene": "#0097A7",
            "Infrabasalt": "#00695C",
        }
        groupes = {}
        for feat in forages["features"]:
            p = feat["properties"]
            lo = feat["geometry"]["coordinates"][0]
            la = feat["geometry"]["coordinates"][1]
            if minlon <= lo <= maxlon and minlat <= la <= maxlat:
                nappe = p.get("nappe", "Autre")
                if nappe not in groupes:
                    groupes[nappe] = {"lons":[], "lats":[], "noms":[]}
                groupes[nappe]["lons"].append(lo)
                groupes[nappe]["lats"].append(la)
                groupes[nappe]["noms"].append(p.get("nom", ""))

        nb_forages = sum(len(g["lons"]) for g in groupes.values())

        for nappe, d in sorted(groupes.items()):
            fig.add_trace(go.Scattermapbox(
                lon=d["lons"], lat=d["lats"], mode="markers",
                name=f"{nappe} ({len(d['lons'])})",
                marker=dict(size=9, color=COULEURS_NAPPE.get(nappe, "#4db8ff"), opacity=0.9),
                text=d["noms"],
                hovertemplate="<b>%{text}</b><br>Nappe: " + nappe + "<extra></extra>",
            ))

        st.metric("Forages dans la zone", nb_forages)

    lons_poly = [c[0] for c in bbox["coords"]]
    lats_poly = [c[1] for c in bbox["coords"]]
    fig.add_trace(go.Scattermapbox(
        lon=lons_poly + [lons_poly[0]],
        lat=lats_poly + [lats_poly[0]],
        mode="lines",
        line=dict(color="#ff4444", width=2),
        name="Limite commune",
        hoverinfo="skip",
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center={"lat": bbox["centerlat"], "lon": bbox["centerlon"]},
            zoom=9,
        ),
        title=f"Reseau hydraulique et forages — {commune_name}",
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)

'''

old = '\ndef afficher_carte_forages():'
new = NOUVELLE_FONCTION + '\ndef afficher_carte_forages():'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
