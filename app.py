import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

# 🔹 تسجيل خط عربي (تقدر تبدلو بخط آخر عندك)
pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))

# 📄 إعداد الصفحة
st.set_page_config(page_title="منشئ السيرة الذاتية", page_icon="📄", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>📄 منشئ السيرة الذاتية</h1>
    <p style='text-align: center; font-size:18px; color: #117A65;'>
    أدخل معلوماتك خطوة بخطوة، ثم أنشئ سيرتك الذاتية الاحترافية بنقرة واحدة 🚀
    </p>
    """,
    unsafe_allow_html=True
)

# 📌 المعلومات الشخصية
st.header("🔹 المعلومات الشخصية")
name = st.text_input("✍️ الاسم الكامل")
email = st.text_input("📧 البريد الإلكتروني")
phone = st.text_input("📞 رقم الهاتف")
address = st.text_area("📍 العنوان")

# 🎓 التعليم
st.header("🔹 التعليم")
degree = st.text_input("🎓 الشهادة")
university = st.text_input("🏫 الجامعة")
grad_year = st.text_input("📅 سنة التخرج")

# 💼 الخبرات
st.header("🔹 الخبرات العملية")
job_title = st.text_input("💼 المسمى الوظيفي")
company = st.text_input("🏢 الشركة")
work_years = st.text_input("📆 المدة (من - إلى)")

# 🛠 المهارات
st.header("🔹 المهارات")
skills = st.text_area("⚡ اكتب مهاراتك (افصل بينها بفاصلة ,)")

# 📸 صورة شخصية
st.header("🔹 صورة شخصية")
photo = st.file_uploader("⬆️ ارفع صورتك (اختياري)", type=["jpg", "png", "jpeg"])


# ✅ إنشاء PDF
if st.button("🚀 إنشاء السيرة الذاتية"):
    if not name.strip():
        st.error("⚠️ يرجى إدخال على الأقل الاسم!")
    else:
        pdf_file = "CV.pdf"
        c = canvas.Canvas(pdf_file, pagesize=A4)
        c.setFont("Arabic", 14)

        width, height = A4
        y = height - 2 * cm

        # 📸 إضافة الصورة إذا موجودة
        if photo:
            img_path = "temp_photo.png"
            with open(img_path, "wb") as f:
                f.write(photo.read())
            c.drawImage(img_path, width - 5*cm, y - 2*cm, 4*cm, 4*cm)
            y -= 3 * cm

        # 📝 كتابة البيانات
        c.drawString(2*cm, y, f"الاسم: {name}"); y -= 1*cm
        c.drawString(2*cm, y, f"البريد الإلكتروني: {email}"); y -= 1*cm
        c.drawString(2*cm, y, f"الهاتف: {phone}"); y -= 1*cm
        c.drawString(2*cm, y, f"العنوان: {address}"); y -= 1.5*cm

        c.drawString(2*cm, y, "التعليم:"); y -= 1*cm
        c.drawString(3*cm, y, f"{degree} - {university} ({grad_year})"); y -= 1.5*cm

        c.drawString(2*cm, y, "الخبرات:"); y -= 1*cm
        c.drawString(3*cm, y, f"{job_title} في {company} - {work_years}"); y -= 1.5*cm

        c.drawString(2*cm, y, "المهارات:"); y -= 1*cm
        for skill in skills.split(","):
            c.drawString(3*cm, y, f"- {skill.strip()}")
            y -= 0.8*cm

        c.save()

        # 📥 تحميل الملف
        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ تحميل السيرة الذاتية", f, file_name="CV.pdf")

        st.success("✅ تم إنشاء السيرة الذاتية بنجاح!")

        # 🧹 حذف الصورة المؤقتة
        if photo:
            os.remove(img_path)
