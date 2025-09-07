import streamlit as st
import openai

# 🔑 حط API KEY تاعك من OpenAI هنا
openai.api_key = "YOUR_API_KEY"

# 🎨 إعدادات واجهة
st.set_page_config(page_title="مولد الصور بالذكاء الاصطناعي", page_icon="🖼️", layout="centered")

st.title("🖼️ مولد الصور بالذكاء الاصطناعي")
st.write("اكتب وصف للصورة لي حاب يخرجها الذكاء الاصطناعي ✨")

# 📝 إدخال النص
prompt = st.text_area("✍️ اكتب الوصف هنا:", height=100)

# ⚙️ اختيار الحجم
size = st.radio("📐 اختر حجم الصورة:", ["256x256", "512x512", "1024x1024"], index=1)

# ⚡ زر التوليد
if st.button("🚀 توليد الصورة"):
    if prompt.strip() == "":
        st.warning("⚠️ لازم تكتب وصف للصورة")
    else:
        with st.spinner("⏳ جاري توليد الصورة..."):
            try:
                response = openai.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size
                )
                image_url = response.data[0].url
                st.image(image_url, caption="✅ الصورة المولدة", use_column_width=True)
                st.success("🎉 توليد ناجح! تقدر تحفظ الصورة بالضغط يمين > حفظ الصورة")
            except Exception as e:
                st.error(f"🚨 خطأ: {str(e)}")
