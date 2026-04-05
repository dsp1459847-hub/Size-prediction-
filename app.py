import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Supreme Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: Supreme Master (Same-Day Tracker)</h1>", unsafe_allow_html=True)

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

# --- 3. Same Day Match Logic ---
def check_same_day_matches(clean_df, selected_date, hot_nums):
    # उस दिन की सभी शिफ्टों के जो नंबर अब तक आ चुके हैं (एक्सेल के अनुसार)
    today_data = clean_df[clean_df['date'] == selected_date]
    today_nums = today_data['num'].unique()
    
    matches = [f"{n:02d}" for n in hot_nums if n in today_nums]
    if matches:
        return "✅ Match: " + ", ".join(matches)
    return "⏳ No Match Yet"

# --- 4. मास्टर लॉजिक ---
def get_math_logic(clean_df, target_shift, selected_date):
    # प्रेडिक्शन के लिए पिछला डेटा
    history_data = clean_df[(clean_df['shift'] == target_shift) & (clean_df['date'] < selected_date)].sort_values('date')
    
    if len(history_data) < 20: return None, None, "Data Kam Hai", []
    
    all_nums = history_data['num'].values
    
    # HOT Numbers
    counts = Counter(all_nums[-45:])
    hot_10 = [n for n, c in counts.most_common(10)]
    hot_str = "🔥 **HOT:** " + ", ".join([f"{n:02d}" for n in hot_10])
    
    # DUE Numbers
    last_seen = {n: 999 for n in range(100)}
    for i, n in enumerate(all_nums):
        last_seen[n] = len(all_nums) - i
    due = sorted(last_seen.items(), key=lambda x: x[1], reverse=True)[:10]
    due_str = "⏳ **DUE:** " + ", ".join([f"{n:02d}" for n in [x[0] for x in due]])
    
    # SKIP Numbers
    recent = [f"{n:02d}" for n in all_nums[-20:]]
    skip_str = ", ".join(set(recent))
    
    # Same Day Match Check
    same_day_match = check_same_day_matches(clean_df, selected_date, hot_10)
    
    combined_target = f"{hot_str}\n\n{due_str}"
    return combined_target, skip_str, same_day_match, hot_10

# --- 5. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    shift_cols = list(df.columns[2:8]) # मुख्य 6 शिफ्ट्स
    clean_df = process_excel_data(df, shift_cols)
    
    st.write("---")
    target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())
    
    if st.button("🚀 मास्टर विश्लेषण तैयार करें"):
        row_target = {"Type": "🎯 TARGET (Hot/Due)", "Date": target_date}
        row_match = {"Type": "🔄 SAME DAY MATCH", "Date": target_date}
        row_skip = {"Type": "❌ SKIP (Recent)", "Date": target_date}
        all_60_hot = []
        
        for name in shift_cols:
            t_logic, s_logic, m_logic, h_list = get_math_logic(clean_df, name, target_date)
            row_target[name] = t_logic if t_logic else "N/A"
            row_match[name] = m_logic
            row_skip[name] = s_logic if s_logic else "N/A"
            all_60_hot.extend(h_list)
            
        st.write("---")
        st.subheader(f"✅ 1. शिफ्ट-वाइज प्रेडिक्शन ({target_date})")
        # अब यहाँ 3 टेबल दिखेंगी: Target, Match, और Skip
        st.table(pd.DataFrame([row_target]))
        
        st.info("💡 **Same Day Match:** यह बताता है कि क्या 'Hot' नंबर उस दिन की किसी और शिफ्ट में पहले ही आ चुके हैं।")
        st.table(pd.DataFrame([row_match]))
        
        st.table(pd.DataFrame([row_skip]))
        
        # --- मास्टर प्रोबेबिलिटी चार्ट ---
        st.write("---")
        st.subheader("📊 2. मास्टर प्रोबेबिलिटी चार्ट (Common Hot Numbers)")
        final_counts = Counter(all_60_hot)
        freq_bins = {i: [] for i in range(1, 7)}
        for num, freq in final_counts.items():
            if freq in freq_bins: freq_bins[freq].append(f"{num:02d}")
            elif freq > 6: freq_bins[6].append(f"{num:02d}")
        
        if any(freq_bins.values()):
            max_len = max(len(freq_bins[i]) for i in range(1, 7))
            table_dict = {f"{i} बार कॉमन": sorted(freq_bins[i]) + [""] * (max_len - len(freq_bins[i])) for i in range(1, 7)}
            st.table(pd.DataFrame(table_dict))
            
            strong_ank = freq_bins[3] + freq_bins[4] + freq_bins[5] + freq_bins[6]
            if strong_ank:
                st.success(f"🔥 **सबसे मजबूत कॉमन अंक:** {', '.join(strong_ank)}")
        
        st.balloons()
else:
    st.info("एनालिसिस के लिए एक्सेल फाइल अपलोड करें।")
