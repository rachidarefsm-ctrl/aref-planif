import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="لوحة القيادة - جهة سوس ماسة",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── RTL & Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    * { font-family: 'Cairo', sans-serif !important; }
    
    .main { direction: rtl; }
    .stApp { background: #f0f4f8; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3a5c 0%, #0d2137 100%);
        direction: rtl;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label { color: #a8d8f0 !important; font-weight: 600; }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid;
        margin-bottom: 10px;
    }
    .kpi-card .value { font-size: 2rem; font-weight: 700; }
    .kpi-card .label { font-size: 0.85rem; color: #666; margin-top: 4px; }
    .kpi-blue { border-color: #2196F3; color: #2196F3; }
    .kpi-green { border-color: #4CAF50; color: #4CAF50; }
    .kpi-orange { border-color: #FF9800; color: #FF9800; }
    .kpi-purple { border-color: #9C27B0; color: #9C27B0; }
    .kpi-red { border-color: #F44336; color: #F44336; }
    .kpi-teal { border-color: #009688; color: #009688; }
    
    /* Section headers */
    .section-title {
        background: linear-gradient(90deg, #1a3a5c, #2196F3);
        color: white !important;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 15px 0 10px 0;
        direction: rtl;
    }
    
    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #1a3a5c 0%, #2c6fad 50%, #1a3a5c 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 20px;
        text-align: center;
        direction: rtl;
    }
    .header-banner h1 { font-size: 1.8rem; margin: 0; }
    .header-banner p { font-size: 0.9rem; opacity: 0.85; margin: 5px 0 0 0; }
    
    /* Tree structure */
    .tree-container {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        direction: rtl;
    }
    .central-node {
        background: #1a3a5c;
        color: white;
        padding: 8px 15px;
        border-radius: 8px;
        font-weight: 700;
        margin-bottom: 8px;
        display: inline-block;
    }
    .branch-node {
        background: #e3f2fd;
        color: #1a3a5c;
        padding: 5px 12px;
        border-radius: 6px;
        margin: 3px 0 3px 25px;
        border-right: 3px solid #2196F3;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("data__3_.xlsx", header=1)
    
    # Numeric conversion
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
    
    # Aggregate per school (CD_ETAB)
    etab = df.groupby('CD_ETAB').agg(
        nom_ar=('NOM_ETABA', 'first'),
        type_etab=('LA_NETAB', 'first'),
        prov=('LA_PROV', 'first'),
        commune=('COMMUNE', 'first'),
        milieu=('LA_MIL', 'first'),
        cd_rat=('Cd_RAT', 'first'),
        gresa_modi=('Gresa_modi', 'first'),
        total_eleves=('مج التلاميذ (ذكور و اناث)', 'sum'),
        eleves_mix=('التلاميذ بالأقسام المشتركة (ذكور و اناث)', 'sum'),
        filles=('مج التلميذات', 'sum'),
        filles_mix=('الاناث بالأقسام المشتركة', 'sum'),
        total_classes=('مج الأقسام', 'sum'),
        classes_mix=('الأقسام المشتركة منهم', 'sum'),
        X=('X', 'first'),
        Y=('Y', 'first'),
    ).reset_index()
    
    # Flag: centrale vs annexe
    etab['is_centrale'] = etab['cd_rat'].isna()
    etab['classes_uniques'] = etab['total_classes'] - etab['classes_mix']
    etab['garcons'] = etab['total_eleves'] - etab['filles']
    
    return df, etab

df_raw, etab = load_data()

PROVINCES = sorted(etab['prov'].dropna().unique().tolist())


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 البحث والتصفية")
    st.markdown("---")
    
    # Province filter
    selected_prov = st.selectbox("📍 المديرية", ["الكل"] + PROVINCES, key="prov")
    
    # Commune filter
    if selected_prov != "الكل":
        communes = sorted(etab[etab['prov'] == selected_prov]['commune'].dropna().unique().tolist())
    else:
        communes = sorted(etab['commune'].dropna().unique().tolist())
    selected_commune = st.selectbox("🏘️ الجماعة", ["الكل"] + communes, key="commune")
    
    # School search with autocomplete list
    st.markdown("**🏫 البحث عن مؤسسة**")
    search_text = st.text_input("اكتب اسم المؤسسة أو رمزها", "", key="search")
    
    if search_text:
        mask = (
            etab['nom_ar'].str.contains(search_text, na=False) |
            etab['CD_ETAB'].str.contains(search_text, na=False, case=False)
        )
        if selected_prov != "الكل":
            mask &= etab['prov'] == selected_prov
        if selected_commune != "الكل":
            mask &= etab['commune'] == selected_commune
        suggestions = etab[mask][['CD_ETAB', 'nom_ar']].head(20)
        if not suggestions.empty:
            st.markdown("**نتائج البحث:**")
            for _, row in suggestions.iterrows():
                st.markdown(f"▸ `{row['CD_ETAB']}` — {row['nom_ar']}")
    
    st.markdown("---")
    st.markdown("**جهة سوس - ماسة**")
    st.markdown(f"📊 {len(etab)} مؤسسة إجمالاً")
    st.caption("الموسم الدراسي 2024-2025")


# ─── Apply Filters ────────────────────────────────────────────────────────────
filtered = etab.copy()
if selected_prov != "الكل":
    filtered = filtered[filtered['prov'] == selected_prov]
if selected_commune != "الكل":
    filtered = filtered[filtered['commune'] == selected_commune]


# ─── Header ───────────────────────────────────────────────────────────────────
scope = selected_prov if selected_prov != "الكل" else "جهة سوس - ماسة"
st.markdown(f"""
<div class="header-banner">
    <h1>🏫 لوحة القيادة - التعليم الابتدائي</h1>
    <p>{scope} | الموسم الدراسي 2025-2026</p>
</div>
""", unsafe_allow_html=True)


# ─── KPI Row ──────────────────────────────────────────────────────────────────
total_etab       = len(filtered)
centrales        = filtered['is_centrale'].sum()
annexes          = (~filtered['is_centrale']).sum()
total_eleves     = int(filtered['total_eleves'].sum())
total_filles     = int(filtered['filles'].sum())
total_classes    = int(filtered['total_classes'].sum())
classes_mix_tot  = int(filtered['classes_mix'].sum())
classes_uni_tot  = int(filtered['classes_uniques'].sum())

c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (c1, "kpi-blue",   total_etab,      "عدد المؤسسات",         "🏫"),
    (c2, "kpi-green",  centrales,        "مدارس مركزية",          "🏛️"),
    (c3, "kpi-orange", annexes,          "فروع وملاحق",           "🔗"),
    (c4, "kpi-purple", f"{total_eleves:,}", "إجمالي التلاميذ",   "👥"),
    (c5, "kpi-red",    f"{total_filles:,}", "منهم الإناث",       "👧"),
    (c6, "kpi-teal",   total_classes,   "إجمالي الأقسام",        "📚"),
]
for col, cls, val, lbl, icon in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card {cls}">
            <div class="value">{icon} {val}</div>
            <div class="label">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Row 2: Charts ────────────────────────────────────────────────────────────
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown('<div class="section-title">📊 توزيع المؤسسات حسب المديرية</div>', unsafe_allow_html=True)
    prov_stats = etab.groupby('prov').agg(
        total=('CD_ETAB', 'count'),
        centrales=('is_centrale', 'sum'),
    ).reset_index()
    prov_stats['annexes'] = prov_stats['total'] - prov_stats['centrales']
    fig = go.Figure()
    fig.add_trace(go.Bar(name='مركزية', x=prov_stats['prov'], y=prov_stats['centrales'],
                         marker_color='#1a3a5c', text=prov_stats['centrales'], textposition='inside'))
    fig.add_trace(go.Bar(name='فروع وملاحق', x=prov_stats['prov'], y=prov_stats['annexes'],
                         marker_color='#2196F3', text=prov_stats['annexes'], textposition='inside'))
    fig.update_layout(barmode='stack', height=320, margin=dict(t=10,b=5,l=5,r=5),
                      legend=dict(orientation='h', y=-0.15), plot_bgcolor='white',
                      xaxis=dict(tickfont=dict(size=10)))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">👧 نسبة الإناث والذكور</div>', unsafe_allow_html=True)
    total_g = int(filtered['garcons'].sum())
    total_f = int(filtered['filles'].sum())
    fig2 = go.Figure(go.Pie(
        labels=['ذكور', 'إناث'],
        values=[total_g, total_f],
        hole=0.55,
        marker_colors=['#1a3a5c', '#e91e8c'],
        textinfo='label+percent',
        textfont_size=13,
    ))
    fig2.update_layout(height=320, margin=dict(t=10,b=5,l=5,r=5),
                       showlegend=True, legend=dict(orientation='h', y=-0.1))
    st.plotly_chart(fig2, use_container_width=True)


# ─── Row 3: Classes & Distribution ───────────────────────────────────────────
col_c, col_d = st.columns([1, 1])

with col_c:
    st.markdown('<div class="section-title">📚 الأقسام: موحدة / مشتركة</div>', unsafe_allow_html=True)
    fig3 = go.Figure(go.Pie(
        labels=['أقسام موحدة', 'أقسام مشتركة'],
        values=[classes_uni_tot, classes_mix_tot],
        hole=0.5,
        marker_colors=['#4CAF50', '#FF9800'],
        textinfo='label+value+percent',
        textfont_size=12,
    ))
    fig3.update_layout(height=300, margin=dict(t=10,b=5,l=5,r=5))
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown('<div class="section-title">🏘️ حضري / قروي</div>', unsafe_allow_html=True)
    mil_stats = filtered.groupby('milieu').agg(
        nb=('CD_ETAB', 'count'),
        eleves=('total_eleves', 'sum')
    ).reset_index()
    fig4 = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                         subplot_titles=['عدد المؤسسات', 'عدد التلاميذ'])
    colors = ['#009688', '#FF5722']
    fig4.add_trace(go.Pie(labels=mil_stats['milieu'], values=mil_stats['nb'],
                          hole=0.5, marker_colors=colors, showlegend=False,
                          textinfo='label+percent'), 1, 1)
    fig4.add_trace(go.Pie(labels=mil_stats['milieu'], values=mil_stats['eleves'],
                          hole=0.5, marker_colors=colors, showlegend=False,
                          textinfo='label+percent'), 1, 2)
    fig4.update_layout(height=300, margin=dict(t=30,b=5,l=5,r=5))
    st.plotly_chart(fig4, use_container_width=True)


# ─── توزيع الوحدات المدرسية حسب عدد التلاميذ ────────────────────────────────
st.markdown('<div class="section-title">📈 توزيع المؤسسات حسب عدد التلاميذ (cd_etab)</div>',
            unsafe_allow_html=True)

bins   = [0, 5, 10, 30, 60, 100, 300, 700, float('inf')]
labels = ['< 5', '5-10', '10-30', '30-60', '60-100', '100-300', '300-700', '700+']
filtered_copy = filtered.copy()
filtered_copy['tranche'] = pd.cut(filtered_copy['total_eleves'], bins=bins, labels=labels, right=True)
tranche_stats = filtered_copy.groupby('tranche', observed=True).agg(
    nb_etab=('CD_ETAB', 'count'),
    total_eleves=('total_eleves', 'sum')
).reset_index()

col_e, col_f = st.columns([3, 2])
with col_e:
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=tranche_stats['tranche'].astype(str),
        y=tranche_stats['nb_etab'],
        marker_color=['#e3f2fd','#90caf9','#42a5f5','#1e88e5','#1565c0','#0d47a1','#01579b','#002171'],
        text=tranche_stats['nb_etab'],
        textposition='outside',
        name='عدد المؤسسات'
    ))
    fig5.update_layout(
        height=340, margin=dict(t=10,b=5,l=5,r=5),
        xaxis_title='مجال عدد التلاميذ',
        yaxis_title='عدد المؤسسات',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#eee'),
    )
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.markdown("**جدول التوزيع**")
    display_tranche = tranche_stats.copy()
    display_tranche.columns = ['المجال', 'عدد المؤسسات', 'مجموع التلاميذ']
    display_tranche['%'] = (display_tranche['عدد المؤسسات'] / display_tranche['عدد المؤسسات'].sum() * 100).round(1).astype(str) + '%'
    st.dataframe(display_tranche, use_container_width=True, hide_index=True)


# ─── Carte interactive ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗺️ خريطة توزيع المؤسسات</div>', unsafe_allow_html=True)

map_data = filtered.dropna(subset=['X', 'Y']).copy()
map_data['type_label'] = map_data['is_centrale'].map({True: 'مركزية', False: 'فرع/ملحقة'})
map_data['size'] = map_data['total_eleves'].clip(lower=10)

fig_map = px.scatter_mapbox(
    map_data,
    lat='Y', lon='X',
    color='type_label',
    size='size',
    size_max=20,
    hover_name='nom_ar',
    hover_data={'CD_ETAB': True, 'commune': True, 'total_eleves': True, 'type_label': True, 'X': False, 'Y': False, 'size': False},
    color_discrete_map={'مركزية': '#1a3a5c', 'فرع/ملحقة': '#2196F3'},
    mapbox_style='carto-positron',
    zoom=7,
    height=500,
    labels={'type_label': 'النوع', 'total_eleves': 'التلاميذ', 'commune': 'الجماعة', 'CD_ETAB': 'الرمز'}
)
fig_map.update_layout(margin=dict(t=0,b=0,l=0,r=0), legend=dict(orientation='h', y=0.01))
st.plotly_chart(fig_map, use_container_width=True)


# ─── Arbre المدارس المركزية وفروعها ─────────────────────────────────────────
st.markdown('<div class="section-title">🌳 الربط بين المدارس المركزية وفروعها</div>',
            unsafe_allow_html=True)

tree_filter = filtered.copy()
centrales_df = tree_filter[tree_filter['is_centrale']].sort_values('nom_ar')

if selected_prov == "الكل":
    st.info("اختر مديرية من الشريط الجانبي لعرض الروابط بين المدارس المركزية وفروعها")
else:
    if centrales_df.empty:
        st.warning("لا توجد مدارس مركزية في هذا التصفية")
    else:
        # Build network-style list
        cols_tree = st.columns(2)
        col_idx = 0
        for _, central in centrales_df.iterrows():
            branches = tree_filter[tree_filter['cd_rat'] == central['CD_ETAB']]
            with cols_tree[col_idx % 2]:
                branch_html = ""
                for _, br in branches.iterrows():
                    branch_html += f'<div class="branch-node">🔗 {br["nom_ar"]} <span style="color:#999;font-size:0.75rem">({br["CD_ETAB"]})</span></div>'
                st.markdown(f"""
                <div class="tree-container" style="margin-bottom:12px">
                    <div class="central-node">🏛️ {central['nom_ar']} ({central['CD_ETAB']})</div>
                    <div><small style="color:#666">👥 {int(central['total_eleves'])} تلميذ | 📚 {int(central['total_classes'])} قسم</small></div>
                    {branch_html if branch_html else '<div style="color:#999;font-size:0.8rem;margin-top:4px">لا توجد فروع مرتبطة</div>'}
                </div>""", unsafe_allow_html=True)
            col_idx += 1


# ─── Detailed Table ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 قائمة المؤسسات</div>', unsafe_allow_html=True)

show_df = filtered[[
    'CD_ETAB', 'nom_ar', 'type_etab', 'prov', 'commune', 'milieu',
    'is_centrale', 'total_eleves', 'filles', 'total_classes', 'classes_mix'
]].copy()
show_df['النوع'] = show_df['is_centrale'].map({True: '🏛️ مركزية', False: '🔗 فرع/ملحقة'})
show_df = show_df.drop(columns=['is_centrale'])
show_df.columns = ['الرمز', 'الاسم', 'صنف المؤسسة', 'المديرية', 'الجماعة', 'الوسط',
                   'التلاميذ', 'الإناث', 'الأقسام', 'أقسام مشتركة', 'النوع']

st.dataframe(
    show_df.sort_values('التلاميذ', ascending=False),
    use_container_width=True,
    hide_index=True,
    height=400,
)

st.caption("📂 المصدر: قاعدة بيانات المدارس الابتدائية - جهة سوس ماسة | 2025-2026")
