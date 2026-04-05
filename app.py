import streamlit as st
import pandas as pd
from collections import Counter

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Frequency Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>📊 Master Frequency & Probability Sheet</h1>", unsafe_allow_html=True)
st.write("---")

# --- 2. डेटा प्रोसेसिंग (सभी शिफ्ट का डेटा जोड़ना) ---
def get_combined_data(df, shift_columns):
    all_numbers = []
    for col in shift_columns:
        # हर शिफ्ट के कॉलम से नंबर उठाना
        nums = df[col].dropna().astype(str).tolist()
        for n in nums:
            n = n.strip()
            if n.isdigit():
                all_numbers.append(int(n))
    return all_numbers

# --- 3. एनालिसिस इंजन ---
def create_frequency_table(all_nums):
    counts = Counter(all_nums)
    # 1 से 6 बार तक के लिए ग्रुप (Bins)
    freq_bins = {i: [] for i in range(1, 7)}
    
    for num, freq in counts.items():
        if freq in freq_bins:
            freq_bins[freq].append(f"{num:02d}")
        elif freq > 6:
            # अगर 6 से ज्यादा बार है तो उसे 6 वाले में ही जोड़ना
            freq_bins[6].append(f"{num:02d}")
            
    return freq_bins

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # आपकी शीट के अनुसार C से I तक की शिफ्ट्स (Index 2 to 8)
    shift_cols = list(df.columns[2:9]) 
    
    combined_data = get_combined_data(df, shift_cols)
    
    if combined_data:
        freq_bins = create_frequency_table(combined_data)
        
        st.subheader("📋 अंकों की आवृत्ति चार्ट (Frequency Chart)")
        st.write("ऊपर की लाइन 'बार' (Frequency) दर्शाती है और नीचे उसके 'अंक' (Numbers) हैं:")

        # जैसा आपने माँगा: ऊपर 1, 2, 3, 4, 5, 6 और नीचे उनके अंक
        # हम इसे एक सुंदर डेटाफ्रेम के रूप में दिखाएंगे
        max_len = max(len(freq_bins[i]) for i in range(1, 7))
        
        # टेबल को बराबर करने के लिए खाली जगह भरना
        table_dict = {}
        for i in range(1, 7):
            col_name = f"{i} बार आया"
            nums_list = sorted(freq_bins[i])
            # लिस्ट को बराबर लंबाई का बनाना ताकि टेबल सही दिखे
            table_dict[col_name] = nums_list + [""] * (max_len - len(nums_list))
        
        final_df = pd.DataFrame(table_dict)
        
        # टेबल डिस्प्ले
        st.table(final_df)
        
        st.write("---")
        
        # प्रोबेबिलिटी (संभावना) सेक्शन
        st.subheader("📈 सांख्यिकीय संभावना (Probability Analysis)")
        p_cols = st.columns(6)
        total_unique = len(set(combined_data))
        
        for i in range(1, 7):
            qty = len(freq_bins[i])
            # प्रोबेबिलिटी = (उस श्रेणी के अंक / कुल यूनिक अंक) * 100
            prob = (qty / total_unique * 100) if total_unique > 0 else 0
            p_cols[i-1].metric(label=f"{i} बार श्रेणी", value=f"{qty} अंक", delta=f"{prob:.1f}% Prob")

        st.success("💡 **टिप:** जो अंक 4, 5 या 6 बार आए हैं, उनके आज रिपीट होने या किसी दूसरी शिफ्ट में आने की संभावना सबसे अधिक है।")
    else:
        st.error("शीट में कोई नंबर नहीं मिला।")
else:
    st.info("एनालिसिस शुरू करने के लिए एक्सेल फाइल अपलोड करें।")
    
