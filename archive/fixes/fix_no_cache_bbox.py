with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '@st.cache_data(ttl=1)\ndef get_bbox_commune(commune_name):'
new = 'def get_bbox_commune(commune_name):'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
