with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''        _path2 = os.path.join(os.path.dirname("dashboard/app.py"), "dashboard", "data", "senegal_communes.geojson")'''

new = '''        _path2 = os.path.join(os.path.dirname(__file__), "data", "senegal_communes.geojson")'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
