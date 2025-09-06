import streamlit as st
import json, random, os, datetime

# ------------------------- إعدادات الصفحة + الخلفية -------------------------
st.set_page_config(page_title="لعبة الألغاز والأسئلة", page_icon="🧩", layout="wide")

# CSS للخلفية وشكل الكروت/الأزرار
BG_CSS = """
<style>
/* خلفية متدرّجة ناعمة، وإذا توفرت صورة assets/bg.jpg نستبدلها برمجياً أدناه */
.stApp {
  background: linear-gradient(135deg, #5b5ee6 0%, #9b59b6 50%, #00b4d8 100%);
  background-attachment: fixed;
  color: #ffffff;
}
.card {
  border-radius: 18px;
  padding: 16px 18px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(6px);
  transition: transform .08s ease, background .2s ease;
  cursor: pointer;
}
.card:hover { transform: translateY(-2px); background: rgba(255,255,255,0.12); }
.card.correct { border: 2px solid #2ecc71; background: rgba(46,204,113,0.18); }
.card.wrong   { border: 2px solid #e74c3c; background: rgba(231,76,60,0.18); }
.small { opacity:.9; font-size:.92rem; }
.panel {
  border-radius: 20px; padding: 18px; 
  background: rgba(0,0,0,0.18);
  border: 1px solid rgba(255,255,255,.18);
}
</style>
"""

# إن وجدت صورة خلفية في assets/bg.jpg نركّبها بدلاً من التدرّج
bg_path = "assets/bg.jpg"
if os.path.exists(bg_path):
    BG_CSS += f"""
    <style>
    .stApp {{
      background: url('{bg_path}');
      background-size: cover;
      background-position: center;
      background-attachment: fixed;
      color: #ffffff;
    }}
    </style>
    """
st.markdown(BG_CSS, unsafe_allow_html=True)

# ------------------------- إعداد حالة الجلسة -------------------------
if "qs" not in st.session_state:
    st.session_state.qs = []
if "i" not in st.session_state:
    st.session_state.i = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "username" not in st.session_state:
    st.session_state.username = ""
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "chosen" not in st.session_state:
    st.session_state.chosen = None
if "sound_on" not in st.session_state:
    st.session_state.sound_on = True

# ------------------------- تحميل الأسئلة -------------------------
def load_questions(path="questions.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    random.shuffle(data)
    return data

# ------------------------- الأصوات -------------------------
# روابط خفيفة (يمكنك تغييرها لاحقاً أو إيقافها من الشريط الجانبي)
CORRECT_SND = "https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"
WRONG_SND   = "https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg"

def play_sound(url):
    if st.session_state.sound_on:
        st.markdown(
            f"""
            <audio autoplay="true" style="display:none">
              <source src="{url}">
            </audio>
            """,
            unsafe_allow_html=True
        )

# ------------------------- لوحة المتصدرين -------------------------
LEADER_PATH = "leaderboard.json"

def read_leaderboard():
    if os.path.exists(LEADER_PATH):
        with open(LEADER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def write_leaderboard(rows):
    with open(LEADER_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def push_score(name, score, total):
    rows = read_leaderboard()
    rows.append({
        "name": name,
        "score": score,
        "total": total,
        "streak": st.session_state.best_streak,
        "date": datetime.datetime.utcnow().isoformat() + "Z"
    })
    rows.sort(key=lambda r: (r["score"], r["streak"]), reverse=True)
    rows = rows[:50]
    write_leaderboard(rows)

# ------------------------- واجهة المستخدم -------------------------
with st.sidebar:
    st.title("⚙️ الإعدادات")
    st.session_state.sound_on = st.toggle("تفعيل الصوتيات", value=st.session_state.sound_on)
    st.caption("يمكنك استبدال الخلفية بوضع صورة باسم **assets/bg.jpg** داخل المستودع.")
    st.divider()
    st.subheader("🏆 المتصدرون (أعلى 10)")
    lb = read_leaderboard()[:10]
    if lb:
        for idx, r in enumerate(lb, 1):
            st.write(f"**{idx}. {r['name']}** — {r['score']}/{r['total']} | 🔥 {r['streak']}")
    else:
        st.write("لا توجد نتائج بعد.")

st.markdown(
    "<h1 style='text-align:center; margin-top:-10px'>🧩 لعبة الألغاز والأسئلة</h1>",
    unsafe_allow_html=True
)

container = st.container()
with container:
    # إدخال الاسم عند البداية
    if not st.session_state.username:
        with st.form("start_form", clear_on_submit=False):
            st.subheader("ابدأ اللعب الآن 🚀")
            name = st.text_input("أدخل اسمك", placeholder="مثال: Aboubakr")
            cols = st.columns([1,1,2])
            start = cols[0].form_submit_button("ابدأ ✅")
        if start:
            if name.strip():
                st.session_state.username = name.strip()
                # تحميل الأسئلة وإعادة التعيين
                st.session_state.qs = load_questions()
                st.session_state.i = 0
                st.session_state.score = 0
                st.session_state.streak = 0
                st.session_state.best_streak = 0
                st.session_state.answered = False
                st.session_state.chosen = None
                st.rerun()
            else:
                st.warning("⚠️ من فضلك أدخل اسمك للمتابعة.")
    else:
        qs = st.session_state.qs or load_questions()
        total = len(qs)

        # شريط تقدم + معلومات
        prog = 0 if total == 0 else st.session_state.i/total
        top_c1, top_c2, top_c3, top_c4 = st.columns([2,1,1,1])
        with top_c1:
            st.progress(prog, text=f"التقدم: {st.session_state.i}/{total}")
        with top_c2:
            st.metric("النقاط", st.session_state.score)
        with top_c3:
            st.metric("🔥 السلسلة", st.session_state.streak)
        with top_c4:
            st.metric("🏅 أفضل سلسلة", st.session_state.best_streak)

        # انتهاء اللعبة؟
        if st.session_state.i >= total:
            st.success(f"🎉 أحسنت يا {st.session_state.username}! نتيجتك: {st.session_state.score}/{total}")
            push_score(st.session_state.username, st.session_state.score, total)

            c1, c2 = st.columns(2)
            if c1.button("🔄 العب من جديد"):
                st.session_state.username = ""
                st.rerun()
            if c2.button("❓ أسئلة جديدة"):
                st.session_state.qs = load_questions()
                st.session_state.i = 0
                st.session_state.score = 0
                st.session_state.streak = 0
                st.session_state.best_streak = 0
                st.session_state.answered = False
                st.session_state.chosen = None
                st.rerun()
        else:
            q = qs[st.session_state.i]
            st.subheader(f"❓ السؤال {st.session_state.i+1}: {q['question']}")
            st.caption(q.get("hint","").strip() or " ")

            # خيارات ككروت قابلة للنقر
            cols = st.columns(2)
            chosen_idx = None

            # نحدد نمط الكارد بحسب حالة الإجابة
            def card_class(opt):
                if not st.session_state.answered:
                    return "card"
                # بعد الإجابة: نلوّن الصح والغلط
                if opt == q["answer"]:
                    return "card correct"
                if opt == st.session_state.chosen and opt != q["answer"]:
                    return "card wrong"
                return "card"

            # عرض الخيارات
            options = q["options"]
            for j, opt in enumerate(options):
                with cols[j % 2]:
                    clicked = st.button(opt, key=f"opt_{st.session_state.i}_{j}")
                    st.markdown(f"<div class='{card_class(opt)} small'>{opt}</div>", unsafe_allow_html=True)
                    if clicked and not st.session_state.answered:
                        st.session_state.chosen = opt
                        st.session_state.answered = True
                        if opt == q["answer"]:
                            st.session_state.score += 1
                            st.session_state.streak += 1
                            st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
                            play_sound(CORRECT_SND)
                            st.balloons()
                        else:
                            st.session_state.streak = 0
                            play_sound(WRONG_SND)
                        st.rerun()

            st.write("")  # مسافة بسيطة

            # عند انتهاء السؤال الحالي
            if st.session_state.answered:
                if st.session_state.chosen == q["answer"]:
                    st.success("✅ إجابة صحيحة! ممتاز 👏")
                else:
                    st.error(f"❌ إجابة خاطئة، الصحيح: **{q['answer']}**")
                if q.get("explanation"):
                    st.info(f"ℹ️ شرح: {q['explanation']}")

                n_c1, n_c2 = st.columns([1,1])
                if n_c1.button("➡️ التالي"):
                    st.session_state.i += 1
                    st.session_state.answered = False
                    st.session_state.chosen = None
                    st.rerun()
                if n_c2.button("🔄 سؤال عشوائي"):
                    random.shuffle(st.session_state.qs)
                    st.session_state.i = 0
                    st.session_state.answered = False
                    st.session_state.chosen = None
                    st.rerun()
