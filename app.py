import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Supreme Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: Same-Day 100% Fix</h1>", unsafe_allow_html=True)

# --- 2. मास्टर डेटा क्लीनिंग (तारीख सुधारक) ---
def process_excel_data(df):
    temp_list = []
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # कॉलम पहचानना: B (Index 1) तारीख है, C-I (Index 2-8) शिफ्ट्स हैं
    date_col = df.columns[1] 
    shift_cols = df.columns[2:9]

    for index, row in df.iterrows():
        try:
            raw_val = row[date_col]
            if pd.isna(raw_val): continue
            
            # तारीख को शुद्ध रूप में बदलना (Year, Month, Day अलग करना)
            dt_obj = pd.to_datetime(raw_val)
            d = dt_obj.day
            m = dt_obj.month
            y = dt_obj.year
            
            for s_name in shift_cols:
                val = str(row[s_name]).strip()
                # अगर सेल में नंबर है (दशमलव हटाकर चेक करना)
                clean_val = val.split('.')[0]
                if clean_val.isdigit():
                    temp_list.append({
                        'day': d, 'month': m, 'year': y,
                        'shift': s_name, 
                        'num': int(clean_val),
                        'full_date': dt_obj.date()
                    })
        except: continue
    return pd.DataFrame(temp_list), list(shift_cols)

# --- 3. प्रेडिक्शन और सख्त मिलान ---
def get_supreme_logic(clean_df, target_shift, sel_date):
    # कैलेंडर से चुनी तारीख के टुकड़े
    sd, sm, sy = sel_date.day, sel_date.month, sel_date.year
    
    # SAME DAY MATCH (दिन, महीना, साल के आधार पर मिलान)
    today_match = clean_df[
        (clean_df['shift'] == target_shift) & 
        (clean_df['day'] == sd) & 
        (clean_df['month'] == sm) & 
        (clean_df['year'] == sy)
    ]
    
    if not today_match.empty:
        val = today_match.iloc[0]['num']
        same_day_res = f"📍 **SAME DAY:** {int(val):02d}"
    else:
        same_day_res = "📍 **SAME DAY:** --"

    # पिछला डेटा (Hot/Due) - चुनी तारीख से पहले का
    history = clean_df[
        (clean_df['shift'] == target_shift) & 
        (clean_df['full_date'] < sel_date)
    ].sort_values('full_date')
    
    if len(history) < 10:
        return f"{same_day_res}\n\n⚠️ Data Kam Hai", [], "N/A"

    all_nums = history['num'].values
    counts = Counter(all_nums[-50:])
    hot_10 = [n for n, c in counts.most_common(10)]
    hot_str = "🔥 **HOT:** " + ", ".join([f"{n:02d}" for n in hot_10])
    
    last_seen = {n: 999 for n in range(100)}
    for i, n in enumerate(all_nums): last_seen[n] = len(all_nums) - i
    due = sorted(last_seen.items(), key=lambda x: x[1], reverse=True)[:10]
    due_str = "⏳ **DUE:** " + ", ".join([f"{n:02d}" for n, g in due])
    
    recent = [f"{n:02d}" for n in all_nums[-20:]]
    
    return f"{same_day_res}\n\n{hot_str}\n\n{due_str}", hot_10, ", ".join(set(recent))

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file)
    clean_df, shift_names = process_excel_data(df_raw)
    
    st.write("---")
    # तारीख चुनने का विकल्प
    target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())
    
    if st.button("🚀 मास्टर विश्लेषण तैयार करें"):
        row_main = {"Type": "📊 ANALYTICS", "Date": target_date}
        row_skip = {"Type": "❌ SKIP", "Date": target_date}
        all_60_hot = []
        
        for name in shift_names:
            display_text, h_list, s_logic = get_supreme_logic(clean_df, name, target_date)
            row_main[name] = display_text
            row_skip[name] = s_logic
            all_60_hot.extend(h_list)
            
        st.write("---")
        st.subheader(f"✅ 1. शिफ्ट-वाइज चार्ट ({target_date})")
        st.table(pd.DataFrame([row_main]))
        
        st.subheader("❌ 2. स्किप चार्ट")
        st.table(pd.DataFrame([row_skip]))
        
        # --- मास्टर प्रोबेबिलिटी ---
        st.write("---")
        st.subheader("📊 3. मास्टर प्रोबेबिलिटी चार्ट")
        final_counts = Counter(all_60_hot)
        freq_bins = {i: [] for i in range(1, 7)}
        for num, freq in final_counts.items():
            if freq in freq_bins: freq_bins[freq].append(f"{num:02d}")
            elif freq > 6: freq_bins[6].append(f"{num:02d}")
        
        if any(freq_bins.values()):
            max_len = max(len(freq_bins[i]) for i in range(1, 7)) if any(freq_bins.values()) else 1
            table_dict = {f"{i} बार": sorted(freq_bins[i]) + [""] * (max_len - len(freq_bins[i])) for i in range(1, 7)}
            st.table(pd.DataFrame(table_dict))
        
        st.balloons()
else:
    st.info("एक्सेल फाइल अपलोड करें।")
                    
