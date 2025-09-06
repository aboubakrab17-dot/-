import json, random, time, os, base64
import streamlit as st
import pandas as pd

# ---------- إعدادات عامة ----------
st.set_page_config(page_title="لعبة الألغاز", page_icon="❓", layout="centered")

# خلفية (لو عندك background.jpg في نفس المستودع راح تتطبّق تلقائياً)
def set_bg():
    bg_path = "background.jpg"
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url("data:image/jpg;base64,{b64}") center/cover no-repeat fixed;
            }}
            .question-card {{
                background: rgba(255,255,255,0.85);
                padding: 1.25rem;
                border-radius: 1rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            }}
            .hud {{
                background: rgba(0,0,0,0.55);
                color: #fff;
                padding: .5rem .75rem;
                border-radius: .75rem;
                font-size: .9rem;
                margin-bottom: .5rem;
                display:inline-block;
                margin-right:.5rem;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .question-card {background: #ffffff; padding: 1.25rem; border-radius: 1rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08);}
            .hud {background: #0f172a; color:#fff; padding:.5rem .75rem; border-radius:.75rem; font-size:.9rem; display:inline-block; margin-right:.5rem;}
            </style>
            """,
            unsafe_allow_html=True
        )

set_bg()

# ---------- أصوات مدمجة (بسيطة) ----------
# نغمات قصيرة Base64 (تقدر تبدلهم بملفات correct.mp3 / wrong.mp3 لو حبيت)
BEEP_OK = b"UklGRhQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABYAAAABAAgAZGF0YQAAAAA="
BEEP_NO = b"UklGRhQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABYAAAABAAgAZGF0YQAAAAA="

def play_sound(kind):
    # لو عندك ملفات صوت: correct.mp3 / wrong.mp3 في نفس المستودع، استعملهم
    file_map = {"ok": "correct.mp3", "no": "wrong.mp3"}
    if os.path.exists(file_map[kind]):
        st.audio(file_map[kind])
    else:
        # fallback لنغمة بسيطة (تقريبية)
        data = BEEP_OK if kind == "ok" else BEEP_NO
        st.audio(data)

# ---------- تحميل الأسئلة ----------
@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

QUESTS = load_questions()
DIFFICULTIES = ["سهل", "متوسط", "صعب"]

# ---------- تهيئة الحالة ----------
if "started" not in st.session_state:
    st.session_state.started = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "index" not in st.session_state:
    st.session_state.index = 0
if "picked" not in st.session_state:
    st.session_state.picked = None
if "order" not in st.session_state:
    st.session_state.order = []
if "current_list" not in st.session_state:
    st.session_state.current_list = []
if "deadline" not in st.session_state:
    st.session_state.deadline = None
if "results" not in st.session_state:
    st.session_state.results = []  # (q, user_ans, correct)

# ---------- سايدبار (إعدادات) ----------
st.sidebar.title("إعدادات اللعبة")
st.session_state.name = st.sidebar.text_input("اكتب اسمك لعرضه في الترتيب", value=st.session_state.name)
difficulty = st.sidebar.selectbox("اختيار المستوى", DIFFICULTIES, index=0)
num_questions = st.sidebar.slider("عدد الأسئلة", min_value=5, max_value=30, value=10, step=1)
timer_on = st.sidebar.checkbox("تفعيل مؤقّت لكل سؤال", value=True)
timer_secs = st.sidebar.slider("مدة المؤقّت (ثواني)", 10, 60, 25) if timer_on else 0
sound_on = st.sidebar.checkbox("تفعيل الأصوات", value=True)

# ---------- تحضير الأسئلة حسب المستوى ----------
def filter_by_difficulty(level):
    return [q for q in QUESTS if q.get("difficulty") == level]

def start_game():
    pool = filter_by_difficulty(difficulty)
    random.shuffle(pool)
    st.session_state.current_list = pool[:num_questions]
    st.session_state.order = list(range(len(st.session_state.current_list)))
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.started = True
    st.session_state.picked = None
    if timer_on:
        st.session_state.deadline = time.time() + timer_secs
    else:
        st.session_state.deadline = None

def reset_game():
    st.session_state.started = False
    st.session_state.picked = None
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.current_list = []
    st.session_state.order = []
    st.session_state.deadline = None

# ---------- شاشة البداية ----------
st.markdown("<h1 style='text-align:center;'>لعبة الألغاز التعليمية</h1>", unsafe_allow_html=True)
st.caption("اختبر معلوماتك في مستويات مختلفة، اربح نقاطًا وتصدر لوحة الترتيب.")

colA, colB, colC = st.columns([1,1,1])
with colB:
    if not st.session_state.started:
        if st.button("ابدأ التحدي 👇", use_container_width=True, type="primary"):
            start_game()

# ---------- HUD أعلى الصفحة ----------
if st.session_state.started:
    st.markdown(
        f"""
        <div>
            <span class="hud">اللاعب: {st.session_state.name or "بدون اسم"}</span>
            <span class="hud">المستوى: {difficulty}</span>
            <span class="hud">النقاط: {st.session_state.score}</span>
            <span class="hud">السؤال: {st.session_state.index + 1}/{len(st.session_state.current_list)}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- عرض السؤال ----------
def show_question():
    q_idx = st.session_state.index
    q = st.session_state.current_list[q_idx]
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.subheader(q["question"])
    choice = st.radio("اختر الإجابة:", q["options"], index=None, key=f"radio_{q_idx}")
    st.session_state.picked = choice

    # مؤقّت
    if timer_on and st.session_state.deadline:
        t_left = int(max(0, st.session_state.deadline - time.time()))
        prog = (timer_secs - t_left) / timer_secs
        st.progress(min(max(prog, 0.0), 1.0), text=f"الوقت المتبقي: {t_left} ثانية")
        # لو الوقت خلص
        if t_left <= 0:
            st.warning("انتهى الوقت لهذا السؤال!")
            st.session_state.results.append((q["question"], None, q["answer"]))
            st.session_state.index += 1
            if st.session_state.index < len(st.session_state.current_list):
                if timer_on:
                    st.session_state.deadline = time.time() + timer_secs
            st.experimental_rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("تأكيد الإجابة", use_container_width=True):
            if st.session_state.picked is None:
                st.info("اختر إجابة أولاً.")
                st.stop()
            correct = q["answer"]
            if st.session_state.picked == correct:
                st.success("إجابة صحيحة! +10 نقاط")
                st.session_state.score += 10
                if sound_on: play_sound("ok")
            else:
                st.error(f"إجابة خاطئة! الجواب الصحيح: {correct}")
                if sound_on: play_sound("no")
            st.session_state.results.append((q["question"], st.session_state.picked, correct))
            st.session_state.index += 1
            if st.session_state.index < len(st.session_state.current_list):
                st.session_state.picked = None
                if timer_on:
                    st.session_state.deadline = time.time() + timer_secs
            st.experimental_rerun()
    with c2:
        if st.button("تخطي السؤال", use_container_width=True):
            st.info("تم تخطي السؤال.")
            st.session_state.results.append((q["question"], None, q["answer"]))
            st.session_state.index += 1
            if st.session_state.index < len(st.session_state.current_list):
                st.session_state.picked = None
                if timer_on:
                    st.session_state.deadline = time.time() + timer_secs
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- حفظ/قراءة الترتيب ----------
def save_leaderboard(name, score, level):
    row = {"name": name or "ضيف", "score": score, "level": level, "ts": int(time.time())}
    try:
        if os.path.exists("leaderboard.json"):
            data = json.load(open("leaderboard.json","r",encoding="utf-8"))
        else:
            data = []
        data.append(row)
        with open("leaderboard.json","w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # على ستريملت كلاود قد لا يدوم التخزين، ماشي مشكل

def read_leaderboard():
    try:
        if os.path.exists("leaderboard.json"):
            data = json.load(open("leaderboard.json","r",encoding="utf-8"))
            df = pd.DataFrame(data)
            df = df.sort_values(["score","ts"], ascending=[False, True])
            return df.head(20)
    except Exception:
        pass
    return pd.DataFrame(columns=["name","score","level","ts"])

# ---------- شاشة النتيجة ----------
def show_summary():
    st.markdown("## النتيجة النهائية")
    st.info(f"مجموع نقاطك: {st.session_state.score} من {len(st.session_state.current_list)*10}")

    # جدول تفصيلي
    details = []
    for q, user_ans, correct in st.session_state.results:
        details.append({
            "السؤال": q,
            "إجابتك": user_ans if user_ans is not None else "—",
            "الصحيح": correct,
            "صح؟": "✅" if user_ans == correct else "❌"
        })
    st.dataframe(pd.DataFrame(details), use_container_width=True)

    # حفظ الترتيب
    save_leaderboard(st.session_state.name, st.session_state.score, difficulty)

    st.markdown("### الترتيب العام (Top 20)")
    lb = read_leaderboard()
    if len(lb) == 0:
        st.caption("مازال ما كاش ترتيب دائم. جرّب العب مرّة أخرى!")
    else:
        st.dataframe(lb[["name","level","score"]], use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("إعادة اللعب بنفس الإعدادات", use_container_width=True):
            start_game()
            st.experimental_rerun()
    with c2:
        if st.button("رجوع للشاشة الرئيسية", use_container_width=True):
            reset_game()
            st.experimental_rerun()

# ---------- المنطق الرئيسي ----------
if st.session_state.started:
    if st.session_state.index < len(st.session_state.current_list):
        show_question()
    else:
        show_summary()
else:
    # نصائح سريعة للمستخدم
    with st.expander("كيف تلعب؟"):
        st.markdown(
            """
            1) من الشريط الجانبي: اختر المستوى، عدد الأسئلة، وفعّل المؤقّت/الأصوات إذا حبيت.  
            2) اضغط **ابدأ التحدي**.  
            3) اختر الإجابة واضغط **تأكيد الإجابة**.  
            4) في النهاية تشوف **مجموع نقاطك** وترتيبك في القائمة.  
            """
)
