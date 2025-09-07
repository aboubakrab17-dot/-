import os
import requests
import streamlit as st

# نجيبو الـ Token من Secrets
API_TOKEN = os.getenv("API_TOKEN")
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# إعدادات الصفحة
st.set_page_config(page_title="🎨 مولد الصور", page_icon="🖼️", layout="centered")

# 🌌 خلفية ثابتة
page_bg = """
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-attachment: fixed;
    color: white;
    text-align: center;
}
h1, h2, h3, h4 {
    color: #FFD700;
}
.stButton>button {
    font-size: 18px;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #ff9800;
    color: white;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 🖼️ العنوان
st.title("🎨 مولد الصور بالذكاء الاصطناعي")
st.subheader("✨ اكتب وصف بسيط، وشوف الذكاء الاصطناعي يصنعلك صورة مذهلة ✨")

# 📝 إدخال وصف الصورة
prompt = st.text_area("✍️ اكتب وصف الصورة هنا:")

# 📐 اختيار الحجم
size = st.radio("📐 اختر حجم الصورة:", ["256x256", "512x512", "1024x1024"], index=1)

# 🚀 زر توليد
if st.button("🚀 توليد الصورة"):
    if not prompt.strip():
        st.warning("⚠️ لازم تكتب وصف قبل ما تولّد الصورة.")
    else:
        with st.spinner("⏳ جاري توليد الصورة... استنى لحظة"):
            response = requests.post(
                "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image",
                headers=headers,
                json={"inputs": prompt, "parameters": {"size": size}},
            )

            if response.status_code == 200:
                image_bytes = response.content
                st.image(image_bytes, caption="✅ صورتك الجاهزة", use_column_width=True)

                # زر تحميل بلون أزرق
                st.download_button(
                    "⬇️ تحميل الصورة",
                    data=image_bytes,
                    file_name="generated.png",
                    mime="image/png",
                )
                st.success("🎉 تمت العملية بنجاح! استمتع بالصورة 🌟")
            else:
                st.error(f"❌ خطأ أثناء التوليد: {response.text}")
