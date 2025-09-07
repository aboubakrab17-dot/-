import streamlit as st
from openai import OpenAI

# إعداد صفحة التطبيق
st.set_page_config(
    page_title="مولد الصور بالذكاء الاصطناعي",
    page_icon="🎨",
    layout="centered"
)

# تهيئة API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# خلفية ترحيب
if "started" not in st.session_state:
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h1 style='text-align: center; color: red;'>مرحباً بك 🚀</h1>
        <p style='text-align: center; font-size:18px;'>
        هذه الأداة تتيح لك توليد صور مذهلة 🎨 بالذكاء الاصطناعي انطلاقاً من أي وصف تكتبه.<br>
        اختر فكرة أو مشهداً، ودع الذكاء الاصطناعي يرسمه لك بجودة عالية 😍
        </p>
        """,
        unsafe_allow_html=True
    )

    if st.button("ابدأ الآن 🚀", use_container_width=True):
        st.session_state.started = True
        st.rerun()

# الواجهة الرئيسية بعد الضغط على "ابدأ الآن"
else:
    st.title("🎨 مولد الصور بالذكاء الاصطناعي")
    st.write("✍️ اكتب وصفاً للصورة التي تريد إنشائها:")

    prompt = st.text_area("الوصف:")

    if st.button("إنشاء الصورة"):
        if prompt.strip() == "":
            st.warning("⚠️ من فضلك اكتب وصفاً أولاً.")
        else:
            with st.spinner("⏳ جاري توليد الصورة..."):
                try:
                    response = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt,
                        size="512x512"
                    )
                    image_url = response.data[0].url
                    st.image(image_url, caption="✅ هذه هي الصورة التي تم إنشاؤها")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
