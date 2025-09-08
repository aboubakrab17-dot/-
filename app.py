# app.py
import streamlit as st
import random
import json
from datetime import datetime

# -----------------------------
# بيانات التطبيق (قابلة للتوسع)
# -----------------------------
# لكل مستوى: قائمة من العناصر: كل عنصر = dict { 'ar': 'كلمة\جملة بالعربية', 'en': '...', 'fr': '...' }
# المحتوى مبدئي: أضف أو حرر كما تحب لاحقاً
LEVELS = {
    1: [  # كلمات أساسية
        {"ar": "قطة", "en": "cat", "fr": "chat"},
        {"ar": "كلب", "en": "dog", "fr": "chien"},
        {"ar": "كتاب", "en": "book", "fr": "livre"},
        {"ar": "بيت", "en": "house", "fr": "maison"},
        {"ar": "ماء", "en": "water", "fr": "eau"},
        {"ar": "شمس", "en": "sun", "fr": "soleil"},
        {"ar": "قلم", "en": "pen", "fr": "stylo"},
        {"ar": "تفاحة", "en": "apple", "fr": "pomme"},
    ],
    2: [  # جمل بسيطة / تركيب كلمات
        {"ar": "أنا طالب", "en": "I am a student", "fr": "Je suis étudiant"},
        {"ar": "أنا أحب القرأة", "en": "I like reading", "fr": "J'aime lire"},
        {"ar": "هو يكتب رسالة", "en": "He writes a letter", "fr": "Il écrit une lettre"},
        {"ar": "هي تشرب الماء", "en": "She drinks water", "fr": "Elle boit de l'eau"},
    ],
    3: [  # جمل متوسطه
        {"ar": "أين المكتبة؟", "en": "Where is the library?", "fr": "Où est la bibliothèque?"},
        {"ar": "الطقس جميل اليوم", "en": "The weather is nice today", "fr": "Il fait beau aujourd'hui"},
        {"ar": "أحب تعلم اللغات", "en": "I love learning languages", "fr": "J'aime apprendre des langues"},
    ],
}

# اقتراحات سريعة (كويز او افكار)
SUGGESTIONS = [
    "اعطني 5 كلمات متعلقة بالطعام",
    "علمني 5 أفعال شائعة",
    "رتب الجملة: I am a student",
    "ترجم: أين الحمام؟",
    "اختر الكلمة الصحيحة لكلمة 'قطة'",
    # يمكن توسيع القائمة حتى 50 اقتراح حسب الطلب
] + [f"اقتراح جاهز #{i}" for i in range(6, 51)]

# -----------------------------
# إعدادات الواجهة (CSS)
# -----------------------------
PAGE_CSS = """
<style>
body {
    color: #e6eef8;
}

/* خلفية جميلة */
.stApp {
    background: radial-gradient(circle at 10% 20%, #0f1724 0%, #071021 30%, #0f2540 70%);
    font-family: "Cairo", "Segoe UI", Roboto, sans-serif;
}

/*Header*/
h1 {
    font-size: 34px;
    color: #fff;
    text-align: center;
}
h2 { color: #fff; }

/* مح گفتگو شبيهة */
.chat-bubble {
    border-radius: 16px;
    padding: 14px 18px;
    margin: 10px 0;
    max-width: 88%;
    font-size: 16px;
    line-height: 1.35;
    color: #05202a;
}
.user { background: linear-gradient(90deg,#a8ff78,#78ffd6); margin-left: auto; }
.bot  { background: linear-gradient(90deg,#cfe9ff,#a0d2ff); color: #062233; }

/* الاقتراحات */
.suggestion {
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 10px;
    margin: 6px 0;
    color: #e6f6ff;
}

/* ازرار مميزة */
.big-btn button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    font-weight: 700;
    padding: 12px 18px;
    border-radius: 12px;
    border: none;
}

/* البطاقات */
.card {
    background: rgba(255,255,255,0.04);
    border-radius: 14px; padding: 12px; margin: 8px 0;
}
.small {
    font-size: 13px; color:#cfeaff;
}

/* inputs */
div.stTextInput > label, div.stTextArea > label { color: #dff1ff !important; font-weight:600; }
input, textarea { background: rgba(255,255,255,0.03) !important; color: #e9fbff !important; border-radius:10px; padding:8px; }
</style>
"""

# -----------------------------
# مساعدات ووظائف
# -----------------------------
def init_state():
    """تهيئة المتغيرات في session_state"""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"  # لغة الهدف: users learns en/fr from ar
    if "level" not in st.session_state:
        st.session_state.level = 1
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "lives" not in st.session_state:
        st.session_state.lives = 3
    if "badge" not in st.session_state:
        st.session_state.badge = []
    if "history" not in st.session_state:
        st.session_state.history = []  # قائمة الدردشات/النتائج
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "question_type" not in st.session_state:
        st.session_state.question_type = None
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "correct_in_row" not in st.session_state:
        st.session_state.correct_in_row = 0
    if "seed" not in st.session_state:
        st.session_state.seed = random.randint(1, 999999)
    if "target_language" not in st.session_state:
        st.session_state.target_language = "en"  # أو "fr"
    if "ui_theme" not in st.session_state:
        st.session_state.ui_theme = "dark"

def add_history(role, text):
    st.session_state.history.append({"when": datetime.now().isoformat(), "role": role, "text": text})

def gain_xp(amount):
    st.session_state.xp += amount
    # شارات بسيطة
    if st.session_state.xp >= 200 and "Bronze" not in st.session_state.badge:
        st.session_state.badge.append("Bronze")
    if st.session_state.xp >= 500 and "Silver" not in st.session_state.badge:
        st.session_state.badge.append("Silver")
    if st.session_state.xp >= 1000 and "Gold" not in st.session_state.badge:
        st.session_state.badge.append("Gold")

def next_level_if_ready():
    # شرط بسيط للترقية: xp >= level * 100
    if st.session_state.xp >= st.session_state.level * 100 and st.session_state.level < max(LEVELS.keys()):
        st.session_state.level += 1
        st.session_state.correct_in_row = 0
        add_history("bot", f"🎉 مبروك! انتقلت للمستوى {st.session_state.level}")
        return True
    return False

def pick_question():
    """يختار سؤال عشوائي بناء على المستوى واللغة الهدف"""
    lvl = st.session_state.level
    pool = LEVELS.get(lvl, [])
    if not pool:
        return None
    # pick random item
    item = random.choice(pool)
    # question types: multiple_choice, order_words, write_translation
    qtypes = ["multiple_choice", "order_words", "write_translation"]
    # on simple levels bias to multiple_choice
    if lvl == 1:
        weights = [0.6, 0.3, 0.1]
    elif lvl == 2:
        weights = [0.35, 0.4, 0.25]
    else:
        weights = [0.25, 0.35, 0.4]
    qtype = random.choices(qtypes, weights=weights, k=1)[0]
    st.session_state.question_type = qtype
    st.session_state.current_question = item
    st.session_state.question_index += 1
    return {"item": item, "type": qtype}

def build_multiple_choice(item):
    """يبني سؤال اختيار متعدد: من العربية للغة الهدف"""
    target = st.session_state.target_language
    correct = item[target]
    # اجابات خاطئة مختارة من مستويات اخرى
    wrong = []
    all_choices = []
    for lvl, items in LEVELS.items():
        for it in items:
            val = it[target]
            if val != correct and val not in wrong:
                wrong.append(val)
    wrong = random.sample(wrong, k=min(3, len(wrong)))
    all_choices = wrong + [correct]
    random.shuffle(all_choices)
    return {"question": item["ar"], "choices": all_choices, "answer": correct}

def build_order_words(item):
    """ابني ترتيب كلمات (word building) للغة الهدف"""
    target = st.session_state.target_language
    sentence = item[target]
    # نفصل الكلمات (نسخة بسيطة)
    tokens = sentence.replace("?", "").replace(".", "").replace("'", " ").replace("’", " ").split()
    if len(tokens) <= 1:
        # fallback to multiple choice
        return None
    shuffled = tokens.copy()
    random.shuffle(shuffled)
    return {"sentence": sentence, "tokens": tokens, "shuffled": shuffled}

def build_write_translation(item):
    """إعطاء المستخدم ترجمة ويجب كتابة ترجمة"""
    target = st.session_state.target_language
    return {"question": item["ar"], "expected": item[target]}

def check_answer(qtype, item, user_answer):
    target = st.session_state.target_language
    if qtype == "multiple_choice":
        correct = item[target]
        if user_answer.strip().lower() == correct.strip().lower():
            return True, correct
        else:
            return False, correct
    elif qtype == "order_words":
        expected = " ".join(item["target_tokens"]) if "target_tokens" in item else item[target]
        # normalize
        if user_answer.strip().lower() == expected.strip().lower():
            return True, expected
        else:
            return False, expected
    elif qtype == "write_translation":
        expected = item[target]
        if user_answer.strip().lower() == expected.strip().lower():
            return True, expected
        else:
            return False, expected
    else:
        return False, ""

# -----------------------------
# بناء الواجهة
# -----------------------------
def header():
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.title("🔹 بوت تعلم اللغات — Duolingo Lite")
    st.markdown("<div style='text-align:center; color:#cfeeff; font-weight:600;'>تعلم الإنجليزية والفرنسية من العربية — سهل، ممتع، ومكيّف مع مستواك</div>", unsafe_allow_html=True)
    # شريط الحالة
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.markdown(f"<div class='card small'>💠 مستوى: {st.session_state.level}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card small'>⭐ XP: {st.session_state.xp} | ❤️ قلوب: {st.session_state.lives}</div>", unsafe_allow_html=True)
    with col3:
        badgelist = ", ".join(st.session_state.badge) if st.session_state.badge else "لا شارات بعد"
        st.markdown(f"<div class='card small'>🏅 شارات: {badgelist}</div>", unsafe_allow_html=True)

def sidebar_settings():
    st.sidebar.title("⚙️ الإعدادات")
    st.sidebar.markdown("**اللغة الهدف**")
    st.session_state.target_language = st.sidebar.radio("اختر لغة التعلم:", ("en", "fr"), index=0)
    st.sidebar.markdown("**التعليمات**")
    st.sidebar.info("اختر اللغة التي تريد تعلمها. استعمل الاقتراحات أو اكتب سؤالك. كل إجابة صحيحة تكسبك XP، ومع زيادة XP تنتقل للمستوى التالي.")
    if st.sidebar.button("إعادة ضبط التقدم"):
        st.session_state.level = 1
        st.session_state.xp = 0
        st.session_state.lives = 3
        st.session_state.badge = []
        st.session_state.history = []
        st.success("تم إعادة الضبط!")

def suggestions_ui():
    st.markdown("### ✨ اقتراحات سريعة")
    cols = st.columns(3)
    # عرض أول 9 اقتراحات كأزرار
    for i, s in enumerate(SUGGESTIONS[:9]):
        if cols[i % 3].button(s):
            # لو ضغط المستخدم على اقتراح، نعرضه كبوت يجيب
            add_history("user", s)
            # رد بوت تجريبي — يمكن تخصيص لردود ذكية لاحقاً
            add_history("bot", f"حسناً — سأبدأ ب: {s}")
    if st.button("عرض المزيد من الاقتراحات"):
        st.write(", ".join(SUGGESTIONS))

def show_chat_history():
    # نعرض اخر 6 رسائل
    for msg in st.session_state.history[-12:]:
        cls = "bot" if msg["role"] == "bot" else "user"
        st.markdown(f"<div class='chat-bubble {cls}'>{msg['text']}</div>", unsafe_allow_html=True)

# -----------------------------
# واجهة السؤال والتقييم
# -----------------------------
def exercise_area():
    st.markdown("---")
    st.subheader("🔎 تمرين اليوم")
    # تجهيز سؤال إن لم يكن موجود
    if not st.session_state.current_question:
        q = pick_question()
        if not q:
            st.info("لا يوجد محتوى لهذا المستوى. أضف كلمات/جمل للمستويات في الكود.")
            return
    else:
        q = {"item": st.session_state.current_question, "type": st.session_state.question_type}

    item = q["item"]
    qtype = q["type"]
    target = st.session_state.target_language

    # بناء السؤال تبع النوع
    if qtype == "multiple_choice":
        mc = build_multiple_choice(item)
        st.markdown(f"<div class='card'>🔤 **ترجم الكلمة:** <b style='color:#fff'>{mc['question']}</b></div>", unsafe_allow_html=True)
        choice = st.radio("اختر الإجابة الصحيحة:", mc["choices"], key=f"mc_{st.session_state.question_index}")
        if st.button("✅ تأكيد الإجابة", key=f"confirm_mc_{st.session_state.question_index}"):
            correct = mc["answer"]
            if choice.strip().lower() == correct.strip().lower():
                add_history("user", choice)
                add_history("bot", "✅ إجابة صحيحة — أحسنت!")
                gain_xp(20)
                st.session_state.correct_in_row += 1
            else:
                add_history("user", choice)
                add_history("bot", f"❌ خطأ — الإجابة الصحيحة: **{correct}**")
                st.session_state.lives -= 1
                st.session_state.correct_in_row = 0
            st.session_state.current_question = None
            next_level_if_ready()

    elif qtype == "order_words":
        built = build_order_words(item)
        if not built:
            # fallback
            st.write("خطأ: هذا التمرين غير مناسب لهذا العنصر، سيتم تحويله لتمرين كتابة.")
            st.session_state.question_type = "write_translation"
            return
        target_sentence = built["sentence"]
        # نخزن tokens للمعاينة والتحقق بعدها
        st.session_state.current_question["target_tokens"] = built["tokens"]
        st.markdown(f"<div class='card'>🔤 **ركب الجملة الصحيحة ({'إنجليزي' if target=='en' else 'فرنسي'}):** <b style='color:#fff'>{item['ar']}</b></div>", unsafe_allow_html=True)
        st.write("اسحب الكلمات بالترتيب لي يعطيك الجملة الصحيحة (هنا نستخدم أزرار بسيطة):")
        # أزرار لاختيار ترتيب (نسخة مبسطة بدون drag/drop)
        tokens = built["shuffled"]
        # حالة الاختيارات الحالية
        if "order_state" not in st.session_state:
            st.session_state.order_state = []
        col_count = len(tokens)
        cols = st.columns(col_count)
        for i, t in enumerate(tokens):
            if cols[i].button(t, key=f"tok_{st.session_state.question_index}_{i}"):
                st.session_state.order_state.append(t)
        st.write("الترتيب الحالي: ", " | ".join(st.session_state.order_state))
        if st.button("✅ تحقق من الترتيب", key=f"check_order_{st.session_state.question_index}"):
            answer = " ".join(st.session_state.order_state).strip()
            expected = " ".join(built["tokens"]).strip()
            add_history("user", answer or "(فارغ)")
            if answer.lower() == expected.lower():
                add_history("bot", "✅ رائع! الترتيب صحيح.")
                gain_xp(30)
                st.session_state.correct_in_row += 1
            else:
                add_history("bot", f"❌ ليس صحيحاً. الجملة الصحيحة: **{expected}**")
                st.session_state.lives -= 1
                st.session_state.correct_in_row = 0
            # تنظيف للحل القادم
            st.session_state.order_state = []
            st.session_state.current_question = None
            next_level_if_ready()

    elif qtype == "write_translation":
        write = build_write_translation(item)
        st.markdown(f"<div class='card'>✍️ **اكتب ترجمة باللغة {'الإنجليزية' if target=='en' else 'الفرنسية'}:</b> <b style='color:#fff'>{write['question']}</b></div>", unsafe_allow_html=True)
        answer = st.text_input("اكتب ترجمتك هنا:", key=f"write_{st.session_state.question_index}")
        if st.button("✅ تحقق", key=f"check_write_{st.session_state.question_index}"):
            add_history("user", answer or "(فارغ)")
            expected = write["expected"]
            if answer.strip().lower() == expected.strip().lower():
                add_history("bot", "✅ ممتاز! ترجمتك صحيحة.")
                gain_xp(25)
                st.session_state.correct_in_row += 1
            else:
                add_history("bot", f"❌ ليس دقيقاً. الإجابة: **{expected}**")
                st.session_state.lives -= 1
                st.session_state.correct_in_row = 0
            st.session_state.current_question = None
            next_level_if_ready()
    else:
        st.write("نوع سؤال غير معروف.")

    # تحقق من حالة القلوب (lives)
    if st.session_state.lives <= 0:
        st.error("💔 انتهت قلوبك! أعد تشغيل المستوى أو اضغط إعادة المحاولة لإستعادة القلوب.")
        if st.button("إعادة المحاولة (إعادة 3 قلوب)"):
            st.session_state.lives = 3
            st.session_state.current_question = None
            st.session_state.correct_in_row = 0

# -----------------------------
# صفحة النتائج والملف الشخصي
# -----------------------------
def profile_area():
    st.markdown("---")
    st.subheader("👤 ملفك")
    st.markdown(f"- المستوى: **{st.session_state.level}**")
    st.markdown(f"- XP: **{st.session_state.xp}**")
    st.markdown(f"- قلوب: {'❤️'*st.session_state.lives}{'🖤'*(3-st.session_state.lives)}")
    st.markdown(f"- شارات: {', '.join(st.session_state.badge) if st.session_state.badge else 'لا شارات'}")
    if st.button("تحميل تقرير التقدم (JSON)"):
        st.download_button("تحميل التقدم", data=json.dumps(st.session_state.history, ensure_ascii=False, indent=2), file_name="progress.json", mime="application/json")

# -----------------------------
# الرئيسية
# -----------------------------
def main():
    st.set_page_config(page_title="بوت تعلم اللغات", layout="wide")
    init_state()
    header()
    sidebar_settings()

    left, right = st.columns([2, 1])
    with left:
        # دردشة وتاريخ الأسئلة
        show_chat_history()
        exercise_area()
    with right:
        st.markdown("### 🔎 سريع")
        suggestions_ui()
        st.markdown("### 🏆 إنجازات")
        st.write(", ".join(st.session_state.badge) if st.session_state.badge else "لا إنجازات بعد — ابدأ الآن!")
        st.markdown("### ⚡ نصائح")
        st.info("ركز على التكرار. كلما جاوبت صحيح تحصل XP وتنتقل للمستوى التالي. استعمل الاقتراحات لتجربة تمارين مختلفة.")
        st.markdown("### 🔢 الحالة الحالية")
        profile_area()

    # استجابة عند الترقية
    if st.session_state.level > 1:
        st.success(f"مبروك! أنت الآن في المستوى {st.session_state.level}")

if __name__ == "__main__":
    main()
