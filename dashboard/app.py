"""
Senegal Climate Alert — Streamlit Dashboard Standalone
Lit directement la base SQLite sans API
Run: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌍 Sénégal Climate Alert",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0a0f1e; }
    [data-testid="stSidebar"] { background: #0d1527; border-right: 1px solid #1e3a5f; }
    .metric-card {
        background: linear-gradient(135deg, #1a2744 0%, #0d1e3d 100%);
        border: 1px solid #2a4a7f; border-radius: 12px;
        padding: 20px; text-align: center; margin: 8px 0;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #4db8ff; }
    .metric-label { font-size: 0.85rem; color: #8ab4d4; margin-top: 4px; }
    .alert-critical { background: #2d0a0a; border-left: 4px solid #ff4444; padding: 12px; border-radius: 6px; margin: 6px 0; }
    .alert-high     { background: #2d1a0a; border-left: 4px solid #ff8c00; padding: 12px; border-radius: 6px; margin: 6px 0; }
    .alert-medium   { background: #2d2a0a; border-left: 4px solid #ffd700; padding: 12px; border-radius: 6px; margin: 6px 0; }
    .alert-low      { background: #0a2d1a; border-left: 4px solid #44ff88; padding: 12px; border-radius: 6px; margin: 6px 0; }
    h1, h2, h3 { color: #e8f4fd !important; }
    .stSelectbox label, .stSlider label, .stRadio label { color: #8ab4d4 !important; }
</style>
""", unsafe_allow_html=True)

# ── Connexion SQLite ──────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_climate.db")

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=300)
def get_communes():
    conn = get_conn()
    df = pd.read_sql("SELECT DISTINCT commune_name, region, latitude, longitude FROM commune_climate_data ORDER BY commune_name", conn)
    return df

@st.cache_data(ttl=300)
def get_scenarios():
    conn = get_conn()
    df = pd.read_sql("SELECT DISTINCT scenario FROM commune_climate_data WHERE scenario IS NOT NULL", conn)
    return df["scenario"].tolist()

@st.cache_data(ttl=60)
def get_annual(commune, scenario):
    conn = get_conn()
    q = """
        SELECT year, AVG(temp_annual_mean) as temp_mean,
               AVG(temp_annual_max) as temp_max,
               AVG(temp_annual_min) as temp_min,
               SUM(precip_annual_total) as precip_total,
               AVG(humidity_annual_mean) as humidity,
               AVG(drought_index) as drought,
               AVG(spi_index) as spi,
               AVG(heat_stress) as heat_stress,
               AVG(risk_level = 'high') * 100 as pct_high_risk
        FROM commune_climate_data
        WHERE commune_name = ? AND scenario = ? AND resolution = 'annual' AND year IS NOT NULL
        GROUP BY year ORDER BY year
    """
    return pd.read_sql(q, conn, params=[commune, scenario])

@st.cache_data(ttl=60)
def get_monthly(commune, scenario):
    conn = get_conn()
    q = """
        SELECT year_month,
               AVG(temp_monthly_mean) as temp_mean,
               AVG(temp_monthly_max) as temp_max,
               SUM(precip_monthly_total) as precip_total,
               AVG(humidity_monthly_mean) as humidity
        FROM commune_climate_data
        WHERE commune_name = ? AND scenario = ? AND resolution = 'monthly' AND year_month IS NOT NULL
        GROUP BY year_month ORDER BY year_month
    """
    return pd.read_sql(q, conn, params=[commune, scenario])

@st.cache_data(ttl=60)
def get_daily(commune, scenario, year):
    conn = get_conn()
    q = """
        SELECT date_daily, temp_daily, precip_daily, humidity_daily, wind_speed_daily
        FROM commune_climate_data
        WHERE commune_name = ? AND scenario = ? AND resolution = 'daily'
        AND strftime('%Y', date_daily) = ?
        ORDER BY date_daily
    """
    return pd.read_sql(q, conn, params=[commune, scenario, str(year)])

@st.cache_data(ttl=300)
def get_all_regions_annual(scenario, year):
    conn = get_conn()
    q = """
        SELECT commune_name, region, latitude, longitude,
               AVG(temp_annual_mean) as temp_mean,
               SUM(precip_annual_total) as precip_total,
               AVG(drought_index) as drought,
               AVG(heat_stress) as heat_stress,
               risk_level
        FROM commune_climate_data
        WHERE scenario = ? AND year = ? AND resolution = 'annual'
        GROUP BY commune_name
    """
    return pd.read_sql(q, conn, params=[scenario, year])

LAYOUT = dict(paper_bgcolor="#0a0f1e", plot_bgcolor="#0d1527",
              font_color="#e8f4fd", margin=dict(t=40, b=20, l=10, r=10))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Navigation")
    page = st.radio("", [
        "📊 Aperçu",
        "🌡️ Température",
        "🌧️ Précipitations & Sécheresse",
        "🗺️ Carte Interactive",
        "📉 Comparaison Scénarios",
        "⚠️ Alertes & Risques",
        "💾 Export",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### ⚙️ Paramètres")

    communes_df = get_communes()
    commune_list = communes_df["commune_name"].tolist()
    selected_commune = st.selectbox("🏘️ Commune", commune_list)

    scenarios = get_scenarios() or ["SSP2-4.5", "SSP1-1.9", "SSP5-8.5"]
    selected_scenario = st.selectbox("🌡️ Scénario", scenarios)

    st.markdown("---")
    st.success("🟢 Base de données connectée")
    conn = get_conn()
    nb = pd.read_sql("SELECT COUNT(*) as n FROM commune_climate_data", conn).iloc[0]["n"]
    st.caption(f"📦 {nb:,} enregistrements")

# ── PAGE : Aperçu ─────────────────────────────────────────────────────────────
if page == "📊 Aperçu":
    st.markdown("# 🌍 Système d'Alerte Climatique — Sénégal 2025–2055")
    st.caption("Données journalières · mensuelles · annuelles")

    nb_communes = len(commune_list)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{nb_communes}</div><div class="metric-label">Communes</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">2025–2055</div><div class="metric-label">Période (30 ans)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label">Scénarios CMIP6</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{nb/1000:.0f}K</div><div class="metric-label">Enregistrements</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 📊 Aperçu annuel — {selected_commune} · {selected_scenario}")

    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(df, x="year", y="temp_mean",
                          title="🌡️ Température moyenne annuelle (°C)",
                          color_discrete_sequence=["#ff6b6b"], template="plotly_dark")
            fig.update_layout(**LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df, x="year", y="precip_total",
                          title="🌧️ Précipitations annuelles (mm)",
                          color_discrete_sequence=["#4db8ff"], template="plotly_dark")
            fig2.update_layout(**LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            if "drought" in df.columns and df["drought"].notna().any():
                fig3 = px.line(df, x="year", y="drought",
                               title="🏜️ Indice de sécheresse",
                               color_discrete_sequence=["#ffd700"], template="plotly_dark")
                fig3.update_layout(**LAYOUT)
                st.plotly_chart(fig3, use_container_width=True)
        with col4:
            if "heat_stress" in df.columns and df["heat_stress"].notna().any():
                fig4 = px.area(df, x="year", y="heat_stress",
                               title="🔥 Stress thermique",
                               color_discrete_sequence=["#ff4444"], template="plotly_dark")
                fig4.update_layout(**LAYOUT)
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Aucune donnée annuelle disponible pour cette commune.")

# ── PAGE : Température ────────────────────────────────────────────────────────
elif page == "🌡️ Température":
    st.markdown(f"# 🌡️ Température — {selected_commune}")

    resolution = st.radio("Résolution", ["Annuelle", "Mensuelle", "Journalière"], horizontal=True)

    if resolution == "Annuelle":
        df = get_annual(selected_commune, selected_scenario)
        if not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["year"], y=df["temp_max"], name="T° max", line=dict(color="#ff4444")))
            fig.add_trace(go.Scatter(x=df["year"], y=df["temp_mean"], name="T° moyenne", line=dict(color="#ffd700")))
            fig.add_trace(go.Scatter(x=df["year"], y=df["temp_min"], name="T° min", line=dict(color="#4db8ff")))
            fig.update_layout(title="Évolution des températures 2025–2055",
                              template="plotly_dark", **LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("T° min projetée", f"{df['temp_min'].min():.1f}°C")
            col2.metric("T° moyenne", f"{df['temp_mean'].mean():.1f}°C")
            col3.metric("T° max projetée", f"{df['temp_max'].max():.1f}°C")

    elif resolution == "Mensuelle":
        df = get_monthly(selected_commune, selected_scenario)
        if not df.empty:
            fig = px.line(df, x="year_month", y="temp_mean",
                          title="Température mensuelle moyenne (°C)",
                          color_discrete_sequence=["#ff6b6b"], template="plotly_dark")
            fig.update_layout(**LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    else:
        year = st.slider("Année", 2025, 2055, 2030)
        df = get_daily(selected_commune, selected_scenario, year)
        if not df.empty:
            fig = px.line(df, x="date_daily", y="temp_daily",
                          title=f"Température journalière {year}",
                          color_discrete_sequence=["#ff6b6b"], template="plotly_dark")
            fig.update_layout(**LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

# ── PAGE : Précipitations & Sécheresse ───────────────────────────────────────
elif page == "🌧️ Précipitations & Sécheresse":
    st.markdown(f"# 🌧️ Précipitations & Sécheresse — {selected_commune}")

    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x="year", y="precip_total",
                         title="Précipitations annuelles (mm)",
                         color="precip_total",
                         color_continuous_scale=["#ff4444", "#ffd700", "#4db8ff"],
                         template="plotly_dark")
            fig.update_layout(**LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if df["spi"].notna().any():
                fig2 = px.bar(df, x="year", y="spi",
                              title="Indice SPI (Standardized Precipitation Index)",
                              color="spi",
                              color_continuous_scale=["#ff4444", "#ffffff", "#4db8ff"],
                              template="plotly_dark")
                fig2.update_layout(**LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

        if df["drought"].notna().any():
            fig3 = px.line(df, x="year", y="drought",
                           title="Indice de sécheresse (0=normal, 1=sécheresse sévère)",
                           color_discrete_sequence=["#ffd700"], template="plotly_dark")
            fig3.add_hline(y=0.5, line_dash="dash", line_color="red",
                           annotation_text="Seuil critique")
            fig3.update_layout(**LAYOUT)
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 📊 Statistiques pluviométriques")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Précip. min", f"{df['precip_total'].min():.0f} mm")
        col2.metric("Précip. moy.", f"{df['precip_total'].mean():.0f} mm")
        col3.metric("Précip. max", f"{df['precip_total'].max():.0f} mm")
        col4.metric("Tendance", f"{df['precip_total'].iloc[-1] - df['precip_total'].iloc[0]:.0f} mm")
    else:
        st.warning("Pas de données disponibles.")

# ── PAGE : Carte Interactive ──────────────────────────────────────────────────
elif page == "🗺️ Carte Interactive":
    st.markdown("# 🗺️ Carte Interactive du Sénégal")

    year = st.slider("Année de référence", 2025, 2055, 2030)
    variable = st.selectbox("Variable", ["temp_mean", "precip_total", "drought", "heat_stress"])

    df_map = get_all_regions_annual(selected_scenario, year)
    if not df_map.empty:
        labels = {
            "temp_mean": "T° moyenne (°C)",
            "precip_total": "Précipitations (mm)",
            "drought": "Indice sécheresse",
            "heat_stress": "Stress thermique"
        }
        colors = {
            "temp_mean": "Reds",
            "precip_total": "Blues",
            "drought": "YlOrRd",
            "heat_stress": "hot"
        }

        fig = px.scatter_mapbox(
            df_map, lat="latitude", lon="longitude",
            hover_name="commune_name",
            hover_data=["region", variable],
            color=variable,
            color_continuous_scale=colors[variable],
            size_max=15,
            zoom=5.5,
            center={"lat": 14.5, "lon": -14.5},
            mapbox_style="carto-darkmatter",
            title=f"{labels[variable]} — {year} · {selected_scenario}",
            template="plotly_dark",
        )
        fig.update_layout(paper_bgcolor="#0a0f1e", font_color="#e8f4fd",
                          height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Données cartographiques non disponibles pour cette année.")

# ── PAGE : Comparaison Scénarios ──────────────────────────────────────────────
elif page == "📉 Comparaison Scénarios":
    st.markdown(f"# 📉 Comparaison des Scénarios — {selected_commune}")

    colors_sc = {"SSP1-1.9": "#44ff88", "SSP2-4.5": "#ffd700", "SSP5-8.5": "#ff4444"}
    variable = st.selectbox("Variable", ["temp_mean", "precip_total", "drought", "heat_stress"])
    labels = {"temp_mean": "T° moyenne (°C)", "precip_total": "Précipitations (mm)",
               "drought": "Indice sécheresse", "heat_stress": "Stress thermique"}

    fig = go.Figure()
    summary = []
    for sc in scenarios:
        df = get_annual(selected_commune, sc)
        if not df.empty and variable in df.columns:
            fig.add_trace(go.Scatter(
                x=df["year"], y=df[variable],
                name=sc, mode="lines+markers",
                line=dict(color=colors_sc.get(sc, "#ffffff"), width=2),
            ))
            summary.append({
                "Scénario": sc,
                f"Min": round(df[variable].min(), 2),
                f"Moyenne": round(df[variable].mean(), 2),
                f"Max": round(df[variable].max(), 2),
                f"Tendance 2055 vs 2025": round(df[variable].iloc[-1] - df[variable].iloc[0], 2),
            })

    fig.update_layout(
        title=f"{labels[variable]} — Comparaison scénarios · {selected_commune}",
        template="plotly_dark", **LAYOUT,
        legend=dict(bgcolor="#0d1527", bordercolor="#2a4a7f"),
    )
    st.plotly_chart(fig, use_container_width=True)

    if summary:
        st.markdown("### 📊 Résumé statistique")
        st.dataframe(pd.DataFrame(summary), use_container_width=True)

# ── PAGE : Alertes & Risques ──────────────────────────────────────────────────
elif page == "⚠️ Alertes & Risques":
    st.markdown(f"# ⚠️ Alertes & Risques — {selected_commune}")

    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        last = df.iloc[-1]
        temp_max = last.get("temp_max", 0) or 0
        precip = last.get("precip_total", 0) or 0
        drought = last.get("drought", 0) or 0

        # Niveau de risque global
        score = 0
        if temp_max >= 42: score += 3
        elif temp_max >= 38: score += 2
        elif temp_max >= 35: score += 1
        if drought >= 0.7: score += 3
        elif drought >= 0.5: score += 2
        elif drought >= 0.3: score += 1
        if precip < 200: score += 2
        elif precip < 400: score += 1

        if score >= 6:
            st.markdown('<div class="alert-critical">🔴 <b>CRITIQUE</b> — Risques climatiques extrêmes projetés à l\'horizon 2055</div>', unsafe_allow_html=True)
        elif score >= 4:
            st.markdown('<div class="alert-high">🟠 <b>ÉLEVÉ</b> — Risques importants nécessitant adaptation urgente</div>', unsafe_allow_html=True)
        elif score >= 2:
            st.markdown('<div class="alert-medium">🟡 <b>MODÉRÉ</b> — Surveillance recommandée</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-low">🟢 <b>FAIBLE</b> — Conditions relativement stables</div>', unsafe_allow_html=True)

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("T° max 2055", f"{temp_max:.1f}°C", f"+{temp_max - df.iloc[0].get('temp_max', temp_max):.1f}°C")
        col2.metric("Précip. 2055", f"{precip:.0f} mm", f"{precip - df.iloc[0].get('precip_total', precip):.0f} mm")
        col3.metric("Sécheresse 2055", f"{drought:.2f}", "")

        st.markdown("### 💡 Recommandations agricoles")
        if score >= 6:
            st.error("🚨 Transition urgente vers cultures xérophytes (niébé, sorgho). Agroforesterie indispensable. Systèmes de retenue d'eau.")
        elif score >= 4:
            st.warning("⚠️ Introduire variétés résistantes à la sécheresse. Renforcer irrigation. Surveiller stress thermique.")
        elif score >= 2:
            st.info("ℹ️ Maintenir cultures traditionnelles avec irrigation complémentaire. Diversifier les variétés.")
        else:
            st.success("✅ Conditions favorables. Maintenir pratiques actuelles. Prévention préventive recommandée.")

# ── PAGE : Export ─────────────────────────────────────────────────────────────
elif page == "💾 Export":
    st.markdown(f"# 💾 Export — {selected_commune}")

    resolution = st.selectbox("Résolution", ["annual", "monthly", "daily"])
    year_range = st.slider("Période", 2025, 2055, (2025, 2055))

    if st.button("📥 Charger", type="primary"):
        conn = get_conn()
        q = f"""
            SELECT * FROM commune_climate_data
            WHERE commune_name = ? AND scenario = ? AND resolution = ?
            AND (year >= ? OR strftime('%Y', date_daily) >= ?)
            AND (year <= ? OR strftime('%Y', date_daily) <= ?)
        """
        df = pd.read_sql(q, conn, params=[
            selected_commune, selected_scenario, resolution,
            year_range[0], str(year_range[0]),
            year_range[1], str(year_range[1])
        ])

        if not df.empty:
            st.success(f"✅ {len(df):,} enregistrements")
            st.dataframe(df.head(50), use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Télécharger CSV", csv,
                f"{selected_commune}_{resolution}_{selected_scenario}.csv",
                "text/csv"
            )
        else:
            st.warning("Aucune donnée trouvée.")
