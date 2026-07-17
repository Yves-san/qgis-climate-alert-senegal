with open("app.py", "r", encoding="utf-8") as f:
    contenu = f.read()

ancien_bloc = """    data = proj[commune]["scenarios"][sc_key]
    df = pd.DataFrame({
        "date":     data["time"],
        "temp_mean":data["temperature_2m_mean"],
        "temp_max": data["temperature_2m_max"],
        "temp_min": data["temperature_2m_min"],
        "precip":   data["precipitation_sum"],
        "eto":      data["et0_fao_evapotranspiration"],
        "vent":     data["windspeed_10m_max"],
    })
    df["date"] = pd.to_datetime(df["date"])"""

nouveau_bloc = """    data = proj[commune]["scenarios"][sc_key]
    # Precipitation limitee a 2025-2050 (donnees reelles Open-Meteo) :
    # on tronque tout le reste a la meme longueur pour rester aligne.
    n = len(data["precipitation_sum"])
    df = pd.DataFrame({
        "date":     data.get("time_precipitation", data["time"])[:n],
        "temp_mean":data["temperature_2m_mean"][:n],
        "temp_max": data["temperature_2m_max"][:n],
        "temp_min": data["temperature_2m_min"][:n],
        "precip":   data["precipitation_sum"][:n],
        "eto":      data["et0_fao_evapotranspiration"][:n],
        "vent":     data["windspeed_10m_max"][:n],
    })
    df["date"] = pd.to_datetime(df["date"])"""

if ancien_bloc not in contenu:
    print("ATTENTION : bloc attendu non trouve tel quel. Verification manuelle necessaire.")
else:
    contenu = contenu.replace(ancien_bloc, nouveau_bloc)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(contenu)
    print("app.py corrige avec succes.")
