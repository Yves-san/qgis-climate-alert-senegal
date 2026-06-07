with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = 'def afficher_carte_forages():\n    import json, os\n    import plotly.graph_objects as go\n    import streamlit as st'

new = '@st.cache_data(ttl=3600)\ndef charger_forages():\n    import json, os\n    chemins = [\n        os.path.join(os.path.dirname(__file__), "data", "forages_senegal.geojson"),\n        os.path.join(os.path.dirname(__file__), "..", "data", "forages_senegal.geojson"),\n    ]\n    path = next((p for p in chemins if os.path.exists(p)), None)\n    if path is None: return None\n    with open(path, encoding="utf-8") as f:\n        return json.load(f)\n\n@st.cache_data(ttl=3600)\ndef charger_hydrographie():\n    import json, os\n    chemins = [\n        os.path.join(os.path.dirname(__file__), "..", "data", "hydrographie_sn.geojson"),\n        os.path.join(os.path.dirname(__file__), "data", "hydrographie_sn.geojson"),\n    ]\n    path = next((p for p in chemins if os.path.exists(p)), None)\n    if path is None: return None\n    with open(path, encoding="utf-8") as f:\n        return json.load(f)\n\ndef afficher_carte_forages():\n    import plotly.graph_objects as go\n    import streamlit as st\n    gj = charger_forages()\n    if gj is None:\n        st.error("Fichier forages non trouve")\n        return'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
