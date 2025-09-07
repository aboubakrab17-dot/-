import streamlit as st
import json
import random
import time

# ===== CSS للتصميم والخلفية =====
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: "Cairo", sans-serif;
    }
    .stButton>button {
        background-color: #ff9800;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #e68900;
    }
    .question-box {
        background-color: rgba(0,0,0,0.5);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ===== تحميل الأسئلة من ملف JSON =====
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ===== حالة الجلسة =====
if "score" not in st.session_state:
    st.session_state.score = 0
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "used_questions" not in st.session_state:
    st.session_state.used_questions = []
if "time_left" not in st.session_state:
    st.session_state.time_left = 20
if "music_on" not in st.session_state:
    st.session_state.music_on = True

# ===== زر تشغيل / إيقاف الموسيقى =====
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔊 إيقاف الصوت" if st.session_state.music_on else "🔈 تشغيل الصوت"):
        st.session_state.music_on = not st.session_state.music_on

# إدماج الموسيقى
if st.session_state.music_on:
    st.markdown(
        """
        <audio autoplay loop>
            <source src="background.mp3" type="audio/mpeg">
        </audio>
        """,
        unsafe_allow_html=True
    )

# ===== دالة لعرض سؤال جديد =====
def new_question():
    available = [q for q in questions if q["question"] not in st.session_state.used_questions]
    if not available:
        return None
    q = random.choice(available)
    st.session_state.used_questions.append(q["question"])
    return q

# ===== واجهة اللعبة =====
st.title("🎮 لعبة الألغاز التعليمية")

if st.button("▶️ بدء اللعبة"):
    st.session_state.score = 0
    st.session_state.q_index = 0
    st.session_state.used_questions = []
    st.session_state.time_left = 20

question = new_question()

if question:
    st.markdown(f"<div class='question-box'><h3>{question['question']}</h3></div>", unsafe_allow_html=True)

    # عرض الخيارات
    answer = st.radio("اختر الإجابة:", question["options"], key=st.session_state.q_index)

    if st.button("تحقق من الإجابة"):
        if answer == question["answer"]:
            st.success("✅ إجابة صحيحة! أحسنت 🎉")
            st.session_state.score += 1
        else:
            st.error(f"❌ خاطئة! الجواب الصحيح هو: {question['answer']}")

    # عرض العداد
    st.markdown(f"⏱️ الوقت المتبقي: **{st.session_state.time_left} ثانية**")

    # تقليل الوقت
    if st.session_state.time_left > 0:
        st.session_state.time_left -= 1
        time.sleep(1)
        st.experimental_rerun()
    else:
        st.warning("⌛ انتهى الوقت!")
else:
    st.success(f"🎉 انتهت اللعبة! مجموع نقاطك: {st.session_state.score}")
