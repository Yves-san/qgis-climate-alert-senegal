with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    page = st.radio("", [
        "📊 Aperçu",
        "🌡️ Température",
        "🌧️ Précipitations",
        "🏜️ Sécheresse",
        "💧 Ressources en eau",
        "🌱 Sols & Calendrier Cultural",
        "🗺️ Carte Interactive",
        "⚠️ Alertes & Conseils",
        "📉 Comparaison Scénarios",
        "💧 Réseau Hydraulique",
        "💾 Export",
    ], label_visibility="collapsed")'''

new = '''    page = st.radio("", [
        "📊 Aperçu",
        "🌡️ Température",
        "🌧️ Précipitations",
        "🏜️ Sécheresse",
        "💧 Réseau Hydraulique",
        "💧 Ressources en eau",
        "🌱 Sols & Calendrier Cultural",
        "🗺️ Carte Interactive",
        "⚠️ Alertes & Conseils",
        "📉 Comparaison Scénarios",
        "💾 Export",
    ], label_visibility="collapsed")'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
