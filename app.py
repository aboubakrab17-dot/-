# app.py
# لعبة ألغاز عربية - نسخة مبسطة ومستقرة (ملف واحد)
# متطلبات: streamlit
# تشغيل محلي: streamlit run app.py

import streamlit as st
import random, time, json
from pathlib import Path
from copy import deepcopy

# ---------------- page config & CSS ----------------
st.set_page_config(page_title="لعبة الألغاز 🎯", page_icon="🧩", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {font-family: 'Cairo', sans-serif;}
:root {
  --bg1: #0b1220;
  --bg2: #132433;
  --card: rgba(255,255,255,0.02);
  --accent: #ffb86b;
  --accent2: #6be7ff;
  --muted: #c6e7f5;
}
[data-testid="stAppViewContainer"]{
  background: radial-gradient(800px 300px at 10% 10%, rgba(107,231,255,0.04), transparent 10%),
              radial-gradient(700px 300px at 90% 30%, rgba(255,184,107,0.03), transparent 12%),
              linear-gradient(180deg,var(--bg1),var(--bg2));
  color: #e9fbff;
}
.header {text-align:center; margin-bottom:6px;}
.title {font-size:34px; font-weight:700; color:var(--accent);}
.subtitle {color:var(--muted); margin-bottom:12px;}

/* card */
.card {background:var(--card); padding:14px; border-radius:12px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); margin-bottom:12px;}
.btn-wide>button{width:100%; background: linear-gradient(90deg,var(--accent),#ff7b7b); color:#071226; font-weight:700; padding:10px 12px; border-radius:10px;}
.timer {display:inline-block; padding:6px 10px; border-radius:999px; font-weight:700; color:#071226; background:linear-gradient(90deg,var(--accent2),#00ffa8);}
.progress-wrap {background: rgba(255,255,255,0.03); height:10px; border-radius:999px; overflow:hidden; margin-top:8px;}
.progress-bar {height:10px; background: linear-gradient(90deg,var(--accent2),var(--accent)); width:0%; transition: width .2s linear;}
.question {font-size:20px; font-weight:700; margin-bottom:10px; color:#ffffff;}
.small {color:var(--muted);}
.option {background: rgba(255,255,255,0.02); padding:12px; border-radius:10px; margin:8px 0;}
.leader {padding:8px; background: rgba(255,255,255,0.02); border-radius:8px; margin-bottom:6px;}
</style>
""", unsafe_allow_html=True)

# ---------------- sounds (اختياري: روابط أو ضع "" لتعطيل) ----------------
SOUND_CORRECT = ""   # مثال: "https://actions.google.com/sounds/v1/human_voices/applause.ogg"
SOUND_WRONG = ""
SOUND_TIMEOUT = ""

# ---------------- load optional questions.json ----------------
BASE = Path(__file__).parent
QUESTIONS_FILE = BASE / "questions.json"

def load_questions_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cleaned = []
        for i, e in enumerate(data):
            if not isinstance(e, dict):
                continue
            q = e.get("question") or e.get("q")
            options = e.get("options") or e.get("choices")
            answer = e.get("answer")
            hint = e.get("hint", "")
            level = e.get("level", "متوسط")
            if q and isinstance(options, list) and answer in options:
                cleaned.append({"id": i+1, "question": str(q), "options": options, "answer": answer, "hint": hint, "level": level})
        return cleaned
    except Exception:
        return None

# ---------------- default Arabic questions (fallback) ----------------
DEFAULT_QUESTIONS = [
    {"id":1, "question":"ما عاصمة اليابان؟", "options":["طوكيو","أوساكا","ناغويا","سوبورو"], "answer":"طوكيو", "hint":"مدينة كبيرة في آسيا", "level":"ساهل"},
    {"id":2, "question":"ما هو الكوكب الأقرب إلى الشمس؟", "options":["عطارد","الزهره","الأرض","المريخ"], "answer":"عطارد", "hint":"اسمه يشبه اسم إله روماني", "level":"ساهل"},
    {"id":3, "question":"ما عدد الكواكب في النظام الشمسي (التقليدي)؟", "options":["8","9","7","10"], "answer":"8", "hint":"استُبعد بلوتو", "level":"ساهل"},
    {"id":4, "question":"ما هو أكبر حيوان بري؟", "options":["الفيل الإفريقي","الحوت الأزرق","الزرافة","التمساح"], "answer":"الفيل الإفريقي", "hint":"ضخم بأذنين كبيرتين", "level":"متوسط"},
    {"id":5, "question":"من مخترع المصباح الكهربائي (شائع)؟", "options":["توماس إديسون","ألكسندر بيك","غاليليو","نجاد"], "answer":"توماس إديسون", "hint":"مشهور في التاريخ الأمريكي", "level":"متوسط"},
    {"id":6, "question":"ما هو الرمز الكيميائي للماء؟", "options":["H2O","CO2","O2","NaCl"], "answer":"H2O", "hint":"مكون من الهيدروجين والأكسجين", "level":"ساهل"},
    {"id":7, "question":"أكبر قارة في العالم؟", "options":["آسيا","أفريقيا","أوروبا","أمريكا الجنوبية"], "answer":"آسيا", "hint":"تضم الصين والهند", "level":"ساهل"},
    {"id":8, "question":"من هو مؤلف مسرحية 'هاملت'؟", "options":["شكسبير","تولستوي","ديكنز","موليير"], "answer":"شكسبير", "hint":"شاعر ومسرحي إنجليزي", "level":"متوسط"},
    {"id":9, "question":"متى بدأت الحرب العالمية الأولى؟", "options":["1914","1939","1918","1920"], "answer":"1914", "hint":"قبل 1918", "level":"صعب"},
    {"id":10, "question":"ما وحدة قياس التيار الكهربائي؟", "options":["أمبير","فولت","واط","أوم"], "answer":"أمبير", "hint":"رمزها A", "level":"متوسط"},
    {"id":11, "question":"ما أصغر قارة من حيث المساحة؟", "options":["أستراليا","أوروبا","أمريكا الجنوبية","أفريقيا"], "answer":"أستراليا", "hint":"قارة وجزيرة كبيرة", "level":"متوسط"},
    {"id":12, "question":"ما هي لغة البرمجة المشهورة لصفحات الويب (الواجهة الأمامية)؟", "options":["JavaScript","Python","C++","Go"], "answer":"JavaScript", "hint":"تعمل في المتصفح", "level":"متوسط"},
    {"id":13, "question":"ما اسم أكبر محيط في العالم؟", "options":["المحيط الهادئ","المحيط الأطلسي","المحيط الهندي","المحيط المتجمد الشمالي"], "answer":"المحيط الهادئ", "hint":"يمتد بين آسيا وأمريكا", "level":"متوسط"},
    {"id":14, "question":"ما أسرع حيوان بري؟", "options":["الفهد","الأسد","النمر","الزرافة"], "answer":"الفهد", "hint":"يجرى بسرعة كبيرة", "level":"ساهل"},
    {"id":15, "question":"من هو مؤسس علم الجبر (المعروف)؟", "options":["الخوارزمي","ابن سينا","أرخميدس","إقليدس"], "answer":"الخوارزمي", "hint":"عالم رياضيات عربي", "level":"صعب"},
    {"id":16, "question":"ما اسم الغاز الذي نتنفسه بكثرة؟", "options":["النيتروجين","الأكسجين","ثاني أكسيد الكربون","الهيدروجين"], "answer":"النيتروجين", "hint":"يشكل معظم الهواء", "level":"متوسط"},
    {"id":17, "question":"ما هو العضو المسؤول عن ضخ الدم في الجسم؟", "options":["القلب","الرئة","الدماغ","الكبد"], "answer":"القلب", "hint":"عضو عضلي نابض", "level":"ساهل"},
    {"id":18, "question":"من هو أول من هبط على القمر؟", "options":["نيل أرمسترونغ","باز ألدرين","مايكل كولينز","يوحنا"], "answer":"نيل أرمسترونغ", "hint":"عام 1969", "level":"متوسط"},
    {"id":19, "question":"ما هي عملة اليابان؟", "options":["ين","دولار","يورو","جنيه"], "answer":"ين", "hint":"رمزها ¥", "level":"ساهل"},
    {"id":20, "question":"ما اسم العملية التي تحول النباتات الضوء لطاقة؟", "options":["التركيب الضوئي","التنفس","التخمر","التحلل"], "answer":"التركيب الضوئي", "hint":"تحتاج ضوء الشمس", "level":"متوسط"},
    {"id":21, "question":"في أي قارة تقع مصر؟", "options":["أفريقيا","آسيا","أوروبا","أمريكا"], "answer":"أفريقيا", "hint":"تقع جزئياً في آسيا (سيناء)", "level":"ساهل"},
    {"id":22, "question":"ما أعلى جبل في العالم؟", "options":["إيفرست","ك2","كانشندزنجا","ماكينلي"], "answer":"إيفرست", "hint":"يقع في جبال الهيمالايا", "level":"متوسط"},
    {"id":23, "question":"ما اسم أكبر قارة بحرية (حسب المساحة المائية حولها)؟", "options":["المحيط الهادئ","المحيط الأطلسي","المحيط الهندي","المحيط المتجمد الجنوبي"], "answer":"المحيط الهادئ", "hint":"أكبر محيط", "level":"صعب"},
    {"id":24, "question":"ما وحدة قياس المقاومة الكهربائية؟", "options":["أوم","فولت","أمبير","واط"], "answer":"أوم", "hint":"رمزها Ω", "level":"متوسط"},
    {"id":25, "question":"من كتب 'الأمير'؟", "options":["نيكولو مكيافيلي","شكسبير","دستويفسكي","جميل صدقي الزهاوي"], "answer":"نيكولو مكيافيلي", "hint":"فيلسوف إيطالي", "level":"صعب"},
    {"id":26, "question":"ما عدد أيام السنة الكبيسة؟", "options":["366","365","360","364"], "answer":"366", "hint":"تحدث كل 4 سنوات تقريبًا", "level":"ساهل"},
    {"id":27, "question":"ما اسم العضو الذي يعالج السموم في الجسم؟", "options":["الكبد","الكلية","القلب","الرئة"], "answer":"الكبد", "hint":"يساعد في الهضم وتخزين الطاقة", "level":"متوسط"},
    {"id":28, "question":"ما هي عاصمة مصر؟", "options":["القاهرة","الإسكندرية","الأقصر","أسوان"], "answer":"القاهرة", "hint":"أكبر مدينة في مصر", "level":"ساهل"},
    {"id":29, "question":"ما معادلة أينشتاين الشهيرة؟", "options":["E=mc^2","F=ma","V=IR","pV=nRT"], "answer":"E=mc^2", "hint":"تربط الطاقة والكتلة", "level":"صعب"},
    {"id":30, "question":"ما اسم الرمز @ بالإنجليزية؟", "options":["At","Hash","Dollar","Percent"], "answer":"At", "hint":"يستخدم في البريد الإلكتروني", "level":"ساهل"}
]

# ---------------- prepare questions source ----------------
loaded = None
if QUESTIONS_FILE.exists():
    loaded = load_questions_file(QUESTIONS_FILE)
QUESTIONS = loaded if loaded else DEFAULT_QUESTIONS

# ---------------- session init ----------------
def init_session():
    st.session_state.setdefault("started", False)
    st.session_state.setdefault("player", "")
    st.session_state.setdefault("difficulty", "متوسط")  # ساهل، متوسط، صعب
    st.session_state.setdefault("num_questions", min(10, len(QUESTIONS)))
    st.session_state.setdefault("time_per_q", 25)
    st.session_state.setdefault("pool", [])
    st.session_state.setdefault("index", 0)
    st.session_state.setdefault("current", None)
    st.session_state.setdefault("q_start", None)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("streak", 0)
    st.session_state.setdefault("xp", 0)
    st.session_state.setdefault("leaderboard", [])
    st.session_state.setdefault("sound", True)
    st.session_state.setdefault("answered", False)
    st.session_state.setdefault("hint_used_for", {})  # index -> True if hint used
    st.session_state.setdefault("radio_key_prefix", "sel_")
init_session()

# ---------------- helper functions ----------------
def build_pool(n, difficulty):
    # filter by difficulty if present in questions
    level_filtered = [q for q in QUESTIONS if q.get("level","متوسط") == difficulty]
    pool = level_filtered if len(level_filtered) >= n else QUESTIONS.copy()
    pool = deepcopy(pool)
    random.shuffle(pool)
    return pool[:n]

def start_game():
    st.session_state.pool = build_pool(st.session_state.num_questions, st.session_state.difficulty)
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.xp = 0
    st.session_state.answered = False
    st.session_state.hint_used_for = {}
    load_current_question()

def load_current_question():
    if st.session_state.index < 0 or st.session_state.index >= len(st.session_state.pool):
        st.session_state.current = None
        st.session_state.q_start = None
        return
    q = deepcopy(st.session_state.pool[st.session_state.index])
    # ensure options exist
    opts = q.get("options") or []
    if not isinstance(opts, list) or len(opts) < 2:
        # invalid question: fallback to simple placeholder
        q["options"] = ["نعم","لا"]
        q["answer"] = "نعم"
    else:
        random.shuffle(opts)
        q["options"] = opts
    st.session_state.current = q
    st.session_state.q_start = time.time()
    st.session_state.answered = False

def time_remaining():
    if st.session_state.q_start is None:
        return st.session_state.time_per_q
    elapsed = time.time() - st.session_state.q_start
    left = int(st.session_state.time_per_q - elapsed)
    return max(0, left)

def mark_timeout():
    # mark as answered and do not crash
    st.session_state.answered = True
    st.session_state.streak = 0
    # play timeout sound if set
    if st.session_state.sound and SOUND_TIMEOUT:
        try:
            st.audio(SOUND_TIMEOUT)
        except:
            pass

def submit_answer(selected_value):
    q = st.session_state.current
    if not q:
        return
    st.session_state.answered = True
    correct = (selected_value == q.get("answer"))
    if correct:
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.xp += 10
        if st.session_state.sound and SOUND_CORRECT:
            try: st.audio(SOUND_CORRECT)
            except: pass
        st.success("✅ إجابة صحيحة!")
    else:
        st.session_state.streak = 0
        if st.session_state.sound and SOUND_WRONG:
            try: st.audio(SOUND_WRONG)
            except: pass
        st.error(f"❌ خاطئ — الإجابة الصحيحة: {q.get('answer')}")
    # do not auto-advance to avoid rerun problems; user clicks التالي

def use_hint():
    idx = st.session_state.index
    q = st.session_state.current
    if not q:
        return
    opts = q.get("options", [])
    correct = q.get("answer")
    wrongs = [o for o in opts if o != correct]
    if len(wrongs) >= 1:
        # remove one wrong option for simplicity
        to_remove = random.choice(wrongs)
        new_opts = [o for o in opts if o != to_remove]
        st.session_state.current["options"] = new_opts
        # reflect in pool too
        st.session_state.pool[st.session_state.index]["options"] = new_opts
        st.session_state.hint_used_for[idx] = True
        st.info("تم حذف خيار خاطئ (تلميح).")
    else:
        st.info("لا يمكن إعطاء تلميح لهذا السؤال.")

def next_question():
    # advance index, load next or finish
    st.session_state.index += 1
    if st.session_state.index < len(st.session_state.pool):
        load_current_question()
    else:
        # end of game
        st.session_state.current = None
        st.session_state.q_start = None
        st.session_state.answered = False

# ---------------- Layout: header ----------------
st.markdown('<div class="header"><div class="title">لعبة الألغاز العربية</div><div class="subtitle">سلسلة أسئلة سريعة — جرّب معلوماتك ونافس أصدقائك</div></div>', unsafe_allow_html=True)

# ---------------- Main logic ----------------
# If not started: show settings
if not st.session_state.started:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.session_state.player = st.text_input("اكتب اسمك (اختياري):", value=st.session_state.player)
        st.session_state.sound = st.checkbox("تشغيل الأصوات", value=st.session_state.sound)
        st.session_state.difficulty = st.selectbox("اختر مستوى الصعوبة:", ["ساهل", "متوسط", "صعب"], index=["ساهل","متوسط","صعب"].index(st.session_state.difficulty))
        st.session_state.num_questions = st.slider("عدد الأسئلة:", min_value=5, max_value=min(30, len(QUESTIONS)), value=st.session_state.num_questions)
        st.session_state.time_per_q = st.slider("مدة كل سؤال (ثانية):", min_value=8, max_value=120, value=st.session_state.time_per_q)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶️ ابدأ اللعبة", key="start"):
            st.session_state.started = True
            start_game()
        st.markdown("</div>", unsafe_allow_html=True)

    # sidebar: show basic info
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**ملاحظة:** يمكنك وضع ملف `questions.json` في نفس المجلد لعرض أسئلة خاصة (انظر الشريط الجانبي).")
    st.markdown("</div>", unsafe_allow_html=True)

# During game: show question
elif st.session_state.started and st.session_state.current:
    q = st.session_state.current
    idx = st.session_state.index
    total = len(st.session_state.pool)

    # header status
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    c1.markdown(f"**السؤال:** {idx+1} / {total}")
    c2.markdown(f"**النقاط:** {st.session_state.score}")
    c3.markdown(f"**السلسلة:** {st.session_state.streak}")
    st.markdown("</div>", unsafe_allow_html=True)

    # question card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<div class='question'>❓ {q.get('question')}</div>", unsafe_allow_html=True)

    # time and progress
    left = time_remaining()
    st.markdown(f"⏱ الوقت المتبقي: <span class='timer'>{left} ث</span>", unsafe_allow_html=True)
    pct = 0
    if st.session_state.time_per_q > 0:
        elapsed = st.session_state.time_per_q - left
        pct = int((elapsed / st.session_state.time_per_q) * 100)
    st.markdown(f"<div class='progress-wrap'><div class='progress-bar' style='width:{pct}%;'></div></div>", unsafe_allow_html=True)

    # if time ran out and not answered => mark timeout and show message and let user press التالي
    if left == 0 and not st.session_state.answered:
        mark_timeout()
        st.warning("انتهى الوقت! اضغط 'التالي' للانتقال للسؤال التالي.")
        # show correct answer
        st.info(f"الإجابة الصحيحة: **{q.get('answer')}**")

    # show options (radio) with a unique key per question index
    options = q.get("options", []) or ["نعم","لا"]
    radio_key = f"{st.session_state['radio_key_prefix']}{idx}"
    selected = st.radio("اختر الإجابة:", options, key=radio_key)

    # buttons: confirm, hint, next
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("✅ تأكيد"):
            if not st.session_state.answered and left>0:
                submit_answer(selected)
            elif st.session_state.answered:
                st.info("لقد أجبت بالفعل. اضغط التالي للانتقال.")
            else:
                st.info("انتهى الوقت، اضغط التالي للانتقال.")
    with col2:
        if st.button("💡 تلميح"):
            if not st.session_state.answered:
                use_hint()
            else:
                st.info("لا يمكن طلب تلميح بعد الإجابة.")
    with col3:
        if st.button("⏭ التالي"):
            next_question()

    # show hint text if exists
    if q.get("hint"):
        st.markdown(f"<div class='small'>تلميح: {q.get('hint')}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# End of game: show results
elif st.session_state.started and st.session_state.current is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    total = len(st.session_state.pool)
    st.markdown(f"## 🎉 انتهت الجولة — نتيجتك: {st.session_state.score} / {total}")
    st.markdown(f"**المستوى:** {st.session_state.difficulty} — **XP:** {st.session_state.xp}")
    st.markdown("</div>", unsafe_allow_html=True)

    # leaderboard: store in session (session-only)
    name = st.session_state.player or "لاعب"
    st.session_state.leaderboard.append({"name": name, "score": st.session_state.score, "xp": st.session_state.xp, "time": int(time.time())})
    lb_sorted = sorted(st.session_state.leaderboard, key=lambda r: (-r["score"], -r["xp"], r["time"]))
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🏆 نتائج هذه الجلسة")
    for i, r in enumerate(lb_sorted[:10], start=1):
        st.markdown(f"<div class='leader'>{i}. <b>{r['name']}</b> — {r['score']} نقطة — XP:{r['xp']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("🔁 إعادة اللعب"):
            start_game()
    with c2:
        if st.button("🏠 العودة للصفحة الرئيسية"):
            st.session_state.started = False
            st.session_state.current = None

# ---------------- Sidebar info & JSON example ----------------
with st.sidebar:
    st.markdown("## حول اللعبة")
    st.markdown("- عربي فقط · واجهة بسيطة · متوافقة مع الهواتف")
    st.markdown("- لو أردت أسئلة مخصصة: ارفع `questions.json` في نفس المجلد بصيغة المثال أدناه.")
    st.markdown("**مثال صيغة JSON:**")
    st.code("""
[
  {
    "question": "ما عاصمة فرنسا؟",
    "options": ["باريس","روما","مدريد","برلين"],
    "answer": "باريس",
    "hint": "مدينة الأنوار",
    "level": "ساهل"
  }
]
    """, language="json")
    st.markdown("---")
    st.markdown(f"عدد الأسئلة المتوفّرة: **{len(QUESTIONS)}**")
    st.markdown("ملف الصوت: يعمل إن أعطيت روابط صحيحة في أعلى الملف.")
