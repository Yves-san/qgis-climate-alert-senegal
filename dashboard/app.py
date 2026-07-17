import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os

# Chemin absolu vers le dossier dashboard
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Climate Alert Sénégal", page_icon="🌍", layout="wide")

st.markdown("""
<style>
.main { background-color: #0A1628; color: #F0F4FF; }
.card-temp { background: rgba(255,255,255,0.06); border: 0.5px solid rgba(255,255,255,0.12);
    border-radius: 14px; padding: 24px 16px; text-align: center; }
.card-label { font-size: 12px; color: rgba(240,244,255,0.5); margin-bottom: 8px; }
.card-icon { font-size: 36px; margin-bottom: 8px; }
.card-value { font-size: 28px; font-weight: 500; color: #60A5FA; }
.card-sub { font-size: 12px; color: rgba(240,244,255,0.4); margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("🌍 Climate Alert Sénégal")
st.markdown("**Surveillance climatique des 46 départements · Projections 2025–2055**")
st.divider()

model_names = ["CMCC_CM2_VHR4", "FGOALS_f3_H", "HiRAM_SIT_HR", "MRI_AGCM3_2_S", "EC_Earth3P_HR", "MPI_ESM1_2_XR", "NICAM16_8S"]

@st.cache_data
def load_spi():
    return pd.read_csv(os.path.join(BASE_DIR, "spi_mensuel.csv"))

@st.cache_data
def load_temperature(model):
    return pd.read_csv(os.path.join(BASE_DIR, f"temperature_{model}.csv"), parse_dates=["date"])

@st.cache_data
def load_precipitation(model):
    return pd.read_csv(os.path.join(BASE_DIR, f"precipitation_{model}.csv"), parse_dates=["date"])

spi_df = load_spi()

st.sidebar.header("Paramètres")
selected_model = st.sidebar.selectbox("Modèle climatique", model_names, index=3)
selected_year = st.sidebar.slider("Année", 2025, 2050, date.today().year)
selected_date = st.sidebar.date_input("Date précise", value=date.today(), min_value=date(2025,1,1), max_value=date(2050,12,31))

col1, col2, col3, col4 = st.columns(4)
spi_model = spi_df[spi_df["model"] == selected_model]
spi_recent = spi_model[spi_model["year_month"].str.startswith(str(selected_year))]
spi_mean = spi_recent["SPI"].mean() if not spi_recent.empty else 0

temp_df = load_temperature(selected_model)
temp_year = temp_df[temp_df["date"].dt.year == selected_year]
temp_max = temp_year["temperature_2m_max"].max() if not temp_year.empty else 0
temp_mean = temp_year["temperature_2m_mean"].mean() if not temp_year.empty else 0

precip_df = load_precipitation(selected_model)
precip_year = precip_df[precip_df["date"].dt.year == selected_year]
precip_total = precip_year["precipitation_sum"].sum() if not precip_year.empty else 0

with col1:
    spi_color = "🔴" if spi_mean < -1.5 else "🟡" if spi_mean < -1 else "🟢"
    st.metric(f"{spi_color} SPI moyen", f"{spi_mean:.2f}")
with col2:
    st.metric("🌡️ T° max", f"{temp_max:.1f}°C")
with col3:
    st.metric("🌡️ T° moyenne", f"{temp_mean:.1f}°C")
with col4:
    st.metric("🌧️ Précip. totale", f"{precip_total:.0f} mm")

st.divider()

tab1, tab2, tab3 = st.tabs(["📉 SPI Mensuel", "🌡️ Températures", "🌧️ Précipitations"])

with tab1:
    st.subheader(f"Indice SPI mensuel — {selected_model}")
    fig_spi = go.Figure()
    colors = {"CMCC_CM2_VHR4":"#00D4AA","FGOALS_f3_H":"#F59E0B","HiRAM_SIT_HR":"#FF6B6B",
              "MRI_AGCM3_2_S":"#60A5FA","EC_Earth3P_HR":"#A78BFA","MPI_ESM1_2_XR":"#34D399","NICAM16_8S":"#FB923C"}
    for model in model_names:
        m_df = spi_df[spi_df["model"] == model]
        fig_spi.add_trace(go.Scatter(x=m_df["year_month"], y=m_df["SPI"], name=model,
            line=dict(color=colors[model], width=1.5 if model == selected_model else 0.8),
            opacity=1.0 if model == selected_model else 0.3))
    fig_spi.add_hline(y=-1.0, line_dash="dash", line_color="#F59E0B", annotation_text="Sécheresse modérée")
    fig_spi.add_hline(y=-1.5, line_dash="dash", line_color="#FF6B6B", annotation_text="Sécheresse sévère")
    fig_spi.add_hline(y=0, line_color="white", line_width=0.5)
    fig_spi.update_layout(paper_bgcolor="#0A1628", plot_bgcolor="#0A1628",
        font_color="#F0F4FF", height=400, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_spi, use_container_width=True)

with tab2:
    st.subheader(f"Températures — {selected_date.strftime('%d %B %Y')}")
    temp_day = temp_df[temp_df["date"].dt.date == selected_date]
    if not temp_day.empty:
        t_min = float(temp_day["temperature_2m_min"].values[0])
        t_max_day = float(temp_day["temperature_2m_max"].values[0])
        t_nuit = round(t_min - 2, 1)
    else:
        t_min = round(float(temp_mean) - 5, 1) if temp_mean else 20.0
        t_max_day = round(float(temp_max), 1) if temp_max else 35.0
        t_nuit = round(t_min - 2, 1)
        st.info("Données interpolées — date hors plage 2025-2050")

    c1, c2, c3 = st.columns(3)
    with c1:
        icon = "🌅" if t_min < 25 else "☀️"
        st.markdown(f"""<div class="card-temp">
            <div class="card-icon">{icon}</div>
            <div class="card-label">Matin (6h-10h)</div>
            <div class="card-value">{t_min:.0f}°C</div>
            <div class="card-sub">Température minimale</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        icon = "🥵" if t_max_day > 38 else "😎" if t_max_day > 32 else "🌤️"
        st.markdown(f"""<div class="card-temp">
            <div class="card-icon">{icon}</div>
            <div class="card-label">Après-midi (12h-16h)</div>
            <div class="card-value" style="color:#FF6B6B">{t_max_day:.0f}°C</div>
            <div class="card-sub">Température maximale</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        icon = "🌙" if t_nuit < 22 else "🌛"
        st.markdown(f"""<div class="card-temp">
            <div class="card-icon">{icon}</div>
            <div class="card-label">Nuit (20h-6h)</div>
            <div class="card-value" style="color:#00D4AA">{t_nuit:.0f}°C</div>
            <div class="card-sub">Température nocturne</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    temp_df2 = temp_df.copy()
    temp_df2["year"] = temp_df2["date"].dt.year
    temp_annual = temp_df2.groupby("year").agg(
        t_max=("temperature_2m_max","mean"),
        t_mean=("temperature_2m_mean","mean"),
        t_min=("temperature_2m_min","mean")
    ).reset_index()
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=temp_annual["year"], y=temp_annual["t_max"], name="T° max", line=dict(color="#FF6B6B")))
    fig_temp.add_trace(go.Scatter(x=temp_annual["year"], y=temp_annual["t_mean"], name="T° moyenne", line=dict(color="#F59E0B")))
    fig_temp.add_trace(go.Scatter(x=temp_annual["year"], y=temp_annual["t_min"], name="T° min", line=dict(color="#00D4AA")))
    fig_temp.add_vline(x=selected_year, line_dash="dash", line_color="white", opacity=0.5)
    fig_temp.update_layout(paper_bgcolor="#0A1628", plot_bgcolor="#0A1628",
        font_color="#F0F4FF", height=350, yaxis_title="°C")
    st.plotly_chart(fig_temp, use_container_width=True)

with tab3:
    st.subheader(f"Précipitations mensuelles — {selected_model}")
    precip_df2 = load_precipitation(selected_model)
    precip_df2["month"] = precip_df2["date"].dt.month
    precip_df2["year"] = precip_df2["date"].dt.year
    precip_monthly = precip_df2.groupby(["year","month"])["precipitation_sum"].sum().reset_index()
    precip_pivot = precip_monthly[precip_monthly["year"] == selected_year]
    fig_precip = px.bar(precip_pivot, x="month", y="precipitation_sum",
        color="precipitation_sum", color_continuous_scale=["#FF6B6B","#F59E0B","#00D4AA"],
        labels={"month":"Mois","precipitation_sum":"Précipitations (mm)"},
        title=f"Précipitations mensuelles {selected_year}")
    fig_precip.update_layout(paper_bgcolor="#0A1628", plot_bgcolor="#0A1628", font_color="#F0F4FF", height=400)
    fig_precip.update_xaxes(tickvals=list(range(1,13)), ticktext=["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"])
    st.plotly_chart(fig_precip, use_container_width=True)

st.divider()
st.caption("Climate Alert Sénégal · Licence 1 Géomatique · USSEIN · Données : Open-Meteo Climate API")
