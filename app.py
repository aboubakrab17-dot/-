import streamlit as st
import json
import random

# تحميل الأسئلة من ملف JSON
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# حالة التطبيق
if "score" not in st.session_state:
    st.session_state.score = 0
if "asked_questions" not in st.session_state:
    st.session_state.asked_questions = []

st.title("🧩 لعبة الألغاز والأسئلة")

st.write("مرحبا بك في لعبة الألغاز! جاوب على الأسئلة وجمع النقاط 🎉")

# اختيار سؤال عشوائي لم يُطرح بعد
available_questions = [q for q in questions if q["question"] not in st.session_state.asked_questions]

if available_questions:
    question = random.choice(available_questions)
    st.session_state.asked_questions.append(question["question"])

    st.subheader("❓ السؤال:")
    st.write(question["question"])

    answer = st.text_input("✍️ اكتب إجابتك هنا:")

    if st.button("تحقق"):
        if answer.strip().lower() == question["answer"].strip().lower():
            st.success("✔️ إجابة صحيحة! أحسنت 👏")
            st.session_state.score += 1
        else:
            st.error(f"❌ خطأ! الجواب الصحيح هو: {question['answer']}")

    st.info(f"🔢 مجموع نقاطك: {st.session_state.score}")
else:
    st.success("🎉 لقد أجبت على جميع الأسئلة! رائع 👏👏")
