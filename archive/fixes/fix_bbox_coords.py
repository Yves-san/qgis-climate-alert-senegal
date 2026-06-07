with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    lons_poly = [c[0] for c in bbox["coords"]]
    lats_poly = [c[1] for c in bbox["coords"]]
    fig.add_trace(go.Scattermapbox(
        lon=lons_poly + [lons_poly[0]],
        lat=lats_poly + [lats_poly[0]],
        mode="lines",
        line=dict(color="#ff4444", width=2),
        name="Limite commune",
        hoverinfo="skip",
    ))'''

new = '''    # bbox = (minlon, minlat, maxlon, maxlat)
    minlon, minlat, maxlon, maxlat = bbox[0], bbox[1], bbox[2], bbox[3]
    lons_poly = [minlon, maxlon, maxlon, minlon, minlon]
    lats_poly = [minlat, minlat, maxlat, maxlat, minlat]
    fig.add_trace(go.Scattermapbox(
        lon=lons_poly,
        lat=lats_poly,
        mode="lines",
        line=dict(color="#ff4444", width=2),
        name="Limite commune",
        hoverinfo="skip",
    ))'''

if old in content:
    content = content.replace(old, new, 1)
    print('coords: Done')
else:
    print('coords: TEXTE NON TROUVE')

old2 = 'center={"lat": bbox["centerlat"], "lon": bbox["centerlon"]},'
new2 = 'center={"lat": (bbox[1]+bbox[3])/2, "lon": (bbox[0]+bbox[2])/2},'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('center: Done')
else:
    print('center: TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
