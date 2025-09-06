import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="بوت تعليم البرمجة - نمط فيسبوك", layout="centered")

# ======================
# تنسيقات تشبه فيسبوك مسنجر
# ======================
CUSTOM_CSS = """
<style>
/* حصر العرض باش يبان تطبيق دردشة */
.main .block-container{
  max-width: 760px;
}

/* حاوية الدردشة */
.chat-wrap{
  background:#f5f6f7;
  padding:16px 12px 80px;
  border-radius:14px;
  border:1px solid #e0e0e0;
  min-height: 60vh;
  position: relative;
}

/* فقاعة الرسالة العامة */
.msg{
  max-width: 78%;
  padding:10px 12px;
  border-radius:20px;
  margin: 6px 0;
  line-height: 1.45;
  word-wrap: break-word;
  font-size: 15px;
  box-shadow: 0 1px 1px rgba(0,0,0,0.06);
}

/* رسالة المستخدم (يمين - أزرق) */
.msg.user{
  margin-left: auto;
  background: #0084ff;
  color: #fff;
  border-bottom-right-radius: 6px;
}

/* رسالة البوت (يسار - رمادي فاتح) */
.msg.bot{
  margin-right: auto;
  background: #e9ecef;
  color: #111;
  border-bottom-left-radius: 6px;
}

/* وقت الرسالة تحت الفقاعة */
.time{
  font-size: 11px;
  opacity: 0.75;
  margin-top: 4px;
}

/* سطر الوقت لليمين أو اليسار */
.time.right{ text-align: right; padding-right: 6px; }
.time.left{  text-align: left;  padding-left:  6px; }

/* مؤشر الكتابة (ثلاث نقاط) */
.typing{
  display:inline-block;
  background:#e9ecef;
  padding:10px 12px;
  border-radius:20px;
  border-bottom-left-radius: 6px;
  color:#333;
}
.dot{ height:6px; width:6px; background:#888; display:inline-block; margin:0 2px; border-radius:50%; animation: blink 1.3s infinite; }
.dot:nth-child(2){ animation-delay: .2s; }
.dot:nth-child(3){ animation-delay: .4s; }
@keyframes blink{ 0%{opacity:.2} 20%{opacity:1} 100%{opacity:.2} }

/* شريط الإدخال مثبت تحت */
.input-bar{
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffffcc;
  backdrop-filter: blur(6px);
  padding: 10px 8px;
  border-top: 1px solid #e0e0e0;
  border-bottom-left-radius: 14px;
  border-bottom-right-radius: 14px;
}

/* أزرار الاقتراحات */
.suggestions{
  display: grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 8px;
  margin-top: 10px;
}
.sbtn{
  width: 100%;
  border:1px solid #d8d8d8;
  background: #fff;
  border-radius: 18px;
  padding: 8px 10px;
  cursor:pointer;
}
.sbtn:hover{ background:#f2f2f2; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ======================
# قاعدة بيانات الردود (مفصلة وطويلة)
# ======================
RESPONSES = {
    "السلام": """وعليكم السلام ورحمة الله وبركاته! مرحباً بك في بوت تعليم البرمجة.
أنا هنا باش نعاونك تبدأ من الصفر: نفهمك ما هي البرمجة، أساسياتها، أشهر اللغات، وخطة تعلم عملية خطوة بخطوة.
جرب تكتب: "ما هي البرمجة" أو "كيف اتعلم البرمجة" أو استعمل الأزرار الجاهزة بالأسفل.""",

    "ما هي البرمجة": """البرمجة هي طريقة للتواصل مع الحاسوب عن طريق كتابة أوامر وتعليمات بلغة يفهمها.
هذه الأوامر تخليه ينفّذ مهام من البسيطة (جمع رقمين) للمعقدة (تشغيل مواقع ضخمة أو تطبيقات ذكاء اصطناعي).
فوائد البرمجة:
1) حلّ المشكلات بالتفكير المنطقي.
2) أتمتة الأعمال المتكررة.
3) بناء تطبيقات ومواقع وألعاب ومنتجات رقمية كاملة.
بالمختصر: البرمجة = تحويل الأفكار إلى واقع رقمي يعمل.""",

    "ما هي اساسيات البرمجة": """الأساسيات التي لازم أي مبتدئ يتعلمها:
• المتغيرات: تخزين البيانات بأسماء.
• أنواع البيانات: نصوص، أعداد صحيحة/عشرية، قيم منطقية.
• الشروط: if/else لاتخاذ قرارات.
• الحلقات: for/while للتكرار.
• الدوال: تجميع أوامر في وظيفة واحدة قابلة لإعادة الاستخدام.
هذه القواعد مشتركة تقريباً بين كل اللغات، وإذا فهمتها تبقى تبدل بين اللغات بسهولة.""",

    "ما هي لغة بايثون": """بايثون لغة مشهورة وسهلة القراءة، مناسبة للمبتدئين والمحترفين.
تُستعمل في: تطوير الويب (Flask/Django)، الذكاء الاصطناعي وتحليل البيانات (NumPy/Pandas)، الأتمتة والبرامج النصية.
قوتها في بساطة الصياغة وكثرة المكتبات الجاهزة، لذلك ننصح نبدأ بها.""",

    "كيف اتعلم البرمجة": """خطة عملية:
1) اختر لغة واحدة للبداية (ننصح ببايثون).
2) تعلم الأساسيات المذكورة (متغيرات/شروط/حلقات/دوال).
3) طبّق مباشرة بتمارين صغيرة بدل الحفظ.
4) أنجز مشروع بسيط (آلة حاسبة، مدير مهام، موقع صغير).
5) شارك في مجتمع/دروس، واسأل عند التعطّل.
الالتزام اليومي 30–60 دقيقة يغيّر مستواك في أشهر قليلة.""",

    "اريد نصيحة": """النصيحة الذهبية: لا تنتظر الكمال. اكتب كود واغلط وتعلم من الخطأ.
كرّر المحاولة وابني عادات صغيرة يومياً. الاستمرارية أهم من السرعة.""",

    "اعطني حكمة": """"تعلم البرمجة يعلّمك التفكير المنظم. كل مشكلة كبيرة تُحل إذا قسّمتها لخطوات صغيرة." """,

    "اعطني مصادر": """مصادر موصى بها للمبتدئين:
• FreeCodeCamp (مجاني وتمارين كثيرة)
• W3Schools (مراجعة سريعة للأُسس)
• MDN (مرجع قوي للويب)
• YouTube: قنوات تعليم عربية/أجنبية ممتازة (Elzero, Mosh, Corey Schafer)
اختر مصدر واحد في البداية حتى لا تتشتت.""",

    "ماذا اتعلم بعد بايثون": """بعد الأساسيات، اختر مساراً:
• الويب: Flask/Django + HTML/CSS/JS + قواعد بيانات (SQL).
• الذكاء الاصطناعي/البيانات: NumPy, Pandas, Matplotlib ثم تعلم الخوارزميات.
• الأتمتة: سكربتات لإدارة الملفات، الجداول، والمهام اليومية.
اختر مجال يعجبك وامشِ فيه بانتظام.""",

    "ما الفرق بين الجافا والبايثون": """بايثون: كود قصير وسهل، ممتازة للنماذج السريعة والبيانات والذكاء الاصطناعي.
جافا: صارمة ومستقرة للتطبيقات الكبيرة والمؤسساتية وأندرويد (مع كوتلن اليوم).
ابدأ ببايثون لتسهيل الدخول، ثم تعلّم جافا إن احتجت بنية أقوى لمشاريع ضخمة.""",

    "اعطني تمرين بسيط": """تمرين بايثون:
اكتب برنامج يطلب من المستخدم اسمه وسنه، ثم يرد برسالة مناسبة ويخبره إن كان قاصراً (<18) أو راشداً.
حاول تستعمل input()، تحويل النص إلى رقم، و if/else. هذا التمرين يجمع المتغيرات والشروط.""",

    "اعطني معلومة عشوائية": """أول مبرمجة في التاريخ هي آدا لوفلايس (القرن 19). دوّنت خوارزمية لآلة ميكانيكية وتُعتبر بذلك أول برنامج حاسوبي موثّق."""
}

UNKNOWN_REPLY = "هناك خطأ، أرسل رسالة أخرى."

# ======================
# حالة التطبيق
# ======================
if "messages" not in st.session_state:
    # كل رسالة: dict فيه المرسل والنص والوقت
    st.session_state.messages = [
        {"sender": "bot", "text": "مرحباً! أنا بوت لتعليم البرمجة. اسألني أو استعمل الخيارات الجاهزة بالأسفل.", "time": datetime.now().strftime("%H:%M")}
    ]

if "typing" not in st.session_state:
    st.session_state.typing = False

# ======================
# دوال مساعدة
# ======================
def add_message(sender: str, text: str):
    st.session_state.messages.append({
        "sender": sender,
        "text": text.strip(),
        "time": datetime.now().strftime("%H:%M")
    })

def render_chat():
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    # عرض الرسائل
    for m in st.session_state.messages:
        if m["sender"] == "user":
            st.markdown(
                f"""<div class="msg user">{m['text']}</div>
                    <div class="time right">{m['time']}</div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""<div class="msg bot">{m['text']}</div>
                    <div class="time left">{m['time']}</div>""",
                unsafe_allow_html=True
            )

    # مؤشر كتابة
    if st.session_state.typing:
        st.markdown(
            """<div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>""",
            unsafe_allow_html=True
        )
        st.markdown('<div class="time left">الآن</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def get_bot_reply(user_text: str) -> str:
    key = user_text.strip().lower()
    return RESPONSES.get(key, UNKNOWN_REPLY)

# ======================
# واجهة
# ======================
st.markdown("### دردشة بشكل فيسبوك")

render_chat()

# شريط إدخال + أزرار
with st.container():
    st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    c1, c2 = st.columns([6, 1.2])
    with c1:
        user_input = st.text_input("اكتب رسالتك… (مثال: ما هي البرمجة)", label_visibility="collapsed", key="chat_input")
    with c2:
        send = st.button("إرسال", use_container_width=True)

    # اقتراحات سريعة
    st.markdown('<div class="suggestions">', unsafe_allow_html=True)
    sugg_cols = st.columns(2)
    suggestions = [
        "السلام",
        "ما هي البرمجة",
        "ما هي اساسيات البرمجة",
        "ما هي لغة بايثون",
        "كيف اتعلم البرمجة",
        "اعطني مصادر",
        "ماذا اتعلم بعد بايثون",
        "ما الفرق بين الجافا والبايثون",
        "اعطني تمرين بسيط",
        "اعطني معلومة عشوائية"
    ]
    # زر لمسح المحادثة
    suggestions.append("مسح المحادثة")

    # نوزّع الأزرار
    for i, s in enumerate(suggestions):
        with sugg_cols[i % 2]:
            if st.button(s, key=f"sugg_{i}", use_container_width=True):
                if s == "مسح المحادثة":
                    st.session_state.messages = []
                    add_message("bot", "تم مسح المحادثة. ابدأ رسالة جديدة.")
                else:
                    add_message("user", s)
                    st.session_state.typing = True
                    # إعادة الرسم لإظهار مؤشر الكتابة
                    st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# منطق الإرسال
if send and user_input.strip():
    add_message("user", user_input)
    st.session_state.typing = True
    st.experimental_rerun()

# إذا مؤشر الكتابة شغّال، ننتظر لحظات ثم نرد
if st.session_state.typing:
    # محاكاة "البوت يكتب…"
    time.sleep(0.8)
    # آخر رسالة من المستخدم
    last_user = None
    for m in reversed(st.session_state.messages):
        if m["sender"] == "user":
            last_user = m["text"]
            break
    bot_text = get_bot_reply(last_user or "")
    add_message("bot", bot_text)
    st.session_state.typing = False
    st.experimental_rerun()
