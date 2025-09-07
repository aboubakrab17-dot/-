# --------------------------- app.py (FULL, fixed) ---------------------------
import streamlit as st
import json, random, time
from typing import Dict, List, Any

st.set_page_config(page_title="🎮 ألغاز • Quiz", page_icon="🧠", layout="wide")

# ====== خلفية + ستايل (تصميم غلاس مع تدرّج + تعديل حقول الإدخال والاختيارات) ======
BG_URL = "https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=1600&auto=format&fit=crop"
CSS = f"""
<style>
/* خلفية */
[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(0, 255, 204, .10), transparent 60%),
    radial-gradient(900px 500px at 90% 10%, rgba(255, 0, 128, .10), transparent 60%),
    linear-gradient(135deg, #0b0f1a 0%, #0a0d18 60%, #0b0f1a 100%),
    url('{BG_URL}') no-repeat center/cover fixed;
}}
.block-container {{
  background: rgba(0,0,0,.28);
  backdrop-filter: blur(6px);
  border-radius: 18px;
  padding: 18px 20px;
}}
/* نص */
h1,h2,h3,h4,h5,h6,label, p, span, div {{
  color:#f2f5fb !important;
}}
/* المدخلات (نص) */
.stTextInput > div > div > input {{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  color: #fff !important;
  border-radius: 12px;
}}
.stTextInput input::placeholder {{ color: rgba(255,255,255,.65) !important; }}

/* select (BaseWeb) */
[data-baseweb="select"] > div {{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  color: #fff !important; border-radius: 12px;
}}
[data-baseweb="select"] * {{ color:#fff !important; }}
/* أزرار */
.stButton>button {{
  background: linear-gradient(135deg,#7c3aed 0%,#06b6d4 100%);
  border: 0; color: #fff; font-weight: 700;
  border-radius: 12px; padding: .6rem 1rem;
}}
.stButton>button:hover {{ filter: brightness(1.05); }}
/* الراديو (الاختيارات) */
div[role="radiogroup"] > label {{
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  border-radius: 12px; padding: .55rem .8rem; margin:.25rem 0;
}}
/* البطاقات والتنبيهات */
.stAlert, .stMetric {{
  background: rgba(0,0,0,.45) !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  border-radius: 14px !important;
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ====== أسئلة افتراضية (Fallback) تُستخدم تلقائياً إذا لم يوجد ملف أو كان فارغ ======
DEFAULT_DATA: Dict[str, List[Dict[str, Any]]] = {
    "ar": [
        {"question":"ما البروتوكول الذي يشفّر المواقع بـ https؟", "options":["TLS","FTP","SSH","SCP"], "answer":"TLS", "hint":"الجيل الأحدث من SSL."},
        {"question":"أي عضو يفرز الإنسولين؟", "options":["البنكرياس","الكبد","الطحال","المعدة"], "answer":"البنكرياس","hint":"يقع خلف المعدة."},
        {"question":"ما الدولة الأكثر جزرًا في العالم؟", "options":["السويد","إندونيسيا","اليابان","الفلبين"], "answer":"السويد","hint":"أكثر من 200 ألف جزيرة."},
        {"question":"كم عدد الكروموسومات عند الإنسان؟", "options":["46","44","48","42"], "answer":"46","hint":"23 زوجًا."},
        {"question":"ما أصغر عدد أولي زوجي؟", "options":["2","3","5","7"], "answer":"2","hint":"الوحيد الزوجي."},
        {"question":"أي طبقة في نموذج OSI مسؤولة عن التوجيه؟", "options":["الشبكة","بيانات","جلسة","تطبيق"], "answer":"الشبكة","hint":"الطبقة الثالثة."},
        {"question":"العنصر ذو الرمز Fe هو؟", "options":["الحديد","النحاس","الفضة","الزنك"], "answer":"الحديد","hint":"يتأكسد للون بني."},
        {"question":"أطول نهر في العالم حسب أطول مجرى؟", "options":["النيل","الأمازون","اليانغتسي","الكونغو"], "answer":"النيل","hint":"في إفريقيا."}
    ],
    "en": [
        {"question":"Which algorithm is used by modern blockchains to link blocks?", "options":["Hashing","Sorting","Compression","Encryption"], "answer":"Hashing","hint":"SHA family."},
        {"question":"What gas is most responsible for the greenhouse effect on Venus?", "options":["CO₂","O₂","CH₄","N₂"], "answer":"CO₂","hint":"Over 96% of the atmosphere."},
        {"question":"Smallest unit of a neural network that applies a weighted sum + activation?", "options":["Neuron","Epoch","Batch","Kernel"], "answer":"Neuron","hint":"Also called node."},
        {"question":"Which planet has the strongest winds in the Solar System?", "options":["Neptune","Jupiter","Mars","Saturn"], "answer":"Neptune","hint":">2000 km/h."},
        {"question":"What is the Big-O of binary search?", "options":["O(log n)","O(n)","O(n log n)","O(1)"], "answer":"O(log n)","hint":"Halves the search space."},
        {"question":"Which vitamin is produced in skin by sunlight?", "options":["Vitamin D","Vitamin A","Vitamin B12","Vitamin C"], "answer":"Vitamin D","hint":"UV related."},
        {"question":"What is the heaviest naturally occurring element (by stable atomic number)?", "options":["Uranium","Lead","Plutonium","Mercury"], "answer":"Uranium","hint":"Z=92."},
        {"question":"World’s largest desert by area?", "options":["Antarctic","Sahara","Arctic","Gobi"], "answer":"Antarctic","hint":"Cold desert."}
    ]
}

# ====== تحميل الأسئلة بأمان ======
def load_questions(path="questions.json") -> Dict[str, List[Dict[str, Any]]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return DEFAULT_DATA
    except json.JSONDecodeError:
        st.warning("⚠️ خطأ في صيغة JSON — تم استخدام الأسئلة الافتراضية.")
        return DEFAULT_DATA

    def normalize(lst):
        out=[]
        for q in (lst or []):
            if not isinstance(q, dict): 
                continue
            question = str(q.get("question","")).strip()
            opts = list(q.get("options", []))
            ans = str(q.get("answer","")).strip()
            hint = str(q.get("hint","")).strip()
            if question and isinstance(opts, list) and len(opts)>=2 and ans:
                if ans not in opts:
                    opts.append(ans)
                # إزالة تكرارات
                opts = list(dict.fromkeys(opts))
                out.append({"question":question,"options":opts,"answer":ans,"hint":hint})
        return out

    ar = normalize(data.get("ar", []))
    en = normalize(data.get("en", []))
    if not ar and not en:
        return DEFAULT_DATA
    return {"ar": ar or DEFAULT_DATA["ar"], "en": en or DEFAULT_DATA["en"]}

# ====== حالة التطبيق ======
if "DATA" not in st.session_state:
    st.session_state.DATA = load_questions()
if "screen" not in st.session_state:
    st.session_state.screen = "menu"
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_ts" not in st.session_state:
    st.session_state.start_ts = None
if "removed_opts" not in st.session_state:
    st.session_state.removed_opts = {}
if "used_5050" not in st.session_state:
    st.session_state.used_5050 = set()
if "show_hint" not in st.session_state:
    st.session_state.show_hint = False
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 10
if "time_per_q" not in st.session_state:
    st.session_state.time_per_q = 25
if "player" not in st.session_state:
    st.session_state.player = ""

# ====== أدوات ======
def reset_game():
    data = st.session_state.DATA.get(st.session_state.lang, [])
    pool = data[:]
    random.shuffle(pool)
    n = max(1, min(st.session_state.num_questions, len(pool)))
    st.session_state.questions = pool[:n]
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.start_ts = time.time()
    st.session_state.removed_opts = {}
    st.session_state.used_5050 = set()
    st.session_state.show_hint = False
    st.session_state.screen = "game"

def cur_q():
    i = st.session_state.q_index
    qs = st.session_state.questions
    return qs[i] if 0 <= i < len(qs) else None

def seconds_left():
    if not st.session_state.start_ts:
        return st.session_state.time_per_q
    left = st.session_state.time_per_q - int(time.time()-st.session_state.start_ts)
    return max(0, left)

def next_q(auto=False):
    st.session_state.q_index += 1
    st.session_state.start_ts = time.time()
    st.session_state.show_hint = False
    if st.session_state.q_index >= len(st.session_state.questions):
        st.session_state.screen = "result"
        if not auto: st.balloons()

def apply_5050(idx, q):
    correct = q["answer"]
    wrongs = [o for o in q["options"] if o != correct]
    random.shuffle(wrongs)
    remove = set(wrongs[:max(1, len(q["options"])//2 - 1)])
    st.session_state.removed_opts[idx] = remove
    st.session_state.used_5050.add(idx)

# ====== شاشة القائمة ======
def menu():
    st.markdown("## 🧠 أفضل لعبة ألغاز")
    st.caption("إختبر معلوماتك وتحدَّ نفسك! اختر اللغة، عدد الأسئلة، ومدّة كل سؤال.")

    c1, c2 = st.columns([3,2])
    with c1:
        st.text_input("✨ اكتب اسمك", key="player", placeholder="Player")
        st.selectbox("🌐 Language / اللغة", options=[("ar","العربية"),("en","English")],
                     index=0 if st.session_state.lang=="ar" else 1,
                     key="lang", format_func=lambda x: x[1])
    with c2:
        st.slider("🔢 عدد الأسئلة", 5, 30, key="num_questions")
        st.slider("⏳ مدة كل سؤال (ثانية)", 10, 60, key="time_per_q")

    avail = len(st.session_state.DATA.get(st.session_state.lang, []))
    st.info(f"الأسئلة المتاحة للغة المختارة: **{avail}**")

    c3, c4 = st.columns(2)
    with c3:
        if st.button("▶️ ابدأ اللعبة", use_container_width=True):
            if avail == 0:
                st.error("لا توجد أسئلة لهذه اللغة (تم تعطيل البدء).")
            else:
                reset_game()
                st.experimental_rerun()
    with c4:
        if st.button("🔄 إعادة تحميل الأسئلة (من JSON)", use_container_width=True):
            st.session_state.DATA = load_questions()
            st.success("تم التحديث من الملف (أو استخدام الافتراضي).")

# ====== شاشة اللعب ======
def game():
    q = cur_q()
    if not q:
        st.session_state.screen = "result"
        st.experimental_rerun()
        return

    total = len(st.session_state.questions)
    idx = st.session_state.q_index

    top1, top2, top3 = st.columns([2,1,1])
    with top1:
        st.progress((idx)/max(1,total))
        st.caption(f"{idx+1} / {total}")
    with top2:
        st.metric("⭐ النقاط", f"{st.session_state.score}")
    with top3:
        left = seconds_left()
        st.metric("⏱️ الوقت", f"{left}s")
        if left > 0:
            time.sleep(0.5); st.experimental_rerun()
        else:
            st.warning("⏰ انتهى الوقت! تم التخطي تلقائيًا.")
            next_q(auto=True); st.experimental_rerun()

    st.markdown(f"### ❓ {q['question']}")

    options = q["options"][:]
    if idx in st.session_state.removed_opts:
        rem = st.session_state.removed_opts[idx]
        options = [o for o in options if o not in rem]
    random.shuffle(options)

    choice = st.radio("اختر الإجابة:", options, key=f"pick_{idx}")
    b1,b2,b3,b4 = st.columns(4)
    with b1:
        if st.button("💡 تلميح", use_container_width=True):
            st.session_state.show_hint = not st.session_state.show_hint
    with b2:
        if idx in st.session_state.used_5050:
            st.button("🧪 50/50 (مستعملة)", disabled=True, use_container_width=True)
        else:
            if st.button("🧪 50/50", use_container_width=True):
                apply_5050(idx, q); st.experimental_rerun()
    with b3:
        if st.button("⏭️ تخطي", use_container_width=True):
            next_q(); st.experimental_rerun()
    with b4:
        if st.button("✅ تأكيد", use_container_width=True):
            if choice == q["answer"]:
                st.success("✔️ صحيحة"); st.session_state.score += 1
            else:
                st.error(f"❌ خاطئة. الصحيح: **{q['answer']}**")
            next_q(); st.experimental_rerun()

    if st.session_state.show_hint:
        st.info(q["hint"] or "لا يوجد تلميح.")

# ====== شاشة النتيجة ======
def result():
    total = len(st.session_state.questions)
    score = st.session_state.score
    pct = int((score/total)*100) if total else 0
    st.markdown("## 🏁 النتيجة")
    st.success(f"**{st.session_state.player or 'Player'}** — نقاطك: **{score}/{total}** ({pct}%)")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("🔁 إعادة اللعب", use_container_width=True):
            reset_game(); st.experimental_rerun()
    with c2:
        if st.button("🏠 القائمة الرئيسية", use_container_width=True):
            st.session_state.screen = "menu"; st.experimental_rerun()

# ====== توجيه ======
if st.session_state.screen == "menu":
    menu()
elif st.session_state.screen == "game":
    game()
else:
    result()
# --------------------------- END ---------------------------
