# app.py
import streamlit as st
import random
import datetime
import secrets
import string

# ---------------------- إعدادات عامة + تنسيق ----------------------
st.set_page_config(page_title="🎉 مركز الترفيه والمساعدة", page_icon="✨", layout="centered")

# CSS الخلفية + بطاقات + أزرار
BACKGROUND_CSS = """
<style>
/* خلفية متدرجة ثابتة مع نقش بسيط */
body {
  background: radial-gradient(ellipse at top left, #0f2027 0%, #203a43 40%, #2c5364 100%) fixed;
}
[data-testid="stAppViewContainer"] {
  background: linear-gradient(120deg, rgba(15,32,39,0.85), rgba(32,58,67,0.85), rgba(44,83,100,0.85)),
              url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1920&auto=format&fit=crop') center/cover fixed;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; }

/* بطاقات */
.card {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

/* عناوين */
h1,h2,h3 { color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.35); }

/* نصوص */
p, li, label, span, .stMarkdown {
  color: #f3f7fb !important;
}

/* أزرار */
.stButton button {
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,0.18);
  background: linear-gradient(135deg, #22c1c3, #136a8a);
  transition: transform 0.08s ease, filter 0.2s ease;
}
.stButton button:hover { transform: translateY(-1px); filter: brightness(1.05); }
.stButton button:active { transform: translateY(1px) scale(0.99); }

/* مدخلات */
.stTextInput input, .stTextArea textarea, .stSelectbox div, .stRadio div {
  background: rgba(255,255,255,0.08) !important;
  color: #eaf2f6 !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
}

/* شارات */
.tag {
  display:inline-block; padding:4px 10px; border-radius:999px;
  background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.18);
  font-size:0.85rem; margin-right:6px; color:#eaf2f6;
}

/* شريط جانبي */
.css-1d391kg, [data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(15,32,39,0.9), rgba(44,83,100,0.85));
  border-right: 1px solid rgba(255,255,255,0.12);
}

/* شريط التقدم */
.stProgress > div > div > div {
  background-image: linear-gradient(90deg, #00d2ff, #3a7bd5) !important;
}
</style>
"""
st.markdown(BACKGROUND_CSS, unsafe_allow_html=True)

# ---------------------- حالة الجلسة ----------------------
if "rps_score" not in st.session_state:
    st.session_state.rps_score = {"player": 0, "cpu": 0}

if "quiz" not in st.session_state:
    st.session_state.quiz = {
        "questions": [],
        "index": 0,
        "correct": 0,
        "done": False
    }

if "guess" not in st.session_state:
    st.session_state.guess = {
        "target": random.randint(1, 50),
        "tries": 0,
        "active": True
    }

# ---------------------- بيانات المحتوى ----------------------
QUOTES = [
    "✨ من جدّ وجد، ومن زرع حصد.",
    "🚀 الطريق إلى النجاح يبدأ بخطوة.",
    "💡 التعلّم كنز يتبع صاحبه أينما ذهب.",
    "🌱 اعمل بصمت ودع نجاحك يصنع الضجيج.",
    "🧭 لا تنتظر الفرصة، اصنعها."
]
DUA = [
    "🕌 اللهم إني أسألك علماً نافعاً، ورزقاً طيباً، وعملاً متقبلاً.",
    "🤲 اللهم يسّر لي أمري واشرح صدري ووفقني لكل خير.",
    "🕊️ اللهم ارزقنا الإخلاص والقبول والبركة في الوقت."
]
FACTS = [
    "📚 هل تعلم؟ الدماغ يستهلك حوالي 20% من طاقة الجسم.",
    "🌍 قارة أفريقيا هي الأكثر تنوعاً لغوياً في العالم.",
    "🔭 يمكن للعين البشرية رؤية مجرة درب التبانة بالعين المجردة في سماء صافية."
]
JOKES = [
    "😂 المعلم: لماذا كتابك متّسخ؟ الطالب: لأن عندنا درس نظافة!",
    "😄 واحد راح للطبيب قاله: كل ما نشرب شاي نتوجع. قاله: اشرب قهوة.",
    "🤣 جاب سلّم للبحر… قال باش يطلع الموج!"
]
RIDDLES = [
    {"q": "شيء له أسنان ولا يعض؟", "a": "المشط"},
    {"q": "شيء إذا أخذت منه كبر؟", "a": "الحفرة"},
    {"q": "شيء يسمع بلا أذن ويتكلم بلا لسان؟", "a": "الهاتف"},
    {"q": "يمشي بلا قدمين ويبكي بلا عينين؟", "a": "السحاب"}
]
QUIZ_QUESTIONS = [
    {"q": "أكبر كوكب في المجموعة الشمسية؟", "a": "المشتري"},
    {"q": "عدد قارات العالم؟", "a": "7"},
    {"q": "عاصمة اليابان؟", "a": "طوكيو"},
    {"q": "مخترع المصباح الكهربائي؟", "a": "توماس إديسون"},
    {"q": "أسرع حيوان بري؟", "a": "الفهد"},
    {"q": "الغاز الذي نتنفسه للحياة؟", "a": "الأكسجين"},
    {"q": "أطول نهر في العالم؟", "a": "النيل"},
    {"q": "لغة يتحدث بها أكبر عدد من الناس كلغة أم؟", "a": "الصينية"},
    {"q": "مربع 12؟", "a": "144"},
    {"q": "عاصمة إسبانيا؟", "a": "مدريد"},
    {"q": "أقرب كوكب للشمس؟", "a": "عطارد"},
    {"q": "مؤلف كتاب الجمهورية؟", "a": "أفلاطون"},
    {"q": "بلد مشهور بالتانغو؟", "a": "الأرجنتين"},
    {"q": "سنة بها 366 يوماً؟", "a": "كبيسة"},
    {"q": "محيط يطل على اليابان؟", "a": "الهادئ"}
]

# ---------------------- وظائف مساعدة ----------------------
def hr():
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

def gen_password(length=12, with_symbols=True):
    alphabet = string.ascii_letters + string.digits + ("!@#$%^&*?" if with_symbols else "")
    return "".join(secrets.choice(alphabet) for _ in range(length))

def gen_palette(n=5):
    # يولّد ألوان HEX حلوة
    cols = []
    for _ in range(n):
        r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        cols.append(f"#{r:02x}{g:02x}{b:02x}")
    return cols

def copy_help(text):
    st.code(text, language="text")

# ---------------------- الشريط الجانبي ----------------------
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    theme = st.radio("الثيم:", ["غامق", "فاتح"], index=0, horizontal=True)
    st.markdown("<span class='tag'>بدون API</span> <span class='tag'>سهل</span> <span class='tag'>متفاعل</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📌 الأقسام")
    section = st.radio("اختر:", [
        "الترحيب", "حجر/ورقة/مقص", "كويز", "ألغاز", "نكت", "اقتباس/دعاء/معلومة",
        "تخمين الرقم", "اسم مستعار", "كلمات سر", "لوحة ألوان"
    ])

# ثيم بسيط (تأثير لوني على البطاقة)
card_bg = "rgba(255,255,255,0.08)" if theme == "غامق" else "rgba(255,255,255,0.85)"

# ---------------------- الترحيب ----------------------
if section == "الترحيب":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.markdown("### 👋 أهلاً بك!")
    st.write("هذا مركز صغير يجمع الترفيه + الفائدة. كل الأدوات تعمل **بدون مفاتيح** وبدون أي إعدادات خارجية.")
    st.write("ابدأ من الشريط الجانبي واختر القسم الذي يعجبك.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- حجر/ورقة/مقص ----------------------
if section == "حجر/ورقة/مقص":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("✊✋✌️ حجر/ورقة/مقص")
    options = ["حجر", "ورقة", "مقص"]
    user_choice = st.radio("اختر حركتك:", options, horizontal=True, index=0)
    if st.button("🎲 العب"):
        cpu = random.choice(options)
        st.write(f"🖥️ الكمبيوتر اختار: **{cpu}**")
        if cpu == user_choice:
            st.info("🤝 تعادل!")
        elif (user_choice == "حجر" and cpu == "مقص") or \
             (user_choice == "ورقة" and cpu == "حجر") or \
             (user_choice == "مقص" and cpu == "ورقة"):
            st.session_state.rps_score["player"] += 1
            st.success("🎉 ربحت!")
        else:
            st.session_state.rps_score["cpu"] += 1
            st.error("😢 خسرت!")

    st.progress(min(1.0, (st.session_state.rps_score["player"] / max(1, (st.session_state.rps_score["player"]+st.session_state.rps_score["cpu"])))))
    st.caption(f"النتيجة 👤 {st.session_state.rps_score['player']} : {st.session_state.rps_score['cpu']} 🖥️")
    if st.button("🔄 تصفير النتيجة"):
        st.session_state.rps_score = {"player": 0, "cpu": 0}
        st.success("تم التصفير ✅")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- كويز ----------------------
if section == "كويز":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("❓ مسابقة سريعة (بدون تكرار)")
    # تهيئة الأسئلة مرة واحدة
    if not st.session_state.quiz["questions"]:
        qs = QUIZ_QUESTIONS.copy()
        random.shuffle(qs)
        st.session_state.quiz["questions"] = qs
        st.session_state.quiz["index"] = 0
        st.session_state.quiz["correct"] = 0
        st.session_state.quiz["done"] = False

    qdata = None
    if not st.session_state.quiz["done"]:
        idx = st.session_state.quiz["index"]
        qdata = st.session_state.quiz["questions"][idx]
        st.subheader(f"سؤال {idx+1} من {len(st.session_state.quiz['questions'])}")
        user_ans = st.text_input("✍️ جوابك:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("تحقق"):
                if user_ans.strip():
                    if user_ans.strip() == qdata["a"]:
                        st.success("✅ صحيح!")
                        st.session_state.quiz["correct"] += 1
                    else:
                        st.error(f"❌ خطأ! الجواب الصحيح: {qdata['a']}")
                else:
                    st.warning("اكتب جوابًا أولًا 🙂")
        with col2:
            if st.button("➡️ التالي"):
                st.session_state.quiz["index"] += 1
                if st.session_state.quiz["index"] >= len(st.session_state.quiz["questions"]):
                    st.session_state.quiz["done"] = True

    if st.session_state.quiz["done"]:
        total = len(st.session_state.quiz["questions"])
        correct = st.session_state.quiz["correct"]
        st.success(f"النتيجة النهائية: {correct} / {total}")
        percent = int((correct/total)*100)
        st.progress(percent/100)
        report = f"نتيجة الكويز: {correct}/{total} ({percent}%) في تاريخ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        st.download_button("⬇️ تحميل النتيجة", data=report, file_name="quiz_result.txt")
        if st.button("🔁 إعادة الكويز"):
            st.session_state.quiz = {"questions": [], "index": 0, "correct": 0, "done": False}
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- ألغاز ----------------------
if section == "ألغاز":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("🧠 لغز عشوائي")
    rid = random.choice(RIDDLES)
    st.write(f"**{rid['q']}**")
    ans = st.text_input("إجابتك:")
    if st.button("تحقق من اللغز"):
        if ans.strip() == rid["a"]:
            st.success("🎉 صحيح! برافو 👏")
        else:
            st.error(f"❌ خطأ! الحل: {rid['a']}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- نكت ----------------------
if section == "نكت":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("😂 نكتة عشوائية")
    if st.button("🤣 هات نكتة"):
        st.info(random.choice(JOKES))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- اقتباس/دعاء/معلومة ----------------------
if section == "اقتباس/دعاء/معلومة":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("✨ لمسة يومية")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("💡 اقتباس"):
            st.success(random.choice(QUOTES))
    with colB:
        if st.button("🤲 دعاء"):
            st.info(random.choice(DUA))
    with colC:
        if st.button("📚 معلومة"):
            st.warning(random.choice(FACTS))
    # معلومة اليوم حسب التاريخ
    st.caption("🎯 معلومة/اقتباس اليوم:")
    daily = random.choice(QUOTES + DUA + FACTS)
    st.write(daily)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- تخمين الرقم ----------------------
if section == "تخمين الرقم":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("🔢 لعبة التخمين (1 إلى 50)")
    guess = st.number_input("جرّب حظك:", min_value=1, max_value=50, step=1)
    if st.button("تحقق"):
        st.session_state.guess["tries"] += 1
        t = st.session_state.guess["target"]
        if guess == t:
            st.success(f"🎉 صح! الرقم هو {t}. عدد المحاولات: {st.session_state.guess['tries']}")
            st.session_state.guess = {"target": random.randint(1, 50), "tries": 0, "active": True}
        elif guess < t:
            st.info("⬆️ أكبر شوية")
        else:
            st.info("⬇️ أصغر شوية")
    if st.button("🔄 إعادة ضبط"):
        st.session_state.guess = {"target": random.randint(1, 50), "tries": 0, "active": True}
        st.success("تم إعادة الضبط ✅")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- اسم مستعار ----------------------
if section == "اسم مستعار":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("🕹️ مولّد اسم مستعار")
    styles = ["Legend", "Shadow", "Nova", "Blaze", "Storm", "Ghost", "Falcon", "Drift", "Quantum", "Hunter"]
    addons = ["X", "_Pro", "HD", "77", "999", "_MK", "Prime", "Zero", "FX", "XR"]
    base = st.text_input("اكتب كلمة تحبها (اختياري):", "")
    if st.button("🎯 هات اسم"):
        if base.strip():
            nick = f"{base.capitalize()}{random.choice(addons)}"
        else:
            nick = f"{random.choice(styles)}{random.choice(addons)}"
        st.success(f"اسمك المقترح: **{nick}**")
        copy_help(nick)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- كلمات سر ----------------------
if section == "كلمات سر":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("🔐 مولّد كلمات سر قوية")
    length = st.slider("الطول:", 8, 32, 14)
    sym = st.checkbox("إضافة رموز (!@#...)", value=True)
    if st.button("⚡ توليد"):
        pwd = gen_password(length, sym)
        st.success("تم التوليد ✅ انسخها من الصندوق:")
        copy_help(pwd)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- لوحة ألوان ----------------------
if section == "لوحة ألوان":
    st.markdown(f"<div class='card' style='background:{card_bg}'>", unsafe_allow_html=True)
    st.header("🎨 لوحة ألوان عشوائية")
    n = st.slider("عدد الألوان:", 3, 8, 5)
    if st.button("✨ أنشئ لوحة"):
        palette = gen_palette(n)
        cols = st.columns(n)
        for i, c in enumerate(palette):
            with cols[i]:
                st.markdown(f"<div style='height:90px;width:100%;border-radius:10px;background:{c};border:1px solid rgba(255,255,255,0.4)'></div>", unsafe_allow_html=True)
                st.write(c)
                copy_help(c)
    st.markdown("</div>", unsafe_allow_html=True)
