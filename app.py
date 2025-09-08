import streamlit as st
import random

# إعداد الصفحة
st.set_page_config(page_title="منصة تعليمية مثل Duolingo", page_icon="🦉", layout="centered")

# 🎨 CSS للتصميم
page_bg = """
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
    font-family: "Cairo", sans-serif;
}
h1, h2, h3, label {
    color: #fff !important;
    text-align: center;
}
.stButton button {
    background-color: #00c6ff;
    color: white;
    border-radius: 12px;
    font-weight: bold;
    padding: 10px 20px;
    transition: 0.3s;
}
.stButton button:hover {
    background-color: #0096c7;
}
.stRadio label {
    color: #fff !important;
    font-size: 18px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 🧠 بيانات الدروس (الإنجليزية والفرنسية)
lessons = {
    "English": [
        {"question": "اختر الترجمة الصحيحة: قطة", "options": ["Cat", "Dog", "Car"], "answer": "Cat"},
        {"question": "اختر الترجمة الصحيحة: كتاب", "options": ["Book", "Table", "Chair"], "answer": "Book"},
        {"question": "اختر الترجمة الصحيحة: سلام", "options": ["Peace", "War", "Love"], "answer": "Peace"},
    ],
    "Français": [
        {"question": "اختر الترجمة الصحيحة: Chat", "options": ["قطة", "كلب", "كتاب"], "answer": "قطة"},
        {"question": "اختر الترجمة الصحيحة: Maison", "options": ["منزل", "سيارة", "طاولة"], "answer": "منزل"},
        {"question": "اختر الترجمة الصحيحة: Amour", "options": ["حب", "حرب", "سلام"], "answer": "حب"},
    ]
}

# 🎯 حفظ الحالة
if "score" not in st.session_state:
    st.session_state.score = 0
if "step" not in st.session_state:
    st.session_state.step = 0
if "lang" not in st.session_state:
    st.session_state.lang = None

# 🏁 اختيار اللغة
if st.session_state.lang is None:
    st.title("🦉 مرحبا بك في منصتك التعليمية")
    st.subheader("اختر اللغة التي تريد تعلمها")
    lang_choice = st.radio("🌍 اختر لغة:", ["English", "Français"])
    if st.button("ابدأ التعلم 🚀"):
        st.session_state.lang = lang_choice
        st.rerun()

# 📖 عرض الأسئلة + شريط التقدم
else:
    lang = st.session_state.lang
    questions = lessons[lang]
    total_questions = len(questions)

    # شريط التقدم
    progress = st.session_state.step / total_questions
    st.progress(progress)

    if st.session_state.step < total_questions:
        q = questions[st.session_state.step]
        st.header(f"📘 السؤال {st.session_state.step + 1} من {total_questions}")
        st.subheader(q["question"])
        choice = st.radio("اختر الإجابة:", q["options"], key=f"q_{st.session_state.step}")

        if st.button("تحقق ✅"):
            if choice == q["answer"]:
                st.success("إجابة صحيحة 🎉")
                st.session_state.score += 1
            else:
                st.error(f"إجابة خاطئة ❌، الصحيح هو: {q['answer']}")
            st.session_state.step += 1
            st.rerun()
    else:
        st.title("🏆 النتيجة النهائية")
        st.success(f"لقد أنهيت الاختبار! نتيجتك: {st.session_state.score}/{total_questions} 🎯")
        if st.button("🔄 إعادة المحاولة"):
            st.session_state.score = 0
            st.session_state.step = 0
            st.session_state.lang = None
            st.rerun()
