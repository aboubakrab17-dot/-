# app.py
# -*- coding: utf-8 -*-

import json
from pathlib import Path
import streamlit as st

APP_TITLE = "📿 أذكاري – (حصن المسلم المصغّر)"
DATA_FILE = Path(__file__).with_name("adhkar.json")

# -----------------------------
# تهيئة عامّة
# -----------------------------
st.set_page_config(page_title="أذكاري", page_icon="📿", layout="centered")

# ثيم وخط عربي وخلفية
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
:root{
  --card-bg: rgba(255,255,255,0.82);
  --card-border: rgba(0,0,0,0.06);
}
html, body, [class*="css"]  {
  font-family: 'Cairo', sans-serif !important;
}
.stApp {
  background: linear-gradient(135deg, #c9e6ff 0%, #a5d8ff 35%, #95d0ff 60%, #9ad0e8 100%),
              url('https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1600&q=60');
  background-attachment: fixed;
  background-size: cover;
}
.block-container { padding-top: 1.2rem; padding-bottom: 4rem; }
h1, h2, h3 { color:#0b2e4f; }
.adk-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 1.1rem 1.1rem 0.8rem 1.1rem;
  margin-bottom: 0.9rem;
  box-shadow: 0 10px 20px rgba(0,0,0,0.04);
}
.adk-title { font-weight: 800; font-size: 1.15rem; color:#0b2e4f; margin-bottom: .35rem; }
.adk-meta { font-size: .86rem; color:#2f4c63; opacity:.85; margin-top:.3rem }
.adk-text { font-size: 1.05rem; line-height: 2; direction: rtl; white-space: pre-wrap; }
.adk-badge {
  display:inline-block; padding:.2rem .55rem; border-radius:999px; background:#e8f4ff; 
  border:1px solid #b5dbff; font-size:.8rem; margin-right:.4rem; color:#0b2e4f;
}
.grid-2 > div { width:100% }
@media (min-width: 800px){
  .grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap: .8rem }
}
.stButton>button {
  border-radius: 12px !important;
  font-weight: 700;
}
.search-box input { border-radius: 999px !important; border: 1px solid #b5dbff !important; }
.small { font-size:.86rem; opacity:.85 }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# تحميل البيانات
# -----------------------------
def load_data() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # إن لم يوجد الملف (للاحتياط)
    return {"sections": []}

DATA = load_data()
SECTIONS = {sec["id"]: sec for sec in DATA.get("sections", [])}

# -----------------------------
# حالة التطبيق
# -----------------------------
def ensure_state():
    st.session_state.setdefault("page", "home")           # home | section | favorites | search
    st.session_state.setdefault("current_section", None)  # section id
    st.session_state.setdefault("favs", set())            # set of (sec_id, index)

ensure_state()

def go(page: str, **kwargs):
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

# -----------------------------
# أدوات مساعدة
# -----------------------------
def section_button(title: str, sec_id: str):
    if st.button(f"📗 {title}", key=f"btn_{sec_id}"):
        go("section", current_section=sec_id)

def render_header():
    st.write(f"### {APP_TITLE}")
    st.caption("صَلِّ على النبي ﷺ — مرحبًا بك! اختر فصلًا لتقرأه مباشرة. يعرض كل ذكر: النص + المصدر + الفضل + عدد التكرار.")

def render_search_box():
    q = st.text_input("🔎 اكتب كلمة للبحث (مثال: 'أستغفر' أو 'سبحان الله')", key="q", placeholder="ابحث في جميع الأذكار…", label_visibility="collapsed")
    return (q or "").strip()

def render_section(sec):
    st.markdown(f"### {sec['title']}")
    st.button("⬅️ العودة للقائمة الرئيسية", on_click=lambda: go("home"), key=f"back_{sec['id']}")
    st.download_button("⬇️ تحميل هذا القسم (JSON)", data=json.dumps(sec, ensure_ascii=False, indent=2),
                       file_name=f"{sec['id']}.json", mime="application/json", key=f"dl_{sec['id']}")

    st.write("")
    items = sec.get("items", [])
    for i, it in enumerate(items):
        card_key = f"card_{sec['id']}_{i}"
        fav_key = f"{sec['id']}::{i}"
        is_fav = fav_key in st.session_state.favs

        st.markdown('<div class="adk-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-title">{it.get("title","")}</div>', unsafe_allow_html=True)

        # شارات صغيرة
        repeat = it.get("repeat", 1)
        st.markdown(
            f'<span class="adk-badge">🔁 التكرار: {repeat}</span>'
            f' <span class="adk-badge">📚 المصدر</span> '
            f'<span class="adk-badge">✨ الفضل</span>',
            unsafe_allow_html=True
        )
        st.write("")
        st.markdown(f'<div class="adk-text">{it.get("text","")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-meta">📚 {it.get("source","")}<br>✨ {it.get("benefit","")}</div>', unsafe_allow_html=True)

        # أزرار المفضلة + عدّاد بسيط للتكرار
        cols = st.columns([1,1.2, 6])
        with cols[0]:
            if st.button(("⭐️ إزالة من المفضلة" if is_fav else "☆ إضافة للمفضلة"), key=f"fav_{fav_key}"):
                if is_fav:
                    st.session_state.favs.discard(fav_key)
                else:
                    st.session_state.favs.add(fav_key)
                st.rerun()
        with cols[1]:
            done_key = f"done_{fav_key}"
            cnt = st.number_input("عدّاد", min_value=0, max_value=1000, value=0, key=done_key, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

def render_home():
    render_header()

    # بحث سريع أعلى الصفحة
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    q = render_search_box()
    st.markdown('</div>', unsafe_allow_html=True)
    if q:
        go("search", q=q)

    st.markdown("## 🌿 الأقسام المتوفرة")
    grid = st.container()
    with grid:
        cols = st.columns(2)
        sec_list = list(SECTIONS.values())
        for idx, sec in enumerate(sec_list):
            with cols[idx % 2]:
                section_button(sec["title"], sec["id"])

    st.markdown("## 🔎 البحث السريع في كل الأذكار")
    q2 = st.text_input("اكتب كلمة للبحث (مثال: 'أستغفر' أو 'سبحان الله')", key="q2", placeholder="ابحث في جميع الأقسام…")
    if q2.strip():
        go("search", q=q2.strip())

    st.button("⭐️ المفضلات والموارد", on_click=lambda: go("favorites"))

def render_search(q: str):
    st.button("⬅️ رجوع", on_click=lambda: go("home"))
    st.markdown(f"### نتائج البحث عن: **{q}**")

    found = []
    for sec in SECTIONS.values():
        for i, it in enumerate(sec.get("items", [])):
            blob = f"{it.get('title','')} {it.get('text','')} {it.get('source','')} {it.get('benefit','')}"
            if q in blob:
                found.append((sec, i, it))

    if not found:
        st.info("لا توجد نتائج مطابقة.")
        return

    for sec, i, it in found:
        st.markdown('<div class="adk-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-title">[{sec["title"]}] — {it["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-text">{it["text"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-meta">📚 {it.get("source","")}<br>✨ {it.get("benefit","")}</div>', unsafe_allow_html=True)
        cols = st.columns([1,3])
        with cols[0]:
            if st.button("فتح القسم", key=f"open_{sec['id']}_{i}"):
                go("section", current_section=sec["id"])
        st.markdown("</div>", unsafe_allow_html=True)

def render_favorites():
    st.button("⬅️ رجوع", on_click=lambda: go("home"))
    st.markdown("### ⭐️ المفضلات")
    favs = sorted(list(st.session_state.favs))
    if not favs:
        st.info("لا توجد أذكار في المفضلة بعد.")
        return
    for fav in favs:
        sec_id, idx = fav.split("::")
        idx = int(idx)
        sec = SECTIONS.get(sec_id)
        if not sec: continue
        it = sec["items"][idx]
        st.markdown('<div class="adk-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-title">[{sec["title"]}] — {it["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-text">{it["text"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="adk-meta">📚 {it.get("source","")}<br>✨ {it.get("benefit","")}</div>', unsafe_allow_html=True)
        if st.button("إزالة من المفضلة", key=f"rm_{fav}"):
            st.session_state.favs.discard(fav)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# التوجيه (Routing)
# -----------------------------
page = st.session_state.page

if page == "home":
    render_home()

elif page == "section":
    sec_id = st.session_state.get("current_section")
    sec = SECTIONS.get(sec_id)
    if not sec:
        st.warning("القسم غير موجود.")
        st.button("⬅️ رجوع", on_click=lambda: go("home"))
    else:
        render_section(sec)

elif page == "search":
    render_search(st.session_state.get("q", ""))

elif page == "favorites":
    render_favorites()

else:
    go("home")
