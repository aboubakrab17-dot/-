import streamlit as st
import json
import random
import os

# تحميل الأسئلة
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

# تحميل الترتيب
def load_leaderboard():
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# حفظ الترتيب
def save_leaderboard(data):
    with open("leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# إعداد الصفحة
st.set_page_config(page_title="لعبة الألغاز والأسئلة 🎮", page_icon="🧩", layout="centered")

st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .main {
        background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# الحالة
if "questions" not in st.session_state:
    st.session_state.questions = load_questions()
    random.shuffle(st.session_state.questions)
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.username = ""

# إدخال اسم اللاعب
if st.session_state.username == "":
    st.title("🎮 لعبة الألغاز والأسئلة 🧩")
    st.subheader("أجب عن الأسئلة واجمع النقاط 🚀")
    name = st.text_input("أدخل اسمك لبدء اللعبة ✨")
    if st.button("ابدأ"):
        if name.strip() != "":
            st.session_state.username = name.strip()
            st.rerun()
        else:
            st.warning("⚠️ من فضلك أدخل اسمك للمتابعة")
else:
    # عرض السؤال الحالي
    if st.session_state.index < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.index]
        st.header(f"❓ السؤال {st.session_state.index + 1}: {q['question']}")

        options = q["options"]
        answer = st.radio("اختر الإجابة:", options, key=f"q{st.session_state.index}")

        if st.button("إرسال الإجابة"):
            if answer == q["answer"]:
                st.success("✅ إجابة صحيحة! أحسنت 👏")
                st.session_state.score += 1
            else:
                st.error(f"❌ خطأ! الجواب الصحيح هو: {q['answer']}")
            st.session_state.index += 1
            st.rerun()
    else:
        # عرض النتيجة النهائية
        st.success(f"🎉 انتهت اللعبة! نتيجتك: {st.session_state.score}/{len(st.session_state.questions)}")

        leaderboard = load_leaderboard()
        leaderboard.append({"name": st.session_state.username, "score": st.session_state.score})
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
        save_leaderboard(leaderboard)

        st.subheader("🏆 لوحة المتصدرين:")
        for i, entry in enumerate(leaderboard, start=1):
            st.write(f"{i}. {entry['name']} - {entry['score']} نقطة")

        if st.button("🔄 العب من جديد"):
            st.session_state.questions = load_questions()
            random.shuffle(st.session_state.questions)
            st.session_state.index = 0
            st.session_state.score = 0
            st.session_state.username = ""
            st.rerun()
