# app.py
import os
import io
import requests
from PIL import Image
import streamlit as st

# PDF libs
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# ---- SETTINGS ----
st.set_page_config(page_title="CV Builder — بوت السيفي", layout="centered", page_icon="📄")

# Create fonts folder
FONTS_DIR = "fonts"
os.makedirs(FONTS_DIR, exist_ok=True)

# Try to download a good Arabic TTF if missing
FONT_NAME = "NotoNaskhArabic-Regular.ttf"
FONT_PATH = os.path.join(FONTS_DIR, FONT_NAME)
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf"

def ensure_font():
    if os.path.exists(FONT_PATH) and os.path.getsize(FONT_PATH) > 10000:
        return True
    try:
        r = requests.get(FONT_URL, timeout=20)
        if r.status_code == 200:
            with open(FONT_PATH, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        return False
    return False

font_ok = ensure_font()

# helpers for Arabic shaping
def shape_text(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception:
        # fallback: return original
        return text

# helper to check if any arabic chars
def has_arabic(s):
    return any("\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F" for ch in s)

# suggestions list (50) -- for "quick fill"
SUGGESTIONS = [
    "مهندس برمجيات مبتدئ", "مطور ويب (Frontend)", "مطور ويب (Fullstack)",
    "مطور بايثون", "متدرب في تكنولوجيا المعلومات", "مصمم جرافيك إبداعي",
    "متخصص تسويق رقمي", "مدير مشاريع صغير", "محلل بيانات مبتدئ",
    "مهندس شبكات", "مطور تطبيقات أندرويد", "مطور iOS مبتدئ",
    "مصمم واجهات المستخدم UI/UX", "كاتب محتوى رقمي", "مترجم لغات",
    "محاسب مبتدئ", "موظف خدمة زبائن محترف", "بائع ميداني",
    "مصمم شعارات", "فريلانسر في تطوير الويب", "مساعد إداري",
    "مهندس إلكترونيات", "مختص صيانة حواسيب", "مدرب لغات",
    "باحث بازار", "مصور فوتوغرافي", "فيديوغرافر", "مشرف متجر الكتروني",
    "مندوب مبيعات", "مساعد تسويق", "مختص SEO/SEM", "مصمم موشن جرافيك",
    "مطور ألعاب مبتدئ", "مختص أمن معلومات", "مراقب جودة برمجيات",
    "أخصائي موارد بشرية", "محلل نظم", "مهندس تعلم آلي مبتدئ",
    "مزارع تجريبي", "مهندس صوت", "منسق فعاليات", "كاتِب سيناريو",
    "مستشار صغير أعمال", "مطور روبوتات", "فنان رقمي", "مساعد قانوني",
    "مترجم تقني", "مشرف إنتاج"
]

# UI: custom CSS for background and "chat style"
BG_URL = "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1400&q=80"
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('{BG_URL}');
        background-size: cover;
        background-attachment: fixed;
    }}
    .card {{
        background: rgba(255,255,255,0.95);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }}
    .chat-bubble-me {{
        background: #dcf8c6;
        padding: 12px 16px;
        border-radius: 18px;
        display:inline-block;
        max-width: 85%;
        margin-bottom:6px;
        font-size:16px;
    }}
    .chat-bubble-bot {{
        background: #e8f0ff;
        padding: 12px 16px;
        border-radius: 18px;
        display:inline-block;
        max-width: 85%;
        margin-bottom:6px;
        font-size:16px;
    }}
    .muted {{ color: #666; font-size:14px; }}
    </style>
    """, unsafe_allow_html=True)

st.title("📄 CV Builder — أنشئ سيفيك بثواني")
st.write("بسيط، جميل، يدعم العربي ويخرج PDF جاهز للطباعة. اختر اقتراح من القائمة أو اكتب وصِفك الخاص.")

with st.container():
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("معلومات أساسية")
        name = st.text_input("الاسم الكامل", value="أسمك هنا")
        title = st.text_input("المسمى الوظيفي", value="مطور / مصمم ...")
        contact = st.text_input("بريد إلكتروني أو هاتف", value="example@mail.com")
        location = st.text_input("المدينة / البلد", value="الجزائر")
        photo = st.file_uploader("صورة شخصية (اختياري)", type=["png","jpg","jpeg"])

        st.subheader("نبذة قصيرة")
        # suggestions selector
        suggested = st.selectbox("اختر من الاقتراحات الجاهزة (أو اكتب)", ["— اختر اقتراح —"] + SUGGESTIONS)
        if suggested and suggested != "— اختر اقتراح —":
            default_summary = f"{suggested} — أبحث عن فرصة لتطبيق مهاراتي وتعلم المزيد."
        else:
            default_summary = "اكتب نبذة قصيرة عن نفسك هنا..."
        summary = st.text_area("النبذة (ملخص قصير)", value=default_summary, height=120)

    with col2:
        st.subheader("الخبرات والتعليم")
        st.write("أضف كل خبرة في سطر جديد، استخدم ( - ) للفصل بين العنوان والوصف.")
        experiences = st.text_area("الخبرات (كل سطر: منصب | شركة | الفترة | وصف قصير)", 
                                   value="مطور ويب | شركة مثال | 2022-الآن | تطوير واجهات المستخدم",
                                   height=220)

        st.write("التعليم (سطر لكل سجل)")
        education = st.text_area("التعليم", value="بكالوريوس علوم حاسوب | جامعة ... | 2020", height=120)

        st.write("المهارات (افصل بفاصلة)")
        skills = st.text_input("المهارات", value="Python, HTML, CSS, JavaScript")

# extra
st.markdown("---")
st.subheader("تفاصيل إضافية (اختياري)")
languages = st.text_input("اللغات (مثال: العربية - متقن، الإنجليزية - جيد)", value="العربية - متقن, الإنجليزية - جيد")
hobbies = st.text_input("الهوايات / الاهتمامات", value="تصميم، موسيقى، قراءة")
links = st.text_input("روابط مهمة (LinkedIn, GitHub)", value="https://github.com/username")

# generate PDF
def build_pdf_bytes(data: dict) -> bytes:
    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # register font
    used_font = None
    try:
        if font_ok:
            pdf.add_font("NotoArabic", "", FONT_PATH, uni=True)
            used_font = "NotoArabic"
        else:
            # try default DejaVu (if available) else fallback to Arial (not Arabic-safe)
            pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
            used_font = "DejaVu"
    except Exception:
        used_font = None

    # Header - name
    if used_font:
        pdf.set_font(used_font, size=20)
    else:
        pdf.set_font("Arial", size=20)
    # Name may be Arabic -> shape if needed
    name_print = shape_text(data["name"]) if has_arabic(data["name"]) else data["name"]
    pdf.cell(0, 10, txt=name_print, ln=True)

    # title & contact
    if used_font:
        pdf.set_font(used_font, size=12)
    else:
        pdf.set_font("Arial", size=12)
    title_print = shape_text(data["title"]) if has_arabic(data["title"]) else data["title"]
    contact_print = shape_text(data["contact"]) if has_arabic(data["contact"]) else data["contact"]
    location_print = shape_text(data["location"]) if has_arabic(data["location"]) else data["location"]

    pdf.multi_cell(0, 6, f"{title_print} · {contact_print} · {location_print}")
    pdf.ln(4)

    # Summary section
    if used_font:
        pdf.set_font(used_font, size=12)
    else:
        pdf.set_font("Arial", size=12)
    pdf.cell(0, 6, txt=shape_text("النبذة:") if has_arabic("النبذة:") else "Summary:", ln=True)
    summary_print = shape_text(data["summary"]) if has_arabic(data["summary"]) else data["summary"]
    pdf.multi_cell(0, 6, summary_print)
    pdf.ln(6)

    # Experiences
    pdf.set_font(used_font if used_font else "Arial", size=12)
    pdf.cell(0, 6, txt=shape_text("الخبرة العملية:") if has_arabic("الخبرة العملية:") else "Experience:", ln=True)
    for line in data["experiences"].splitlines():
        line = line.strip()
        if not line:
            continue
        prefix = "- "
        text_line = prefix + line
        text_line = shape_text(text_line) if has_arabic(text_line) else text_line
        pdf.multi_cell(0, 6, text_line)
    pdf.ln(4)

    # Education
    pdf.cell(0, 6, txt=shape_text("التعليم:") if has_arabic("التعليم:") else "Education:", ln=True)
    for line in data["education"].splitlines():
        line = line.strip()
        if not line:
            continue
        line_print = shape_text(line) if has_arabic(line) else line
        pdf.multi_cell(0, 6, "- " + line_print)

    pdf.ln(4)
    # Skills
    pdf.cell(0, 6, txt=shape_text("المهارات:") if has_arabic("المهارات:") else "Skills:", ln=True)
    pdf.multi_cell(0, 6, shape_text(data["skills"]) if has_arabic(data["skills"]) else data["skills"])

    pdf.ln(6)
    pdf.cell(0, 6, txt=shape_text("معلومات إضافية:") if has_arabic("معلومات إضافية:") else "Extra:", ln=True)
    extras = f"Languages: {data['languages']} | Hobbies: {data['hobbies']} | Links: {data['links']}"
    extras_print = shape_text(extras) if has_arabic(extras) else extras
    pdf.multi_cell(0, 6, extras_print)

    # if an image buffer provided
    if data.get("photo_bytes"):
        try:
            # write image to temp file and place at top-right
            img = Image.open(io.BytesIO(data["photo_bytes"]))
            # save as temporary jpeg
            tmp_path = os.path.join(FONTS_DIR, "tmp_profile.jpg")
            img.convert("RGB").save(tmp_path, "JPEG")
            # Place image
            # set x near right margin
            pdf.image(tmp_path, x=150, y=10, w=40)
        except Exception:
            pass

    # produce bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="ignore") if isinstance(pdf.output(dest="S"), str) else pdf.output(dest="S")
    return pdf_bytes

# generate button area
st.markdown("---")
st.subheader("إنتاج السيفي (PDF)")
generate_click = st.button("✅ أنشئ السيفي و نزّل PDF الآن")

if generate_click:
    # prepare data
    photo_bytes = None
    if photo:
        try:
            photo_bytes = photo.read()
        except Exception:
            photo_bytes = None

    payload = {
        "name": name,
        "title": title,
        "contact": contact,
        "location": location,
        "summary": summary,
        "experiences": experiences,
        "education": education,
        "skills": skills,
        "languages": languages,
        "hobbies": hobbies,
        "links": links,
        "photo_bytes": photo_bytes
    }

    with st.spinner("⏳ يجري إنشاء PDF ..."):
        try:
            pdf_bytes = build_pdf_bytes(payload)
            st.success("تم إنشاء PDF بنجاح، حمّله من الزر التالي.")
            st.download_button("⬇️ حمل CV كـ PDF", data=pdf_bytes, file_name="cv.pdf", mime="application/pdf")
        except Exception as e:
            st.error("حصل خطأ أثناء إنشاء PDF. رسالة الخطأ:")
            st.exception(e)
            if not font_ok:
                st.warning("ملاحظة: التطبيق حاول تحميل خط عربي آليًا لكن فشل. حاول تشغيل التطبيق مع اتصال إنترنت أو قم يدوياً بوضع ملف خط TTF عربي داخل مجلد 'fonts/'.")
else:
    st.info("اضغط على زر 'أنشئ السيفي' لإنتاج ملف PDF جاهز.")
