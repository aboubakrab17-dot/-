import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import os

# إعداد الصفحة
st.set_page_config(page_title="مولد السيرة الذاتية", page_icon="📄", layout="centered")
st.title("📄 مولد السيرة الذاتية (CV)")

st.write("✅ املأ معلوماتك أدناه واضغط على زر إنشاء السيرة الذاتية لتحميلها PDF.")

# ✅ مدخلات المستخدم
name = st.text_input("👤 الاسم الكامل:")
job_title = st.text_input("💼 المسمى الوظيفي:")
email = st.text_input("📧 البريد الإلكتروني:")
phone = st.text_input("📱 رقم الهاتف:")
address = st.text_input("📍 العنوان:")

st.subheader("🎯 المهارات")
skills = st.text_area("أدخل مهاراتك (افصلها بفواصل)", "Python, HTML, CSS, Communication")

st.subheader("🏫 التعليم")
education = st.text_area("أدخل التعليم (مثال: جامعة كذا - تخصص كذا - سنة كذا)")

st.subheader("💼 الخبرات")
experience = st.text_area("أدخل خبراتك العملية (مثال: شركة كذا - منصب كذا - من سنة إلى سنة)")

# ✅ زر إنشاء CV
if st.button("🚀 إنشاء السيرة الذاتية"):
    if name.strip() == "":
        st.error("⚠️ يجب إدخال على الأقل الاسم الكامل.")
    else:
        # ملف مؤقت
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        width, height = A4

        # العنوان
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, name)
        c.setFont("Helvetica", 14)
        c.drawString(50, height - 80, job_title)

        # معلومات الاتصال
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 120, f"📧 البريد: {email}")
        c.drawString(50, height - 140, f"📱 الهاتف: {phone}")
        c.drawString(50, height - 160, f"📍 العنوان: {address}")

        # قسم المهارات
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 200, "🎯 المهارات:")
        c.setFont("Helvetica", 12)
        for i, skill in enumerate(skills.split(",")):
            c.drawString(70, height - 220 - i * 20, f"- {skill.strip()}")

        # قسم التعليم
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 300, "🏫 التعليم:")
        c.setFont("Helvetica", 12)
        for i, edu in enumerate(education.split("\n")):
            c.drawString(70, height - 320 - i * 20, f"- {edu.strip()}")

        # قسم الخبرات
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 420, "💼 الخبرات:")
        c.setFont("Helvetica", 12)
        for i, exp in enumerate(experience.split("\n")):
            c.drawString(70, height - 440 - i * 20, f"- {exp.strip()}")

        c.save()

        # عرض رابط التحميل
        with open(temp_file.name, "rb") as f:
            st.download_button(
                label="⬇️ تحميل السيرة الذاتية PDF",
                data=f,
                file_name=f"CV_{name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

        # حذف الملف المؤقت
        os.unlink(temp_file.name)
