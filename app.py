import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# 🔑 التوكن تاعك (حطو في secrets في streamlit)
HF_TOKEN = st.secrets["HF_TOKEN"]

# ✅ رابط صحيح للموديل
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# إعدادات الصفحة
st.set_page_config(page_title="تجريب التوكن 🎨", page_icon="✨")
st.title("🚀 تجربة توليد صورة بالتوكن")

# إدخال الوصف
prompt = st.text_input("✍️ اكتب وصف الصورة:", "رجل يجري على الشاطئ")

# زر التجربة
if st.button("تجربة التوكن"):
    with st.spinner("⏳ جاري التوليد..."):
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

        if response.status_code == 200:
            try:
                image = Image.open(BytesIO(response.content))
                st.image(image, caption="✅ النتيجة")
            except Exception:
                st.error("⚠️ النتيجة مشي صورة. ممكن الرد فيه رسالة نصية مش صورة.")
        else:
            st.error(f"❌ خطأ: {response.status_code}\n\n{response.text}")
