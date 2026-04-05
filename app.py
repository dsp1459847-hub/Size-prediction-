import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: 60-Ank Probability", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>📊 60-Ank Hot Probability Sheet</h1>", unsafe_allow_html=True)

# --- 2. डेटा प्रोसेसिंग ---
def process_excel_data(df, shift_columns):
    temp_list = []
    for index, row in df.iterrows():
        try:
            dt = pd.to_datetime(row.iloc[1]).date()
            for s_name in shift_columns:
                val = str(row[s_name]).strip()
                if val.isdigit():
                    temp_list.append({'date': dt, 'shift': s_name, 'num': int(val)})
        except: continue
    return pd.DataFrame(temp_list)

# --- 3. 60-Ank Logic (सभी शिफ्ट्स के Hot अंकों का मिलान) ---
def get_60_ank_probability(clean_df, shift_cols):
    all_hot_predictions = []
    
    for name in shift_cols:
        shift_data = clean_df[clean_df['shift'] == name].sort_values('date')
        if len(shift_data) >= 20:
            all_nums = shift_data['num'].values
            # हर शिफ्ट के टॉप 10 Hot अंक निकालना (पिछले 45 दिन के आधार पर)
            counts = Counter(all_nums[-45:])
            hot_10 = [n for n, c in counts.most_common(10)]
            all_hot_predictions.extend(hot_10)
    
    # अब इन कुल 60 अंकों (6-7 शिफ्ट × 10) की फ्रीक्वेंसी देखना
    final_counts = Counter(all_hot_predictions)
    
    # 1 से 6 बार तक के डिब्बे (Bins)
    freq_bins = {i: [] for i in range(1, 7)}
    for num, freq in final_counts.items():
        if freq in freq_bins:
            freq_bins[freq].append(f"{num:02d}")
        elif freq > 6:
            freq_bins[6].append(f"{num:02d}")
            
    return freq_bins

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    shift_cols = list(df.columns[2:8]) # आपकी मुख्य 6 शिफ्ट्स (C से H)
    clean_df = process_excel_data(df, shift_cols)
    
    if st.button("🚀 60-Ank प्रोबेबिलिटी चार्ट जनरेट करें"):
        freq_bins = get_60_ank_probability(clean_df, shift_cols)
        
        st.write("---")
        st.subheader("📋 मास्टर प्रोबेबिलिटी चार्ट (Hot Predictions का मिलान)")
        st.write("यह चार्ट बताता है कि कौन सा अंक कितनी शिफ्टों के 'Hot' पैटर्न में कॉमन आया है:")

        # टेबल लेआउट (Header: 1, 2, 3, 4, 5, 6)
        max_len = max(len(freq_bins[i]) for i in range(1, 7))
        table_dict = {}
        for i in range(1, 7):
            col_name = f"{i} बार (Common)"
            nums = sorted(freq_bins[i])
            table_dict[col_name] = nums + [""] * (max_len - len(nums))
        
        st.table(pd.DataFrame(table_dict))
        
        # --- Probability Highlights ---
        st.write("---")
        st.subheader("📈 अंकों की शक्ति (Power Ranking)")
        p_cols = st.columns(3)
        
        # Super Strong (4, 5, 6 बार वाले)
        super_strong = freq_bins[4] + freq_bins[5] + freq_bins[6]
        p_cols[0].metric("Super Strong (4-6 Bar)", f"{len(super_strong)} Ank")
        
        # Medium (2-3 बार वाले)
        medium = freq_bins[2] + freq_bins[3]
        p_cols[1].metric("Medium (2-3 Bar)", f"{len(medium)} Ank")
        
        # Low (1 बार वाले)
        low = freq_bins[1]
        p_cols[2].metric("Low (1 Bar)", f"{len(low)} Ank")
        
        if super_strong:
            st.success(f"🔥 **सबसे मजबूत अंक:** {', '.join(super_strong)} (ये अंक कई शिफ्टों के पैटर्न में एक साथ आ रहे हैं)")
else:
    st.info("एनालिसिस के लिए एक्सेल फाइल अपलोड करें।")
    
