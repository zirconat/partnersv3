import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import io
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Unified Contact Database", layout="wide")

# --- 2. HELPERS (TIMEZONE, AGE & IMAGE PROCESSING) ---
def get_sg_time():
    """Returns current Singapore time (UTC+8)."""
    return datetime.utcnow() + timedelta(hours=8)

def calculate_age(birthdate):
    """Calculates age based on the current date (Year: 2026)."""
    if not birthdate:
        return "N/A"
    today = get_sg_time().date()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def process_uploaded_image(uploaded_file):
    """Converts a JPG/PNG/JPEG file to a Base64 string for persistent storage."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode()
        return f"data:image/jpeg;base64,{base64_str}"
    return None

def get_current_user():
    """Simulated Production User Object."""
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {"email": "admin@company.com", "name": "Alex Tan", "role": "Admin"}
    return st.session_state.user_info

# --- 3. SESSION STATE INITIALIZATION & MULTI-COMPANY SAMPLE DATA ---
if 'contacts_db' not in st.session_state:
    ts_now = get_sg_time().strftime("%d %b %y, %H:%M")
    st.session_state.contacts_db = [
        {
            "id": 1, "name": "Lim Boon Hock", "birthdate": date(1960, 1, 5), "company": "Global Corp Group",
            "appointment": "Group Chairman", "country": "Singapore", "mobile": "+65 9000 1111", "office": "+65 6111 2222",
            "email": "bh.lim@globalcorp.com", "address": "1 Marina Boulevard, Singapore", "hobbies": "Wine Tasting",
            "dietary": "Halal", "receptions": ["NYR"], "festivities": ["Chinese New Year"], "assumed_date": date(2010, 5, 1),
            "retire_date": None, "marital_status": "Married", "spouse": "Siti Aminah", "children": "3",
            "reporting_to": None, "vehicle_reg": "S1K", "golf": "Yes", "handicap": "12", "status": "Active",
            "category": "Chief", "tier": "A", "photo": "https://www.w3schools.com/howto/img_avatar2.png",
            "last_updated_by_name": "System", "last_updated_at": ts_now, "history": [{"ts": ts_now, "user": "System", "msg": "Initial Entry"}], "comments": []
        },
        {
            "id": 2, "name": "Tan Ah Teck", "birthdate": date(1975, 2, 14), "company": "Global Corp Group",
            "appointment": "CEO, Singapore", "country": "Singapore", "mobile": "+65 9123 4567",
            "reporting_to": "Lim Boon Hock", "status": "Active", "category": "Chief", "tier": "A",
            "photo": "https://www.w3schools.com/howto/img_avatar.png", "last_updated_at": ts_now, 
            "history": [{"ts": ts_now, "user": "System", "msg": "Initial Entry"}], "comments": []
        },
        {
            "id": 3, "name": "James Smith", "birthdate": date(1982, 3, 20), "company": "TechVantage Ltd",
            "appointment": "Managing Director", "country": "Australia", "mobile": "+61 412 345 678",
            "reporting_to": "Lim Boon Hock", "status": "Active", "category": "Overseas", "tier": "B",
            "photo": "https://www.w3schools.com/howto/img_avatar.png", "last_updated_at": ts_now, 
            "history": [{"ts": ts_now, "user": "System", "msg": "Initial Entry"}], "comments": []
        },
        {
            "id": 4, "name": "Sarah Connor", "birthdate": date(1985, 1, 28), "company": "TechVantage Ltd",
            "appointment": "Operations Manager", "country": "Australia", "mobile": "+61 499 888 777",
            "reporting_to": "James Smith", "status": "Active", "category": "Overseas", "tier": "C",
            "photo": "https://www.w3schools.com/howto/img_avatar2.png", "last_updated_at": ts_now, 
            "history": [{"ts": ts_now, "user": "System", "msg": "Initial Entry"}], "comments": []
        }
    ]

# --- 4. DATA CONSTANTS ---
CATEGORIES = ["Chief", "Deputy Chief", "Overseas", "Local", "Others"]
CAT_PRIORITY = {"Chief": 1, "Deputy Chief": 2, "Overseas": 3, "Local": 4, "Others": 5}
STATUS_OPTIONS = ["Active", "Inactive"]
COUNTRIES = ["Singapore", "Malaysia", "USA", "UK", "Australia", "Japan", "China", "India"]
TIERS = ["A", "B", "C", "D"]
FESTIVITIES = ["Chinese New Year", "Hari Raya", "Deepavali", "Christmas", "National Day"]
RECEPTIONS = ["ALSE", "NYR", "BigShow", "National Day"]
MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed"]

# --- 5. AUTHENTICATION ---
user = get_current_user()
IS_ADMIN = user['role'] == "Admin"

# --- 6. SIDEBAR: SEARCH, BULK & INDIVIDUAL ENTRY ---
with st.sidebar:
    st.title("👤 User Profile")
    st.markdown(f"### Welcome, **{user['name']}**")
    
    st.divider()
    test_role = st.toggle("Simulate Admin Mode", value=IS_ADMIN)
    if test_role != IS_ADMIN:
        st.session_state.user_info['role'] = "Admin" if test_role else "User"
        st.rerun()

    if IS_ADMIN:
        st.divider()
        st.header("📥 Bulk Import")
        # Template Generator
        all_keys = list(st.session_state.contacts_db[0].keys())
        exclude = ['id', 'history', 'comments', 'last_updated_at', 'last_updated_by_name']
        template_cols = [k for k in all_keys if k not in exclude]
        template_df = pd.DataFrame(columns=template_cols)
        csv_template = template_df.to_csv(index=False)
        st.download_button("📂 Download CSV Template", data=csv_template, file_name="contact_template.csv", mime="text/csv")
        
        uploaded_csv = st.file_uploader("Upload CSV Data", type="csv")
        if uploaded_csv:
            df_up = pd.read_csv(uploaded_csv)
            if st.button("Confirm Bulk Import"):
                ts = get_sg_time().strftime("%d %b %y, %H:%M")
                for _, row in df_up.iterrows():
                    new_id = max([x['id'] for x in st.session_state.contacts_db], default=0) + 1
                    entry = {k: (row[k] if k in row else None) for k in template_cols}
                    entry.update({"id": new_id, "last_updated_at": ts, "last_updated_by_name": user['name'], 
                                  "history": [{"ts": ts, "user": user['name'], "msg": "Bulk Import"}], "comments": [], 
                                  "photo": "https://www.w3schools.com/howto/img_avatar.png"})
                    st.session_state.contacts_db.append(entry)
                st.success(f"Successfully imported {len(df_up)} contacts.")
                st.rerun()

        st.divider()
        st.header("➕ Individual Entry")
        with st.expander("New Contact Form"):
            with st.form("sidebar_add", clear_on_submit=True):
                n_name = st.text_input("Full Name*")
                n_comp = st.text_input("Company*")
                n_appt = st.text_input("Appointment")
                n_rep = st.selectbox("Reporting To", [None] + [p['name'] for p in st.session_state.contacts_db])
                
                b_mode = st.radio("Birthdate Logic", ["Input Date", "Input Age Only"], horizontal=True)
                if b_mode == "Input Date":
                    n_bday = st.date_input("Birthdate", value=date(1980,1,1))
                else:
                    n_age_val = st.number_input("Age", value=40)
                    n_bday = date(get_sg_time().year - n_age_val, 1, 1)

                n_ctry = st.selectbox("Country", COUNTRIES)
                n_cat = st.selectbox("Category", CATEGORIES)
                n_tier = st.selectbox("Tier", TIERS)
                n_stat = st.selectbox("Status", STATUS_OPTIONS)
                
                if st.form_submit_button("Save Record"):
                    if n_name and n_comp:
                        ts = get_sg_time().strftime("%d %b %y, %H:%M")
                        new_id = max([x['id'] for x in st.session_state.contacts_db], default=0) + 1
                        st.session_state.contacts_db.append({
                            "id": new_id, "name": n_name, "company": n_comp, "appointment": n_appt, "birthdate": n_bday,
                            "country": n_ctry, "category": n_cat, "tier": n_tier, "status": n_stat, "reporting_to": n_rep,
                            "photo": "https://www.w3schools.com/howto/img_avatar.png", "last_updated_at": ts, 
                            "last_updated_by_name": user['name'], "history": [{"ts": ts, "user": user['name'], "msg": "Manual Creation"}], "comments": []
                        })
                        st.rerun()

    st.divider()
    st.header("🔍 Filters")
    search_q = st.text_input("Keyword Search").lower()
    f_country = st.multiselect("Country", COUNTRIES)
    f_cat = st.multiselect("Category", CATEGORIES)

# --- 7. FILTERING & SORTING ---
filtered_list = [c for c in st.session_state.contacts_db if 
                (not search_q or search_q in c.get('name','').lower() or search_q in c.get('company','').lower()) and 
                (not f_country or c.get('country') in f_country) and (not f_cat or c.get('category') in f_cat)]

sorted_list = sorted(filtered_list, key=lambda x: (x.get('country','zzz').lower(), x.get('company','zzz').lower(), CAT_PRIORITY.get(x.get('category'), 5)))

# --- 8. MAIN DASHBOARD ---
st.title("📇 Integrated Contact Dashboard")

# 8.1 BIRTHDAY SPOTLIGHT (Current + Next 2 Months)
now = get_sg_time()
upcoming_months = [(now.month + i - 1) % 12 + 1 for i in range(3)]
bday_pool = [c for c in st.session_state.contacts_db if c.get('birthdate') and c['birthdate'].month in upcoming_months]

if bday_pool:
    with st.expander("🎂 Birthday Spotlight (Next 3 Months)", expanded=True):
        for m in upcoming_months:
            m_name = datetime(2000, m, 1).strftime('%B')
            m_bdays = [b for b in bday_pool if b['birthdate'].month == m]
            if m_bdays:
                st.markdown(f"**{m_name}**")
                cols = st.columns(6)
                for idx, p in enumerate(m_bdays):
                    with cols[idx % 6]:
                        st.info(f"**{p['name']}**\n\n({p['birthdate'].strftime('%d %b')})")

# 8.2 HIERARCHY TREE
with st.expander("🌳 Multi-Company Reporting Hierarchy"):
    
    companies = sorted(list(set([x['company'] for x in st.session_state.contacts_db])))
    for comp in companies:
        st.markdown(f"#### 🏢 {comp}")
        comp_contacts = [x for x in st.session_state.contacts_db if x['company'] == comp]
        for c in comp_contacts:
            if c.get('reporting_to'):
                st.markdown(f"↳ **{c['name']}** ({c['appointment']}) reports to **{c['reporting_to']}**")
            else:
                st.markdown(f"👑 **{c['name']}** ({c['appointment']}) [Head of Chain]")

# 8.3 MAIN LISTING
curr_country, curr_company = None, None
all_names = [p['name'] for p in st.session_state.contacts_db]

for i, c in enumerate(sorted_list):
    safe_anchor = c['name'].replace(" ", "_")
    st.markdown(f'<div id="{safe_anchor}"></div>', unsafe_allow_html=True)

    if c.get('country') != curr_country:
        curr_country = c.get('country')
        st.markdown(f"<h1 style='color: #1E3A8A; border-bottom: 2px solid #1E3A8A; padding-top: 20px;'>🌍 {curr_country}</h1>", unsafe_allow_html=True)
    
    if c.get('company') != curr_company:
        curr_company = c.get('company')
        st.markdown(f"<h3 style='background-color: #F3F4F6; padding: 10px; border-radius: 5px; margin-top: 10px;'>🏢 {curr_company}</h3>", unsafe_allow_html=True)

    age = calculate_age(c.get('birthdate'))
    bday_str = c.get('birthdate').strftime("%d %b %Y") if c.get('birthdate') else "N/A"
    
    with st.container(border=True):
        # Header Row
        h1, h2 = st.columns([3, 1.5])
        with h2:
            l1, l2, l3 = st.columns(3)
            s_color = "green" if c.get('status') == "Active" else "grey"
            l1.markdown(f":{s_color}[● {c.get('status','Active')}]")
            l2.markdown(f":blue[● {c.get('category','Local')}]")
            l3.markdown(f":orange[● Tier {c.get('tier','D')}]")

        col_img, col_main = st.columns([1, 4])
        with col_img:
            st.image(c.get('photo'), width=140)
            if st.button("🔎 Zoom", key=f"z_{c['id']}"): 
                st.dialog("Full Image")(lambda: st.image(c.get('photo'), use_container_width=True))()

        with col_main:
            # Layout adjustment: Name then Appointment/Company
            st.markdown(f"## **{c.get('name')}** ({age} yrs)")
            st.markdown(f"#### {c.get('appointment')}, {c.get('company')}")
            
            d1, d2, d3, d4 = st.columns(4)
            d1.write(f"📍 {c.get('country')}")
            d1.write(f"🎂 **{bday_str}**")
            d2.markdown(f"📱 [M: {c.get('mobile', 'N/A')}](tel:{c.get('mobile')})")
            d2.write(f"📞 O: {c.get('office', 'N/A')}")
            d2.markdown(f"📧 [**{c.get('email', 'N/A')}**](mailto:{c.get('email')})")
            
            rep = c.get('reporting_to', 'N/A')
            if rep in all_names:
                d3.markdown(f"👤 **Reports to:** [{rep}](#{rep.replace(' ','_')})")
            else:
                d3.write(f"👤 **Reports to:** {rep}")
            d3.write(f"💍 **Spouse:** {c.get('spouse', 'N/A')}")
            
            golf_icon = "⛳" if c.get('golf') == "Yes" else "⚪"
            d4.write(f"**{golf_icon} Golf:** {c.get('golf','No')}")
            if c.get('golf') == "Yes":
                d4.write(f"**Hcp:** {c.get('handicap','N/A')}")

        with st.expander("📄 View Full Profile & Logistics"):
            v1, v2 = st.columns(2)
            with v1:
                st.write(f"**Office Address:** {c.get('address', 'N/A')}")
                st.write(f"**Hobbies:** {c.get('hobbies', 'N/A')}")
                st.write(f"**Dietary:** {c.get('dietary', 'N/A')}")
                st.write(f"**Receptions:** {', '.join(c.get('receptions', []))}")
                st.write(f"**Festivities:** {', '.join(c.get('festivities', []))}")
            with v2:
                child_val = c.get('children', 'Uncertain / Unknown')
                st.write(f"**Marital:** {c.get('marital_status', 'N/A')}")
                st.markdown(f"**Children:** {child_val}")
                st.write(f"**Vehicle Reg:** {c.get('vehicle_reg', 'N/A')}")
                st.write(f"**Tenure Start:** {c.get('assumed_date', 'N/A')}")

        if IS_ADMIN:
            with st.expander("🛠️ ADMIN: Full Record Edit & Selective Sync"):
                with st.form(f"edit_{c['id']}"):
                    t1, t2, t3 = st.tabs(["💼 Professional", "🚚 Logistics", "👥 Personal/Golf"])
                    with t1:
                        c1, c2 = st.columns(2)
                        u_name = c1.text_input("Name", value=c.get('name'))
                        u_photo_file = c2.file_uploader("Update Photo", type=["jpg", "png"])
                        u_comp = c1.text_input("Company", value=c.get('company'))
                        u_appt = c2.text_input("Appointment", value=c.get('appointment'))
                        u_rep = c1.text_input("Reporting To", value=c.get('reporting_to','')) 
                        
                        st.write("---")
                        b_mode_edit = st.radio("Birthdate Logic", ["Input Date", "Input Age Only"], key=f"edit_bmode_{c['id']}", horizontal=True)
                        if b_mode_edit == "Input Date":
                            u_bday = st.date_input("Birthdate", value=c.get('birthdate', date(1980,1,1)))
                        else:
                            curr_calc_age = calculate_age(c.get('birthdate'))
                            u_age_val = st.number_input("Age", value=int(curr_calc_age) if isinstance(curr_calc_age, int) else 40)
                            u_bday = date(get_sg_time().year - u_age_val, 1, 1)
                        st.write("---")

                        u_ctry = c1.selectbox("Country", COUNTRIES, index=COUNTRIES.index(c.get('country')) if c.get('country') in COUNTRIES else 0)
                        u_tier = c1.selectbox("Tiering", TIERS, index=TIERS.index(c.get('tier')) if c.get('tier') in TIERS else 0)
                        u_cat = c2.selectbox("Category", CATEGORIES, index=CATEGORIES.index(c.get('category')) if c.get('category') in CATEGORIES else 0)
                        u_stat = c2.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(c.get('status')) if c.get('status') in STATUS_OPTIONS else 0)
                    with t2:
                        c1, c2 = st.columns(2)
                        u_addr = c1.text_area("Office Address", value=c.get('address',''))
                        u_fest = st.multiselect("Festivities", FESTIVITIES, default=c.get('festivities',[]))
                        u_recep = st.multiselect("Receptions", RECEPTIONS, default=c.get('receptions',[]))
                        u_veh = c2.text_input("Vehicle Reg", value=c.get('vehicle_reg',''))
                        u_mob = c1.text_input("Mobile No.", value=c.get('mobile',''))
                        u_off = c2.text_input("Office No.", value=c.get('office',''))
                        u_email = st.text_input("Email", value=c.get('email',''))
                    with t3:
                        c1, c2 = st.columns(2)
                        u_mar = c1.selectbox("Marital", MARITAL_STATUSES, index=MARITAL_STATUSES.index(c.get('marital_status')) if c.get('marital_status') in MARITAL_STATUSES else 0)
                        u_spouse = c2.text_input("Spouse Name", value=c.get('spouse',''))
                        u_child = c1.text_input("Children", value=c.get('children', 'Uncertain / Unknown'))
                        u_diet = c2.text_input("Dietary", value=c.get('dietary',''))
                        u_hob = c1.text_input("Hobbies", value=c.get('hobbies',''))
                        u_golf = c1.selectbox("Golf?", ["No", "Yes"], index=1 if c.get('golf')=="Yes" else 0)
                        u_handi = c2.text_input("Handicap", value=c.get('handicap',''))

                    # LIVE SYNC PREVIEW
                    colleagues = [x for x in st.session_state.contacts_db if x['company'] == u_comp and x['id'] != c['id']]
                    st.divider()
                    st.markdown("### 🔄 Selective Bulk Sync Preview")
                    sync_fields = []
                    s_c1, s_c2 = st.columns(2)
                    if s_c1.checkbox("Sync Office Address to colleagues", key=f"s_addr_{c['id']}"): sync_fields.append(('address', u_addr))
                    if s_c1.checkbox("Sync Tiering to colleagues", key=f"s_tier_{c['id']}"): sync_fields.append(('tier', u_tier))
                    
                    if sync_fields and colleagues:
                        st.warning(f"⚠️ **Live Preview: Updating {len(colleagues)} other contacts at {u_comp}:**")
                        for idx, col_entry in enumerate(colleagues, 1):
                            st.markdown(f"{idx}. **{col_entry['name']}** ({col_entry['appointment']})")

                    if st.form_submit_button("Commit Changes"):
                        ts = get_sg_time().strftime("%d %b %y, %H:%M")
                        new_data = {
                            "name": u_name, "company": u_comp, "appointment": u_appt, "birthdate": u_bday,
                            "country": u_ctry, "tier": u_tier, "category": u_cat, "status": u_stat, "address": u_addr, "email": u_email,
                            "festivities": u_fest, "receptions": u_recep, "vehicle_reg": u_veh, "mobile": u_mob, "office": u_off,
                            "marital_status": u_mar, "spouse": u_spouse, "children": u_child, "reporting_to": u_rep,
                            "dietary": u_diet, "hobbies": u_hob, "golf": u_golf, "handicap": u_handi
                        }
                        
                        history_msgs = []
                        for field, new_val in new_data.items():
                            old_val = c.get(field)
                            if str(old_val) != str(new_val):
                                history_msgs.append(f"**{field.replace('_',' ').title()}**: '{old_val}' ➜ '{new_val}'")
                        
                        new_photo = process_uploaded_image(u_photo_file) or c.get('photo')
                        for fk, fv in sync_fields:
                            for col in colleagues:
                                col[fk] = fv
                                col['last_updated_at'], col['last_updated_by_name'] = ts, f"Sync via {user['name']}"
                                col['history'].append({"ts": ts, "user": user['name'], "msg": f"Bulk Sync: {fk} updated"})
                        
                        c.update(new_data)
                        c['photo'] = new_photo
                        c['last_updated_at'], c['last_updated_by_name'] = ts, user['name']
                        if history_msgs:
                            c['history'].append({"ts": ts, "user": user['name'], "msg": " | ".join(history_msgs)})
                        st.rerun()

        st.info(f"🚩 **Last Updated:** {c.get('last_updated_at')} by **{c.get('last_updated_by_name')}**")
        
        h_col, c_col = st.columns(2)
        with h_col:
            with st.expander(f"🕒 Audit History ({len(c.get('history', []))})"):
                for entry in reversed(c.get('history', [])):
                    st.caption(f"📅 {entry['ts']} | 👤 {entry['user']}")
                    st.markdown(f"- {entry['msg']}")
        with c_col:
            with st.expander(f"💬 Comments ({len(c.get('comments', []))})"):
                for m in c.get('comments', []): st.write(f"**{m['user_name']}:** {m['text']}")
                new_com = st.text_input("Add Comment", key=f"com_{c['id']}")
                if st.button("Post", key=f"btn_{c['id']}"):
                    c['comments'].append({"user_name": user['name'], "text": new_com})
                    ts = get_sg_time().strftime("%d %b %y, %H:%M")
                    c['history'].append({"ts": ts, "user": user['name'], "msg": "New Comment Added"})
                    st.rerun()

st.divider()
st.download_button("📥 Full Export (CSV)", data=pd.DataFrame(st.session_state.contacts_db).astype(str).to_csv(index=False), file_name="db_export.csv")