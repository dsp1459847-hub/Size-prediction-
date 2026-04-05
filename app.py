import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- 1. पेज सेटअप और स्टाइलिंग ---
st.set_page_config(page_title="MAYA AI: Supreme Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: Supreme Master Dashboard</h1>", unsafe_allow_html=True)

# --- 2. डेटा प्रोसेसिंग फंक्शन ---
def process_excel_data(df, shift_columns):
    temp_list = []
    for index, row in df.iterrows():
        try:
            # तारीख को सही फॉर्मेट में पढ़ना
            dt = pd.to_datetime(row.iloc[1]).date()
            for s_name in shift_columns:
                val = str(row[s_name]).strip()
                if val.isdigit():
                    temp_list.append({'date': dt, 'shift': s_name, 'num': int(val)})
        except: continue
    return pd.DataFrame(temp_list)

# --- 3. पुराना लॉजिक: Hot/Due और Skip (Per Shift) ---
def get_math_logic(clean_df, target_shift, selected_date):
    # केवल चुनी हुई तारीख तक का पिछला डेटा लेना
    shift_data = clean_df[(clean_df['shift'] == target_shift) & (clean_df['date'] < selected_date)].sort_values('date')
    
    if len(shift_data) < 20: return None, None, []
    
    all_nums = shift_data['num'].values
    
    # A. Hot Numbers (Top 10) - पिछले 45 रिकॉर्ड्स
    counts = Counter(all_nums[-45:])
    hot_10 = [n for n, c in counts.most_common(10)]
    hot_str = "🔥 **HOT:** " + ", ".join([f"{n:02d}" for n in hot_10])
    
    # B. Due/Gap Numbers (Top 10)
    last_seen = {}
    for n in range(100):
        found = False
        for i in range(len(all_nums)-1, -1, -1):
            if all_nums[i] == n:
                last_seen[n] = len(all_nums) - i
                found = True
                break
        if not found: last_seen[n] = 999
    
    due = sorted(last_seen.items(), key=lambda x: x[1], reverse=True)[:10]
    due_nums = [n for n, gap in due]
    due_str = "⏳ **DUE:** " + ", ".join([f"{n:02d}" for n in due_nums])
    
    # C. Skip Numbers
    recent = [f"{n:02d}" for n in all_nums[-20:]]
    skip_str = ", ".join(set(recent))
    
    combined_target = f"{hot_str}\n\n{due_str}"
    return combined_target, skip_str, hot_10

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    shift_cols = list(df.columns[2:8]) # आपकी 6 मुख्य शिफ्ट्स (C से H)
    clean_df = process_excel_data(df, shift_cols)
    
    st.write("---")
    # तारीख चुनने का विकल्प वापस जोड़ा गया
    target_date = st.date_input("📅 प्रेडिक्शन के लिए तारीख चुनें (कैलेंडर):", datetime.date.today())
    
    if st.button("🚀 मास्टर विश्लेषण तैयार करें"):
        # डेटा स्टोर करने के लिए लिस्ट
        row_target = {"Type": "🎯 TARGET (Hot/Due)", "Date": target_date}
        row_skip = {"Type": "❌ SKIP (Recent)", "Date": target_date}
        all_60_hot_ank = []
        
        # --- पार्ट 1: शिफ्ट-वाइज चार्ट ---
        for name in shift_cols:
            t_logic, s_logic, h_list = get_math_logic(clean_df, name, target_date)
            row_target[name] = t_logic if t_logic else "Data Kam Hai"
            row_skip[name] = s_logic if s_logic else "Data Kam Hai"
            all_60_hot_ank.extend(h_list)
            
        st.write("---")
        st.subheader(f"✅ 1. शिफ्ट-वाइज चार्ट ({target_date})")
        st.table(pd.DataFrame([row_target]))
        
        st.subheader("❌ 2. शिफ्ट-वाइज स्किप चार्ट")
        st.table(pd.DataFrame([row_skip]))
        
        # --- पार्ट 2: 60-Ank प्रोबेबिलिटी चार्ट ---
        st.write("---")
        st.subheader("📊 3. मास्टर प्रोबेबिलिटी चार्ट (Common Hot Numbers)")
        
        final_counts = Counter(all_60_hot_ank)
        freq_bins = {i: [] for i in range(1, 7)}
        for num, freq in final_counts.items():
            if freq in freq_bins: freq_bins[freq].append(f"{num:02d}")
            elif freq > 6: freq_bins[6].append(f"{num:02d}")
        
        # टेबल बनाना
        if any(freq_bins.values()):
            max_len = max(len(freq_bins[i]) for i in range(1, 7))
            table_dict = {}
            for i in range(1, 7):
                col_name = f"{i} बार कॉमन"
                nums = sorted(freq_bins[i])
                table_dict[col_name] = nums + [""] * (max_len - len(nums))
            
            st.table(pd.DataFrame(table_dict))
            
            # हाईलाइट्स
            strong_ank = freq_bins[3] + freq_bins[4] + freq_bins[5] + freq_bins[6]
            if strong_ank:
                st.success(f"🔥 **सबसे मजबूत कॉमन अंक:** {', '.join(strong_ank)}")
        else:
            st.warning("प्रोबेबिलिटी चार्ट के लिए पर्याप्त डेटा नहीं है।")
        
        st.balloons()
else:
    st.info("एनालिसिस के लिए एक्सेल फाइल अपलोड करें।")
