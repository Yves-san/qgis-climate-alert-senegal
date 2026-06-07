with open('dashboard/app.py', 'r') as f:
    content = f.read()

# La fonction retourne (minlon, minlat, maxlon, maxlat)
# mais le code attend un dict
replacements = [
    ('bbox["minlon"]', 'bbox[0]'),
    ('bbox["minlat"]', 'bbox[1]'),
    ('bbox["maxlon"]', 'bbox[2]'),
    ('bbox["maxlat"]', 'bbox[3]'),
]

for old, new in replacements:
    count = content.count(old)
    content = content.replace(old, new)
    print(f'{old} → {new} ({count} remplacement(s))')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
