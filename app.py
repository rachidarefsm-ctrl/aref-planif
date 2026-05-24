import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

st.set_page_config(
    page_title="السلك الابتدائي - سوس ماسة",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; direction: rtl; }
.metric-card {
    background: white; border-radius: 12px; padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07); text-align: center;
    border-top: 4px solid;
}
.stMetric { direction: rtl; }
div[data-testid="stMetricValue"] { font-family: 'Cairo', sans-serif; font-size: 2rem; font-weight: 900; }
div[data-testid="stMetricLabel"] { font-family: 'Cairo', sans-serif; font-size: 0.9rem; }
.header-box {
    background: linear-gradient(135deg, #0d2137 0%, #1e3f6e 100%);
    border-radius: 16px; padding: 24px 32px; color: white; margin-bottom: 24px;
}
.header-box h1 { font-size: 1.6rem; font-weight: 900; margin: 0; }
.header-box p { font-size: 0.85rem; opacity: 0.65; margin: 4px 0 0 0; }
.section-title {
    font-size: 1rem; font-weight: 700; color: #1a2535;
    border-right: 4px solid #1e88e5; padding-right: 10px; margin: 20px 0 12px 0;
}
.etab-card {
    background: #f8fafc; border-radius: 10px; padding: 14px 16px;
    border-right: 4px solid #1e88e5; margin-bottom: 8px;
}
.branch-card {
    background: #fff; border-radius: 8px; padding: 10px 14px;
    border-right: 3px solid #90caf9; margin-bottom: 6px; font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)


# ── LOAD DATA ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("/mnt/user-data/uploads/data__3_.xlsx", header=1)
    df.columns = [
        'LA_PROV','COMMUNE','LA_MIL','CD_ETAB','Cd_RAT','Gresa_modi',
        'NOM_ETABA','LA_NETAB','code_zone','X','Y','libformatAr',
        'eleves_mouwahad','eleves_mousharak',
        'filles_mouwahad','filles_mousharak',
        'classes_mouwahad','classes_mousharak'
    ]
    df = df[df['LA_PROV'] != 'Total general']
    df = df[df['LA_PROV'].notna()]
    df = df[~df['LA_PROV'].str.contains('Total', na=False)]
    df = df[df['CD_ETAB'].notna()]

    inst = df.groupby(
        ['LA_PROV','COMMUNE','CD_ETAB','Cd_RAT','Gresa_modi','NOM_ETABA','LA_NETAB','LA_MIL'],
        dropna=False
    ).agg(
        eleves_mouwahad=('eleves_mouwahad','sum'),
        eleves_mousharak=('eleves_mousharak','sum'),
        filles_mouwahad=('filles_mouwahad','sum'),
        filles_mousharak=('filles_mousharak','sum'),
        classes_mouwahad=('classes_mouwahad','sum'),
        classes_mousharak=('classes_mousharak','sum'),
    ).reset_index()

    inst['total_eleves'] = (inst['eleves_mouwahad'] + inst['eleves_mousharak']).astype(int)
    inst['total_filles'] = (inst['filles_mouwahad'] + inst['filles_mousharak']).astype(int)
    inst['classes_mouwahad'] = inst['classes_mouwahad'].round(1)
    inst['classes_mousharak'] = inst['classes_mousharak'].round(1)
    inst['total_classes'] = (inst['classes_mouwahad'] + inst['classes_mousharak']).round(1)

    # Gresa_modi NaN -> empty string
    inst['Gresa_modi'] = inst['Gresa_modi'].fillna('')
    inst['Cd_RAT'] = inst['Cd_RAT'].fillna('')

    return inst

inst = load_data()

# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## لوحة تحكم السلك الابتدائي")
    st.markdown("**جهة سوس - ماسة**")
    st.markdown("---")

    provinces = ['الكل'] + sorted(inst['LA_PROV'].unique().tolist())
    sel_prov = st.selectbox("المديرية الاقليمية", provinces)

    if sel_prov != 'الكل':
        communes_list = ['الكل'] + sorted(inst[inst['LA_PROV'] == sel_prov]['COMMUNE'].unique().tolist())
    else:
        communes_list = ['الكل'] + sorted(inst['COMMUNE'].unique().tolist())
    sel_commune = st.selectbox("الجماعة", communes_list)

    st.markdown("---")
    search_q = st.text_input("البحث عن مؤسسة", placeholder="اسم او رمز المؤسسة...")

    st.markdown("---")
    st.caption("المصدر: قاعدة البيانات الرسمية للسلك الابتدائي - الاكاديمية الجهوية - الموسم 2024/2025")

# ── FILTER DATA ────────────────────────────────────────────────────
filtered = inst.copy()
if sel_prov != 'الكل':
    filtered = filtered[filtered['LA_PROV'] == sel_prov]
if sel_commune != 'الكل':
    filtered = filtered[filtered['COMMUNE'] == sel_commune]

# ── HEADER ─────────────────────────────────────────────────────────
title = f"احصاءات: {sel_prov}" if sel_prov != 'الكل' else "احصاءات جهة سوس - ماسة"
subtitle = f"جماعة: {sel_commune}" if sel_commune != 'الكل' else (
    sel_prov if sel_prov != 'الكل' else "جميع المديريات الاقليمية"
) + " - السلك الابتدائي"

st.markdown(f"""
<div class="header-box">
  <h1>🏫 {title}</h1>
  <p>{subtitle}</p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ──────────────────────────────────────────────────────
total_eleves = int(filtered['total_eleves'].sum())
total_filles = int(filtered['total_filles'].sum())
total_garcons = total_eleves - total_filles
total_cls_m = int(filtered['classes_mouwahad'].sum())
total_cls_s = round(float(filtered['classes_mousharak'].sum()), 1)
total_cls = round(float(filtered['total_classes'].sum()), 1)
nb_etab = len(filtered)
pct_filles = round(total_filles / total_eleves * 100, 1) if total_eleves > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("عدد المؤسسات", f"{nb_etab:,}")
with c2:
    st.metric("اجمالي التلاميذ", f"{total_eleves:,}")
with c3:
    st.metric("الاناث", f"{total_filles:,}", f"{pct_filles}%")
with c4:
    st.metric("اقسام موحدة", f"{total_cls_m:,}")
with c5:
    st.metric("اقسام مشتركة", f"{total_cls_s:,}")

st.markdown("---")

# ── SEARCH RESULT ──────────────────────────────────────────────────
if search_q and len(search_q) >= 2:
    q = search_q.lower()
    results = filtered[
        filtered['NOM_ETABA'].str.lower().str.contains(q, na=False) |
        filtered['CD_ETAB'].str.lower().str.contains(q, na=False)
    ]
    if len(results) > 0:
        st.markdown('<div class="section-title">نتائج البحث</div>', unsafe_allow_html=True)
        for _, r in results.iterrows():
            # Find siblings (same Gresa_modi)
            gresa = r['Gresa_modi']
            siblings = inst[
                (inst['Gresa_modi'] == gresa) & (inst['CD_ETAB'] != r['CD_ETAB'])
            ] if gresa else pd.DataFrame()

            with st.expander(f"🏫 {r['NOM_ETABA']}  |  {r['CD_ETAB']}  |  {r['LA_PROV']}", expanded=True):
                i1, i2, i3, i4 = st.columns(4)
                i1.metric("التلاميذ", int(r['total_eleves']))
                i2.metric("الاناث", int(r['total_filles']))
                i3.metric("اقسام موحدة", r['classes_mouwahad'])
                i4.metric("اقسام مشتركة", r['classes_mousharak'])
                st.caption(f"الجماعة: {r['COMMUNE']}  |  الوسط: {r['LA_MIL']}  |  رمز المرجع: {gresa or 'غير محدد'}")

                if len(siblings) > 0:
                    st.markdown(f"**الوحدات المرتبطة ({len(siblings)}):**")
                    for _, s in siblings.iterrows():
                        st.markdown(f"""
                        <div class="branch-card">
                          <b>{s['NOM_ETABA']}</b>
                          <span style="color:#607d8b;font-size:0.8rem;"> | {s['CD_ETAB']} | {s['total_eleves']} تلميذ | {s['total_filles']} اناث | {s['total_classes']} قسم</span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.caption("لا توجد وحدات مرتبطة في قاعدة البيانات")
        st.markdown("---")

# ── TABS ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "نظرة عامة",
    "شبكة المؤسسات",
    "توزيع الوحدات المدرسية",
    "جدول المؤسسات"
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 - OVERVIEW
# ════════════════════════════════════════════════════════════════════
with tab1:
    prov_stats = filtered.groupby('LA_PROV').agg(
        nb_etab=('CD_ETAB','count'),
        total_eleves=('total_eleves','sum'),
        total_filles=('total_filles','sum'),
        cls_m=('classes_mouwahad','sum'),
        cls_s=('classes_mousharak','sum'),
    ).reset_index()
    prov_stats['pct_filles'] = (prov_stats['total_filles'] / prov_stats['total_eleves'] * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">عدد المؤسسات حسب المديرية</div>', unsafe_allow_html=True)
        fig1 = px.bar(
            prov_stats.sort_values('nb_etab', ascending=True),
            x='nb_etab', y='LA_PROV', orientation='h',
            labels={'nb_etab': 'عدد المؤسسات', 'LA_PROV': ''},
            color='nb_etab',
            color_continuous_scale='Blues',
            text='nb_etab'
        )
        fig1.update_traces(textposition='outside')
        fig1.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=0,r=20,t=10,b=10),
            height=300,
            font=dict(family='Cairo')
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">التلاميذ حسب المديرية</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='الاجمالي', y=prov_stats['LA_PROV'],
            x=prov_stats['total_eleves'], orientation='h',
            marker_color='#90caf9'
        ))
        fig2.add_trace(go.Bar(
            name='الاناث', y=prov_stats['LA_PROV'],
            x=prov_stats['total_filles'], orientation='h',
            marker_color='#ce93d8'
        ))
        fig2.update_layout(
            barmode='group', margin=dict(l=0,r=20,t=10,b=10),
            height=300, font=dict(family='Cairo'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">الاقسام الموحدة مقابل المشتركة</div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Pie(
            labels=['اقسام موحدة', 'اقسام مشتركة'],
            values=[total_cls_m, total_cls_s],
            hole=0.55,
            marker_colors=['#1e88e5','#fb8c00'],
            textfont=dict(family='Cairo')
        ))
        fig3.update_layout(
            margin=dict(l=20,r=20,t=10,b=10), height=260,
            font=dict(family='Cairo'),
            annotations=[dict(text=f'{total_cls}', x=0.5, y=0.5, font_size=22, showarrow=False)]
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">نسبة الاناث حسب المديرية (%)</div>', unsafe_allow_html=True)
        fig4 = px.bar(
            prov_stats.sort_values('pct_filles', ascending=True),
            x='pct_filles', y='LA_PROV', orientation='h',
            labels={'pct_filles': 'نسبة الاناث %', 'LA_PROV': ''},
            color='pct_filles',
            color_continuous_scale='Purples',
            text=prov_stats.sort_values('pct_filles', ascending=True)['pct_filles'].apply(lambda v: f"{v}%")
        )
        fig4.update_traces(textposition='outside')
        fig4.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=0,r=20,t=10,b=10),
            height=260, font=dict(family='Cairo'),
            xaxis=dict(range=[0, 60])
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Milieu breakdown
    st.markdown('<div class="section-title">التوزيع حسب الوسط (حضري / قروي)</div>', unsafe_allow_html=True)
    mil_stats = filtered.groupby('LA_MIL').agg(
        nb=('CD_ETAB','count'),
        eleves=('total_eleves','sum'),
        filles=('total_filles','sum'),
    ).reset_index()
    m1, m2, m3, m4 = st.columns(4)
    for _, row in mil_stats.iterrows():
        lbl = str(row['LA_MIL'])
        with m1 if lbl == 'حضري' else m2:
            st.metric(f"المؤسسات ({lbl})", f"{int(row['nb']):,}")
        with m3 if lbl == 'حضري' else m4:
            st.metric(f"التلاميذ ({lbl})", f"{int(row['eleves']):,}")

# ════════════════════════════════════════════════════════════════════
# TAB 2 - NETWORK
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">مجموعات المدارس والوحدات المرتبطة بها (Gresa_modi)</div>', unsafe_allow_html=True)
    st.caption("كل مجموعة تضم الوحدات المدرسية المرتبطة بنفس رمز المرجع. انقر على المجموعة لعرض التفاصيل.")

    groups = filtered.groupby('Gresa_modi')
    group_list = []
    for key, gdf in groups:
        total_e = int(gdf['total_eleves'].sum())
        total_f = int(gdf['total_filles'].sum())
        total_c = round(float(gdf['total_classes'].sum()), 1)
        main_row = gdf[gdf['CD_ETAB'] == key]
        main_name = main_row['NOM_ETABA'].values[0] if len(main_row) > 0 else (gdf['NOM_ETABA'].values[0] if len(gdf) > 0 else key)
        group_list.append({
            'key': key, 'name': main_name, 'nb': len(gdf),
            'eleves': total_e, 'filles': total_f, 'classes': total_c,
            'members': gdf
        })
    group_list.sort(key=lambda x: -x['eleves'])

    # Pagination
    PAGE = 20
    total_groups = len(group_list)
    page = st.number_input(f"الصفحة (الاجمالي: {total_groups} مجموعة)", min_value=1,
                           max_value=math.ceil(total_groups/PAGE), value=1, step=1)
    start = (page-1)*PAGE
    page_groups = group_list[start:start+PAGE]

    for g in page_groups:
        with st.expander(
            f"🏫 {g['name']}  |  رمز المرجع: {g['key']}  |  {g['nb']} وحدة  |  {g['eleves']:,} تلميذ  |  {g['filles']:,} اناث"
        ):
            for _, row in g['members'].iterrows():
                is_main = row['CD_ETAB'] == g['key']
                border_color = '#1e88e5' if is_main else '#90caf9'
                icon = "🔵" if is_main else "↳"
                st.markdown(f"""
                <div style="background:#f8fafc;border-radius:8px;padding:10px 14px;
                     border-right:4px solid {border_color};margin-bottom:6px;font-size:0.85rem;">
                  {icon} <b>{row['NOM_ETABA']}</b>
                  <span style="color:#607d8b;">
                   &nbsp;|&nbsp; {row['CD_ETAB']}
                   &nbsp;|&nbsp; {int(row['total_eleves'])} تلميذ
                   &nbsp;|&nbsp; {int(row['total_filles'])} اناث
                   &nbsp;|&nbsp; {row['classes_mouwahad']} موحدة
                   &nbsp;|&nbsp; {row['classes_mousharak']} مشتركة
                   &nbsp;|&nbsp; {row['LA_MIL']}
                   &nbsp;|&nbsp; {row['COMMUNE']}
                  </span>
                </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 - DISTRIBUTION
# ════════════════════════════════════════════════════════════════════
with tab3:
    RANGES = [
        {'label': 'اقل من 5',  'min': 0,   'max': 5},
        {'label': '5 - 10',    'min': 5,   'max': 10},
        {'label': '10 - 30',   'min': 10,  'max': 30},
        {'label': '30 - 60',   'min': 30,  'max': 60},
        {'label': '60 - 100',  'min': 60,  'max': 100},
        {'label': '100 - 300', 'min': 100, 'max': 300},
        {'label': '300 - 700', 'min': 300, 'max': 700},
        {'label': '700 فاكثر', 'min': 700, 'max': 99999},
    ]
    COLORS = ['#ef5350','#ff7043','#ffa726','#ffca28','#66bb6a','#26a69a','#42a5f5','#7e57c2']

    counts = []
    for r in RANGES:
        c = len(filtered[(filtered['total_eleves'] >= r['min']) & (filtered['total_eleves'] < r['max'])])
        counts.append(c)
    total_inst = sum(counts)

    st.markdown('<div class="section-title">توزيع الوحدات المدرسية حسب عدد التلاميذ</div>', unsafe_allow_html=True)
    st.caption("تصنيف المؤسسات وفق مجالات عدد التلاميذ (CD_ETAB)")

    # Summary table
    dist_df = pd.DataFrame({
        'المجال': [r['label'] for r in RANGES],
        'عدد المؤسسات': counts,
        'النسبة %': [round(c/total_inst*100, 1) if total_inst > 0 else 0 for c in counts],
    })
    st.dataframe(dist_df, use_container_width=True, hide_index=True)

    # Bar chart
    fig_dist = go.Figure(go.Bar(
        x=[r['label'] for r in RANGES],
        y=counts,
        marker_color=COLORS,
        text=counts,
        textposition='outside',
        customdata=[round(c/total_inst*100,1) if total_inst>0 else 0 for c in counts],
        hovertemplate='%{x}<br>عدد: %{y}<br>نسبة: %{customdata}%<extra></extra>'
    ))
    fig_dist.update_layout(
        margin=dict(l=20,r=20,t=30,b=20),
        height=350, font=dict(family='Cairo', size=13),
        yaxis_title='عدد المؤسسات',
        xaxis_title='مجال عدد التلاميذ',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='#ecf0f5')
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # Pie chart
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        fig_pie = go.Figure(go.Pie(
            labels=[r['label'] for r in RANGES],
            values=counts,
            marker_colors=COLORS,
            hole=0.4,
            textfont=dict(family='Cairo')
        ))
        fig_pie.update_layout(
            margin=dict(l=20,r=20,t=10,b=10),
            height=320, font=dict(family='Cairo'),
            legend=dict(orientation='v', font=dict(size=11))
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_p2:
        st.markdown('<div class="section-title">ملاحظات التحليل</div>', unsafe_allow_html=True)
        max_idx = counts.index(max(counts))
        small = counts[0] + counts[1]  # <10
        medium = counts[2] + counts[3] + counts[4]  # 10-100
        large = counts[5] + counts[6] + counts[7]  # 100+
        st.markdown(f"""
        - **اكبر فئة:** {RANGES[max_idx]['label']} بـ **{counts[max_idx]}** مؤسسة ({round(counts[max_idx]/total_inst*100,1) if total_inst>0 else 0}%)
        - **مؤسسات صغيرة** (اقل من 10 تلاميذ): **{small}** مؤسسة ({round(small/total_inst*100,1) if total_inst>0 else 0}%)
        - **مؤسسات متوسطة** (10 الى 100): **{medium}** مؤسسة ({round(medium/total_inst*100,1) if total_inst>0 else 0}%)
        - **مؤسسات كبيرة** (اكثر من 100): **{large}** مؤسسة ({round(large/total_inst*100,1) if total_inst>0 else 0}%)
        - **متوسط التلاميذ** لكل مؤسسة: **{round(filtered['total_eleves'].mean(), 1) if len(filtered)>0 else 0}**
        - **الحد الاقصى:** {int(filtered['total_eleves'].max()) if len(filtered)>0 else 0} تلميذ
        - **الحد الادنى:** {int(filtered['total_eleves'].min()) if len(filtered)>0 else 0} تلميذ
        """)

# ════════════════════════════════════════════════════════════════════
# TAB 4 - TABLE
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="section-title">قائمة المؤسسات ({len(filtered):,} مؤسسة)</div>', unsafe_allow_html=True)

    display_df = filtered[[
        'CD_ETAB','NOM_ETABA','LA_PROV','COMMUNE','LA_MIL',
        'total_eleves','total_filles','classes_mouwahad','classes_mousharak','total_classes',
        'Gresa_modi','LA_NETAB'
    ]].copy()
    display_df.columns = [
        'رمز المؤسسة','اسم المؤسسة','المديرية','الجماعة','الوسط',
        'اجمالي التلاميذ','الاناث','اقسام موحدة','اقسام مشتركة','اجمالي الاقسام',
        'رمز المرجع','نوع المؤسسة'
    ]
    display_df = display_df.sort_values('اجمالي التلاميذ', ascending=False).reset_index(drop=True)

    # Sort option
    sort_col = st.selectbox("ترتيب حسب", ['اجمالي التلاميذ','الاناث','اجمالي الاقسام','اسم المؤسسة'])
    asc = st.checkbox("ترتيب تصاعدي", value=False)
    display_df = display_df.sort_values(sort_col, ascending=asc).reset_index(drop=True)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=False,
        column_config={
            'رمز المؤسسة': st.column_config.TextColumn(width='small'),
            'اسم المؤسسة': st.column_config.TextColumn(width='large'),
            'اجمالي التلاميذ': st.column_config.NumberColumn(format="%d"),
            'الاناث': st.column_config.NumberColumn(format="%d"),
        }
    )

    # Download
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "تحميل البيانات CSV",
        data=csv.encode('utf-8-sig'),
        file_name=f"مؤسسات_سوس_ماسة_{sel_prov.replace('الكل','الكل')}.csv",
        mime='text/csv'
    )
