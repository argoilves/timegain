import streamlit as st
import math

# --- LEHE SEADISTUSED ---
st.set_page_config(
    page_title="Ajavõidu kalkulaator",
    page_icon="🚗",
    layout="centered"
)

# --- CSS STIILID ---
st.markdown("""
<style>
    /* 1. ÜLDINE DISAIN (SUNNIME HELEDA TEEMA) */
    .stApp {
        background-color: #f4f4f9;
        color: #333333;
    }
    
    /* Sisendite sildid tumedaks */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
        color: #333333 !important;
        font-weight: bold;
    }
    
    /* 2. PARANDUS: EXPANDER (DETAILVAADE) HELEDAKS */
    [data-testid="stExpanderDetails"] {
        background-color: #f8f9fa !important;
        color: #333333 !important;
        border-radius: 8px;
    }
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border-radius: 8px;
        color: #333333 !important;
    }
    .streamlit-expanderHeader {
        color: #333333 !important;
        font-weight: bold;
    }
    /* Sundida markdown teksti expanderi sees tumedaks */
    [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li {
        color: #333333 !important;
    }

    /* Nuppude stiil */
    div.stButton > button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 10px;
        font-size: 16px;
    }
    div.stButton > button:hover {
        background-color: #ff3333;
        color: white;
    }

    /* 3. RISKIKAARTIDE STIIL */
    .risk-container {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 20px;
        margin-top: 20px;
    }
    .risk-box {
        flex: 1;
        min-width: 120px;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        background-color: #e0f7fa;
        border: 1px solid #0097a7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #333 !important;
    }
    .risk-icons {
        font-size: 2em;
        margin-bottom: 5px;
        line-height: 1;
    }
    .risk-title {
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 5px;
        display: block;
        color: #555;
    }
    .risk-val {
        font-size: 1.6em;
        font-weight: bold;
        color: #333;
    }
    
    /* Ikoonide pööramine */
    .flipped {
        display: inline-block;
        transform: scaleX(-1);
    }

    /* 4. VISUAALNE GRAAFIK (RIBA) - SUURENDATUD KÕRGUST JA PAIGUTUST */
    .bar-wrapper {
        position: relative;
        width: 100%;
        height: 160px; /* Suurendatud, et tekstid ei kattuks */
        background: #eeeeee;
        border-radius: 8px;
        margin-top: 20px;
        overflow: hidden;
        border: 1px solid #ccc;
        color: #333;
    }
    .bar-header {
        position: absolute;
        top: 10px;
        left: 0;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: #777;
        font-weight: bold;
    }
    .bar-container {
        position: absolute;
        bottom: 30px; /* Liigutatud allapoole */
        left: 0;
        width: 100%;
        height: 50px;
        background: #ddd;
        border-radius: 4px;
    }
    .bar-segment {
        height: 100%;
        position: absolute;
        top: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.8em;
        white-space: nowrap;
        overflow: hidden;
        box-shadow: 1px 0 2px rgba(0,0,0,0.2);
        transition: width 0.5s ease;
    }
    .icon-marker {
        position: absolute;
        bottom: 85px; /* Liigutatud allapoole koos ribaga */
        font-size: 24px;
        transform: translateX(-50%);
        text-align: center;
        line-height: 1;
        transition: left 0.5s ease;
        z-index: 10;
        color: #333;
    }
    .reaction-line {
        position: absolute;
        top: 35px; /* Liigutatud allapoole pealkirjast eemale */
        bottom: 30px;
        width: 2px;
        background-color: rgba(0,0,0,0.3);
        z-index: 5;
        border-right: 1px dashed white;
    }
    .reaction-label {
        position: absolute;
        top: 35px; /* Liigutatud allapoole */
        font-size: 10px;
        color: #666;
        padding-left: 4px;
    }

    /* 5. ALUMISED INFO-RIBAD */
    .alert-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: bold;
        text-align: center;
        color: #333 !important;
    }
    .alert-green { background-color: #d4edda; border: 1px solid #c3e6cb; }
    .alert-red { background-color: #f8d7da; border: 1px solid #f5c6cb; }
    .alert-yellow { background-color: #fff3cd; border: 1px solid #ffeeba; }
</style>
""", unsafe_allow_html=True)

# --- FÜÜSIKA JA ARVUTUSED ---

DECELERATION_MULTIPLIERS = {
    "dryAsphalt": {"good": 7, "worn": 6, "very_worn": 5},
    "wetAsphalt": {"good": 4.5, "worn": 3.5, "very_worn": 2.5},
    "gravel": {"good": 3.5, "worn": 2.8, "very_worn": 2},
    "snow": {"good": 1.5, "worn": 1, "very_worn": 0.7},
    "ice": {"good": 0.5, "worn": 0.3, "very_worn": 0.1}
}

FATALITY_RISK_DATA = {
    'pedestrian': [(0, 0), (10, 1), (20, 5), (30, 15), (40, 35), (50, 65), (60, 90), (70, 98), (80, 100), (110, 100)],
    'sideImpact': [(0, 0), (20, 1), (30, 2), (40, 5), (50, 15), (60, 40), (70, 70), (80, 90), (90, 98), (100, 100), (110, 100)],
    'headOn': [(0, 0), (40, 1), (50, 2), (60, 5), (70, 10), (80, 25), (90, 50), (100, 75), (110, 100)]
}

def kmh_to_ms(kmh): return kmh * 1000 / 3600
def ms_to_kmh(ms): return ms * 3600 / 1000

def get_deceleration(road, tire):
    return 9.81 * (DECELERATION_MULTIPLIERS[road][tire] / 10)

def calculate_stopping_distance(speed_kmh, road, tire, reaction_time):
    if speed_kmh <= 0: return 0, 0, 0, 0
    speed_ms = kmh_to_ms(speed_kmh)
    decel = get_deceleration(road, tire)
    reaction_dist = speed_ms * reaction_time
    braking_dist = (speed_ms ** 2) / (2 * decel)
    total_dist = reaction_dist + braking_dist
    total_time = reaction_time + (speed_ms / decel)
    return reaction_dist, braking_dist, total_dist, total_time

def calculate_collision_speed(init_speed_kmh, obstacle_dist, road, tire, reaction_time):
    if init_speed_kmh <= 0: return 0
    init_speed_ms = kmh_to_ms(init_speed_kmh)
    decel = get_deceleration(road, tire)
    reaction_dist = init_speed_ms * reaction_time
    dist_after_reaction = obstacle_dist - reaction_dist
    
    if obstacle_dist <= reaction_dist: return init_speed_kmh
    speed_squared = (init_speed_ms ** 2) - (2 * decel * dist_after_reaction)
    if speed_squared <= 0: return 0
    return ms_to_kmh(math.sqrt(speed_squared))

def get_fatality_risk(speed, risk_type):
    data = FATALITY_RISK_DATA[risk_type]
    speed = min(speed, data[-1][0])
    if speed <= 0: return 0
    if speed >= data[-1][0]: return data[-1][1]
    for i in range(len(data) - 1):
        v1, r1 = data[i]
        v2, r2 = data[i+1]
        if v1 <= speed <= v2:
            return r1 + (speed - v1) * (r2 - r1) / (v2 - v1)
    return data[-1][1]

# --- UI ---

st.title("Ajavõidu kalkulaator")

if 'show_results' not in st.session_state:
    st.session_state.show_results = False

col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("Läbitav vahemaa (km)", value=10.0, step=0.1, min_value=0.1)
    allowed_speed = st.number_input("Lubatud sõidukiirus (km/h)", value=30, step=1, min_value=1)
    road_key = st.selectbox("Teeolud", options=["dryAsphalt", "wetAsphalt", "gravel", "snow", "ice"], 
                            format_func=lambda x: {"dryAsphalt": "Kuiv asfalt", "wetAsphalt": "Märg asfalt", "gravel": "Kruus", "snow": "Lumi", "ice": "Jää"}[x])

with col2:
    reaction_time = st.number_input("Reageerimisaeg (s)", value=1.0, step=0.1, min_value=0.1)
    actual_speed = st.number_input("Keskmine reaalne sõidukiirus (km/h)", value=50, step=1, min_value=1)
    tire_key = st.selectbox("Rehvide seisukord", options=["good", "worn", "very_worn"], 
                            format_func=lambda x: {"good": "Head", "worn": "Kulunud", "very_worn": "Väga kulunud"}[x])

obstacle_dist = st.number_input("Kaugus takistusest (m)", value=25.0, step=1.0, min_value=0.0)

st.write("") 

if st.button("Arvuta"):
    st.session_state.show_results = True

# --- TULEMUSED ---
if st.session_state.show_results:
    
    # Arvutused
    time_gain_min = (distance/allowed_speed - distance/actual_speed) * 60
    
    r_dist_all, b_dist_all, total_dist_allowed, time_all = calculate_stopping_distance(allowed_speed, road_key, tire_key, reaction_time)
    r_dist_act, b_dist_act, total_dist_actual, time_act = calculate_stopping_distance(actual_speed, road_key, tire_key, reaction_time)
    
    excess_dist = max(0, total_dist_actual - total_dist_allowed)
    coll_speed = calculate_collision_speed(actual_speed, obstacle_dist, road_key, tire_key, reaction_time)
    
    # Riskid
    risk_ped = int(get_fatality_risk(coll_speed, 'pedestrian'))
    risk_head = int(get_fatality_risk(coll_speed, 'headOn'))
    risk_side = int(get_fatality_risk(coll_speed, 'sideImpact'))
    
    st.markdown("---")

    # 1. AJAVÕIT
    time_gain_msg = ""
    bg_class = "alert-yellow"
    if time_gain_min > 0.01:
        time_gain_msg = f"🚗 Säästate aega: {time_gain_min:.1f} min"
        bg_class = "alert-green"
    elif time_gain_min < -0.01:
        time_gain_msg = f"🚗 Kaotate aega: {abs(time_gain_min):.1f} min"
        bg_class = "alert-red"
    else:
        time_gain_msg = "🚗 Ajavõitu ega kaotust pole."

    st.markdown(f'<div class="alert-box {bg_class}">{time_gain_msg}</div>', unsafe_allow_html=True)

    # 2. RISKIKAARDID
    def get_risk_color(val):
        if val == 0: return "#28a745"
        if val < 50: return "#ffc107"
        return "#dc3545"

    risk_html = f"""
    <div class="risk-container">
        <div class="risk-box">
            <div class="risk-icons"><span class="flipped">🚶</span>💥🚗</div>
            <span class="risk-title">Jalakäija:</span>
            <div class="risk-val" style="color: {get_risk_color(risk_ped)}">{risk_ped}%</div>
        </div>
        <div class="risk-box">
            <div class="risk-icons"><span class="flipped">🚗</span>💥🚗</div>
            <span class="risk-title">Laupkokkupõrge:</span>
            <div class="risk-val" style="color: {get_risk_color(risk_head)}">{risk_head}%</div>
        </div>
        <div class="risk-box">
            <div class="risk-icons">🚘💥🚗</div>
            <span class="risk-title">Külgkokkupõrge:</span>
            <div class="risk-val" style="color: {get_risk_color(risk_side)}">{risk_side}%</div>
        </div>
    </div>
    """
    st.markdown(risk_html, unsafe_allow_html=True)

    # 3. MODAL / DETAILVAADE
    with st.expander("ℹ️ Detailne arvutuskäik"):
        road_name = {"dryAsphalt": "Kuiv asfalt", "wetAsphalt": "Märg asfalt", "gravel": "Kruus", "snow": "Lumi", "ice": "Jää"}[road_key]
        tire_name = {"good": "Head", "worn": "Kulunud", "very_worn": "Väga kulunud"}[tire_key]
        decel_val = get_deceleration(road_key, tire_key)

        st.markdown(f"""
        **Reageerimine ja Pidurdus:**
        * Reageerimisaeg: {reaction_time} s
        * Aeglustus ({road_name}, {tire_name} rehvid): {decel_val:.2f} m/s²
        
        **Lubatud kiirus ({allowed_speed} km/h):**
        * Reageerimisteekond: {r_dist_all:.1f} m
        * Pidurdusteekond: {b_dist_all:.1f} m
        * **Peatumisteekond kokku: {total_dist_allowed:.1f} m**
        
        **Tegelik kiirus ({actual_speed} km/h):**
        * Reageerimisteekond: {r_dist_act:.1f} m
        * Pidurdusteekond: {b_dist_act:.1f} m
        * **Peatumisteekond kokku: {total_dist_actual:.1f} m**
        
        **Kokkupõrke analüüs:**
        * Takistus on {obstacle_dist} m kaugusel.
        * Tegelikul kiirusel on kokkupõrke kiirus **{coll_speed:.1f} km/h**.
        """)

    # 4. GRAAFILINE RIBA
    # Arvutame skaala
    max_scale = max(total_dist_actual, total_dist_allowed, obstacle_dist, 1) * 1.15
    def pct(val): return (val / max_scale) * 100
    
    # Ikoonide asukohad
    final_car_dist = min(total_dist_actual, obstacle_dist) if coll_speed > 0 else total_dist_actual
    car_pos = pct(final_car_dist)
    ped_pos = pct(obstacle_dist)
    
    # Ribade laiused
    bar1_width = pct(total_dist_allowed)
    bar2_width = pct(excess_dist)
    bar2_left = bar1_width 
    
    if total_dist_actual < total_dist_allowed:
        bar1_width = pct(total_dist_actual)
        bar2_width = 0

    # Konstrueerime HTML-i ühes reas või kasutame hoolikalt taandeid, et vältida "koodiploki" efekti
    # Tekstide kuvamise loogika: näita ainult siis, kui riba on piisavalt lai
    bar1_text = f"{total_dist_allowed:.1f}m" if bar1_width > 12 else ""
    bar2_text = f"+{excess_dist:.1f}m" if bar2_width > 12 else ""

    # Ehitame HTML stringi nii, et ei tekiks probleeme taanetega
    bar_html = f"""
    <div class="bar-wrapper">
        <div class="bar-header">Peatumisteekonna visualiseering</div>
        
        <div class="icon-marker" style="left: {ped_pos}%;">
            <span class="flipped" style="display:inline-block;">🚶</span><br>
            <span style="font-size: 12px; font-weight:bold;">{obstacle_dist:.1f}m</span>
        </div>
        
        <div class="icon-marker" style="left: {car_pos}%; z-index: 12;">
            <span class="flipped" style="display:inline-block;">🚗</span>
        </div>

        <div class="bar-container">
            <div class="bar-segment" style="width: {bar1_width}%; background-color: #28a745; left: 0;">{bar1_text}</div>
            <div class="bar-segment" style="width: {bar2_width}%; background-color: #dc3545; left: {bar2_left}%;">{bar2_text}</div>
        </div>
        
        <div class="reaction-line" style="left: {pct(r_dist_act)}%;"></div>
        <div class="reaction-label" style="left:{pct(r_dist_act) + 1}%;">Reageerimine ({r_dist_act:.1f}m)</div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)
    
    # 5. ALUMISED HOIATUSED
    st.write("") 
    
    if coll_speed > 0:
        st.markdown(f'<div class="alert-box alert-red">💥 Kokkupõrge kiirusel {coll_speed:.0f} km/h</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-box alert-green">✅ Sõiduk peatus enne takistust.</div>', unsafe_allow_html=True)
    
    if excess_dist > 0:
        st.markdown(f'<div class="alert-box alert-yellow">Kiiruse ületamisest tingitud lisamaa: +{excess_dist:.1f} meetrit</div>', unsafe_allow_html=True)
