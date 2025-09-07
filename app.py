# app.py
import streamlit as st
import random, time, json
from pathlib import Path
from datetime import datetime

# ------------- Page setup -------------
st.set_page_config(page_title="Ultimate Trivia Game", page_icon="🎮", layout="centered")

# ------------- Neon animated background + UI style -------------
CSS = """
<style>
.stApp {
  background: linear-gradient(-45deg, #1e3c72, #2a5298, #0f2027, #203a43, #2c5364);
  background-size: 400% 400%;
  animation: gradient 18s ease infinite;
}
@keyframes gradient {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}
.block-container{
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 1.1rem;
}
h1,h2,h3,h4,h5,h6,p,span,div,label { color: #fff !important; }
.stButton>button, .stDownloadButton>button {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.10);
  padding: .6rem .9rem;
}
.stButton>button:hover, .stDownloadButton>button:hover { background: rgba(255,255,255,0.18); }
.timer-badge {
  display:inline-block; padding: .35rem .75rem;
  background: rgba(0, 200, 255, .15);
  border: 1px solid rgba(0, 200, 255, .4);
  border-radius: 999px; font-weight: 700;
}
.q-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 14px; padding: 1rem 1.1rem; margin-bottom: .75rem;
  font-size: 1.05rem;
}
.choice-btn {
  width: 100%; text-align: left;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08);
  padding: 0.7rem 1rem; margin-bottom: .6rem;
}
.choice-btn:hover { background: rgba(255,255,255,0.18); }
.small-note { opacity: .85; font-size: .92rem; }
@media (max-width: 480px) { .block-container{ padding: .9rem; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------- Sounds -------------
SND_CORRECT = "https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"
SND_WRONG   = "https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg"
SND_TIMEOUT = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"

def play(url:str):
    if not st.session_state.sounds_on: return
    st.markdown(f"""<audio autoplay style="display:none"><source src="{url}"></audio>""", unsafe_allow_html=True)

# ------------- Language packs -------------
T = {
    "en": {
        "title": "🎮 Ultimate Trivia Game",
        "enter_name": "✨ Enter your name to start",
        "difficulty": "🎯 Difficulty",
        "mix": "Mix", "easy": "easy", "medium": "medium", "hard": "hard",
        "num_q": "🧩 Number of questions",
        "per_q": "⏳ Time per question (sec)",
        "global_timer": "⏱️ Global round timer",
        "global_limit": "⌛ Round total time (sec)",
        "sound": "🔊 Sounds",
        "start": "🚀 Start",
        "player": "👤 Player", "score": "🏅 Score", "streak": "🔥 Streak",
        "time_left": "⏳ Time left",
        "round_left": "⏱️ Round left",
        "hint": "💡 Hint", "fifty": "🎯 50/50", "skip": "⏭️ Skip", "mute": "🔊/🔇 Toggle sound",
        "correct": "✅ Correct! Great job 👏",
        "wrong": "❌ Wrong! Correct answer:",
        "no_hint": "💡 No hint for this question.",
        "used_hint_max": "🚫 You already used 2 hints.",
        "used_5050": "🚫 50/50 already used.",
        "time_up": "⏰ Time is up!",
        "finished": "🎉 Well done {name}! Round finished.",
        "final_score": "🔢 Your final score: **{score}** of **{total}**",
        "report": "📊 Performance report",
        "acc": "Accuracy", "avg": "Avg time", "fastest": "Fastest", "slowest": "Slowest",
        "by_diff": "By difficulty → Easy: **{easy}%** | Medium: **{med}%** | Hard: **{hard}%**",
        "leaderboard": "🏆 Leaderboard (Top 10)",
        "restart_same": "🔄 Replay — same settings",
        "new_settings": "🧰 New settings",
        "lang": "🌍 Language", "lang_note": "Default is English. You can switch anytime.",
        "toggle_to_ar": "Switch to العربية",
        "toggle_to_en": "Switch to English",
    },
    "ar": {
        "title": "🎮 أفضل لعبة ألغاز",
        "enter_name": "✨ اكتب اسمك للبدء",
        "difficulty": "🎯 اختر المستوى",
        "mix": "Mix", "easy": "easy", "medium": "medium", "hard": "hard",
        "num_q": "🧩 عدد الأسئلة",
        "per_q": "⏳ وقت لكل سؤال (ث)",
        "global_timer": "⏱️ مؤقت عام للجولة",
        "global_limit": "⌛ زمن الجولة الكلي (ث)",
        "sound": "🔊 الصوت",
        "start": "🚀 ابدأ",
        "player": "👤 اللاعب", "score": "🏅 النقاط", "streak": "🔥 السلسلة",
        "time_left": "⏳ الوقت المتبقي",
        "round_left": "⏱️ المتبقي للجولة",
        "hint": "💡 تلميح", "fifty": "🎯 50/50", "skip": "⏭️ تخطي", "mute": "🔊/🔇 تبديل الصوت",
        "correct": "✅ إجابة صحيحة! ممتاز 👏",
        "wrong": "❌ خطأ! الجواب الصحيح:",
        "no_hint": "💡 هذا السؤال ما عندوش تلميح.",
        "used_hint_max": "🚫 استعملت تلميحين بالفعل.",
        "used_5050": "🚫 استعملت 50/50 من قبل.",
        "time_up": "⏰ انتهى الوقت!",
        "finished": "🎉 مبروك {name}! أنهيت الجولة.",
        "final_score": "🔢 نتيجتك النهائية: **{score}** من **{total}**",
        "report": "📊 تقرير الأداء",
        "acc": "الدقة", "avg": "متوسط الزمن", "fastest": "الأسرع", "slowest": "الأبطأ",
        "by_diff": "حسب الصعوبة → سهل: **{easy}%** | متوسط: **{med}%** | صعب: **{hard}%**",
        "leaderboard": "🏆 لوحة المتصدرين (Top 10)",
        "restart_same": "🔄 إعادة اللعب — نفس الإعدادات",
        "new_settings": "🧰 إعدادات جديدة",
        "lang": "🌍 اللغة", "lang_note": "الافتراضية الإنجليزية. تقدر تبدّل في أي وقت.",
        "toggle_to_ar": "التبديل إلى العربية",
        "toggle_to_en": "التبديل إلى English",
    }
}

# ------------- Load questions (external or default) -------------
DEFAULT_EN = [
    {"question":"What color is the sky on a clear day?","options":["Red","Blue","Green","Black"],"answer":"Blue","difficulty":"easy","hint":"Rayleigh scattering!"},
    {"question":"How many legs does a spider have?","options":["6","8","10","12"],"answer":"8","difficulty":"easy","hint":"More than an insect."},
    {"question":"Capital of Algeria?","options":["Oran","Algiers","Constantine","Setif"],"answer":"Algiers","difficulty":"easy"},
    {"question":"How many sides does a triangle have?","options":["2","3","4","5"],"answer":"3","difficulty":"easy"},
    {"question":"Closest planet to the Sun?","options":["Jupiter","Earth","Mercury","Venus"],"answer":"Mercury","difficulty":"easy"},
    {"question":"Which is the Red Planet?","options":["Venus","Mars","Jupiter","Saturn"],"answer":"Mars","difficulty":"medium"},
    {"question":"How many continents are there?","options":["5","6","7","8"],"answer":"7","difficulty":"medium"},
    {"question":"Where is the Eiffel Tower?","options":["Rome","Paris","London","Madrid"],"answer":"Paris","difficulty":"medium"},
    {"question":"Unit of electrical power?","options":["Volt","Ohm","Watt","Ampere"],"answer":"Watt","difficulty":"medium","hint":"P = V × I"},
    {"question":"Largest ocean?","options":["Atlantic","Indian","Arctic","Pacific"],"answer":"Pacific","difficulty":"medium"},
    {"question":"Year of Algerian Revolution?","options":["1952","1954","1962","1945"],"answer":"1954","difficulty":"hard"},
    {"question":"Fastest land animal?","options":["Gazelle","Cheetah","Lion","Tiger"],"answer":"Cheetah","difficulty":"hard"},
    {"question":"Element with symbol Fe?","options":["Gold","Copper","Iron","Zinc"],"answer":"Iron","difficulty":"hard"},
    {"question":"Heaviest planet?","options":["Jupiter","Saturn","Neptune","Earth"],"answer":"Jupiter","difficulty":"hard"},
    {"question":"Largest desert?","options":["Sahara","Gobi","Kalahari","Australia"],"answer":"Sahara","difficulty":"hard"},
]
DEFAULT_AR = [
    {"question":"ما لون السماء في يوم صافٍ؟","options":["أحمر","أزرق","أخضر","أسود"],"answer":"أزرق","difficulty":"easy","hint":"تشتّت رايلي."},
    {"question":"كم عدد أرجل العنكبوت؟","options":["6","8","10","12"],"answer":"8","difficulty":"easy","hint":"أكثر من الحشرة."},
    {"question":"ما عاصمة الجزائر؟","options":["وهران","الجزائر العاصمة","قسنطينة","سطيف"],"answer":"الجزائر العاصمة","difficulty":"easy"},
    {"question":"كم أضلاع المثلث؟","options":["2","3","4","5"],"answer":"3","difficulty":"easy"},
    {"question":"أقرب كوكب للشمس؟","options":["المشتري","الأرض","عطارد","الزهرة"],"answer":"عطارد","difficulty":"easy"},
    {"question":"ما هو الكوكب الأحمر؟","options":["الزهرة","المريخ","المشتري","زحل"],"answer":"المريخ","difficulty":"medium"},
    {"question":"كم عدد قارات العالم؟","options":["5","6","7","8"],"answer":"7","difficulty":"medium"},
    {"question":"أين يقع برج إيفل؟","options":["روما","باريس","لندن","مدريد"],"answer":"باريس","difficulty":"medium"},
    {"question":"وحدة قياس القدرة؟","options":["فولت","أوم","واط","أمبير"],"answer":"واط","difficulty":"medium","hint":"P = V × I"},
    {"question":"أكبر محيط؟","options":["الأطلسي","الهندي","المتجمد","الهادي"],"answer":"الهادي","difficulty":"medium"},
    {"question":"سنة اندلاع الثورة الجزائرية؟","options":["1952","1954","1962","1945"],"answer":"1954","difficulty":"hard"},
    {"question":"أسرع حيوان بري؟","options":["الغزال","الفهد","الأسد","النمر"],"answer":"الفهد","difficulty":"hard"},
    {"question":"العنصر Fe؟","options":["الذهب","النحاس","الحديد","الزنك"],"answer":"الحديد","difficulty":"hard"},
    {"question":"أثقل كوكب؟","options":["المشتري","زحل","نبتون","الأرض"],"answer":"المشتري","difficulty":"hard"},
    {"question":"أكبر صحراء؟","options":["الكبرى","غوبي","كالاهاري","أستراليا"],"answer":"الصحراء الكبرى","difficulty":"hard"},
]

def load_bank(lang):
    p = Path(f"questions_{lang}.json")
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_EN if lang=="en" else DEFAULT_AR

# ------------- Session state -------------
ss = st.session_state
defaults = {
    "lang": "en",               # default English
    "player": None,
    "sounds_on": True,
    "difficulty": "Mix",
    "num_questions": 10,
    "perq_limit": 15,
    "global_timer_on": False,
    "global_limit": 180,
    "global_start": None,
    "pool": [],
    "idx": -1,
    "score": 0,
    "streak": 0,
    "best_streak": 0,
    "question_start": None,
    "hidden_options": set(),
    "used_hint": 0,
    "used_5050": False,
    "leaderboard": [],
    "history": [],
    "answer_times": []
}
for k,v in defaults.items():
    if k not in ss: ss[k] = v

# ------------- Helpers -------------
def L(key, **kw):
    return T[ss.lang][key].format(**kw) if kw else T[ss.lang][key]

def time_per_diff(diff):
    return 20 if diff=="easy" else 15 if diff=="medium" else 12 if diff=="hard" else 15

def build_pool():
    bank = load_bank(ss.lang)
    if ss.difficulty == "Mix":
        pool = bank[:]
    else:
        pool = [q for q in bank if q.get("difficulty","easy")==ss.difficulty]
    random.shuffle(pool)
    n = min(ss.num_questions, len(pool))
    ss.pool = pool[:n]
    ss.idx = -1

def next_q():
    ss.idx += 1
    ss.hidden_options = set()
    ss.question_start = time.time()

def cur_q():
    if 0 <= ss.idx < len(ss.pool):
        return ss.pool[ss.idx]
    return None

def accuracy(items):
    if not items: return 0.0
    return 100.0 * sum(1 for _,ok,_ in items)/len(items)

def acc_for(level):
    subset = [ok for d,ok,_ in ss.history if d==level]
    return (100*sum(subset)/len(subset)) if subset else 0

# ------------- Header (title + language toggle) -------------
left, mid, right = st.columns([1,2,1])
with mid: st.title(L("title"))
with right:
    if st.button(("🇸🇦 "+L("toggle_to_ar")) if ss.lang=="en" else ("🇬🇧 "+L("toggle_to_en"))):
        ss.lang = "ar" if ss.lang=="en" else "en"
        st.rerun()

# ------------- Start screen -------------
if not ss.player:
    name = st.text_input(L("enter_name"), value="")
    c1, c2 = st.columns(2)
    with c1:
        diff = st.selectbox(L("difficulty"), [L("mix"), L("easy"), L("medium"), L("hard")], index=0)
        sounds = st.toggle(L("sound"), value=True)
    with c2:
        # map localized labels back to internal keys
        rev = {L("mix"):"Mix", L("easy"):"easy", L("medium"):"medium", L("hard"):"hard"}
        max_n = len(load_bank(ss.lang)) if rev[diff]=="Mix" else len([q for q in load_bank(ss.lang) if q.get("difficulty")==rev[diff]])
        max_n = max(5, max_n)
        num = st.slider(L("num_q"), 5, min(100, max_n), value=min(10, max_n))
        perq = st.slider(L("per_q"), 8, 40, time_per_diff(rev[diff]))

    g_on = st.toggle(L("global_timer"), value=False)
    g_lim = st.slider(L("global_limit"), 60, 900, 180, disabled=not g_on)
    st.caption(f"**{L('lang')}** — {L('lang_note')}")

    if st.button(L("start")):
        if name.strip():
            ss.player = name.strip()
            ss.sounds_on = sounds
            ss.difficulty = rev[diff]
            ss.num_questions = num
            ss.perq_limit = perq
            ss.score = 0; ss.streak = 0; ss.best_streak = 0
            ss.history = []; ss.answer_times = []
            ss.used_hint = 0; ss.used_5050 = False
            build_pool(); next_q()
            if g_on:
                ss.global_timer_on = True
                ss.global_limit = g_lim
                ss.global_start = time.time()
            else:
                ss.global_timer_on = False
                ss.global_start = None
            st.rerun()
        else:
            st.warning("⚠️" + (" Please enter a valid name." if ss.lang=="en" else " أدخل اسم صالح."))
    st.stop()

# ------------- Top info bar -------------
total = len(ss.pool)
answered = max(0, ss.idx)
st.progress(answered/total if total else 0.0, text=f"{answered}/{total}")

# per-question timer
if ss.question_start:
    elapsed_q = int(time.time() - ss.question_start)
    remain_q = max(0, ss.perq_limit - elapsed_q)
else:
    remain_q = ss.perq_limit

# global timer
if ss.global_timer_on and ss.global_start:
    elapsed_g = int(time.time() - ss.global_start)
    remain_g = max(0, ss.global_limit - elapsed_g)
else:
    remain_g = None

top = st.container()
with top:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(L("player"), ss.player)
    c2.metric(L("score"), ss.score)
    c3.metric(L("streak"), ss.streak)
    badge = f"<span class='timer-badge'>{('⏱️ ' + str(remain_g) + 's') if remain_g is not None else ('⏳ ' + str(remain_q) + 's')}</span>"
    c4.markdown(badge, unsafe_allow_html=True)

# auto refresh every second while timers running
if cur_q() and (remain_q > 0) and (remain_g is None or remain_g > 0):
    st.markdown("<script>setTimeout(()=>window.parent.location.reload(),1000);</script>", unsafe_allow_html=True)

# timeouts
if cur_q() and remain_q == 0:
    st.warning(L("time_up"))
    play(SND_TIMEOUT)
    q = cur_q()
    spent = ss.perq_limit
    ss.history.append((q.get("difficulty","easy"), False, spent))
    ss.answer_times.append(spent)
    ss.streak = 0
    next_q(); st.rerun()

if cur_q() and ss.global_timer_on and remain_g == 0:
    st.error(L("time_up"))
    ss.idx = len(ss.pool)
    st.rerun()

# ------------- Question UI -------------
q = cur_q()
if q:
    st.markdown(f"<div class='q-card'>❓ {q['question']}</div>", unsafe_allow_html=True)

    visible = [o for o in q["options"] if o not in ss.hidden_options]

    # render choices as buttons (no white radios)
    for opt in visible:
        if st.button(opt, key=f"opt_{ss.idx}_{opt}", use_container_width=True):
            spent = int(time.time() - ss.question_start) if ss.question_start else 0
            if opt == q["answer"]:
                st.success(L("correct"))
                play(SND_CORRECT)
                pts = 1 if q.get("difficulty")=="easy" else 2 if q.get("difficulty")=="medium" else 3
                if spent <= 5: pts += 1  # speed bonus
                ss.score += pts
                ss.streak += 1
                ss.best_streak = max(ss.best_streak, ss.streak)
                ss.history.append((q.get("difficulty","easy"), True, spent))
                ss.answer_times.append(spent)
                st.balloons()
            else:
                st.error(f"{L('wrong')} **{q['answer']}**")
                play(SND_WRONG)
                ss.streak = 0
                ss.history.append((q.get("difficulty","easy"), False, spent))
                ss.answer_times.append(spent)

            time.sleep(0.6)
            next_q(); st.rerun()

    cA, cB, cC, cD = st.columns(4)
    with cA:
        if st.button(L("hint"), use_container_width=True):
            if ss.used_hint >= 2:
                st.warning(T[ss.lang]["used_hint_max"])
            else:
                msg = q.get("hint")
                if msg:
                    st.info(f"💡 {msg}")
                    ss.used_hint += 1
                else:
                    st.info(T[ss.lang]["no_hint"])
    with cB:
        if st.button(L("fifty"), use_container_width=True):
            if ss.used_5050:
                st.warning(T[ss.lang]["used_5050"])
            else:
                wrongs = [o for o in q["options"] if o != q["answer"]]
                hide = set(random.sample(wrongs, k=min(2, len(wrongs))))
                ss.hidden_options |= hide
                ss.used_5050 = True
                st.rerun()
    with cC:
        if st.button(L("skip"), use_container_width=True):
            spent = int(time.time() - ss.question_start) if ss.question_start else 0
            ss.history.append((q.get("difficulty","easy"), False, spent))
            ss.answer_times.append(spent)
            ss.streak = 0
            next_q(); st.rerun()
    with cD:
        if st.button(L("mute"), use_container_width=True):
            ss.sounds_on = not ss.sounds_on; st.rerun()

else:
    # ------------- End screen -------------
    st.success(T[ss.lang]["finished"].format(name=ss.player))
    st.write(T[ss.lang]["final_score"].format(score=ss.score, total=total))

    # stats
    if ss.answer_times:
        avg = sum(ss.answer_times)/len(ss.answer_times)
        fastest = min(ss.answer_times)
        slowest = max(ss.answer_times)
    else:
        avg = fastest = slowest = 0
    total_correct = sum(1 for _,ok,_ in ss.history if ok)
    acc_all = accuracy(ss.history)
    acc_easy = acc_for("easy"); acc_med = acc_for("medium"); acc_hard = acc_for("hard")

    st.subheader(L("report"))
    st.write(f"- ✅ {L('acc')}: **{acc_all:.1f}%**")
    st.write(f"- ⏱️ {L('avg')}: **{avg:.1f}s** — {L('fastest')}: **{fastest}s** | {L('slowest')}: **{slowest}s**")
    st.write(f"- 🔥 {L('streak')}: **{ss.best_streak}**")
    st.write("– " + T[ss.lang]["by_diff"].format(easy=int(acc_easy), med=int(acc_med), hard=int(acc_hard)))

    # leaderboard (session)
    ss.leaderboard.append({
        "name": ss.player, "score": ss.score, "mode": ss.difficulty,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    ss.leaderboard = sorted(ss.leaderboard, key=lambda r: r["score"], reverse=True)[:10]

    st.subheader(L("leaderboard"))
    for i, r in enumerate(ss.leaderboard, 1):
        st.write(f"{i}. {r['name']} — {r['score']} ({r['mode']}) — {r['date']}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button(L("restart_same"), use_container_width=True):
            build_pool(); next_q()
            ss.score=0; ss.streak=0; ss.best_streak=0
            ss.history=[]; ss.answer_times=[]
            ss.used_hint=0; ss.used_5050=False
            if ss.global_timer_on: ss.global_start = time.time()
            st.rerun()
    with c2:
        if st.button(L("new_settings"), use_container_width=True):
            # reset to start
            for key in ["player","pool","idx","history","answer_times"]:
                ss[key] = defaults[key]
            ss.score=0; ss.streak=0; ss.best_streak=0
            ss.used_hint=0; ss.used_5050=False
            ss.global_timer_on=False; ss.global_start=None
            st.rerun()
