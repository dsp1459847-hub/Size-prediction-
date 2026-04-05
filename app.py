import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Supreme Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: Supreme Master (Same-Day View)</h1>", unsafe_allow_html=True)

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

# --- 3. मास्टर लॉजिक (आपके बताए फॉर्मेट में) ---
def get_supreme_logic(clean_df, target_shift, selected_date):
    # A. Same Day Result (शीट में उस दिन उस शिफ्ट में क्या नंबर है)
    today_val = clean_df[(clean_df['shift'] == target_shift) & (clean_df['date'] == selected_date)]
    if not today_val.empty:
        same_day_res = f"📍 **SAME DAY:** {today_val.iloc[0]['num']:02d}"
    else:
        same_day_res = "📍 **SAME DAY:** --"

    # B. पिछला डेटा (Hot/Due निकालने के लिए)
    history_data = clean_df[(clean_df['shift'] == target_shift) & (clean_df['date'] < selected_date)].sort_values('date')
    
    if len(history_data) < 20:
        return f"{same_day_res}\n\n⚠️ Data Kam Hai", [], "N/A"

    all_nums = history_data['num'].values
    
    # HOT Numbers (Top 10)
    counts = Counter(all_nums[-45:])
    hot_10 = [n for n, c in counts.most_common(10)]
    hot_str = "🔥 **HOT:** " + ", ".join([f"{n:02d}" for n in hot_10])
    
    # DUE Numbers (Top 10)
    last_seen = {n: 999 for n in range(100)}
    for i, n in enumerate(all_nums):
        last_seen[n] = len(all_nums) - i
    due = sorted(last_seen.items(), key=lambda x: x[1], reverse=True)[:10]
    due_nums = [x[0] for x in due]
    due_str = "⏳ **DUE:** " + ", ".join([f"{n:02d}" for n in due_nums])
    
    # SKIP Numbers
    recent = [f"{n:02d}" for n in all_nums[-20:]]
    skip_str = ", ".join(set(recent))
    
    # पूरा कॉम्बिनेशन (Order: Same Day -> Hot -> Due)
    full_display = f"{same_day_res}\n\n{hot_str}\n\n{due_str}"
    
    return full_display, hot_10, skip_str

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    shift_cols = list(df.columns[2:8]) # C से H शिफ्ट्स
    clean_df = process_excel_data(df, shift_cols)
    
    st.write("---")
    target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())
    
    if st.button("🚀 मास्टर विश्लेषण तैयार करें"):
        row_main = {"Type": "📊 ANALYTICS (Same/Hot/Due)", "Date": target_date}
        row_skip = {"Type": "❌ SKIP (Recent)", "Date": target_date}
        all_60_hot = []
        
        for name in shift_cols:
            display_text, h_list, s_logic = get_supreme_logic(clean_df, name, target_date)
            row_main[name] = display_text
            row_skip[name] = s_logic
            all_60_hot.extend(h_list)
            
        st.write("---")
        st.subheader(f"✅ 1. शिफ्ट-वाइज चार्ट ({target_date})")
        
        # मुख्य टेबल (Same Day, Hot, Due एक साथ)
        st.table(pd.DataFrame([row_main]))
        
        st.subheader("❌ 2. स्किप चार्ट (Recent Numbers)")
        st.table(pd.DataFrame([row_skip]))
        
        # --- मास्टर प्रोबेबिलिटी चार्ट ---
        st.write("---")
        st.subheader("📊 3. मास्टर प्रोबेबिलिटी चार्ट (Common Hot Numbers)")
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
            
