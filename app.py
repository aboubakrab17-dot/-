import streamlit as st
import json, random, time

# -------------------- إعدادات عامة للصفحة --------------------
st.set_page_config(page_title="لعبة الألغاز | Quiz Master", layout="wide")

# -------------------- CSS: خلفية، أزرار، عناصر --------------------
APP_CSS = """
<style>
/* خلفية */
[data-testid="stAppViewContainer"]{
  background-image:url("https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1920&auto=format&fit=crop");
  background-size:cover; background-position:center; background-attachment:fixed;
}
/* صندوق المحتوى */
.block-container{
  background:rgba(0,0,0,0.55); border-radius:20px; padding:24px; color:#fff;
}
/* العناوين */
h1,h2,h3,h4{ color:#fff !important; }
/* الأزرار */
.stButton>button{
  background:#222; color:#fff; border-radius:12px; padding:10px 18px; border:1px solid #444;
}
.stButton>button:hover{ background:#3a3a3a; }
/* الراديو */
.stRadio>div{ background:rgba(0,0,0,0.4); padding:10px 14px; border-radius:12px; }
/* المتركس */
[data-testid="stMetricValue"]{ color:#fff; }
/* التلميح */
.alert-hint{
  background:rgba(255,255,255,0.08); border:1px dashed #7dd3fc; padding:10px 14px; border-radius:12px;
}
/* فواصل جميلة */
.hr{ height:1px; background:linear-gradient(90deg,transparent,#999,transparent); margin:10px 0 18px; }
.badge{ display:inline-block; background:#0ea5e9; color:white; padding:3px 8px; border-radius:999px; font-size:12px; }
.counter{ font-weight:700; }
.timer {
  font-size:18px; font-weight:700; color:#facc15;
}
.options-grid { display:grid; grid-template-columns: 1fr; gap:10px; }
@media(min-width:768px){ .options-grid{ grid-template-columns: 1fr 1fr; } }
.opt-btn{
  width:100%; border:1px solid #555; background:#111; color:#fff; border-radius:12px; padding:12px 14px;
}
.opt-btn:hover{ background:#1f2937; border-color:#777; }
.correct{ background:#065f46 !important; border-color:#10b981 !important; }
.wrong{ background:#7f1d1d !important; border-color:#ef4444 !important; }
.footer-note{ color:#e5e7eb; font-size:12px; opacity:.85; }
.lang-chip{ background:#111; border:1px solid #444; border-radius:999px; padding:6px 10px; color:#fff; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# -------------------- نصوص واجهة باللغتين --------------------
UI = {
    "ar": {
        "title": "🧩 لعبة الألغاز - إصدار محترف",
        "start": "▶️ ابدأ اللعبة",
        "next": "➡️ سؤال آخر",
        "confirm": "✅ تأكيد الإجابة",
        "hint": "💡 تلميح",
        "score": "النقاط",
        "streak": "السلسلة",
        "time_left": "الوقت المتبقي",
        "time_up": "⏰ انتهى الوقت!",
        "game_over": "🎉 انتهت اللعبة! نتيجتك",
        "choose": "اختر الإجابة:",
        "right": "🎯 صحيح!",
        "wrong": "❌ خطأ! الجواب الصحيح:",
        "settings": "⚙️ إعدادات",
        "lang": "اللغة",
        "lang_ar": "العربية",
        "lang_en": "English",
        "count": "عدد الأسئلة",
        "per_q_sec": "⏳ وقت لكل سؤال (ثواني)",
        "sound": "🔊 المؤثرات الصوتية",
        "mix": "ترتيب عشوائي للأسئلة",
        "name": "👤 اسم اللاعب (اختياري)",
        "hint_used": "تم استعمال التلميح",
        "no_more": "لا توجد أسئلة أخرى.",
        "restart": "🔄 إعادة اللعب",
        "leader": "🏆 لوحة المتصدرين (محلية)",
        "your_name": "اسمك",
        "save_score": "💾 حفظ نتيجتي",
        "saved": "✅ تم حفظ نتيجتك محليًا.",
        "total": "المجموع",
        "sec": "ثانية",
        "question": "سؤال"
    },
    "en": {
        "title": "🧩 Pro Quiz Game",
        "start": "▶️ Start Game",
        "next": "➡️ Next Question",
        "confirm": "✅ Confirm",
        "hint": "💡 Hint",
        "score": "Score",
        "streak": "Streak",
        "time_left": "Time left",
        "time_up": "⏰ Time is up!",
        "game_over": "🎉 Game Over! Your score",
        "choose": "Choose an answer:",
        "right": "🎯 Correct!",
        "wrong": "❌ Wrong! Correct answer:",
        "settings": "⚙️ Settings",
        "lang": "Language",
        "lang_ar": "العربية",
        "lang_en": "English",
        "count": "Number of questions",
        "per_q_sec": "⏳ Time per question (sec)",
        "sound": "🔊 Sound effects",
        "mix": "Shuffle questions",
        "name": "👤 Player name (optional)",
        "hint_used": "Hint used",
        "no_more": "No more questions.",
        "restart": "🔄 Restart",
        "leader": "🏆 Leaderboard (Local)",
        "your_name": "Your name",
        "save_score": "💾 Save my score",
        "saved": "✅ Your score is saved locally.",
        "total": "Total",
        "sec": "sec",
        "question": "Question"
    }
}

# -------------------- حالة الجلسة --------------------
def init_state():
    defaults = {
        "lang": "ar",
        "questions": [],
        "order": [],
        "idx": 0,
        "score": 0,
        "streak": 0,
        "show_hint": False,
        "selected": None,
        "answered": False,
        "deadline": None,
        "per_q_sec": 20,
        "count": 10,
        "sound": True,
        "shuffle": True,
        "player": "",
        "leaderboard": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
T = UI[st.session_state["lang"]]

# -------------------- تحميل الأسئلة --------------------
@st.cache_data(show_spinner=False)
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # يرجّع dict فيه قائمتين en/ar
    return data

DATA = load_questions()

def get_lang_key(base, lang):
    # يبني مفتاح السؤال حسب اللغة
    return f"{base}_{lang}"

def build_pool(lang):
    pool = []
    for q in DATA[lang]:
        pool.append(q)
    return pool

# تهيئة الأسئلة حسب الإعدادات
def prepare_game():
    st.session_state["questions"] = build_pool(st.session_state["lang"])
    if st.session_state["shuffle"]:
        random.shuffle(st.session_state["questions"])
    st.session_state["order"] = list(range(min(st.session_state["count"], len(st.session_state["questions"]))))
    st.session_state["idx"] = 0
    st.session_state["score"] = 0
    st.session_state["streak"] = 0
    st.session_state["show_hint"] = False
    st.session_state["selected"] = None
    st.session_state["answered"] = False
    st.session_state["deadline"] = None

# -------------------- مؤثرات صوتية --------------------
SND_CORRECT = "https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"
SND_WRONG   = "https://actions.google.com/sounds/v1/cartoon/boing.ogg"

def play_sound(url):
    if st.session_state["sound"]:
        st.audio(url)

# -------------------- رأس الصفحة --------------------
left, mid, right = st.columns([1,2,1])
with left:
    if st.button("🇸🇦" if st.session_state["lang"] == "en" else "🇬🇧"):
        st.session_state["lang"] = "ar" if st.session_state["lang"] == "en" else "en"
        T = UI[st.session_state["lang"]]
        prepare_game()
with mid:
    st.markdown(f"<h1 style='text-align:center'>{T['title']}</h1>", unsafe_allow_html=True)
with right:
    st.markdown(f"<div class='badge'>{T['lang']}: {T['lang_ar'] if st.session_state['lang']=='ar' else T['lang_en']}</div>", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -------------------- الشريط الجانبي: إعدادات + لوحة متصدرين --------------------
with st.sidebar:
    st.subheader(T["settings"])
    st.session_state["player"] = st.text_input(T["name"], value=st.session_state["player"])
    st.session_state["count"] = st.slider(T["count"], 5, 50, st.session_state["count"])
    st.session_state["per_q_sec"] = st.slider(T["per_q_sec"], 5, 90, st.session_state["per_q_sec"])
    st.session_state["sound"] = st.checkbox(T["sound"], value=st.session_state["sound"])
    st.session_state["shuffle"] = st.checkbox(T["mix"], value=st.session_state["shuffle"])

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader(T["leader"])
    name_to_save = st.text_input(T["your_name"], key="lb_name")
    if st.button(T["save_score"]):
        if name_to_save.strip():
            st.session_state["leaderboard"].append(
                {"name": name_to_save.strip(), "score": st.session_state["score"], "total": len(st.session_state["order"])}
            )
            st.success(T["saved"])
        else:
            st.warning("⚠️ أدخل اسمًا صالحًا" if st.session_state["lang"]=="ar" else "⚠️ Enter a valid name")
    # عرض أبسط لوحة
    if st.session_state["leaderboard"]:
        st.table(st.session_state["leaderboard"])

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -------------------- زر بدء/إعادة --------------------
cols = st.columns([1,1,1,1])
with cols[0]:
    if st.button(T["start"]):
        prepare_game()
        st.session_state["deadline"] = time.time() + st.session_state["per_q_sec"]

with cols[1]:
    if st.button(T["restart"]):
        prepare_game()

# -------------------- عرض النقاط + السلسلة + المؤقت --------------------
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(T["score"], st.session_state["score"])
with m2:
    st.metric(T["streak"], st.session_state["streak"])
with m3:
    # مؤقت حي يعتمد على موعد نهائي (deadline)
    if st.session_state["deadline"]:
        remaining = int(max(0, st.session_state["deadline"] - time.time()))
        st.markdown(f"<div class='timer'>⏳ {T['time_left']}: <span class='counter'>{remaining}</span> {T['sec'] if st.session_state['lang']=='ar' else T['sec']}</div>", unsafe_allow_html=True)
        # تحديث كل ثانية
        st.experimental_set_query_params(t=str(int(time.time())))  # force change
        st.autorefresh = st.experimental_rerun if remaining == 0 else None

# -------------------- المنطق الرئيسي لعرض السؤال --------------------
def get_current_question():
    if not st.session_state["order"]:
        return None
    if st.session_state["idx"] >= len(st.session_state["order"]):
        return None
    q = st.session_state["questions"][st.session_state["order"][st.session_state["idx"]]]
    return q

q = get_current_question()

if not q:
    # نهاية اللعبة
    st.success(f"{T['game_over']}: {st.session_state['score']} / {len(st.session_state['order'])}")
    st.stop()

# نصوص حسب اللغة
lang = st.session_state["lang"]
q_text   = q[f"question_{lang}"]
opts     = q[f"options_{lang}"]
answer   = q[f"answer_{lang}"]
hint_txt = q[f"hint_{lang}"]

# عنوان السؤال + عدّاد الأسئلة
top_a, top_b = st.columns([3,1])
with top_a:
    st.subheader(f"{T['question']} {st.session_state['idx']+1}/{len(st.session_state['order'])} — {q_text}")
with top_b:
    st.markdown(f"<div class='badge'>{T['total']}: {len(st.session_state['order'])}</div>", unsafe_allow_html=True)

st.write("")  # مسافة

# شبكة خيارات (أزرار) مع تلوين بعد التأكيد
if "answered" not in st.session_state:
    st.session_state["answered"] = False

# اختيار المستخدم
if st.session_state["selected"] not in opts:
    st.session_state["selected"] = None

def pick(opt):
    st.session_state["selected"] = opt

# عرض الخيارات كأزرار شبكية
st.markdown("<div class='options-grid'>", unsafe_allow_html=True)
btn_cols = st.columns(2)
for i, opt in enumerate(opts):
    col = btn_cols[i % 2]
    with col:
        classes = "opt-btn"
        if st.session_state["answered"]:
            if opt == answer:
                classes += " correct"
            elif opt == st.session_state["selected"] and opt != answer:
                classes += " wrong"
        clicked = st.button(opt, key=f"opt_{st.session_state['idx']}_{i}")
        if clicked and not st.session_state["answered"]:
            pick(opt)
st.markdown("</div>", unsafe_allow_html=True)

# تلميح
hcol1, hcol2, hcol3 = st.columns([1,1,1])
with hcol1:
    if st.button(T["hint"]):
        st.session_state["show_hint"] = True
with hcol2:
    pass
with hcol3:
    pass

if st.session_state["show_hint"]:
    st.markdown(f"<div class='alert-hint'>💡 {hint_txt}</div>", unsafe_allow_html=True)

st.write("")
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# تأكيد الإجابة
cc1, cc2 = st.columns([1,1])
with cc1:
    if st.button(T["confirm"]):
        if st.session_state["selected"] is None:
            st.warning("⚠️ اختر إجابة أولاً" if lang=="ar" else "⚠️ Please select an option")
        else:
            st.session_state["answered"] = True
            if st.session_state["selected"] == answer:
                st.success(T["right"])
                play_sound(SND_CORRECT)
                st.session_state["score"] += 1
                st.session_state["streak"] += 1
            else:
                st.error(f"{T['wrong']} {answer}")
                play_sound(SND_WRONG)
                st.session_state["streak"] = 0

with cc2:
    if st.button(T["next"]):
        # انتقال للسؤال التالي
        st.session_state["idx"] += 1
        st.session_state["show_hint"] = False
        st.session_state["selected"] = None
        st.session_state["answered"] = False
        st.session_state["deadline"] = time.time() + st.session_state["per_q_sec"]
        st.experimental_rerun()

# إدارة انتهاء الوقت
if st.session_state["deadline"]:
    remaining = st.session_state["deadline"] - time.time()
    if remaining <= 0 and not st.session_state["answered"]:
        st.warning(T["time_up"])
        play_sound(SND_WRONG)
        st.session_state["streak"] = 0
        # أظهر الإجابة الصحيحة
        st.info((T["wrong"] + " " + answer) if lang=="ar" else (T["wrong"] + " " + answer))
        # جهّز للسؤال التالي
        st.session_state["answered"] = True
