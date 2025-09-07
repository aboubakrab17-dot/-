import streamlit as st
import time, datetime, random

# =========================
# إعدادات الصفحة
# =========================
st.set_page_config(page_title="البوت الشاب", page_icon="🤖", layout="wide")

# =========================
# CSS: ستايل واتساب/مسنجر + خلفية جذابة
# =========================
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}

html, body {
  background: linear-gradient(135deg,#c9eaff 0%, #fdfbfb 40%, #ffe9f0 100%) !important;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.block-container { padding-top: 10px !important; }

.chat-wrap {
  max-width: 860px;
  margin: 0 auto;
  padding: 6px 6px 22px;
  direction: rtl;
}
.header-title {
  text-align: center; font-weight: 800; font-size: 28px; color: #0b5cff; margin-top: 4px;
}
.header-sub {
  text-align: center; font-size: 16.5px; color: #333; margin-bottom: 12px;
}

.msg {
  padding: 12px 16px;
  border-radius: 18px;
  margin: 8px 0;
  max-width: 82%;
  font-size: 18px;
  line-height: 1.65;
  word-wrap: break-word;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.msg.user {
  margin-left: auto;
  background: #dcf8c6; color: #111; text-align: right;
}
.msg.bot {
  margin-right: auto;
  background: #e1f0ff; color: #111; text-align: left;
}
.msg .time {
  font-size: 12px; color: #666; margin-top: 6px; opacity: .9;
  text-align: right;
}
.msg.bot .time { text-align: left; }

.stButton > button {
  background-color: #25D366; color: #fff;
  border: none !important; border-radius: 26px;
  padding: 11px 18px; font-size: 16px; font-weight: 700;
  box-shadow: 0 4px 10px rgba(37,211,102,0.25);
  transition: transform .08s ease-in-out, background .12s;
}
.stButton > button:hover { background-color: #128C7E; transform: translateY(-1px); }
.stButton { background: transparent !important; }

.suggestion button {
  background: #0084FF !important;
  box-shadow: 0 4px 10px rgba(0,132,255,0.18) !important;
}
.suggestion button:hover { background: #0a6ddc !important; }

.sugg-title {
  font-size: 18px; font-weight: 800; color: #222; margin: 8px 0 6px;
}

.clear button {
  background: #e9e9e9 !important; color: #333 !important; box-shadow: none !important;
}
.clear button:hover { background: #d8d8d8 !important; }

.typing {
  font-size: 14px; color: #666; margin: 6px 0 4px;
}

/* الوضع الداكن */
body.dark, html.dark {
  background: linear-gradient(135deg,#1c1c1c 0%, #2d2d2d 50%, #3b3b3b 100%) !important;
}
.dark .msg.user { background: #056162; color: #fff; }
.dark .msg.bot { background: #262d31; color: #fff; }
.dark .header-title, .dark .header-sub { color: #eee; }
</style>
""", unsafe_allow_html=True)

# =========================
# حالة الجلسة
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "typing" not in st.session_state:
    st.session_state.typing = False
if "dark" not in st.session_state:
    st.session_state.dark = False

# =========================
# دوال مساعدة
# =========================
def now_ts(): return time.time()
def fmt_time(ts): return datetime.datetime.fromtimestamp(ts).strftime("%H:%M")
def add_user(msg): st.session_state.messages.append({"role":"user","content":msg,"ts":now_ts()})
def add_bot(msg): st.session_state.messages.append({"role":"bot","content":msg,"ts":now_ts()})
def render_chat():
    for m in st.session_state.messages:
        css = "user" if m["role"]=="user" else "bot"
        st.markdown(f"<div class='msg {css}'>{m['content']}<div class='time'>{fmt_time(m['ts'])}</div></div>", unsafe_allow_html=True)

# =========================
# منطق الردود (مبسّط)
# =========================
def reply_logic(q: str) -> str:
    return "✅ استلمت: " + q + "\n(رد تجريبي — يمكنك التوسع حسب الحاجة)"

# =========================
# تصدير المحادثة
# =========================
def export_txt() -> str:
    lines = []
    for m in st.session_state.messages:
        who = "أنا" if m["role"]=="user" else "البوت"
        lines.append(f"[{fmt_time(m['ts'])}] {who}: {m['content']}")
    return "\n".join(lines)

# =========================
# واجهة العنوان
# =========================
mode = "dark" if st.session_state.dark else "light"
st.markdown(f"<body class='{mode}'><div class='chat-wrap'>", unsafe_allow_html=True)
st.markdown("<div class='header-title'>💬 البوت الشاب — دردشة ستايل واتساب</div>", unsafe_allow_html=True)
st.markdown("<div class='header-sub'>اكتب سؤالك أو اختر من 50 اقتراح مرتب 👇</div>", unsafe_allow_html=True)

# =========================
# عرض الرسائل
# =========================
render_chat()
if st.session_state.typing:
    st.markdown("<div class='typing'>البوت يكتب…</div>", unsafe_allow_html=True)

# =========================
# إدخال المستخدم
# =========================
with st.form("send_form", clear_on_submit=True):
    user_text = st.text_input("✍️ اكتب رسالتك هنا...", "", help="أرسل أي نص أو استعمل الاقتراحات")
    c1, c2, c3 = st.columns([1,1,1])
    send = c1.form_submit_button("إرسال ✈️")
    clear = c2.form_submit_button("مسح المحادثة 🗑️")
    download = c3.form_submit_button("⬇️ تحميل")

if clear: st.session_state.messages = []; st.rerun()
if download:
    st.download_button("تحميل الآن", data=export_txt().encode("utf-8"), file_name=f"chat_{int(time.time())}.txt", mime="text/plain")

if send and user_text.strip():
    add_user(user_text)
    st.session_state.typing = True
    st.rerun()

if st.session_state.typing:
    time.sleep(0.25)
    last_user = next((m for m in reversed(st.session_state.messages) if m["role"]=="user"), None)
    bot_text = reply_logic(last_user["content"] if last_user else "")
    add_bot(bot_text)
    st.session_state.typing = False
    st.rerun()

# =========================
# قائمة الاقتراحات (≈50)
# =========================
st.markdown("<div class='sugg-title'>✨ قائمة الاقتراحات:</div>", unsafe_allow_html=True)

suggestions = [
    "خطة دراسة قوية", "تعلم البرمجة من الصفر", "HTML/CSS/JS بسرعة", "نصائح تنظيم الوقت",
    "فكرة مشروع بسيط", "مصادر مجانية للتعلم", "حكمة ملهمة", "تمارين رياضية منزلية",
    "وصفة سريعة", "كيف أتعلم لغة إنجليزية", "طرق الحفظ السريع", "أفضل كتب تطوير الذات",
    "أهمية الرياضة", "أفكار محتوى يوتيوب", "كيف تبدأ التجارة الإلكترونية", "طرق الربح أونلاين",
    "أفكار مشاريع صغيرة", "إدارة الوقت في الدراسة", "مواقع مجانية مفيدة", "أفضل تطبيقات الهاتف",
    "خطوات تعلم الذكاء الاصطناعي", "مقدمة في بايثون", "تعلم الجافا", "تصميم واجهات مواقع",
    "طرق التركيز أثناء المذاكرة", "كيف تصبح مبرمج محترف", "تعلم التصميم الجرافيكي", "نصائح للنجاح",
    "أهداف قصيرة المدى", "تنظيم النوم", "التغذية الصحية", "تمارين العقل", "كيف أتغلب على الكسل",
    "زيادة الثقة بالنفس", "طرق تحسين الذاكرة", "أفضل كورسات مجانية", "أفكار تطبيقات مبتكرة",
    "التسويق الرقمي", "مهارات التواصل", "التحدث أمام الجمهور", "إدارة المشاريع",
    "تعلم قواعد البيانات", "استخدام Git و Github", "تعلم Flutter", "أساسيات الأمن السيبراني",
    "تعلم الذكاء الاصطناعي", "تعلم Machine Learning", "أفضل لغات البرمجة", "طرق تحسين الكتابة",
    "أهمية القراءة اليومية", "خطة تعلم Web Development"
]

cols = st.columns(5)
for i, s in enumerate(suggestions):
    with cols[i % 5]:
        if st.button(s, key=f"sugg_{i}", use_container_width=True):
            add_user(s); st.session_state.typing = True; st.rerun()

# =========================
# إضافات: الوضع + عداد + اقتراح عشوائي
# =========================
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("🌙 تبديل الوضع", use_container_width=True):
        st.session_state.dark = not st.session_state.dark
        st.rerun()
with c2:
    st.info(f"📊 عدد الرسائل: {len(st.session_state.messages)}")
with c3:
    if st.button("🎲 اقتراح عشوائي", use_container_width=True):
        pick = random.choice(suggestions)
        add_user(pick); st.session_state.typing = True; st.rerun()

st.markdown("</div></body>", unsafe_allow_html=True)
