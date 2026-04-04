import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import datetime

# --- 1. पेज स्टाइलिंग (स्क्रीनशॉट के अनुसार) ---
st.set_page_config(page_title="MAYA AI Hybrid", layout="wide")

st.markdown("""
    <style>
    /* मुख्य हेडर और बॉडी */
    .stApp { background-color: #ffffff; }
    
    /* प्रेडिक्शन बॉक्स (हल्का हरा - जैसा स्क्रीनशॉट में है) */
    .prediction-box { 
        background-color: #e8f5e9; 
        padding: 12px; 
        border-radius: 5px; 
        text-align: center; 
        color: #2e7d32; 
        font-weight: 500; 
        font-size: 18px;
        margin: 5px;
        border: 1px solid #c8e6c9;
    }
    
    /* स्किप बॉक्स (हल्का लाल - जैसा स्क्रीनशॉट में है) */
    .skip-box { 
        background-color: #ffebee; 
        padding: 8px; 
        border-radius: 5px; 
        text-align: center; 
        border: 1px solid #ffcdd2; 
        color: #c62828; 
        font-size: 14px; 
        margin: 3px;
    }
    
    /* शिफ्ट हेडर स्टाइल */
    .shift-header {
        font-weight: bold;
        color: #333;
        margin-top: 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. डेटा क्लीनिंग ---
def clean_and_prepare_data(df, shift_columns):
    temp_list = []
    for index, row in df.iterrows():
        try:
            raw_date = pd.to_datetime(row.iloc[1])
            for s_name in shift_columns:
                val = str(row[s_name]).strip()
                if val.isdigit():
                    n = int(val)
                    if 0 <= n <= 99:
                        temp_list.append({
                            'date': raw_date.date(),
                            'day_num': raw_date.day,
                            'weekday': raw_date.weekday(),
                            'shift': s_name,
                            'num': n
                        })
        except: continue
    return pd.DataFrame(temp_list)

# --- 3. Hybrid AI इंजन ---
def get_hybrid_analysis(clean_df, target_shift, target_date):
    shift_data = clean_df[clean_df['shift'] == target_shift]
    if len(shift_data) < 25: return None
    
    nums = shift_data['num'].values
    days = shift_data['day_num'].values
    wdays = shift_data['weekday'].values
    window = 5
    
    X, y = [], []
    for i in range(window, len(nums)):
        X.append(list(nums[i-window:i]) + [days[i], wdays[i]])
        y.append(nums[i])
    
    X_train = np.array(X)
    y_train = np.array(y)

    le = LabelEncoder()
    y_encoded = le.fit_transform(y_train)

    rf = RandomForestClassifier(n_estimators=150, random_state=42)
    rf.fit(X_train, y_train)
    
    xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, verbosity=0)
    xgb.fit(X_train, y_encoded)
    
    input_feat = list(nums[-window:]) + [target_date.day, target_date.weekday()]
    
    rf_probs = rf.predict_proba([input_feat])[0]
    xgb_probs = xgb.predict_proba([input_feat])[0]
    
    final_scores = (rf_probs + xgb_probs) / 2
    all_classes = rf.classes_
    sorted_idx = np.argsort(final_scores)
    
    return list(all_classes[sorted_idx[-10:][::-1]]), list(all_classes[sorted_idx[:20]])

# --- 4. UI Dashboard ---
st.title("🔮 MAYA AI: Hybrid Edition")

uploaded_file = st.file_uploader("📂 अपनी Excel डेटा शीट अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    shift_cols = df.columns[2:9]
    clean_df = clean_and_prepare_data(df, shift_cols)
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())
    with c2:
        selected_shift = st.selectbox("🎯 शिफ्ट चुनें:", ["All Shifts"] + list(shift_cols))

    if st.button("🚀 RUN HYBRID ANALYSIS"):
        shifts_to_run = shift_cols if selected_shift == "All Shifts" else [selected_shift]
        
        for s_name in shifts_to_run:
            results = get_hybrid_analysis(clean_df, s_name, target_date)
            if results:
                top_10, bottom_20 = results
                
                # शिफ्ट हेडर (जैसे स्क्रीनशॉट में है)
                st.markdown(f"<div class='shift-header'>🎰 {s_name}</div>", unsafe_allow_html=True)
                
                # टॉप 10 हिट्स (हल्का हरा ग्रिड)
                t_cols = st.columns(10)
                for i, n in enumerate(top_10):
                    t_cols[i].markdown(f"<div class='prediction-box'>{n:02d}</div>", unsafe_allow_html=True)
                
                # बॉटम 20 स्किप्स (एक्सपैंडर और हल्का लाल ग्रिड)
                with st.expander(f"❌ Skip These (Bottom 20)"):
                    b_cols = st.columns(10)
                    for i, n in enumerate(bottom_20):
                        b_cols[i % 10].markdown(f"<div class='skip-box'>{n:02d}</div>", unsafe_allow_html=True)
                st.write("---")
            else:
                st.warning(f"⚠️ {s_name}: डेटा कम है।")
        st.balloons()
else:
    st.info("Maya AI को शुरू करने के लिए फाइल अपलोड करें।")
