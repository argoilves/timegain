import streamlit as st
import math

# --- LEHE SEADISTUSED ---
st.set_page_config(
    page_title="Ajavõidu kalkulaator",
    page_icon="🚗",
    layout="centered"
)

# --- CSS STIILID (VISUAAL JA HELE TEEMA) ---
# See plokk sunnib peale heleda teema ja defineerib ikoonide pööramise
st.markdown("""
    <style>
        /* Sunnime peale heleda tausta ja tumeda teksti */
        [data-testid="stAppViewContainer"] {
            background-color: #f4f4f9;
            color: #333333;
        }
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0);
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
        }
        .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
            color: #333333 !important;
            font-weight: bold;
        }
        
        /* Ikoonide pööramine (peegelpilt) */
        .flipped {
            display: inline-block;
            transform: scaleX(-1);
        }
        
        /* Riskikaartide stiilid */
        .risk-container {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
            margin-top: 20px;
        }
        .risk-box {
            flex: 1;
            min-width: 140px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            background-color: #e0f7fa;
            border: 1px solid #0097a7;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            color: #555;
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
        }
        .risk-val {
            font-size: 1.6em;
            font-weight: bold;
        }
        
        /* Visualiseerimise ribad */
        .bar-wrapper {
            position: relative;
            width: 100%;
            height: 160px;
            background: #eee;
            border-radius: 8px;
            margin-top: 30px;
            overflow: hidden; 
        }
        .bar-container {
            position: absolute;
            bottom: 60px;
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
            overflow: visible;
        }
        .icon-marker {
            position: absolute;
            bottom: 115px;
            font-size: 24px;
            transform: translateX(-50%);
            text-align: center;
            line-height: 1;
            transition: left 0.5s ease-out;
        }
        .reaction-line {
            position: absolute;
            top: 20px;
            height: 140px;
            width: 2px;
            background-color: rgba(0,0,0,0.2);
            z-index: 5;
        }
    </style>
""", unsafe_allow_html=True)

# --- FÜÜSIKA JA LOOGIKA ---

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

# --- UI LOGIC ---

# Initsialiseerime sessiooni oleku, et tulemused püsiks ees
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

st.title("Ajavõidu kalkulaator")

# Sisendid
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

# ARVUTA NUPP
if st.button("Arvuta", type="primary"):
    st.session_state.calculated = True

# KUVAME TULEMUSED AINULT SIIS, KUI NUPPU ON VAJUTATUD
if st.session_state.calculated:
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
    
    # Ajavõit
    if time_gain_min > 0.01:
        st.success(f"🚗 Säästate aega: **{time_gain_min:.1f} min**")
    elif time_gain_min < -0.01:
        st.error(f"🚗 Kaotate aega: **{abs(time_gain_min):.1f} min**")
    else:
        st.info("🚗 Ajavõitu ega kaotust pole.")

    # Riskikaardid (HTML)
    def get_risk_color(val):
        if val == 0: return "#28a745" # Roheline
        if val < 50: return "#ffc107" # Kollane
        return "#dc3545" # Punane

    risk_html = f"""
    <div class="risk-container">
        <div class="risk-box">
            <div class="risk-icons">
                <span class="flipped">🚶</span>💥🚗
            </div>
            <span class="risk-title">Jalakäija:</span>
            <div class="risk-val" style="color: {get_risk_color(risk_ped)}">{risk_ped}%</div>
        </div>
        <div class="risk-box">
            <div class="risk-icons">
                <span class="flipped">🚗</span>💥🚗
            </div>
            <span class="risk-title">Laupkokkupõrge:</span>
            <div class="risk-val" style="color: {get_risk_color(risk_head)}">{risk_head}%</div>
        </div>
        <div class="risk-box">
            <div class="risk-icons">
                🚘💥🚗
            </div>
            <span class="risk-title">Külgkokkupõrge:</span>
            <div class="risk-val" style="color: {get_risk_color(risk_side)}">{risk_side}%</div>
        </div>
    </div>
    """
    st.markdown(risk_html, unsafe_allow_html=True)

    # VISUALISEERIMINE (RIBA)
    # Arvutame skaala
    max_scale = max(total_dist_actual, total_dist_allowed, obstacle_dist, 1) * 1.15
    
    def pct(val): return (val / max_scale) * 100
    
    # Ikoonide asukohad
    car_pos = pct(min(total_dist_actual, obstacle_dist) if coll_speed > 0 else total_dist_actual)
    ped_pos = pct(obstacle_dist)
    
    # Ribade loogika (täpselt nagu JS-is)
    # Roheline riba = Lubatud kiirusega peatumine
    bar1_width = pct(total_dist_allowed)
    
    # Punane riba = Liigne maa (kui tegelik > lubatud)
    bar2_width = pct(excess_dist)
    bar2_left = bar1_width # Punane algab rohelise lõpust
    
    # Kui tegelik peatumine on lühem kui lubatud (sõitis aeglasemalt), siis bar1 on lühem ja bar2 on 0
    if total_dist_actual < total_dist_allowed:
        bar1_width = pct(total_dist_actual)
        bar2_width = 0

    bar_html = f"""
    <div class="bar-wrapper">
        <div style="text-align: center; padding-top: 10px; font-weight: bold; color: #555;">Peatumisteekond</div>
        
        <div class="icon-marker" style="left: {ped_pos}%;">
            <span class="flipped" style="display:inline-block;">🚶</span><br>
            <span style="font-size: 12px; color: #333;">{obstacle_dist:.1f}m</span>
        </div>
        
        <div class="icon-marker" style="left: {car_pos}%; z-index: 10;">
            <span class="flipped" style="display:inline-block;">🚗</span>
        </div>

        <div class="bar-container">
            <div class="bar-segment" style="width: {bar1_width}%; background-color: #28a745; left: 0;">
                {f'{total_dist_allowed:.1f}m' if bar1_width > 15 else ''}
            </div>
            
            <div class="bar-segment" style="width: {bar2_width}%; background-color: #dc3545; left: {bar2_left}%;">
                {f'+{excess_dist:.1f}m' if bar2_width > 10 else ''}
            </div>
        </div>
        
        <div class="reaction-line" style="left: {pct(r_dist_act)}%;"></div>
        <div style="position:absolute; top:5px; left:{pct(r_dist_act) + 1}%; font-size:10px; color:#666;">Reageerimine</div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)
    
    # Lisainfo teksti kujul
    st.write("") # Tühik
    if coll_speed > 0:
        st.error(f"💥 **Kokkupõrge kiirusel {coll_speed:.0f} km/h**")
    else:
        st.success("✅ **Sõiduk peatus enne takistust.**")
    
    if excess_dist > 0:
        st.warning(f"Kiiruse ületamisest tingitud lisamaa: **+{excess_dist:.1f} meetrit**")
