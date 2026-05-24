

cat > /home/claude/app.py << 'PYEOF'
import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="السلك الابتدائي - سوس ماسة",
    page_icon="U+1F3EB",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 900; }
.header-box {
    background: linear-gradient(135deg, #0d2137 0%, #1e3f6e 100%);
    border-radius: 16px; padding: 24px 32px; color: white; margin-bottom: 20px;
}
.header-box h1 { font-size: 1.5rem; font-weight: 900; margin: 0; }
.header-box p  { font-size: 0.85rem; opacity: 0.65; margin: 4px 0 0 0; }
.sec-title {
    font-size: 1rem; font-weight: 700; color: #1a2535;
    border-right: 4px solid #1e88e5; padding-right: 10px; margin: 18px 0 10px 0;
}
.branch-card {
    background: #f8fafc; border-radius: 8px; padding: 10px 14px;
    border-right: 4px solid #90caf9; margin-bottom: 6px; font-size: 0.84rem;
}
</style>
""", unsafe_allow_html=True)


# ── LOAD DATA ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("data__3_.xlsx", header=1)
    df.columns = [
        'LA_PROV','COMMUNE','LA_MIL','CD_ETAB','Cd_RAT','Gresa_modi',
        'NOM_ETABA','LA_NETAB','code_zone','X','Y','libformatAr',
        'eleves_mouwahad','eleves_mousharak',
        'filles_mouwahad','filles_mousharak',
        'classes_mouwahad','classes_mousharak'
    ]
    df = df[df['LA_PROV'].notna()]
    df = df[~df['LA_PROV'].astype(str).str.contains('Total', na=False)]
    df = df[df['CD_ETAB'].notna()]

    inst = df.groupby(
        ['LA_PROV','COMMUNE','CD_ETAB','Cd_RAT','Gresa_modi',
         'NOM_ETABA','LA_NETAB','LA_MIL'],
        dropna=False
    ).agg(
        eleves_mouwahad=('eleves_mouwahad','sum'),
        eleves_mousharak=('eleves_mousharak','sum'),
        filles_mouwahad=('filles_mouwahad','sum'),
        filles_mousharak=('filles_mousharak','sum'),
        classes_mouwahad=('classes_mouwahad','sum'),
        classes_mousharak=('classes_mousharak','sum'),
    ).reset_index()

    inst['total_eleves']    = (inst['eleves_mouwahad'] + inst['eleves_mousharak']).astype(int)
    inst['total_filles']    = (inst['filles_mouwahad'] + inst['filles_mousharak']).astype(int)
    inst['classes_mouwahad']  = inst['classes_mouwahad'].round(1)
    inst['classes_mousharak'] = inst['classes_mousharak'].round(1)
    inst['total_classes']   = (inst['classes_mouwahad'] + inst['classes_mousharak']).round(1)
    inst['Gresa_modi'] = inst['Gresa_modi'].fillna('').astype(str)
    inst['Cd_RAT']     = inst['Cd_RAT'].fillna('').astype(str)
    return inst

inst = load_data()

# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### لوحة السلك الابتدائي")
    st.markdown("**جهة سوس - ماسة**")
    st.divider()

    provs = ['الكل'] + sorted(inst['LA_PROV'].unique().tolist())
    sel_prov = st.selectbox("المديرية الاقليمية", provs)

    comm_src = inst if sel_prov == 'الكل' else inst[inst['LA_PROV'] == sel_prov]
    comms = ['الكل'] + sorted(comm_src['COMMUNE'].unique().tolist())
    sel_commune = st.selectbox("الجماعة", comms)

    st.divider()
    search_q = st.text_input("البحث عن مؤسسة", placeholder="اسم او رمز...")
    st.divider()
    st.caption("الموسم الدراسي 2024/2025")

# ── FILTER ─────────────────────────────────────────────────────────
filt = inst.copy()
if sel_prov != 'الكل':
    filt = filt[filt['LA_PROV'] == sel_prov]
if sel_commune != 'الكل':
    filt = filt[filt['COMMUNE'] == sel_commune]

# ── HEADER ─────────────────────────────────────────────────────────
title = f"احصاءات: {sel_prov}" if sel_prov != 'الكل' else "احصاءات جهة سوس - ماسة"
sub   = (f"جماعة: {sel_commune}" if sel_commune != 'الكل'
         else (sel_prov if sel_prov != 'الكل' else "جميع المديريات") + " - السلك الابتدائي")
st.markdown(f'<div class="header-box"><h1>&#x1F3EB; {title}</h1><p>{sub}</p></div>',
            unsafe_allow_html=True)

# ── KPI ────────────────────────────────────────────────────────────
tot_e  = int(filt['total_eleves'].sum())
tot_f  = int(filt['total_filles'].sum())
tot_cm = int(filt['classes_mouwahad'].sum())
tot_cs = round(float(filt['classes_mousharak'].sum()), 1)
tot_cl = round(float(filt['total_classes'].sum()), 1)
nb     = len(filt)
pct_f  = round(tot_f / tot_e * 100, 1) if tot_e > 0 else 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("المؤسسات",       f"{nb:,}")
c2.metric("التلاميذ",       f"{tot_e:,}")
c3.metric("الاناث",         f"{tot_f:,}", f"{pct_f}%")
c4.metric("اقسام موحدة",   f"{tot_cm:,}")
c5.metric("اقسام مشتركة",  f"{tot_cs:,}")
st.divider()

# ── SEARCH ─────────────────────────────────────────────────────────
if search_q and len(search_q.strip()) >= 2:
    q = search_q.strip().lower()
    res = filt[
        filt['NOM_ETABA'].str.lower().str.contains(q, na=False) |
        filt['CD_ETAB'].str.lower().str.contains(q, na=False)
    ]
    st.markdown(f'<div class="sec-title">نتائج البحث ({len(res)})</div>', unsafe_allow_html=True)
    for _, r in res.iterrows():
        gresa = str(r['Gresa_modi'])
        siblings = inst[(inst['Gresa_modi'] == gresa) & (inst['CD_ETAB'] != r['CD_ETAB'])] \
                   if gresa else pd.DataFrame()
        with st.expander(f"&#x1F3EB; {r['NOM_ETABA']} | {r['CD_ETAB']} | {r['LA_PROV']}"):
            i1,i2,i3,i4 = st.columns(4)
            i1.metric("التلاميذ", int(r['total_eleves']))
            i2.metric("الاناث",   int(r['total_filles']))
            i3.metric("اقسام موحدة",   r['classes_mouwahad'])
            i4.metric("اقسام مشتركة",  r['classes_mousharak'])
            st.caption(f"الجماعة: {r['COMMUNE']} | الوسط: {r['LA_MIL']} | رمز المرجع: {gresa}")
            if len(siblings) > 0:
                st.markdown(f"**الوحدات المرتبطة ({len(siblings)}):**")
                for _, s in siblings.iterrows():
                    st.markdown(f"""<div class="branch-card">
                        &#x21B3; <b>{s['NOM_ETABA']}</b>
                        <span style="color:#607d8b;"> | {s['CD_ETAB']}
                        | {int(s['total_eleves'])} تلميذ | {int(s['total_filles'])} اناث
                        | {s['total_classes']} قسم | {s['LA_MIL']}</span>
                    </div>""", unsafe_allow_html=True)
    st.divider()

# ── TABS ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["نظرة عامة", "شبكة المؤسسات",
                                   "توزيع الوحدات", "جدول المؤسسات"])

# ════════════════════════════════
# TAB 1  نظرة عامة
# ════════════════════════════════
with tab1:
    prov_df = filt.groupby('LA_PROV').agg(
        nb_etab     =('CD_ETAB','count'),
        total_eleves=('total_eleves','sum'),
        total_filles=('total_filles','sum'),
        cls_m       =('classes_mouwahad','sum'),
        cls_s       =('classes_mousharak','sum'),
    ).reset_index()
    prov_df['pct_filles'] = (prov_df['total_filles'] /
                             prov_df['total_eleves'] * 100).round(1)
    prov_df = prov_df.set_index('LA_PROV')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sec-title">عدد المؤسسات حسب المديرية</div>',
                    unsafe_allow_html=True)
        st.bar_chart(prov_df['nb_etab'])

    with col2:
        st.markdown('<div class="sec-title">التلاميذ والاناث حسب المديرية</div>',
                    unsafe_allow_html=True)
        st.bar_chart(prov_df[['total_eleves','total_filles']],
                     color=['#1e88e5','#ce93d8'])

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="sec-title">الاقسام الموحدة والمشتركة</div>',
                    unsafe_allow_html=True)
        st.bar_chart(prov_df[['cls_m','cls_s']])

    with col4:
        st.markdown('<div class="sec-title">نسبة الاناث % حسب المديرية</div>',
                    unsafe_allow_html=True)
        st.bar_chart(prov_df['pct_filles'])

    st.markdown('<div class="sec-title">جدول ملخص المديريات</div>',
                unsafe_allow_html=True)
    prov_df2 = prov_df.copy().reset_index()
    prov_df2.columns = ['المديرية','المؤسسات','التلاميذ','الاناث',
                        'اقسام موحدة','اقسام مشتركة','نسبة الاناث %']
    st.dataframe(prov_df2, use_container_width=True, hide_index=True)

    # Milieu
    st.markdown('<div class="sec-title">التوزيع حسب الوسط</div>',
                unsafe_allow_html=True)
    mil_df = filt.groupby('LA_MIL').agg(
        nb=('CD_ETAB','count'),
        eleves=('total_eleves','sum'),
        filles=('total_filles','sum'),
    ).reset_index()
    mil_df.columns = ['الوسط','المؤسسات','التلاميذ','الاناث']
    st.dataframe(mil_df, use_container_width=True, hide_index=True)

# ════════════════════════════════
# TAB 2  شبكة المؤسسات
# ════════════════════════════════
with tab2:
    st.markdown('<div class="sec-title">مجموعات المدارس والوحدات المرتبطة (Gresa_modi)</div>',
                unsafe_allow_html=True)
    st.caption("كل مجموعة تضم الوحدات المدرسية المرتبطة بنفس رمز المرجع.")

    groups = []
    for key, gdf in filt.groupby('Gresa_modi'):
        main = gdf[gdf['CD_ETAB'] == key]
        name = main['NOM_ETABA'].values[0] if len(main) > 0 else gdf['NOM_ETABA'].values[0]
        groups.append({
            'key': key, 'name': name,
            'nb': len(gdf),
            'eleves': int(gdf['total_eleves'].sum()),
            'filles': int(gdf['total_filles'].sum()),
            'classes': round(float(gdf['total_classes'].sum()), 1),
            'members': gdf
        })
    groups.sort(key=lambda x: -x['eleves'])

    PAGE = 15
    total_g = len(groups)
    page = st.number_input(
        f"الصفحة (الاجمالي: {total_g} مجموعة)",
        min_value=1, max_value=max(1, math.ceil(total_g/PAGE)),
        value=1, step=1
    )
    for g in groups[(page-1)*PAGE : page*PAGE]:
        with st.expander(
            f"&#x1F3EB; {g['name']}  |  {g['key']}  |  "
            f"{g['nb']} وحدة  |  {g['eleves']:,} تلميذ  |  {g['filles']:,} اناث"
        ):
            for _, row in g['members'].iterrows():
                is_main = row['CD_ETAB'] == g['key']
                bc = '#1e88e5' if is_main else '#90caf9'
                icon = "&#x1F535;" if is_main else "&#x21B3;"
                st.markdown(f"""<div class="branch-card"
                    style="border-right-color:{bc};">
                    {icon} <b>{row['NOM_ETABA']}</b>
                    <span style="color:#607d8b;">
                    &nbsp;|&nbsp;{row['CD_ETAB']}
                    &nbsp;|&nbsp;{int(row['total_eleves'])} تلميذ
                    &nbsp;|&nbsp;{int(row['total_filles'])} اناث
                    &nbsp;|&nbsp;{row['classes_mouwahad']} موحدة
                    &nbsp;|&nbsp;{row['classes_mousharak']} مشتركة
                    &nbsp;|&nbsp;{row['LA_MIL']}
                    &nbsp;|&nbsp;{row['COMMUNE']}
                    </span></div>""", unsafe_allow_html=True)

# ════════════════════════════════
# TAB 3  توزيع الوحدات
# ════════════════════════════════
with tab3:
    RANGES = [
        ('اقل من 5',  0,   5),
        ('5 - 10',    5,   10),
        ('10 - 30',   10,  30),
        ('30 - 60',   30,  60),
        ('60 - 100',  60,  100),
        ('100 - 300', 100, 300),
        ('300 - 700', 300, 700),
        ('700 فاكثر', 700, 99999),
    ]
    counts = [
        len(filt[(filt['total_eleves'] >= mn) & (filt['total_eleves'] < mx)])
        for _, mn, mx in RANGES
    ]
    total_inst = sum(counts)

    st.markdown('<div class="sec-title">توزيع الوحدات المدرسية حسب عدد التلاميذ</div>',
                unsafe_allow_html=True)

    dist_df = pd.DataFrame({
        'المجال':        [r[0] for r in RANGES],
        'عدد المؤسسات': counts,
        'النسبة %':     [round(c/total_inst*100, 1) if total_inst > 0 else 0 for c in counts],
    }).set_index('المجال')

    st.bar_chart(dist_df['عدد المؤسسات'])
    st.dataframe(dist_df.reset_index(), use_container_width=True, hide_index=True)

    st.markdown('<div class="sec-title">تحليل</div>', unsafe_allow_html=True)
    max_i   = counts.index(max(counts))
    small   = counts[0] + counts[1]
    medium  = counts[2] + counts[3] + counts[4]
    large   = counts[5] + counts[6] + counts[7]
    avg_e   = round(filt['total_eleves'].mean(), 1) if len(filt) > 0 else 0
    max_e   = int(filt['total_eleves'].max()) if len(filt) > 0 else 0
    min_e   = int(filt['total_eleves'].min()) if len(filt) > 0 else 0

    a1, a2, a3 = st.columns(3)
    a1.metric("مؤسسات صغيرة (اقل من 10)",  f"{small}",
              f"{round(small/total_inst*100,1) if total_inst>0 else 0}%")
    a2.metric("مؤسسات متوسطة (10 الى 100)", f"{medium}",
              f"{round(medium/total_inst*100,1) if total_inst>0 else 0}%")
    a3.metric("مؤسسات كبيرة (اكثر من 100)", f"{large}",
              f"{round(large/total_inst*100,1) if total_inst>0 else 0}%")

    b1, b2, b3 = st.columns(3)
    b1.metric("متوسط التلاميذ", avg_e)
    b2.metric("الحد الاقصى",    max_e)
    b3.metric("الحد الادنى",    min_e)

# ════════════════════════════════
# TAB 4  جدول المؤسسات
# ════════════════════════════════
with tab4:
    st.markdown(f'<div class="sec-title">قائمة المؤسسات ({len(filt):,})</div>',
                unsafe_allow_html=True)

    sort_col = st.selectbox("ترتيب حسب",
        ['total_eleves','total_filles','total_classes','NOM_ETABA'])
    asc = st.checkbox("تصاعدي", value=False)

    disp = filt[[
        'CD_ETAB','NOM_ETABA','LA_PROV','COMMUNE','LA_MIL',
        'total_eleves','total_filles',
        'classes_mouwahad','classes_mousharak','total_classes',
        'Gresa_modi','LA_NETAB'
    ]].sort_values(sort_col, ascending=asc).reset_index(drop=True)

    disp.columns = [
        'رمز','الاسم','المديرية','الجماعة','الوسط',
        'التلاميذ','الاناث',
        'موحدة','مشتركة','الاقسام',
        'رمز المرجع','النوع'
    ]
    st.dataframe(disp, use_container_width=True, height=500, hide_index=False)

    csv = disp.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "تحميل CSV",
        data=csv.encode('utf-8-sig'),
        file_name="مؤسسات_سوس_ماسة.csv",
        mime='text/csv'
    )
PYEOF

