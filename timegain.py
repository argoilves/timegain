import streamlit as st
import math
import textwrap

# --- LEHE SEADISTUSED ---
st.set_page_config(
    page_title="Ajavõidu kalkulaator",
    page_icon="🚗",
    layout="centered"
)

# --- CSS STIILID ---
# Siin määrame värvid, fondid ja graafika stiilid.
# Force light theme: Sunnime peale heleda tausta ja tumeda teksti.
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

        /* 2. RISKIKAARTIDE STIIL (nagu veebis) */
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
            background-color: #e0f7fa; /* Hele sinine */
            border: 1px solid #0097a7;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            color: #333 !important; /* Tume tekst */
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
        
        /* Ikoonide pööramine (peegelpilt) */
        .flipped {
            display: inline-block;
            transform: scaleX(-1);
        }

        /* 3. VISUAALNE GRAAFIK (RIBA) */
        .bar-wrapper {
            position: relative;
            width: 100%;
            height: 140px;
            background: #eeeeee;
            border-radius: 8px;
            margin-top: 20px;
            overflow: hidden;
            border: 1px solid #ccc;
            color: #333;
        }
        .bar-header {
            text-align: center;
            padding-top: 5px;
            font-size: 12px;
            color: #777;
            width: 100%;
        }
        .bar-container {
            position: absolute;
            bottom: 40px;
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
            bottom: 95px;
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
            top: 10px;
            bottom: 40px;
            width: 2px;
            background-color: rgba(0,0,0,0.3);
            z-index: 5;
            border-right: 1px dashed white;
        }

        /* 4. ALUMI
