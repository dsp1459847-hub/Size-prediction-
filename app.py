import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Supreme Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: Ultra-Fix Engine</h1>", unsafe_allow_html=True)

# --- 2. स्मार्ट डेटा प्रोसेसिंग (Improved) ---
def process_excel_data(df):
    # कॉलम के नाम साफ करना
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # 1. तारीख वाला कॉलम ढूंढना (Column 1 या जिसमें 'DATE' हो)
    date_col = None
    for col in df.columns:
        if 'DATE' in col or 'TARIK' in col or 'DAT' in col:
            date_col = col
            break
    if not date_col:
        date_col = df.columns[1] # Default to second column (B)

    # 2. शिफ्ट वाले कॉलम (DS, FD, GD, GL आदि) - Index 2 से आगे
    exclude = ['S.NO', 'SNO', 'DATE', 'DAY', 'MONTH', 'YEAR', 'UNNAMED', 'INDEX']
    shift_cols = [c for c in df.columns if not any(x in c for x in exclude) and len(str(c)) <= 5]
    
    temp_list = []
    for index, row in df.iterrows():
        try:
            raw_val = row[date_col]
            if pd.isna(raw_val): continue
            
            # तारीख को Normalize करना
            dt_obj = pd.to_datetime(raw_val, errors='coerce')
            if pd.isna(dt_obj): continue
            
            for s_name in shift_cols:
                val = str(row[s_name]).strip().split('.')[0]
                if val.isdigit():
                    temp_list.append({
                        'day': dt_obj.day, 'month': dt_obj.month, 'year': dt_obj.year,
                        'shift': s_name, 'num': int(val), 'full_date': dt_obj.date()
                    })
        except: continue
        
    return pd.DataFrame(temp_list), shift_cols

# --- 3. प्रेडिक्शन लॉजिक ---
def get_supreme_logic(clean_df, target_shift, sel_date):
    sd, sm, sy = sel_date.day, sel_date.month, sel_date.year
    
    # SAME DAY MATCH
    today_match = clean_df[
        (clean_df['shift'] == target_shift) & 
        (clean_df['day'] == sd) & (clean_df['month'] == sm) & (clean_df['year'] == sy)
    ]
    
    same_day_res = f"📍 **SAME DAY:** {int(today_match.iloc[0]['num']):02d}" if not today_match.empty else "📍 **SAME DAY:** --"

    # पिछला डेटा (Hot/Due)
    history = clean_df[(clean_df['shift'] == target_shift) & (clean_df['full_date'] < sel_date)].sort_values('full_date')
    
    if len(history) < 5:
        return f"{same_day_res}\n\n⚠️ Data Kam Hai", [], "N/A"

    all_nums = history['num'].values
    hot_10 = [n for n, c in Counter(all_nums[-60:]).most_common(10)]
    
    last_seen = {n: 999 for n in range(100)}
    for i, n in enumerate(all_nums): last_seen[n] = len(all_nums) - i
    due_nums = [x[0] for x in sorted(last_seen.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    display = f"{same_day_res}\n\n🔥 **HOT:** {', '.join([f'{n:02d}' for n in hot_10])}\n\n⏳ **DUE:** {', '.join([f'{n:02d}' for n in due_nums])}"
    
    recent = ", ".join(set([f"{n:02d}" for n in all_nums[-20:]]))
    return display, hot_10, recent

# --- 4. UI Dashboard ---
uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        # इंजन openpyxl का उपयोग करना सुरक्षित है
        df_raw = pd.read_excel(uploaded_file, engine='openpyxl')
        clean_df, shift_names = process_excel_data(df_raw)
        
        if clean_df.empty:
            st.error("❌ डेटा रीड नहीं हो पाया। कृपया सुनिश्चित करें कि 'DATE' कॉलम में सही तारीखें हैं।")
        else:
            target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())
            
            if st.button("🚀 विश्लेषण शुरू करें"):
                row_main, row_skip, all_60_hot = {"Type": "📊 ANALYTICS"}, {"Type": "❌ SKIP"}, []
                
                for name in shift_names:
                    display_text, h_list, s_logic = get_supreme_logic(clean_df, name, target_date)
                    row_main[name], row_skip[name] = display_text, s_logic
                    all_60_hot.extend(h_list)
                
                st.subheader(f"✅ शिफ्ट-वाइज चार्ट ({target_date})")
                st.table(pd.DataFrame([row_main]))
                st.subheader("❌ स्किप चार्ट")
                st.table(pd.DataFrame([row_skip]))
                
                # प्रोबेबिलिटी चार्ट
                counts = Counter(all_60_hot)
                freq_bins = {i: sorted([f"{n:02d}" for n, f in counts.items() if f == i]) for i in range(1, 7)}
                max_l = max(len(v) for v in freq_bins.values()) if any(freq_bins.values()) else 1
                st.subheader("📊 मास्टर प्रोबेबिलिटी")
                st.table(pd.DataFrame({f"{i} बार": v + [""]*(max_l-len(v)) for i, v in freq_bins.items()}))
                st.balloons()
            
    except Exception as e:
        st.error(f"❌ एरर: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
