import streamlit as st
import random

# --- إعداد واجهة التطبيق ---
st.set_page_config(page_title="تعلم اللغات - Duolingo Clone", page_icon="🌍", layout="centered")

# --- CSS للتصميم ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1f4037, #99f2c8);
        color: white;
    }
    .user-msg {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: right;
        max-width: 70%;
        margin-left: auto;
    }
    .bot-msg {
        background-color: #2196F3;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: left;
        max-width: 70%;
        margin-right: auto;
    }
    .status-bar {
        background: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 15px;
        text-align: center;
        font-size: 18px;
    }
    .stTextInput > div > div > input {
        background-color: #1e1e1e;
        color: white;
        border-radius: 10px;
        border: 1px solid #555;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- بيانات التطبيق ---
words = {
    "ar_en": {
        "شمس": "sun",
        "قمر": "moon",
        "ماء": "water",
        "كتاب": "book",
        "قطة": "cat",
        "كلب": "dog",
    },
    "ar_fr": {
        "شمس": "soleil",
        "قمر": "lune",
        "ماء": "eau",
        "كتاب": "livre",
        "قطة": "chat",
        "كلب": "chien",
    }
}

sentences = [
    ("I like reading", ["I", "like", "reading"]),
    ("The cat drinks water", ["The", "cat", "drinks", "water"]),
    ("The sun is bright", ["The", "sun", "is", "bright"])
]

# --- تخزين الجلسة ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "hearts" not in st.session_state:
    st.session_state.hearts = 3
if "mode" not in st.session_state:
    st.session_state.mode = "menu"
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# --- تحديث المستوى ---
def update_level():
    if st.session_state.xp >= st.session_state.level * 50:
        st.session_state.level += 1
        st.session_state.chat_history.append(("bot", f"🎉 مبروك! انتقلت للمستوى {st.session_state.level}"))

# --- تمرين: ترجمة ---
def translation_exercise(lang="ar_en"):
    word, answer = random.choice(list(words[lang].items()))
    st.session_state.current_question = ("translation", word, answer)
    st.session_state.chat_history.append(("bot", f"✍️ ترجم الكلمة: **{word}**"))

# --- تمرين: اختيارات متعددة ---
def mcq_exercise(lang="ar_en"):
    word, answer = random.choice(list(words[lang].items()))
    options = list(words[lang].values())
    random.shuffle(options)
    if answer not in options[:3]:
        options = options[:3] + [answer]
    random.shuffle(options)
    st.session_state.current_question = ("mcq", word, answer, options)
    st.session_state.chat_history.append(("bot", f"🎯 اختر الترجمة الصحيحة لكلمة: **{word}**"))

# --- تمرين: تركيب جملة ---
def sentence_exercise():
    correct_sentence, words_list = random.choice(sentences)
    shuffled = words_list[:]
    random.shuffle(shuffled)
    st.session_state.current_question = ("sentence", correct_sentence, shuffled)
    st.session_state.chat_history.append(("bot", f"🔤 رتب الكلمات لتكوين الجملة الصحيحة: {', '.join(shuffled)}"))

# --- التحقق من الإجابة ---
def check_answer(user_msg):
    q = st.session_state.current_question
    if not q:
        return

    if q[0] == "translation":
        word, answer = q[1], q[2]
        if user_msg.lower().strip() == answer:
            st.session_state.chat_history.append(("bot", "✅ صحيح!"))
            st.session_state.xp += 10
        else:
            st.session_state.chat_history.append(("bot", f"❌ خطأ! الإجابة: {answer}"))
            st.session_state.hearts -= 1

    elif q[0] == "mcq":
        word, answer, options = q[1], q[2], q[3]
        if user_msg.lower().strip() == answer:
            st.session_state.chat_history.append(("bot", "✅ اختيار صحيح!"))
            st.session_state.xp += 15
        else:
            st.session_state.chat_history.append(("bot", f"❌ خطأ! الجواب: {answer}"))
            st.session_state.hearts -= 1

    elif q[0] == "sentence":
        correct_sentence, shuffled = q[1], q[2]
        if user_msg.strip() == correct_sentence:
            st.session_state.chat_history.append(("bot", "✅ جملة صحيحة!"))
            st.session_state.xp += 20
        else:
            st.session_state.chat_history.append(("bot", f"❌ خطأ! الجملة: {correct_sentence}"))
            st.session_state.hearts -= 1

    update_level()
    st.session_state.current_question = None

# --- شريط الحالة ---
hearts_display = "❤️" * st.session_state.hearts
st.markdown(
    f"<div class='status-bar'>📊 المستوى: {st.session_state.level} | ⭐ XP: {st.session_state.xp} | {hearts_display}</div>",
    unsafe_allow_html=True
)

# --- عنوان ---
st.title("🌍 بوت تعليم اللغات (نسخة دوولينجو)")

# --- عرض المحادثة ---
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>{msg}</div>", unsafe_allow_html=True)

# --- إدخال المستخدم ---
user_input = st.text_input("اكتب هنا:", key="chat_input", value="", placeholder="اكتب إجابتك...", label_visibility="collapsed")

if st.button("إرسال"):
    if user_input.strip():
        st.session_state.chat_history.append(("user", user_input))
        check_answer(user_input)

# --- أزرار اختيار التمرين ---
st.subheader("اختر تمرين:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📖 ترجمة"):
        translation_exercise("ar_en")
with col2:
    if st.button("📝 اختيار متعدد"):
        mcq_exercise("ar_en")
with col3:
    if st.button("🔤 تركيب جملة"):
        sentence_exercise()
