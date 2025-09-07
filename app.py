import streamlit as st
import openai
import os
import requests

# استدعاء مفتاح OpenAI من المتغيرات البيئية
openai.api_key = os.getenv("OPENAI_API_KEY")

# إعدادات الصفحة
st.set_page_config(
    page_title="مولد الصور بالذكاء الاصطناعي",
    page_icon="🎨",
    layout="centered"
)

# CSS مخصص للخلفية والأزرار
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f9f9f9, #e3f2fd);
        font-family: "Tajawal", sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .big-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #ff5722;
    }
    .subtitle {
        font-size: 18px;
        text-align: center;
        color: #444;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# الصفحة الرئيسية
st.markdown('<p class="big-title">🚀 مرحباً بك!</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">هذه الأداة تتيح لك توليد صور مذهلة بالذكاء الاصطناعي انطلاقاً من أي وصف تكتبه. 🖼️</p>',
    unsafe_allow_html=True
)

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    if st.button("ابدأ الآن 🚀"):
        st.session_state.page = "generator"
        st.experimental_rerun()

elif st.session_state.page == "generator":
    # خلفية جديدة للصفحة الثانية
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("✍️ اكتب وصفك للصورة")
    user_prompt = st.text_area("أدخل وصفك هنا:", placeholder="مثال: قطة تجري وسط حقل من الزهور 🌸")

    if st.button("إنشاء الصورة 🎨"):
        if not user_prompt.strip():
            st.error("⚠️ من فضلك أدخل وصفاً أولاً")
        else:
            try:
                with st.spinner("⏳ جاري إنشاء الصورة..."):
                    response = openai.images.generate(
                        model="gpt-image-1",
                        prompt=user_prompt,
                        size="512x512"
                    )
                    image_url = response.data[0].url
                    st.image(image_url, caption="✅ تم إنشاء الصورة بنجاح")

                    # جلب الصورة للتحميل
                    img_data = requests.get(image_url).content
                    st.download_button(
                        label="⬇️ تحميل الصورة",
                        data=img_data,
                        file_name="generated_image.png",
                        mime="image/png"
                    )
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
