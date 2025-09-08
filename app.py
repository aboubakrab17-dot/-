# ----------------------------- #
#         CV Builder App        #
#    Streamlit + FPDF + PIL     #
#   By: بوتك الشاب – نسخة خفيفة  #
# ----------------------------- #

import io
import re
from datetime import datetime

import streamlit as st
from fpdf import FPDF
from PIL import Image

# ----------------------------- #
# إعداد الصفحة والستايل
# ----------------------------- #
st.set_page_config(
    page_title="CV صانع",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# خلفية متدرجة + تنسيق عناصر (واتساب ستايل)
CSS = """
<style>
/* خلفية */
.stApp {
  background: linear-gradient(135deg, #111827 0%, #0b1730 40%, #132a4a 100%);
  color: #e5e7eb;
  font-family: "Segoe UI", system-ui, -apple-system, Arial, sans-serif;
}

/* العنوان */
h1,h2,h3 { color: #e6f0ff !important; }

/* كارت الدردشة */
.chat-card {
  background: #0f172a;
  border: 1px solid #21324d;
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 6px 20px rgba(0,0,0,.25);
}

/* فقاعة المستخدم */
.bubble-me {
  background: #c9f7c1;
  color: #0f172a;
  border-radius: 14px;
  padding: 12px 14px;
  margin: 8px 0;
  max-width: 92%;
}

/* فقاعة البوت */
.bubble-bot {
  background: #e8f0ff;
  color: #0b1730;
  border-radius: 14px;
  padding: 12px 14px;
  margin: 8px 0;
  max-width: 92%;
  border: 1px solid #c6d6ff;
}

/* أزرار */
.stButton>button {
  background: linear-gradient(135deg,#2563eb,#0ea5e9);
  border: 0;
  color: white;
  padding: 10px 16px;
  border-radius: 14px;
  font-weight: 600;
  box-shadow: 0 8px 16px rgba(14,165,233,.25);
}
.stButton>button:hover { filter: brightness(1.06); }

/* حقول الإدخال */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input {
  background: #0f172a !important;
  color: #e5e7eb !important;
  border-radius: 12px;
  border: 1px solid #23324c !important;
}

/* شارة صغيرة */
.badge {
  display:inline-block;
  background:#1f2937;
  border:1px solid #334155;
  color:#d1d5db;
  padding:5px 10px;
  border-radius:999px;
  font-size:12px;
  margin:2px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------- #
# الحالة العامة
# ----------------------------- #
if "step" not in st.session_state: st.session_state.step = 1
if "data" not in st.session_state:
    st.session_state.data = {
        "name": "",
        "title": "",
        "email": "",
        "phone": "",
        "location": "",
        "summary": "",
        "skills": [],
        "languages": [],
        "experience": [],   # كل عنصر dict: {"role","company","period","details"}
        "education": [],    # {"degree","school","year"}
        "projects": [],     # {"name","link","desc"}
        "links": [],        # {"label","url"}
    }

def add_badge(text):
    st.markdown(f"<span class='badge'>{text}</span>", unsafe_allow_html=True)

# ----------------------------- #
# شريط علوي
# ----------------------------- #
st.markdown(
    "<div class='chat-card'><h1>🧾 صانع السيرة — ستايل واتساب</h1>"
    "<p>جاوب خطوة بخطوة، وزّر <strong>إنشاء PDF</strong> في الأخير. الكتابة كبيرة وواضحة، وكل شيء بسيط وسريع ✨</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ----------------------------- #
# معاينة فورية (يمين/يسار)
# ----------------------------- #
left, right = st.columns([1.05, 0.95])

with right:
    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    st.subheader("👀 معاينة سريعة")
    d = st.session_state.data
    if d["name"]:
        st.markdown(f"<div class='bubble-me'><b>{d['name']}</b> — {d.get('title','')}</div>", unsafe_allow_html=True)
    if d["summary"]:
        st.markdown(f"<div class='bubble-bot'>{d['summary']}</div>", unsafe_allow_html=True)
    if d["skills"]:
        st.markdown("**المهارات:** " + "، ".join(d["skills"]))
    if d["languages"]:
        st.markdown("**اللغات:** " + "، ".join(d["languages"]))
    if d["experience"]:
        st.markdown("**الخبرات:**")
        for x in d["experience"]:
            st.markdown(f"- **{x['role']}** @ {x['company']} — _{x['period']}_")
    if d["education"]:
        st.markdown("**التعليم:**")
        for x in d["education"]:
            st.markdown(f"- **{x['degree']}** — {x['school']} ({x['year']})")
    if d["projects"]:
        st.markdown("**المشاريع:**")
        for x in d["projects"]:
            link = f" — [{x['link']}]({x['link']})" if x['link'] else ""
            st.markdown(f"- **{x['name']}**{link}: {x['desc']}")
    if d["links"]:
        st.markdown("**روابط:**")
        for x in d["links"]:
            st.markdown(f"- [{x['label']}]({x['url']})")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------- #
# اقتراحات سريعة (50 اقتراح)
# ----------------------------- #
SUGGESTIONS = [
"اكتب ملخص مهني قصير", "أضف 6 مهارات تقنية", "أضف 6 مهارات شخصية",
"أضف تجربة عمل: مصمم واجهات", "أضف تجربة عمل: مطور باك", "أضف تجربة عمل: خدمة زبائن",
"أضف مشروع ويب شخصي", "أضف مشروع متجر إلكتروني", "أضف مشروع بوت دردشة",
"أضف تعليم: ليسانس إعلام آلي", "أضف تعليم: ماستر إدارة أعمال", "أضف تعليم: تقني سامي",
"أضف لغة: العربية ممتاز", "أضف لغة: الإنجليزية جيد جداً", "أضف لغة: الفرنسية متوسط",
"أضف رابط GitHub", "أضف رابط LinkedIn", "أضف بريد إلكتروني",
"أضف رقم هاتف", "أضف مدينة الإقامة", "أضف لقب وظيفي مناسب",
"نظّم المهارات في فئات", "اكتب إنجازات بالأرقام", "اختصر الملخص لـ 3 أسطر",
"أضف مشروع ذكاء اصطناعي", "أضف مشروع تطبيق جوال", "أضف مشروع تحليل بيانات",
"أضف قسم دورات/شهادات", "أضف قسم الجوائز", "أضف قسم الهوايات",
"رتّب الخبرات من الأحدث للأقدم", "احذف الحشو الزائد", "استخدم لغة عملية",
"أضف كلمات مفتاحية للوظيفة", "راجع الإملاء", "أضف رابط سيرة على الويب",
"أضف مشروع بفريق", "أضف مسؤوليات واضحة", "أضف تقنيات مستخدمة",
"أضف قسم التطوع", "أضف قسم نشاطات", "أضف هدف وظيفي قصير",
"أضف مراجع عند الطلب", "أضف شهادة Google", "أضف شهادة AWS",
"أضف مهارات Office", "أضف مهارات تواصل", "أضف مهارات تنظيم",
"أضف مهارات قيادية", "أضف مهارات حل المشاكل"
]

with left:
    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    st.subheader("💡 اقتراحات سريعة")
    cols = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(s, key=f"sug{i}"):
                # مجرد حشو ذكي بسيط حسب النص
                if "مهارات" in s:
                    st.session_state.data["skills"] = list(set(st.session_state.data["skills"] + ["Teamwork","Problem Solving","Time Management","Communication","Creativity","Adaptability"]))
                elif s.startswith("أضف لغة"):
                    lang = s.split(":")[-1].strip()
                    st.session_state.data["languages"] = list(set(st.session_state.data["languages"] + [lang]))
                elif "GitHub" in s:
                    st.session_state.data["links"].append({"label":"GitHub","url":"https://github.com/username"})
                elif "LinkedIn" in s:
                    st.session_state.data["links"].append({"label":"LinkedIn","url":"https://linkedin.com/in/username"})
                elif "بريد" in s:
                    st.session_state.data["email"] = "yourmail@example.com"
                elif "رقم" in s:
                    st.session_state.data["phone"] = "+213 555 000 000"
                elif "مدينة" in s:
                    st.session_state.data["location"] = "Algiers, Algeria"
                elif "لقب وظيفي" in s:
                    st.session_state.data["title"] = "Frontend Developer"
                elif "ملخص" in s:
                    st.session_state.data["summary"] = "مطور واجهات أمامية شغوف، خبرة في React و Tailwind، أركز على الأداء وتجربة المستخدم وإنجاز المهام بسرعة وبجودة."
                elif "تعليم" in s:
                    st.session_state.data["education"].append({"degree":"BSc Computer Science","school":"University","year":"2023"})
                elif "مشروع" in s:
                    st.session_state.data["projects"].append({"name":"Portfolio Website","link":"https://example.com","desc":"موقع شخصي يعرض الأعمال والتقنيات المستعملة."})
                elif "خبرة" in s:
                    st.session_state.data["experience"].append({"role":"UI/UX Designer","company":"Creative Co.","period":"2022 - 2023","details":"تصميم واجهات تفاعلية وتحسين تجربة المستخدم."})
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------- #
# نموذج الخطوات (Wizard)
# ----------------------------- #
with left:
    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    st.subheader(f"🧩 الخطوة {st.session_state.step} / 5")

    d = st.session_state.data
    step = st.session_state.step

    if step == 1:
        st.markdown("### 👤 المعلومات الأساسية")
        d["name"] = st.text_input("الاسم الكامل", d["name"])
        d["title"] = st.text_input("المسمى الوظيفي (اختياري)", d["title"])
        cols = st.columns(2)
        d["email"] = cols[0].text_input("البريد الإلكتروني", d["email"])
        d["phone"] = cols[1].text_input("الهاتف", d["phone"])
        d["location"] = st.text_input("المدينة / الدولة", d["location"])

    elif step == 2:
        st.markdown("### 🧠 ملخص مهني")
        d["summary"] = st.text_area("اكتب 2–4 أسطر عن نفسك", d["summary"], height=120)

        st.markdown("### 🧰 المهارات")
        skills_str = ", ".join(d["skills"])
        skills_str = st.text_input("أضف مهارات مفصولة بفواصل", skills_str, placeholder="Python, React, Teamwork ...")
        d["skills"] = [s.strip() for s in skills_str.split(",") if s.strip()]

        st.markdown("### 🌍 اللغات")
        langs_str = ", ".join(d["languages"])
        langs_str = st.text_input("أضف لغات مفصولة بفواصل", langs_str, placeholder="Arabic, English, French ...")
        d["languages"] = [s.strip() for s in langs_str.split(",") if s.strip()]

    elif step == 3:
        st.markdown("### 💼 الخبرات")
        with st.form("exp_form", clear_on_submit=True):
            role = st.text_input("المسمى الوظيفي")
            company = st.text_input("الشركة")
            period = st.text_input("الفترة (مثال: 2021 - 2023)")
            details = st.text_area("تفاصيل/إنجازات مختصرة", height=90)
            submitted = st.form_submit_button("➕ إضافة خبرة")
        if submitted and role and company:
            d["experience"].append({"role": role, "company": company, "period": period, "details": details})
        for i, x in enumerate(d["experience"]):
            st.markdown(f"- **{x['role']}** @ {x['company']} — _{x['period']}_")
            if st.button("🗑️ حذف", key=f"del_exp_{i}"):
                d["experience"].pop(i)
                st.experimental_rerun()

    elif step == 4:
        st.markdown("### 🎓 التعليم")
        with st.form("edu_form", clear_on_submit=True):
            degree = st.text_input("الشهادة/الدرجة")
            school = st.text_input("المؤسسة")
            year = st.text_input("العام")
            submitted = st.form_submit_button("➕ إضافة تعليم")
        if submitted and degree and school:
            d["education"].append({"degree": degree, "school": school, "year": year})
        for i, x in enumerate(d["education"]):
            st.markdown(f"- **{x['degree']}** — {x['school']} ({x['year']})")
            if st.button("🗑️ حذف", key=f"del_edu_{i}"):
                d["education"].pop(i)
                st.experimental_rerun()

    elif step == 5:
        st.markdown("### 🧪 المشاريع والروابط")
        with st.form("proj_form", clear_on_submit=True):
            name = st.text_input("اسم المشروع")
            link = st.text_input("رابط (اختياري)")
            desc = st.text_area("وصف مختصر", height=80)
            submitted = st.form_submit_button("➕ إضافة مشروع")
        if submitted and name:
            d["projects"].append({"name": name, "link": link, "desc": desc})

        with st.form("link_form", clear_on_submit=True):
            label = st.text_input("اسم الرابط (GitHub, LinkedIn ...)")
            url = st.text_input("الرابط")
            submitted2 = st.form_submit_button("➕ إضافة رابط")
        if submitted2 and label and url:
            d["links"].append({"label": label, "url": url})

        st.markdown("#### الروابط الحالية")
        for i, x in enumerate(d["links"]):
            st.markdown(f"- **{x['label']}** — {x['url']}")
            if st.button("🗑️ حذف", key=f"del_link_{i}"):
                d["links"].pop(i)
                st.experimental_rerun()

    st.write("")
    c1, c2, c3 = st.columns(3)
    if step > 1 and c1.button("⬅️ السابق"):
        st.session_state.step -= 1
        st.experimental_rerun()
    if step < 5 and c3.button("التالي ➡️"):
        st.session_state.step += 1
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------- #
# توليد PDF (أساسي)
# ملاحظة: FPDF لا يدعم العربية بشكل كامل بدون ملف خط TTF.
# سيعمل جيدًا مع الحروف اللاتينية/الأرقام. للنصوص العربية،
# يمكن إضافة خط TTF لاحقًا (ميزة اختيارية).
# ----------------------------- #
def make_pdf(data: dict) -> bytes:
    pdf = FPDF(format="A4", unit="mm")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ألوان
    PRIMARY = (37, 99, 235)  # أزرق
    pdf.set_fill_color(*PRIMARY)
    pdf.rect(0, 0, 210, 35, "F")

    # العنوان
    pdf.set_xy(10, 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    name_line = (data.get("name") or "Your Name")
    title_line = (data.get("title") or "")
    pdf.cell(0, 7, name_line, ln=1)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 6, title_line, ln=1)

    # معلومات الاتصال
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Contact", ln=1)
    pdf.set_font("Helvetica", "", 11)
    contact = []
    if data.get("email"): contact.append(f"Email: {data['email']}")
    if data.get("phone"): contact.append(f"Phone: {data['phone']}")
    if data.get("location"): contact.append(f"Location: {data['location']}")
    for c in contact:
        pdf.multi_cell(0, 6, c)

    # الملخص
    if data.get("summary"):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Summary", ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, data["summary"])

    # المهارات
    if data.get("skills"):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Skills", ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, " • " + " | ".join(data["skills"]))

    # اللغات
    if data.get("languages"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Languages", ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, " • " + " | ".join(data["languages"]))

    # الخبرات
    if data.get("experience"):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Experience", ln=1)
        pdf.set_font("Helvetica", "", 11)
        for x in data["experience"]:
            header = f"{x['role']} @ {x['company']} ({x['period']})"
            pdf.multi_cell(0, 6, "• " + header)
            if x.get("details"): pdf.multi_cell(0, 6, "   - " + x["details"])

    # التعليم
    if data.get("education"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Education", ln=1)
        pdf.set_font("Helvetica", "", 11)
        for x in data["education"]:
            pdf.multi_cell(0, 6, f"• {x['degree']} — {x['school']} ({x['year']})")

    # المشاريع
    if data.get("projects"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Projects", ln=1)
        pdf.set_font("Helvetica", "", 11)
        for x in data["projects"]:
            line = f"• {x['name']}"
            if x.get("link"): line += f" — {x['link']}"
            pdf.multi_cell(0, 6, line)
            if x.get("desc"): pdf.multi_cell(0, 6, "   - " + x["desc"])

    # الروابط
    if data.get("links"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Links", ln=1)
        pdf.set_font("Helvetica", "", 11)
        for x in data["links"]:
            pdf.multi_cell(0, 6, f"• {x['label']}: {x['url']}")

    # تذييل
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} • CV Builder")

    return bytes(pdf.output(dest="S").encode("latin1"))

# ----------------------------- #
# أزرار التصدير
# ----------------------------- #
with left:
    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    st.subheader("📤 تصدير")

    pdf_bytes = make_pdf(st.session_state.data)
    st.download_button(
        "⬇️ تنزيل PDF",
        data=pdf_bytes,
        file_name=f"CV_{(st.session_state.data.get('name') or 'my').replace(' ','_')}.pdf",
        mime="application/pdf",
    )

    # حفظ JSON بسيط
    import json
    st.download_button(
        "💾 حفظ البيانات (JSON)",
        data=json.dumps(st.session_state.data, ensure_ascii=False, indent=2),
        file_name="cv_data.json",
        mime="application/json",
    )

    st.caption("تنبيه: لعرض العربية بشكل مثالي داخل الـ PDF، تحتاج إضافة خط TTF لاحقًا (ميزة اختيارية).")

    st.markdown("</div>", unsafe_allow_html=True)
