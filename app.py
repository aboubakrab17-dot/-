import streamlit as st
import random

# 🎨 إعدادات الصفحة
st.set_page_config(page_title="منصتي التعليمية 🦉", page_icon="🦉", layout="centered")

# 🌈 CSS للتصميم
page_bg = """
<style>
.stApp {
    background: linear-gradient(135deg, #6EE7B7, #3B82F6); /* أخضر + أزرق */
    color: white;
    font-family: "Cairo", sans-serif;
}
h1, h2, h3, label {
    color: #fff !important;
    text-align: center;
}
.stButton button {
    background-color: #22c55e;
    color: white;
    border-radius: 12px;
    font-weight: bold;
    padding: 12px 25px;
    font-size: 18px;
    transition: 0.3s;
}
.stButton button:hover {
    background-color: #16a34a;
}
.stRadio label {
    color: #000 !important;
    font-size: 20px;
    background: #fff;
    padding: 8px 12px;
    border-radius: 10px;
    margin: 5px;
    display: block;
}
.score-box {
    background-color: rgba(255,255,255,0.2);
    padding: 12px;
    border-radius: 15px;
    margin: 10px 0;
    text-align: center;
    font-size: 18px;
}
.heart {
    font-size: 26px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 🧠 بيانات الدروس
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

# 🎯 حالة المستخدم
if "score" not in st.session_state:
    st.session_state.score = 0
if "step" not in st.session_state:
    st.session_state.step = 0
if "lang" not in st.session_state:
    st.session_state.lang = None
if "level" not in st.session_state:
    st.session_state.level = 1
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "hearts" not in st.session_state:
    st.session_state.hearts = 3  # ❤️ عدد المحاولات

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

    # عرض المستوى و XP + ❤️ قلوب
    hearts_display = "❤️" * st.session_state.hearts + "🤍" * (3 - st.session_state.hearts)
    st.markdown(f"<div class='score-box'>📊 المستوى: {st.session_state.level} | ⭐ XP: {st.session_state.xp} | <span class='heart'>{hearts_display}</span></div>", unsafe_allow_html=True)

    if st.session_state.step < total_questions and st.session_state.hearts > 0:
        q = questions[st.session_state.step]
        st.header(f"📘 السؤال {st.session_state.step + 1} من {total_questions}")
        st.subheader(q["question"])
        choice = st.radio("اختر الإجابة:", q["options"], key=f"q_{st.session_state.step}")

        if st.button("تحقق ✅"):
            if choice == q["answer"]:
                st.success("إجابة صحيحة 🎉 +10 XP")
                st.session_state.score += 1
                st.session_state.xp += 10
            else:
                st.error(f"إجابة خاطئة ❌، الصحيح هو: {q['answer']}")
                st.session_state.hearts -= 1
            st.session_state.step += 1
            st.rerun()
    else:
        st.title("🏆 النتيجة النهائية")
        st.success(f"لقد أنهيت الاختبار! نتيجتك: {st.session_state.score}/{total_questions} 🎯")

        if st.session_state.hearts == 0:
            st.error("💔 انتهت المحاولات! حاول مرة أخرى")

        # ترقية المستوى
        if st.session_state.score == total_questions:
            st.session_state.level += 1
            st.success(f"🎉 مبروك! انتقلت إلى المستوى {st.session_state.level} 🆙")

        if st.button("🔄 إعادة المحاولة"):
            st.session_state.score = 0
            st.session_state.step = 0
            st.session_state.lang = None
            st.session_state.hearts = 3
            st.rerun()
