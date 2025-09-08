# app.py
# تطبيق Streamlit: "أذكار - كتاب رقمي" (واجهة إسلامية، عرض كتب الأذكار بالكامل)
# التعليمات: ضع ملف adhkar.json في نفس المجلد، ثم شغّل: streamlit run app.py

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import base64

st.set_page_config(page_title="أذكار - كتاب رقمي", page_icon="🌺", layout="wide")

# ---- CSS & خلفية وتصميم ----
PAGE_BG = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

html, body, [class*="css"]  {
  font-family: 'Cairo', sans-serif;
}

.stApp {
  background-image: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(0,0,0,0.05)), url('https://images.unsplash.com/photo-1505682634904-d7c8d5b1f0b7?auto=format&fit=crop&w=1400&q=60');
  background-size: cover;
  color: #0b2340;
}

.header {
  padding: 28px 40px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
  box-shadow: 0 6px 20px rgba(2,6,23,0.25);
  margin-bottom: 18px;
}

.h-title {
  font-size: 34px;
  font-weight: 700;
  color: #06344b;
}

.h-sub {
  color: #0a5566;
  margin-top: 6px;
  opacity: 0.95;
}

/* بطاقات الأقسام */
.section-card {
  background: rgba(255,255,255,0.85);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 8px 4px;
  transition: transform .12s ease;
  box-shadow: 0 6px 16px rgba(10,20,30,0.08);
}
.section-card:hover { transform: translateY(-4px); }

/* عرض الكتاب */
.book {
  background: rgba(255,255,255,0.94);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 10px 30px rgba(5,10,20,0.12);
  color: #062033;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
}

/* زر جميل */
.big-btn{
  background: linear-gradient(90deg,#3ad59f,#2ba6ff);
  color: white;
  padding: 10px 16px;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

/* نص الأذكار */
.adhkar-text {
  font-size: 20px;
  line-height: 1.8;
  margin-bottom: 12px;
}

/* مرجع وفائدة */
.meta {
  color: #083542;
  opacity: 0.85;
  font-size: 14px;
  margin-top: 6px;
  margin-bottom: 18px;
  background: rgba(10,20,20,0.02);
  padding: 8px;
  border-radius: 8px;
}

/* favorite badge */
.fav {
  padding: 6px 10px;
  background: #ffdede;
  border-radius: 8px;
  font-weight: 600;
  color: #7a1420;
}

.small {
  font-size: 13px;
  opacity: 0.85;
  color: #043240;
}
</style>
"""

st.markdown(PAGE_BG, unsafe_allow_html=True)

# ---- utils ----
DATA_FILE = Path("adhkar.json")
SAMPLE_FILE = Path("adhkar_sample.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    elif SAMPLE_FILE.exists():
        with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"sections": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def to_download_link(obj, filename="download.json"):
    b = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    b64 = base64.b64encode(b).decode()
    href = f'<a download="{filename}" href="data:application/json;base64,{b64}">⬇️ تحميل نسخة JSON</a>'
    return href

# ---- session_state init ----
if "section" not in st.session_state:
    st.session_state.section = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []

data = load_data()

# ---- Header / Intro ----
with st.container():
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown('<div class="header">', unsafe_allow_html=True)
        st.markdown('<div class="h-title">🌺 أذكار — كتاب رقمي (حصن المصطفى)</div>', unsafe_allow_html=True)
        st.markdown('<div class="h-sub">صَلِّ على النبي ﷺ — مرحباً بك! اختر فصلاً لتقرأه مباشرة على شكل كتاب. كل ذكر: نص + مرجع + فائدة.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.write("")
        if st.button("🏠 الرئيسية"):
            st.session_state.section = None

# ---- Sidebar: قائمة الأقسام + أدوات ----
with st.sidebar:
    st.header("القائمة")
    st.write("تصفّح الأقسام أو حمّل/حرّر البيانات")
    if st.button("⟳ إعادة تحميل البيانات"):
        st.experimental_rerun()
    st.markdown("---")
    st.subheader("أقسام متاحة")
    for sec in data.get("sections", []):
        text = sec.get("title", "بدون عنوان")
        if st.button(f"📖 {text}"):
            st.session_state.section = sec["id"]
    st.markdown("---")
    st.subheader("أدوات")
    st.markdown(to_download_link(data, filename="adhkar_export.json"), unsafe_allow_html=True)
    st.markdown("**ملاحظة:** لتحميل/تعديل الأذكار، أنشئ/حرّر ملف `adhkar.json` في نفس المجلد حسب الصيغة الموضّحة في المستند.")

# ---- Main UI ----
st.markdown("<div class='book'>", unsafe_allow_html=True)

if st.session_state.section is None:
    # عرض القائمة الرئيسية بشكل جذاب
    st.markdown("## 🌿 الأقسام المتوفرة")
    cols = st.columns(2)
    for i, sec in enumerate(data.get("sections", [])):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="section-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <div style="font-weight:700; font-size:18px;">{sec.get('title')}</div>
                  <div class="small">{sec.get('subtitle', '')}</div>
                </div>
                <div style="text-align:right;">
                  <div class="fav">{len(sec.get('items', []))} ذِكر</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔎 البحث السريع في كل الأذكار")
    q = st.text_input("اكتب كلمة للبحث (مثال: 'أستغفر' أو 'سبحان الله')", value="")
    if q.strip():
        found = []
        ql = q.strip().lower()
        for sec in data.get("sections", []):
            for item in sec.get("items", []):
                if ql in item.get("text", "").lower() or ql in item.get("title", "").lower():
                    found.append((sec, item))
        st.markdown(f"#### نتائج البحث ({len(found)})")
        for sec, item in found:
            st.markdown(f"**{sec['title']}** — **{item.get('title','')}**")
            st.markdown(f"<div class='adhkar-text'>{item.get('text')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta'>مرجع: {item.get('source','-')} · فائدة: {item.get('benefit','-')}</div>", unsafe_allow_html=True)

else:
    # عرض صفحة قسم كـكتاب (كل الأذكار تظهر دفعة واحدة)
    sec = next((s for s in data.get("sections", []) if s["id"] == st.session_state.section), None)
    if not sec:
        st.error("القسم غير موجود")
    else:
        st.markdown(f"<div class='section-title'>{sec.get('title')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small'>{sec.get('subtitle','')}</div>", unsafe_allow_html=True)
        st.markdown("---")
        # أزرار أعلى الصفحة
        col_a, col_b, col_c = st.columns([1,2,1])
        with col_a:
            if st.button("🔙 الرجوع"):
                st.session_state.section = None
        with col_b:
            if st.button("★ إضافة للمفضلات"):
                if sec["id"] not in st.session_state.favorites:
                    st.session_state.favorites.append(sec["id"])
                    st.success("تمت الإضافة للمفضلات")
                else:
                    st.info("موجود بالفعل في المفضلات")
        with col_c:
            if st.button("⬇️ تنزيل القسم (JSON)"):
                st.markdown(to_download_link(sec, filename=f"{sec['id']}.json"), unsafe_allow_html=True)

        # عرض كل الأذكار داخل القسم (كتاب)
        for idx, item in enumerate(sec.get("items", []), start=1):
            st.markdown(f"<div style='margin-top:10px'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700; font-size:18px;'>{idx}. {item.get('title','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='adhkar-text'>{item.get('text','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta'>📚 المرجع: {item.get('source','غير محدد')} &nbsp; • &nbsp; ✅ الفائدة: {item.get('benefit','-')}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---- Footer: المفضلات وملفات التوثيق ----
with st.expander("المفضلات والموارد"):
    st.write("📌 المفضلات (الأقسام التي حفظتها):")
    for fav in st.session_state.favorites:
        sec = next((s for s in data.get("sections", []) if s["id"] == fav), None)
        if sec:
            st.write(f"- {sec['title']} ({len(sec.get('items',[]))} ذكر)")
    st.markdown("---")
    st.write("📝 ملاحظة مهمة عن المحتوى:")
    st.write("""
    * ضع نصوص الأذكار في ملف `adhkar.json` بنفس الصيغة المتّبعة بالأسفل (أنشأت ملف عيّنة `adhkar_sample.json`).
    * إذا أردت إدراج نصوص مأخوذة من كتاب معين، تأكد من الترخيص أو استخدم نصوص أصلية/عربية مُعتمدة أو استشهد بالمصدر.
    """)
    st.markdown("---")
    st.write("📂 صيغة JSON المطلوبة (مثال مختصر):")
    st.code("""
{
  "sections": [
    {
      "id": "morning",
      "title": "أذكار الصباح",
      "subtitle": "أذكار الصباح من السنة",
      "items": [
        {
          "title": "بسم الله الذي لا يضر",
          "text": "بِسْمِ اللَّهِ الَّذِي لا يَضُرُّ...",
          "source": "حديث - صحيح ...",
          "benefit": "حماية من كل ضرر"
        }
      ]
    }
  ]
}
    """, language="json")

# نهاية الملف
