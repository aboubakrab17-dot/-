# -*- coding: utf-8 -*-
import json, re, random, io, base64
from datetime import datetime
import streamlit as st

# --------------------------- الإعدادات العامة ---------------------------
st.set_page_config(page_title="حصن المسلم - أذكار", page_icon="🌿", layout="centered")

# جلسة
ss = st.session_state
if "favorites" not in ss: ss.favorites = set()
if "font_size" not in ss: ss.font_size = 22
if "line_height" not in ss: ss.line_height = 2.0
if "theme" not in ss: ss.theme = "light"     # light | dark
if "wird" not in ss: ss.wird = []            # ورد اليوم (قائمة من المفاتيح (قسم, index))

# --------------------------- تنسيقات CSS راقية ---------------------------
def inject_css():
    grad_light = "linear-gradient(135deg,#E6F4EA 0%,#D6E6FF 50%,#F9F7E8 100%)"
    grad_dark  = "linear-gradient(135deg,#0f172a 0%,#0b2b29 50%,#111827 100%)"
    card_bg_l  = "rgba(255,255,255,.78)"
    card_bg_d  = "rgba(17,24,39,.66)"
    font_url   = "https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap"

    st.markdown(f"""
    <style>
      @import url('{font_url}');
      html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Amiri', 'Scheherazade', 'Traditional Arabic', serif !important;
        direction: rtl; text-align: right;
        background: {grad_dark if ss.theme=='dark' else grad_light};
        scroll-behavior: smooth;
      }}
      h1,h2,h3,h4,h5,h6 {{
        letter-spacing: .2px; margin-top:.1rem; margin-bottom:.35rem;
      }}
      .book-card {{
        backdrop-filter: blur(8px);
        background:{card_bg_d if ss.theme=='dark' else card_bg_l};
        border: 1px solid rgba(0,0,0,.08);
        border-radius: 18px; padding: 18px 18px;
        margin: 10px 0 16px 0;
        box-shadow: 0 8px 24px rgba(0,0,0,.06);
      }}
      .badge {{
        display:inline-block; padding:.2rem .6rem; border-radius:999px;
        font-size: .9rem; margin-left:.35rem;
        background: #10b98122; border:1px solid #10b98155;
      }}
      .muted {{ opacity:.8 }}
      .mark  {{ background:#fde68a; padding:2px 4px; border-radius:6px; }}
      .toolbar {{ display:flex; gap:.4rem; align-items:center; margin-top:.6rem }}
      .btn {{
        border:1px solid rgba(0,0,0,.12); padding:.25rem .6rem; border-radius:10px;
        background:rgba(255,255,255,.6); cursor:pointer; font-size:.95rem
      }}
      .btn:hover {{ filter:brightness(.95) }}
      .counter {{
        display:inline-flex; gap:.35rem; align-items:center;
        padding:.15rem .55rem; border-radius:999px; border:1px dashed #94a3b8;
      }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# --------------------------- تحميل البيانات ---------------------------
@st.cache_data(show_spinner=False)
def load_adhkar():
    """يحمل ملف adhkar.json، وإن لم يوجد يرجع عيّنة صغيرة للعرض."""
    try:
        with open("adhkar.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        return data
    except Exception:
        # عيّنة بسيطة – يمكنك استبدالها لاحقًا بملفك الكامل
        sample = {
          "أذكار الصباح": [
            {"text":"أصبحنا وأصبح الملك لله، والحمد لله...","reference":"رواه مسلم","benefit":"تحصين اليوم وطلب البركة"},
            {"text":"اللهم بك أصبحنا وبك أمسينا...","reference":"رواه الترمذي","benefit":"تفويض الأمر لله"}
          ],
          "أذكار المساء": [
            {"text":"أمسينا وأمسى الملك لله...","reference":"رواه مسلم","benefit":"التحصين عند المساء"}
          ],
          "أذكار النوم": [
            {"text":"باسمك اللهم أموت وأحيا","reference":"البخاري","benefit":"حفظ قبل النوم"}
          ],
          "بعد الصلاة": [
            {"text":"أستغفر الله (ثلاثًا) ثم: اللهم أنت السلام ومنك السلام...","reference":"مسلم","benefit":"تكفير الذنوب بعد الصلاة"}
          ]
        }
        return sample

ADHKAR = load_adhkar()

# --------------------------- أدوات مساعدة ---------------------------
def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def highlight(text: str, query: str) -> str:
    if not query: return text
    pattern = re.escape(query)
    return re.sub(pattern, lambda m: f"<span class='mark'>{m.group(0)}</span>", text, flags=re.IGNORECASE)

def as_download_bytes(txt: str, filename="adhkar.txt") -> bytes:
    return txt.encode("utf-8")

def section_to_text(section_name: str) -> str:
    items = ADHKAR.get(section_name, [])
    lines = [f"📗 {section_name}", "-"*40]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}️⃣  {normalize(it.get('text',''))}")
        if it.get("reference"): lines.append(f"   📖 المرجع: {normalize(it['reference'])}")
        if it.get("benefit"):   lines.append(f"   🌿 الفائدة: {normalize(it['benefit'])}")
        lines.append("")
    return "\n".join(lines).strip()

def toggle_fav(key_tuple):
    key = json.dumps(key_tuple, ensure_ascii=False)
    if key in ss.favorites: ss.favorites.remove(key)
    else: ss.favorites.add(key)

def fav_badge(key_tuple):
    key = json.dumps(key_tuple, ensure_ascii=False)
    return "⭐️ مفضّل" if key in ss.favorites else "☆ أضف للمفضلة"

# --------------------------- رأس الصفحة ---------------------------
st.markdown(
    f"""
    <div style="text-align:center;margin:.3rem 0 1rem 0">
      <div style="font-size:2.2rem">🌸 حصن المسلم</div>
      <div class="muted" style="font-size:1.15rem">صلِّ على النبي ﷺ – اقرأ أذكارك بشكل كتابي واضح بلا ضغط زائد</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------- إعدادات سريعة ---------------------------
with st.expander("⚙️ إعدادات العرض", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        ss.font_size = st.slider("حجم الخط", 18, 30, ss.font_size, 1)
    with c2:
        ss.line_height = st.slider("تباعد السطور", 1.2, 2.6, ss.line_height, .1)
    with c3:
        ss.theme = st.radio("المظهر", ["light","dark"], index=0 if ss.theme=="light" else 1, horizontal=True)
    st.caption("يُحفظ الضبط أثناء الجلسة تلقائيًا.")

st.markdown(
    f"<style>.book-card, .book-card * {{ font-size:{ss.font_size}px; line-height:{ss.line_height}em; }}</style>",
    unsafe_allow_html=True
)

# --------------------------- تبويبات رئيسية قليلة الأزرار ---------------------------
tab_book, tab_search, tab_fav, tab_wird, tab_tasbih = st.tabs(
    ["📖 الكتاب", "🔎 البحث", "⭐ المفضلة", "🗓️ ورد اليوم", "🧿 مُسبّحة"]
)

# =========================== 📖 الكتاب ===========================
with tab_book:
    st.subheader("الأقسام")
    # قائمة الأقسام كسطر واحد قابل للتمرير – بدون أزرار كثيرة
    section_names = list(ADHKAR.keys())
    idx = st.selectbox("اختر قسماً للعرض دفعة واحدة:", section_names, index=0, label_visibility="collapsed")
    st.markdown("—"*40)

    # عرض القسم كصفحات كتابية متتالية
    items = ADHKAR.get(idx, [])
    if not items:
        st.info("لا توجد مواد في هذا القسم حالياً.")
    else:
        st.markdown(f"### 📗 {idx}")
        st.caption("يُعرض القسم كاملاً ككتاب. يمكنك الإضافة إلى المفضلة أو التنزيل كملف نصي.")
        # تنزيل القسم
        st.download_button(
            "⬇️ تنزيل القسم (TXT)",
            data=as_download_bytes(section_to_text(idx)),
            file_name=f"{idx}.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.markdown("")

        for i, it in enumerate(items, 1):
            text   = normalize(it.get("text",""))
            ref    = normalize(it.get("reference",""))
            benefit= normalize(it.get("benefit",""))
            with st.container():
                st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                st.markdown(f"**{i}️⃣ الذِّكر:**<br>{text}", unsafe_allow_html=True)
                if ref:
                    st.markdown(f"<div class='badge'>📖 {ref}</div>", unsafe_allow_html=True)
                if benefit:
                    st.markdown(f"<div class='badge'>🌿 {benefit}</div>", unsafe_allow_html=True)

                # شريط أدوات صغير جداً
                colA, colB, colC = st.columns([1,1,1])
                with colA:
                    if st.button(fav_badge((idx, i-1)), key=f"fav_{idx}_{i}"):
                        toggle_fav((idx, i-1))
                with colB:
                    st.download_button("📥 تنزيل الذكر", data=as_download_bytes(text+"\n"), file_name=f"{idx}_{i}.txt", key=f"dl_{idx}_{i}")
                with colC:
                    add_to_wird = st.button("🗓️ أضِفه لورد اليوم", key=f"wird_{idx}_{i}")
                    if add_to_wird:
                        ss.wird.append((idx, i-1))
                        st.success("أُضيف الذكر إلى ورد اليوم.")

                st.markdown("</div>", unsafe_allow_html=True)

# =========================== 🔎 البحث ===========================
with tab_search:
    st.subheader("ابحث في كل الأذكار")
    q = st.text_input("اكتب كلمة للبحث (مثال: أستغفر، سبحان، الملك...)", "")
    if q:
        q_norm = normalize(q)
        results = []
        for sec, lst in ADHKAR.items():
            for j, it in enumerate(lst):
                haystack = " ".join([it.get("text",""), it.get("benefit",""), it.get("reference","")])
                if q_norm and q_norm in haystack:
                    results.append((sec, j, it))
        st.caption(f"النتائج: {len(results)}")
        if results:
            for sec, j, it in results:
                st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                st.markdown(f"**📗 {sec}**", unsafe_allow_html=True)
                st.markdown(highlight(normalize(it.get('text','')), q_norm), unsafe_allow_html=True)
                if it.get("reference"):
                    st.markdown(f"<span class='badge'>📖 {highlight(it['reference'], q_norm)}</span>", unsafe_allow_html=True)
                if it.get("benefit"):
                    st.markdown(f"<span class='badge'>🌿 {highlight(it['benefit'], q_norm)}</span>", unsafe_allow_html=True)
                if st.button(fav_badge((sec, j)), key=f"sf_{sec}_{j}"):
                    toggle_fav((sec, j))
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("لا نتائج مطابقة.")
    else:
        st.caption("ابدأ الكتابة للبحث المباشر.")

# =========================== ⭐ المفضلة ===========================
with tab_fav:
    st.subheader("قائمة المفضلة")
    if not ss.favorites:
        st.info("لا توجد مفضلات بعد. أضِف من تبويب (الكتاب) أو (البحث).")
    else:
        fav_keys = [json.loads(k) for k in ss.favorites]
        txt_all = []
        for sec, j in fav_keys:
            item = ADHKAR.get(sec, [])[j]
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            st.markdown(f"**📗 {sec}**", unsafe_allow_html=True)
            st.markdown(normalize(item.get("text","")))
            if item.get("reference"): st.caption("📖 " + item["reference"])
            if item.get("benefit"):   st.caption("🌿 " + item["benefit"])
            if st.button("🗑️ إزالة من المفضلة", key=f"rm_{sec}_{j}"):
                toggle_fav((sec, j))
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            txt_all.append(f"{sec} - {normalize(item.get('text',''))}")

        st.download_button("⬇️ تنزيل المفضلة (TXT)", data=as_download_bytes("\n\n".join(txt_all)),
                           file_name="favorites.txt", use_container_width=True)

# =========================== 🗓️ ورد اليوم ===========================
with tab_wird:
    st.subheader("ورد اليوم")
    st.caption("اختيار تلقائي لعدد من الأذكار من الأقسام (يمكنك الإضافة يدويًا من تبويب الكتاب).")
    cols = st.columns([2,1])
    with cols[0]:
        count = st.slider("كم ذكراً؟", 3, 20, 7)
    with cols[1]:
        if st.button("🔁 توليد ورد جديد", use_container_width=True):
            choices = []
            for sec, lst in ADHKAR.items():
                choices += [(sec, i) for i in range(len(lst))]
            random.shuffle(choices)
            ss.wird = choices[:count]
    if not ss.wird:
        st.info("أنشئ وردًا من الزر أعلاه أو أضف أذكارًا من تبويب الكتاب.")
    else:
        for sec, j in ss.wird:
            it = ADHKAR.get(sec, [])[j]
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            st.markdown(f"**📗 {sec}**", unsafe_allow_html=True)
            st.markdown(normalize(it.get("text","")))
            if it.get("reference"): st.caption("📖 " + it["reference"])
            if it.get("benefit"):   st.caption("🌿 " + it["benefit"])
            st.markdown("</div>", unsafe_allow_html=True)

        # تنزيل الورد
        lines = []
        for sec, j in ss.wird:
            it = ADHKAR.get(sec, [])[j]
            lines.append(f"{sec} - {normalize(it.get('text',''))}")
        st.download_button("⬇️ تنزيل ورد اليوم (TXT)",
                           data=as_download_bytes("\n\n".join(lines)),
                           file_name=f"ورد_{datetime.now().date()}.txt",
                           use_container_width=True)

# =========================== 🧿 مُسبّحة ===========================
with tab_tasbih:
    st.subheader("مُسبّحة بسيطة")
    if "tasbih" not in ss: ss.tasbih = {"phrase": "سُبحانَ الله", "count": 0, "target": 33}
    c1,c2,c3,c4 = st.columns([3,1,1,1])
    with c1:
        ss.tasbih["phrase"] = st.text_input("الذِّكر:", ss.tasbih["phrase"])
    with c2:
        ss.tasbih["target"] = st.number_input("الهدف", 1, 1000, ss.tasbih["target"], step=1)
    with c3:
        if st.button("➕"):
            ss.tasbih["count"] += 1
    with c4:
        if st.button("🔄 تصفير"):
            ss.tasbih["count"] = 0

    prog = min(1.0, ss.tasbih["count"]/max(1,ss.tasbih["target"]))
    st.progress(prog, text=f"{ss.tasbih['count']} / {ss.tasbih['target']}")
    st.markdown(
        f"<div class='book-card'><div class='counter'>🧿 {ss.tasbih['phrase']} — الحالي: {ss.tasbih['count']}</div></div>",
        unsafe_allow_html=True
    )

# --------------------------- تذييل ---------------------------
st.markdown("---")
st.caption("المصدر المقترح: «حصن المسلم» – النصوص تُدرج من ملف adhkar.json. \
أضِف جميع الأذكار المأثورة مع المراجع والفوائد داخل الملف ليظهر الكتاب كاملاً.")
