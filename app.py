import streamlit as st
import json
import random
import time

# إعدادات الصفحة
st.set_page_config(page_title="لعبة الأسئلة 🎮", layout="centered")

# CSS للخلفية + تنسيقات
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.postimg.cc/tRdJ6Qss/gaming-bg.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
[data-testid="stToolbar"] {visibility: hidden;}
.question-box {
    background: rgba(0,0,0,0.65);
    padding: 20px;
    border-radius: 15px;
    color: white;
    font-size: 20px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# تحميل الأسئلة
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# خزن الحالة
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = []

# إدخال اسم اللاعب
if not st.session_state.player_name:
    st.session_state.player_name = st.text_input("✨ ادخل اسمك للبدء")
    if st.session_state.player_name:
        st.success(f"مرحبا {st.session_state.player_name} 👋")
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()

# إظهار النقاط
st.markdown(f"### 🏅 نقاطك الحالية: {st.session_state.score}")

# جلب السؤال الحالي
if st.session_state.q_index < len(questions):
    q = questions[st.session_state.q_index]

    # مؤقت
    time_limit = 15
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = time_limit - elapsed

    if remaining <= 0:
        st.warning("⏰ انتهى الوقت! تخسر هذه الجولة...")
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        st.rerun()

    st.progress(remaining / time_limit)

    st.markdown(f"<div class='question-box'>❓ {q['question']}</div>", unsafe_allow_html=True)

    answer = st.radio("الاختيارات:", q["options"], index=None)

    if st.button("إجابة ✅"):
        if answer:
            if answer == q["answer"]:
                st.success("إجابة صحيحة 🎉👏")
                # نقاط حسب الصعوبة
                if q["difficulty"] == "easy":
                    st.session_state.score += 1
                elif q["difficulty"] == "medium":
                    st.session_state.score += 2
                elif q["difficulty"] == "hard":
                    st.session_state.score += 3
            else:
                st.error("إجابة خاطئة ❌")
            st.session_state.q_index += 1
            st.session_state.start_time = time.time()
            st.rerun()
else:
    st.balloons()
    st.success(f"🎮 انتهت اللعبة! مجموع نقاطك: {st.session_state.score}")

    # حفظ النتيجة في لوحة المتصدرين
    st.session_state.leaderboard.append(
        {"name": st.session_state.player_name, "score": st.session_state.score}
    )
    st.session_state.leaderboard = sorted(
        st.session_state.leaderboard, key=lambda x: x["score"], reverse=True
    )[:5]

    st.subheader("🏆 لوحة المتصدرين")
    for idx, player in enumerate(st.session_state.leaderboard, 1):
        st.write(f"{idx}. {player['name']} — {player['score']} نقطة")

    if st.button("🔄 إعادة اللعب"):
        st.session_state.score = 0
        st.session_state.q_index = 0
        st.session_state.start_time = time.time()
        st.rerun()
