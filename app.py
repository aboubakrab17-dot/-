import streamlit as st
import json
import random
import os

# -----------------------------
# تحميل الأسئلة من ملف JSON
# -----------------------------
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# تحميل/حفظ الإحصائيات
# -----------------------------
def load_leaderboard():
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_leaderboard(data):
    with open("leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------------
# واجهة اللعبة
# -----------------------------
def main():
    st.set_page_config(page_title="لعبة الألغاز", layout="wide")

    st.title("🧩 لعبة الألغاز التفاعلية")

    # اختيار الخلفية
    background = st.sidebar.selectbox("🎨 اختر الخلفية", ["🌌 فضاء", "🌳 غابة", "🏙️ مدينة", "🏖️ شاطئ"])
    if background == "🌌 فضاء":
        st.markdown("""<style>body {background-color: black; color: white;}</style>""", unsafe_allow_html=True)
    elif background == "🌳 غابة":
        st.markdown("""<style>body {background-color: #2e8b57; color: white;}</style>""", unsafe_allow_html=True)
    elif background == "🏙️ مدينة":
        st.markdown("""<style>body {background-color: #708090; color: white;}</style>""", unsafe_allow_html=True)
    elif background == "🏖️ شاطئ":
        st.markdown("""<style>body {background-color: #f4e1d2; color: black;}</style>""", unsafe_allow_html=True)

    # تحميل الأسئلة
    questions = load_questions()

    # اختيار الصعوبة
    difficulty = st.sidebar.radio("🎯 اختر المستوى", ["سهل", "متوسط", "صعب"])

    # إدخال اسم اللاعب
    player_name = st.text_input("📝 أدخل اسمك للعب", "")
    if not player_name:
        st.warning("⚠️ من فضلك أدخل اسمك للمتابعة.")
        return

    # تحميل لوحة الترتيب
    leaderboard = load_leaderboard()
    if player_name not in leaderboard:
        leaderboard[player_name] = {"games_played": 0, "total_score": 0, "best_score": 0}

    # حالة الجلسة
    if "index" not in st.session_state:
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.finished = False

    # عرض السؤال
    if not st.session_state.finished:
        q_list = questions[difficulty]
        if st.session_state.index < len(q_list):
            q = q_list[st.session_state.index]
            st.subheader(f"❓ السؤال {st.session_state.index + 1}: {q['question']}")
            answer = st.radio("اختر الإجابة:", q["options"], key=f"q_{st.session_state.index}")
            if st.button("✅ تأكيد"):
                if answer == q["answer"]:
                    st.success("🎉 إجابة صحيحة!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ خطأ! الجواب الصحيح هو: {q['answer']}")
                st.session_state.index += 1
        else:
            st.session_state.finished = True
            st.success(f"🏆 انتهت اللعبة! نتيجتك: {st.session_state.score}/{len(q_list)}")

            # تحديث النتائج
            leaderboard[player_name]["games_played"] += 1
            leaderboard[player_name]["total_score"] += st.session_state.score
            leaderboard[player_name]["best_score"] = max(leaderboard[player_name]["best_score"], st.session_state.score)
            save_leaderboard(leaderboard)

    # إعادة اللعب
    if st.session_state.finished and st.button("🔄 العب من جديد"):
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.finished = False

    # عرض لوحة الترتيب
    st.sidebar.subheader("🏅 لوحة الترتيب")
    for player, stats in leaderboard.items():
        avg = stats["total_score"] / stats["games_played"] if stats["games_played"] > 0 else 0
        st.sidebar.write(f"👤 {player}: أفضل نتيجة {stats['best_score']}, معدل {avg:.2f}")

if __name__ == "__main__":
    main()
