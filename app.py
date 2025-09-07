import streamlit as st
import time, datetime

# =========================
# إعدادات الصفحة
# =========================
st.set_page_config(page_title="البوت الشاب", page_icon="🤖", layout="wide")

# =========================
# CSS: ستايل واتساب/مسنجر + إزالة الخلفيات البيضاء
# =========================
st.markdown("""
<style>
/* إخفاء قوائم ستريملت */
#MainMenu, header, footer {visibility: hidden;}
/* خلفية ناعمة */
html, body {
  background: linear-gradient(135deg,#f4f8ff 0%, #eef6ff 40%, #ffffff 100%);
}
.block-container {
  padding-top: 10px !important;
}

/* غلاف الدردشة */
.chat-wrap {
  max-width: 860px;
  margin: 0 auto;
  padding: 6px 6px 22px;
  direction: rtl;
}

/* عنوان */
.header-title {
  text-align: center; font-weight: 800; font-size: 28px; color: #0b5cff; margin-top: 4px;
}
.header-sub {
  text-align: center; font-size: 16.5px; color: #333; margin-bottom: 12px;
}

/* رسائل */
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

/* أزرار عامة */
.stButton > button {
  background-color: #25D366; color: #fff;
  border: none !important; border-radius: 26px;
  padding: 11px 18px; font-size: 16px; font-weight: 700;
  box-shadow: 0 4px 10px rgba(37,211,102,0.25);
  transition: transform .08s ease-in-out, background .12s;
}
.stButton > button:hover { background-color: #128C7E; transform: translateY(-1px); }
.stButton > button:focus { outline: none !important; }

/* إزالة أي خلفية بيضاء حول الأزرار */
.stButton { background: transparent !important; }

/* أزرار الاقتراحات */
.suggestion button {
  background: #0084FF !important;
  box-shadow: 0 4px 10px rgba(0,132,255,0.18) !important;
}
.suggestion button:hover { background: #0a6ddc !important; }

/* صفوف منسقة */
.row { display: flex; gap: 8px; flex-wrap: wrap; }
.row .stButton > button { width: 100%; }

/* عنوان الاقتراحات */
.sugg-title {
  font-size: 18px; font-weight: 800; color: #222; margin: 8px 0 6px;
}

/* حقل الإدخال */
.input-help { font-size: 14px; color: #666; margin-top: -6px; margin-bottom: 8px; }

/* زر مسح رمادي */
.clear button {
  background: #e9e9e9 !important; color: #333 !important; box-shadow: none !important;
}
.clear button:hover { background: #d8d8d8 !important; }

/* مؤشر يكتب... */
.typing {
  font-size: 14px; color: #666; margin: 6px 0 4px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# حالة الجلسة
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []   # {"role","content","ts"}
if "typing" not in st.session_state:
    st.session_state.typing = False

# =========================
# دوال مساعدة
# =========================
def now_ts():
    return time.time()

def fmt_time(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%H:%M")

def add_user(msg):
    st.session_state.messages.append({"role":"user","content":msg,"ts":now_ts()})

def add_bot(msg):
    st.session_state.messages.append({"role":"bot","content":msg,"ts":now_ts()})

def render_chat():
    for m in st.session_state.messages:
        css = "user" if m["role"]=="user" else "bot"
        st.markdown(
            f"<div class='msg {css}'>{m['content']}<div class='time'>{fmt_time(m['ts'])}</div></div>",
            unsafe_allow_html=True
        )

def long(text):
    # يضمن ردود مفصلة وطويلة
    return text

# =========================
# منطق الردود (بدون API)
# =========================
def reply_logic(q: str) -> str:
    t = q.strip().lower().replace("أ","ا").replace("إ","ا").replace("آ","ا")
    # كلمات مفتاحية موسّعة ومحتوى مطوّل
    if any(k in t for k in ["خطة", "plan", "دراسة"]):
        return long(
        "🗓️ خطة تعلم قوية (45–60 دقيقة/يوم):\n"
        "1) إحماء سريع: راجع ملخص آخر درس (5–10 د).\n"
        "2) تركيز أساسي: مفهوم جديد + مثال مطبق (25–35 د).\n"
        "3) تثبيت: تمارين قصيرة أو سؤالين تحدّي (10–15 د).\n"
        "أسبوعيًا: لخص أهم ما تعلمته + أنشئ مشروعًا صغيرًا (حتى لو بسيط جدًا).\n"
        "🎯 نصائح الذهب: استمرارية > كمال، خطط جلساتك قبل أن تبدأ، ودوّن تقدمك.\n"
        )
    if any(k in t for k in ["تعلم البرمجة", "البرمجة", "programming"]):
        return long(
        "👨‍💻 كيف تبدأ البرمجة عمليًا:\n"
        "• اختر لغة سهلة: بايثون.\n"
        "• الأساسيات: متغيرات، شروط، حلقات، دوال، هياكل بيانات.\n"
        "• طبّق يوميًا بمشاريع صغيرة: آلة حاسبة، مذكر مهام، لعبة نصية.\n"
        "• افهم الأخطاء بدل نسخ الحلول فقط.\n"
        "• شارك أعمالك على GitHub واطلب ملاحظات.\n"
        "📌 موارد مجانية مقترحة: وثائق رسمية + تمارين Codewars + دورات قصيرة مجانية.\n"
        )
    if any(k in t for k in ["html", "css", "جافاسكربت", "javascript", "ويب"]):
        return long(
        "🌐 طريق الويب السريع:\n"
        "1) HTML: بنية الصفحة (العناوين، الفقرات، الروابط، الصور).\n"
        "2) CSS: تنسيق (ألوان، مسافات، خطوط، Grid/Flex).\n"
        "3) JS: تفاعل (أزرار، نوافذ، جلب بيانات).\n"
        "🎯 تمرين 3 أيام: أنشئ صفحة شخصية (تعريف + معرض صور + نموذج تواصل).\n"
        )
    if any(k in t for k in ["نصيحة", "تنظيم الوقت", "productivity", "نصائح"]):
        return long(
        "⏱️ إنتاجيتك في 4 نقاط:\n"
        "• قاعدة 25/5: تركيز 25 دقيقة + راحة 5 دقائق.\n"
        "• قاعدة 1-3: حدِّد هدفًا كبيرًا وهدفين صغار لليوم.\n"
        "• منع التشتيت: أطفئ الإشعارات خلال جلسة التركيز.\n"
        "• مراجعة مسائية: سطران عمّا أنجزته وما ستفعله غدًا.\n"
        )
    if any(k in t for k in ["مشروع", "startup", "business", "فكرة"]):
        return long(
        "🚀 فكرة مشروع قابلة للتنفيذ بسرعة:\n"
        "• أداة تلخيص مقالات ودروس مع حفظ PDF وتقاسم الرابط.\n"
        "• خطة: نسخة أولى S MVP بصفحة واحدة + نموذج إدخال النص.\n"
        "• نموذج ربح: مجاني محدود + اشتراك رمزي لمزايا متقدمة.\n"
        )
    if any(k in t for k in ["حكمة", "اقتباس", "quote"]):
        return long("💡 «الاستمرارية تصنع ما لا يصنعه الحماس العابر.»")
    if any(k in t for k in ["تمرين", "رياضة", "workout"]):
        return long(
        "💪 روتين منزلي 12 دقيقة:\n"
        "سكوات 15 – ضغط 12 – قفز 20 – بلانك 30ث، كرر 3 مرات. لا تنس الإحماء والماء.\n"
        )
    if any(k in t for k in ["وصفة", "طبخ", "recipe"]):
        return long(
        "🍲 وصفة سريعة: تونة + خس + طماطم + خيار + ذرة + ليمون + زيت زيتون + ملح وفلفل.\n"
        "جاهزة بـ7 دقائق. قدّمها مع خبز كامل للحصول على وجبة متوازنة.\n"
        )
    if any(k in t for k in ["مصادر", "free", "كورسات", "تعلم مجاني"]):
        return long(
        "📚 مصادر مجانية:\n"
        "• وثائق بايثون الرسمية + RealPython مقالات.\n"
        "• FreeCodeCamp لأساسيات الويب.\n"
        "• Codewars/LeetCode للتحديات.\n"
        )
    # افتراضي
    return long(
        "🙂 باش نجاوبك بشكل أدق، استعمل كلمات مفتاحية مثل:\n"
        "• خطة — تعلم البرمجة — HTML/CSS/JS — نصيحة — مشروع — حكمة — تمرين — وصفة — مصادر\n"
        "أو اضغط على أحد الاقتراحات الجاهزة بالأسفل 👇"
    )

def export_txt() -> str:
    lines = []
    for m in st.session_state.messages:
        who = "أنا" if m["role"]=="user" else "البوت"
        lines.append(f"[{fmt_time(m['ts'])}] {who}: {m['content']}")
    return "\n".join(lines)

# =========================
# واجهة العنوان
# =========================
st.markdown("<div class='chat-wrap'>", unsafe_allow_html=True)
st.markdown("<div class='header-title'>💬 البوت الشاب — دردشة ستايل واتساب</div>", unsafe_allow_html=True)
st.markdown("<div class='header-sub'>اكتب سؤالك أو اختر اقتراحًا — ردود واضحة، طويلة ومفيدة، بلا أي مفاتيح أو تعقيد.</div>", unsafe_allow_html=True)

# =========================
# عرض الرسائل
# =========================
render_chat()

# مؤشر يكتب...
if st.session_state.typing:
    st.markdown("<div class='typing'>البوت يكتب…</div>", unsafe_allow_html=True)

# =========================
# إدخال المستخدم (form لتفادي لخبطة إعادة الرسم)
# =========================
with st.form("send_form", clear_on_submit=True):
    user_text = st.text_input("✍️ اكتب رسالتك هنا...", "", help="مثال: خطة — تعلم البرمجة — HTML/CSS/JS — مصادر")
    c1, c2, c3 = st.columns([1,1,1])
    send = c1.form_submit_button("إرسال ✈️")
    clear = c2.form_submit_button("مسح المحادثة 🗑️")
    download = c3.form_submit_button("⬇️ تحميل المحادثة")

if clear:
    st.session_state.messages = []
    st.rerun()

if download:
    st.download_button(
        "تحميل الملف الآن ⬇️",
        data=export_txt().encode("utf-8"),
        file_name=f"chat_{int(time.time())}.txt",
        mime="text/plain",
        use_container_width=True
    )

if send and user_text.strip():
    add_user(user_text)
    st.session_state.typing = True
    st.rerun()

# لو آخر رسالة من المستخدم وتبعت، نولد رد ونوقف المؤشر
if st.session_state.typing:
    # محاكاة كتابة قصيرة (بدون تأخير كبير)
    time.sleep(0.25)
    last_user = next((m for m in reversed(st.session_state.messages) if m["role"]=="user"), None)
    bot_text = reply_logic(last_user["content"] if last_user else "")
    add_bot(bot_text)
    st.session_state.typing = False
    st.rerun()

# =========================
# اقتراحات جاهزة — صفّين منظّمين
# =========================
st.markdown("<div class='sugg-title'>✨ اقتراحات جاهزة:</div>", unsafe_allow_html=True)

def add_pair(text):
    add_user(text); st.session_state.typing = True; st.rerun()

row1 = st.columns(3)
sugs1 = ["اعطيني خطة دراسة قوية", "تعلم البرمجة من الصفر", "HTML/CSS/JS بسرعة"]
for i, s in enumerate(sugs1):
    with row1[i]:
        if st.button(s, key=f"s1_{i}", use_container_width=True):
            add_pair(s)

row2 = st.columns(3)
sugs2 = ["نصائح لتنظيم الوقت", "فكرة مشروع بسيط", "مصادر مجانية للتعلم"]
for i, s in enumerate(sugs2):
    with row2[i]:
        if st.button(s, key=f"s2_{i}", use_container_width=True):
            add_pair(s)

# زر مسح في الأسفل أيضاً
st.markdown("<br>", unsafe_allow_html=True)
center = st.columns([2,1,2])[1]
with center:
    st.markdown("<div class='clear'>", unsafe_allow_html=True)
    if st.button("مسح المحادثة 🗑️", key="clear_bottom", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # chat-wrap
