import streamlit as st
import requests
from PIL import Image
from io import BytesIO

🔑 حط التوكن تاعك هنا

HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="تجريب التوكن 🎨", page_icon="✨")
st.title("🚀 تجربة توليد صورة بالتوكن")

prompt = st.text_input("✍️ اكتب وصف الصورة:", "A cat playing guitar")

if st.button("تجربة التوكن"):
with st.spinner("⏳ جاري التوليد..."):
response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
if response.status_code == 200:
image = Image.open(BytesIO(response.content))
st.image(image, caption="✅ النتيجة")
else:
st.error(f"❌ خطأ: {response.status_code} - {response.text}")

