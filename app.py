import streamlit as st
import pandas as pd
from collections import Counter

# --- 1. Page Styling ---
st.set_page_config(page_title="Shift-Wise Frequency", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1565c0;'>📈 Shift-Wise Hot Number Analytics</h1>", unsafe_allow_html=True)

# --- 2. Data Cleaning ---
def get_shift_data(df, shift_name):
    # Excel se us specific shift ka data nikalna
    nums = df[shift_name].dropna().astype(str).tolist()
    clean_nums = []
    for n in nums:
        if n.strip().isdigit():
            clean_nums.append(int(n))
    return clean_nums

# --- 3. Analysis Logic ---
def analyze_shift_freq(nums):
    total = len(nums)
    counts = Counter(nums)
    
    # 1 se 6 bar tak ka map
    freq_map = {i: [] for i in range(1, 7)}
    for num, f in counts.items():
        if f in freq_map:
            freq_map[f].append(f"{num:02d}")
    
    return freq_map, total

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 Apni Excel File Upload Karein", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    shift_cols = list(df.columns[2:8]) # Pehli 6 Shifts (C se H tak)
    
    st.write("### 📅 Sabhi Shifts Ka Frequency Report")
    
    for s_name in shift_cols:
        with st.expander(f"📊 {s_name} Ka Report Dekhein", expanded=True):
            s_nums = get_shift_data(df, s_name)
            if s_nums:
                freq_map, total = analyze_shift_freq(s_nums)
                
                # Table Data
                report_list = []
                for f in range(1, 7):
                    n_list = freq_map[f]
                    qty = len(n_list)
                    # Probability: Us frequency ke kitne numbers hain total 100 mein se
                    prob = (qty / 100) * 100 
                    
                    report_list.append({
                        "Frequency": f"{f} Baar Aaye",
                        "Kitne Ank (Qty)": qty,
                        "Sambhvana (Prob %)": f"{prob:.1f}%",
                        "Ank (Numbers)": ", ".join(n_list) if n_list else "Koi Nahi"
                    })
                
                st.table(pd.DataFrame(report_list))
            else:
                st.warning(f"{s_name} mein koi valid data nahi mila.")
    
    st.success("💡 Tip: Jo number 5 ya 6 baar aaye hain, wo 'Extreme Hot' hain. Jo 1 baar aaye hain wo 'Cold' hain.")
else:
    st.info("Excel file upload karein taaki main har shift ka analysis kar sakun.")
    
