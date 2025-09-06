import streamlit as st
import json
import random
import os

# تحميل الأسئلة من ملف JSON
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

# تحميل ترتيب النقاط
def load_leaderboard():
    if not os.path.exists("leaderboard.json"):
        return []
    with open("leaderboard.json", "r", encoding="utf-8") as f:
        return json.load(f)

# حفظ الترتيب
def save_leaderboard(leaderboard):
    with open("leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)

# بداية البرنامج
st.set_page_config(page_title="لعبة الألغاز 🧩", page_icon="🎮", layout="centered")

# خلفية CSS
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
.big-font {
    font-size:24px !important;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.title("🎮 لعبة الألغاز والأسئلة 🧩")
st.write("أجب عن الأسئلة واجمع النقاط! 🚀")

# تحميل البيانات
questions = load_questions()
leaderboard = load_leaderboard()

# تهيئة الجلسة
if "score" not in st.session_state:
    st.session_state.score = 0
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "username" not in st.session_state:
    st.session_state.username = ""

# إدخال اسم اللاعب
if st.session_state.username == "":
    st.session_state.username = st.text_input("أدخل اسمك لبدء اللعبة ✨")
    if st.session_state.username:
        st.session_state.score = 0
        st.session_state.q_index = 0
        st.experimental_rerun()

else:
    # عرض سؤال
    if st.session_state.q_index < len(questions):
        q = questions[st.session_state.q_index]
        st.markdown(f"### ❓ السؤال {st.session_state.q_index+1}: {q['question']}")

        # عرض الخيارات
        answer = st.radio("اختر الإجابة الصحيحة 👇", q["options"], key=st.session_state.q_index)

        if st.button("إرسال"):
            if answer == q["answer"]:
                st.success("✅ إجابة صحيحة! أحسنت 🎉")
                st.session_state.score += 1
            else:
                st.error(f"❌ إجابة خاطئة! الصح هو: {q['answer']}")

            st.session_state.q_index += 1
            st.experimental_rerun()

    else:
        st.subheader(f"انتهت اللعبة! 🏆 مجموع نقاطك: {st.session_state.score}")

        # حفظ النقاط في الترتيب
        leaderboard.append({"name": st.session_state.username, "score": st.session_state.score})
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]  # أفضل 10
        save_leaderboard(leaderboard)

        st.write("📊 أفضل اللاعبين:")
        for i, player in enumerate(leaderboard, start=1):
            st.write(f"{i}. {player['name']} — {player['score']} نقطة")

        if st.button("إعادة اللعب 🔄"):
            st.session_state.username = ""
            st.experimental_rerun()
