with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''            if geom_type == "Polygon":
                for ring in coords:'''

new = '''            if geom_type == "Point":
                lon, lat = coords
                delta = 0.15
                return (lon - delta, lat - delta, lon + delta, lat + delta)
            if geom_type == "Polygon":
                for ring in coords:'''

if old in content:
    with open('dashboard/app.py', 'w') as f:
        f.write(content.replace(old, new, 1))
    print('Done')
else:
    print('TEXTE NON TROUVE')
