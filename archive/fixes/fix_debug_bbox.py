with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    path = next((p for p in chemins if os.path.exists(p)), None)\n    if path is None:\n        return None'

new = '''    path = next((p for p in chemins if os.path.exists(p)), None)
    if path is None:
        import streamlit as st
        st.error("Chemins testes: " + str(chemins))
        return None'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
