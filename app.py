# app.py
# لعبة ألغاز عربية بسيطة وجذابة لـ Streamlit
# حفظ الملف كـ app.py ثم شغّل: streamlit run app.py

import streamlit as st
import json
import random
import time
from pathlib import Path
from copy import deepcopy

# -------------------- إعدادات موارد (عدل المسارات لو تحب صوت/خلفية محلية) --------------------
BASE = Path(__file__).parent
QUESTIONS_FILE = BASE / "questions.json"   # لو تحط ملف JSON هنا رح يتم استخدامه
ASSETS_DIR = BASE / "assets"               # مجلد اختياري للأصوات/صور

# أمثلة: ضع مسار أو رابط إذا عندك، أو اتركهم فارغين
SOUND_CORRECT = ""     # "assets/correct.mp3" أو رابط mp3
SOUND_WRONG = ""       # "assets/wrong.mp3"
SOUND_TIMEOUT = ""     # "assets/timeout.mp3"
SOUND_BG = ""          # "assets/bg.mp3"  (موسيقى خلفية - اختياري، لا تضع إن لم تكن متوفرة)

# -------------------- إعداد صفحة و CSS --------------------
st.set_page_config(page_title="لعبة الألغاز العربية", page_icon="🧠", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg,#07172b 0%, #0f2a43 50%, #072033 100%);
        color: #eaf6ff;
        font-family: 'Cairo', sans-serif;
    }
    .title { font-size: 38px; font-weight:700; color: #ffd166; text-align:center; margin-bottom:6px; }
    .subtitle { text-align:center; color:#bfe9ff; margin-top:0; margin-bottom:18px; }
    .card { background: rgba(255,255,255,0.03); border-radius:14px; padding:14px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .question { font-size:20px; font-weight:700; margin-bottom:12px; }
    .option { background: rgba(255,255,255,0.02); border-radius:10px; padding:12px; margin:8px 0; cursor:pointer; color:#eaf6ff; }
    .btn-primary > button { background: linear-gradient(90deg,#ffb86b,#ff6d6d); color:#071426; font-weight:700; border-radius:10px; padding:10px 16px; }
    .btn-ghost > button { background: transparent; border:1px solid rgba(255,255,255,0.12); color:#eaf6ff; border-radius:10px; padding:10px 16px; }
    .small { color:#bfe9ff; font-size:13px; }
    .timer { background: linear-gradient(90deg,#00d4ff,#00ffa6); color:#071426; padding:6px 10px; border-radius:999px; font-weight:800; display:inline-block; }
    .progress-wrap { background: rgba(255,255,255,0.06); height:10px; border-radius:999px; overflow:hidden; margin-top:6px; }
    .progress-bar { height:10px; background: linear-gradient(90deg,#00ffa6,#00d4ff); width:0%; transition: width 0.25s ease; }
    .info { background: rgba(255,255,255,0.02); padding:8px 12px; border-radius:10px; color:#cfefff; }
    </style>
    """, unsafe_allow_html=True
)

# -------------------- تحميل الأسئلة --------------------
def load_questions_file(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cleaned = []
        for i, item in enumerate(data):
            # توقع البنية: {"question": "...", "options": [...], "answer": "...", "hint": "..."}
            if not isinstance(item, dict):
                continue
            q = item.get("question") or item.get("q") or None
            opts = item.get("options") or item.get("choices") or item.get("choices_list") or []
            ans = item.get("answer") or item.get("correct") or None
            hint = item.get("hint") or item.get("explain") or ""
            if q and isinstance(opts, list) and ans in opts:
                cleaned.append({
                    "id": item.get("id", i+1),
                    "question": str(q),
                    "options": opts,
                    "answer": ans,
                    "hint": str(hint)
                })
        return cleaned
    except Exception as e:
        return None

# بيانات افتراضية (تُستخدم لو ماكانش ملف)
DEFAULT_QUESTIONS = [
    {"id":1, "question":"ما هو الكوكب المعروف بالكوكب الأحمر؟", "options":["المريخ","الزهرة","عطارد","المشتري"], "answer":"المريخ", "hint":"اسمه يبدأ بحرف الميم."},
    {"id":2, "question":"من هو مخترع المصباح الكهربائي (الشائع ذكره)؟", "options":["توماس إديسون","نيوتن","ألبرت أينشتاين","جراهام بيل"], "answer":"توماس إديسون", "hint":"اشتهر بتطوير المصباح التجاري."},
    {"id":3, "question":"كم عدد الكواكب في المجموعة الشمسية حسب التصنيف الحالي؟", "options":["8","9","7","10"], "answer":"8", "hint":"بعد إعادة تصنيف بلوتو."},
    {"id":4, "question":"ما هي عاصمة الجزائر؟", "options":["وهران","قسنطينة","الجزائر العاصمة","عنابة"], "answer":"الجزائر العاصمة", "hint":"تبدأ ب'ال' وتحتوي على كلمة 'عاصمة' أحياناً."},
    {"id":5, "question":"ما هو أسرع حيوان بري؟", "options":["الفهد","الأسد","الغزال","الحصان"], "answer":"الفهد", "hint":"يقوم بانقضاضات سريعة جدا."},
    {"id":6, "question":"ما هو العنصر الذي يرمز له بالرمز O؟", "options":["الذهب","الأوكسجين","الحديد","الفضة"], "answer":"الأوكسجين", "hint":"نستهلكه عند التنفس."},
    {"id":7, "question":"ما هي أكبر قارة من حيث المساحة؟", "options":["أفريقيا","آسيا","أوروبا","أمريكا الشمالية"], "answer":"آسيا", "hint":"تضم الصين والهند."},
    {"id":8, "question":"من هو مؤلف رواية 'البؤساء'؟", "options":["فيكتور هوغو","تولستوي","تشارلز ديكنز","مارك توين"], "answer":"فيكتور هوغو", "hint":"كاتب فرنسي."},
    {"id":9, "question":"ما هو العضو الذي يضخ الدم في الجسم؟", "options":["الكبد","القلب","الرئتين","الطحال"], "answer":"القلب", "hint":"يمكنك قياس نبضه في الرسغ."},
    {"id":10, "question":"أي بروتوكول يضمن اتصال آمن للمواقع؟", "options":["HTTP","FTP","SMTP","HTTPS"], "answer":"HTTPS", "hint":"يتضمن حرف S في النهاية."}
]

# تحميل من ملف إذا موجود
if QUESTIONS_FILE.exists():
    loaded = load_questions_file(QUESTIONS_FILE)
    if loaded is None or len(loaded) == 0:
        st.warning("ملف questions.json موجود لكن صياغته غير صحيحة أو فارغ. سيتم استخدام الأسئلة الافتراضية.")
        QUESTIONS = deepcopy(DEFAULT_QUESTIONS)
    else:
        QUESTIONS = loaded
else:
    QUESTIONS = deepcopy(DEFAULT_QUESTIONS)

# فقط تأكد ان العناصر متوفرة
if not isinstance(QUESTIONS, list) or len(QUESTIONS) == 0:
    QUESTIONS = deepcopy(DEFAULT_QUESTIONS)

# -------------------- تهيئة session_state --------------------
def init():
    st.session_state.setdefault("started", False)
    st.session_state.setdefault("player", "")
    st.session_state.setdefault("num_questions", min(10, len(QUESTIONS)))
    st.session_state.setdefault("time_per_q", 25)
    st.session_state.setdefault("pool", [])
    st.session_state.setdefault("index", 0)
    st.session_state.setdefault("current", None)   # السؤال الحالي dict
    st.session_state.setdefault("q_start", None)   # وقت بداية السؤال
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("xp", 0)
    st.session_state.setdefault("level", 1)
    st.session_state.setdefault("streak", 0)
    st.session_state.setdefault("leaderboard", [])  # قائمة بسيطة داخل الجلسة
    st.session_state.setdefault("sound", True)
    st.session_state.setdefault("hints_used", 0)
    st.session_state.setdefault("timed_out_processed", {})  # map index->bool

init()

# -------------------- أدوات اللعبة --------------------
def make_pool(n):
    pool = QUESTIONS.copy()
    random.shuffle(pool)
    return pool[:n]

def start_game():
    n = st.session_state.num_questions
    st.session_state.pool = make_pool(n)
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.xp = 0
    st.session_state.level = 1
    st.session_state.streak = 0
    st.session_state.hints_used = 0
    st.session_state.timed_out_processed = {}
    st.session_state.started = True
    load_next_question()

def load_next_question():
    if st.session_state.index >= len(st.session_state.pool):
        st.session_state.current = None
        st.session_state.q_start = None
        return
    q = deepcopy(st.session_state.pool[st.session_state.index])
    # shuffle options but keep answer as value (string)
    opts = q.get("options", [])[:]
    random.shuffle(opts)
    q["shuffled"] = opts
    st.session_state.current = q
    st.session_state.q_start = time.time()
    # mark timed_out_processed false for this index
    st.session_state.timed_out_processed[st.session_state.index] = False
    # set radio default
    st.session_state.setdefault(f"choice_{st.session_state.index}", None)

def time_remaining():
    if st.session_state.q_start is None:
        return st.session_state.time_per_q
    left = int(st.session_state.time_per_q - (time.time() - st.session_state.q_start))
    return max(0, left)

def process_timeout():
    idx = st.session_state.index
    if st.session_state.timed_out_processed.get(idx):
        return
    st.session_state.timed_out_processed[idx] = True
    # treat as wrong / skip: reset streak, no xp
    st.session_state.streak = 0
    # optionally play timeout sound
    if st.session_state.sound and SOUND_TIMEOUT:
        try:
            st.audio(SOUND_TIMEOUT)
        except:
            pass
    # move next
    st.session_state.index += 1
    if st.session_state.index < len(st.session_state.pool):
        load_next_question()
    else:
        st.session_state.current = None
        st.session_state.q_start = None
    # rerun to update UI
    st.rerun()

def handle_confirm(selected_value):
    q = st.session_state.current
    if q is None:
        return
    correct = (selected_value == q["answer"])
    if correct:
        st.session_state.score += 1
        st.session_state.xp += 10
        st.session_state.streak += 1
        # level up logic: every 50 xp increases level
        if st.session_state.xp >= st.session_state.level * 50:
            st.session_state.level += 1
            # celebration
            st.balloons()
    else:
        st.session_state.streak = 0
        # could deduct xp? leave as-is
    # play sounds if set
    if st.session_state.sound:
        try:
            if correct and SOUND_CORRECT:
                st.audio(SOUND_CORRECT)
            elif not correct and SOUND_WRONG:
                st.audio(SOUND_WRONG)
        except:
            pass
    # move next
    st.session_state.index += 1
    if st.session_state.index < len(st.session_state.pool):
        load_next_question()
    else:
        st.session_state.current = None
        st.session_state.q_start = None
    st.rerun()

def use_hint():
    q = st.session_state.current
    if not q:
        return
    options = q["shuffled"]
    correct = q["answer"]
    wrongs = [o for o in options if o != correct]
    if len(wrongs) >= 2:
        # remove two wrongs
        to_remove = set(random.sample(wrongs, 2))
        q["shuffled"] = [o for o in options if o not in to_remove]
        st.session_state.hints_used += 1
        # update in pool too
        st.session_state.pool[st.session_state.index]["shuffled"] = q["shuffled"]
    else:
        st.info("لا يمكن حذف خيارات أكثر.")

# -------------------- واجهة اللعبة --------------------
st.markdown('<div class="title">لعبة الألغاز العربية</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">اختبر معلوماتك — واجهة عربية سهلة وسريعة</div>', unsafe_allow_html=True)

# top controls
col_top = st.columns([3,1,1])
with col_top[0]:
    name = st.text_input("✍️ اكتب اسمك (اختياري):", value=st.session_state.player)
    st.session_state.player = name.strip()
with col_top[1]:
    sound_toggle = st.checkbox("🔊 صوت", value=st.session_state.sound)
    st.session_state.sound = sound_toggle
with col_top[2]:
    # show XP and level small
    st.markdown(f"<div style='text-align:center' class='info'><b>XP:</b> {st.session_state.xp} — <b>مستوى:</b> {st.session_state.level}</div>", unsafe_allow_html=True)

st.markdown("")  # spacer

# configuration / start area (if not started)
if not st.session_state.started:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ إعدادات اللعبة", unsafe_allow_html=True)
        n_q = st.slider("عدد الأسئلة:", min_value=5, max_value=min(50, len(QUESTIONS)), value=st.session_state.num_questions)
        st.session_state.num_questions = n_q
        t_q = st.slider("مدة كل سؤال (ثانية):", min_value=8, max_value=120, value=st.session_state.time_per_q)
        st.session_state.time_per_q = t_q
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶️ ابدأ اللعبة الآن", use_container_width=True):
            if len(QUESTIONS) == 0:
                st.error("لا توجد أسئلة. أضف ملف questions.json أو تأكد من البيانات.")
            else:
                start_game()
        st.markdown("</div>", unsafe_allow_html=True)
    # show sample info and leaderboard
    st.markdown("<br>")
    st.markdown("<div class='card'><b>ملاحظات:</b> يمكنك تحميل ملف questions.json في نفس مجلد التطبيق لتغيير الأسئلة. اللعبة تستخدم بيانات افتراضية إن لم يوجد ملف.</div>", unsafe_allow_html=True)

# gameplay
elif st.session_state.started and st.session_state.current:
    q = st.session_state.current
    idx = st.session_state.index
    total = len(st.session_state.pool)

    # header row: question number, score, streak
    cols = st.columns([1,1,1])
    cols[0].markdown(f"**السؤال:** {idx+1} / {total}")
    cols[1].markdown(f"**النقاط:** {st.session_state.score}")
    cols[2].markdown(f"**السلسلة:** {st.session_state.streak}")

    # progress bar
    progress_pct = int((idx / total) * 100)
    st.progress(progress_pct)

    # question card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<div class='question'>❓ {q['question']}</div>", unsafe_allow_html=True)

    # time left
    left = time_remaining()
    # if timeout happened and not processed, process now
    if left <= 0 and not st.session_state.timed_out_processed.get(idx, False):
        # show timeout message then process
        st.warning("⏳ انتهى الوقت! يتم الانتقال للسؤال التالي...")
        process_timeout()   # this will rerun
    # show timer & visual bar
    st.markdown(f"<div>⏱ الوقت المتبقي: <span class='timer'>{left} ث</span></div>", unsafe_allow_html=True)
    pct_bar = int(((st.session_state.time_per_q - left) / st.session_state.time_per_q) * 100) if st.session_state.time_per_q>0 else 0
    st.markdown(f"<div class='progress-wrap'><div class='progress-bar' style='width:{pct_bar}%' ></div></div>", unsafe_allow_html=True)

    # show shuffled options
    options = q.get("shuffled", q.get("options", [])).copy()
    choice_key = f"choice_{idx}"
    # default radio selection if not set
    if st.session_state.get(choice_key) is None and len(options)>0:
        st.session_state[choice_key] = 0
    selected_index = st.radio("اختر الإجابة:", options, index=st.session_state.get(choice_key,0), key=choice_key)

    # buttons row
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("✅ تأكيد الإجابة"):
            # handle confirm
            handle_confirm(selected_index)
    with c2:
        if st.button("💡 تلميح"):
            use_hint()
            # stay on same question; no rerun needed (UI updates)
    with c3:
        if st.button("⏭ تخطّي"):
            st.session_state.streak = 0
            st.session_state.index += 1
            if st.session_state.index < len(st.session_state.pool):
                load_next_question()
            else:
                st.session_state.current = None
                st.session_state.q_start = None
            st.rerun()

    # show hint text optionally
    if q.get("hint"):
        st.markdown(f"<div class='small'>تلميح: {q.get('hint')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close card

# finished: show results
elif st.session_state.started and not st.session_state.current:
    total = len(st.session_state.pool)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"## 🎉 انتهت الجولة — نتيجتك: {st.session_state.score} / {total}")
    st.markdown(f"**XP:** {st.session_state.xp} — **المستوى:** {st.session_state.level}")
    st.markdown(f"**التلميحات المستخدمة:** {st.session_state.hints_used}")
    st.markdown("</div>", unsafe_allow_html=True)

    # leaderboard: نضيف نتيجة الجلسة
    name = st.session_state.player or "لاعب"
    st.session_state.leaderboard.append({"name": name, "score": st.session_state.score, "xp": st.session_state.xp, "level": st.session_state.level, "time": int(time.time())})
    # عرض أعلى 10
    sorted_lb = sorted(st.session_state.leaderboard, key=lambda x: (-x["score"], -x["xp"], x["time"]))
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🏆 لوحة النتائج (داخل الجلسة)")
    for i, row in enumerate(sorted_lb[:10], start=1):
        st.markdown(f"{i}. {row['name']} — {row['score']} نقطة — XP:{row['xp']} — مستوى:{row['level']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # action buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 العب مرة أخرى"):
            start_game()
    with c2:
        if st.button("🏠 العودة إلى القائمة"):
            st.session_state.started = False
            st.session_state.current = None
            st.rerun()

# -------------------- شريط جانبي للمساعدة --------------------
with st.sidebar:
    st.markdown("## معلومات سريعة")
    st.markdown(f"- الأسئلة المتاحة: **{len(QUESTIONS)}**")
    st.markdown(f"- استخدم ملف questions.json لو حبيت تعدل الأسئلة")
    st.markdown("---")
    st.markdown("صيغة السؤال في JSON (مثال):")
    st.code("""
[
  {
    "question": "ما هي عاصمة فرنسا؟",
    "options": ["باريس","لندن","برلين","روما"],
    "answer": "باريس",
    "hint": "مدينة النور"
  }
]
    """, language="json")
    st.markdown("---")
    st.markdown("ملاحظة: لو وضعت أصوات في المتغيرات في أعلى الكود، ستُشغّل عند الإجابة.")

# نهاية الملف
