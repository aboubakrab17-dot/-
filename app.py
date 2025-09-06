import streamlit as st
import json
import random
import time

# ---------------- تحميل الأسئلة ----------------
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ---------------- تهيئة الحالة ----------------
if "remaining_questions" not in st.session_state:
    st.session_state.remaining_questions = questions.copy()
    random.shuffle(st.session_state.remaining_questions)

if "score" not in st.session_state:
    st.session_state.score = 0

if "player" not in st.session_state:
    st.session_state.player = ""

# ---------------- إدخال اسم اللاعب ----------------
if not st.session_state.player:
    st.title("🎮 لعبة الأسئلة والألغاز ❓")
    st.session_state.player = st.text_input("ادخل اسمك للبدء ✨")
    if st.session_state.player:
        st.experimental_rerun()
    st.stop()

# ---------------- عرض اللعبة ----------------
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(f"مرحبًا {st.session_state.player} 👋")
st.subheader("أجب عن الأسئلة وحاول تجمع أكبر عدد من النقاط 🏆")

# ---------------- عرض سؤال ----------------
if st.session_state.remaining_questions:
    total = len(questions)
    current_index = total - len(st.session_state.remaining_questions) + 1
    st.progress(current_index / total)

    q = st.session_state.remaining_questions[0]
    st.markdown(f"### ❓ السؤال {current_index}: {q['question']}")

    # مؤقت
    time_limit = 20
    start_time = time.time()

    # الاختيارات
    answer = st.radio("اختر الإجابة:", q["options"])

    if st.button("تأكيد ✅"):
        elapsed = time.time() - start_time
        if elapsed > time_limit:
            st.warning("⏳ انتهى الوقت! خسرت هذه الجولة.")
        elif answer == q["answer"]:
            st.success("🎉 إجابة صحيحة!")
            st.session_state.score += 1
        else:
            st.error(f"❌ إجابة خاطئة! الصحيحة هي: {q['answer']}")

        st.session_state.remaining_questions.pop(0)
        st.experimental_rerun()

else:
    st.success(f"🎉 خلصت الأسئلة! نتيجتك: {st.session_state.score} / {len(questions)}")

    # ---------------- حفظ النتائج ----------------
    try:
        with open("leaderboard.json", "r", encoding="utf-8") as f:
            leaderboard = json.load(f)
    except:
        leaderboard = []

    leaderboard.append({"name": st.session_state.player, "score": st.session_state.score})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    with open("leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

    # ---------------- عرض الترتيب ----------------
    st.subheader("🏆 الترتيب:")
    for idx, entry in enumerate(leaderboard[:5], 1):
        st.write(f"**{idx}. {entry['name']}** - {entry['score']} نقطة")
