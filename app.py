import streamlit as st
import openai

# 🔑 المفتاح تاع API (مخبيش المسافات باش يخدم صح)
API_KEY = "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"
openai.api_key = API_KEY

# ⚙️ إعدادات الصفحة
st.set_page_config(page_title="مولد الصور بالذكاء الاصطناعي", page_icon="🎨", layout="centered")

# 🖼️ العنوان
st.title("🎨 مولد الصور بالذكاء الاصطناعي")
st.write("اكتب وصف للصورة لي تحبها وخلي الذكاء الاصطناعي يرسمهالك 👇")

# ✍️ إدخال النص
prompt = st.text_area("📝 اكتب وصف الصورة:", "")

# 📐 اختيار حجم الصورة
size = st.radio(
    "📐 اختر حجم الصورة:",
    ("256x256", "512x512", "1024x1024"),
    index=1
)

# 🚀 زر التوليد
if st.button("🚀 توليد الصورة"):
    if not prompt.strip():
        st.error("⚠️ من فضلك اكتب وصف الصورة قبل التوليد.")
    else:
        try:
            with st.spinner("⏳ جاري توليد الصورة..."):
                response = openai.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size
                )
                image_url = response.data[0].url
                st.image(image_url, caption="✅ النتيجة", use_column_width=True)
                st.success("🎉 تمت العملية بنجاح!")
        except Exception as e:
            st.error(f"❌ خطأ: {e}")
