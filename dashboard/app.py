"""
Senegal Climate Alert — Dashboard Complet 9 pages
46 communes - Sols - Calendrier - Précipitations - Conseils - Export
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
    'Dakar':'Sol sableux (Deck-Dior) - faible rétention hydrique',
    'Pikine':'Sol sableux dégradé - urbanisation intense',
    'Guediawaye':'Sol sableux - nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical - bon drainage',
    'Bargny':'Sol salin - mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) - arachide',
    'Bambey':'Sol Dior sableux - très cultivé',
    'Mbacké':'Sol Dior et Deck - polyculture',
    'Fatick':'Sol sulfaté acide - tannes - mangrove',
    'Gossas':'Sol ferrugineux - mil dominant',
    'Foundiougne':'Sol alluvial - riziculture de mangrove',
    'Sokone':'Sol hydromorphe - sel',
    'Kaolack':'Sol argileux (Deck) - bassin arachidier',
    'Kaffrine':'Sol Dior et Deck - transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé - coton',
    'Kolda':'Sol ferralitique - forêt dégradée',
    'Vélingara':'Sol ferrugineux - savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique - cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge - or et cultures',
    'Saraya':'Sol latéritique - or alluvionnaire',
    'Salékata':'Sol ferralitique - igname et mil',
    'Louga':'Sol Dior sableux - déficit pluviométrique',
    'Linguère':'Sol sableux sahélien - élevage',
    'Kébémer':'Sol Dior - arachide et mil',
    'Matam':'Sol alluvial (Walo) - riz irrigué',
    'Kanel':'Sol alluvial - décrue et irrigation',
    'Ranérou':'Sol sableux sahélien - élevage extensif',
    'Saint-Louis':'Sol alluvial delta - riz irrigué',
    'Podor':'Sol Walo - culture de décrue',
    'Dagana':'Sol argileux lourd - riziculture irriguée',
    'Richard-Toll':'Sol argileux - canne à sucre',
    'Sédhiou':'Sol ferralitique - anacarde',
    'Goudomp':'Sol hydromorphe - riziculture',
    'Bounkiling':'Sol ferralitique - anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical - savane',
    'Bakel':'Sol sableux sahélien - mil et riz de décrue',
    'Goudiry':'Sol ferrugineux - sorgho',
    'Koumpentoum':'Sol ferrugineux - arachide',
    'Thiès':'Sol ferrugineux rouge - phosphate',
    'Mbour':'Sol sableux côtier - maraîchage',
    'Tivaouane':'Sol Dior - arachide',
    'Mékhe':'Sol ferrugineux - maïs',
    'Khombole':'Sol Dior - arachide',
    'Ziguinchor':'Sol ferralitique - riz et anacarde',
    'Bignona':'Sol ferralitique - anacarde',
    'Oussouye':'Sol hydromorphe - riziculture de mangrove',
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
    'Dakar':'Sol sableux (Deck-Dior) - faible rétention hydrique',
    'Pikine':'Sol sableux dégradé - urbanisation intense',
    'Guediawaye':'Sol sableux - nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical - bon drainage',
    'Bargny':'Sol salin - mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) - arachide',
    'Bambey':'Sol Dior sableux - très cultivé',
    'Mbacké':'Sol Dior et Deck - polyculture',
    'Fatick':'Sol sulfaté acide - tannes - mangrove',
    'Gossas':'Sol ferrugineux - mil dominant',
    'Foundiougne':'Sol alluvial - riziculture de mangrove',
    'Sokone':'Sol hydromorphe - sel',
    'Kaolack':'Sol argileux (Deck) - bassin arachidier',
    'Kaffrine':'Sol Dior et Deck - transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé - coton',
    'Kolda':'Sol ferralitique - forêt dégradée',
    'Vélingara':'Sol ferrugineux - savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique - cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge - or et cultures',
    'Saraya':'Sol latéritique - or alluvionnaire',
    'Salékata':'Sol ferralitique - igname et mil',
    'Louga':'Sol Dior sableux - déficit pluviométrique',
    'Linguère':'Sol sableux sahélien - élevage',
    'Kébémer':'Sol Dior - arachide et mil',
    'Matam':'Sol alluvial (Walo) - riz irrigué',
    'Kanel':'Sol alluvial - décrue et irrigation',
    'Ranérou':'Sol sableux sahélien - élevage extensif',
    'Saint-Louis':'Sol alluvial delta - riz irrigué',
    'Podor':'Sol Walo - culture de décrue',
    'Dagana':'Sol argileux lourd - riziculture irriguée',
    'Richard-Toll':'Sol argileux - canne à sucre',
    'Sédhiou':'Sol ferralitique - anacarde',
    'Goudomp':'Sol hydromorphe - riziculture',
    'Bounkiling':'Sol ferralitique - anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical - savane',
    'Bakel':'Sol sableux sahélien - mil et riz de décrue',
    'Goudiry':'Sol ferrugineux - sorgho',
    'Koumpentoum':'Sol ferrugineux - arachide',
    'Thiès':'Sol ferrugineux rouge - phosphate',
    'Mbour':'Sol sableux côtier - maraîchage',
    'Tivaouane':'Sol Dior - arachide',
    'Mékhe':'Sol ferrugineux - maïs',
    'Khombole':'Sol Dior - arachide',
    'Ziguinchor':'Sol ferralitique - riz et anacarde',
    'Bignona':'Sol ferralitique - anacarde',
    'Oussouye':'Sol hydromorphe - riziculture de mangrove',
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

### ⚠️ Causes et risques climatiques projetés (2025–2055 - scénario {scenario})

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
    'Dakar':'Sol sableux (Deck-Dior) - faible rétention hydrique',
    'Pikine':'Sol sableux dégradé - urbanisation intense',
    'Guediawaye':'Sol sableux - nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical - bon drainage',
    'Bargny':'Sol salin - mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) - arachide',
    'Bambey':'Sol Dior sableux - très cultivé',
    'Mbacké':'Sol Dior et Deck - polyculture',
    'Fatick':'Sol sulfaté acide - tannes - mangrove',
    'Gossas':'Sol ferrugineux - mil dominant',
    'Foundiougne':'Sol alluvial - riziculture de mangrove',
    'Sokone':'Sol hydromorphe - sel',
    'Kaolack':'Sol argileux (Deck) - bassin arachidier',
    'Kaffrine':'Sol Dior et Deck - transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé - coton',
    'Kolda':'Sol ferralitique - forêt dégradée',
    'Vélingara':'Sol ferrugineux - savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique - cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge - or et cultures',
    'Saraya':'Sol latéritique - or alluvionnaire',
    'Salékata':'Sol ferralitique - igname et mil',
    'Louga':'Sol Dior sableux - déficit pluviométrique',
    'Linguère':'Sol sableux sahélien - élevage',
    'Kébémer':'Sol Dior - arachide et mil',
    'Matam':'Sol alluvial (Walo) - riz irrigué',
    'Kanel':'Sol alluvial - décrue et irrigation',
    'Ranérou':'Sol sableux sahélien - élevage extensif',
    'Saint-Louis':'Sol alluvial delta - riz irrigué',
    'Podor':'Sol Walo - culture de décrue',
    'Dagana':'Sol argileux lourd - riziculture irriguée',
    'Richard-Toll':'Sol argileux - canne à sucre',
    'Sédhiou':'Sol ferralitique - anacarde',
    'Goudomp':'Sol hydromorphe - riziculture',
    'Bounkiling':'Sol ferralitique - anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical - savane',
    'Bakel':'Sol sableux sahélien - mil et riz de décrue',
    'Goudiry':'Sol ferrugineux - sorgho',
    'Koumpentoum':'Sol ferrugineux - arachide',
    'Thiès':'Sol ferrugineux rouge - phosphate',
    'Mbour':'Sol sableux côtier - maraîchage',
    'Tivaouane':'Sol Dior - arachide',
    'Mékhe':'Sol ferrugineux - maïs',
    'Khombole':'Sol Dior - arachide',
    'Ziguinchor':'Sol ferralitique - riz et anacarde',
    'Bignona':'Sol ferralitique - anacarde',
    'Oussouye':'Sol hydromorphe - riziculture de mangrove',
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
    'Dakar':'Sol sableux (Deck-Dior) - faible rétention hydrique',
    'Pikine':'Sol sableux dégradé - urbanisation intense',
    'Guediawaye':'Sol sableux - nappe phréatique affleurante',
    'Rufisque':'Sol ferrugineux tropical - bon drainage',
    'Bargny':'Sol salin - mangrove dégradée',
    'Diourbel':'Sol ferrugineux (Dior) - arachide',
    'Bambey':'Sol Dior sableux - très cultivé',
    'Mbacké':'Sol Dior et Deck - polyculture',
    'Fatick':'Sol sulfaté acide - tannes - mangrove',
    'Gossas':'Sol ferrugineux - mil dominant',
    'Foundiougne':'Sol alluvial - riziculture de mangrove',
    'Sokone':'Sol hydromorphe - sel',
    'Kaolack':'Sol argileux (Deck) - bassin arachidier',
    'Kaffrine':'Sol Dior et Deck - transition sahélienne',
    'Nioro du Rip':'Sol ferrugineux lessivé - coton',
    'Kolda':'Sol ferralitique - forêt dégradée',
    'Vélingara':'Sol ferrugineux - savane arbustive',
    'Médina Yoro Foulah':'Sol latéritique - cuirasse ferrugineuse',
    'Kédougou':'Sol ferralitique rouge - or et cultures',
    'Saraya':'Sol latéritique - or alluvionnaire',
    'Salékata':'Sol ferralitique - igname et mil',
    'Louga':'Sol Dior sableux - déficit pluviométrique',
    'Linguère':'Sol sableux sahélien - élevage',
    'Kébémer':'Sol Dior - arachide et mil',
    'Matam':'Sol alluvial (Walo) - riz irrigué',
    'Kanel':'Sol alluvial - décrue et irrigation',
    'Ranérou':'Sol sableux sahélien - élevage extensif',
    'Saint-Louis':'Sol alluvial delta - riz irrigué',
    'Podor':'Sol Walo - culture de décrue',
    'Dagana':'Sol argileux lourd - riziculture irriguée',
    'Richard-Toll':'Sol argileux - canne à sucre',
    'Sédhiou':'Sol ferralitique - anacarde',
    'Goudomp':'Sol hydromorphe - riziculture',
    'Bounkiling':'Sol ferralitique - anacarde et riz',
    'Tambacounda':'Sol ferrugineux tropical - savane',
    'Bakel':'Sol sableux sahélien - mil et riz de décrue',
    'Goudiry':'Sol ferrugineux - sorgho',
    'Koumpentoum':'Sol ferrugineux - arachide',
    'Thiès':'Sol ferrugineux rouge - phosphate',
    'Mbour':'Sol sableux côtier - maraîchage',
    'Tivaouane':'Sol Dior - arachide',
    'Mékhe':'Sol ferrugineux - maïs',
    'Khombole':'Sol Dior - arachide',
    'Ziguinchor':'Sol ferralitique - riz et anacarde',
    'Bignona':'Sol ferralitique - anacarde',
    'Oussouye':'Sol hydromorphe - riziculture de mangrove',
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


HYDRAULIQUE = {
    "Dakar":{"nappe":"Nappe sables quaternaires 5-15m saumâtre","eau_types":["Mer Atlantique","Eau souterraine","Eau ville SDE"],"fleuves":"Aucun fleuve - presquîle","lacs":"Lac Rose salé - Baie de Hann","mares":"Mares temporaires hivernage","forages":45,"puits":120,"perimetre_irrigue_ha":150,"acces_eau":"Très bon","risque_penurie":"Modéré","lat":14.6928,"lon":-17.0407},
    "Pikine":{"nappe":"Nappe affleurante 2-8m risque salinisation","eau_types":["Eau souterraine","Eau ville","Mer proche"],"fleuves":"Aucun","lacs":"Lac Mbeubeuss zones humides","mares":"Nombreuses inondations","forages":28,"puits":85,"perimetre_irrigue_ha":80,"acces_eau":"Bon","risque_penurie":"Modéré","lat":14.7667,"lon":-17.1500},
    "Guediawaye":{"nappe":"Nappe sableuse 3-10m qualité variable","eau_types":["Eau souterraine","Eau ville"],"fleuves":"Aucun","lacs":"Zones humides côtières","mares":"Mares temporaires","forages":18,"puits":60,"perimetre_irrigue_ha":40,"acces_eau":"Bon","risque_penurie":"Faible","lat":14.7550,"lon":-17.2850},
    "Rufisque":{"nappe":"Nappe Maestrichtien 80-200m bonne qualité","eau_types":["Eau souterraine profonde","Mer Atlantique","Eau ville"],"fleuves":"Aucun direct","lacs":"Baie de Rufisque","mares":"Mares saisonnières","forages":22,"puits":75,"perimetre_irrigue_ha":120,"acces_eau":"Bon","risque_penurie":"Faible","lat":14.7167,"lon":-17.2667},
    "Bargny":{"nappe":"Nappe côtière saline 10-25m eau douce rare","eau_types":["Mer Atlantique","Eau souterraine saline","Eau ville"],"fleuves":"Aucun","lacs":"Mangrove dégradée zones salées","mares":"Mares salées","forages":8,"puits":30,"perimetre_irrigue_ha":20,"acces_eau":"Difficile","risque_penurie":"Élevé","lat":14.6942,"lon":-17.2311},
    "Diourbel":{"nappe":"Nappe Paléocène 30-80m bonne qualité","eau_types":["Eau souterraine","Eau ville","Eau pluie collectée"],"fleuves":"Aucun permanent","lacs":"Aucun","mares":"Mares temporaires élevage","forages":35,"puits":180,"perimetre_irrigue_ha":200,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.6500,"lon":-16.2333},
    "Bambey":{"nappe":"Continental terminal 40-90m","eau_types":["Eau souterraine","Eau pluie"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares villageoises","forages":25,"puits":150,"perimetre_irrigue_ha":180,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.7000,"lon":-16.4500},
    "Mbacké":{"nappe":"Nappe Maestrichtien 60-120m bonne qualité","eau_types":["Eau souterraine profonde","Eau ville","Eau pluie"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares temporaires","forages":30,"puits":160,"perimetre_irrigue_ha":220,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.8000,"lon":-15.9100},
    "Fatick":{"nappe":"Nappe Sénégalo-mauritanien 20-60m légèrement salée","eau_types":["Eau souterraine","Eau salée bras mer","Eau douce saisonnière"],"fleuves":"Bras Sine-Saloum saumâtre","lacs":"Delta Saloum mangroves bolons","mares":"Nombreuses mares et bolons","forages":40,"puits":200,"perimetre_irrigue_ha":350,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.3386,"lon":-16.4114},
    "Gossas":{"nappe":"Continental terminal 50-100m","eau_types":["Eau souterraine","Eau pluie"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares temporaires villageoises","forages":18,"puits":90,"perimetre_irrigue_ha":100,"acces_eau":"Difficile","risque_penurie":"Élevé","lat":14.5000,"lon":-16.0667},
    "Foundiougne":{"nappe":"Nappe alluviale 5-20m qualité variable","eau_types":["Eau saumâtre bras mer","Eau douce saisonnière","Eau souterraine"],"fleuves":"Bras Saloum mangroves","lacs":"Delta Saloum bolons","mares":"Bolons et chenaux permanents","forages":25,"puits":110,"perimetre_irrigue_ha":280,"acces_eau":"Bon","risque_penurie":"Modéré","lat":14.1333,"lon":-16.4667},
    "Sokone":{"nappe":"Nappe côtière salinité variable 10-30m","eau_types":["Eau saumâtre","Eau douce souterraine","Mer Saloum"],"fleuves":"Fleuve Saloum bolons","lacs":"Delta Saloum","mares":"Mares et bolons permanents","forages":20,"puits":80,"perimetre_irrigue_ha":200,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":13.8833,"lon":-16.3667},
    "Kaolack":{"nappe":"Nappe Maestrichtien 40-100m très bonne qualité","eau_types":["Eau souterraine","Fleuve Saloum","Eau ville SDE"],"fleuves":"Fleuve Saloum navigable","lacs":"Bras Saloum lac salé aval","mares":"Mares temporaires","forages":55,"puits":280,"perimetre_irrigue_ha":500,"acces_eau":"Bon","risque_penurie":"Faible","lat":13.9667,"lon":-16.0167},
    "Kaffrine":{"nappe":"Nappe Maestrichtien 60-140m bonne qualité","eau_types":["Eau souterraine profonde","Eau pluie collectée"],"fleuves":"Aucun permanent marigots saisonniers","lacs":"Aucun permanent","mares":"Mares temporaires élevage","forages":42,"puits":220,"perimetre_irrigue_ha":300,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.1056,"lon":-15.5506},
    "Nioro du Rip":{"nappe":"Continental terminal 40-80m","eau_types":["Eau souterraine","Marigots saisonniers","Eau pluie"],"fleuves":"Marigot du Rip saisonnier","lacs":"Aucun permanent","mares":"Mares saisonnières","forages":30,"puits":160,"perimetre_irrigue_ha":250,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":13.7500,"lon":-15.7833},
    "Kolda":{"nappe":"Continental terminal 20-50m excellente qualité","eau_types":["Eau souterraine douce","Fleuve Casamance","Marigots permanents"],"fleuves":"Fleuve Casamance permanent navigable","lacs":"Marigots et bas-fonds permanents","mares":"Nombreuses mares permanentes et temporaires","forages":65,"puits":350,"perimetre_irrigue_ha":800,"acces_eau":"Très bon","risque_penurie":"Faible","lat":12.8908,"lon":-14.9508},
    "Vélingara":{"nappe":"Continental terminal 25-60m bonne qualité","eau_types":["Eau souterraine douce","Marigots permanents","Fleuve Gambie proche"],"fleuves":"Marigot de Vélingara Fleuve Gambie nord","lacs":"Bas-fonds permanents","mares":"Nombreuses mares permanentes","forages":50,"puits":280,"perimetre_irrigue_ha":600,"acces_eau":"Bon","risque_penurie":"Faible","lat":13.1500,"lon":-14.1000},
    "Médina Yoro Foulah":{"nappe":"Nappe latéritique 15-40m qualité moyenne","eau_types":["Eau souterraine","Marigots saisonniers"],"fleuves":"Marigots saisonniers","lacs":"Bas-fonds temporaires","mares":"Mares temporaires","forages":25,"puits":140,"perimetre_irrigue_ha":200,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":13.4000,"lon":-14.2000},
    "Kédougou":{"nappe":"Nappe altérites 10-30m excellente qualité","eau_types":["Eau souterraine douce","Fleuve Gambie","Rivières permanentes","Cascades"],"fleuves":"Fleuve Gambie Fleuve Falémé nombreuses rivières","lacs":"Cascades de Dindéfelo cours eau permanents","mares":"Mares et rivières permanentes","forages":40,"puits":200,"perimetre_irrigue_ha":400,"acces_eau":"Excellent","risque_penurie":"Très faible","lat":12.5569,"lon":-12.1747},
    "Saraya":{"nappe":"Nappe altérites 8-25m très bonne qualité","eau_types":["Eau souterraine douce","Fleuve Falémé","Rivières permanentes"],"fleuves":"Fleuve Falémé permanent or alluvionnaire","lacs":"Cours eau permanents","mares":"Nombreuses mares et rivières","forages":20,"puits":100,"perimetre_irrigue_ha":150,"acces_eau":"Bon","risque_penurie":"Faible","lat":12.8333,"lon":-11.7500},
    "Salékata":{"nappe":"Nappe altérites 10-30m","eau_types":["Eau souterraine douce","Rivières saisonnières"],"fleuves":"Rivières saisonnières","lacs":"Bas-fonds temporaires","mares":"Mares temporaires","forages":12,"puits":60,"perimetre_irrigue_ha":80,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":12.6300,"lon":-12.8200},
    "Louga":{"nappe":"Nappe Maestrichtien 80-200m très bonne mais profonde","eau_types":["Eau souterraine profonde","Eau pluie collectée"],"fleuves":"Aucun permanent","lacs":"Aucun","mares":"Mares temporaires critiques élevage","forages":38,"puits":190,"perimetre_irrigue_ha":150,"acces_eau":"Difficile","risque_penurie":"Élevé","lat":15.6167,"lon":-16.2333},
    "Linguère":{"nappe":"Nappe Maestrichtien 100-250m très profonde","eau_types":["Eau souterraine très profonde","Eau pluie"],"fleuves":"Aucun permanent marigots saisonniers","lacs":"Aucun","mares":"Mares temporaires essentielles pasteurs","forages":25,"puits":120,"perimetre_irrigue_ha":80,"acces_eau":"Très difficile","risque_penurie":"Très élevé","lat":15.3833,"lon":-15.1167},
    "Kébémer":{"nappe":"Nappe Paléocène 40-100m qualité correcte","eau_types":["Eau souterraine","Eau pluie collectée"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares temporaires","forages":22,"puits":110,"perimetre_irrigue_ha":120,"acces_eau":"Moyen","risque_penurie":"Élevé","lat":15.3667,"lon":-16.4500},
    "Matam":{"nappe":"Nappe alluviale fleuve 5-20m bonne qualité","eau_types":["Fleuve Sénégal","Eau souterraine alluviale","Canaux SAED"],"fleuves":"Fleuve Sénégal permanent grand débit","lacs":"Plaine inondation Walo mares décrue","mares":"Mares décrue permanentes walo","forages":48,"puits":250,"perimetre_irrigue_ha":1200,"acces_eau":"Très bon","risque_penurie":"Faible","lat":15.6553,"lon":-13.2553},
    "Kanel":{"nappe":"Nappe alluviale 8-25m bonne qualité","eau_types":["Fleuve Sénégal","Eau alluviale","Canaux irrigation"],"fleuves":"Fleuve Sénégal décrue agricole Doué","lacs":"Plaine Walo inondable","mares":"Mares décrue importantes","forages":30,"puits":160,"perimetre_irrigue_ha":800,"acces_eau":"Bon","risque_penurie":"Faible","lat":15.4900,"lon":-13.1700},
    "Ranérou":{"nappe":"Nappe Maestrichtien 100-200m très profonde","eau_types":["Eau souterraine très profonde","Eau pluie"],"fleuves":"Aucun permanent","lacs":"Aucun","mares":"Mares temporaires critiques élevage pastoral","forages":15,"puits":70,"perimetre_irrigue_ha":50,"acces_eau":"Très difficile","risque_penurie":"Très élevé","lat":15.3000,"lon":-13.9600},
    "Saint-Louis":{"nappe":"Nappe alluviale delta 3-10m salinité variable","eau_types":["Fleuve Sénégal","Mer Atlantique","Eau douce delta","Canaux SAED","Lac de Guiers"],"fleuves":"Fleuve Sénégal delta très grand débit","lacs":"Lac de Guiers Lac Diama plaine inondable","mares":"Nombreuses mares permanentes et temporaires","forages":80,"puits":400,"perimetre_irrigue_ha":5000,"acces_eau":"Excellent","risque_penurie":"Très faible","lat":16.0167,"lon":-16.4833},
    "Podor":{"nappe":"Nappe alluviale Walo 5-15m bonne qualité","eau_types":["Fleuve Sénégal","Eau alluviale","Canaux SAED"],"fleuves":"Fleuve Sénégal Doué défluent","lacs":"Plaine Walo inondable","mares":"Mares décrue importantes","forages":45,"puits":230,"perimetre_irrigue_ha":2500,"acces_eau":"Très bon","risque_penurie":"Faible","lat":16.6500,"lon":-15.2000},
    "Dagana":{"nappe":"Nappe alluviale 3-12m bonne qualité","eau_types":["Fleuve Sénégal","Lac de Guiers","Canaux SAED","Eau douce"],"fleuves":"Fleuve Sénégal Lac de Guiers","lacs":"Lac de Guiers réservoir eau douce majeur","mares":"Lac de Guiers plaine inondable","forages":50,"puits":250,"perimetre_irrigue_ha":3500,"acces_eau":"Excellent","risque_penurie":"Très faible","lat":16.4000,"lon":-15.7667},
    "Richard-Toll":{"nappe":"Nappe alluviale 2-8m bonne qualité","eau_types":["Fleuve Sénégal","Lac de Guiers","Canaux CSS","Eau douce abondante"],"fleuves":"Fleuve Sénégal canal CSS","lacs":"Lac de Guiers adjacent","mares":"Canaux irrigation permanents","forages":35,"puits":120,"perimetre_irrigue_ha":8000,"acces_eau":"Excellent","risque_penurie":"Très faible","lat":16.4628,"lon":-15.7022},
    "Sédhiou":{"nappe":"Continental terminal 15-40m très bonne qualité","eau_types":["Fleuve Casamance","Eau souterraine douce","Marigots permanents"],"fleuves":"Fleuve Casamance permanent navigable","lacs":"Marigots et bras mer permanents","mares":"Nombreuses mares permanentes","forages":55,"puits":300,"perimetre_irrigue_ha":700,"acces_eau":"Très bon","risque_penurie":"Faible","lat":12.7078,"lon":-15.5569},
    "Goudomp":{"nappe":"Continental terminal 10-30m excellente qualité","eau_types":["Fleuve Casamance","Eau souterraine douce","Marigots"],"fleuves":"Fleuve Casamance marigots permanents","lacs":"Bas-fonds permanents mangrove","mares":"Nombreuses mares et marigots","forages":35,"puits":180,"perimetre_irrigue_ha":400,"acces_eau":"Bon","risque_penurie":"Faible","lat":12.5700,"lon":-15.1800},
    "Bounkiling":{"nappe":"Continental terminal 12-35m bonne qualité","eau_types":["Marigots permanents","Eau souterraine douce","Eau pluie"],"fleuves":"Marigots permanents affluents Casamance","lacs":"Bas-fonds permanents","mares":"Mares permanentes","forages":28,"puits":140,"perimetre_irrigue_ha":300,"acces_eau":"Bon","risque_penurie":"Faible","lat":12.9000,"lon":-14.9700},
    "Tambacounda":{"nappe":"Continental terminal 30-80m bonne qualité","eau_types":["Fleuve Gambie","Eau souterraine","Marigots saisonniers"],"fleuves":"Fleuve Gambie nord Fleuve Falémé est","lacs":"Mares permanentes saison sèche","mares":"Mares importantes élevage","forages":60,"puits":320,"perimetre_irrigue_ha":600,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":13.7719,"lon":-13.7731},
    "Bakel":{"nappe":"Nappe alluviale Fleuve Sénégal 5-20m","eau_types":["Fleuve Sénégal","Fleuve Falémé","Eau alluviale"],"fleuves":"Fleuve Sénégal Fleuve Falémé confluent","lacs":"Plaine inondable mares décrue","mares":"Mares décrue importantes","forages":25,"puits":130,"perimetre_irrigue_ha":400,"acces_eau":"Bon","risque_penurie":"Modéré","lat":14.9000,"lon":-12.4667},
    "Goudiry":{"nappe":"Continental terminal 40-90m","eau_types":["Eau souterraine","Marigots saisonniers"],"fleuves":"Marigots saisonniers Falémé est","lacs":"Mares temporaires","mares":"Mares temporaires importantes","forages":30,"puits":160,"perimetre_irrigue_ha":200,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.1833,"lon":-12.7333},
    "Koumpentoum":{"nappe":"Continental terminal 35-80m","eau_types":["Eau souterraine","Marigots saisonniers","Eau pluie"],"fleuves":"Marigots saisonniers","lacs":"Aucun permanent","mares":"Mares temporaires","forages":28,"puits":150,"perimetre_irrigue_ha":250,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":13.9833,"lon":-14.5500},
    "Thiès":{"nappe":"Nappe Paléocène 20-60m bonne qualité","eau_types":["Eau souterraine","Eau ville SDE","Eau pluie"],"fleuves":"Aucun permanent","lacs":"Aucun","mares":"Mares temporaires","forages":45,"puits":230,"perimetre_irrigue_ha":400,"acces_eau":"Bon","risque_penurie":"Modéré","lat":14.7861,"lon":-16.9203},
    "Mbour":{"nappe":"Nappe sableuse côtière 10-30m qualité variable","eau_types":["Mer Atlantique","Eau souterraine","Eau ville"],"fleuves":"Aucun permanent marigots côtiers","lacs":"Lac Tanma zones humides côtières","mares":"Mares côtières temporaires","forages":35,"puits":180,"perimetre_irrigue_ha":350,"acces_eau":"Bon","risque_penurie":"Modéré","lat":14.3917,"lon":-16.7250},
    "Tivaouane":{"nappe":"Nappe Paléocène 25-70m qualité correcte","eau_types":["Eau souterraine","Eau ville","Eau pluie"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares temporaires","forages":28,"puits":140,"perimetre_irrigue_ha":200,"acces_eau":"Moyen","risque_penurie":"Modéré","lat":14.9500,"lon":-16.8333},
    "Mékhe":{"nappe":"Nappe Paléocène 30-80m","eau_types":["Eau souterraine","Eau pluie"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares temporaires","forages":18,"puits":90,"perimetre_irrigue_ha":150,"acces_eau":"Difficile","risque_penurie":"Élevé","lat":14.8833,"lon":-16.4167},
    "Khombole":{"nappe":"Nappe Paléocène 30-75m","eau_types":["Eau souterraine","Eau pluie"],"fleuves":"Aucun","lacs":"Aucun","mares":"Mares temporaires","forages":15,"puits":80,"perimetre_irrigue_ha":120,"acces_eau":"Difficile","risque_penurie":"Élevé","lat":14.7500,"lon":-16.7000},
    "Ziguinchor":{"nappe":"Continental terminal 8-25m excellente eau douce","eau_types":["Fleuve Casamance","Eau souterraine douce","Marigots permanents","Mangrove"],"fleuves":"Fleuve Casamance permanent navigable eau douce","lacs":"Bras mer mangroves bolons permanents","mares":"Nombreuses mares et marigots permanents","forages":70,"puits":400,"perimetre_irrigue_ha":1500,"acces_eau":"Excellent","risque_penurie":"Très faible","lat":12.5589,"lon":-16.2719},
    "Bignona":{"nappe":"Continental terminal 10-30m très bonne qualité","eau_types":["Marigots permanents","Eau souterraine douce","Fleuve Casamance proche"],"fleuves":"Marigots permanents affluents Casamance","lacs":"Bas-fonds permanents mangroves","mares":"Nombreuses mares permanentes","forages":50,"puits":280,"perimetre_irrigue_ha":900,"acces_eau":"Très bon","risque_penurie":"Faible","lat":12.8101,"lon":-16.2244},
    "Oussouye":{"nappe":"Continental terminal 6-20m excellente qualité","eau_types":["Marigots permanents","Eau souterraine douce","Mer proche","Mangrove"],"fleuves":"Marigots permanents bolons mangrove","lacs":"Bolons permanents mangroves étendues","mares":"Mares et bolons permanents","forages":35,"puits":200,"perimetre_irrigue_ha":600,"acces_eau":"Excellent","risque_penurie":"Très faible","lat":12.4844,"lon":-16.5464},
}



def afficher_section_hydraulique(commune, selected_scenario):
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    import streamlit as st

    data = HYDRAULIQUE.get(commune, None)
    if not data:
        st.warning(f"Données hydrauliques non disponibles pour {commune}")
        return

    st.markdown(f"## 💧 Ressources en eau — {commune}")

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("🔧 Forages fonctionnels", str(data["forages"]))
    col2.metric("🪣 Puits disponibles", str(data["puits"]))
    col3.metric("🌾 Périmètre irrigué", f"{data['perimetre_irrigue_ha']} ha")
    col4.metric("⚠️ Risque pénurie", data["risque_penurie"])

    st.markdown("---")
    col1,col2 = st.columns(2)

    with col1:
        st.markdown("### 🌊 Types d eau disponibles")
        for eau in data["eau_types"]:
            if any(x in eau for x in ["Mer","Atlantique"]):
                emoji = "🔵"
                type_label = "eau salée"
            elif any(x in eau for x in ["Fleuve","fleuve","Rivière"]):
                emoji = "🟦"
                type_label = "eau douce courante"
            elif any(x in eau for x in ["Lac","lac"]):
                emoji = "🟩"
                type_label = "eau douce stagnante"
            elif any(x in eau for x in ["Marigot","marigot","Cascade"]):
                emoji = "🟢"
                type_label = "eau douce saisonnière"
            elif any(x in eau for x in ["Canal","SAED","CSS","irrigation"]):
                emoji = "🟡"
                type_label = "eau irriguée"
            elif any(x in eau for x in ["souterraine","nappe","puits","Eau ville"]):
                emoji = "🟤"
                type_label = "eau souterraine"
            elif any(x in eau for x in ["saumâtre","Mangrove","salée"]):
                emoji = "🟠"
                type_label = "eau saumâtre"
            else:
                emoji = "💧"
                type_label = ""
            st.markdown(f"{emoji} **{eau}** *({type_label})*" if type_label else f"{emoji} **{eau}**")

        st.markdown(f"**🪨 Nappe :** {data['nappe']}")
        st.markdown(f"**🏞️ Fleuves :** {data['fleuves']}")
        st.markdown(f"**🌊 Lacs/Zones humides :** {data['lacs']}")
        st.markdown(f"**🐸 Mares :** {data['mares']}")

    with col2:
        st.markdown("### 📊 Infrastructure hydraulique")
        fig = go.Figure(go.Bar(
            x=["Forages","Puits","Périmètre (ha/10)"],
            y=[data["forages"], data["puits"], data["perimetre_irrigue_ha"]//10],
            marker_color=["#1565C0","#2E7D32","#F57F17"],
            text=[f"{data['forages']}",f"{data['puits']}",f"{data['perimetre_irrigue_ha']} ha"],
            textposition="outside",
        ))
        fig.update_layout(
            title="Infrastructure eau disponible",
            template="plotly_dark",
            paper_bgcolor="#0a0f1e",plot_bgcolor="#0d1527",
            font_color="#e8f4fd",showlegend=False,
            height=300,margin=dict(t=40,b=20,l=10,r=10)
        )
        st.plotly_chart(fig,use_container_width=True)

    st.markdown("---")
    st.markdown("### 🗺️ Carte hydraulique par département")
    st.caption("Reseau hydraulique + forages PNADT filtrés pour la commune selectionnee")
    import json, os
    _path = os.path.join(os.path.dirname(__file__), "data", "senegal_communes.geojson")
    with open(_path, encoding="utf-8") as _f:
        _geo = json.load(_f)
    _dept_list = sorted([f["properties"]["name"] for f in _geo["features"]])
    _dept_sel = st.selectbox("🏘️ Département", _dept_list, key="eau_dept_select")
    _FONDS = {
        "🗺️ OpenStreetMap": "open-street-map",
        "🌙 Sombre (Carto)": "carto-darkmatter",
        "⬜ Clair (Carto)": "carto-positron",
        "🏔️ Terrain (Stamen)": "stamen-terrain",
        "🖤 Contraste (Stamen)": "stamen-toner",
        "🎨 Aquarelle (Stamen)": "stamen-watercolor",
    }
    _fond_choisi = st.selectbox("🗺️ Fond de carte", list(_FONDS.keys()), key="fond_carte_select")
    _style = _FONDS[_fond_choisi]
    if st.button("🗺️ Afficher la carte de " + _dept_sel):
        afficher_carte_commune_eau(_dept_sel, map_style=_style)
    st.markdown("---")
    st.markdown("### 🗺️ Carte des 4218 forages officiels du Sénégal")
    st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")
    if st.button("🗺️ Afficher tous les forages du Senegal"):
        afficher_carte_forages()

    st.markdown("### 🗺️ Carte des types d eau par commune")
    st.caption("Chaque commune est colorée selon son type d eau principal")

    import plotly.graph_objects as go
    COULEURS_EAU = {
        "eau salée":       "#0D47A1",
        "eau douce courante": "#1E88E5",
        "eau douce stagnante": "#26A69A",
        "eau saisonnière": "#66BB6A",
        "eau irriguée":    "#FDD835",
        "eau souterraine": "#8D6E63",
        "eau saumâtre":    "#FF7043",
        "eau de pluie":    "#90CAF9",
    }

    def get_type_principal(eau_types):
        for eau in eau_types:
            if any(x in eau for x in ["Mer","Atlantique","salée"]): return "eau salée"
            if any(x in eau for x in ["Fleuve","Rivière","fleuve"]): return "eau douce courante"
            if any(x in eau for x in ["Lac","lac"]): return "eau douce stagnante"
            if any(x in eau for x in ["Marigot","marigot","saisonnier"]): return "eau saisonnière"
            if any(x in eau for x in ["Canal","SAED","irrigation"]): return "eau irriguée"
            if any(x in eau for x in ["souterraine","nappe","puits","Eau ville"]): return "eau souterraine"
            if any(x in eau for x in ["saumâtre","Mangrove"]): return "eau saumâtre"
        return "eau de pluie"

    fig_types = go.Figure()
    groupes = {}
    for c, d in HYDRAULIQUE.items():
        t = get_type_principal(d["eau_types"])
        if t not in groupes:
            groupes[t] = {"lats":[],"lons":[],"noms":[],"infos":[]}
        groupes[t]["lats"].append(d["lat"])
        groupes[t]["lons"].append(d["lon"])
        groupes[t]["noms"].append(c)
        groupes[t]["infos"].append(
            f"{c}<br>Type: {t}<br>Forages: {d['forages']}<br>Puits: {d['puits']}<br>Acces: {d['acces_eau']}<br>Risque: {d['risque_penurie']}"
        )

    EMOJIS = {
        "eau salée": "🔵",
        "eau douce courante": "🟦",
        "eau douce stagnante": "🟩",
        "eau saisonnière": "🟢",
        "eau irriguée": "🟡",
        "eau souterraine": "🟤",
        "eau saumâtre": "🟠",
        "eau de pluie": "💧",
    }

    for t, g in groupes.items():
        fig_types.add_trace(go.Scattermapbox(
            lat=g["lats"], lon=g["lons"],
            mode="markers",
            name=f"{EMOJIS.get(t,'')} {t} ({len(g['lats'])})",
            marker=dict(size=14, color=COULEURS_EAU.get(t,"#fff"), opacity=0.85),
            text=g["infos"],
            hovertemplate="%{text}<extra></extra>",
        ))

    fig_types.update_layout(
        mapbox=dict(style="open-street-map", center={"lat":14.5,"lon":-14.5}, zoom=5.5),
        title="Types d eau disponibles par commune — Sénégal",
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1,
                   title=dict(text="Type d eau principal")),
    )
    st.plotly_chart(fig_types, use_container_width=True)

    st.markdown("### 🎨 Légende types d eau")
    col1,col2,col3,col4 = st.columns(4)
    col1.markdown("🔵 Mer / Océan (salée)")
    col1.markdown("🟦 Fleuve / Rivière (douce courante)")
    col2.markdown("🟩 Lac (douce stagnante)")
    col2.markdown("🟢 Marigot (saisonnière)")
    col3.markdown("🟡 Canal irrigation")
    col3.markdown("🟤 Eau souterraine / Puits")
    col4.markdown("🟠 Eau saumâtre / Mangrove")
    col4.markdown("💧 Eau de pluie")

    st.markdown("---")
    st.info(f"""
    💡 Recommandations hydrauliques pour {commune} :
    Forages disponibles : {data["forages"]} - Puits : {data["puits"]} - Périmètre irrigué : {data["perimetre_irrigue_ha"]} ha
    Accès à l eau : {data["acces_eau"]} - Risque pénurie : {data["risque_penurie"]}
    Actions prioritaires : réhabiliter les forages existants - construire des retenues d eau - développer l irrigation goutte-à-goutte.
    """)




# ── Données hydrauliques par commune ─────────────────────────────────────────
HYDRAULIQUE = {
    'Dakar': {
        'nappe': 'Nappe des sables quaternaires - profondeur 5-15m - eau saumâtre côtier',
        'eau_types': ['Mer (Atlantique)', 'Eau souterraine', 'Eau de ville (SDE)'],
        'fleuves': 'Aucun fleuve - presquîle entourée de mer',
        'lacs': 'Lac Rose (lac salé) - Baie de Hann',
        'mares': 'Mares temporaires en hivernage',
        'forages': 45, 'puits': 120, 'perimetre_irrigue_ha': 150,
        'acces_eau': 'Très bon (réseau SDE)', 'risque_penurie': 'Modéré (surexploitation nappe)',
        'lat': 14.6928, 'lon': -17.0407, 'couleur_eau': '#1565C0',
    },
    'Pikine': {
        'nappe': 'Nappe phréatique affleurante - 2-8m - risque salinisation',
        'eau_types': ['Eau souterraine', 'Eau de ville', 'Mer (proche)'],
        'fleuves': 'Aucun - zone périurbaine',
        'lacs': 'Lac Mbeubeuss (décharge) - zones humides dégradées',
        'mares': 'Nombreuses mares en hivernage - inondations fréquentes',
        'forages': 28, 'puits': 85, 'perimetre_irrigue_ha': 80,
        'acces_eau': 'Bon (réseau SDE partiel)', 'risque_penurie': 'Modéré',
        'lat': 14.7667, 'lon': -17.1500, 'couleur_eau': '#1976D2',
    },
    'Guediawaye': {
        'nappe': 'Nappe sableuse superficielle - 3-10m - qualité variable',
        'eau_types': ['Eau souterraine', 'Eau de ville'],
        'fleuves': 'Aucun',
        'lacs': 'Zones humides côtières',
        'mares': 'Mares temporaires',
        'forages': 18, 'puits': 60, 'perimetre_irrigue_ha': 40,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 14.7550, 'lon': -17.2850, 'couleur_eau': '#1976D2',
    },
    'Rufisque': {
        'nappe': 'Nappe du Maestrichtien - 80-200m - bonne qualité',
        'eau_types': ['Eau souterraine profonde', 'Mer (Atlantique)', 'Eau de ville'],
        'fleuves': 'Aucun direct',
        'lacs': 'Baie de Rufisque',
        'mares': 'Mares saisonnières',
        'forages': 22, 'puits': 75, 'perimetre_irrigue_ha': 120,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 14.7167, 'lon': -17.2667, 'couleur_eau': '#0D47A1',
    },
    'Bargny': {
        'nappe': 'Nappe côtière saline - eau douce rare - 10-25m',
        'eau_types': ['Mer (Atlantique)', 'Eau souterraine saline', 'Eau de ville'],
        'fleuves': 'Aucun',
        'lacs': 'Mangrove dégradée - zones salées',
        'mares': 'Mares salées',
        'forages': 8, 'puits': 30, 'perimetre_irrigue_ha': 20,
        'acces_eau': 'Difficile (eau salée dominante)', 'risque_penurie': 'Élevé',
        'lat': 14.6942, 'lon': -17.2311, 'couleur_eau': '#0D47A1',
    },
    'Diourbel': {
        'nappe': 'Nappe du Paléocène - 30-80m - bonne qualité',
        'eau_types': ['Eau souterraine', 'Eau de ville', 'Eau de pluie collectée'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun lac permanent',
        'mares': 'Mares temporaires hivernage - importantes pour élevage',
        'forages': 35, 'puits': 180, 'perimetre_irrigue_ha': 200,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 14.6500, 'lon': -16.2333, 'couleur_eau': '#388E3C',
    },
    'Bambey': {
        'nappe': 'Nappe du Continental terminal - 40-90m',
        'eau_types': ['Eau souterraine', 'Eau de pluie'],
        'fleuves': 'Aucun',
        'lacs': 'Aucun',
        'mares': 'Mares villageoises temporaires',
        'forages': 25, 'puits': 150, 'perimetre_irrigue_ha': 180,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 14.7000, 'lon': -16.4500, 'couleur_eau': '#388E3C',
    },
    'Mbacké': {
        'nappe': 'Nappe du Maestrichtien - 60-120m - bonne qualité',
        'eau_types': ['Eau souterraine profonde', 'Eau de ville', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun',
        'mares': 'Mares temporaires importantes',
        'forages': 30, 'puits': 160, 'perimetre_irrigue_ha': 220,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 14.8000, 'lon': -15.9100, 'couleur_eau': '#388E3C',
    },
    'Fatick': {
        'nappe': 'Nappe du Sénégalo-mauritanien - 20-60m - légèrement salée en zones basses',
        'eau_types': ['Eau souterraine', 'Eau salée (bras mer)', 'Eau douce saisonnière'],
        'fleuves': 'Bras du Sine-Saloum - eau saumâtre',
        'lacs': 'Delta du Saloum - mangroves - bolons',
        'mares': 'Nombreuses mares et bolons',
        'forages': 40, 'puits': 200, 'perimetre_irrigue_ha': 350,
        'acces_eau': 'Moyen (salinité problématique)', 'risque_penurie': 'Modéré',
        'lat': 14.3386, 'lon': -16.4114, 'couleur_eau': '#00897B',
    },
    'Gossas': {
        'nappe': 'Nappe du Continental terminal - 50-100m',
        'eau_types': ['Eau souterraine', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun',
        'mares': 'Mares temporaires villageoises',
        'forages': 18, 'puits': 90, 'perimetre_irrigue_ha': 100,
        'acces_eau': 'Difficile', 'risque_penurie': 'Élevé',
        'lat': 14.5000, 'lon': -16.0667, 'couleur_eau': '#388E3C',
    },
    'Foundiougne': {
        'nappe': 'Nappe alluviale - 5-20m - qualité variable selon salinité',
        'eau_types': ['Eau saumâtre (bras mer)', 'Eau douce saisonnière', 'Eau souterraine'],
        'fleuves': 'Bras du Saloum - mangroves',
        'lacs': 'Delta du Saloum - bolons nombreux',
        'mares': 'Bolons et chenaux permanents',
        'forages': 25, 'puits': 110, 'perimetre_irrigue_ha': 280,
        'acces_eau': 'Bon (mais salinité)', 'risque_penurie': 'Modéré',
        'lat': 14.1333, 'lon': -16.4667, 'couleur_eau': '#00897B',
    },
    'Sokone': {
        'nappe': 'Nappe côtière - salinité variable - 10-30m',
        'eau_types': ['Eau saumâtre', 'Eau douce souterraine', 'Mer (Saloum)'],
        'fleuves': 'Fleuve Saloum - bolons',
        'lacs': 'Delta du Saloum',
        'mares': 'Mares et bolons permanents',
        'forages': 20, 'puits': 80, 'perimetre_irrigue_ha': 200,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 13.8833, 'lon': -16.3667, 'couleur_eau': '#00897B',
    },
    'Kaolack': {
        'nappe': 'Nappe du Maestrichtien - 40-100m - très bonne qualité',
        'eau_types': ['Eau souterraine', 'Fleuve Saloum', 'Eau de ville (SDE)'],
        'fleuves': 'Fleuve Saloum - navigation possible',
        'lacs': 'Bras du Saloum - lac salé en aval',
        'mares': 'Mares temporaires',
        'forages': 55, 'puits': 280, 'perimetre_irrigue_ha': 500,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 13.9667, 'lon': -16.0167, 'couleur_eau': '#1565C0',
    },
    'Kaffrine': {
        'nappe': 'Nappe du Maestrichtien - 60-140m - bonne qualité',
        'eau_types': ['Eau souterraine profonde', 'Eau de pluie collectée'],
        'fleuves': 'Aucun permanent - marigots saisonniers',
        'lacs': 'Aucun permanent',
        'mares': 'Mares temporaires importantes pour élevage',
        'forages': 42, 'puits': 220, 'perimetre_irrigue_ha': 300,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 14.1056, 'lon': -15.5506, 'couleur_eau': '#388E3C',
    },
    'Nioro du Rip': {
        'nappe': 'Nappe du Continental terminal - 40-80m',
        'eau_types': ['Eau souterraine', 'Marigots saisonniers', 'Eau de pluie'],
        'fleuves': 'Marigot du Rip - saisonnier',
        'lacs': 'Aucun permanent',
        'mares': 'Mares saisonnières importantes',
        'forages': 30, 'puits': 160, 'perimetre_irrigue_ha': 250,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 13.7500, 'lon': -15.7833, 'couleur_eau': '#388E3C',
    },
    'Kolda': {
        'nappe': 'Nappe du Continental terminal - 20-50m - excellente qualité',
        'eau_types': ['Eau souterraine douce', 'Fleuve Casamance', 'Marigots permanents'],
        'fleuves': 'Fleuve Casamance - permanent - navigable',
        'lacs': 'Marigots et bas-fonds permanents',
        'mares': 'Nombreuses mares permanentes et temporaires',
        'forages': 65, 'puits': 350, 'perimetre_irrigue_ha': 800,
        'acces_eau': 'Très bon', 'risque_penurie': 'Faible',
        'lat': 12.8908, 'lon': -14.9508, 'couleur_eau': '#2E7D32',
    },
    'Vélingara': {
        'nappe': 'Nappe du Continental terminal - 25-60m - bonne qualité',
        'eau_types': ['Eau souterraine douce', 'Marigots permanents', 'Fleuve Gambie (proche)'],
        'fleuves': 'Marigot de Vélingara - Fleuve Gambie (nord)',
        'lacs': 'Bas-fonds permanents',
        'mares': 'Nombreuses mares permanentes',
        'forages': 50, 'puits': 280, 'perimetre_irrigue_ha': 600,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 13.1500, 'lon': -14.1000, 'couleur_eau': '#2E7D32',
    },
    'Médina Yoro Foulah': {
        'nappe': 'Nappe latéritique - 15-40m - qualité moyenne',
        'eau_types': ['Eau souterraine', 'Marigots saisonniers'],
        'fleuves': 'Marigots saisonniers',
        'lacs': 'Bas-fonds temporaires',
        'mares': 'Mares temporaires',
        'forages': 25, 'puits': 140, 'perimetre_irrigue_ha': 200,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 13.4000, 'lon': -14.2000, 'couleur_eau': '#388E3C',
    },
    'Kédougou': {
        'nappe': 'Nappe des altérites - 10-30m - excellente qualité',
        'eau_types': ['Eau souterraine douce', 'Fleuve Gambie', 'Rivières permanentes', 'Cascades'],
        'fleuves': 'Fleuve Gambie - Fleuve Falémé - nombreuses rivières',
        'lacs': 'Nombreux cours eau permanents - cascades de Dindefelo',
        'mares': 'Mares et rivières permanentes',
        'forages': 40, 'puits': 200, 'perimetre_irrigue_ha': 400,
        'acces_eau': 'Excellent', 'risque_penurie': 'Très faible',
        'lat': 12.5569, 'lon': -12.1747, 'couleur_eau': '#1B5E20',
    },
    'Saraya': {
        'nappe': 'Nappe des altérites - 8-25m - très bonne qualité',
        'eau_types': ['Eau souterraine douce', 'Fleuve Falémé', 'Rivières permanentes'],
        'fleuves': 'Fleuve Falémé - permanent - or alluvionnaire',
        'lacs': 'Cours eau permanents',
        'mares': 'Nombreuses mares et rivières',
        'forages': 20, 'puits': 100, 'perimetre_irrigue_ha': 150,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 12.8333, 'lon': -11.7500, 'couleur_eau': '#1B5E20',
    },
    'Salékata': {
        'nappe': 'Nappe des altérites - 10-30m',
        'eau_types': ['Eau souterraine douce', 'Rivières saisonnières'],
        'fleuves': 'Rivières saisonnières',
        'lacs': 'Bas-fonds temporaires',
        'mares': 'Mares temporaires',
        'forages': 12, 'puits': 60, 'perimetre_irrigue_ha': 80,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 12.6300, 'lon': -12.8200, 'couleur_eau': '#2E7D32',
    },
    'Louga': {
        'nappe': 'Nappe du Maestrichtien - 80-200m - très bonne qualité mais profonde',
        'eau_types': ['Eau souterraine profonde', 'Eau de pluie collectée'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun permanent',
        'mares': 'Mares temporaires critiques pour élevage',
        'forages': 38, 'puits': 190, 'perimetre_irrigue_ha': 150,
        'acces_eau': 'Difficile (profondeur nappe)', 'risque_penurie': 'Élevé',
        'lat': 15.6167, 'lon': -16.2333, 'couleur_eau': '#F57F17',
    },
    'Linguère': {
        'nappe': 'Nappe du Maestrichtien - 100-250m - très profonde',
        'eau_types': ['Eau souterraine très profonde', 'Eau de pluie'],
        'fleuves': 'Aucun permanent - marigots saisonniers',
        'lacs': 'Aucun permanent',
        'mares': 'Mares temporaires essentielles pour pasteurs',
        'forages': 25, 'puits': 120, 'perimetre_irrigue_ha': 80,
        'acces_eau': 'Très difficile', 'risque_penurie': 'Très élevé',
        'lat': 15.3833, 'lon': -15.1167, 'couleur_eau': '#E65100',
    },
    'Kébémer': {
        'nappe': 'Nappe du Paléocène - 40-100m - qualité correcte',
        'eau_types': ['Eau souterraine', 'Eau de pluie collectée'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun',
        'mares': 'Mares temporaires',
        'forages': 22, 'puits': 110, 'perimetre_irrigue_ha': 120,
        'acces_eau': 'Moyen', 'risque_penurie': 'Élevé',
        'lat': 15.3667, 'lon': -16.4500, 'couleur_eau': '#F57F17',
    },
    'Matam': {
        'nappe': 'Nappe alluviale du fleuve Sénégal - 5-20m - bonne qualité',
        'eau_types': ['Fleuve Sénégal', 'Eau souterraine alluviale', 'Canaux SAED'],
        'fleuves': 'Fleuve Sénégal - permanent - grand débit',
        'lacs': 'Plaine inondation (Walo) - mares decrue',
        'mares': 'Mares decrue permanentes - walo',
        'forages': 48, 'puits': 250, 'perimetre_irrigue_ha': 1200,
        'acces_eau': 'Très bon (fleuve)', 'risque_penurie': 'Faible',
        'lat': 15.6553, 'lon': -13.2553, 'couleur_eau': '#1565C0',
    },
    'Kanel': {
        'nappe': 'Nappe alluviale - 8-25m - bonne qualité',
        'eau_types': ['Fleuve Sénégal', 'Eau alluviale', 'Canaux irrigation'],
        'fleuves': 'Fleuve Sénégal - décrue agricole',
        'lacs': 'Plaine inondable (Walo)',
        'mares': 'Mares decrue importantes',
        'forages': 30, 'puits': 160, 'perimetre_irrigue_ha': 800,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 15.4900, 'lon': -13.1700, 'couleur_eau': '#1565C0',
    },
    'Ranérou': {
        'nappe': 'Nappe du Maestrichtien - 100-200m - très profonde',
        'eau_types': ['Eau souterraine très profonde', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun permanent',
        'mares': 'Mares temporaires critiques pour élevage pastoral',
        'forages': 15, 'puits': 70, 'perimetre_irrigue_ha': 50,
        'acces_eau': 'Très difficile', 'risque_penurie': 'Très élevé',
        'lat': 15.3000, 'lon': -13.9600, 'couleur_eau': '#E65100',
    },
    'Saint-Louis': {
        'nappe': 'Nappe alluviale delta - 3-10m - qualité variable (salinité)',
        'eau_types': ['Fleuve Sénégal', 'Mer (Atlantique)', 'Eau douce delta', 'Canaux SAED'],
        'fleuves': 'Fleuve Sénégal - delta - très grand débit',
        'lacs': 'Lac de Guiers - lac Diama - plaine inondable',
        'mares': 'Nombreuses mares permanentes et temporaires',
        'forages': 80, 'puits': 400, 'perimetre_irrigue_ha': 5000,
        'acces_eau': 'Excellent (fleuve + irrigation)', 'risque_penurie': 'Très faible',
        'lat': 16.0167, 'lon': -16.4833, 'couleur_eau': '#0D47A1',
    },
    'Podor': {
        'nappe': 'Nappe alluviale Walo - 5-15m - bonne qualité',
        'eau_types': ['Fleuve Sénégal', 'Eau alluviale', 'Canaux SAED'],
        'fleuves': 'Fleuve Sénégal - Doué (défluent)',
        'lacs': 'Plaine Walo inondable - mares permanentes',
        'mares': 'Mares decrue importantes',
        'forages': 45, 'puits': 230, 'perimetre_irrigue_ha': 2500,
        'acces_eau': 'Très bon', 'risque_penurie': 'Faible',
        'lat': 16.6500, 'lon': -15.2000, 'couleur_eau': '#1565C0',
    },
    'Dagana': {
        'nappe': 'Nappe alluviale - 3-12m - bonne qualité',
        'eau_types': ['Fleuve Sénégal', 'Lac de Guiers', 'Canaux SAED', 'Eau douce'],
        'fleuves': 'Fleuve Sénégal - Lac de Guiers',
        'lacs': 'Lac de Guiers (réservoir eau douce majeur)',
        'mares': 'Lac de Guiers - plaine inondable',
        'forages': 50, 'puits': 250, 'perimetre_irrigue_ha': 3500,
        'acces_eau': 'Excellent', 'risque_penurie': 'Très faible',
        'lat': 16.4000, 'lon': -15.7667, 'couleur_eau': '#0D47A1',
    },
    'Richard-Toll': {
        'nappe': 'Nappe alluviale - 2-8m - bonne qualité',
        'eau_types': ['Fleuve Sénégal', 'Lac de Guiers', 'Canaux CSS', 'Eau douce abondante'],
        'fleuves': 'Fleuve Sénégal - canal de la CSS',
        'lacs': 'Lac de Guiers (adjacent)',
        'mares': 'Canaux irrigation permanents',
        'forages': 35, 'puits': 120, 'perimetre_irrigue_ha': 8000,
        'acces_eau': 'Excellent (irrigation intensive)', 'risque_penurie': 'Très faible',
        'lat': 16.4628, 'lon': -15.7022, 'couleur_eau': '#0D47A1',
    },
    'Sédhiou': {
        'nappe': 'Nappe du Continental terminal - 15-40m - très bonne qualité',
        'eau_types': ['Fleuve Casamance', 'Eau souterraine douce', 'Marigots permanents'],
        'fleuves': 'Fleuve Casamance - permanent - navigable',
        'lacs': 'Marigots et bras mer permanents',
        'mares': 'Nombreuses mares permanentes',
        'forages': 55, 'puits': 300, 'perimetre_irrigue_ha': 700,
        'acces_eau': 'Très bon', 'risque_penurie': 'Faible',
        'lat': 12.7078, 'lon': -15.5569, 'couleur_eau': '#2E7D32',
    },
    'Goudomp': {
        'nappe': 'Nappe du Continental terminal - 10-30m - excellente qualité',
        'eau_types': ['Fleuve Casamance', 'Eau souterraine douce', 'Marigots'],
        'fleuves': 'Fleuve Casamance - marigots permanents',
        'lacs': 'Bas-fonds permanents - mangrove',
        'mares': 'Nombreuses mares et marigots',
        'forages': 35, 'puits': 180, 'perimetre_irrigue_ha': 400,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 12.5700, 'lon': -15.1800, 'couleur_eau': '#2E7D32',
    },
    'Bounkiling': {
        'nappe': 'Nappe du Continental terminal - 12-35m - bonne qualité',
        'eau_types': ['Marigots permanents', 'Eau souterraine douce', 'Eau de pluie'],
        'fleuves': 'Marigots permanents - affluents Casamance',
        'lacs': 'Bas-fonds permanents',
        'mares': 'Mares permanentes',
        'forages': 28, 'puits': 140, 'perimetre_irrigue_ha': 300,
        'acces_eau': 'Bon', 'risque_penurie': 'Faible',
        'lat': 12.9000, 'lon': -14.9700, 'couleur_eau': '#2E7D32',
    },
    'Tambacounda': {
        'nappe': 'Nappe du Continental terminal - 30-80m - bonne qualité',
        'eau_types': ['Fleuve Gambie', 'Eau souterraine', 'Marigots saisonniers'],
        'fleuves': 'Fleuve Gambie (nord) - Fleuve Falémé (est)',
        'lacs': 'Mares permanentes en saison sèche',
        'mares': 'Mares importantes pour élevage',
        'forages': 60, 'puits': 320, 'perimetre_irrigue_ha': 600,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 13.7719, 'lon': -13.7731, 'couleur_eau': '#F57F17',
    },
    'Bakel': {
        'nappe': 'Nappe alluviale Fleuve Sénégal - 5-20m',
        'eau_types': ['Fleuve Sénégal', 'Fleuve Falémé', 'Eau alluviale'],
        'fleuves': 'Fleuve Sénégal - Fleuve Falémé (confluent)',
        'lacs': 'Plaine inondable - mares decrue',
        'mares': 'Mares decrue importantes',
        'forages': 25, 'puits': 130, 'perimetre_irrigue_ha': 400,
        'acces_eau': 'Bon (fleuve)', 'risque_penurie': 'Modéré',
        'lat': 14.9000, 'lon': -12.4667, 'couleur_eau': '#1565C0',
    },
    'Goudiry': {
        'nappe': 'Nappe du Continental terminal - 40-90m',
        'eau_types': ['Eau souterraine', 'Marigots saisonniers'],
        'fleuves': 'Marigots saisonniers - Falémé (est)',
        'lacs': 'Mares temporaires',
        'mares': 'Mares temporaires importantes',
        'forages': 30, 'puits': 160, 'perimetre_irrigue_ha': 200,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 14.1833, 'lon': -12.7333, 'couleur_eau': '#F57F17',
    },
    'Koumpentoum': {
        'nappe': 'Nappe du Continental terminal - 35-80m',
        'eau_types': ['Eau souterraine', 'Marigots saisonniers', 'Eau de pluie'],
        'fleuves': 'Marigots saisonniers',
        'lacs': 'Aucun permanent',
        'mares': 'Mares temporaires',
        'forages': 28, 'puits': 150, 'perimetre_irrigue_ha': 250,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 13.9833, 'lon': -14.5500, 'couleur_eau': '#F57F17',
    },
    'Thiès': {
        'nappe': 'Nappe du Paléocène - 20-60m - bonne qualité',
        'eau_types': ['Eau souterraine', 'Eau de ville (SDE)', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun permanent',
        'mares': 'Mares temporaires',
        'forages': 45, 'puits': 230, 'perimetre_irrigue_ha': 400,
        'acces_eau': 'Bon', 'risque_penurie': 'Modéré',
        'lat': 14.7861, 'lon': -16.9203, 'couleur_eau': '#1976D2',
    },
    'Mbour': {
        'nappe': 'Nappe sableuse côtière - 10-30m - qualité variable',
        'eau_types': ['Mer (Atlantique)', 'Eau souterraine', 'Eau de ville'],
        'fleuves': 'Aucun permanent - marigots côtiers',
        'lacs': 'Lac Tanma - zones humides côtières',
        'mares': 'Mares côtières temporaires',
        'forages': 35, 'puits': 180, 'perimetre_irrigue_ha': 350,
        'acces_eau': 'Bon', 'risque_penurie': 'Modéré',
        'lat': 14.3917, 'lon': -16.7250, 'couleur_eau': '#1976D2',
    },
    'Tivaouane': {
        'nappe': 'Nappe du Paléocène - 25-70m - qualité correcte',
        'eau_types': ['Eau souterraine', 'Eau de ville', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun',
        'mares': 'Mares temporaires',
        'forages': 28, 'puits': 140, 'perimetre_irrigue_ha': 200,
        'acces_eau': 'Moyen', 'risque_penurie': 'Modéré',
        'lat': 14.9500, 'lon': -16.8333, 'couleur_eau': '#1976D2',
    },
    'Mékhe': {
        'nappe': 'Nappe du Paléocène - 30-80m',
        'eau_types': ['Eau souterraine', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun',
        'mares': 'Mares temporaires',
        'forages': 18, 'puits': 90, 'perimetre_irrigue_ha': 150,
        'acces_eau': 'Difficile', 'risque_penurie': 'Élevé',
        'lat': 14.8833, 'lon': -16.4167, 'couleur_eau': '#F57F17',
    },
    'Khombole': {
        'nappe': 'Nappe du Paléocène - 30-75m',
        'eau_types': ['Eau souterraine', 'Eau de pluie'],
        'fleuves': 'Aucun permanent',
        'lacs': 'Aucun',
        'mares': 'Mares temporaires',
        'forages': 15, 'puits': 80, 'perimetre_irrigue_ha': 120,
        'acces_eau': 'Difficile', 'risque_penurie': 'Élevé',
        'lat': 14.7500, 'lon': -16.7000, 'couleur_eau': '#F57F17',
    },
    'Ziguinchor': {
        'nappe': 'Nappe du Continental terminal - 8-25m - excellente qualité eau douce',
        'eau_types': ['Fleuve Casamance', 'Eau souterraine douce', 'Marigots permanents', 'Mangrove'],
        'fleuves': 'Fleuve Casamance - permanent - navigable - eau douce',
        'lacs': 'Bras mer - mangroves - bolons permanents',
        'mares': 'Nombreuses mares et marigots permanents',
        'forages': 70, 'puits': 400, 'perimetre_irrigue_ha': 1500,
        'acces_eau': 'Excellent', 'risque_penurie': 'Très faible',
        'lat': 12.5589, 'lon': -16.2719, 'couleur_eau': '#1B5E20',
    },
    'Bignona': {
        'nappe': 'Nappe du Continental terminal - 10-30m - très bonne qualité',
        'eau_types': ['Marigots permanents', 'Eau souterraine douce', 'Fleuve Casamance (proche)'],
        'fleuves': 'Marigots permanents - affluents Casamance',
        'lacs': 'Bas-fonds permanents - mangroves',
        'mares': 'Nombreuses mares permanentes',
        'forages': 50, 'puits': 280, 'perimetre_irrigue_ha': 900,
        'acces_eau': 'Très bon', 'risque_penurie': 'Faible',
        'lat': 12.8101, 'lon': -16.2244, 'couleur_eau': '#2E7D32',
    },
    'Oussouye': {
        'nappe': 'Nappe du Continental terminal - 6-20m - excellente qualité',
        'eau_types': ['Marigots permanents', 'Eau souterraine douce', 'Mer (proche)', 'Mangrove'],
        'fleuves': 'Marigots permanents - bolons - mangrove',
        'lacs': 'Bolons permanents - mangroves étendues',
        'mares': 'Mares et bolons permanents',
        'forages': 35, 'puits': 200, 'perimetre_irrigue_ha': 600,
        'acces_eau': 'Excellent', 'risque_penurie': 'Très faible',
        'lat': 12.4844, 'lon': -16.5464, 'couleur_eau': '#1B5E20',
    },
}


def afficher_carte_hydrographie(selected_scenario):
    import json, os
    import plotly.graph_objects as go

    geojson_path = os.path.join(os.path.dirname(__file__), "data", "hydrographie_sn.geojson")
    if not os.path.exists(geojson_path):
        geojson_path = os.path.join(os.path.dirname(__file__), "..", "data", "hydrographie_sn.geojson")
    if not os.path.exists(geojson_path):
        st.error(f"Fichier hydrographie non trouvé")
        return

    with open(geojson_path, encoding="utf-8") as f:
        gj = json.load(f)

    COULEURS = {
        "Main river":       ("#1565C0", 3),
        "Secondary river":  ("#1976D2", 2),
        "Temporary stream": ("#90CAF9", 1),
        "Lake":             ("#0D47A1", 2),
        "Canal":            ("#00897B", 2),
        "Pond":             ("#26C6DA", 1),
        "Swamp":            ("#558B2F", 1),
        "Reservoir":        ("#1B5E20", 2),
    }
    LABELS = {
        "Main river":       "Fleuve principal",
        "Secondary river":  "Rivière secondaire",
        "Temporary stream": "Cours d eau temporaire",
        "Lake":             "Lac",
        "Canal":            "Canal",
        "Pond":             "Mare / Etang",
        "Swamp":            "Marais / Zone humide",
        "Reservoir":        "Réservoir",
    }

    traces_par_type = {}
    for feat in gj["features"]:
        props = feat["properties"]
        t = props.get("type", "Autre")
        coords = feat["geometry"]["coordinates"]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        couleur, width = COULEURS.get(t, ("#4db8ff", 1))
        label = LABELS.get(t, t)
        if t not in traces_par_type:
            traces_par_type[t] = {"lons":[],"lats":[],"couleur":couleur,"width":width,"label":label}
        traces_par_type[t]["lons"] += lons + [None]
        traces_par_type[t]["lats"] += lats + [None]

    fig = go.Figure()
    ordre = ["Temporary stream","Pond","Swamp","Canal","Reservoir","Secondary river","Lake","Main river"]
    for t in ordre:
        if t not in traces_par_type:
            continue
        d = traces_par_type[t]
        fig.add_trace(go.Scattermapbox(
            lon=d["lons"], lat=d["lats"],
            mode="lines",
            name=d["label"],
            line=dict(color=d["couleur"], width=d["width"]),
            hoverinfo="name",
        ))

    fig.update_layout(
        mapbox=dict(style="open-street-map",center={"lat":14.5,"lon":-14.5},zoom=5.5),
        title="Réseau Hydrographique du Sénégal",
        height=650,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(bgcolor="#0d1527",bordercolor="#2a4a7f",borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Légende")
    legende_items = [
        ("Fleuve principal",       "#1565C0", 6),
        ("Rivière secondaire",     "#1976D2", 4),
        ("Cours d eau temporaire", "#90CAF9", 2),
        ("Lac",                    "#0D47A1", 4),
        ("Canal",                  "#00897B", 3),
        ("Mare / Etang",           "#26C6DA", 2),
        ("Marais / Zone humide",   "#558B2F", 2),
        ("Réservoir",              "#1B5E20", 3),
    ]
    html_leg = "<div style='display:flex;flex-wrap:wrap;gap:14px;padding:12px;background:#0d1527;border-radius:8px;'>"
    for label, couleur, ep in legende_items:
        html_leg += f"<div style='display:flex;align-items:center;gap:8px;'><svg width='45' height='10'><line x1='0' y1='5' x2='45' y2='5' stroke='{couleur}' stroke-width='{ep}' stroke-linecap='round'/></svg><span style='color:#e8f4fd;font-size:13px;'>{label}</span></div>"
    html_leg += "</div>"
    st.markdown(html_leg, unsafe_allow_html=True)

    from collections import Counter
    types_count = Counter(f["properties"]["type"] for f in gj["features"])
    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total segments", str(len(gj["features"])))
    c2.metric("Fleuves principaux", str(types_count.get("Main river",0)))
    c3.metric("Rivières secondaires", str(types_count.get("Secondary river",0)))
    c4.metric("Cours temporaires", str(types_count.get("Temporary stream",0)))

    noms = set()
    for feat in gj["features"]:
        n = feat["properties"].get("name","")
        t = feat["properties"].get("type","")
        if n and t in ["Main river","Secondary river","Lake","Canal"]:
            noms.add(f"{n} ({LABELS.get(t,t)})")
    st.markdown("### Principaux cours d eau")
    for nom in sorted(noms):
        st.markdown(f"- {nom}")



import json as _json
import os as _os

@st.cache_data(ttl=300)
def get_projections(commune, scenario):
    """Charge les projections journalières 2025-2055"""
    # Cherche le fichier dans plusieurs emplacements possibles
    chemins = [
        _os.path.join(_os.path.dirname(__file__), "projections_2025_2055.json"),
        _os.path.join(_os.path.dirname(__file__), "data", "projections_2025_2055.json"),
        _os.path.join(_os.path.dirname(__file__), "data", "projections", "projections_2025_2055.json"),
        _os.path.join(_os.path.dirname(__file__), "..", "data", "projections", "projections_2025_2055.json"),
    ]
    path = next((p for p in chemins if _os.path.exists(p)), None)
    if path is None:
        return None
    with open(path, encoding="utf-8") as f:
        proj = _json.load(f)
    # Mapping scénario
    sc_map = {"SSP1-1.9":"SSP1","SSP2-4.5":"SSP2","SSP5-8.5":"SSP5"}
    sc_key = sc_map.get(scenario, "SSP2")
    if commune not in proj:
        return None
    if sc_key not in proj[commune]["scenarios"]:
        return None
    data = proj[commune]["scenarios"][sc_key]
    df = pd.DataFrame({
        "date":     data["time"],
        "temp_mean":data["temperature_2m_mean"],
        "temp_max": data["temperature_2m_max"],
        "temp_min": data["temperature_2m_min"],
        "precip":   data["precipitation_sum"],
        "eto":      data["et0_fao_evapotranspiration"],
        "vent":     data["windspeed_10m_max"],
    })
    df["date"] = pd.to_datetime(df["date"])
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    return df

def agreger_mensuel(df):
    """Agrège les données journalières en mensuel"""
    return df.groupby("year_month").agg(
        temp_mean=("temp_mean","mean"),
        temp_max =("temp_max","max"),
        temp_min =("temp_min","min"),
        precip   =("precip","sum"),
        eto      =("eto","mean"),
        vent     =("vent","mean"),
    ).reset_index().round(2)

def agreger_annuel(df):
    """Agrège les données journalières en annuel"""
    return df.groupby("year").agg(
        temp_mean=("temp_mean","mean"),
        temp_max =("temp_max","max"),
        temp_min =("temp_min","min"),
        precip   =("precip","sum"),
        eto      =("eto","mean"),
        vent     =("vent","mean"),
    ).reset_index().round(2)


@st.cache_data(ttl=3600)
def charger_forages():
    import json, os
    chemins = [
        os.path.join(os.path.dirname(__file__), "data", "forages_senegal.geojson"),
        os.path.join(os.path.dirname(__file__), "..", "data", "forages_senegal.geojson"),
    ]
    path = next((p for p in chemins if os.path.exists(p)), None)
    if path is None: return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=3600)
def charger_hydrographie():
    import json, os
    chemins = [
        os.path.join(os.path.dirname(__file__), "..", "data", "hydrographie_sn.geojson"),
        os.path.join(os.path.dirname(__file__), "data", "hydrographie_sn.geojson"),
    ]
    path = next((p for p in chemins if os.path.exists(p)), None)
    if path is None: return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_bbox_commune(commune_name):
    import json, os
    chemins = [
        os.path.join(os.path.dirname(__file__), "data", "senegal_communes.geojson"),
        os.path.join(os.path.dirname(__file__), "..", "data", "communes", "senegal_communes.geojson"),
        os.path.join(os.path.dirname(__file__), "data", "communes", "senegal_communes.geojson"),
    ]
    path = next((p for p in chemins if os.path.exists(p)), None)
    if path is None:
        import streamlit as st
        st.error("Chemins testes: " + str(chemins))
        return None
    with open(path, encoding="utf-8") as f:
        communes = json.load(f)
    for feat in communes["features"]:
        if feat["properties"]["name"] == commune_name:
            coords = feat["geometry"]["coordinates"]
            geom_type = feat["geometry"]["type"]
            all_coords = []
            if geom_type == "Point":
                lon, lat = coords
                delta = 0.15
                return {
                    "minlon": lon - delta, "maxlon": lon + delta,
                    "minlat": lat - delta, "maxlat": lat + delta,
                    "centerlon": lon, "centerlat": lat,
                    "coords": [[lon-delta,lat-delta],[lon+delta,lat-delta],[lon+delta,lat+delta],[lon-delta,lat+delta]]
                }
            if geom_type == "Polygon":
                for ring in coords:
                    all_coords.extend(ring)
            elif geom_type == "MultiPolygon":
                for poly in coords:
                    for ring in poly:
                        all_coords.extend(ring)
            if all_coords:
                lons = [c[0] for c in all_coords]
                lats = [c[1] for c in all_coords]
                return {
                    "minlon": min(lons), "maxlon": max(lons),
                    "minlat": min(lats), "maxlat": max(lats),
                    "centerlon": sum(lons)/len(lons),
                    "centerlat": sum(lats)/len(lats),
                    "coords": all_coords
                }
    return None

def afficher_carte_commune_eau(commune_name, map_style="open-street-map"):
    import plotly.graph_objects as go
    bbox = get_bbox_commune(commune_name)
    if bbox is None:
        st.warning("Geometrie non disponible pour " + commune_name)
        return

    marge = 0.3
    minlon = bbox["minlon"] - marge
    maxlon = bbox["maxlon"] + marge
    minlat = bbox["minlat"] - marge
    maxlat = bbox["maxlat"] + marge

    hydro = charger_hydrographie()
    forages = charger_forages()

    fig = go.Figure()

    if hydro:
        COULEURS_HYDRO = {
            "Main river": "#1565C0",
            "Secondary river": "#42A5F5",
            "Lake": "#26A69A",
            "Canal": "#FDD835",
            "Reservoir": "#0097A7",
        }
        # Grouper les segments par type pour une légende propre
        groupes_hydro = {}
        for feat in hydro["features"]:
            geom = feat["geometry"]
            props = feat["properties"]
            type_eau = props.get("type", "Cours d eau")
            nom_eau = props.get("name", "")
            couleur = COULEURS_HYDRO.get(type_eau, "#90CAF9")
            label = nom_eau if nom_eau and nom_eau not in groupes_hydro else type_eau
            if geom["type"] == "LineString":
                lons = [c[0] for c in geom["coordinates"]]
                lats = [c[1] for c in geom["coordinates"]]
                if any(minlon <= lo <= maxlon and minlat <= la <= maxlat for lo, la in zip(lons, lats)):
                    if type_eau not in groupes_hydro:
                        groupes_hydro[type_eau] = {"lons": [], "lats": [], "couleur": couleur}
                    groupes_hydro[type_eau]["lons"] += lons + [None]
                    groupes_hydro[type_eau]["lats"] += lats + [None]
            elif geom["type"] == "Point":
                lo, la = geom["coordinates"]
                if minlon <= lo <= maxlon and minlat <= la <= maxlat:
                    key = f"pt_{type_eau}"
                    if key not in groupes_hydro:
                        groupes_hydro[key] = {"lons": [], "lats": [], "couleur": couleur}
                    groupes_hydro[key]["lons"].append(lo)
                    groupes_hydro[key]["lats"].append(la)

        for label, g in groupes_hydro.items():
            is_point = label.startswith("pt_")
            fig.add_trace(go.Scattermapbox(
                lon=g["lons"], lat=g["lats"],
                mode="markers" if is_point else "lines",
                line=dict(color=g["couleur"], width=3) if not is_point else None,
                marker=dict(size=8, color=g["couleur"]) if is_point else None,
                name=label.replace("pt_", ""),
                hoverinfo="name",
                showlegend=True,
            ))

    if forages:
        COULEURS_NAPPE = {
            "Maastrichtien": "#0D47A1",
            "Eocene": "#1565C0",
            "Socle paleocene": "#1976D2",
            "Paleocene": "#1E88E5",
            "Continental": "#42A5F5",
            "Quaternaire": "#90CAF9",
            "Oligo-miocene": "#0097A7",
            "Infrabasalt": "#00695C",
        }
        groupes = {}
        for feat in forages["features"]:
            p = feat["properties"]
            lo = feat["geometry"]["coordinates"][0]
            la = feat["geometry"]["coordinates"][1]
            if minlon <= lo <= maxlon and minlat <= la <= maxlat:
                nappe = p.get("nappe", "Autre")
                if nappe not in groupes:
                    groupes[nappe] = {"lons":[], "lats":[], "noms":[]}
                groupes[nappe]["lons"].append(lo)
                groupes[nappe]["lats"].append(la)
                groupes[nappe]["noms"].append(p.get("nom", ""))

        nb_forages = sum(len(g["lons"]) for g in groupes.values())

        for nappe, d in sorted(groupes.items()):
            fig.add_trace(go.Scattermapbox(
                lon=d["lons"], lat=d["lats"], mode="markers",
                name=f"{nappe} ({len(d['lons'])})",
                marker=dict(size=9, color=COULEURS_NAPPE.get(nappe, "#4db8ff"), opacity=0.9),
                text=d["noms"],
                hovertemplate="<b>%{text}</b><br>Nappe: " + nappe + "<extra></extra>",
            ))

        st.metric("Forages dans la zone", nb_forages)

    # bbox = (minlon, minlat, maxlon, maxlat)
    minlon, minlat, maxlon, maxlat = bbox["minlon"], bbox["minlat"], bbox["maxlon"], bbox["maxlat"]
    lons_poly = [minlon, maxlon, maxlon, minlon, minlon]
    lats_poly = [minlat, minlat, maxlat, maxlat, minlat]
    fig.add_trace(go.Scattermapbox(
        lon=lons_poly,
        lat=lats_poly,
        mode="lines",
        line=dict(color="#ff4444", width=2),
        name="Limite commune",
        hoverinfo="skip",
    ))

    # Zoom adaptatif selon la taille du département
    import math
    lat_range = bbox["maxlat"] - bbox["minlat"]
    lon_range = bbox["maxlon"] - bbox["minlon"]
    max_range = max(lat_range, lon_range)
    if max_range < 0.5: zoom_auto = 10
    elif max_range < 1.0: zoom_auto = 9
    elif max_range < 2.0: zoom_auto = 8
    elif max_range < 4.0: zoom_auto = 7
    else: zoom_auto = 6

    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center={"lat": (bbox["minlat"]+bbox["maxlat"])/2, "lon": (bbox["minlon"]+bbox["maxlon"])/2},
            zoom=zoom_auto,
        ),
        title=f"Reseau hydraulique et forages — {commune_name}",
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(
            bgcolor="#0d1527", bordercolor="#2a4a7f", borderwidth=1,
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=10), itemwidth=30,
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})


def afficher_carte_forages():
    import plotly.graph_objects as go
    import streamlit as st
    gj = charger_forages()
    if gj is None:
        st.error("Fichier forages non trouve")
        return

    path = os.path.join(os.path.dirname(__file__), "data", "forages_senegal.geojson")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "..", "data", "forages_senegal.geojson")
    if not os.path.exists(path):
        st.error("Fichier forages non trouve")
        return

    import json as _json_f
    with open(path, encoding="utf-8") as f:
        gj = _json_f.load(f)

    COULEURS = {
        "Maastrichtien":   "#0D47A1",
        "Eocene":          "#1565C0",
        "Socle paleocene": "#1976D2",
        "Paleocene":       "#1E88E5",
        "Continental":     "#42A5F5",
        "Quaternaire":     "#90CAF9",
        "Oligo-miocene":   "#0097A7",
        "Infrabasalt":     "#00695C",
    }

    # Regroupe par nappe
    traces = {}
    for feat in gj["features"]:
        p   = feat["properties"]
        nappe = p.get("nappe","Autre")
        lon = feat["geometry"]["coordinates"][0]
        lat = feat["geometry"]["coordinates"][1]
        if nappe not in traces:
            traces[nappe] = {"lons":[],"lats":[],"noms":[],"couleur":p.get("couleur","#4db8ff")}
        traces[nappe]["lons"].append(lon)
        traces[nappe]["lats"].append(lat)
        traces[nappe]["noms"].append(p.get("nom",""))

    fig = go.Figure()
    for nappe, d in sorted(traces.items()):
        fig.add_trace(go.Scattermapbox(
            lon=d["lons"], lat=d["lats"],
            mode="markers",
            name=f"{nappe} ({len(d['lons'])})",
            marker=dict(size=5, color=d["couleur"], opacity=0.8),
            text=d["noms"],
            hovertemplate="<b>%{text}</b><br>Nappe: " + nappe + "<extra></extra>",
        ))

    fig.update_layout(
        mapbox=dict(style="open-street-map",center={"lat":14.5,"lon":-14.5},zoom=6),
        title="Forages du Sénégal — 4218 points d eau officiels (PNADT)",
        height=650,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="#0a0f1e",
        font_color="#e8f4fd",
        legend=dict(bgcolor="#0d1527",bordercolor="#2a4a7f",borderwidth=1,
                   title=dict(text="Type de nappe")),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Légende avec traits
    st.markdown("### Légende — Types de nappes")
    html = "<div style='display:flex;flex-wrap:wrap;gap:12px;padding:10px;background:#0d1527;border-radius:8px;'>"
    for nappe, couleur in COULEURS.items():
        nb = len(traces.get(nappe, {}).get("lons", []))
        html += f"""<div style='display:flex;align-items:center;gap:6px;'>
            <div style='width:12px;height:12px;border-radius:50%;background:{couleur};'></div>
            <span style='color:#e8f4fd;font-size:13px;'>{nappe} ({nb})</span>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # Stats
    st.markdown("---")
    st.markdown("### Statistiques des forages")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total forages", "4 218")
    c2.metric("Nappe principale", "Maastrichtien")
    c3.metric("Plus profonde", "300m (Maastrichtien)")
    c4.metric("Plus accessible", "Quaternaire (5-20m)")


LAYOUT = dict(paper_bgcolor="#0a0f1e", plot_bgcolor="#0d1527", font_color="#e8f4fd", margin=dict(t=40,b=20,l=10,r=10))

with st.sidebar:
    st.markdown("## 🌍 Navigation")
    page = st.radio("", [
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
    st.caption(f"📦 {nb:,} enregistrements - 46 communes")

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
    st.caption(f"Commune : **{selected_commune}** - Région : **{region}** - Scénario : **{selected_scenario}**")
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
        st.info(f"💧 **Début des pluies :** {cal.get('debut_pluies','N/A')} - **Hivernage :** {cal.get('hivernage','N/A')} - **Cultures :** {cal.get('cultures','N/A')}")
    st.markdown(f'<div class="info-card">💡 <b>Conseil :</b> {conseil}</div>', unsafe_allow_html=True)

elif page == "🌡️ Température":
    st.markdown(f"# 🌡️ Température — {selected_commune}")

    resolution = st.radio("Que voulez-vous voir ?", [
        "📅 Un jour précis",
        "📆 Mois par mois",
        "📊 Année par année"
    ], horizontal=True)

    df_proj = get_projections(selected_commune, selected_scenario)

    if resolution == "📅 Un jour précis":
        import datetime as dt
        from datetime import timedelta

        st.markdown("### 📅 Choisissez votre date")
        date_choisie = st.date_input(
            "Jour · Mois · Année",
            value=dt.date(2030, 6, 15),
            min_value=dt.date(2025, 1, 1),
            max_value=dt.date(2055, 12, 31),
            label_visibility="collapsed"
        )

        if df_proj is not None:
            df_jour = df_proj[df_proj["date"] == pd.Timestamp(date_choisie)]
            if not df_jour.empty:
                row = df_jour.iloc[0]
                tmin  = row["temp_min"]
                tmoy  = row["temp_mean"]
                tmax  = row["temp_max"]
                pluie = row["precip"]

                # Titre principal
                mois_fr = ["Janvier","Février","Mars","Avril","Mai","Juin",
                           "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
                date_str = f"{date_choisie.day} {mois_fr[date_choisie.month-1]} {date_choisie.year}"
                st.markdown(f"## 📅 {date_str} — {selected_commune}")
                st.markdown("---")

                # Températures matin / après-midi / nuit
                st.markdown("### 🕐 Températures de la journée")
                c1,c2,c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <div style='background:#1a2744;border-radius:12px;padding:20px;text-align:center;'>
                        <div style='font-size:40px;'>🌅</div>
                        <div style='color:#8ab4d4;font-size:14px;'>Matin (6h-10h)</div>
                        <div style='font-size:32px;font-weight:bold;color:#4db8ff;'>{tmin:.0f}°C</div>
                        <div style='color:#8ab4d4;font-size:12px;'>Température minimale</div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    couleur_aprem = "#ff4444" if tmax>=38 else "#FF9800" if tmax>=35 else "#ffd700"
                    st.markdown(f"""
                    <div style='background:#1a2744;border-radius:12px;padding:20px;text-align:center;'>
                        <div style='font-size:40px;'>🌞</div>
                        <div style='color:#8ab4d4;font-size:14px;'>Après-midi (12h-16h)</div>
                        <div style='font-size:32px;font-weight:bold;color:{couleur_aprem};'>{tmax:.0f}°C</div>
                        <div style='color:#8ab4d4;font-size:12px;'>Température maximale</div>
                    </div>""", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div style='background:#1a2744;border-radius:12px;padding:20px;text-align:center;'>
                        <div style='font-size:40px;'>🌙</div>
                        <div style='color:#8ab4d4;font-size:14px;'>Nuit (20h-6h)</div>
                        <div style='font-size:32px;font-weight:bold;color:#4db8ff;'>{(tmin-2):.0f}°C</div>
                        <div style='color:#8ab4d4;font-size:12px;'>Température nocturne</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Pluie
                st.markdown("### 🌧️ Pluie prévue ce jour")
                if pluie >= 20:
                    st.success(f"🌧️ **Forte pluie : {pluie:.1f} mm** — Bonne journée pour les cultures ! Pas besoin d arroser.")
                elif pluie >= 5:
                    st.info(f"🌦️ **Pluie modérée : {pluie:.1f} mm** — Les plantes seront bien arrosées naturellement.")
                elif pluie >= 1:
                    st.warning(f"🌂 **Petite pluie : {pluie:.1f} mm** — Insuffisant pour les cultures. Arrosage complémentaire conseillé.")
                else:
                    st.error(f"☀️ **Pas de pluie : {pluie:.1f} mm** — Pensez à arroser vos cultures.")

                st.markdown("---")

                # Message principal selon température
                st.markdown("### 💡 Que faire ce jour-là ?")
                if tmax >= 42:
                    st.markdown(f"""
                    <div style='background:#2d0a0a;border-left:6px solid #ff4444;border-radius:8px;padding:20px;'>
                        <h3 style='color:#ff4444;'>🔴 CHALEUR EXTRÊME — DANGER</h3>
                        <p style='color:#e8f4fd;font-size:16px;'>La température atteindra <b>{tmax:.0f}°C</b> ce jour à {selected_commune}.</p>
                        <ul style='color:#e8f4fd;font-size:15px;line-height:2;'>
                            <li>🚫 Ne travaillez PAS aux champs entre 10h et 18h</li>
                            <li>💧 Arrosez vos cultures très tôt le matin (avant 7h)</li>
                            <li>🐄 Mettez les animaux à l ombre avec de l eau fraîche</li>
                            <li>🧴 Protégez-vous du soleil si vous devez sortir</li>
                            <li>💊 Buvez beaucoup d eau — au moins 3 litres par jour</li>
                        </ul>
                    </div>""", unsafe_allow_html=True)
                elif tmax >= 38:
                    st.markdown(f"""
                    <div style='background:#2d1a0a;border-left:6px solid #FF9800;border-radius:8px;padding:20px;'>
                        <h3 style='color:#FF9800;'>🟠 JOURNÉE TRÈS CHAUDE — ATTENTION</h3>
                        <p style='color:#e8f4fd;font-size:16px;'>La température atteindra <b>{tmax:.0f}°C</b> ce jour à {selected_commune}.</p>
                        <ul style='color:#e8f4fd;font-size:15px;line-height:2;'>
                            <li>⏰ Travaillez aux champs tôt le matin (6h-10h) ou en soirée (17h-19h)</li>
                            <li>💧 Arrosez vos cultures le matin et le soir</li>
                            <li>🌿 Couvrez le sol avec de la paille pour garder l humidité</li>
                            <li>🐄 Surveillez vos animaux — donnez leur de l eau fraîche</li>
                            <li>💧 Buvez régulièrement de l eau</li>
                        </ul>
                    </div>""", unsafe_allow_html=True)
                elif tmax >= 35:
                    st.markdown(f"""
                    <div style='background:#2d2a0a;border-left:6px solid #ffd700;border-radius:8px;padding:20px;'>
                        <h3 style='color:#ffd700;'>🟡 JOURNÉE CHAUDE — NORMALE POUR LA SAISON</h3>
                        <p style='color:#e8f4fd;font-size:16px;'>La température atteindra <b>{tmax:.0f}°C</b> ce jour à {selected_commune}.</p>
                        <ul style='color:#e8f4fd;font-size:15px;line-height:2;'>
                            <li>✅ Vous pouvez travailler normalement aux champs</li>
                            <li>⏰ Évitez quand même les heures les plus chaudes (13h-15h)</li>
                            <li>💧 Arrosez le matin de préférence</li>
                            <li>🎯 Bonne journée pour semer ou planter</li>
                        </ul>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:#0a2d1a;border-left:6px solid #44ff88;border-radius:8px;padding:20px;'>
                        <h3 style='color:#44ff88;'>🟢 BONNE JOURNÉE — CONDITIONS FAVORABLES</h3>
                        <p style='color:#e8f4fd;font-size:16px;'>La température atteindra <b>{tmax:.0f}°C</b> ce jour à {selected_commune}.</p>
                        <ul style='color:#e8f4fd;font-size:15px;line-height:2;'>
                            <li>✅ Excellente journée pour travailler aux champs</li>
                            <li>🌱 Bonne journée pour semer, planter ou récolter</li>
                            <li>💧 Arrosez normalement selon vos habitudes</li>
                            <li>🐄 Vos animaux seront à l aise</li>
                        </ul>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("Données non disponibles pour cette date.")
        else:
            st.warning("Données de projection non disponibles.")

    elif resolution == "📆 Mois par mois":
        if df_proj is not None:
            df_m = agreger_mensuel(df_proj)
            st.markdown("### 📆 Températures mois par mois (2025-2055)")
            st.caption("Passez la souris sur le graphique pour voir les valeurs exactes")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_m["year_month"],y=df_m["temp_max"],
                name="Chaleur max (°C)",line=dict(color="#ff4444",width=1.5)))
            fig.add_trace(go.Scatter(x=df_m["year_month"],y=df_m["temp_mean"],
                name="Chaleur moyenne (°C)",line=dict(color="#ffd700",width=1.5)))
            fig.add_trace(go.Scatter(x=df_m["year_month"],y=df_m["temp_min"],
                name="Fraîcheur minimale (°C)",line=dict(color="#4db8ff",width=1.5)))
            fig.add_hline(y=38,line_dash="dash",line_color="red",
                annotation_text="⚠️ Seuil de chaleur dangereuse (38°C)")
            fig.update_layout(
                title=f"Évolution de la chaleur mois par mois · {selected_commune}",
                template="plotly_dark",**LAYOUT,
                xaxis_title="Mois et Année",
                yaxis_title="Température (°C)",
            )
            st.plotly_chart(fig,use_container_width=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("🌙 Nuit la plus fraîche",f"{df_m['temp_min'].min():.0f}°C")
            c2.metric("🌞 Chaleur moyenne",f"{df_m['temp_mean'].mean():.0f}°C")
            c3.metric("🔥 Journée la plus chaude",f"{df_m['temp_max'].max():.0f}°C")
        else:
            st.warning("Données non disponibles.")

    else:
        if df_proj is not None:
            df_a = agreger_annuel(df_proj)
            st.markdown("### 📊 Évolution de la chaleur année par année (2025-2055)")
            st.caption("Plus les années passent, plus il fera chaud")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_a["year"],y=df_a["temp_max"],
                name="Chaleur max (°C)",line=dict(color="#ff4444",width=2)))
            fig.add_trace(go.Scatter(x=df_a["year"],y=df_a["temp_mean"],
                name="Chaleur moyenne (°C)",line=dict(color="#ffd700",width=2)))
            fig.add_trace(go.Scatter(x=df_a["year"],y=df_a["temp_min"],
                name="Fraîcheur minimale (°C)",line=dict(color="#4db8ff",width=2)))
            fig.add_hline(y=38,line_dash="dash",line_color="red",
                annotation_text="⚠️ Seuil de chaleur dangereuse (38°C)")
            fig.update_layout(
                title=f"Comment la chaleur va évoluer à {selected_commune} d ici 2055",
                template="plotly_dark",**LAYOUT,
                xaxis_title="Année",
                yaxis_title="Température (°C)",
            )
            st.plotly_chart(fig,use_container_width=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("🌙 Nuit la plus fraîche",f"{df_a['temp_min'].min():.0f}°C")
            c2.metric("🌞 Chaleur en 2055",f"{df_a['temp_mean'].iloc[-1]:.0f}°C",
                      f"+{df_a['temp_mean'].iloc[-1]-df_a['temp_mean'].iloc[0]:.1f}°C vs 2025")
            c3.metric("🔥 Journée la plus chaude",f"{df_a['temp_max'].max():.0f}°C")

            # Tableau simple années dangereuses
            annees_chaudes = df_a[df_a["temp_max"]>=38]["year"].tolist()
            if annees_chaudes:
                st.markdown("### ⚠️ Années où il fera très chaud (T° > 38°C)")
                st.markdown("Ces années-là, faites très attention pendant les travaux agricoles :")
                cols = st.columns(min(len(annees_chaudes),6))
                for i,annee in enumerate(annees_chaudes[:6]):
                    cols[i%6].markdown(f"<div style='background:#2d0a0a;border-radius:8px;padding:10px;text-align:center;color:#ff4444;font-weight:bold;'>{annee}</div>",unsafe_allow_html=True)
            else:
                st.success('Pour ce scenario, les temperatures restent gerables.')
            df_m = agreger_mensuel(df_proj)
            if 'year_month' in df_m.columns:
                mois_chauds = df_m[df_m['temp_max']>=38][['year_month','temp_max']].head(10)
                if not mois_chauds.empty:
                    st.markdown('### Mois les plus caniculaires')
                    for _,row in mois_chauds.iterrows():
                        st.error('Mois ' + str(row['year_month']) + ' : ' + str(int(row['temp_max'])) + ' C — Ne travaillez pas aux champs en journee')
        else:
            st.warning("Données non disponibles.")

elif page == "🌧️ Précipitations":
    region, sol, cal, conseil = get_info(selected_commune)
    st.markdown(f"# 🌧️ Précipitations — {selected_commune}")
    if cal: st.info(f"📅 **Début des pluies :** {cal.get('debut_pluies','N/A')} - **Hivernage :** {cal.get('hivernage','N/A')}")
    df = get_annual(selected_commune, selected_scenario)
    if not df.empty:
        fig = px.bar(df,x="year",y="precip_total",title=f"Précipitations annuelles (mm) - {selected_commune}",color="precip_total",color_continuous_scale=["#ff4444","#ffd700","#4db8ff"],template="plotly_dark")
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
        st.markdown("### Comment la secheresse va evoluer a " + selected_commune + " d ici 2055")
        st.caption("La ligne monte vers le rouge = la secheresse devient plus severe. En dessous de 0.3 = normal. Au dessus de 0.6 = danger.")
        fig = px.line(df,x="year",y="drought",title="Evolution de la secheresse (0=normal, 1=severe)",color_discrete_sequence=["#ffd700"],template="plotly_dark")
        fig.add_hline(y=0.3,line_dash="dot",line_color="orange",annotation_text="Attention : commence a secher")
        fig.add_hline(y=0.6,line_dash="dash",line_color="red",annotation_text="DANGER : secheresse critique")
        fig.update_layout(**LAYOUT,xaxis_title="Annee",yaxis_title="Niveau de secheresse (0=normal, 1=severe)")
        st.plotly_chart(fig,use_container_width=True)
        drought_2025 = df["drought"].iloc[0]
        drought_2055 = df["drought"].iloc[-1]
        hausse = drought_2055 - drought_2025
        if drought_2055 >= 0.6:
            niveau = "CRITIQUE"
            couleur = "error"
        elif drought_2055 >= 0.3:
            niveau = "MODERE"
            couleur = "warning"
        else:
            niveau = "NORMAL"
            couleur = "success"
        texte = (
            "**Comment lire ce graphique ?**\n\n"
            "La ligne jaune montre comment la secheresse va evoluer a " + selected_commune + " entre 2025 et 2055. "
            "Plus la ligne monte, plus la secheresse sera severe.\n\n"
            "**Situation en 2025 :** niveau de secheresse a " + f"{drought_2025:.2f}" + " sur 1.\n\n"
            "**Situation en 2055 :** niveau prevu a " + f"{drought_2055:.2f}" + " sur 1 — niveau " + niveau + ".\n\n"
            "**Hausse prevue :** +" + f"{hausse:.2f}" + " points d ici 2055.\n\n"
            "**Les 2 lignes de seuil :**\n"
            "- Ligne orange pointillee (0.3) : a partir de ce niveau, les agriculteurs doivent commencer a economiser l eau et adapter leurs cultures.\n"
            "- Ligne rouge tiretee (0.6) : niveau critique — risque serieux de perte de recolte et de manque d eau pour les animaux.\n\n"
            "**Ce que cela signifie pour vous :**\n"
        )
        if drought_2055 >= 0.6:
            texte += (
                "- La situation sera tres difficile a " + selected_commune + " d ici 2055.\n"
                "- Commencez des maintenant a prevoir des cultures resistantes a la secheresse comme le mil et le sorgho.\n"
                "- Construisez ou renforcez vos reserves d eau (citernes, bassins).\n"
                "- Renseignez-vous aupres de l ANACIM et des services agricoles locaux pour des aides."
            )
        elif drought_2055 >= 0.3:
            texte += (
                "- La secheresse sera moderee mais il faut s y preparer.\n"
                "- Privilegiez les varietes de cultures adaptees a la chaleur et au manque de pluie.\n"
                "- Surveillez le niveau de vos puits et forages chaque annee."
            )
        else:
            texte += (
                "- La situation reste geerable pour ce scenario.\n"
                "- Continuez vos pratiques agricoles habituelles en restant vigilant.\n"
                "- Suivez les alertes meteo de l ANACIM chaque saison."
            )
        if couleur == "error":
            st.error(texte)
        elif couleur == "warning":
            st.warning(texte)
        else:
            st.success(texte)
        if df["spi"].notna().any():
            st.markdown("### Les pluies seront-elles suffisantes ?")
            st.caption("Barres bleues = bonnes pluies. Barres rouges = manque de pluie. Plus les barres rouges sont grandes, plus c est sec.")
            fig2 = px.bar(df,x="year",y="spi",title="Deficit de pluie annee par annee (barres rouges = manque de pluie)",color="spi",color_continuous_scale=["#ff4444","#ffffff","#4db8ff"],template="plotly_dark")
            fig2.update_layout(**LAYOUT,xaxis_title="Annee",yaxis_title="Niveau de pluie (positif=abondant, negatif=deficit)")
            st.plotly_chart(fig2,use_container_width=True)
        spi_moy = df["spi"].mean() if df["spi"].notna().any() else 0
        st.markdown("---")
        st.markdown("### Que dit le SPI pour votre commune ?")
        if spi_moy > 0:
            st.success("Bonne saison des pluies prevue. Semez et plantez normalement.")
        elif spi_moy > -0.2:
            st.warning("Legèrement sec. Surveillez vos reserves.")
        elif spi_moy > -0.5:
            st.error("Secheresse moderee. Plantez mil et sorgho uniquement.")
        else:
            st.error("SECHERESSE SEVERE. Protegez vos reserves d eau.")
        with st.expander("Cest quoi le SPI ? Cliquez pour comprendre"):
            st.markdown("""
### Le SPI en langage simple

Le **SPI** (Indice de Precipitation Standardise) est un chiffre qui dit si les pluies sont normales, trop faibles ou trop fortes par rapport aux 30 dernieres annees dans votre region.

---

### Comment lire le chiffre ?

| Valeur SPI | Signification | Couleur |
|---|---|---|
| superieur a +1 | Pluies tres abondantes | Vert fonce |
| 0 a +1 | Pluies normales ou bonnes | Vert |
| 0 a -0.5 | Legerement sec | Jaune |
| -0.5 a -1 | Secheresse moderee | Orange |
| inferieur a -1 | Secheresse severe | Rouge |

---

### La formule utilisee

SPI = (pluies de cette annee - moyenne historique) divise par ecart-type

- Si les pluies de cette annee sont superieures a la moyenne : SPI positif
- Si les pluies de cette annee sont inferieures a la moyenne : SPI negatif
- Plus le chiffre est negatif, plus la secheresse est severe

---

### Exemple concret

Kaolack recoit normalement 600 mm de pluie par an.
- Si en 2040 il tombe 750 mm : SPI = +1.25 (bonne annee)
- Si en 2040 il tombe 450 mm : SPI = -1.25 (secheresse moderee)
- Si en 2040 il tombe 300 mm : SPI = -2.5 (secheresse severe)

Saint-Louis recoit normalement 280 mm par an.
- Meme si il tombe peu de pluie, si cest normal pour Saint-Louis, le SPI reste proche de 0.

---

### A quoi ca sert concretement ?

- Savoir a lavance si la saison sera bonne ou mauvaise
- Decider quoi planter selon la quantite deau disponible
- Gerer les reserves deau des puits, forages et mares
- Alerter les autorites avant une crise de secheresse

---

### Sources des donnees

- **ANACIM** : Agence Nationale de lAviation Civile et de la Meteorologie du Senegal
- **NASA POWER** : donnees satellitaires mondiales
- **Copernicus ERA5** : service meteorologique europeen
- Modeles climatiques SSP1-1.9, SSP2-4.5, SSP5-8.5
            """)
        annees = df[df["drought"]>0.6]["year"].tolist()
        if annees: st.error(f"⚠️ Années sécheresse sévère projetées : {', '.join(map(str,annees))}")

elif page == "💧 Ressources en eau":
    afficher_section_hydraulique(selected_commune, selected_scenario)

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
        fig = px.scatter_mapbox(df_map,lat="latitude",lon="longitude",hover_name="commune_name",hover_data={"region":True,variable:True,"latitude":False,"longitude":False},color=variable,color_continuous_scale=cscales[variable],size_max=18,zoom=5.5,center={"lat":14.5,"lon":-14.5},mapbox_style="open-street-map",title=f"{labels[variable]} - {year} - {selected_scenario}")
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
    fig.update_layout(title=f"Comparaison - {selected_commune}",template="plotly_dark",**LAYOUT,legend=dict(bgcolor="#0d1527",bordercolor="#2a4a7f"))
    st.plotly_chart(fig,use_container_width=True)
    if summary: st.dataframe(pd.DataFrame(summary),use_container_width=True)

elif page == "💧 Réseau Hydraulique":
    st.markdown("# 💧 Ressources en Eau du Sénégal")
    sous_page = st.radio("", ["🗺️ Réseau hydrographique","🔵 Forages officiels (4218)","📊 Ressources par commune"], horizontal=True)

    if sous_page == "🗺️ Réseau hydrographique":
        afficher_carte_hydrographie(selected_scenario)
    elif sous_page == "🔵 Forages officiels (4218)":
        st.markdown("### 🔵 Carte des 4218 forages officiels du Sénégal")
        st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")
        afficher_carte_forages()
    else:
        afficher_section_hydraulique(selected_commune, selected_scenario)

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


