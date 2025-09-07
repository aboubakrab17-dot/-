import streamlit as st
import requests
from PIL import Image
from io import BytesIO



HF_TOKEN = "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"

رابط الموديل (تقدر تبدلو بموديل آخر كي تحب)

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

إعدادات الصفحة

st.set_page_config(page_title="تجريب التوكن 🎨", page_icon="✨")
st.title("🚀 تجربة توليد صورة بالتوكن")

إدخال الوصف

prompt = st.text_input("✍️ اكتب وصف الصورة:", "A cat playing guitar")

زر التجربة

if st.button("تجربة التوكن"):
with st.spinner("⏳ جاري التوليد..."):
response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

if response.status_code == 200:  
        try:  
            image = Image.open(BytesIO(response.content))  
            st.image(image, caption="✅ النتيجة")  
        except Exception:  
            st.error("⚠️ استقبلت رسبونس مشي صورة. ممكن التوكن محدود أو الموديل مشي مفعّل.")  
    else:  
        st.error(f"❌ خطأ: {response.status_code}\n\n{response.text}")

