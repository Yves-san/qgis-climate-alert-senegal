with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''        for feat in hydro["features"]:
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
                    ))'''

new = '''        # Grouper les segments par type pour une légende propre
        groupes_hydro = {}
        for feat in hydro["features"]:
            geom = feat["geometry"]
            props = feat["properties"]
            type_eau = props.get("type", "Cours d eau")
            nom_eau = props.get("name", "")
            couleur = COULEURS_HYDRO.get(type_eau, "#90CAF9")
            label = nom_eau if nom_eau and nom_eau not in groupes_hydro else type_eau
            if geom["type"] == "LineString":
                lons = [c[0] for c in geom["coordinates"]]
                lats = [c[1] for c in geom["coordinates"]]
                if any(minlon <= lo <= maxlon and minlat <= la <= maxlat for lo, la in zip(lons, lats)):
                    if type_eau not in groupes_hydro:
                        groupes_hydro[type_eau] = {"lons": [], "lats": [], "couleur": couleur}
                    groupes_hydro[type_eau]["lons"] += lons + [None]
                    groupes_hydro[type_eau]["lats"] += lats + [None]
            elif geom["type"] == "Point":
                lo, la = geom["coordinates"]
                if minlon <= lo <= maxlon and minlat <= la <= maxlat:
                    key = f"pt_{type_eau}"
                    if key not in groupes_hydro:
                        groupes_hydro[key] = {"lons": [], "lats": [], "couleur": couleur}
                    groupes_hydro[key]["lons"].append(lo)
                    groupes_hydro[key]["lats"].append(la)

        for label, g in groupes_hydro.items():
            is_point = label.startswith("pt_")
            fig.add_trace(go.Scattermapbox(
                lon=g["lons"], lat=g["lats"],
                mode="markers" if is_point else "lines",
                line=dict(color=g["couleur"], width=3) if not is_point else None,
                marker=dict(size=8, color=g["couleur"]) if is_point else None,
                name=label.replace("pt_", ""),
                hoverinfo="name",
                showlegend=True,
            ))'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
