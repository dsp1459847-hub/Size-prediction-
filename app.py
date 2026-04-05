import streamlit as st
import pandas as pd
from collections import Counter

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Master Frequency", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1e88e5;'>📊 Master Hot Number Sheet (Combined)</h1>", unsafe_allow_html=True)
st.write("---")

# --- 2. डेटा प्रोसेसिंग (सभी शिफ्ट को मिलाना) ---
def get_master_data(df, shift_cols):
    master_list = []
    for col in shift_cols:
        # हर शिफ्ट का डेटा उठाना
        nums = df[col].dropna().astype(str).tolist()
        for n in nums:
            n = n.strip()
            if n.isdigit():
                master_list.append(int(n))
    return master_list

# --- 3. एनालिसिस इंजन ---
def create_frequency_sheet(all_nums):
    counts = Counter(all_nums)
    # 1 से 6+ बार तक के लिए घर (Columns) बनाना
    freq_bins = {i: [] for i in range(1, 7)}
    
    for num, freq in counts.items():
        if freq in freq_bins:
            freq_bins[freq].append(f"{num:02d}")
        elif freq > 6:
            # अगर 6 से ज्यादा बार आया है तो उसे 6 वाले में ही रखें या अलग दिखाएं
            freq_bins[6].append(f"{num:02d}*")
            
    return freq_bins

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # आपकी शीट के अनुसार C से I तक की शिफ्ट्स (Index 2 to 8)
    shift_cols = list(df.columns[2:9]) 
    
    all_data = get_master_data(df, shift_cols)
    
    if all_data:
        freq_bins = create_frequency_sheet(all_data)
        
        st.subheader("📋 मास्टर फ्रीक्वेंसी चार्ट (सभी शिफ्ट्स का जोड़)")
        
        # टेबल को आपके बताए फॉर्मेट में तैयार करना
        # Rows को Columns में बदलने के लिए dictionary
        display_data = {
            "1 Baar Aaye": ", ".join(sorted(freq_bins[1])),
            "2 Baar Aaye": ", ".join(sorted(freq_bins[2])),
            "3 Baar Aaye": ", ".join(sorted(freq_bins[3])),
            "4 Baar Aaye": ", ".join(sorted(freq_bins[4])),
            "5 Baar Aaye": ", ".join(sorted(freq_bins[5])),
            "6+ Baar Aaye": ", ".join(sorted(freq_bins[6]))
        }
        
        # Horizontal Table दिखाना (जैसा आपने माँगा था)
        st.table(pd.DataFrame([display_data]))
        
        st.write("---")
        
        # प्रोबेबिलिटी कैलकुलेशन
        st.subheader("📈 आंकड़ों की शक्ति (Probability)")
        p_cols = st.columns(6)
        for i in range(1, 7):
            qty = len(freq_bins[i])
            p_cols[i-1].metric(f"{i} Baar", f"{qty} Ank", delta=f"Prob: {qty}%")

        st.info("💡 **Strategy:** जो अंक 4, 5, या 6 बार आए हैं, वे सबसे 'Hot' हैं। जो अंक इस टेबल में नहीं हैं, वे अभी तक आए ही नहीं (Zero Frequency)।")
    else:
        st.error("डेटा नहीं मिला।")
else:
    st.info("एनालिसिस के लिए एक्सेल फाइल अपलोड करें।")
    
