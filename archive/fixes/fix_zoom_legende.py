with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center={"lat": (bbox["minlat"]+bbox["maxlat"])/2, "lon": (bbox["minlon"]+bbox["maxlon"])/2},
            zoom=9,
        ),
        title=f"Reseau hydraulique et forages — {commune_name}",
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)'''

new = '''    # Zoom adaptatif selon la taille du département
    import math
    lat_range = bbox["maxlat"] - bbox["minlat"]
    lon_range = bbox["maxlon"] - bbox["minlon"]
    max_range = max(lat_range, lon_range)
    if max_range < 0.5: zoom_auto = 10
    elif max_range < 1.0: zoom_auto = 9
    elif max_range < 2.0: zoom_auto = 8
    elif max_range < 4.0: zoom_auto = 7
    else: zoom_auto = 6

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center={"lat": (bbox["minlat"]+bbox["maxlat"])/2, "lon": (bbox["minlon"]+bbox["maxlon"])/2},
            zoom=zoom_auto,
        ),
        title=f"Reseau hydraulique et forages — {commune_name}",
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(
            bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1,
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=10), itemwidth=30,
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
