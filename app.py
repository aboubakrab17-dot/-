import streamlit as st
from fpdf import FPDF
import qrcode
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="مولد السيرة الذاتية", page_icon="📄", layout="centered")

# CSS للتصميم
page_bg = """
<style>
.stApp {
    background: linear-gradient(135deg, #74ABE2, #5563DE);
    color: white;
    font-family: "Cairo", sans-serif;
}
h1, h2, h3, label {
    color: #fff !important;
}
.stTextInput > div > div > input {
    background-color: #222;
    color: white;
    border-radius: 10px;
    padding: 10px;
}
.stTextArea textarea {
    background-color: #222;
    color: white;
    border-radius: 10px;
    padding: 10px;
}
.stButton button {
    background-color: #00c6ff;
    color: white;
    border-radius: 12px;
    font-weight: bold;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 📝 العنوان
st.title("📄 مولد السيرة الذاتية الاحترافي")

# 📌 مدخلات المستخدم
name = st.text_input("👤 الاسم الكامل")
job = st.text_input("💼 الوظيفة")
email = st.text_input("📧 البريد الإلكتروني")
phone = st.text_input("📱 رقم الهاتف")
address = st.text_input("📍 العنوان")
about = st.text_area("📝 نبذة عنك")
skills = st.text_area("⭐ المهارات (افصل بينهم بفواصل ,)")
experience = st.text_area("📂 الخبرات")
education = st.text_area("🎓 التعليم")

# 🎨 اختيار القالب
template = st.selectbox("🎨 اختر القالب", ["كلاسيكي", "مودرن", "مبسط"])

# 🖋️ اختيار الخط
font_choice = st.selectbox("✍️ اختر الخط", ["Arial", "Times", "Courier"])

# 📱 QR Code
generate_qr = st.checkbox("📱 إضافة QR Code بمعلوماتي")

# 🚀 زر إنشاء CV
if st.button("🚀 إنشاء السيرة الذاتية"):
    if not name.strip():
        st.error("⚠️ اكتب اسمك على الأقل!")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(font_choice, "B", 18)

        # خلفية خاصة بالقوالب
        if template == "كلاسيكي":
            pdf.set_fill_color(230, 230, 250)
            pdf.rect(0, 0, 210, 297, "F")
        elif template == "مودرن":
            pdf.set_fill_color(200, 230, 255)
            pdf.rect(0, 0, 210, 297, "F")
        elif template == "مبسط":
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(0, 0, 210, 297, "F")

        # 📝 المعلومات
        pdf.set_text_color(0, 51, 102)
        pdf.cell(200, 10, name, ln=True, align="C")
        pdf.set_font(font_choice, "", 12)
        pdf.cell(200, 10, job, ln=True, align="C")
        pdf.ln(10)

        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, f"📧 {email}\n📱 {phone}\n📍 {address}")
        pdf.ln(5)

        pdf.multi_cell(0, 10, f"📝 نبذة:\n{about}")
        pdf.ln(5)

        pdf.multi_cell(0, 10, f"⭐ المهارات:\n{skills}")
        pdf.ln(5)

        pdf.multi_cell(0, 10, f"📂 الخبرات:\n{experience}")
        pdf.ln(5)

        pdf.multi_cell(0, 10, f"🎓 التعليم:\n{education}")

        # 📱 إضافة QR Code
        if generate_qr:
            qr_data = f"Name: {name}\nJob: {job}\nEmail: {email}\nPhone: {phone}\nAddress: {address}"
            qr_img = qrcode.make(qr_data)
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            pdf.image(buf, x=160, y=10, w=40)

        # 📥 تحميل
        output = BytesIO()
        pdf.output(output, "F")
        st.success("✅ تم إنشاء CV بنجاح!")
        st.download_button("📥 تحميل السيرة الذاتية", data=output.getvalue(), file_name="CV.pdf", mime="application/pdf")
