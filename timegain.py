import streamlit as st
import math

# --- KONFIGURATSIOON ---
st.set_page_config(
    page_title="Ajavõidu kalkulaator",
    page_icon="🚗",
    layout="centered"
)

# --- FÜÜSIKA JA LOOGIKA ---

# Teekatte ja rehvide hõõrdetegurid (vastavad JS koodi loogikale)
DECELERATION_MULTIPLIERS = {
    "dryAsphalt": {"good": 7, "worn": 6, "very_worn": 5},
    "wetAsphalt": {"good": 4.5, "worn": 3.5, "very_worn": 2.5},
    "gravel": {"good": 3.5, "worn": 2.8, "very_worn": 2},
    "snow": {"good": 1.5, "worn": 1, "very_worn": 0.7},
    "ice": {"good": 0.5, "worn": 0.3, "very_worn": 0.1}
}

# Hukkumisriski andmed (interpolatsiooniks)
FATALITY_RISK_DATA = {
    'pedestrian': [
        (0, 0), (10, 1), (20, 5), (30, 15), (40, 35), (50, 65),
        (60, 90), (70, 98), (80, 100), (110, 100)
    ],
    'sideImpact': [
        (0, 0), (20, 1), (30, 2), (40, 5), (50, 15), (60, 40),
        (70, 70), (80, 90), (90, 98), (100, 100), (110, 100)
    ],
    'headOn': [
        (0, 0), (40, 1), (50, 2), (60, 5), (70, 10), (80, 25),
        (90, 50), (100, 75), (110, 100)
    ]
}

def kmh_to_ms(kmh):
    return kmh * 1000 / 3600

def ms_to_kmh(ms):
    return ms * 3600 / 1000

def get_deceleration(road_cond, tire_cond):
    multiplier = DECELERATION_MULTIPLIERS[road_cond][tire_cond]
    return 9.81 * (multiplier / 10)

def calculate_stopping_distance(speed_kmh, road, tire, reaction_time):
    if speed_kmh <= 0:
        return 0, 0, 0, 0
    
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
    
    if obstacle_dist <= reaction_dist:
        return init_speed_kmh
    
    speed_squared = (init_speed_ms ** 2) - (2 * decel * dist_after_reaction)
    
    if speed_squared <= 0:
        return 0
    else:
        return ms_to_kmh(math.sqrt(speed_squared))

def get_fatality_risk(speed, risk_type):
    data = FATALITY_RISK_DATA[risk_type]
    # Piira kiirus maksimaalse tabelis oleva väärtusega
    speed = min(speed, data[-1][0])
    
    if speed <= 0: return 0
    if speed >= data[-1][0]: return data[-1][1]
    
    for i in range(len(data) - 1):
        v1, r1 = data[i]
        v2, r2 = data[i+1]
        if v1 <= speed <= v2:
            if v2 == v1: return r1
            return r1 + (speed - v1) * (r2 - r1) / (v2 - v1)
            
    return data[-1][1]

# --- TÕLKED ---
TRANSLATIONS = {
    "et": {
        "title": "Ajavõidu kalkulaator",
        "dist_label": "Läbitav vahemaa (km)",
        "reaction_label": "Reageerimisaeg (s)",
        "allowed_label": "Lubatud sõidukiirus (km/h)",
        "actual_label": "Keskmine reaalne sõidukiirus (km/h)",
        "obs_label": "Kaugus takistusest (m)",
        "road_label": "Teeolud",
        "tire_label": "Rehvide seisukord",
        "time_gain": "Säästate aega",
        "time_loss": "Kaotate aega",
        "no_change": "Ajavõitu ega kaotust pole.",
        "risk_ped": "Jalakäija",
        "risk_head": "Laupkokkupõrge",
        "risk_side": "Külgkokkupõrge",
        "stopped": "Sõiduk peatus",
        "collision": "Kokkupõrge",
        "dist_info": "Peatumisteekond kokku",
        "reaction_dist": "Reageerimine",
        "braking_dist": "Pidurdus",
        "excess_dist": "Lisamaa kiiruse ületamisest",
        "options_road": {"dryAsphalt": "Kuiv asfalt", "wetAsphalt": "Märg asfalt", "gravel": "Kruus", "snow": "Lumi", "ice": "Jää"},
        "options_tire": {"good": "Head", "worn": "Kulunud", "very_worn": "Väga kulunud"}
    },
    "en": {
        "title": "Time Gain Calculator",
        "dist_label": "Distance (km)",
        "reaction_label": "Reaction time (s)",
        "allowed_label": "Allowed speed (km/h)",
        "actual_label": "Actual speed (km/h)",
        "obs_label": "Distance to obstacle (m)",
        "road_label": "Road conditions",
        "tire_label": "Tire conditions",
        "time_gain": "Time saved",
        "time_loss": "Time lost",
        "no_change": "No time gained or lost.",
        "risk_ped": "Pedestrian",
        "risk_head": "Head-on",
        "risk_side": "Side impact",
        "stopped": "Vehicle stopped",
        "collision": "Collision",
        "dist_info": "Total stopping distance",
        "reaction_dist": "Reaction",
        "braking_dist": "Braking",
        "excess_dist": "Excess distance due to speeding",
        "options_road": {"dryAsphalt": "Dry Asphalt", "wetAsphalt": "Wet Asphalt", "gravel": "Gravel", "snow": "Snow", "ice": "Ice"},
        "options_tire": {"good": "Good", "worn": "Worn", "very_worn": "Very Worn"}
    },
    "ru": {
        "title": "Калькулятор выигрыша времени",
        "dist_label": "Расстояние (км)",
        "reaction_label": "Время реакции (с)",
        "allowed_label": "Разрешенная скорость (км/ч)",
        "actual_label": "Фактическая скорость (км/ч)",
        "obs_label": "Расстояние до препятствия (м)",
        "road_label": "Дорожные условия",
        "tire_label": "Состояние шин",
        "time_gain": "Выигрыш времени",
        "time_loss": "Потеря времени",
        "no_change": "Нет выигрыша или потери времени.",
        "risk_ped": "Пешеход",
        "risk_head": "Лобовое",
        "risk_side": "Боковое",
        "stopped": "Остановка",
        "collision": "Столкновение",
        "dist_info": "Общий тормозной путь",
        "reaction_dist": "Реакция",
        "braking_dist": "Торможение",
        "excess_dist": "Лишний путь из-за скорости",
        "options_road": {"dryAsphalt": "Сухой асфальт", "wetAsphalt": "Мокрый асфальт", "gravel": "Гравий", "snow": "Снег", "ice": "Лед"},
        "options_tire": {"good": "Хорошие", "worn": "Изношенные", "very_worn": "Очень изношенные"}
    }
}

# --- KASUTAJALIIDES (UI) ---

# Keele valik
lang_code = st.selectbox("🌐 Language / Keel / Язык", ["et", "en", "ru"], index=0, label_visibility="collapsed")
t = TRANSLATIONS[lang_code]

st.title(t["title"])

# Sisendid
col1, col2 = st.columns(2)
with col1:
    distance = st.number_input(t["dist_label"], value=10.0, step=1.0, min_value=0.1)
    allowed_speed = st.number_input(t["allowed_label"], value=30, step=5, min_value=1)
    road_key = st.selectbox(
        t["road_label"], 
        options=list(t["options_road"].keys()), 
        format_func=lambda x: t["options_road"][x]
    )

with col2:
    reaction_time = st.number_input(t["reaction_label"], value=1.0, step=0.1, min_value=0.1)
    actual_speed = st.number_input(t["actual_label"], value=50, step=5, min_value=1)
    tire_key = st.selectbox(
        t["tire_label"], 
        options=list(t["options_tire"].keys()), 
        format_func=lambda x: t["options_tire"][x]
    )

obstacle_dist = st.number_input(t["obs_label"], value=25.0, step=1.0, min_value=0.0)

# --- ARVUTUSED ---

# Ajavõit
allowed_time_h = distance / allowed_speed
actual_time_h = distance / actual_speed
time_diff_h = allowed_time_h - actual_time_h
time_diff_min = abs(time_diff_h * 60)
time_diff_sec = abs(time_diff_h * 3600)

# Peatumisteekonnad
r_dist_all, b_dist_all, total_dist_allowed, time_all = calculate_stopping_distance(allowed_speed, road_key, tire_key, reaction_time)
r_dist_act, b_dist_act, total_dist_actual, time_act = calculate_stopping_distance(actual_speed, road_key, tire_key, reaction_time)

# Lisa pidurdusmaa (kui kiirus on suurem)
excess_dist = max(0, total_dist_actual - total_dist_allowed)

# Kokkupõrke kiirused
coll_speed_allowed = calculate_collision_speed(allowed_speed, obstacle_dist, road_key, tire_key, reaction_time)
coll_speed_actual = calculate_collision_speed(actual_speed, obstacle_dist, road_key, tire_key, reaction_time)

# Riskid
risk_ped = int(get_fatality_risk(coll_speed_actual, 'pedestrian'))
risk_head = int(get_fatality_risk(coll_speed_actual, 'headOn'))
risk_side = int(get_fatality_risk(coll_speed_actual, 'sideImpact'))

# --- TULEMUSTE KUVAMINE ---

st.markdown("---")

# 1. Ajavõidu info
if time_diff_h > 0.0001:
    st.success(f"🚗 {t['time_gain']}: **{time_diff_min:.1f} min**")
elif time_diff_h < -0.0001:
    st.error(f"🚗 {t['time_loss']}: **{time_diff_min:.1f} min**")
else:
    st.info(f"🚗 {t['no_change']}")

# 2. Riskikaardid (kasutades CSS-i, et jäljendada originaalset stiili)
def risk_color(val):
    if val == 0: return "#28a745" # Roheline
    if val < 50: return "#ffc107" # Kollane
    return "#dc3545" # Punane

st.markdown(f"""
    <style>
    .risk-container {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; }}
    .risk-box {{ 
        flex: 1; min-width: 100px; padding: 15px; border-radius: 8px; text-align: center; 
        background-color: #f8f9fa; border: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .risk-val {{ font-size: 24px; font-weight: bold; }}
    </style>
    <div class="risk-container">
        <div class="risk-box">
            <div>🚶 {t['risk_ped']}</div>
            <div class="risk-val" style="color: {risk_color(risk_ped)}">{risk_ped}%</div>
        </div>
        <div class="risk-box">
            <div>💥🚗 {t['risk_head']}</div>
            <div class="risk-val" style="color: {risk_color(risk_head)}">{risk_head}%</div>
        </div>
        <div class="risk-box">
            <div>🚗💥 {t['risk_side']}</div>
            <div class="risk-val" style="color: {risk_color(risk_side)}">{risk_side}%</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. Visuaalne graafik (HTML/CSS Streamliti sees)
# Arvutame protsendid skaala jaoks
max_scale = max(total_dist_actual, total_dist_allowed, obstacle_dist, 1) * 1.1

def pct(val):
    return (val / max_scale) * 100

# CSS stiilid ribadele
st.markdown("""
<style>
.bar-chart-container { position: relative; width: 100%; height: 180px; background-color: #eee; border-radius: 8px; margin-top: 20px; overflow: hidden; }
.bar-row { position: absolute; height: 40px; left: 0; display: flex; align-items: center; color: white; font-weight: bold; font-size: 12px; border-radius: 4px; transition: width 0.5s; }
.bar-label { position: absolute; right: 5px; text-shadow: 1px 1px 2px black; }
.marker-line { position: absolute; top: 0; bottom: 0; width: 2px; background: #333; z-index: 10; border-right: 1px dashed white;}
.icon { position: absolute; font-size: 24px; transform: translateX(-50%); transition: left 0.5s; bottom: 50px; }
.obs-line { position: absolute; top: 0; bottom: 0; width: 2px; background: black; z-index: 5; opacity: 0.3; }
</style>
""", unsafe_allow_html=True)

# HTML sisu genereerimine
html_visuals = f"""
<div class="bar-chart-container">
    <div class="obs-line" style="left: {pct(obstacle_dist)}%;"></div>
    <div style="position: absolute; left: {pct(obstacle_dist)}%; top: 5px; font-size: 20px; transform: translateX(-50%);">🚶</div>
    <div style="position: absolute; left: {pct(obstacle_dist)}%; bottom: 5px; font-size: 10px; transform: translateX(-50%);">{obstacle_dist:.1f}m</div>

    <div class="bar-row" style="top: 100px; width: {pct(total_dist_allowed)}%; background-color: #28a745; opacity: 0.6;">
        <span class="bar-label">{total_dist_allowed:.1f} m</span>
    </div>
    
    <div class="bar-row" style="top: 40px; width: {pct(r_dist_act)}%; background-color: #17a2b8; z-index: 2;"></div>
    
    <div class="bar-row" style="top: 40px; width: {pct(total_dist_actual)}%; background-color: {'#dc3545' if coll_speed_actual > 0 else '#28a745'};">
        <span class="bar-label">{total_dist_actual:.1f} m</span>
    </div>
    
    <div class="marker-line" style="left: {pct(r_dist_act)}%; height: 60px; top: 30px;"></div>
    <div style="position: absolute; left: {pct(r_dist_act)}%; top: 10px; font-size: 10px; color: #333;">{t['reaction_dist']}</div>

    <div class="icon" style="left: {pct(min(total_dist_actual, obstacle_dist))}%;">🚗</div>
</div>
"""
st.markdown(html_visuals, unsafe_allow_html=True)

# Detailsem info
st.caption(f"ℹ️ {t['dist_info']}: {total_dist_actual:.1f}m ({time_act:.1f}s)")
if coll_speed_actual > 0:
    st.caption(f"💥 **{t['collision']} @ {coll_speed_actual:.0f} km/h**")
else:
    st.caption(f"✅ **{t['stopped']}**")

if excess_dist > 0:
    st.warning(f"{t['excess_dist']}: +{excess_dist:.1f} m")
