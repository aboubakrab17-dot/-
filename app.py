# app.py
# متطلبات: streamlit, Pillow
# pip install streamlit Pillow

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import json
from io import BytesIO
from datetime import datetime

# ---------------------------
# بيانات دروس وكلمات (قابلة للتعديل/التوسيع)
# ---------------------------
LESSONS = {
    "English": [
        {
            "id": "en_1",
            "title": "Greetings & Basics",
            "examples": [
                {"ar": "مرحبا", "target": "Hello"},
                {"ar": "مع السلامة", "target": "Goodbye"},
                {"ar": "شكرا", "target": "Thank you"},
                {"ar": "من فضلك", "target": "Please"},
                {"ar": "نعم", "target": "Yes"},
                {"ar": "لا", "target": "No"}
            ],
            "sentences": [
                {"ar": "كيف حالك؟", "target": "How are you?"},
                {"ar": "أنا بخير، شكراً", "target": "I'm fine, thank you"}
            ]
        },
        {
            "id": "en_2",
            "title": "Daily Actions",
            "examples": [
                {"ar": "آكل", "target": "I eat"},
                {"ar": "أقرأ", "target": "I read"},
                {"ar": "أعمل", "target": "I work"},
                {"ar": "أنام", "target": "I sleep"}
            ],
            "sentences": [
                {"ar": "أنا أذهب إلى المدرسة", "target": "I go to school"},
                {"ar": "هو يقرأ كتاباً", "target": "He reads a book"}
            ]
        },
    ],
    "French": [
        {
            "id": "fr_1",
            "title": "Salutations & Bases",
            "examples": [
                {"ar": "مرحبا", "target": "Bonjour"},
                {"ar": "مع السلامة", "target": "Au revoir"},
                {"ar": "شكرا", "target": "Merci"},
                {"ar": "من فضلك", "target": "S'il vous plaît"},
                {"ar": "نعم", "target": "Oui"},
                {"ar": "لا", "target": "Non"}
            ],
            "sentences": [
                {"ar": "كيف حالك؟", "target": "Comment ça va?"},
                {"ar": "أنا بخير، شكراً", "target": "Je vais bien, merci"}
            ]
        },
        {
            "id": "fr_2",
            "title": "Actions journalières",
            "examples": [
                {"ar": "آكل", "target": "Je mange"},
                {"ar": "أقرأ", "target": "Je lis"},
                {"ar": "أعمل", "target": "Je travaille"},
                {"ar": "أنام", "target": "Je dors"}
            ],
            "sentences": [
                {"ar": "أنا أذهب إلى المدرسة", "target": "Je vais à l'école"},
                {"ar": "هو يقرأ كتاباً", "target": "Il lit un livre"}
            ]
        },
    ]
}

# اقتراحات سريعة (50 اقتراح منسق)
SUGGESTIONS = [
    "اعطني جملة يومية لترديدها",
    "علمني 5 كلمات إنجليزية مفيدة",
    "علمني 5 كلمات فرنسية مفيدة",
    "اختبرني على التحيات",
    "اختبرني على الأفعال اليومية",
    "رتّب الجملة التالية",
    "املأ الفراغ: I ____ to school",
    "اختر الترجمة الصحيحة لكلمة 'Hello'",
    "علّمني اسم أيام الأسبوع بالعربية والإنجليزية",
    "علّمني الأرقام حتى 10",
    "ترجم: كيف حالك؟",
    "أعطني 3 جمل بسيطة بالإنجليزية",
    "أعطني 3 جمل بسيطة بالفرنسية",
    "مرّني على النطق: Thank you",
    "علّمني كلمات للسفر",
    "علّمني عبارات عند الطلب في مطعم",
    "اختبرني على القواعد: a/an",
    "أعطني نصيحة لتعلم اللغة",
    "علّمني عبارات للتعارف",
    "اسألني ترجمة كلمة عشوائية",
    "علّمني صيغة الماضي للأفعال الشائعة",
    "علّمني كيفية السؤال عن الاتجاه",
    "أعطني حوار بسيط للترحيب",
    "علّمني كيفية تقديم نفسك",
    "أعطني 5 صفات شخصية بالعربية والإنجليزية",
    "علّمني كلمات الطقس",
    "اختبرني على العائلات (family)",
    "علّمني أفعال خاطئة شائعة",
    "رتب الجملة: 'to / I / school / go'",
    "املأ الفراغ: She ____ (eat/eats) an apple",
    "اختر الصحيح: 'Their/There/They're'",
    "علّمني كلمات العمل (office)",
    "علّمني كلمات في المطبخ",
    "علّمني مفرد وجمع لكلمات",
    "علّمني عبارات طبية بسيطة",
    "أعطني مثال على سؤال وإجابته",
    "علّمني كلمات المشاعر (happy, sad...)",
    "عطي اختبار سريع 5 أسئلة",
    "علّمني كلمات حول الأكل",
    "علّمني كلمات حول الأوقات",
    "رتّب الكلمات لتكوين سؤال",
    "علّمني أفعال مساعده (can, must)",
    "علّمني كيفية قول 'أحب' و 'لا أحب'",
    "أعطني قائمة مألوفة من 10 كلمات",
    "علّمني كلمات المواصلات"
]
# ---------------------------
# مساعدة واجهة (CSS)
# ---------------------------
st.set_page_config(page_title="بوت تعلم لغات - شبيه Duolingo", page_icon="🦉", layout="wide")
APP_CSS = """
<style>
:root {
  --bubble-user: linear-gradient(90deg,#8df5c8,#2bd59f);
  --bubble-bot: linear-gradient(90deg,#b6e0ff,#7aa8ff);
  --bg: linear-gradient(180deg, #0f1724 0%, #0b1220 100%);
  --card: rgba(255,255,255,0.03);
}
body, .stApp { background: var(--bg); font-family: 'Cairo', sans-serif; color: #e6eef8; }
h1, h2, h3 { color: #fff; }
.chat-bubble {
  padding: 14px 18px;
  border-radius: 16px;
  margin: 8px 0;
  max-width: 86%;
  font-size: 1.05rem;
}
.user { background: var(--bubble-user); color: #05221a; margin-left: auto; border-bottom-right-radius: 6px; }
.bot { background: var(--bubble-bot); color: #04213b; border-bottom-left-radius: 6px; }
.sidebar-card { background: var(--card); padding: 12px; border-radius: 12px; color: #dfefff; }
.btn-primary { background: linear-gradient(90deg,#00c6ff,#0072ff); color:white; padding:10px 14px; border-radius:10px; }
.small-muted { color: #9fb0cc; font-size:0.9rem; }
.suggestion { background: rgba(255,255,255,0.06); padding:10px; border-radius:10px; margin:6px 0; color:#fff; }
.progress-box { background: rgba(255,255,255,0.03); padding:10px; border-radius:12px; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# ---------------------------
# جسد التطبيق / حالة الجلسة
# ---------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "hearts" not in st.session_state:
    st.session_state.hearts = 5
if "level" not in st.session_state:
    st.session_state.level = 1
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = None
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of dicts: {"who": "user"/"bot","text": "...", "time": "..."}
if "history" not in st.session_state:
    st.session_state.history = []
if "progress" not in st.session_state:
    st.session_state.progress = 0  # 0-100 percent in current lesson

# ---------------------------
# وظائف مساعدة
# ---------------------------
def add_message(who, text):
    st.session_state.messages.append({"who": who, "text": text, "time": datetime.now().strftime("%H:%M")})

def add_xp(points):
    st.session_state.xp += points
    # Level up every 200 XP
    next_level_xp = st.session_state.level * 200
    if st.session_state.xp >= next_level_xp:
        st.session_state.level += 1
        add_message("bot", f"🎉 مبارك! وصلت للمستوى {st.session_state.level}! لقد ربحت مهارة جديدة.")
        st.session_state.xp = st.session_state.xp - next_level_xp

def lose_heart():
    st.session_state.hearts = max(0, st.session_state.hearts - 1)
    if st.session_state.hearts == 0:
        add_message("bot", "💤 انتهت القلوب! استرح وانطلق من جديد بعد قليل (أعد الصفحة أو اضغط إعادة تعيين القلوب).")

def reset_hearts():
    st.session_state.hearts = 5

def pick_random_example(lang):
    lesson_list = LESSONS.get(lang, [])
    if not lesson_list: return None
    lesson = random.choice(lesson_list)
    word = random.choice(lesson["examples"])
    return lesson, word

def save_progress_snapshot():
    st.session_state.history.append({
        "time": datetime.now().isoformat(),
        "xp": st.session_state.xp,
        "level": st.session_state.level,
        "hearts": st.session_state.hearts,
        "progress": st.session_state.progress,
        "lang": st.session_state.lang
    })

# تمارين
def exercise_translate(ar_text, target_text):
    # نعرض للمستخدم النص العربي ويكتب الترجمة (target)
    ans = st.text_input("✍️ اكتب الترجمة هنا (باللغة المختارة):", key=f"translate_{random.randint(0,999999)}")
    if st.button("تحقق ✅", key=f"check_trans_{random.randint(0,999999)}"):
        user = ans.strip()
        if not user:
            st.warning("اكتب إجابتك أولا")
            return False
        if user.lower() == target_text.lower():
            add_message("bot", f"✅ ممتاز! الإجابة صحيحة: `{target_text}`")
            add_xp(15)
            st.success("✅ صحيح! +15 XP")
            return True
        else:
            lose_heart()
            add_message("bot", f"❌ تقريباً: الإجابة الصحيحة كانت `{target_text}`")
            st.error(f"❌ خاطئ. الإجابة الصحيحة: {target_text}. -1 قلب")
            return False

def exercise_multiple_choice(prompt_text, choices, correct):
    st.write("📝 السؤال:")
    st.info(prompt_text)
    choice = st.radio("اختر الإجابة الصحيحة:", choices, key=f"mc_{random.randint(0,999999)}")
    if st.button("تحقق ✅", key=f"mc_check_{random.randint(0,999999)}"):
        if choice == correct:
            add_message("bot", f"✅ ممتاز! `{correct}` هي الإجابة الصحيحة.")
            add_xp(10)
            st.success("✅ صحيح! +10 XP")
            return True
        else:
            lose_heart()
            add_message("bot", f"❌ للأسف ... الإجابة الصحيحة: `{correct}`")
            st.error(f"❌ خاطئ. الإجابة الصحيحة: {correct}. -1 قلب")
            return False

def exercise_fill_blank(sentence_with_blank, answer):
    st.write("📝 املأ الفراغ:")
    st.info(sentence_with_blank)
    user = st.text_input("أكمل الفراغ هنا:", key=f"fb_{random.randint(0,999999)}")
    if st.button("تحقق ✅", key=f"fb_check_{random.randint(0,999999)}"):
        if user.strip().lower() == answer.strip().lower():
            add_message("bot", f"✅ ممتاز! الإجابة: `{answer}`")
            add_xp(12)
            st.success("✅ صحيح! +12 XP")
            return True
        else:
            lose_heart()
            add_message("bot", f"❌ الإجابة الصحيحة: `{answer}`")
            st.error(f"❌ خاطئ. الإجابة الصحيحة: {answer}. -1 قلب")
            return False

def exercise_order_words(target_sentence):
    # نكسر الجملة لكلمات ونخلط ونطلب من المستخدم ترتيبها بالضغط
    words = target_sentence.split()
    shuffled = words[:]
    random.shuffle(shuffled)
    st.write("🧩 رتب الكلمات لتكوين الجملة الصحيحة:")
    st.write("اضغط على الكلمات بالترتيب (ستظهر في الحقل أسفل)")
    if "order_choice" not in st.session_state:
        st.session_state.order_choice = []
        st.session_state.order_shuffled = shuffled
    col1, col2 = st.columns([3,2])
    with col1:
        for i, w in enumerate(st.session_state.order_shuffled):
            if st.button(w, key=f"wordbtn_{i}_{random.randint(0,9999)}"):
                st.session_state.order_choice.append(w)
    with col2:
        st.write("تشكيلك:")
        st.write(" > " + " ".join(st.session_state.order_choice))
        if st.button("مسح الترتيب", key=f"clear_ord_{random.randint(0,9999)}"):
            st.session_state.order_choice = []
    if st.button("تحقق الترتيب ✅", key=f"check_ord_{random.randint(0,9999)}"):
        assembled = " ".join(st.session_state.order_choice)
        if assembled.strip().lower() == target_sentence.strip().lower():
            add_message("bot", f"✅ ترتيب ممتاز! `{target_sentence}`")
            st.success("✅ صحيح! +18 XP")
            add_xp(18)
            st.session_state.order_choice = []
            return True
        else:
            lose_heart()
            add_message("bot", f"❌ لم يكن الترتيب صحيحاً. الإجابة الصحيحة: `{target_sentence}`")
            st.error(f"❌ خاطئ. الإجابة الصحيحة: {target_sentence}. -1 قلب")
            st.session_state.order_choice = []
            return False

# ---------------------------
# الواجهة الرئيسية
# ---------------------------
def header():
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("<h1 style='margin-bottom:0.2rem;'>🦉 البوت الشاب — تعلم الإنجليزية & الفرنسية</h1>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>اختَر اللغة ثم ابدأ الدرس — تجربة قصيرة ومرحة مثل Duolingo</div>", unsafe_allow_html=True)
    with col2:
        # Status card
        st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
        st.markdown(f"<b>لغة:</b> {st.session_state.lang}<br><b>المستوى:</b> {st.session_state.level}<br><b>XP:</b> {st.session_state.xp} • <b>قلوب:</b> {'❤'*st.session_state.hearts}</div>", unsafe_allow_html=True)
        st.markdown("", unsafe_allow_html=True)

def sidebar():
    st.sidebar.title("⚙️ الإعدادات السريعة")
    lang_choice = st.sidebar.selectbox("اختر اللغة المراد تعلمها:", ["English", "French"], index=0 if st.session_state.lang=="English" else 1)
    st.session_state.lang = lang_choice
    st.sidebar.markdown("---")
    st.sidebar.subheader("الحالة")
    st.sidebar.write(f"XP: {st.session_state.xp}")
    st.sidebar.write(f"مستوى: {st.session_state.level}")
    st.sidebar.write("قلوب: " + ("❤ " * st.session_state.hearts))
    if st.sidebar.button("🔄 إعادة تعيين القلوب"):
        reset_hearts()
        st.sidebar.success("✅ تم إعادة تعيين القلوب")
    if st.sidebar.button("📥 حفظ لقطة تقدم"):
        save_progress_snapshot()
        st.sidebar.success("✅ حفظت لقطة التقدم")
    st.sidebar.markdown("---")
    st.sidebar.subheader("معلومات ومساعدة")
    st.sidebar.write("هذا التطبيق تجريبي، مصمم لتعليم المفردات وقواعد بسيطة. يمكنك تطوير المحتوى بسرعة بإضافة دروس جديدة داخل LESSONS.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("اقتراحات سريعة")
    # عرض عدد محدود من الاقتراحات
    for s in SUGGESTIONS[:8]:
        if st.sidebar.button(s, key=f"sug_{SUGGESTIONS.index(s)}"):
            add_message("user", s)
            handle_user_query(s)

# ---------------------------
# معالجة رسالة المستخدم (مركز التمارين)
# ---------------------------
def handle_user_query(text):
    # البوت يفسر ويختار تمرين أو يرد إجابة سريعة
    lang = st.session_state.lang
    lower = text.strip().lower()

    # بعض أوامر محددة:
    if "اقترح" in lower or "اعطني" in lower or "علمني" in lower:
        # مثال: اعطني 5 كلمات إنجليزية مفيدة
        if "5 كلمات" in lower or "5 كلمات" in text:
            # نجيب 5 كلمات عشوائية من دروس اللغة
            words = []
            for lesson in LESSONS[lang]:
                words += [ex["target"] for ex in lesson["examples"]]
            sample = random.sample(words, min(5, len(words)))
            add_message("bot", f"✨ هنا 5 كلمات مفيدة ({lang}): " + ", ".join(sample))
            return

    # تمرين عشوائي بسيط
    choice = random.choice(["translate", "mc", "fill", "order", "sentence"])
    if choice == "translate":
        lesson, ex = pick_random_example(lang)
        add_message("bot", f"📝 ترجمة: {ex['ar']} → ؟")
        st.session_state.pending = {"type":"translate","ar":ex["ar"], "target":ex["target"]}
    elif choice == "mc":
        # multiple choice: نأخذ كلمة ونولد 3 خيارات خاطئة
        lesson, ex = pick_random_example(lang)
        correct = ex["target"]
        # جمع المرشحات
        pool = []
        for ls in LESSONS[lang]:
            pool += [e["target"] for e in ls["examples"]]
        pool = list(set(pool))
        pool.remove(correct)
        wrongs = random.sample(pool, min(3, len(pool)))
        choices = wrongs + [correct]
        random.shuffle(choices)
        add_message("bot", f"❓ اختر الترجمة الصحيحة لكلمة: {ex['ar']}")
        st.session_state.pending = {"type":"mc","prompt":ex["ar"], "choices":choices, "correct":correct}
    elif choice == "fill":
        # pick sentence and replace word with blank
        lesson = random.choice(LESSONS[lang])
        sent = random.choice(lesson["sentences"])
        target = sent["target"]
        # اختار كلمة داخل target للفراغ (واحدة من الكلمات)
        words = target.split()
        idx = random.randint(0, len(words)-1)
        answer = words[idx].strip(".,?")
        blank_sentence = " ".join([("____" if i==idx else w) for i,w in enumerate(words)])
        add_message("bot", f"🧩 املأ الفراغ: {blank_sentence}")
        st.session_state.pending = {"type":"fill","sentence":blank_sentence,"answer":answer}
    elif choice == "order":
        lesson = random.choice(LESSONS[lang])
        sent = random.choice(lesson["sentences"])
        add_message("bot", f"🔀 رتب الجملة: {sent['ar']} → {sent['target']}")
        st.session_state.pending = {"type":"order", "target":sent["target"]}
    elif choice == "sentence":
        # عرض جملة واطلب ترجمتها
        lesson = random.choice(LESSONS[lang])
        sent = random.choice(lesson["sentences"])
        add_message("bot", f"🗣️ ترجم الجملة: {sent['ar']}")
        st.session_state.pending = {"type":"translate","ar":sent["ar"], "target":sent["target"]}

# ---------------------------
# واجهة الدرس وواجهة المحادثة
# ---------------------------

def main_interface():
    header()
    sidebar()

    # تخطيط الصفحة الرئيسي: يمين - لوحة الدردشة، يسار - اقتراحات/درس
    left, right = st.columns([3,1])

    with left:
        # صندوق الدردشة
        st.markdown("<div style='padding:10px; border-radius:12px; background: rgba(255,255,255,0.02);'>", unsafe_allow_html=True)
        # عرض الرسائل
        for msg in st.session_state.messages:
            who = msg["who"]
            cls = "user" if who=="user" else "bot"
            content = msg["text"]
            time = msg["time"]
            if who == "user":
                st.markdown(f"<div class='chat-bubble user'>{content}<div style='font-size:0.8rem; opacity:0.7; margin-top:6px'>{time}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble bot'>{content}<div style='font-size:0.8rem; opacity:0.7; margin-top:6px'>{time}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # حقل إرسال المستخدم
        user_input = st.text_input("اكتب رسالتك أو اضغط اقتراح:", key="user_text")
        col1, col2 = st.columns([8,2])
        with col1:
            pass
        with col2:
            if st.button("✈️ إرسال"):
                if user_input.strip():
                    add_message("user", user_input)
                    handle_user_query(user_input)
                    st.session_state.user_text = ""
                else:
                    st.warning("اكتب شيئًا أو اختر اقتراحًا!")

        st.markdown("---")
        # إذا كان هناك تمرين قيد الانتظار، نعرضه
        pending = st.session_state.get("pending", None)
        if pending:
            ptype = pending.get("type")
            if ptype == "translate":
                st.markdown("### 📝 تمرين: الترجمة")
                st.info(f"ترجم: **{pending['ar']}**")
                ans = st.text_input("✍️ اكتب الترجمة:", key=f"pending_translate_{random.randint(0,999999)}")
                if st.button("تحقق من الترجمة ✅", key=f"pending_trans_btn_{random.randint(0,999999)}"):
                    if ans.strip().lower() == pending["target"].strip().lower():
                        add_message("bot", f"✅ أحسنت! الإجابة: `{pending['target']}`")
                        add_xp(15)
                        st.success("✅ صحيح! +15 XP")
                        st.session_state.pending = None
                    else:
                        lose_heart()
                        add_message("bot", f"❌ الإجابة الصحيحة: `{pending['target']}`")
                        st.error(f"❌ خاطئ. الإجابة الصحيحة: {pending['target']}. -1 قلب")
                        st.session_state.pending = None
            elif ptype == "mc":
                st.markdown("### ❓ تمرين: اختيار متعدد")
                st.info(f"اختر الترجمة الصحيحة لـ: **{pending['prompt']}**")
                choice = st.radio("الخيارات:", pending["choices"], key=f"pending_mc_{random.randint(0,999999)}")
                if st.button("تحقق ✅", key=f"pending_mc_btn_{random.randint(0,999999)}"):
                    if choice == pending["correct"]:
                        add_message("bot", f"✅ ممتاز! `{pending['correct']}`")
                        add_xp(10)
                        st.success("✅ صحيح! +10 XP")
                    else:
                        lose_heart()
                        add_message("bot", f"❌ الإجابة الصحيحة: `{pending['correct']}`")
                        st.error(f"❌ خاطئ. الإجابة الصحيحة: {pending['correct']}. -1 قلب")
                    st.session_state.pending = None
            elif ptype == "fill":
                st.markdown("### 🧩 تمرين: املأ الفراغ")
                st.info(pending["sentence"])
                ans = st.text_input("أكمل الفراغ:", key=f"pending_fill_{random.randint(0,999999)}")
                if st.button("تحقق ✅", key=f"pending_fill_btn_{random.randint(0,999999)}"):
                    if ans.strip().lower() == pending["answer"].strip().lower():
                        add_message("bot", f"✅ أحسنت! الإجابة: `{pending['answer']}`")
                        add_xp(12)
                        st.success("✅ صحيح! +12 XP")
                    else:
                        lose_heart()
                        add_message("bot", f"❌ الإجابة الصحيحة: `{pending['answer']}`")
                        st.error(f"❌ خاطئ. الإجابة الصحيحة: {pending['answer']}. -1 قلب")
                    st.session_state.pending = None
            elif ptype == "order":
                st.markdown("### 🔀 تمرين: رتب الكلمات")
                st.info(f"قم بترتيب الجملة التالية بالإنجليزية/الفرنسية: (على شكل كلمات)")
                target = pending["target"]
                # نستعمل نفس دالة الترتيب لكن في واجهة بسيطة هنا
                words = target.split()
                shuffled = words[:]
                random.shuffle(shuffled)
                if "ord_tmp" not in st.session_state or st.session_state.get("ord_target")!=target:
                    st.session_state.ord_tmp = []
                    st.session_state.ord_shuffled = shuffled
                    st.session_state.ord_target = target
                cols = st.columns([1]*3)
                # عرض أزرار
                for i,w in enumerate(st.session_state.ord_shuffled):
                    if cols[i%3].button(w, key=f"ordbtn_{i}_{random.randint(0,9999)}"):
                        st.session_state.ord_tmp.append(w)
                st.write("تشكيلك: " + " ".join(st.session_state.ord_tmp))
                if st.button("مسح التشكيل"):
                    st.session_state.ord_tmp = []
                if st.button("تحقق الترتيب"):
                    assembled = " ".join(st.session_state.ord_tmp).strip()
                    if assembled.lower() == target.lower():
                        add_message("bot", f"✅ ترتيب ممتاز! `{target}`")
                        add_xp(18)
                        st.success("✅ صحيح! +18 XP")
                    else:
                        lose_heart()
                        add_message("bot", f"❌ الترتيب لم يكن صحيحًا. الصحيح: `{target}`")
                        st.error(f"❌ خاطئ. الإجابة الصحيحة: {target}. -1 قلب")
                    st.session_state.pending = None
                    st.session_state.ord_tmp = []
                    st.session_state.ord_shuffled = []
            else:
                # نوع غير معروف
                add_message("bot", "خطأ داخلي: نوع تمرين غير معروف.")
                st.session_state.pending = None

    with right:
        # لوحة جانبية: الدرس الحالي، اقتراحات سريعة، تقدم
        st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
        st.subheader("🏁 الدرس السريع")
        # اختيار الدرس من القائمة
        lessons = LESSONS[st.session_state.lang]
        lesson_titles = [f"{l['title']}" for l in lessons]
        choice = st.selectbox("اختر درس:", lesson_titles, key="lesson_select")
        st.session_state.current_lesson = lessons[lesson_titles.index(choice)]
        st.markdown(f"**درس:** {st.session_state.current_lesson['title']}")
        st.write("أمثلة كلمات (مقتطف):")
        exs = st.session_state.current_lesson["examples"]
        for ex in exs[:6]:
            st.markdown(f"- `{ex['target']}` — {ex['ar']}")
        st.markdown("---")
        # Progress and actions
        st.markdown("<div class='progress-box'>", unsafe_allow_html=True)
        st.write(f"التقدّم في الدرس: {st.session_state.progress}%")
        st.progress(min(100, max(0, st.session_state.progress)))
        if st.button("ابدأ تمرين عشوائي"):
            # نطلق تمرين
            add_message("user", "ابدأ تمرين")
            handle_user_query("ابدأ تمرين")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("✨ اقتراحات سريعة")
        for i, s in enumerate(SUGGESTIONS[:12]):
            if st.button(s, key=f"right_sug_{i}"):
                add_message("user", s)
                handle_user_query(s)
        st.markdown("---")
        st.subheader("🔧 أدوات")
        if st.button("💾 تنزيل تقدم الجلسة"):
            # نصيحة: نحفظ كـ JSON
            snapshot = {
                "messages": st.session_state.messages,
                "history": st.session_state.history,
                "stats": {
                    "xp": st.session_state.xp,
                    "level": st.session_state.level,
                    "hearts": st.session_state.hearts,
                    "lang": st.session_state.lang
                }
            }
            bytes_out = BytesIO()
            bytes_out.write(json.dumps(snapshot, ensure_ascii=False, indent=2).encode("utf-8"))
            bytes_out.seek(0)
            st.download_button("🔽 حمل ملف الجلسة (json)", data=bytes_out, file_name="session_snapshot.json", mime="application/json")
        if st.button("♻️ إعادة ضبط كل شيء"):
            # إعادة ضبط مع حفظ
            save_progress_snapshot()
            st.session_state.xp = 0
            st.session_state.hearts = 5
            st.session_state.level = 1
            st.session_state.messages = []
            st.session_state.pending = None
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# الصفحة الرئيسية / تشغيل
# ---------------------------
def run_app():
    main_interface()

# Start with a welcoming message at first run
if len(st.session_state.messages) == 0:
    add_message("bot", "مرحبًا بك! اختر اللغة واستخدم الاقتراحات أو اكتب سؤالك. أنا هنا أساعدك في تعلم الكلمات والجُمل والتمارين الخفيفة — تجربة سريعة مرحة مثل Duolingo 😊")
    st.experimental_rerun()

run_app()
