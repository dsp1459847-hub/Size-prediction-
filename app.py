import streamlit as st
import pandas as pd
from collections import Counter
import datetime
import io

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="MAYA AI: Manual Fix", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: 100% Manual Reader</h1>", unsafe_allow_html=True)

# --- 2. 100% मैनुअल डेटा प्रोसेसिंग ---
def process_excel_manual(df):
    # कॉलम के नाम हटाकर उन्हें 0, 1, 2... में बदल देना (ताकि नाम का लफड़ा ही खत्म हो जाए)
    df.columns = range(df.shape[1])
    
    # कॉलम 1 (B) = तारीख | कॉलम 2 से 8 (C से I) = शिफ्ट्स
    date_idx = 1
    shift_indices = range(2, 9)
    
    # शिफ्ट के नाम (DS, FD, GD, GL, DB, SG, DL) - आप अपनी पसंद से बदल सकते हैं
    shift_names = ["DS", "FD", "GD", "GL", "DB", "SG", "DL"]
    
    temp_list = []
    for index, row in df.iterrows():
        try:
            raw_val = row[date_idx]
            if pd.isna(raw_val): continue
            
            # तारीख को साफ़ करना
            dt_obj = pd.to_datetime(raw_val, errors='coerce')
            if pd.isna(dt_obj): continue
            
            for i, s_idx in enumerate(shift_indices):
                val = str(row[s_idx]).strip().split('.')[0]
                if val.isdigit():
                    temp_list.append({
                        'day': dt_obj.day, 'month': dt_obj.month, 'year': dt_obj.year,
                        'shift': shift_names[i], 'num': int(val), 'full_date': dt_obj.date()
                    })
        except: continue
        
    return pd.DataFrame(temp_list), shift_names

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
# फ़ाइल अपलोड करते समय Cache साफ़ करने के लिए 'key' का इस्तेमाल
uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="excel_uploader")

if uploaded_file:
    try:
        # फ़ाइल को बाइट्स की तरह पढ़ना (ताकि कोई एरर न आए)
        input_data = uploaded_file.read()
        df_raw = pd.read_excel(io.BytesIO(input_data), engine='openpyxl')
        
        clean_df, shift_names = process_excel_manual(df_raw)
        
        if clean_df.empty:
            st.error("❌ डेटा पढ़ा नहीं जा सका। कृपया चेक करें कि कॉलम B में तारीखें हैं या नहीं।")
        else:
            st.success("✅ फ़ाइल सफलतापूर्वक रीड हो गई!")
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
        st.error(f"❌ गड़बड़ हुई: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
