# app.py
import streamlit as st
import random
import time
import json
from pathlib import Path
from datetime import datetime

# -------------------- إعدادات الصفحة --------------------
st.set_page_config(page_title="أفضل لعبة ألغاز في العالم 🎮", page_icon="🎮", layout="centered")

# -------------------- خلفية Neon + Grid (بدون صور خارجية) --------------------
NEON_CSS = """
<style>
.stApp {
  background:
    radial-gradient(60% 80% at 50% 20%, rgba(141, 0, 255, 0.35), rgba(0,0,0,0) 60%),
    radial-gradient(70% 60% at 20% 10%, rgba(0, 212, 255, 0.25), rgba(0,0,0,0) 60%),
    linear-gradient(135deg, rgba(20,20,35,0.95) 0%, rgba(10,10,20,0.95) 100%),
    repeating-linear-gradient( to right, rgba(255,255,255,0.06) 0 1px, transparent 1px 50px),
    repeating-linear-gradient( to bottom, rgba(255,255,255,0.06) 0 1px, transparent 1px 50px);
  background-blend-mode: screen, screen, normal, overlay, overlay;
}
.block-container{
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 1.2rem;
}
h1,h2,h3,h4,h5,h6,p,span,div,label { color: #fff !important; }
.stButton>button {
  border-radius: 12px; border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08); padding: 0.6rem 0.9rem;
}
.stButton>button:hover { background: rgba(255,255,255,0.18); }
.timer-badge {
  display: inline-block; padding: .35rem .75rem;
  background: rgba(0, 200, 255, .15);
  border: 1px solid rgba(0, 200, 255, .4);
  border-radius: 999px; font-weight: 700;
}
.q-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 14px; padding: 1rem 1.1rem; margin-bottom: .75rem;
  font-size: 1.1rem;
}
.choice-btn {
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08);
  padding: 0.7rem 1rem; margin-bottom: .6rem; text-align: left;
}
.choice-btn:hover { background: rgba(255,255,255,0.18); }
@media (max-width: 480px) { .block-container{ padding: 1rem; } }
</style>
"""
st.markdown(NEON_CSS, unsafe_allow_html=True)

# -------------------- أسئلة افتراضية (لو ماكانش questions.json) --------------------
DEFAULT_QUESTIONS = [
    # easy
    {"question":"ما لون السماء في يوم صافٍ؟","options":["أحمر","أزرق","أخضر","أسود"],"answer":"أزرق","difficulty":"easy","hint":"تشتّت رايلي يخلي السماء تميل للأزرق."},
    {"question":"كم عدد أرجل العنكبوت؟","options":["6","8","10","12"],"answer":"8","difficulty":"easy","hint":"أكثر من الحشرات (6)."},
    {"question":"ما عاصمة الجزائر؟","options":["وهران","الجزائر العاصمة","قسنطينة","سطيف"],"answer":"الجزائر العاصمة","difficulty":"easy"},
    {"question":"كم أضلاع المثلث؟","options":["2","3","4","5"],"answer":"3","difficulty":"easy"},
    {"question":"أقرب كوكب للشمس؟","options":["المشتري","الأرض","عطارد","الزهرة"],"answer":"عطارد","difficulty":"easy"},
    # medium
    {"question":"الكوكب الأحمر؟","options":["الزهرة","المريخ","المشتري","زحل"],"answer":"المريخ","difficulty":"medium"},
    {"question":"عدد قارات العالم؟","options":["5","6","7","8"],"answer":"7","difficulty":"medium"},
    {"question":"أين يقع برج إيفل؟","options":["روما","باريس","لندن","مدريد"],"answer":"باريس","difficulty":"medium"},
    {"question":"وحدة قياس القدرة؟","options":["فولت","أوم","واط","أمبير"],"answer":"واط","difficulty":"medium","hint":"P = V × I"},
    {"question":"أكبر محيط؟","options":["الأطلسي","الهندي","المتجمد","الهادي"],"answer":"الهادي","difficulty":"medium"},
    # hard
    {"question":"سنة اندلاع الثورة الجزائرية؟","options":["1952","1954","1962","1945"],"answer":"1954","difficulty":"hard"},
    {"question":"أسرع حيوان بري؟","options":["الغزال","الفهد","الأسد","النمر"],"answer":"الفهد","difficulty":"hard"},
    {"question":"العنصر Fe؟","options":["الذهب","النحاس","الحديد","الزنك"],"answer":"الحديد","difficulty":"hard"},
    {"question":"أثقل كوكب؟","options":["المشتري","زحل","نبتون","الأرض"],"answer":"المشتري","difficulty":"hard"},
    {"question":"أكبر صحراء؟","options":["الكبرى","غوبي","كالاهاري","أستراليا"],"answer":"الصحراء الكبرى","difficulty":"hard"},
]

def load_questions():
    p = Path("questions.json")
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_QUESTIONS
    return DEFAULT_QUESTIONS

QUESTIONS = load_questions()
ALL_COUNT = len(QUESTIONS)

# -------------------- حالة الجلسة --------------------
ss = st.session_state
defaults = {
    "player": None,
    "difficulty": "Mix",
    "sounds_on": True,
    "pool": [],
    "idx": -1,
    "score": 0,
    "streak": 0,
    "best_streak": 0,
    "question_start": None,
    "perq_limit": 15,
    "global_timer_on": False,
    "global_start": None,
    "global_limit": 180,  # 3 دقائق افتراضياً
    "hidden_options": set(),
    "used_hint": 0,
    "used_5050": False,
    "leaderboard": [],
    "num_questions": min(10, ALL_COUNT),
    "history": [],   # [(difficulty, correct_bool, time_sec)]
    "answer_times": []
}
for k,v in defaults.items():
    if k not in ss: ss[k] = v

# -------------------- دوال --------------------
def time_per_difficulty():
    if ss.difficulty == "easy":   return 20
    if ss.difficulty == "medium": return 15
    if ss.difficulty == "hard":   return 12
    return 15  # Mix

def select_pool():
    # فلترة حسب المستوى
    pool = QUESTIONS[:] if ss.difficulty == "Mix" else [q for q in QUESTIONS if q.get("difficulty","easy")==ss.difficulty]
    random.shuffle(pool)
    # نختار العدد المطلوب بدون تكرار
    n = min(ss.num_questions, len(pool))
    ss.pool = pool[:n]
    ss.idx = -1

def next_question():
    ss.idx += 1
    ss.hidden_options = set()
    ss.perq_limit = time_per_difficulty()
    ss.question_start = time.time()

def current_question():
    if 0 <= ss.idx < len(ss.pool):
        return ss.pool[ss.idx]
    return None

def play_sound(url: str):
    if not ss.sounds_on: return
    st.markdown(f"""<audio autoplay style="display:none"><source src="{url}"></audio>""", unsafe_allow_html=True)

def apply_5050(q):
    if ss.used_5050: 
        st.warning("🚫 استعملت 50/50 من قبل.")
        return
    wrongs = [o for o in q["options"] if o != q["answer"]]
    hide = set(random.sample(wrongs, k=min(2, len(wrongs))))
    ss.hidden_options |= hide
    ss.used_5050 = True

def show_hint(q):
    if ss.used_hint >= 2:
        st.warning("🚫 وصلت للحدّ الأقصى للتلميحات (2).")
        return
    hint = q.get("hint")
    if hint:
        st.info(f"💡 تلميح: {hint}")
        ss.used_hint += 1
    else:
        st.info("💡 ماكانش تلميح لهذا السؤال.")

def points_for(q):
    d = q.get("difficulty","easy")
    return 1 if d=="easy" else 2 if d=="medium" else 3

def finish_round():
    # حفظ النتيجة في المتصدرين
    ss.leaderboard.append({
        "name": ss.player, "score": ss.score, "mode": ss.difficulty,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    ss.leaderboard = sorted(ss.leaderboard, key=lambda r: r["score"], reverse=True)[:10]

# -------------------- شاشة البداية --------------------
st.title("🎮 أفضل لعبة ألغاز في العالم")
if not ss.player:
    name = st.text_input("✨ اكتب اسمك للبدء", value="")
    colA, colB = st.columns(2)
    with colA:
        diff = st.selectbox("🎯 اختر المستوى", ["Mix", "easy", "medium", "hard"], index=0)
        sounds = st.toggle("🔊 صوت", value=True)
    with colB:
        max_n = ALL_COUNT if diff=="Mix" else len([q for q in QUESTIONS if q.get("difficulty","easy")==diff])
        max_n = max(5, max_n)  # ضمان حد أدنى
        num = st.slider("🧩 عدد الأسئلة", 5, min(50, max_n), value=min(10, max_n))
        perq = st.slider("⏳ وقت لكل سؤال (ثانية)", 8, 40, time_per_difficulty())
    g_on = st.toggle("⏱️ مؤقت عام للجولة", value=False)
    g_lim = st.slider("⌛ زمن الجولة الكلي (ث)", 60, 600, 180, disabled=not g_on)

    if st.button("🚀 ابدأ"):
        if name.strip():
            ss.player = name.strip()
            ss.difficulty = diff
            ss.sounds_on = sounds
            ss.num_questions = num
            # تحضير الجولة
            select_pool()
            # نثبت وقت السؤال حسب اختيار المستخدم (غير إلزامي بمستوى)
            ss.perq_limit = perq
            next_question()
            ss.score = 0
            ss.streak = 0
            ss.best_streak = 0
            ss.history = []
            ss.answer_times = []
            ss.used_hint = 0
            ss.used_5050 = False
            if g_on:
                ss.global_timer_on = True
                ss.global_limit = g_lim
                ss.global_start = time.time()
            else:
                ss.global_timer_on = False
                ss.global_start = None
            st.rerun()
        else:
            st.warning("⚠️ أدخل اسم صالح.")
    st.stop()

# -------------------- شريط التقدّم + معلومات --------------------
total = len(ss.pool)
answered = max(0, ss.idx)  # المجاوب عليهم
st.progress(answered/total if total else 0.0, text=f"التقدّم: {answered}/{total}")

# مؤقتات
if ss.question_start:
    elapsed_q = int(time.time() - ss.question_start)
    remain_q = max(0, ss.perq_limit - elapsed_q)
else:
    remain_q = ss.perq_limit

if ss.global_timer_on and ss.global_start:
    elapsed_g = int(time.time() - ss.global_start)
    remain_g = max(0, ss.global_limit - elapsed_g)
else:
    remain_g = None

top = st.container()
with top:
    cols = st.columns(4)
    cols[0].metric("👤 اللاعب", ss.player)
    cols[1].metric("🏅 النقاط", ss.score)
    cols[2].metric("🔥 السلسلة", ss.streak)
    if remain_g is not None:
        cols[3].markdown(f"<span class='timer-badge'>⏱️ {remain_g}s</span>", unsafe_allow_html=True)
    else:
        cols[3].markdown(f"<span class='timer-badge'>⏳ {remain_q}s</span>", unsafe_allow_html=True)

# تحديث العدادات كل ثانية
if current_question() and (remain_q > 0) and (remain_g is None or remain_g > 0):
    st.markdown("<script>setTimeout(()=>window.parent.location.reload(),1000);</script>", unsafe_allow_html=True)

# إذا انتهى مؤقت السؤال
if current_question() and remain_q == 0:
    st.warning("⏰ انتهى وقت السؤال!")
    play_sound("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg")
    # سجّل محاولة خاطئة زمن 0؟
    q = current_question()
    ss.history.append((q.get("difficulty","easy"), False, ss.perq_limit))
    ss.answer_times.append(ss.perq_limit)
    ss.streak = 0
    next_question()
    st.rerun()

# إذا انتهى مؤقت الجولة
if current_question() and ss.global_timer_on and remain_g == 0:
    st.error("⌛ انتهى زمن الجولة!")
    # انهي الجولة
    ss.idx = len(ss.pool)  # كي يدخل في شاشة النهاية
    st.rerun()

# -------------------- عرض السؤال الحالي --------------------
q = current_question()
if q:
    st.markdown(f"<div class='q-card'>❓ {q['question']}</div>", unsafe_allow_html=True)

    visible = [o for o in q["options"] if o not in ss.hidden_options]
    chosen = st.session_state.get(f"chosen_{ss.idx}", None)

    for opt in visible:
        if st.button(opt, key=f"opt_{ss.idx}_{opt}", use_container_width=True):
            chosen = opt
            st.session_state[f"chosen_{ss.idx}"] = opt
            spent = int(time.time() - ss.question_start) if ss.question_start else 0

            if opt == q["answer"]:
                st.success("✅ إجابة صحيحة! ممتاز 👏")
                play_sound("https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg")
                pts = points_for(q)
                # مكافأة سرعة: إذا جاوبت في أقل من 5 ثواني، +1
                if spent <= 5: pts += 1
                ss.score += pts
                ss.streak += 1
                ss.best_streak = max(ss.best_streak, ss.streak)
                ss.history.append((q.get("difficulty","easy"), True, spent))
                ss.answer_times.append(spent)
                st.balloons()
            else:
                st.error(f"❌ خطأ! الجواب الصحيح: **{q['answer']}**")
                play_sound("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg")
                ss.streak = 0
                ss.history.append((q.get("difficulty","easy"), False, spent))
                ss.answer_times.append(spent)

            # شرح إن وُجد
            if q.get("explanation"):
                st.info(f"ℹ️ شرح: {q['explanation']}")
            elif q.get("hint"):
                st.caption(f"💡 تلميح سابق: {q['hint']}")

            time.sleep(0.6)
            next_question()
            st.rerun()

    cA, cB, cC, cD = st.columns(4)
    with cA:
        if st.button("💡 تلميح", use_container_width=True):
            show_hint(q)
    with cB:
        if st.button("🎯 50/50", use_container_width=True):
            apply_5050(q); st.rerun()
    with cC:
        if st.button("⏭️ تخطي", use_container_width=True):
            # يعتبرها محاولة بدون نقاط
            spent = int(time.time() - ss.question_start) if ss.question_start else 0
            ss.history.append((q.get("difficulty","easy"), False, spent))
            ss.answer_times.append(spent)
            ss.streak = 0
            next_question(); st.rerun()
    with cD:
        if st.button("🔊/🔇 تبديل الصوت", use_container_width=True):
            ss.sounds_on = not ss.sounds_on; st.rerun()

else:
    # -------------------- نهاية الجولة --------------------
    st.success(f"🎉 مبروك {ss.player}! أنهيت الجولة.")
    st.write(f"🔢 نتيجتك النهائية: **{ss.score}** من **{total}**")
    # إحصائيات
    if ss.answer_times:
        avg = sum(ss.answer_times)/len(ss.answer_times)
        fastest = min(ss.answer_times)
        slowest = max(ss.answer_times)
    else:
        avg = fastest = slowest = 0

    # دقة عامة
    total_correct = sum(1 for _,ok,_ in ss.history if ok)
    accuracy = (100*total_correct/len(ss.history)) if ss.history else 0

    # تفصيل حسب الصعوبة
    def acc_for(level):
        subset = [ok for d,ok,_ in ss.history if d==level]
        return (100*sum(subset)/len(subset)) if subset else 0
    acc_easy = acc_for("easy"); acc_med = acc_for("medium"); acc_hard = acc_for("hard")

    st.subheader("📊 تقرير الأداء")
    st.write(f"- ✅ الدقة العامة: **{accuracy:.1f}%**")
    st.write(f"- ⏱️ متوسط زمن الإجابة: **{avg:.1f}ث** — أسرع: **{fastest}s** | أبطأ: **{slowest}s**")
    st.write(f"- 🔥 أطول سلسلة صحيحة: **{ss.best_streak}**")
    st.write(f"- 🎯 الدقة حسب الصعوبة → سهل: **{acc_easy:.0f}%** | متوسط: **{acc_med:.0f}%** | صعب: **{acc_hard:.0f}%**")

    # لوحة المتصدرين
    finish_round()
    st.subheader("🏆 لوحة المتصدرين (Top 10)")
    for i, r in enumerate(ss.leaderboard, 1):
        st.write(f"{i}. {r['name']} — {r['score']} نقطة ({r['mode']}) — {r['date']}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 إعادة اللعب — نفس الإعدادات", use_container_width=True):
            select_pool(); next_question()
            ss.score = 0; ss.streak = 0; ss.best_streak = 0
            ss.history=[]; ss.answer_times=[]
            ss.used_hint=0; ss.used_5050=False
            if ss.global_timer_on: ss.global_start = time.time()
            st.rerun()
    with c2:
        if st.button("🧰 إعدادات جديدة", use_container_width=True):
            # رجوع للبداية
            for k in ["player","pool","idx","history","answer_times"]:
                ss[k] = defaults[k]
            ss.score=0; ss.streak=0; ss.best_streak=0
            ss.used_hint=0; ss.used_5050=False
            ss.global_timer_on=False; ss.global_start=None
            st.rerun()
