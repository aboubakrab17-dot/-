import streamlit as st
import random
import time
from datetime import datetime

# إعداد الصفحة
st.set_page_config(
    page_title="البوت الشاب — دردشة ستايل واتساب",
    page_icon="💬",
    layout="centered",
)

# CSS لتجميل الستايل كيما واتساب/مسنجر
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #d9a7c7, #fffcdc);
    }
    .title {
        text-align: center;
        font-size: 30px;
        color: #1c5d99;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 20px;
        color: #444;
    }
    .user-msg {
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 12px;
        margin: 8px;
        max-width: 70%;
        text-align: left;
        float: right;
        clear: both;
        font-size: 16px;
    }
    .bot-msg {
        background-color: #f1f0f0;
        padding: 10px;
        border-radius: 12px;
        margin: 8px;
        max-width: 70%;
        text-align: left;
        float: left;
        clear: both;
        font-size: 16px;
    }
    .time {
        font-size: 11px;
        color: gray;
        margin-top: 3px;
    }
    .suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 20px;
    }
    .suggestion-btn {
        background-color: #1c5d99;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 14px;
    }
    .suggestion-btn:hover {
        background-color: #163d66;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# عناوين
st.markdown('<div class="title">💬 البوت الشاب — دردشة ستايل واتساب</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">👇 اكتب سؤالك أو اختر من 50 اقتراح مرتب</div>', unsafe_allow_html=True)

# تهيئة المحادثة
if "chat" not in st.session_state:
    st.session_state.chat = []

# لائحة الاقتراحات
suggestions = [
    "اعطيني خطة دراسة أسبوعية",
    "أعطيني فكرة مشروع بسيط",
    "احكيلي نكتة 😁",
    "حكمة اليوم",
    "كيف نزيد الإنتاجية؟",
    "طرق سهلة لتعلم لغة إنجليزية",
    "كيفاش نربح من الانترنت؟",
    "اعطيني وصفة أكل سريعة",
    "تمارين رياضية منزلية",
    "كيفاش نركز في القراءة؟",
    "خطوات فتح مشروع صغير",
    "اعطيني نصيحة للتحفيز",
    "أفضل كتب لتطوير الذات",
    "كيف نتعامل مع الضغط؟",
    "طرق تنظيم الوقت",
    "كيفاش نطور مهارات التواصل؟",
    "أهداف ممكن نديرها هذا الأسبوع",
    "اعطيني ملخص كتاب شاب",
    "جملة إنجليزية مترجمة",
    "كيفاش نولي نفيق بكري؟",
    "طرق الحفظ السريع",
    "كيفاش نزيد الثقة بالنفس؟",
    "ألعاب ذهنية للتسلية",
    "أفضل مواقع للتعلم",
    "اعطيني مشروع برمجي صغير",
    "كيف نتعلم البرمجة بسهولة؟",
    "طرق الربح من يوتيوب",
    "اعطيني وصفة كوكيز 🍪",
    "خطة لمراجعة الامتحانات",
    "كيفاش نتعلم التصوير؟",
    "أحسن طرق لتعلم الرسم",
    "كيف نتعامل مع التوتر؟",
    "طرق تحسين الخط",
    "كيفاش نزيد التركيز في الدراسة؟",
    "جملة تحفيزية",
    "أفضل كورسات مجانية",
    "كيفاش نولي كاتب شاب؟",
    "ألعاب نقدر نديرها مع صحابي",
    "طرق تعلم الفرنسية",
    "كيفاش نطور مشروع تخرجي؟",
    "أحسن أفلام تحفيزية",
    "معلومة عشوائية 🤔",
    "أسرع طرق تعلم typing",
    "كيفاش ندير سيرة ذاتية؟",
    "أحسن تطبيقات للموبايل",
    "كيف نتعلم الذكاء الاصطناعي؟",
    "اعطيني خطة يومية",
    "طرق التحكم في الغضب",
    "جملة مضحكة",
    "اعطيني قائمة أهداف للشهر"
]

# عرض المحادثة
for role, msg, timestamp in st.session_state.chat:
    if role == "user":
        st.markdown(f'<div class="user-msg">{msg}<div class="time">{timestamp}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg}<div class="time">{timestamp}</div></div>', unsafe_allow_html=True)

# إدخال الرسالة
user_input = st.text_input("...اكتب رسالتك هنا")

# زر إرسال
if st.button("📤 إرسال"):
    if user_input.strip() != "":
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat.append(("user", user_input, now))
        bot_reply = f"📩 استلمت: {user_input}\n✅ (رد تجريبي — يمكنك التوسع حسب الحاجة)"
        st.session_state.chat.append(("bot", bot_reply, now))
        st.experimental_rerun()

# عرض الاقتراحات
st.markdown('<div class="suggestions">', unsafe_allow_html=True)
for i, sug in enumerate(suggestions):
    if st.button(sug, key=f"sug_{i}"):
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat.append(("user", sug, now))
        bot_reply = f"📩 استلمت: {sug}\n✅ (رد تجريبي — يمكنك التوسع حسب الحاجة)"
        st.session_state.chat.append(("bot", bot_reply, now))
        st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)
