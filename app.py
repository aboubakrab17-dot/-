import streamlit as st
import openai
import base64
import requests

# 📌 مفتاح API من secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🎨 CSS الخلفية + ستايل النصوص والأزرار
page_bg = """
<style>
body {
  background-image: url("https://images.unsplash.com/photo-1526948128573-703ee1aeb6fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80");
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  color: #ffffff;
  font-family: 'Cairo', sans-serif;
}

.block-container {
  background-color: rgba(0, 0, 0, 0.75);
  padding: 2rem;
  border-radius: 15px;
}

h1, h2, h3, label, p {
  color: #f9f9f9 !important;
  font-weight: bold;
}

.stButton button {
  background: linear-gradient(135deg, #ff7e5f, #feb47b);
  color: white !important;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 12px;
  font-size: 18px;
  font-weight: bold;
  transition: 0.3s;
}

.stButton button:hover {
  background: linear-gradient(135deg, #ff512f, #dd2476);
  transform: scale(1.05);
}

a {
  text-decoration: none;
  font-size: 18px;
  font-weight: bold;
  color: #00ffcc !important;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 🚀 إعداد الصفحة
st.set_page_config(page_title="مولد الصور بالذكاء الاصطناعي", page_icon="🎨", layout="centered")

# 🖼️ العنوان
st.title("🎨 مولد الصور بالذكاء الاصطناعي ✨")
st.write("اكتب وصفاً للصورة لي حاب يترسم، وخلي الذكاء الاصطناعي يبدعلك 👇")

# 📌 إدخال النص
prompt = st.text_area("✍️ اكتب وصف الصورة:", "")

# 📐 اختيار حجم الصورة
size = st.radio("📏 اختر حجم الصورة:", ("256x256", "512x512", "1024x1024"), index=1)

# 🎨 زر توليد الصورة
if st.button("🚀 إنشاء الصورة"):
    if not prompt.strip():
        st.error("⚠️ من فضلك اكتب وصف قبل التوليد.")
    else:
        try:
            with st.spinner("⏳ جاري توليد الصورة..."):
                response = openai.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size
                )
                image_url = response.data[0].url

                # 📸 عرض الصورة
                st.image(image_url, caption="✅ النتيجة", use_column_width=True)

                # 📥 زر تحميل الصورة
                img_data = requests.get(image_url).content
                b64 = base64.b64encode(img_data).decode()
                href = f'<a href="data:file/png;base64,{b64}" download="generated.png">📥 تحميل الصورة</a>'
                st.markdown(href, unsafe_allow_html=True)

                st.success("🎉 تم إنشاء الصورة بنجاح!")
        except Exception as e:
            st.error(f"❌ خطأ: {e}")
