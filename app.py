import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="لوحة القيادة - جهة سوس ماسة",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* { font-family: 'Cairo', sans-serif !important; }
html, body, .stApp { direction: rtl !important; }

/* ── Sidebar RIGHT ── */
section[data-testid="stSidebar"] {
    right: 0 !important;
    left: auto !important;
    background: linear-gradient(180deg, #0d2137 0%, #1a3a5c 60%, #0d2137 100%);
}
section[data-testid="stSidebar"] > div {
    padding: 1rem 1rem 1rem 1rem;
}
/* push main content away from right */
.main .block-container { padding-right: 1rem; padding-left: 1rem; }

/* Sidebar text */
section[data-testid="stSidebar"] * { color: #e8f4fd !important; direction: rtl; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #ffffff !important; }
section[data-testid="stSidebar"] label { color: #a8d8f0 !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }

/* KPI Cards */
.kpi-card {
    background: white; border-radius: 14px; padding: 18px 12px;
    text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    border-top: 4px solid; margin-bottom: 10px; direction: rtl;
}
.kpi-card .value { font-size: 1.8rem; font-weight: 700; }
.kpi-card .label { font-size: 0.8rem; color: #666; margin-top: 4px; }
.kpi-blue   { border-color:#2196F3; color:#2196F3; }
.kpi-green  { border-color:#4CAF50; color:#4CAF50; }
.kpi-orange { border-color:#FF9800; color:#FF9800; }
.kpi-purple { border-color:#9C27B0; color:#9C27B0; }
.kpi-red    { border-color:#F44336; color:#F44336; }
.kpi-teal   { border-color:#009688; color:#009688; }

/* Section title */
.section-title {
    background: linear-gradient(90deg,#1a3a5c,#2196F3);
    color:white !important; padding:10px 20px; border-radius:10px;
    font-size:1.05rem; font-weight:700; margin:15px 0 10px; direction:rtl;
}

/* Header */
.header-banner {
    background: linear-gradient(135deg,#1a3a5c 0%,#2c6fad 50%,#1a3a5c 100%);
    color:white; padding:22px 30px; border-radius:16px;
    margin-bottom:20px; text-align:center; direction:rtl;
}
.header-banner h1 { font-size:1.7rem; margin:0; }
.header-banner p  { font-size:0.88rem; opacity:.85; margin:5px 0 0; }

/* Login page */
.login-box {
    max-width:420px; margin:80px auto; background:white;
    border-radius:20px; padding:40px; box-shadow:0 8px 40px rgba(0,0,0,0.12);
    text-align:center; direction:rtl;
}
.login-box h2 { color:#1a3a5c; font-size:1.6rem; margin-bottom:8px; }
.login-box p  { color:#666; font-size:0.9rem; margin-bottom:24px; }

/* Tree */
.tree-container {
    background:white; border-radius:12px; padding:15px;
    box-shadow:0 2px 10px rgba(0,0,0,0.06); direction:rtl; margin-bottom:12px;
}
.central-node {
    background:#1a3a5c; color:white !important; padding:8px 15px;
    border-radius:8px; font-weight:700; margin-bottom:8px; display:inline-block;
}
.branch-node {
    background:#e3f2fd; color:#1a3a5c !important; padding:5px 12px;
    border-radius:6px; margin:3px 0 3px 25px;
    border-right:3px solid #2196F3; font-size:0.85rem;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ─── LOGIN ───────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
USERS = {
    "admin":    "souss2025",
    "مدير":     "planif2025",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def do_login(user, pwd):
    if user in USERS and USERS[user] == pwd:
        st.session_state.logged_in = True
        st.session_state.username = user
        st.rerun()
    else:
        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

def do_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

if not st.session_state.logged_in:
    # ── صفحة تسجيل الدخول ──
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
        <div class="login-box">
            <div style="font-size:3.5rem">🏫</div>
            <h2>لوحة القيادة</h2>
            <p>التعليم الابتدائي — جهة سوس ماسة</p>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("👤 اسم المستخدم", key="li_user", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password", key="li_pass", placeholder="أدخل كلمة المرور")
        if st.button("🔓 تسجيل الدخول", use_container_width=True, type="primary"):
            do_login(username, password)
        st.caption("للدعم الفني: المديرية الإقليمية — سوس ماسة")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# ─── DATA ────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, header=1)
    num_cols = [
        'مج التلاميذ (ذكور و اناث)',
        'التلاميذ بالأقسام المشتركة (ذكور و اناث)',
        'مج التلميذات',
        'الاناث بالأقسام المشتركة',
        'مج الأقسام',
        'الأقسام المشتركة منهم'
    ]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['X'] = pd.to_numeric(df['X'], errors='coerce')
    df['Y'] = pd.to_numeric(df['Y'], errors='coerce')

    etab = df.groupby('CD_ETAB').agg(
        nom_ar        = ('NOM_ETABA', 'first'),
        type_etab     = ('LA_NETAB',  'first'),
        prov          = ('LA_PROV',   'first'),
        commune       = ('COMMUNE',   'first'),
        milieu        = ('LA_MIL',    'first'),
        cd_rat        = ('Cd_RAT',    'first'),
        gresa_modi    = ('Gresa_modi','first'),
        total_eleves  = ('مج التلاميذ (ذكور و اناث)', 'sum'),
        eleves_mix    = ('التلاميذ بالأقسام المشتركة (ذكور و اناث)', 'sum'),
        filles        = ('مج التلميذات', 'sum'),
        filles_mix    = ('الاناث بالأقسام المشتركة', 'sum'),
        total_classes = ('مج الأقسام', 'sum'),
        classes_mix   = ('الأقسام المشتركة منهم', 'sum'),
        X = ('X', 'first'),
        Y = ('Y', 'first'),
    ).reset_index()

    etab['is_centrale']     = etab['cd_rat'].isna()
    etab['classes_uniques'] = etab['total_classes'] - etab['classes_mix']
    etab['garcons']         = etab['total_eleves'] - etab['filles']
    return df, etab


# ══════════════════════════════════════════════════════════════════════════════
# ─── SIDEBAR (RIGHT) ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"## 🏫 لوحة القيادة")
    st.markdown("**جهة سوس - ماسة**")
    st.markdown(f"👤 مرحباً، **{st.session_state.username}**")
    st.markdown("---")

    # ── رفع الملف ──
    st.markdown("### 📂 تحميل البيانات")
    uploaded_file = st.file_uploader(
        "ارفع ملف Excel المحدّث",
        type=["xlsx"],
        help="اسحب وأفلت ملف .xlsx هنا"
    )

    local_path  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data__3_.xlsx")
    data_source = None

    if uploaded_file is not None:
        data_source = uploaded_file
        st.success("✅ تم تحميل الملف بنجاح")
    elif os.path.exists(local_path):
        data_source = local_path
        st.info("📁 ملف البيانات من المستودع")
    else:
        st.warning("⚠️ يرجى رفع ملف البيانات")

    st.markdown("---")

    if data_source is None:
        st.markdown("### 🔍 البحث والتصفية")
        st.info("يرجى رفع ملف البيانات أولاً")
        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            do_logout()
        st.stop()

    # ── تحميل البيانات ──
    df_raw, etab = load_data(data_source)
    PROVINCES = sorted(etab['prov'].dropna().unique().tolist())

    st.markdown("---")
    st.markdown("### 🔍 البحث والتصفية")

    selected_prov = st.selectbox("📍 المديرية", ["الكل"] + PROVINCES, key="prov")

    if selected_prov != "الكل":
        communes = sorted(etab[etab['prov'] == selected_prov]['commune'].dropna().unique().tolist())
    else:
        communes = sorted(etab['commune'].dropna().unique().tolist())
    selected_commune = st.selectbox("🏘️ الجماعة", ["الكل"] + communes, key="commune")

    st.markdown("**🏫 البحث عن مؤسسة**")
    search_text = st.text_input("اكتب الاسم أو الرمز", "", key="search")
    if search_text:
        mask = (
            etab['nom_ar'].str.contains(search_text, na=False) |
            etab['CD_ETAB'].str.contains(search_text, na=False, case=False)
        )
        if selected_prov    != "الكل": mask &= etab['prov']    == selected_prov
        if selected_commune != "الكل": mask &= etab['commune'] == selected_commune
        suggestions = etab[mask][['CD_ETAB', 'nom_ar']].head(15)
        if not suggestions.empty:
            for _, row in suggestions.iterrows():
                st.markdown(f"▸ `{row['CD_ETAB']}` — {row['nom_ar']}")

    st.markdown("---")
    st.caption(f"📊 {len(etab)} مؤسسة | 2025-2026")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        do_logout()


# ══════════════════════════════════════════════════════════════════════════════
# ─── MAIN CONTENT ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# ── Filters ──
filtered = etab.copy()
if selected_prov    != "الكل": filtered = filtered[filtered['prov']    == selected_prov]
if selected_commune != "الكل": filtered = filtered[filtered['commune'] == selected_commune]

# ── Header ──
scope = selected_prov if selected_prov != "الكل" else "جهة سوس - ماسة"
st.markdown(f"""
<div class="header-banner">
    <h1>🏫 لوحة القيادة — التعليم الابتدائي</h1>
    <p>{scope} | الموسم الدراسي 2025-2026</p>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──
total_etab      = len(filtered)
centrales       = int(filtered['is_centrale'].sum())
annexes         = int((~filtered['is_centrale']).sum())
total_eleves    = int(filtered['total_eleves'].sum())
total_filles    = int(filtered['filles'].sum())
total_classes   = int(filtered['total_classes'].sum())
classes_mix_tot = int(filtered['classes_mix'].sum())
classes_uni_tot = int(filtered['classes_uniques'].sum())

c1,c2,c3,c4,c5,c6 = st.columns(6)
for col, cls, val, lbl, icon in [
    (c1,"kpi-blue",   total_etab,           "عدد المؤسسات",    "🏫"),
    (c2,"kpi-green",  centrales,             "مدارس مركزية",    "🏛️"),
    (c3,"kpi-orange", annexes,               "فروع وملاحق",     "🔗"),
    (c4,"kpi-purple", f"{total_eleves:,}",   "إجمالي التلاميذ","👥"),
    (c5,"kpi-red",    f"{total_filles:,}",   "منهم الإناث",     "👧"),
    (c6,"kpi-teal",   total_classes,         "إجمالي الأقسام",  "📚"),
]:
    with col:
        st.markdown(f'<div class="kpi-card {cls}"><div class="value">{icon} {val}</div><div class="label">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Charts Row 1 ──
ca, cb = st.columns(2)
with ca:
    st.markdown('<div class="section-title">📊 توزيع المؤسسات حسب المديرية</div>', unsafe_allow_html=True)
    ps = etab.groupby('prov').agg(centrales=('is_centrale','sum'), total=('CD_ETAB','count')).reset_index()
    ps['annexes'] = ps['total'] - ps['centrales']
    fig = go.Figure()
    fig.add_trace(go.Bar(name='مركزية',       x=ps['prov'], y=ps['centrales'], marker_color='#1a3a5c', text=ps['centrales'], textposition='inside'))
    fig.add_trace(go.Bar(name='فروع وملاحق', x=ps['prov'], y=ps['annexes'],   marker_color='#2196F3', text=ps['annexes'],   textposition='inside'))
    fig.update_layout(barmode='stack', height=320, margin=dict(t=10,b=5,l=5,r=5),
                      legend=dict(orientation='h',y=-0.25), plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

with cb:
    st.markdown('<div class="section-title">👧 نسبة الإناث والذكور</div>', unsafe_allow_html=True)
    fig2 = go.Figure(go.Pie(
        labels=['ذكور','إناث'],
        values=[int(filtered['garcons'].sum()), total_filles],
        hole=0.55, marker_colors=['#1a3a5c','#e91e8c'],
        textinfo='label+percent', textfont_size=13,
    ))
    fig2.update_layout(height=320, margin=dict(t=10,b=5,l=5,r=5))
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──
cc, cd = st.columns(2)
with cc:
    st.markdown('<div class="section-title">📚 الأقسام: موحدة / مشتركة</div>', unsafe_allow_html=True)
    fig3 = go.Figure(go.Pie(
        labels=['أقسام موحدة','أقسام مشتركة'],
        values=[classes_uni_tot, classes_mix_tot],
        hole=0.5, marker_colors=['#4CAF50','#FF9800'],
        textinfo='label+value+percent', textfont_size=12,
    ))
    fig3.update_layout(height=300, margin=dict(t=10,b=5,l=5,r=5))
    st.plotly_chart(fig3, use_container_width=True)

with cd:
    st.markdown('<div class="section-title">🏘️ حضري / قروي</div>', unsafe_allow_html=True)
    ms = filtered.groupby('milieu').agg(nb=('CD_ETAB','count'), eleves=('total_eleves','sum')).reset_index()
    fig4 = make_subplots(rows=1,cols=2,specs=[[{'type':'domain'},{'type':'domain'}]],
                         subplot_titles=['عدد المؤسسات','عدد التلاميذ'])
    colors = ['#009688','#FF5722']
    fig4.add_trace(go.Pie(labels=ms['milieu'],values=ms['nb'],    hole=0.5,marker_colors=colors,showlegend=False,textinfo='label+percent'),1,1)
    fig4.add_trace(go.Pie(labels=ms['milieu'],values=ms['eleves'],hole=0.5,marker_colors=colors,showlegend=False,textinfo='label+percent'),1,2)
    fig4.update_layout(height=300, margin=dict(t=30,b=5,l=5,r=5))
    st.plotly_chart(fig4, use_container_width=True)

# ── توزيع حسب عدد التلاميذ ──
st.markdown('<div class="section-title">📈 توزيع المؤسسات حسب عدد التلاميذ</div>', unsafe_allow_html=True)
bins   = [0,5,10,30,60,100,300,700,float('inf')]
labels = ['< 5','5-10','10-30','30-60','60-100','100-300','300-700','700+']
fc = filtered.copy()
fc['tranche'] = pd.cut(fc['total_eleves'], bins=bins, labels=labels, right=True)
ts = fc.groupby('tranche', observed=True).agg(nb_etab=('CD_ETAB','count'), total_eleves=('total_eleves','sum')).reset_index()

ce, cf = st.columns([3,2])
with ce:
    fig5 = go.Figure(go.Bar(
        x=ts['tranche'].astype(str), y=ts['nb_etab'],
        marker_color=['#e3f2fd','#90caf9','#42a5f5','#1e88e5','#1565c0','#0d47a1','#01579b','#002171'],
        text=ts['nb_etab'], textposition='outside',
    ))
    fig5.update_layout(height=340, margin=dict(t=10,b=5,l=5,r=5),
                       xaxis_title='مجال عدد التلاميذ', yaxis_title='عدد المؤسسات',
                       plot_bgcolor='white', xaxis=dict(showgrid=False),
                       yaxis=dict(showgrid=True,gridcolor='#eee'))
    st.plotly_chart(fig5, use_container_width=True)

with cf:
    st.markdown("**جدول التوزيع**")
    td = ts.copy()
    td.columns = ['المجال','عدد المؤسسات','مجموع التلاميذ']
    td['%'] = (td['عدد المؤسسات'] / td['عدد المؤسسات'].sum() * 100).round(1).astype(str) + '%'
    st.dataframe(td, use_container_width=True, hide_index=True)

# ── خريطة ──
st.markdown('<div class="section-title">🗺️ خريطة توزيع المؤسسات</div>', unsafe_allow_html=True)
map_data = filtered.dropna(subset=['X','Y']).copy()
map_data['type_label'] = map_data['is_centrale'].map({True:'مركزية',False:'فرع/ملحقة'})
map_data['size'] = map_data['total_eleves'].clip(lower=10)
fig_map = px.scatter_mapbox(
    map_data, lat='Y', lon='X',
    color='type_label', size='size', size_max=20,
    hover_name='nom_ar',
    hover_data={'CD_ETAB':True,'commune':True,'total_eleves':True,'type_label':True,'X':False,'Y':False,'size':False},
    color_discrete_map={'مركزية':'#1a3a5c','فرع/ملحقة':'#2196F3'},
    mapbox_style='carto-positron', zoom=7, height=500,
    labels={'type_label':'النوع','total_eleves':'التلاميذ','commune':'الجماعة','CD_ETAB':'الرمز'}
)
fig_map.update_layout(margin=dict(t=0,b=0,l=0,r=0), legend=dict(orientation='h',y=0.01))
st.plotly_chart(fig_map, use_container_width=True)

# ── شجرة المدارس ──
st.markdown('<div class="section-title">🌳 الربط بين المدارس المركزية وفروعها</div>', unsafe_allow_html=True)
centrales_df = filtered[filtered['is_centrale']].sort_values('nom_ar')
if selected_prov == "الكل":
    st.info("اختر مديرية من الشريط الجانبي لعرض شجرة الروابط")
elif centrales_df.empty:
    st.warning("لا توجد مدارس مركزية في هذه التصفية")
else:
    cols_tree = st.columns(2)
    for i, (_, central) in enumerate(centrales_df.iterrows()):
        branches = filtered[filtered['cd_rat'] == central['CD_ETAB']]
        branch_html = "".join(
            f'<div class="branch-node">🔗 {br["nom_ar"]} <span style="color:#999;font-size:.75rem">({br["CD_ETAB"]})</span></div>'
            for _, br in branches.iterrows()
        )
        with cols_tree[i % 2]:
            st.markdown(f"""
            <div class="tree-container">
                <div class="central-node">🏛️ {central['nom_ar']} ({central['CD_ETAB']})</div>
                <div><small style="color:#555">👥 {int(central['total_eleves'])} تلميذ | 📚 {int(central['total_classes'])} قسم</small></div>
                {branch_html or '<div style="color:#999;font-size:.8rem;margin-top:4px">لا توجد فروع مرتبطة</div>'}
            </div>""", unsafe_allow_html=True)

# ── جدول المؤسسات ──
st.markdown('<div class="section-title">📋 قائمة المؤسسات</div>', unsafe_allow_html=True)
show_df = filtered[['CD_ETAB','nom_ar','type_etab','prov','commune','milieu',
                     'is_centrale','total_eleves','filles','total_classes','classes_mix']].copy()
show_df['النوع'] = show_df['is_centrale'].map({True:'🏛️ مركزية',False:'🔗 فرع/ملحقة'})
show_df = show_df.drop(columns=['is_centrale'])
show_df.columns = ['الرمز','الاسم','صنف المؤسسة','المديرية','الجماعة','الوسط',
                   'التلاميذ','الإناث','الأقسام','أقسام مشتركة','النوع']
st.dataframe(show_df.sort_values('التلاميذ',ascending=False),
             use_container_width=True, hide_index=True, height=400)

st.caption("📂 المصدر: قاعدة بيانات المدارس الابتدائية — جهة سوس ماسة | 2025-2026")
