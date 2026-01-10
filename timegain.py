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
    /* 1. ÜLDINE DISAIN */
    .stApp {
        background-color: #f4f4f9;
        color: #333333;
    }
    
    /* 2. TEKSTIVÄLJAD JA RIPPMENÜÜD VALGEKS (AGRESSIIVNE FIX) */
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    input.st-ai, input.st-ah {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #cccccc !important;
    }
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    li[data-baseweb="option"],
    div[role="option"] {
        background-color: #ffffff !important;
        color: #333333 !important;
    }
    li[data-baseweb="option"]:hover,
    li[data-baseweb="option"][aria-selected="true"],
    div[role="option"]:hover,
    div[role="option"][aria-selected="true"] {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    div[data-testid="stSelectbox"] div[class*="singleValue"] {
        color: #000000 !important;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #333333 !important;
        font-weight: bold;
    }

    /* 3. VISUAALNE GRAAFIK */
    .bar-wrapper {
        position: relative;
        width: 100%;
        height: 220px;
        background: #eeeeee;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 20px;
        overflow: hidden;
        border: 1px solid #ccc;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .bar-header {
        position: absolute;
        top: 10px;
        left: 0;
        width: 100%;
        text-align: center;
        font-size: 14px;
        color: #555;
        font-weight: bold;
        z-index: 20;
    }

    /* IKOONID */
    .icon-base {
        position: absolute;
        bottom: 95px; 
        font-size: 28px;
        transform: translateX(-50%);
        text-align: center;
        line-height: 1;
        width: 60px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* JALAKÄIJA */
    .pedestrian-wrapper {
        z-index: 5;
    }
    
    /* Jalakäija ikoon - ALATI PÜSTI */
    .ped-icon-inner {
        display: inline-block;
        transition: color 0.2s ease-in;
        font-size: 28px;
    }
    
    /* Ainult värv muutub, kui pihta saab */
    .ped-hit {
        color: #d32f2f; /* Veripunane */
        /* transform: rotate(90deg);  <-- SEE RIDA EEMALDATUD */
    }
    
    /* JALAKÄIJA TEKST */
    .ped-label {
        font-size: 12px;
        font-weight: bold;
        color: #333;
        white-space: nowrap;
        margin-bottom: 2px;
        z-index: 30;
    }

    /* AUTO - ANIMEERITUD (LINEAR SÜNKROONIKS) */
    .car-icon {
        left: 0;
        animation: moveCar var(--anim-duration) linear forwards;
        animation-delay: var(--start-delay);
        z-index: 20; 
    }
    @keyframes moveCar {
        from { left: 0; }
        to { left: var(--target-left); }
    }

    /* RIBADE KONTEINER */
    .bar-container {
        position: absolute;
        bottom: 40px; 
        left: 0;
        width: 100%;
        height: 50px;
        background: #ddd;
        border-radius: 4px;
        overflow: hidden;
    }

    /* ROHELINE RIBA */
    .bar-green {
        height: 100%;
        position: absolute;
        left: 0;
        top: 0;
        background-color: #28a745;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 5px;
        color: white;
        font-weight: bold;
        font-size: 0.9em;
        white-space: nowrap;
        width: 0;
        
        /* LINEAR tagab ideaalse sünkrooni autoga */
        animation: growGreen var(--green-duration) linear forwards;
        animation-delay: var(--start-delay);
    }
    @keyframes growGreen {
        to { width: var(--green-width); }
    }

    /* PUNANE RIBA */
    .bar-red {
        height: 100%;
        position: absolute;
        left: var(--green-width);
        top: 0;
        background-color: #dc3545;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.9em;
        white-space: nowrap;
        width: 0;
        
        /* LINEAR tagab ideaalse sünkrooni autoga */
        animation: growRed var(--red-duration) linear forwards;
        animation-delay: calc(var(--start-delay) + var(--green-duration));
    }
    @keyframes growRed {
        to { width: var(--red-width); }
    }

    /* REAGEERIMISE JOON JA TEKST - STAATILISED */
    .reaction-line {
        position: absolute;
        top: 40px;
        bottom: 40px;
        width: 2px;
        background-color: rgba(0,0,0,0.4);
        z-index: 5;
        border-right: 1px dashed white;
    }
    
    .reaction-label {
        position: absolute;
        top: 45px;
        font-size: 11px;
        color: #444;
        padding-left: 6px;
        font-weight: bold;
    }

    .flipped {
        display: inline-block;
        transform: scaleX(-1);
    }

    /* ALUMISED KASTID */
    .alert-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: bold;
        text-align: center;
        color: #333 !important;
        font-size: 1.1em;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .alert-green { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724 !important;}
    .alert-red { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24 !important;}
    .alert-yellow { background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404 !important;}

    /* RISKIKAARDID */
    .risk-container { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; margin-top: 20px; }
    .risk-box { flex: 1; min-width: 120px; padding: 15px; border-radius: 8px; text-align: center; background-color: #e0f7fa; border: 1px solid #0097a7; box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #333 !important; }
    .risk-icons { font-size: 2em; margin-bottom: 5px; line-height: 1; }
    .risk-title { font-weight: bold; font-size: 0.9em; margin-bottom: 5px; display: block; color: #555; }
    .risk-val { font-size: 1.6em; font-weight: bold; color: #333; }

    /* EXPANDER */
    .streamlit-expanderContent { background-color: #ffffff !important; color: #333333 !important; border: 1px solid #ddd; }
    .streamlit-expanderHeader { background-color: #f0f0f0 !important; color: #333333 !important; font-weight: bold; }
    .streamlit-expanderContent p, .streamlit-expanderContent li { color: #333333 !important; }
    
    div.stButton > button { width: 100%; background-color: #ff4b4b; color: white; border: none; padding: 12px; font-size: 18px; font-weight: bold; border-radius: 8px; margin-bottom: 20px; }
    div.stButton > button:hover { background-color: #ff3333; color: white; }
</style>
""", unsafe_allow_html=True)

# --- ARVUTUSED ---
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
def get_deceleration(road, tire): return 9.81 * (DECELERATION_MULTIPLIERS[road][tire] / 10)

def calculate_stopping_distance(speed_kmh, road, tire, reaction_time):
    if speed_kmh <= 0: return 0, 0, 0, 0
    speed_ms = kmh_to_ms(speed_kmh)
    decel = get_deceleration(road, tire)
    reaction_dist = speed_ms * reaction_time
    braking_dist = (speed_ms ** 2) / (2 * decel)
    return reaction_dist, braking_dist, reaction_dist + braking_dist, reaction_time + (speed_ms / decel)

def calculate_collision_speed(init_speed_kmh, obstacle_dist, road, tire, reaction_time):
    if init_speed_kmh <= 0: return 0
    init_speed_ms = kmh_to_ms(init_speed_kmh)
    decel = get_deceleration(road, tire)
    reaction_dist = init_speed_ms * reaction_time
    dist_after_reaction = obstacle_dist - reaction_dist
    if obstacle_dist <= reaction_dist: return init_speed_kmh
    speed_squared = (init_speed_ms ** 2) - (2 * decel * dist_after_reaction)
    return ms_to_kmh(math.sqrt(speed_squared)) if speed_squared > 0 else 0

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

if 'run_id' not in st.session_state:
    st.session_state.run_id = 0

col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("Läbitav vahemaa (km)", value=10.0, step=0.1, min_value=0.1)
    allowed_speed = st.number_input("Lubatud sõidukiirus (km/h)", value=30, step=1, min_value=1)
    road_key = st.selectbox("Teeolud", options=["dryAsphalt", "wetAsphalt", "gravel", "snow", "ice"], format_func=lambda x: {"dryAsphalt": "Kuiv asfalt", "wetAsphalt": "Märg asfalt", "gravel": "Kruus", "snow": "Lumi", "ice": "Jää"}[x])

with col2:
    reaction_time = st.number_input("Reageerimisaeg (s)", value=1.0, step=0.1, min_value=0.1)
    actual_speed = st.number_input("Keskmine reaalne sõidukiirus (km/h)", value=50, step=1, min_value=1)
    tire_key = st.selectbox("Rehvide seisukord", options=["good", "worn", "very_worn"], format_func=lambda x: {"good": "Head", "worn": "Kulunud", "very_worn": "Väga kulunud"}[x])

obstacle_dist = st.number_input("Kaugus takistusest (m)", value=25.0, step=1.0, min_value=0.0)

st.write("") 
if st.button("Arvuta"):
    st.session_state.run_id += 1 

# --- TULEMUSED ---
if st.session_state.run_id > 0:
    
    # Arvutused
    time_gain_min = (distance/allowed_speed - distance/actual_speed) * 60
    r_dist_all, b_dist_all, total_dist_allowed, time_all = calculate_stopping_distance(allowed_speed, road_key, tire_key, reaction_time)
    r_dist_act, b_dist_act, total_dist_actual, time_act = calculate_stopping_distance(actual_speed, road_key, tire_key, reaction_time)
    excess_dist = max(0, total_dist_actual - total_dist_allowed)
    coll_speed = calculate_collision_speed(actual_speed, obstacle_dist, road_key, tire_key, reaction_time)
    
    risk_ped = int(get_fatality_risk(coll_speed, 'pedestrian'))
    risk_head = int(get_fatality_risk(coll_speed, 'headOn'))
    risk_side = int(get_fatality_risk(coll_speed, 'sideImpact'))
    
    # --- ANIMATSIOONI PARAMEETRID ---
    max_scale = max(total_dist_actual, total_dist_allowed, obstacle_dist, 1) * 1.15
    def pct(val): return (val / max_scale) * 100
    
    # Auto sihtmärk
    final_car_dist = total_dist_actual
    
    # Asukohad (%)
    car_target_pct = pct(final_car_dist)
    ped_target_pct = pct(obstacle_dist)
    react_line_pct = pct(r_dist_act) 
    
    # Ribade laiused (%)
    green_bar_width = pct(total_dist_allowed)
    if total_dist_actual < total_dist_allowed:
        green_bar_width = pct(total_dist_actual)
        red_bar_width = 0
    else:
        red_bar_width = pct(excess_dist)

    # Ajastused (Sekundites) - LINEARNE LIIKUMINE SÜNKROONIKS
    ANIM_DURATION = 4.0 
    START_DELAY = 0.5 
    
    total_travel_dist = final_car_dist
    if total_travel_dist <= 0: total_travel_dist = 1
    
    green_ratio = min(1.0, total_dist_allowed / total_travel_dist)
    green_duration = ANIM_DURATION * green_ratio
    
    red_duration = 0
    if total_travel_dist > total_dist_allowed:
        red_duration = ANIM_DURATION * (1.0 - green_ratio)

    bar1_text = f"{total_dist_allowed:.1f}m" if green_bar_width > 12 else ""
    bar2_text = f"+{excess_dist:.1f}m" if red_bar_width > 12 else ""
    
    animation_key = st.session_state.run_id

    # Jalakäija stiil: kas sai pihta? (Ainult värvimuutus, ei kuku pikali)
    ped_inner_class = "ped-icon-inner"
    if coll_speed > 0:
        ped_inner_class += " ped-hit"

    # --- HTML GENEREERIMINE ---
    bar_html = f"""<div class="bar-wrapper" key="{animation_key}" style="--anim-duration: {ANIM_DURATION}s; --start-delay: {START_DELAY}s; --green-duration: {green_duration}s; --red-duration: {red_duration}s; --green-width: {green_bar_width}%; --red-width: {red_bar_width}%; --target-left: {car_target_pct}%;"><div class="bar-header">Peatumisteekonna visualiseering</div><div class="icon-base pedestrian-wrapper" style="left: {ped_target_pct}%;"><span class="ped-label">{obstacle_dist:.1f}m</span><span class="{ped_inner_class}"><span class="flipped" style="display:inline-block;">🚶</span></span></div><div class="icon-base car-icon"><span class="flipped" style="display:inline-block;">🚗</span></div><div class="bar-container"><div class="bar-green">{bar1_text}</div><div class="bar-red">{bar2_text}</div></div><div class="reaction-line" style="left: {react_line_pct}%;"></div><div class="reaction-label" style="left: {react_line_pct}%;">Reageerimine ({r_dist_act:.1f}m)</div></div>"""
    
    st.markdown(bar_html, unsafe_allow_html=True)

    # 3. INFO
    if coll_speed > 0:
        st.markdown(f'<div class="alert-box alert-red">💥 Kokkupõrge kiirusel {coll_speed:.0f} km/h</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-box alert-green">✅ Sõiduk peatus enne takistust.</div>', unsafe_allow_html=True)

    # 4. LISAMAA
    if excess_dist > 0:
        st.markdown(f'<div class="alert-box alert-yellow">Kiiruse ületamisest tingitud lisamaa: +{excess_dist:.1f} meetrit</div>', unsafe_allow_html=True)

    # 5. AJAVÕIT
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

    # 6. DETAILID
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

    # 7. RISKID
    def get_risk_color(val):
        if val == 0: return "#28a745"
        if val < 50: return "#ffc107"
        return "#dc3545"

    risk_html = "".join([
        '<div class="risk-container">',
        '<div class="risk-box">',
        '<div class="risk-icons"><span class="flipped">🚶</span>💥🚗</div>',
        '<span class="risk-title">Jalakäija:</span>',
        f'<div class="risk-val" style="color: {get_risk_color(risk_ped)}">{risk_ped}%</div>',
        '</div>',
        '<div class="risk-box">',
        '<div class="risk-icons"><span class="flipped">🚗</span>💥🚗</div>',
        '<span class="risk-title">Laupkokkupõrge:</span>',
        f'<div class="risk-val" style="color: {get_risk_color(risk_head)}">{risk_head}%</div>',
        '</div>',
        '<div class="risk-box">',
        '<div class="risk-icons">🚘💥🚗</div>',
        '<span class="risk-title">Külgkokkupõrge:</span>',
        f'<div class="risk-val" style="color: {get_risk_color(risk_side)}">{risk_side}%</div>',
        '</div>',
        '</div>'
    ])
    st.markdown(risk_html, unsafe_allow_html=True)
