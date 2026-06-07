with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '                marker=dict(size=4, color=COULEURS_NAPPE.get(nappe,"#4db8ff"), opacity=0.7),'
new = '                marker=dict(size=7, color=COULEURS_NAPPE.get(nappe,"#4db8ff"), opacity=0.9),'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
