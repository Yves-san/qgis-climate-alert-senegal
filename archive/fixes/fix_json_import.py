with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    with open(path, encoding="utf-8") as f:\n        gj = json.load(f)'
new = '    import json as _json_f\n    with open(path, encoding="utf-8") as f:\n        gj = _json_f.load(f)'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
