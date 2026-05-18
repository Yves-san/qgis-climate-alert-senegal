"""
Senegal Climate Alert — Dashboard Complet 9 pages
46 communes · Sols · Calendrier · Précipitations · Conseils · Export
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

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
    .metric-card { background: linear-gradient(135deg,#1a2744,#0d1e3d); border:1px solid #2a4a7f; border-radius:12px; padding:20px; text-align:center; margin:8px 0; }
    .metric-value { font-size:2rem; font-weight:700; color:#4db8ff; }
    .metric-label { font-size:0.85rem; color:#8ab4d4; margin-top:4px; }
    .alert-critical { background:#2d0a0a; border-left:4px solid #ff4444; padding:12px; border-radius:6px; margin:6px 0; }
    .alert-high     { background:#2d1a0a; border-left:4px solid #ff8c00; padding:12px; border-radius:6px; margin:6px 0; }
    .alert-medium   { background:#2d2a0a; border-left:4px solid #ffd700; padding:12px; border-radius:6px; margin:6px 0; }
    .alert-low      { background:#0a2d1a; border-left:4px solid #44ff88; padding:12px; border-radius:6px; margin:6px 0; }
    .info-card { background:#0d1e3d; border:1px solid #2a4a7f; border-radius:8px; padding:12px; margin:6px 0; }
    h1,h2,h3 { color:#e8f4fd !important; }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "demo_climate.db")

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=300)
def get_communes():
    return pd.read_sql("SELECT DISTINCT commune_name,region,latitude,longitude FROM commune_climate_data ORDER BY region,commune_name", get_conn())

@st.cache_data(ttl=300)
def get_scenarios():
    df = pd.read_sql("SELECT DISTINCT scenario FROM commune_climate_data WHERE scenario IS NOT NULL", get_conn())
    return df["scenario"].tolist()

@st.cache_data(ttl=60)
def get_annual(commune, scenario):
    return pd.read_sql("""
        SELECT year,
            AVG(temp_annual_mean) as temp_mean, AVG(temp_annual_max) as temp_max, AVG(temp_annual_min) as temp_min,
            SUM(precip_annual_total) as precip_total, AVG(humidity_annual_mean) as humidity,
            AVG(drought_index) as drought, AVG(spi_index) as spi, AVG(heat_stress) as heat_stress, risk_level
        FROM commune_climate_data
        WHERE commune_name=? AND scenario=? AND resolution='annual' AND year IS NOT NULL
        GROUP BY year ORDER BY year
    """, get_conn(), params=[commune, scenario])

@st.cache_data(ttl=300)
def get_all_map(scenario, year):
    return pd.read_sql("""
        SELECT commune_name,region,latitude,longitude,
            AVG(temp_annual_mean) as temp_mean, AVG(temp_annual_max) as temp_max,
            SUM(precip_annual_total) as precip_total, AVG(drought_index) as drought,
            AVG(heat_stress) as heat_stress
        FROM commune_climate_data
        WHERE scenario=? AND year=? AND resolution='annual'
        GROUP BY commune_name
    """, get_conn(), params=[scenario, year])

SOLS = {
    'Dakar':'Sol sableux (Deck-Dior) · faible rétention hydrique',
    'Pikine':'Sol sableux dégradé · urbanisation intense',
    'Guediawaye':'Sol sableux · nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical · bon drainage',
    'Bargny':'Sol salin · mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) · arachide',
    'Bambey':'Sol Dior sableux · très cultivé',
    'Mbacké':'Sol Dior et Deck · polyculture',
    'Fatick':'Sol sulfaté acide · tannes · mangrove',
    'Gossas':'Sol ferrugineux · mil dominant',
    'Foundiougne':'Sol alluvial · riziculture de mangrove',
    'Sokone':'Sol hydromorphe · sel',
    'Kaolack':'Sol argileux (Deck) · bassin arachidier',
    'Kaffrine':'Sol Dior et Deck · transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé · coton',
    'Kolda':'Sol ferralitique · forêt dégradée',
    'Vélingara':'Sol ferrugineux · savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique · cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge · or et cultures',
    'Saraya':'Sol latéritique · or alluvionnaire',
    'Salékata':'Sol ferralitique · igname et mil',
    'Louga':'Sol Dior sableux · déficit pluviométrique',
    'Linguère':'Sol sableux sahélien · élevage',
    'Kébémer':'Sol Dior · arachide et mil',
    'Matam':'Sol alluvial (Walo) · riz irrigué',
    'Kanel':'Sol alluvial · décrue et irrigation',
    'Ranérou':'Sol sableux sahélien · élevage extensif',
    'Saint-Louis':'Sol alluvial delta · riz irrigué',
    'Podor':'Sol Walo · culture de décrue',
    'Dagana':'Sol argileux lourd · riziculture irriguée',
    'Richard-Toll':'Sol argileux · canne à sucre',
    'Sédhiou':'Sol ferralitique · anacarde',
    'Goudomp':'Sol hydromorphe · riziculture',
    'Bounkiling':'Sol ferralitique · anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical · savane',
    'Bakel':'Sol sableux sahélien · mil et riz de décrue',
    'Goudiry':'Sol ferrugineux · sorgho',
    'Koumpentoum':'Sol ferrugineux · arachide',
    'Thiès':'Sol ferrugineux rouge · phosphate',
    'Mbour':'Sol sableux côtier · maraîchage',
    'Tivaouane':'Sol Dior · arachide',
    'Mékhe':'Sol ferrugineux · maïs',
    'Khombole':'Sol Dior · arachide',
    'Ziguinchor':'Sol ferralitique · riz et anacarde',
    'Bignona':'Sol ferralitique · anacarde',
    'Oussouye':'Sol hydromorphe · riziculture de mangrove',
}

CALENDRIER = {
    'Dakar':{'hivernage':'Juil–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Maraîchage, Niébé','debut_pluies':'20 Juin – 5 Juil'},
    'Pikine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Arachide, Maïs','debut_pluies':'1–10 Juil'},
    'Guediawaye':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Légumes, Maraîchage','debut_pluies':'1–10 Juil'},
    'Rufisque':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Maïs, Niébé','debut_pluies':'5–15 Juil'},
    'Bargny':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maraîchage','debut_pluies':'5–15 Juil'},
    'Diourbel':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juil'},
    'Bambey':{'hivernage':'Juil–Oct','semis':'1–10 Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'1–10 Juil'},
    'Mbacké':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Fatick':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'25 Juin – 10 Juil'},
    'Gossas':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil','debut_pluies':'5–15 Juil'},
    'Foundiougne':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'15–30 Juin'},
    'Sokone':{'hivernage':'Juin–Nov','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'20 Juin – 5 Juil'},
    'Kaolack':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–10 Juil'},
    'Kaffrine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Nioro du Rip':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Coton','debut_pluies':'20 Juin – 5 Juil'},
    'Kolda':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Mil, Coton','debut_pluies':'25 Mai – 10 Juin'},
    'Vélingara':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juin'},
    'Médina Yoro Foulah':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Mil, Arachide','debut_pluies':'1–15 Juin'},
    'Kédougou':{'hivernage':'Avr–Nov','semis':'Avr–Mai','recolte':'Nov–Déc','cultures':'Maïs, Mil, Igname','debut_pluies':'20 Avr – 10 Mai'},
    'Saraya':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Salékata':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Louga':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Arachide, Mil','debut_pluies':'15–31 Juil'},
    'Linguère':{'hivernage':'Juil–Sep','semis':'20–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'20–31 Juil'},
    'Kébémer':{'hivernage':'Juil–Oct','semis':'10–20 Juil','recolte':'Oct','cultures':'Arachide, Mil','debut_pluies':'10–20 Juil'},
    'Matam':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Riz irrigué, Sorgho','debut_pluies':'1–15 Juil'},
    'Kanel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Riz, Mil','debut_pluies':'5–15 Juil'},
    'Ranérou':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'15–31 Juil'},
    'Saint-Louis':{'hivernage':'Juil–Oct','semis':'Juil (irrigué toute année)','recolte':'Oct–Nov','cultures':'Riz irrigué, Légumes','debut_pluies':'1–15 Juil'},
    'Podor':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Dagana':{'hivernage':'Juil–Oct','semis':'Juin (irrigué)','recolte':'Nov','cultures':'Riz irrigué','debut_pluies':'1–15 Juil'},
    'Richard-Toll':{'hivernage':'Toute année','semis':'Continu','recolte':'Continu','cultures':'Canne à sucre, Riz','debut_pluies':'1–10 Juil'},
    'Sédhiou':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Riz, Anacarde','debut_pluies':'20 Mai – 5 Juin'},
    'Goudomp':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'25 Mai – 10 Juin'},
    'Bounkiling':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'1–15 Juin'},
    'Tambacounda':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Arachide, Sorgho','debut_pluies':'10–25 Juin'},
    'Bakel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Goudiry':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Sorgho','debut_pluies':'15–30 Juin'},
    'Koumpentoum':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'15–30 Juin'},
    'Thiès':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Tomate','debut_pluies':'1–10 Juil'},
    'Mbour':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Tomate, Maraîchage','debut_pluies':'1–10 Juil'},
    'Tivaouane':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Mékhe':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maïs, Mil','debut_pluies':'5–15 Juil'},
    'Khombole':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Ziguinchor':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Bignona':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Oussouye':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'10–25 Mai'},
}

def generer_conseil_detaille(commune, region, sol, cal, df_climate=None, scenario="SSP2-4.5"):
    """Génère un conseil agricole approfondi et contextualisé par commune"""
    
    # Données climatiques actuelles et futures
    pluie_actuelle = {
        'Dakar':400,'Pikine':390,'Guediawaye':385,'Rufisque':420,'Bargny':410,
        'Diourbel':520,'Bambey':510,'Mbacké':500,
        'Fatick':650,'Gossas':560,'Foundiougne':700,'Sokone':620,
        'Kaolack':600,'Kaffrine':580,'Nioro du Rip':620,
        'Kolda':900,'Vélingara':850,'Médina Yoro Foulah':880,
        'Kédougou':1300,'Saraya':1200,'Salékata':1250,
        'Louga':280,'Linguère':220,'Kébémer':300,
        'Matam':300,'Kanel':280,'Ranérou':260,
        'Saint-Louis':350,'Podor':250,'Dagana':280,'Richard-Toll':270,
        'Sédhiou':1100,'Goudomp':1150,'Bounkiling':1050,
        'Tambacounda':700,'Bakel':450,'Goudiry':600,'Koumpentoum':750,
        'Thiès':500,'Mbour':550,'Tivaouane':480,'Mékhe':460,'Khombole':490,
        'Ziguinchor':1200,'Bignona':1150,'Oussouye':1300,
    }
    
    temp_actuelle = {
        'Dakar':29.5,'Pikine':30.0,'Guediawaye':30.0,'Rufisque':30.2,'Bargny':30.1,
        'Diourbel':31.5,'Bambey':31.3,'Mbacké':31.8,
        'Fatick':31.0,'Gossas':31.0,'Foundiougne':30.8,'Sokone':31.2,
        'Kaolack':31.8,'Kaffrine':32.0,'Nioro du Rip':31.5,
        'Kolda':31.5,'Vélingara':32.0,'Médina Yoro Foulah':31.8,
        'Kédougou':30.5,'Saraya':31.0,'Salékata':30.8,
        'Louga':31.2,'Linguère':32.0,'Kébémer':31.5,
        'Matam':33.5,'Kanel':33.8,'Ranérou':33.0,
        'Saint-Louis':30.8,'Podor':32.5,'Dagana':32.0,'Richard-Toll':32.2,
        'Sédhiou':31.0,'Goudomp':30.9,'Bounkiling':31.2,
        'Tambacounda':33.1,'Bakel':34.0,'Goudiry':33.5,'Koumpentoum':33.0,
        'Thiès':30.5,'Mbour':30.3,'Tivaouane':30.8,'Mékhe':31.0,'Khombole':30.7,
        'Ziguinchor':30.2,'Bignona':30.5,'Oussouye':30.0,
    }
    
    pluie = pluie_actuelle.get(commune, 500)
    temp  = temp_actuelle.get(commune, 31.0)
    debut = cal.get('debut_pluies', 'Juillet') if cal else 'Juillet'
    cultures = cal.get('cultures', 'Mil, Arachide') if cal else 'Mil, Arachide'
    hivernage = cal.get('hivernage', 'Juil-Oct') if cal else 'Juil-Oct'
    
    # Projections à 30 ans selon scénario
    taux = {'SSP1-1.9':0.03,'SSP2-4.5':0.055,'SSP5-8.5':0.088}
    pluie_rate = {'SSP1-1.9':0.5,'SSP2-4.5':1.0,'SSP5-8.5':1.8}
    
    rate = taux.get(scenario, 0.055)
    prate = pluie_rate.get(scenario, 1.0)
    
    temp_2055   = round(temp + rate * 30, 1)
    pluie_2055  = round(max(0, pluie - pluie * 0.008 * 30 * prate))
    deficit     = pluie - pluie_2055
    hausse_temp = round(temp_2055 - temp, 1)
    
    # Catégorie climatique
    if pluie >= 900:
        zone = "zone humide (Casamance/Guinéenne)"
        zone_conseil = "très favorable à l'agriculture diversifiée"
    elif pluie >= 600:
        zone = "zone soudano-sahélienne"
        zone_conseil = "favorable mais sensible aux variations pluviométriques"
    elif pluie >= 350:
        zone = "zone sahélo-soudanienne"
        zone_conseil = "à risque modéré — adaptation nécessaire"
    else:
        zone = "zone sahélienne sèche"
        zone_conseil = "à risque élevé — pratiques conservatoires essentielles"

    texte = f"""
**📍 Situation actuelle de {commune} ({region})**

{commune} est une commune de {region}, située en **{zone}**, {zone_conseil}. 
Le sol dominant est de type **{sol}**, ce qui conditionne directement les types de cultures possibles, 
la capacité de rétention d'eau et la résistance aux sécheresses.

Actuellement, la commune reçoit en moyenne **{pluie} mm de pluie par an**, avec des températures 
moyennes autour de **{temp}°C**. La saison des pluies (hivernage) s'étend de **{hivernage}**, 
avec un début généralement entre le **{debut}**. Les cultures principales sont : **{cultures}**.

---

**⚠️ Causes et risques climatiques projetés (2025–2055, scénario {scenario})**

Sur les 30 prochaines années, le réchauffement climatique va progressivement modifier les conditions 
agricoles de {commune}. Voici pourquoi :

- 🌡️ **Hausse de température de +{hausse_temp}°C** : Les températures passeront de {temp}°C à environ 
  {temp_2055}°C d'ici 2055. Cette hausse provoque une **évapotranspiration accrue** — les plantes 
  perdent plus d'eau, les sols s'assèchent plus vite, et les besoins en eau des cultures augmentent. 
  Au-delà de 38°C, la plupart des cultures céréalières subissent un **stress thermique** qui réduit 
  leur rendement de 20 à 50%.

- 🌧️ **Déficit pluviométrique de -{deficit} mm** : Les précipitations devraient passer de {pluie} mm 
  à environ {pluie_2055} mm/an, soit une réduction de **{round((deficit/pluie)*100) if pluie>0 else 0}%**. 
  Cela signifie que la saison agricole sera plus courte et les semis plus risqués. Les années de 
  mauvaise pluviométrie seront plus fréquentes et plus sévères.

- 🏜️ **Dégradation du sol** : Le type de sol de {commune} ({sol}) est particulièrement sensible 
  à ces changements. Sous l'effet de la chaleur et du déficit hydrique, la matière organique du sol 
  diminue, réduisant sa fertilité naturelle. Les risques d'érosion éolienne et hydrique augmentent.

---

**💡 Conséquences sur l'agriculture locale**

Sans adaptation, les agriculteurs de {commune} risquent de voir :
- Une **réduction des rendements** de 15 à 40% d'ici 2040 pour les cultures traditionnelles
- Des **pertes de récoltes** lors des années de sécheresse intense (SPEI < -1.5)
- Une **insécurité alimentaire** accrue pour les ménages ruraux
- Un **appauvrissement des sols** progressif rendant certaines parcelles non cultivables
- Des **conflits agriculteurs-éleveurs** intensifiés par la raréfaction des ressources

---

**✅ Solutions et recommandations adaptées à {commune}**

Face à ces défis, voici les actions concrètes recommandées :

**1. Adapter les variétés cultivées**
Passer progressivement aux variétés améliorées résistantes à la sécheresse et à la chaleur. 
Pour {commune}, privilégier les variétés de **{cultures.split(",")[0].strip()}** à cycle court 
(moins de 90 jours) qui permettent de terminer la culture avant la fin de la saison des pluies.

**2. Gérer l'eau de façon optimale**
- Construire des **demi-lunes et des zaï** pour capter et retenir l'eau de pluie
- Installer des **cordons pierreux** perpendiculaires à la pente pour réduire le ruissellement
- Développer des **mares artificielles** et des retenues d'eau pour l'irrigation d'appoint
- Pratiquer le **paillage** (mulching) pour limiter l'évaporation du sol

**3. Protéger et améliorer le sol**
Le sol de type **{sol}** nécessite un apport régulier en matière organique. 
Apporter du compost, pratiquer la **rotation des cultures** et intégrer des légumineuses 
(niébé, arachide) qui fixent l'azote naturellement dans le sol.

**4. Diversifier les sources de revenus**
Ne pas dépendre d'une seule culture. Intégrer l'**arboriculture fruitière** (manguiers, anacardiers) 
qui résistent mieux à la sécheresse une fois établis, et l'**élevage** comme filet de sécurité.

**5. Anticiper le calendrier cultural**
Avec le réchauffement, surveiller attentivement les premières pluies utiles (>20mm en 24h). 
Le début des pluies à {commune} se situe autour du **{debut}** mais peut varier de 2 à 3 semaines 
selon les années. Avoir les semences prêtes à l'avance est crucial.

**6. Se regrouper et mutualiser**
Former des **groupements d'intérêt économique** pour accéder aux semences certifiées, 
aux équipements d'irrigation et aux marchés. La solidarité communautaire est essentielle 
pour faire face aux années difficiles.
"""
    return texte


SOLS = {
    'Dakar':'Sol sableux (Deck-Dior) · faible rétention hydrique',
    'Pikine':'Sol sableux dégradé · urbanisation intense',
    'Guediawaye':'Sol sableux · nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical · bon drainage',
    'Bargny':'Sol salin · mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) · arachide',
    'Bambey':'Sol Dior sableux · très cultivé',
    'Mbacké':'Sol Dior et Deck · polyculture',
    'Fatick':'Sol sulfaté acide · tannes · mangrove',
    'Gossas':'Sol ferrugineux · mil dominant',
    'Foundiougne':'Sol alluvial · riziculture de mangrove',
    'Sokone':'Sol hydromorphe · sel',
    'Kaolack':'Sol argileux (Deck) · bassin arachidier',
    'Kaffrine':'Sol Dior et Deck · transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé · coton',
    'Kolda':'Sol ferralitique · forêt dégradée',
    'Vélingara':'Sol ferrugineux · savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique · cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge · or et cultures',
    'Saraya':'Sol latéritique · or alluvionnaire',
    'Salékata':'Sol ferralitique · igname et mil',
    'Louga':'Sol Dior sableux · déficit pluviométrique',
    'Linguère':'Sol sableux sahélien · élevage',
    'Kébémer':'Sol Dior · arachide et mil',
    'Matam':'Sol alluvial (Walo) · riz irrigué',
    'Kanel':'Sol alluvial · décrue et irrigation',
    'Ranérou':'Sol sableux sahélien · élevage extensif',
    'Saint-Louis':'Sol alluvial delta · riz irrigué',
    'Podor':'Sol Walo · culture de décrue',
    'Dagana':'Sol argileux lourd · riziculture irriguée',
    'Richard-Toll':'Sol argileux · canne à sucre',
    'Sédhiou':'Sol ferralitique · anacarde',
    'Goudomp':'Sol hydromorphe · riziculture',
    'Bounkiling':'Sol ferralitique · anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical · savane',
    'Bakel':'Sol sableux sahélien · mil et riz de décrue',
    'Goudiry':'Sol ferrugineux · sorgho',
    'Koumpentoum':'Sol ferrugineux · arachide',
    'Thiès':'Sol ferrugineux rouge · phosphate',
    'Mbour':'Sol sableux côtier · maraîchage',
    'Tivaouane':'Sol Dior · arachide',
    'Mékhe':'Sol ferrugineux · maïs',
    'Khombole':'Sol Dior · arachide',
    'Ziguinchor':'Sol ferralitique · riz et anacarde',
    'Bignona':'Sol ferralitique · anacarde',
    'Oussouye':'Sol hydromorphe · riziculture de mangrove',
}

CALENDRIER = {
    'Dakar':{'hivernage':'Juil–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Maraîchage, Niébé','debut_pluies':'20 Juin – 5 Juil'},
    'Pikine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Arachide, Maïs','debut_pluies':'1–10 Juil'},
    'Guediawaye':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Légumes, Maraîchage','debut_pluies':'1–10 Juil'},
    'Rufisque':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Maïs, Niébé','debut_pluies':'5–15 Juil'},
    'Bargny':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maraîchage','debut_pluies':'5–15 Juil'},
    'Diourbel':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juil'},
    'Bambey':{'hivernage':'Juil–Oct','semis':'1–10 Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'1–10 Juil'},
    'Mbacké':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Fatick':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'25 Juin – 10 Juil'},
    'Gossas':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil','debut_pluies':'5–15 Juil'},
    'Foundiougne':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'15–30 Juin'},
    'Sokone':{'hivernage':'Juin–Nov','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'20 Juin – 5 Juil'},
    'Kaolack':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–10 Juil'},
    'Kaffrine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Nioro du Rip':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Coton','debut_pluies':'20 Juin – 5 Juil'},
    'Kolda':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Mil, Coton','debut_pluies':'25 Mai – 10 Juin'},
    'Vélingara':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juin'},
    'Médina Yoro Foulah':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Mil, Arachide','debut_pluies':'1–15 Juin'},
    'Kédougou':{'hivernage':'Avr–Nov','semis':'Avr–Mai','recolte':'Nov–Déc','cultures':'Maïs, Mil, Igname','debut_pluies':'20 Avr – 10 Mai'},
    'Saraya':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Salékata':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Louga':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Arachide, Mil','debut_pluies':'15–31 Juil'},
    'Linguère':{'hivernage':'Juil–Sep','semis':'20–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'20–31 Juil'},
    'Kébémer':{'hivernage':'Juil–Oct','semis':'10–20 Juil','recolte':'Oct','cultures':'Arachide, Mil','debut_pluies':'10–20 Juil'},
    'Matam':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Riz irrigué, Sorgho','debut_pluies':'1–15 Juil'},
    'Kanel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Riz, Mil','debut_pluies':'5–15 Juil'},
    'Ranérou':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'15–31 Juil'},
    'Saint-Louis':{'hivernage':'Juil–Oct','semis':'Juil (irrigué toute année)','recolte':'Oct–Nov','cultures':'Riz irrigué, Légumes','debut_pluies':'1–15 Juil'},
    'Podor':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Dagana':{'hivernage':'Juil–Oct','semis':'Juin (irrigué)','recolte':'Nov','cultures':'Riz irrigué','debut_pluies':'1–15 Juil'},
    'Richard-Toll':{'hivernage':'Toute année','semis':'Continu','recolte':'Continu','cultures':'Canne à sucre, Riz','debut_pluies':'1–10 Juil'},
    'Sédhiou':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Riz, Anacarde','debut_pluies':'20 Mai – 5 Juin'},
    'Goudomp':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'25 Mai – 10 Juin'},
    'Bounkiling':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'1–15 Juin'},
    'Tambacounda':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Arachide, Sorgho','debut_pluies':'10–25 Juin'},
    'Bakel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Goudiry':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Sorgho','debut_pluies':'15–30 Juin'},
    'Koumpentoum':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'15–30 Juin'},
    'Thiès':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Tomate','debut_pluies':'1–10 Juil'},
    'Mbour':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Tomate, Maraîchage','debut_pluies':'1–10 Juil'},
    'Tivaouane':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Mékhe':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maïs, Mil','debut_pluies':'5–15 Juil'},
    'Khombole':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Ziguinchor':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Bignona':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Oussouye':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'10–25 Mai'},
}


def generer_conseil_detaille(commune, region, sol, cal, scenario="SSP2-4.5"):
    pluie_base = {
        'Dakar':400,'Pikine':390,'Guediawaye':385,'Rufisque':420,'Bargny':410,
        'Diourbel':520,'Bambey':510,'Mbacke':500,'Fatick':650,'Gossas':560,
        'Foundiougne':700,'Sokone':620,'Kaolack':600,'Kaffrine':580,
        'Nioro du Rip':620,'Kolda':900,'Velingara':850,'Medina Yoro Foulah':880,
        'Kedougou':1300,'Saraya':1200,'Salekata':1250,'Louga':280,
        'Linguere':220,'Kebemer':300,'Matam':300,'Kanel':280,'Ranerou':260,
        'Saint-Louis':350,'Podor':250,'Dagana':280,'Richard-Toll':270,
        'Sedhiou':1100,'Goudomp':1150,'Bounkiling':1050,'Tambacounda':700,
        'Bakel':450,'Goudiry':600,'Koumpentoum':750,'Thies':500,'Mbour':550,
        'Tivaouane':480,'Mekhe':460,'Khombole':490,'Ziguinchor':1200,
        'Bignona':1150,'Oussouye':1300,
    }
    temp_base = {
        'Dakar':29.5,'Pikine':30.0,'Guediawaye':30.0,'Rufisque':30.2,'Bargny':30.1,
        'Diourbel':31.5,'Bambey':31.3,'Mbacke':31.8,'Fatick':31.0,'Gossas':31.0,
        'Foundiougne':30.8,'Sokone':31.2,'Kaolack':31.8,'Kaffrine':32.0,
        'Nioro du Rip':31.5,'Kolda':31.5,'Velingara':32.0,'Medina Yoro Foulah':31.8,
        'Kedougou':30.5,'Saraya':31.0,'Salekata':30.8,'Louga':31.2,
        'Linguere':32.0,'Kebemer':31.5,'Matam':33.5,'Kanel':33.8,'Ranerou':33.0,
        'Saint-Louis':30.8,'Podor':32.5,'Dagana':32.0,'Richard-Toll':32.2,
        'Sedhiou':31.0,'Goudomp':30.9,'Bounkiling':31.2,'Tambacounda':33.1,
        'Bakel':34.0,'Goudiry':33.5,'Koumpentoum':33.0,'Thies':30.5,'Mbour':30.3,
        'Tivaouane':30.8,'Mekhe':31.0,'Khombole':30.7,'Ziguinchor':30.2,
        'Bignona':30.5,'Oussouye':30.0,
    }
    taux_temp  = {'SSP1-1.9':0.03,'SSP2-4.5':0.055,'SSP5-8.5':0.088}
    taux_pluie = {'SSP1-1.9':0.5, 'SSP2-4.5':1.0,  'SSP5-8.5':1.8}

    cle = commune.replace('é','e').replace('è','e').replace('ê','e').replace('â','a').replace('ô','o').replace('û','u').replace('î','i')
    pluie  = pluie_base.get(cle, pluie_base.get(commune, 500))
    temp   = temp_base.get(cle,  temp_base.get(commune, 31.0))
    rate_t = taux_temp.get(scenario, 0.055)
    rate_p = taux_pluie.get(scenario, 1.0)

    temp_2055  = round(temp  + rate_t * 30, 1)
    pluie_2055 = round(max(0, pluie - pluie * 0.008 * 30 * rate_p))
    deficit    = pluie - pluie_2055
    hausse     = round(temp_2055 - temp, 1)
    pct_deficit= round((deficit / pluie) * 100) if pluie > 0 else 0

    debut    = cal.get('debut_pluies','Juillet') if cal else 'Juillet'
    cultures = cal.get('cultures','Mil, Arachide') if cal else 'Mil, Arachide'
    hivern   = cal.get('hivernage','Juil-Oct') if cal else 'Juil-Oct'
    culture1 = cultures.split(',')[0].strip()

    if pluie >= 900:
        zone = "zone humide (domaine guinéen-casamançais)"
        zone_c = "très favorable à une agriculture diversifiée et intensive"
    elif pluie >= 600:
        zone = "zone soudano-sahélienne"
        zone_c = "favorable mais sensible aux variations pluviométriques interannuelles"
    elif pluie >= 350:
        zone = "zone sahélo-soudanienne"
        zone_c = "à risque modéré nécessitant des pratiques d'adaptation progressives"
    else:
        zone = "zone sahélienne sèche"
        zone_c = "à risque élevé où chaque millimètre de pluie est précieux"

    return f"""
### 📍 Situation actuelle de {commune} ({region})

{commune} est une commune de la région de {region}, localisée en **{zone}**, {zone_c}.
Le sol dominant est de type **{sol}**.
Ce type de sol conditionne directement les cultures possibles, la capacité à retenir l'eau et
la résistance naturelle aux périodes de sécheresse.

Aujourd'hui, {commune} reçoit en moyenne **{pluie} mm de pluie par an**, avec des températures
moyennes autour de **{temp}°C**. La saison agricole (hivernage) s'étend de **{hivern}**,
avec les premières pluies utiles attendues vers le **{debut}**.
Les cultures pratiquées sont principalement : **{cultures}**.

---

### ⚠️ Causes et risques climatiques projetés (2025–2055 · scénario {scenario})

Sur les 30 prochaines années, le réchauffement climatique va modifier les conditions de {commune}.
Voici les mécanismes en jeu :

🌡️ **Hausse de température de +{hausse}°C**
Les températures passeront de {temp}°C à environ **{temp_2055}°C d'ici 2055**.
Concrètement, cela provoque une **évapotranspiration accrue** : les plantes transpirent davantage,
les sols s'assèchent plus rapidement, et les besoins en eau des cultures augmentent alors même que
la pluie se raréfie. Au-delà de 38°C, les céréales (mil, sorgho, maïs) subissent un stress thermique
qui peut réduire leur rendement de **20 à 50%**. Pour le sol de {commune}, de type **{sol}**,
la hausse des températures accélère également la minéralisation de la matière organique,
appauvrissant progressivement la terre.

🌧️ **Déficit pluviométrique de -{deficit} mm ({pct_deficit}% de réduction)**
Les précipitations baisseront de {pluie} mm à environ **{pluie_2055} mm/an**.
Cela ne veut pas dire qu'il pleuvra moins chaque jour, mais que les épisodes secs seront
plus longs et les épisodes pluvieux plus intenses et irréguliers.
Pour {commune}, cela signifie des semis de **{culture1}** plus risqués : si la pluie arrive
tardivement (après le {debut}), une partie de la saison est perdue. Les années où le déficit
dépasse 30%, les récoltes peuvent être catastrophiques.

🏜️ **Dégradation progressive du sol**
Le sol de {commune} ({sol}) est sensible à ce double stress thermique et hydrique.
Sans couverture végétale suffisante, les pluies intenses lessivent les éléments nutritifs,
l'érosion s'accélère, et la croûte du sol se durcit, réduisant l'infiltration de l'eau.
Un sol dégradé produit moins, nécessite plus d'intrants, et devient moins rentable à cultiver.

---

### 💡 Conséquences concrètes pour les agriculteurs de {commune}

Sans adaptation, les agriculteurs risquent de subir :
- Une **réduction des rendements de 15 à 40%** d'ici 2040 sur les cultures traditionnelles
- Des **années de récolte nulle** lors des sécheresses sévères (de plus en plus fréquentes)
- Une **insécurité alimentaire** accrue, notamment pour les ménages sans revenus diversifiés
- Un **appauvrissement progressif des sols** rendant certaines parcelles inexploitables
- Des **tensions** sur les ressources en eau et les pâturages

---

### ✅ Solutions concrètes adaptées à {commune}

**1. Choisir les bonnes variétés**
Adopter des variétés de **{culture1}** à cycle court (60-90 jours) et résistantes à la chaleur.
Ces variétés terminent leur cycle avant la fin de l'hivernage, réduisant le risque de perte.
Des semences certifiées sont disponibles auprès de l'ISRA et des coopératives locales.

**2. Mieux gérer chaque goutte d'eau**
- Creuser des **demi-lunes et des zaï** autour des pieds de plantes pour concentrer l'eau
- Construire des **cordons pierreux** le long des courbes de niveau pour stopper le ruissellement
- Pratiquer le **paillage (mulching)** avec des résidus de récolte pour limiter l'évaporation
- Récupérer l'eau de pluie dans des **bassins ou des jarres** pour l'irrigation d'appoint

**3. Nourrir et protéger le sol de {commune}**
Le sol de type **{sol}** nécessite un apport régulier en matière organique.
Produire et épandre du **compost** (déchets organiques + fumier), intégrer des **légumineuses**
(niébé, dolique) dans les rotations pour fixer l'azote, et éviter de laisser le sol nu
entre deux cultures pour limiter l'érosion.

**4. Diversifier pour réduire les risques**
Ne jamais dépendre d'une seule culture. Associer les céréales aux légumineuses, introduire
des **arbres fruitiers** (manguiers, anacardiers, neem) qui constituent un revenu à long terme
et protègent les sols. L'élevage de petits ruminants (moutons, chèvres) offre un filet de sécurité.

**5. Surveiller et anticiper le calendrier**
Le début des pluies à {commune} (autour du **{debut}**) peut varier de 2 à 4 semaines selon les
années. Préparer les semences, les outils et les champs **à l'avance** est crucial.
Ne semer qu'après une pluie utile de plus de **20 mm en 24 heures** pour éviter les faux départs.

**6. Se regrouper et partager les ressources**
Former des **groupements paysans** pour accéder collectivement aux semences certifiées,
aux équipements d'irrigation, au crédit agricole et aux marchés. La solidarité communautaire
est le meilleur outil d'adaptation face aux années difficiles.
"""


SOLS = {
    'Dakar':'Sol sableux (Deck-Dior) · faible rétention hydrique',
    'Pikine':'Sol sableux dégradé · urbanisation intense',
    'Guediawaye':'Sol sableux · nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical · bon drainage',
    'Bargny':'Sol salin · mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) · arachide',
    'Bambey':'Sol Dior sableux · très cultivé',
    'Mbacké':'Sol Dior et Deck · polyculture',
    'Fatick':'Sol sulfaté acide · tannes · mangrove',
    'Gossas':'Sol ferrugineux · mil dominant',
    'Foundiougne':'Sol alluvial · riziculture de mangrove',
    'Sokone':'Sol hydromorphe · sel',
    'Kaolack':'Sol argileux (Deck) · bassin arachidier',
    'Kaffrine':'Sol Dior et Deck · transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé · coton',
    'Kolda':'Sol ferralitique · forêt dégradée',
    'Vélingara':'Sol ferrugineux · savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique · cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge · or et cultures',
    'Saraya':'Sol latéritique · or alluvionnaire',
    'Salékata':'Sol ferralitique · igname et mil',
    'Louga':'Sol Dior sableux · déficit pluviométrique',
    'Linguère':'Sol sableux sahélien · élevage',
    'Kébémer':'Sol Dior · arachide et mil',
    'Matam':'Sol alluvial (Walo) · riz irrigué',
    'Kanel':'Sol alluvial · décrue et irrigation',
    'Ranérou':'Sol sableux sahélien · élevage extensif',
    'Saint-Louis':'Sol alluvial delta · riz irrigué',
    'Podor':'Sol Walo · culture de décrue',
    'Dagana':'Sol argileux lourd · riziculture irriguée',
    'Richard-Toll':'Sol argileux · canne à sucre',
    'Sédhiou':'Sol ferralitique · anacarde',
    'Goudomp':'Sol hydromorphe · riziculture',
    'Bounkiling':'Sol ferralitique · anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical · savane',
    'Bakel':'Sol sableux sahélien · mil et riz de décrue',
    'Goudiry':'Sol ferrugineux · sorgho',
    'Koumpentoum':'Sol ferrugineux · arachide',
    'Thiès':'Sol ferrugineux rouge · phosphate',
    'Mbour':'Sol sableux côtier · maraîchage',
    'Tivaouane':'Sol Dior · arachide',
    'Mékhe':'Sol ferrugineux · maïs',
    'Khombole':'Sol Dior · arachide',
    'Ziguinchor':'Sol ferralitique · riz et anacarde',
    'Bignona':'Sol ferralitique · anacarde',
    'Oussouye':'Sol hydromorphe · riziculture de mangrove',
}

CALENDRIER = {
    'Dakar':{'hivernage':'Juil–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Maraîchage, Niébé','debut_pluies':'20 Juin – 5 Juil'},
    'Pikine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Arachide, Maïs','debut_pluies':'1–10 Juil'},
    'Guediawaye':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Légumes, Maraîchage','debut_pluies':'1–10 Juil'},
    'Rufisque':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Maïs, Niébé','debut_pluies':'5–15 Juil'},
    'Bargny':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maraîchage','debut_pluies':'5–15 Juil'},
    'Diourbel':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juil'},
    'Bambey':{'hivernage':'Juil–Oct','semis':'1–10 Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'1–10 Juil'},
    'Mbacké':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Fatick':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'25 Juin – 10 Juil'},
    'Gossas':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil','debut_pluies':'5–15 Juil'},
    'Foundiougne':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'15–30 Juin'},
    'Sokone':{'hivernage':'Juin–Nov','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'20 Juin – 5 Juil'},
    'Kaolack':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–10 Juil'},
    'Kaffrine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Nioro du Rip':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Coton','debut_pluies':'20 Juin – 5 Juil'},
    'Kolda':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Mil, Coton','debut_pluies':'25 Mai – 10 Juin'},
    'Vélingara':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juin'},
    'Médina Yoro Foulah':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Mil, Arachide','debut_pluies':'1–15 Juin'},
    'Kédougou':{'hivernage':'Avr–Nov','semis':'Avr–Mai','recolte':'Nov–Déc','cultures':'Maïs, Mil, Igname','debut_pluies':'20 Avr – 10 Mai'},
    'Saraya':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Salékata':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Louga':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Arachide, Mil','debut_pluies':'15–31 Juil'},
    'Linguère':{'hivernage':'Juil–Sep','semis':'20–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'20–31 Juil'},
    'Kébémer':{'hivernage':'Juil–Oct','semis':'10–20 Juil','recolte':'Oct','cultures':'Arachide, Mil','debut_pluies':'10–20 Juil'},
    'Matam':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Riz irrigué, Sorgho','debut_pluies':'1–15 Juil'},
    'Kanel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Riz, Mil','debut_pluies':'5–15 Juil'},
    'Ranérou':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'15–31 Juil'},
    'Saint-Louis':{'hivernage':'Juil–Oct','semis':'Juil (irrigué toute année)','recolte':'Oct–Nov','cultures':'Riz irrigué, Légumes','debut_pluies':'1–15 Juil'},
    'Podor':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Dagana':{'hivernage':'Juil–Oct','semis':'Juin (irrigué)','recolte':'Nov','cultures':'Riz irrigué','debut_pluies':'1–15 Juil'},
    'Richard-Toll':{'hivernage':'Toute année','semis':'Continu','recolte':'Continu','cultures':'Canne à sucre, Riz','debut_pluies':'1–10 Juil'},
    'Sédhiou':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Riz, Anacarde','debut_pluies':'20 Mai – 5 Juin'},
    'Goudomp':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'25 Mai – 10 Juin'},
    'Bounkiling':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'1–15 Juin'},
    'Tambacounda':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Arachide, Sorgho','debut_pluies':'10–25 Juin'},
    'Bakel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Goudiry':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Sorgho','debut_pluies':'15–30 Juin'},
    'Koumpentoum':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'15–30 Juin'},
    'Thiès':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Tomate','debut_pluies':'1–10 Juil'},
    'Mbour':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Tomate, Maraîchage','debut_pluies':'1–10 Juil'},
    'Tivaouane':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Mékhe':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maïs, Mil','debut_pluies':'5–15 Juil'},
    'Khombole':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Ziguinchor':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Bignona':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Oussouye':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'10–25 Mai'},
}

def generer_conseil_detaille(commune, region, sol, cal, df_climate=None, scenario="SSP2-4.5"):
    """Génère un conseil agricole approfondi et contextualisé par commune"""
    
    # Données climatiques actuelles et futures
    pluie_actuelle = {
        'Dakar':400,'Pikine':390,'Guediawaye':385,'Rufisque':420,'Bargny':410,
        'Diourbel':520,'Bambey':510,'Mbacké':500,
        'Fatick':650,'Gossas':560,'Foundiougne':700,'Sokone':620,
        'Kaolack':600,'Kaffrine':580,'Nioro du Rip':620,
        'Kolda':900,'Vélingara':850,'Médina Yoro Foulah':880,
        'Kédougou':1300,'Saraya':1200,'Salékata':1250,
        'Louga':280,'Linguère':220,'Kébémer':300,
        'Matam':300,'Kanel':280,'Ranérou':260,
        'Saint-Louis':350,'Podor':250,'Dagana':280,'Richard-Toll':270,
        'Sédhiou':1100,'Goudomp':1150,'Bounkiling':1050,
        'Tambacounda':700,'Bakel':450,'Goudiry':600,'Koumpentoum':750,
        'Thiès':500,'Mbour':550,'Tivaouane':480,'Mékhe':460,'Khombole':490,
        'Ziguinchor':1200,'Bignona':1150,'Oussouye':1300,
    }
    
    temp_actuelle = {
        'Dakar':29.5,'Pikine':30.0,'Guediawaye':30.0,'Rufisque':30.2,'Bargny':30.1,
        'Diourbel':31.5,'Bambey':31.3,'Mbacké':31.8,
        'Fatick':31.0,'Gossas':31.0,'Foundiougne':30.8,'Sokone':31.2,
        'Kaolack':31.8,'Kaffrine':32.0,'Nioro du Rip':31.5,
        'Kolda':31.5,'Vélingara':32.0,'Médina Yoro Foulah':31.8,
        'Kédougou':30.5,'Saraya':31.0,'Salékata':30.8,
        'Louga':31.2,'Linguère':32.0,'Kébémer':31.5,
        'Matam':33.5,'Kanel':33.8,'Ranérou':33.0,
        'Saint-Louis':30.8,'Podor':32.5,'Dagana':32.0,'Richard-Toll':32.2,
        'Sédhiou':31.0,'Goudomp':30.9,'Bounkiling':31.2,
        'Tambacounda':33.1,'Bakel':34.0,'Goudiry':33.5,'Koumpentoum':33.0,
        'Thiès':30.5,'Mbour':30.3,'Tivaouane':30.8,'Mékhe':31.0,'Khombole':30.7,
        'Ziguinchor':30.2,'Bignona':30.5,'Oussouye':30.0,
    }
    
    pluie = pluie_actuelle.get(commune, 500)
    temp  = temp_actuelle.get(commune, 31.0)
    debut = cal.get('debut_pluies', 'Juillet') if cal else 'Juillet'
    cultures = cal.get('cultures', 'Mil, Arachide') if cal else 'Mil, Arachide'
    hivernage = cal.get('hivernage', 'Juil-Oct') if cal else 'Juil-Oct'
    
    # Projections à 30 ans selon scénario
    taux = {'SSP1-1.9':0.03,'SSP2-4.5':0.055,'SSP5-8.5':0.088}
    pluie_rate = {'SSP1-1.9':0.5,'SSP2-4.5':1.0,'SSP5-8.5':1.8}
    
    rate = taux.get(scenario, 0.055)
    prate = pluie_rate.get(scenario, 1.0)
    
    temp_2055   = round(temp + rate * 30, 1)
    pluie_2055  = round(max(0, pluie - pluie * 0.008 * 30 * prate))
    deficit     = pluie - pluie_2055
    hausse_temp = round(temp_2055 - temp, 1)
    
    # Catégorie climatique
    if pluie >= 900:
        zone = "zone humide (Casamance/Guinéenne)"
        zone_conseil = "très favorable à l'agriculture diversifiée"
    elif pluie >= 600:
        zone = "zone soudano-sahélienne"
        zone_conseil = "favorable mais sensible aux variations pluviométriques"
    elif pluie >= 350:
        zone = "zone sahélo-soudanienne"
        zone_conseil = "à risque modéré — adaptation nécessaire"
    else:
        zone = "zone sahélienne sèche"
        zone_conseil = "à risque élevé — pratiques conservatoires essentielles"

    texte = f"""
**📍 Situation actuelle de {commune} ({region})**

{commune} est une commune de {region}, située en **{zone}**, {zone_conseil}. 
Le sol dominant est de type **{sol}**, ce qui conditionne directement les types de cultures possibles, 
la capacité de rétention d'eau et la résistance aux sécheresses.

Actuellement, la commune reçoit en moyenne **{pluie} mm de pluie par an**, avec des températures 
moyennes autour de **{temp}°C**. La saison des pluies (hivernage) s'étend de **{hivernage}**, 
avec un début généralement entre le **{debut}**. Les cultures principales sont : **{cultures}**.

---

**⚠️ Causes et risques climatiques projetés (2025–2055, scénario {scenario})**

Sur les 30 prochaines années, le réchauffement climatique va progressivement modifier les conditions 
agricoles de {commune}. Voici pourquoi :

- 🌡️ **Hausse de température de +{hausse_temp}°C** : Les températures passeront de {temp}°C à environ 
  {temp_2055}°C d'ici 2055. Cette hausse provoque une **évapotranspiration accrue** — les plantes 
  perdent plus d'eau, les sols s'assèchent plus vite, et les besoins en eau des cultures augmentent. 
  Au-delà de 38°C, la plupart des cultures céréalières subissent un **stress thermique** qui réduit 
  leur rendement de 20 à 50%.

- 🌧️ **Déficit pluviométrique de -{deficit} mm** : Les précipitations devraient passer de {pluie} mm 
  à environ {pluie_2055} mm/an, soit une réduction de **{round((deficit/pluie)*100) if pluie>0 else 0}%**. 
  Cela signifie que la saison agricole sera plus courte et les semis plus risqués. Les années de 
  mauvaise pluviométrie seront plus fréquentes et plus sévères.

- 🏜️ **Dégradation du sol** : Le type de sol de {commune} ({sol}) est particulièrement sensible 
  à ces changements. Sous l'effet de la chaleur et du déficit hydrique, la matière organique du sol 
  diminue, réduisant sa fertilité naturelle. Les risques d'érosion éolienne et hydrique augmentent.

---

**💡 Conséquences sur l'agriculture locale**

Sans adaptation, les agriculteurs de {commune} risquent de voir :
- Une **réduction des rendements** de 15 à 40% d'ici 2040 pour les cultures traditionnelles
- Des **pertes de récoltes** lors des années de sécheresse intense (SPEI < -1.5)
- Une **insécurité alimentaire** accrue pour les ménages ruraux
- Un **appauvrissement des sols** progressif rendant certaines parcelles non cultivables
- Des **conflits agriculteurs-éleveurs** intensifiés par la raréfaction des ressources

---

**✅ Solutions et recommandations adaptées à {commune}**

Face à ces défis, voici les actions concrètes recommandées :

**1. Adapter les variétés cultivées**
Passer progressivement aux variétés améliorées résistantes à la sécheresse et à la chaleur. 
Pour {commune}, privilégier les variétés de **{cultures.split(",")[0].strip()}** à cycle court 
(moins de 90 jours) qui permettent de terminer la culture avant la fin de la saison des pluies.

**2. Gérer l'eau de façon optimale**
- Construire des **demi-lunes et des zaï** pour capter et retenir l'eau de pluie
- Installer des **cordons pierreux** perpendiculaires à la pente pour réduire le ruissellement
- Développer des **mares artificielles** et des retenues d'eau pour l'irrigation d'appoint
- Pratiquer le **paillage** (mulching) pour limiter l'évaporation du sol

**3. Protéger et améliorer le sol**
Le sol de type **{sol}** nécessite un apport régulier en matière organique. 
Apporter du compost, pratiquer la **rotation des cultures** et intégrer des légumineuses 
(niébé, arachide) qui fixent l'azote naturellement dans le sol.

**4. Diversifier les sources de revenus**
Ne pas dépendre d'une seule culture. Intégrer l'**arboriculture fruitière** (manguiers, anacardiers) 
qui résistent mieux à la sécheresse une fois établis, et l'**élevage** comme filet de sécurité.

**5. Anticiper le calendrier cultural**
Avec le réchauffement, surveiller attentivement les premières pluies utiles (>20mm en 24h). 
Le début des pluies à {commune} se situe autour du **{debut}** mais peut varier de 2 à 3 semaines 
selon les années. Avoir les semences prêtes à l'avance est crucial.

**6. Se regrouper et mutualiser**
Former des **groupements d'intérêt économique** pour accéder aux semences certifiées, 
aux équipements d'irrigation et aux marchés. La solidarité communautaire est essentielle 
pour faire face aux années difficiles.
"""
    return texte


SOLS = {
    'Dakar':'Sol sableux (Deck-Dior) · faible rétention hydrique',
    'Pikine':'Sol sableux dégradé · urbanisation intense',
    'Guediawaye':'Sol sableux · nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical · bon drainage',
    'Bargny':'Sol salin · mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) · arachide',
    'Bambey':'Sol Dior sableux · très cultivé',
    'Mbacké':'Sol Dior et Deck · polyculture',
    'Fatick':'Sol sulfaté acide · tannes · mangrove',
    'Gossas':'Sol ferrugineux · mil dominant',
    'Foundiougne':'Sol alluvial · riziculture de mangrove',
    'Sokone':'Sol hydromorphe · sel',
    'Kaolack':'Sol argileux (Deck) · bassin arachidier',
    'Kaffrine':'Sol Dior et Deck · transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé · coton',
    'Kolda':'Sol ferralitique · forêt dégradée',
    'Vélingara':'Sol ferrugineux · savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique · cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge · or et cultures',
    'Saraya':'Sol latéritique · or alluvionnaire',
    'Salékata':'Sol ferralitique · igname et mil',
    'Louga':'Sol Dior sableux · déficit pluviométrique',
    'Linguère':'Sol sableux sahélien · élevage',
    'Kébémer':'Sol Dior · arachide et mil',
    'Matam':'Sol alluvial (Walo) · riz irrigué',
    'Kanel':'Sol alluvial · décrue et irrigation',
    'Ranérou':'Sol sableux sahélien · élevage extensif',
    'Saint-Louis':'Sol alluvial delta · riz irrigué',
    'Podor':'Sol Walo · culture de décrue',
    'Dagana':'Sol argileux lourd · riziculture irriguée',
    'Richard-Toll':'Sol argileux · canne à sucre',
    'Sédhiou':'Sol ferralitique · anacarde',
    'Goudomp':'Sol hydromorphe · riziculture',
    'Bounkiling':'Sol ferralitique · anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical · savane',
    'Bakel':'Sol sableux sahélien · mil et riz de décrue',
    'Goudiry':'Sol ferrugineux · sorgho',
    'Koumpentoum':'Sol ferrugineux · arachide',
    'Thiès':'Sol ferrugineux rouge · phosphate',
    'Mbour':'Sol sableux côtier · maraîchage',
    'Tivaouane':'Sol Dior · arachide',
    'Mékhe':'Sol ferrugineux · maïs',
    'Khombole':'Sol Dior · arachide',
    'Ziguinchor':'Sol ferralitique · riz et anacarde',
    'Bignona':'Sol ferralitique · anacarde',
    'Oussouye':'Sol hydromorphe · riziculture de mangrove',
}

CALENDRIER = {
    'Dakar':{'hivernage':'Juil–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Maraîchage, Niébé','debut_pluies':'20 Juin – 5 Juil'},
    'Pikine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Arachide, Maïs','debut_pluies':'1–10 Juil'},
    'Guediawaye':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Légumes, Maraîchage','debut_pluies':'1–10 Juil'},
    'Rufisque':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Maïs, Niébé','debut_pluies':'5–15 Juil'},
    'Bargny':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maraîchage','debut_pluies':'5–15 Juil'},
    'Diourbel':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juil'},
    'Bambey':{'hivernage':'Juil–Oct','semis':'1–10 Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'1–10 Juil'},
    'Mbacké':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Fatick':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'25 Juin – 10 Juil'},
    'Gossas':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil','debut_pluies':'5–15 Juil'},
    'Foundiougne':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'15–30 Juin'},
    'Sokone':{'hivernage':'Juin–Nov','semis':'Juil','recolte':'Nov','cultures':'Arachide, Riz','debut_pluies':'20 Juin – 5 Juil'},
    'Kaolack':{'hivernage':'Juil–Oct','semis':'1–15 Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'1–10 Juil'},
    'Kaffrine':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'5–15 Juil'},
    'Nioro du Rip':{'hivernage':'Juin–Nov','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Coton','debut_pluies':'20 Juin – 5 Juil'},
    'Kolda':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Mil, Coton','debut_pluies':'25 Mai – 10 Juin'},
    'Vélingara':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'1–15 Juin'},
    'Médina Yoro Foulah':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov','cultures':'Mil, Arachide','debut_pluies':'1–15 Juin'},
    'Kédougou':{'hivernage':'Avr–Nov','semis':'Avr–Mai','recolte':'Nov–Déc','cultures':'Maïs, Mil, Igname','debut_pluies':'20 Avr – 10 Mai'},
    'Saraya':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Salékata':{'hivernage':'Avr–Nov','semis':'Mai','recolte':'Nov','cultures':'Mil, Igname','debut_pluies':'1–15 Mai'},
    'Louga':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Arachide, Mil','debut_pluies':'15–31 Juil'},
    'Linguère':{'hivernage':'Juil–Sep','semis':'20–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'20–31 Juil'},
    'Kébémer':{'hivernage':'Juil–Oct','semis':'10–20 Juil','recolte':'Oct','cultures':'Arachide, Mil','debut_pluies':'10–20 Juil'},
    'Matam':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Riz irrigué, Sorgho','debut_pluies':'1–15 Juil'},
    'Kanel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Nov','cultures':'Riz, Mil','debut_pluies':'5–15 Juil'},
    'Ranérou':{'hivernage':'Juil–Sep','semis':'15–31 Juil','recolte':'Sep–Oct','cultures':'Mil, Niébé','debut_pluies':'15–31 Juil'},
    'Saint-Louis':{'hivernage':'Juil–Oct','semis':'Juil (irrigué toute année)','recolte':'Oct–Nov','cultures':'Riz irrigué, Légumes','debut_pluies':'1–15 Juil'},
    'Podor':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Dagana':{'hivernage':'Juil–Oct','semis':'Juin (irrigué)','recolte':'Nov','cultures':'Riz irrigué','debut_pluies':'1–15 Juil'},
    'Richard-Toll':{'hivernage':'Toute année','semis':'Continu','recolte':'Continu','cultures':'Canne à sucre, Riz','debut_pluies':'1–10 Juil'},
    'Sédhiou':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Arachide, Riz, Anacarde','debut_pluies':'20 Mai – 5 Juin'},
    'Goudomp':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov','cultures':'Arachide, Mil','debut_pluies':'25 Mai – 10 Juin'},
    'Bounkiling':{'hivernage':'Mai–Nov','semis':'Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'1–15 Juin'},
    'Tambacounda':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Arachide, Sorgho','debut_pluies':'10–25 Juin'},
    'Bakel':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Mil, Riz de décrue','debut_pluies':'5–20 Juil'},
    'Goudiry':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Mil, Sorgho','debut_pluies':'15–30 Juin'},
    'Koumpentoum':{'hivernage':'Juin–Oct','semis':'Juin–Juil','recolte':'Oct–Nov','cultures':'Arachide, Mil','debut_pluies':'15–30 Juin'},
    'Thiès':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide, Tomate','debut_pluies':'1–10 Juil'},
    'Mbour':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Tomate, Maraîchage','debut_pluies':'1–10 Juil'},
    'Tivaouane':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Mékhe':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct','cultures':'Maïs, Mil','debut_pluies':'5–15 Juil'},
    'Khombole':{'hivernage':'Juil–Oct','semis':'Juil','recolte':'Oct–Nov','cultures':'Arachide','debut_pluies':'5–15 Juil'},
    'Ziguinchor':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Bignona':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz, Anacarde','debut_pluies':'15–31 Mai'},
    'Oussouye':{'hivernage':'Mai–Nov','semis':'Mai–Juin','recolte':'Nov–Déc','cultures':'Riz de mangrove','debut_pluies':'10–25 Mai'},
}

CONSEILS = {
    'Dakar':'Maraîchage urbain. Récupération eaux de pluie. Éviter cultures céréalières en zone dense.',
    'Pikine':'Cultures courte durée (45-60j). Variétés arachide résistantes sécheresse. Compostage.',
    'Guediawaye':'Maraîchage péri-urbain. Irrigation goutte-à-goutte. Légumes cycle court.',
    'Rufisque':'Associer maraîchage et céréales. Protéger sols contre érosion éolienne.',
    'Bargny':'Éviter cultures en zones salines. Pêche prioritaire. Reboisement mangrove.',
    'Diourbel':'Rotation arachide-mil obligatoire. Variétés 75-90j (55-437, Fleur 11). Demi-lunes.',
    'Bambey':'Spécialisation arachide. Semis dès 1ère pluie utile >20mm. Engrais organique zaï.',
    'Mbacké':'Arachide + niébé en association. Jachère courte. Cordons pierreux.',
    'Fatick':'Aménagement tannes pour riz. Variétés tolérantes salinité. Mangrove à protéger.',
    'Gossas':'Mil souna prioritaire. Semis groupés. Banques céréalières villageoises.',
    'Foundiougne':'Riziculture de mangrove. Diguettes anti-sel. Riz flottant en zones inondées.',
    'Sokone':'Diversification riz-arachide. Protection berges. Aquaculture en complément.',
    'Kaolack':'Rotation arachide-sorgho. Stockage semences certifiées. Sol Deck bien géré.',
    'Kaffrine':'Adapter calendrier aux variations pluviométriques. Assurance agricole recommandée.',
    'Nioro du Rip':'Coton + arachide en rotation. Maintenir couverture végétale. Lutte anti-érosion.',
    'Kolda':'Diversifier (maïs, soja, anacarde). Forêts communautaires. Apiculture.',
    'Vélingara':'Arachide précoce + vivrier. Bas-fonds pour riz. Vergers anacarde.',
    'Médina Yoro Foulah':'Sol difficile : engrais verts, jachère améliorée. Sorgho adapté.',
    'Kédougou':'Maïs hybride + igname. Protection forêts galeries. Ruchers. Zone très humide.',
    'Saraya':'Diversifier or et agriculture. Mil rustique. Agroforesterie parkia-faidherbia.',
    'Salékata':'Igname + mil en association. Éviter brûlis. Banques semences locales.',
    'Louga':'Mil souna 55 jours obligatoire. Zaï + demi-lunes. Réservoirs collinaires.',
    'Linguère':'Élevage prioritaire. Mil uniquement en années humides. Embouche bovine.',
    'Kébémer':'Arachide hâtive 75j. Régénération naturelle assistée. Fixation dunes.',
    'Matam':'Riz irrigué SAED. Double culture possible. Maraîchage contre-saison.',
    'Kanel':'Décrue + irrigation. Riz + sorgho. Diguettes de retenue. Banques fourragères.',
    'Ranérou':'Élevage dominant. Mil en hivernage court. Puits pastoraux. RNA.',
    'Saint-Louis':'Riz irrigué 2 campagnes/an. Tomate industrielle. Oignon. Delta fertile.',
    'Podor':'Culture de décrue walo. Riz périmètre irrigué. Mil en zone diéri.',
    'Dagana':'Riziculture irriguée intensive. Canne à sucre. Mécanisation possible.',
    'Richard-Toll':'Canne à sucre industrielle. Riz irrigué 2 cycles. Drainage essentiel.',
    'Sédhiou':'Anacarde en expansion. Riz + arachide. Transformation locale anacarde.',
    'Goudomp':'Arachide + mil. Bas-fonds rizicoles. Agroforesterie recommandée.',
    'Bounkiling':'Anacarde prioritaire. Riz pluvial. Forêts communautaires à préserver.',
    'Tambacounda':'Mil + sorgho résistants. Arachide en rotation. Élevage intégré. Embouche.',
    'Bakel':'Mil souna court. Décrue. Gomme arabique. Élevage. Zone sahélienne difficile.',
    'Goudiry':'Sorgho adapté sols lourds. Niébé fourrager. Élevage bovin extensif.',
    'Koumpentoum':'Arachide + niébé. Rotation avec sorgho. Warrantage agricole.',
    'Thiès':'Arachide + tomate industrielle. Phosphate naturel comme engrais local.',
    'Mbour':'Maraîchage tomate-oignon-chou. Irrigation puits. Agrotourisme.',
    'Tivaouane':'Arachide dominante. Semis sous pluie. Neem comme brise-vent.',
    'Mékhe':'Maïs + mil. Sols bien drainés. Mécanisation tracteur possible.',
    'Khombole':'Arachide hâtive. Association niébé. Cordons pierreux anti-érosion.',
    'Ziguinchor':'Riz + anacarde. Zone très favorable. Maraîchage contre-saison. Vergers.',
    'Bignona':'Anacarde en forte expansion. Riz pluvial + bas-fonds. Huile de palme.',
    'Oussouye':'Riz sacré de mangrove. Pratiques traditionnelles diola efficaces. Pêche.',
}

def afficher_calendrier_gantt(commune):
    """Calendrier cultural sous forme de tableau Gantt Jan-Déc"""
    MOIS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
    
    # Données Gantt par commune : {culture: [mois_debut, mois_fin]}
    GANTT = {
        'Dakar':        [("Maraîchage",1,12),("Niébé",7,10),("Pêche",1,12),("Légumes",10,4)],
        'Pikine':       [("Arachide",7,11),("Maïs",7,10),("Maraîchage",11,4),("Niébé",8,10),("Manioc",1,12)],
        'Guediawaye':   [("Légumes",1,12),("Maraîchage",10,4),("Niébé",8,10)],
        'Rufisque':     [("Maïs",7,10),("Niébé",7,10),("Maraîchage",11,5),("Arachide",7,11)],
        'Bargny':       [("Maraîchage",11,5),("Pêche",1,12),("Niébé",8,10)],
        'Diourbel':     [("Arachide",7,11),("Mil",7,10),("Niébé",8,10),("Sorgho",7,11),("Manioc",1,12)],
        'Bambey':       [("Arachide",7,11),("Niébé",8,10),("Mil",7,10),("Sorgho",7,11)],
        'Mbacké':       [("Arachide",7,11),("Mil",7,10),("Niébé",8,10),("Sorgho",7,11)],
        'Fatick':       [("Arachide",7,11),("Riz pluvial",7,12),("Riz mangrove",6,12),("Maraîchage",12,4),("Mil",7,10),("Pêche",1,12)],
        'Gossas':       [("Mil",7,10),("Niébé",8,10),("Arachide",7,11),("Sorgho",7,11)],
        'Foundiougne':  [("Riz mangrove",6,12),("Riz pluvial",6,11),("Pêche",1,12),("Maraîchage",12,4),("Arachide",6,11)],
        'Sokone':       [("Arachide",7,11),("Riz pluvial",7,12),("Mil",7,10),("Pêche",1,12),("Maraîchage",12,4)],
        'Kaolack':      [("Arachide",7,11),("Mil",7,10),("Sorgho",7,11),("Niébé",8,10),("Maïs",7,10),("Maraîchage",11,4)],
        'Kaffrine':     [("Arachide",7,11),("Mil",7,10),("Niébé",8,10),("Sorgho",7,11),("Maïs",7,10)],
        'Nioro du Rip': [("Arachide",7,11),("Coton",6,11),("Mil",7,10),("Niébé",8,10),("Maïs",7,10),("Sorgho",7,11)],
        'Kolda':        [("Arachide",5,11),("Mil",5,11),("Coton",5,11),("Maïs",5,10),("Riz pluvial",6,11),("Manioc",1,12),("Palmier huile",1,12),("Mangue",3,7),("Anacarde",2,5),("Niébé",6,10)],
        'Vélingara':    [("Arachide",5,11),("Mil",5,11),("Riz bas-fond",6,11),("Maïs",5,10),("Manioc",1,12),("Anacarde",2,5),("Niébé",6,10),("Sorgho",6,11)],
        'Médina Yoro Foulah':[("Mil",6,11),("Arachide",6,11),("Sorgho",6,11),("Maïs",6,10),("Manioc",1,12),("Niébé",7,10)],
        'Kédougou':     [("Maïs",4,10),("Mil",4,11),("Igname",4,12),("Riz pluvial",6,11),("Manioc",1,12),("Arachide",5,11),("Sorgho",6,11),("Mangue",3,7),("Anacarde",2,5),("Niébé",6,10),("Patate douce",5,11)],
        'Saraya':       [("Mil",5,11),("Igname",4,12),("Riz pluvial",6,11),("Manioc",1,12),("Maïs",5,10),("Arachide",5,11),("Anacarde",2,5),("Mangue",3,7)],
        'Salékata':     [("Mil",5,11),("Igname",4,12),("Manioc",1,12),("Maïs",5,10),("Arachide",5,11),("Mangue",3,7)],
        'Louga':        [("Arachide",7,10),("Mil souna",7,10),("Niébé",8,10),("Sorgho",7,10),("Gomme arabique",1,12)],
        'Linguère':     [("Mil",7,10),("Niébé",8,10),("Élevage",1,12),("Gomme arabique",1,12),("Sorgho",7,10)],
        'Kébémer':      [("Arachide",7,10),("Mil",7,10),("Niébé",8,10),("Sorgho",7,10)],
        'Matam':        [("Riz irrigué S1",2,6),("Riz irrigué S2",8,12),("Sorgho",7,11),("Maraîchage",11,4),("Mil",7,10),("Niébé",8,10),("Tomate",11,4),("Oignon",11,5)],
        'Kanel':        [("Riz irrigué",7,11),("Mil",7,10),("Sorgho",7,11),("Décrue",10,12),("Maraîchage",11,4),("Niébé",8,10)],
        'Ranérou':      [("Mil",7,10),("Élevage",1,12),("Niébé",8,10),("Gomme arabique",1,12),("Sorgho",7,10)],
        'Saint-Louis':  [("Riz irrigué S1",2,6),("Riz irrigué S2",8,12),("Tomate",11,4),("Oignon",11,5),("Mil",7,10),("Maraîchage",11,4),("Pêche",1,12)],
        'Podor':        [("Mil",7,10),("Riz irrigué",7,11),("Décrue",10,12),("Sorgho",7,11),("Maraîchage",11,4),("Niébé",8,10)],
        'Dagana':       [("Riz irrigué S1",2,6),("Riz irrigué S2",8,12),("Tomate",11,4),("Oignon",11,5),("Maraîchage",11,4)],
        'Richard-Toll': [("Canne à sucre",1,12),("Riz irrigué S1",2,6),("Riz irrigué S2",8,12),("Tomate",11,4),("Maraîchage",11,4)],
        'Sédhiou':      [("Arachide",5,11),("Riz pluvial",5,11),("Riz mangrove",6,12),("Anacarde",2,5),("Palmier huile",1,12),("Manioc",1,12),("Maïs",5,10),("Mangue",3,7),("Niébé",6,10),("Maraîchage",12,4)],
        'Goudomp':      [("Arachide",5,11),("Mil",5,11),("Riz bas-fond",6,12),("Anacarde",2,5),("Palmier huile",1,12),("Manioc",1,12),("Maïs",5,10),("Mangue",3,7),("Niébé",6,10)],
        'Bounkiling':   [("Riz pluvial",5,12),("Anacarde",2,5),("Arachide",5,11),("Palmier huile",1,12),("Manioc",1,12),("Maïs",5,10),("Mangue",3,7),("Niébé",6,10)],
        'Tambacounda':  [("Mil",6,11),("Arachide",6,11),("Sorgho",6,11),("Élevage",1,12),("Maïs",6,10),("Niébé",7,10),("Sésame",6,10),("Manioc",1,12),("Gomme arabique",1,12)],
        'Bakel':        [("Mil",7,10),("Riz décrue",10,12),("Élevage",1,12),("Sorgho",7,10),("Niébé",8,10),("Gomme arabique",1,12),("Maraîchage",11,4)],
        'Goudiry':      [("Sorgho",6,11),("Mil",6,11),("Niébé",7,10),("Arachide",6,11),("Maïs",6,10),("Élevage",1,12),("Sésame",6,10)],
        'Koumpentoum':  [("Arachide",6,11),("Mil",6,11),("Niébé",7,10),("Sorgho",6,11),("Maïs",6,10),("Manioc",1,12)],
        'Thiès':        [("Arachide",7,11),("Tomate",11,4),("Maraîchage",10,5),("Mil",7,10),("Niébé",8,10),("Oignon",11,4),("Piment",11,4)],
        'Mbour':        [("Tomate",11,4),("Maraîchage",10,5),("Pêche",1,12),("Oignon",11,4),("Chou",11,3),("Piment",11,4),("Niébé",8,10)],
        'Tivaouane':    [("Arachide",7,11),("Niébé",8,10),("Mil",7,10),("Maraîchage",11,4)],
        'Mékhe':        [("Maïs",7,10),("Mil",7,10),("Arachide",7,11),("Niébé",8,10),("Sorgho",7,11)],
        'Khombole':     [("Arachide",7,11),("Niébé",8,10),("Mil",7,10),("Sorgho",7,11)],
        'Ziguinchor':   [("Riz pluvial",5,11),("Riz mangrove",6,12),("Anacarde",2,5),("Arachide",5,11),("Maïs",5,10),("Palmier huile",1,12),("Manioc",1,12),("Mangue",3,7),("Maraîchage",12,4),("Pêche",1,12),("Banane",1,12),("Agrumes",1,12)],
        'Bignona':      [("Riz pluvial",5,11),("Riz mangrove",6,12),("Anacarde",2,5),("Arachide",5,11),("Palmier huile",1,12),("Manioc",1,12),("Mangue",3,7),("Maïs",5,10),("Niébé",6,10),("Banane",1,12)],
        'Oussouye':     [("Riz mangrove",5,12),("Riz pluvial",5,11),("Pêche",1,12),("Palmier huile",1,12),("Manioc",1,12),("Mangue",3,7),("Anacarde",2,5),("Banane",1,12),("Agrumes",1,12)],
    }

    cultures = GANTT.get(commune, [("Mil",7,10),("Arachide",7,11)])
    
    COULEURS = ["#2ECC71","#3498DB","#E74C3C","#F39C12","#9B59B6","#1ABC9C","#E67E22","#16A085"]
    
    # Construction tableau
    rows = []
    for i, (culture, debut, fin) in enumerate(cultures):
        row = {"🌿 Culture": culture}
        for m_idx, mois in enumerate(MOIS, 1):
            if debut <= fin:
                actif = debut <= m_idx <= fin
            else:  # cycle qui chevauche fin d'année
                actif = m_idx >= debut or m_idx <= fin
            row[mois] = "✅" if actif else ""
        rows.append(row)
    
    df_gantt = pd.DataFrame(rows)
    
    # Affichage avec couleurs
    import streamlit as st
    
    st.markdown("#### 📅 Calendrier Cultural — " + commune)
    st.caption("✅ = période active pour cette culture")
    
    # Style conditionnel
    def colorize(val):
        if val == "✅":
            return "background-color: #1a5c2a; color: #2ECC71; text-align: center; font-size: 16px;"
        return "text-align: center; color: #555;"
    
    styled = df_gantt.style.applymap(colorize, subset=MOIS)
    st.dataframe(styled, use_container_width=True, hide_index=True)

LAYOUT = dict(paper_bgcolor="#0a0f1e", plot_bgcolor="#0d1527", font_color="#e8f4fd", margin=dict(t=40,b=20,l=10,r=10))

with st.sidebar:
    st.markdown("## 🌍 Navigation")
    page = st.radio("", [
        "📊 Aperçu",
        "🌡️ Température",
        "🌧️ Précipitations",
        "🏜️ Sécheresse",
        "🌱 Sols & Calendrier Cultural",
        "🗺️ Carte Interactive",
        "⚠️ Alertes & Conseils",
        "📉 Comparaison Scénarios",
        "💾 Export",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### ⚙️ Paramètres")
    communes_df = get_communes()
    commune_list = communes_df["commune_name"].tolist()
    selected_commune = st.selectbox("🏘️ Commune", commune_list)
    scenarios = get_scenarios() or ["SSP1-1.9","SSP2-4.5","SSP5-8.5"]
    selected_scenario = st.selectbox("🌡️ Scénario", scenarios)
    st.markdown("---")
    st.success("🟢 Base connectée")
    nb = pd.read_sql("SELECT COUNT(*) as n FROM commune_climate_data", get_conn()).iloc[0]["n"]
    st.caption(f"📦 {nb:,} enregistrements · 46 communes")

def get_info(commune):
    row = communes_df[communes_df["commune_name"]==commune]
    region  = row["region"].values[0] if not row.empty else "N/A"
    sol     = SOLS.get(commune, "Sol ferrugineux tropical")
    cal     = CALENDRIER.get(commune, {})
    conseil = generer_conseil_detaille(commune, region, sol, cal, selected_scenario)
    return region, sol, cal, conseil

colors_sc = {"SSP1-1.9":"#44ff88","SSP2-4.5":"#ffd700","SSP5-8.5":"#ff4444"}

if page == "📊 Aperçu":
    region, sol, cal, conseil = get_info(selected_commune)
    st.markdown(f"# 🌍 Système d'Alerte Climatique — Sénégal 2025–2055")
    st.caption(f"Commune : **{selected_commune}** · Région : **{region}** · Scénario : **{selected_scenario}**")
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown('<div class="metric-card"><div class="metric-value">46</div><div class="metric-label">Communes</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><div class="metric-value">2025–2055</div><div class="metric-label">30 ans</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label">Scénarios CMIP6</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="metric-value">{nb//1000}K+</div><div class="metric-label">Enregistrements</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        c1,c2 = st.columns(2)
        with c1:
            fig = px.line(df,x="year",y="temp_mean",title="🌡️ Température moyenne (°C)",color_discrete_sequence=["#ff6b6b"],template="plotly_dark")
            fig.update_layout(**LAYOUT); st.plotly_chart(fig,use_container_width=True)
        with c2:
            fig2 = px.bar(df,x="year",y="precip_total",title="🌧️ Précipitations (mm/an)",color_discrete_sequence=["#4db8ff"],template="plotly_dark")
            fig2.update_layout(**LAYOUT); st.plotly_chart(fig2,use_container_width=True)
    if cal:
        st.info(f"💧 **Début des pluies :** {cal.get('debut_pluies','N/A')} · **Hivernage :** {cal.get('hivernage','N/A')} · **Cultures :** {cal.get('cultures','N/A')}")
    st.markdown(f'<div class="info-card">💡 <b>Conseil :</b> {conseil}</div>', unsafe_allow_html=True)

elif page == "🌡️ Température":
    st.markdown(f"# 🌡️ Température — {selected_commune}")
    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"],y=df["temp_max"],name="T° max",line=dict(color="#ff4444",width=2)))
        fig.add_trace(go.Scatter(x=df["year"],y=df["temp_mean"],name="T° moy",line=dict(color="#ffd700",width=2)))
        fig.add_trace(go.Scatter(x=df["year"],y=df["temp_min"],name="T° min",line=dict(color="#4db8ff",width=2)))
        fig.add_hline(y=38,line_dash="dash",line_color="red",annotation_text="Seuil stress 38°C")
        fig.update_layout(title=f"Températures 2025–2055 · {selected_commune}",template="plotly_dark",**LAYOUT)
        st.plotly_chart(fig,use_container_width=True)
        c1,c2,c3 = st.columns(3)
        c1.metric("T° min projetée",f"{df['temp_min'].min():.1f}°C")
        c2.metric("T° moy 2055",f"{df['temp_mean'].iloc[-1]:.1f}°C",f"+{df['temp_mean'].iloc[-1]-df['temp_mean'].iloc[0]:.1f}°C")
        c3.metric("T° max projetée",f"{df['temp_max'].max():.1f}°C")
        df["jours_chauds"] = ((df["temp_max"]-38)*8).clip(lower=0).round().astype(int)
        fig2 = px.bar(df,x="year",y="jours_chauds",title="🔥 Jours T°>38°C estimés/an",color="jours_chauds",color_continuous_scale=["#ffd700","#ff4444"],template="plotly_dark")
        fig2.update_layout(**LAYOUT); st.plotly_chart(fig2,use_container_width=True)

elif page == "🌧️ Précipitations":
    region, sol, cal, conseil = get_info(selected_commune)
    st.markdown(f"# 🌧️ Précipitations — {selected_commune}")
    if cal: st.info(f"📅 **Début des pluies :** {cal.get('debut_pluies','N/A')} · **Hivernage :** {cal.get('hivernage','N/A')}")
    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        fig = px.bar(df,x="year",y="precip_total",title=f"Précipitations annuelles (mm) · {selected_commune}",color="precip_total",color_continuous_scale=["#ff4444","#ffd700","#4db8ff"],template="plotly_dark")
        fig.update_layout(**LAYOUT); st.plotly_chart(fig,use_container_width=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Précip. 2025",f"{df['precip_total'].iloc[0]:.0f} mm")
        c2.metric("Moy. 30 ans",f"{df['precip_total'].mean():.0f} mm")
        c3.metric("Précip. 2055",f"{df['precip_total'].iloc[-1]:.0f} mm")
        tendance = df['precip_total'].iloc[-1]-df['precip_total'].iloc[0]
        c4.metric("Tendance",f"{tendance:.0f} mm",delta_color="inverse")
        st.markdown("### 📊 Comparaison tous scénarios")
        fig2 = go.Figure()
        for sc in scenarios:
            dsc = get_annual(selected_commune,sc)
            if not dsc.empty:
                fig2.add_trace(go.Scatter(x=dsc["year"],y=dsc["precip_total"],name=sc,line=dict(color=colors_sc.get(sc,"#fff"),width=2)))
        fig2.update_layout(title="Précipitations par scénario",template="plotly_dark",**LAYOUT)
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown("### 📋 Début des pluies — toutes communes")
        cal_rows = [{"Commune":c,"Début des pluies":v.get("debut_pluies","N/A"),"Hivernage":v.get("hivernage","N/A"),"Cultures":v.get("cultures","N/A")} for c,v in CALENDRIER.items()]
        st.dataframe(pd.DataFrame(cal_rows),use_container_width=True,height=400)
    st.markdown('---')
    afficher_calendrier_gantt(selected_commune)

elif page == "🏜️ Sécheresse":
    st.markdown(f"# 🏜️ Sécheresse — {selected_commune}")
    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        fig = px.line(df,x="year",y="drought",title="Indice de sécheresse (0=normal · 1=sévère)",color_discrete_sequence=["#ffd700"],template="plotly_dark")
        fig.add_hline(y=0.3,line_dash="dot",line_color="orange",annotation_text="Modéré")
        fig.add_hline(y=0.6,line_dash="dash",line_color="red",annotation_text="Critique")
        fig.update_layout(**LAYOUT); st.plotly_chart(fig,use_container_width=True)
        if df["spi"].notna().any():
            fig2 = px.bar(df,x="year",y="spi",title="Indice SPI (négatif = déficit)",color="spi",color_continuous_scale=["#ff4444","#ffffff","#4db8ff"],template="plotly_dark")
            fig2.update_layout(**LAYOUT); st.plotly_chart(fig2,use_container_width=True)
        annees = df[df["drought"]>0.6]["year"].tolist()
        if annees: st.error(f"⚠️ Années sécheresse sévère projetées : {', '.join(map(str,annees))}")

elif page == "🌱 Sols & Calendrier Cultural":
    region, sol, cal, conseil = get_info(selected_commune)
    st.markdown(f"# 🌱 Sols & Calendrier — {selected_commune}")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### 🪨 Type de sol")
        st.markdown(f'<div class="info-card">🌍 <b>{selected_commune}</b> ({region})<br><br>{sol}</div>',unsafe_allow_html=True)
        st.markdown("### 💡 Conseils agricoles")
        st.markdown(f'<div class="info-card">🌾 {conseil}</div>',unsafe_allow_html=True)
    with c2:
        st.markdown("### 📅 Calendrier Cultural")
        if cal:
            st.markdown(f"""<div class="info-card">
🌧️ <b>Hivernage :</b> {cal.get('hivernage','N/A')}<br>
💧 <b>Début des pluies :</b> {cal.get('debut_pluies','N/A')}<br>
🌱 <b>Semis :</b> {cal.get('semis','N/A')}<br>
🌾 <b>Récolte :</b> {cal.get('recolte','N/A')}<br>
🌿 <b>Cultures :</b> {cal.get('cultures','N/A')}
</div>""",unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('---')
    afficher_calendrier_gantt(selected_commune)
    st.markdown("### 🪨 Type de sol — " + selected_commune)
    st.markdown(f'<div class="info-card">🌍 <b>{selected_commune}</b> ({region})<br><br>{sol}</div>', unsafe_allow_html=True)

elif page == "🗺️ Carte Interactive":
    st.markdown("# 🗺️ Carte Interactive")
    c1,c2 = st.columns(2)
    with c1: year = st.slider("Année",2025,2055,2030)
    with c2: variable = st.selectbox("Variable",["temp_mean","temp_max","precip_total","drought","heat_stress"],format_func=lambda x:{"temp_mean":"🌡️ T° moyenne","temp_max":"🔥 T° max","precip_total":"🌧️ Précipitations","drought":"🏜️ Sécheresse","heat_stress":"⚡ Stress thermique"}[x])
    df_map = get_all_map(selected_scenario, year)
    if not df_map.empty:
        cscales = {"temp_mean":"Reds","temp_max":"hot","precip_total":"Blues","drought":"YlOrRd","heat_stress":"Oranges"}
        labels  = {"temp_mean":"T° moy (°C)","temp_max":"T° max (°C)","precip_total":"Précip (mm)","drought":"Sécheresse","heat_stress":"Stress"}
        fig = px.scatter_mapbox(df_map,lat="latitude",lon="longitude",hover_name="commune_name",hover_data={"region":True,variable:True,"latitude":False,"longitude":False},color=variable,color_continuous_scale=cscales[variable],size_max=18,zoom=5.5,center={"lat":14.5,"lon":-14.5},mapbox_style="open-street-map",title=f"{labels[variable]} · {year} · {selected_scenario}")
        fig.update_layout(height=600,margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig,use_container_width=True)

elif page == "⚠️ Alertes & Conseils":
    region, sol, cal, conseil = get_info(selected_commune)
    st.markdown(f"# ⚠️ Alertes & Conseils — {selected_commune}")
    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        last = df.iloc[-1]
        temp_max = last.get("temp_max",0) or 0
        precip   = last.get("precip_total",0) or 0
        drought  = last.get("drought",0) or 0
        score = 0
        if temp_max>=42: score+=3
        elif temp_max>=38: score+=2
        elif temp_max>=35: score+=1
        if drought>=0.7: score+=3
        elif drought>=0.5: score+=2
        elif drought>=0.3: score+=1
        if precip<200: score+=2
        elif precip<400: score+=1
        if score>=6: st.markdown('<div class="alert-critical">🔴 <b>CRITIQUE</b> — Risques extrêmes à horizon 2055</div>',unsafe_allow_html=True)
        elif score>=4: st.markdown('<div class="alert-high">🟠 <b>ÉLEVÉ</b> — Adaptation urgente</div>',unsafe_allow_html=True)
        elif score>=2: st.markdown('<div class="alert-medium">🟡 <b>MODÉRÉ</b> — Surveillance recommandée</div>',unsafe_allow_html=True)
        else: st.markdown('<div class="alert-low">🟢 <b>FAIBLE</b> — Conditions stables</div>',unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        c1.metric("T° max 2055",f"{temp_max:.1f}°C")
        c2.metric("Précip. 2055",f"{precip:.0f} mm")
        c3.metric("Sécheresse",f"{drought:.2f}")
        st.markdown("---")
        st.markdown("### 🌾 Conseils agricoles")
        st.markdown(conseil)
        st.markdown("### 📅 Calendrier cultural")
        if cal:
            st.markdown(f"- 💧 **Début des pluies :** {cal.get('debut_pluies','N/A')}\n- 🌱 **Semis :** {cal.get('semis','N/A')}\n- 🌾 **Récolte :** {cal.get('recolte','N/A')}\n- 🌿 **Cultures :** {cal.get('cultures','N/A')}")
        st.markdown("### 🪨 Sol")
        st.markdown(f"**Type :** {sol}")
        st.markdown("### 📊 Années à risque")
        df_risk = df[df["drought"]>0.4][["year","temp_max","precip_total","drought"]].copy()
        df_risk.columns = ["Année","T° max","Précip (mm)","Sécheresse"]
        if not df_risk.empty: st.dataframe(df_risk.round(2),use_container_width=True)
        else: st.success("Aucune année à risque élevé pour ce scénario.")

elif page == "📉 Comparaison Scénarios":
    st.markdown(f"# 📉 Comparaison Scénarios — {selected_commune}")
    variable = st.selectbox("Variable",["temp_mean","temp_max","precip_total","drought","heat_stress"],format_func=lambda x:{"temp_mean":"T° moyenne","temp_max":"T° max","precip_total":"Précipitations","drought":"Sécheresse","heat_stress":"Stress thermique"}[x])
    fig = go.Figure()
    summary = []
    for sc in scenarios:
        df = get_annual(selected_commune,sc)
        if not df.empty and variable in df.columns:
            fig.add_trace(go.Scatter(x=df["year"],y=df[variable],name=sc,line=dict(color=colors_sc.get(sc,"#fff"),width=2)))
            v2040 = df[df["year"]==2040][variable].values
            summary.append({"Scénario":sc,"2025":round(df[variable].iloc[0],2),"2040":round(v2040[0],2) if len(v2040) else "N/A","2055":round(df[variable].iloc[-1],2),"Variation":round(df[variable].iloc[-1]-df[variable].iloc[0],2)})
    fig.update_layout(title=f"Comparaison · {selected_commune}",template="plotly_dark",**LAYOUT,legend=dict(bgcolor="#0d1527",bordercolor="#2a4a7f"))
    st.plotly_chart(fig,use_container_width=True)
    if summary: st.dataframe(pd.DataFrame(summary),use_container_width=True)

elif page == "💾 Export":
    st.markdown(f"# 💾 Export — {selected_commune}")
    c1,c2,c3 = st.columns(3)
    with c1: exp_scenario = st.selectbox("Scénario",scenarios)
    with c2: year_start   = st.number_input("Année début",2025,2054,2025)
    with c3: year_end     = st.number_input("Année fin",2026,2055,2055)
    fmt = st.radio("Format",["CSV","JSON"],horizontal=True)
    if st.button("📥 Générer",type="primary"):
        try:
            df_exp = pd.read_sql("""
                SELECT year as Annee, temp_annual_mean as T_moy_C, temp_annual_max as T_max_C,
                       temp_annual_min as T_min_C, precip_annual_total as Precip_mm,
                       humidity_annual_mean as Humidite_pct, drought_index as Secheresse,
                       spi_index as SPI, heat_stress as Stress_thermique, risk_level as Risque, scenario as Scenario
                FROM commune_climate_data
                WHERE commune_name=? AND scenario=? AND resolution='annual' AND year>=? AND year<=?
                ORDER BY year
            """, get_conn(), params=[selected_commune, exp_scenario, int(year_start), int(year_end)])
            if not df_exp.empty:
                st.success(f"✅ {len(df_exp)} années exportées")
                st.dataframe(df_exp,use_container_width=True)
                if fmt=="CSV":
                    data  = df_exp.to_csv(index=False).encode("utf-8")
                    mime  = "text/csv"
                    fname = f"{selected_commune}_{exp_scenario}_{int(year_start)}_{int(year_end)}.csv"
                else:
                    data  = df_exp.to_json(orient="records",indent=2).encode("utf-8")
                    mime  = "application/json"
                    fname = f"{selected_commune}_{exp_scenario}_{int(year_start)}_{int(year_end)}.json"
                st.download_button("⬇️ Télécharger",data,fname,mime)
            else:
                st.warning("Aucune donnée trouvée.")
        except Exception as e:
            st.error(f"Erreur : {e}")


