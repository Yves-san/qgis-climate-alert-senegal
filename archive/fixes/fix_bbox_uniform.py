with open('dashboard/app.py', 'r') as f:
    content = f.read()

# Remplacer le cas Point pour retourner un dict comme les autres
old = '''            if geom_type == "Point":
                lon, lat = coords
                delta = 0.15
                return (lon - delta, lat - delta, lon + delta, lat + delta)'''

new = '''            if geom_type == "Point":
                lon, lat = coords
                delta = 0.15
                return {
                    "minlon": lon - delta, "maxlon": lon + delta,
                    "minlat": lat - delta, "maxlat": lat + delta,
                    "centerlon": lon, "centerlat": lat,
                    "coords": [[lon-delta,lat-delta],[lon+delta,lat-delta],[lon+delta,lat+delta],[lon-delta,lat+delta]]
                }'''

if old in content:
    content = content.replace(old, new, 1)
    print('Point: Done')
else:
    print('Point: TEXTE NON TROUVE')

# Remettre les clés dict au lieu des indices tuple
replacements = [
    ('bbox[0]', 'bbox["minlon"]'),
    ('bbox[1]', 'bbox["minlat"]'),
    ('bbox[2]', 'bbox["maxlon"]'),
    ('bbox[3]', 'bbox["maxlat"]'),
    ('(bbox[1]+bbox[3])/2', 'bbox["centerlat"]'),
    ('(bbox[0]+bbox[2])/2', 'bbox["centerlon"]'),
]

for old2, new2 in replacements:
    count = content.count(old2)
    content = content.replace(old2, new2)
    print(f'{old2} → {new2} ({count}x)')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
