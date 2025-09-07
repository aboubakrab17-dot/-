import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import os

# نجيب التوكن من Secrets
HF_TOKEN = os.getenv("HF_TOKEN")

# نموذج توليد الصور
MODEL_ID = "runwayml/stable-diffusion-v1-5"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt, size):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image = image.resize(size)
        return image
    else:
        st.error(f"❌ خطأ: {response.status_code} - {response.text}")
        return None

# واجهة Streamlit
st.set_page_config(page_title="مولد الصور بالذكاء الاصطناعي", page_icon="✨", layout="centered")

st.markdown(
    "<h2 style='text-align: center;'>✨ اكتب وصف بسيط و شوف الذكاء الاصطناعي يصنعلك صورة ✨</h2>",
    unsafe_allow_html=True,
)

prompt = st.text_area("✍️ اكتب وصف الصورة هنا:", placeholder="مثال: رجل يجري على الشاطئ")

size = st.radio(
    "📐 اختر حجم الصورة",
    ["256x256", "512x512", "1024x1024"],
    index=1
)

sizes_map = {
    "256x256": (256, 256),
    "512x512": (512, 512),
    "1024x1024": (1024, 1024),
}

if st.button("🚀 توليد الصورة"):
    if prompt.strip() == "":
        st.warning("⚠️ لازم تكتب وصف باش نقدر نولد صورة.")
    else:
        with st.spinner("⏳ توليد الصورة جارٍ..."):
            result = generate_image(prompt, sizes_map[size])
            if result:
                st.image(result, caption="✅ صورتك الجاهزة", use_column_width=True)
