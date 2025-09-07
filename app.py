import streamlit as st
from openai import OpenAI
import requests

# 🔑 جلب مفتاح API من secrets
api_key = st.secrets["OPENAI_API_KEY"]

# إنشاء كليان OpenAI
client = OpenAI(api_key=api_key)

# 🎨 إعدادات الواجهة
st.set_page_config(page_title="مولّد الصور بالذكاء الاصطناعي", page_icon="🎨", layout="centered")

# 🖼️ خلفية مخصصة عبر CSS
page_bg = """
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.block-container {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 🏠 نظام الصفحات
if "page" not in st.session_state:
    st.session_state.page = "home"

# ------------------- 🏠 الصفحة الرئيسية -------------------
if st.session_state.page == "home":
    st.markdown(
        """
        <div style="text-align:center; margin-top:50px;">
            <h1 style="color:#FF4B4B;">👋 مرحباً بك!</h1>
            <p style="font-size:18px; color:#333;">
                🎨 هذه الأداة تتيح لك توليد صور مذهلة بالذكاء الاصطناعي انطلاقاً من أي وصف تكتبه.
            </p>
            <p style="font-size:16px; color:#555;">
                اختر فكرة أو مشهداً، ودع الذكاء الاصطناعي يرسمه لك بجودة عالية 🤩
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🚀 ابدأ الآن"):
        st.session_state.page = "generator"
        st.experimental_rerun()

# ------------------- 🎨 صفحة التوليد -------------------
elif st.session_state.page == "generator":
    st.markdown(
        """
        <div style="text-align:center;">
            <h1 style="color:#FF4B4B;">🎨 مولّد الصور بالذكاء الاصطناعي</h1>
            <p style="font-size:18px; color:#333;">
                ✍️ أدخل وصفاً للصورة، وسيقوم الذكاء الاصطناعي برسمها لك.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 📝 إدخال النص
    prompt = st.text_area("🖋️ أدخل وصف الصورة هنا:")

    # 📐 اختيار حجم الصورة
    st.markdown("### 📏 اختر حجم الصورة:")
    size = st.radio(
        "",
        ("256x256", "512x512", "1024x1024"),
        index=1,
        horizontal=True
    )

    # 🚀 زر التوليد
    if st.button("✨ توليد الصورة"):
        if not prompt.strip():
            st.error("⚠️ يرجى كتابة وصف قبل التوليد.")
        else:
            with st.spinner("⏳ جاري توليد الصورة..."):
                try:
                    # توليد الصورة
                    image = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt,
                        size=size
                    )
                    image_url = image.data[0].url

                    # ✅ عرض الصورة
                    st.image(image_url, caption="🌟 النتيجة", use_column_width=True)

                    # ⬇️ زر تحميل
                    img_data = requests.get(image_url).content
                    st.download_button(
                        label="⬇️ تحميل الصورة",
                        data=img_data,
                        file_name="generated_image.png",
                        mime="image/png"
                    )

                    st.success("🎉 تم إنشاء الصورة بنجاح!")
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")

    # 🔙 زر الرجوع
    if st.button("🔙 رجوع إلى الصفحة الرئيسية"):
        st.session_state.page = "home"
        st.experimental_rerun()
