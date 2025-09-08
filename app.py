# app.py
import streamlit as st
from datetime import datetime, date
import json

st.set_page_config(page_title="بوت تعليمي - منصة بسيطة", page_icon="📚", layout="wide")

# -------------------------
# CSS / تصميم (ستايلي)
# -------------------------
PAGE_CSS = """
<style>
/* خلفية عامة */
.stApp {
  background: linear-gradient(180deg, #0f172a 0%, #1f2937 100%);
  color: #e6eef8;
  font-family: "Cairo", "Helvetica", sans-serif;
  padding: 18px;
}

/* العنوان */
h1 { color: #fffb; text-align:center; font-size:34px; margin-bottom:8px; }

/* الكونتينرات */
.chat-container {
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  padding: 18px;
  min-height: 420px;
  box-shadow: 0 6px 24px rgba(2,6,23,0.6);
}

/* فقاعات البوت */
.msg-bot {
  background: linear-gradient(90deg,#a5f3fc,#60a5fa);
  color:#04202a;
  padding:12px 14px;
  display:inline-block;
  border-radius:16px;
  margin:8px 6px;
  max-width:72%;
  box-shadow: 0 4px 10px rgba(2,6,23,0.5);
}

/* فقاعات المستخدم */
.msg-user {
  background: linear-gradient(90deg,#d1fae5,#34d399);
  color:#042018;
  padding:12px 14px;
  display:inline-block;
  border-radius:16px;
  margin:8px 6px;
  max-width:72%;
  float:right;
  box-shadow: 0 4px 10px rgba(2,6,23,0.5);
}

/* وقت الرسالة */
.msg-time { display:block; font-size:11px; color:rgba(255,255,255,0.6); margin-top:6px; }

/* الاقتراحات */
.suggestion {
  background: rgba(255,255,255,0.06);
  color:#fff;
  padding:8px 10px;
  border-radius:14px;
  margin:6px;
  display:inline-block;
  cursor:pointer;
  border: 1px solid rgba(255,255,255,0.04);
}
.suggestion:hover { transform: translateY(-3px); box-shadow: 0 6px 18px rgba(0,0,0,0.6); }

/* الادخال */
input[type="text"], textarea { background: rgba(255,255,255,0.02) !important; color: #fff !important; }
.stButton>button { background: linear-gradient(90deg,#06b6d4,#3b82f6) !important; color: #fff !important; border-radius:10px !important; padding:8px 14px; }
.small-muted { color: rgba(255,255,255,0.6); font-size:12px; }

hr { border: none; height:1px; background: rgba(255,255,255,0.03); margin:12px 0; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

# -------------------------
# بيانات ثابتة: اقتراحات + دورات + دروس
# -------------------------
SUGGESTIONS = [
    "اعطني خطة دراسة يومية لمدة أسبوع",
    "علّمني 5 كلمات إنجليزية مهمة مع أمثلة",
    "اعطني سؤال اختبار قواعد بسيط",
    "ترجم: كيف حالك؟ إلى الإنجليزية",
    "اعطيني نصائح لتحسين النطق",
    "علّمني التحية بالإنجليزية",
    "اعطني جملة يومية لتكرارها",
    "اختبرني في الماضي البسيط",
    "كيف أكتب رسالة بريد رسمي قصيرة؟",
    "اقترح نشاط تفاعلي للفظ الكلمات",
    "أعطني تمرين استماع قصير",
    "صِف أحد المواضيع للكتابة 150 كلمة",
    "علمّني 3 أفعال شائعة مع أمثلة",
    "كيف أتحسن في المحادثة اليومية؟",
    "جرّب اختبار MCQ بسيط",
    "علّمني قاعدة زمن المضارع التام",
    "أعطني 10 كلمات سياحية مُهمة",
    "علّمني إدخال الترحيب في رسالة رسمية",
    "ارسل لي نص قصير لأقرؤه وألّخصه",
    "اعطني مثلًا ثقافيًا إنجليزيًا مع تفسير",
    "كيف أحسن مفرداتي يومياً؟",
    "اقترح لعبة لتعلم المفردات",
    "علّمني أسئلة مقابلة عمل قصيرة",
    "أرسل لي حوار بسيط بالإنجليزية",
    "اعطني 5 عبارات للحديث عن الهوايات",
    "علّمني عبارات طلب الاتجاهات",
    "اختبرني في مصطلحات العمل",
    "علّمني كيفية وصف صورة",
    "أعطني 3 تعابير عامية مفيدة",
    "اقترح لي اختبار كتابة 100 كلمة",
    "علمني كيف أعتذر بصيغة لبقة",
    "تدرب معي على الأسئلة العامة",
    "نقّح لي جملة قصيرة أكتبها",
    "اقترح خطة أسبوعية للتحدّث",
    "علّمني كلمات عند السفر للطائرة",
    "اعطني قواعد سريعة للكتابة",
    "اشرح لي الفرق بين since و for",
    "أعطني أمثلة على conditional نوع 1",
    "علّمني مصطلحات الطقس الأساسية",
    "اعطني تمريناً في تركيب الجمل",
    "علّمني وصف المشاعر بكلمات بسيطة",
    "اقترح 3 أفكار لمشروع تعليمي بسيط",
    "كيف أعد عرض تقديمي بسيط باللغة الإنجليزية؟",
    "اطرح علي 5 أسئلة شخصية للتدريب",
    "علّمني كيف أقرأ جدولاً صغيراً",
    "أرسل لي حكمة اليوم قصيرة",
    "اعطني نصائح لتذكر الكلمات الجديدة"
]

# دروس بسيطة (مثال)
COURSES = {
    "اللغة الإنجليزية": [
        {"type":"mcq", "q":"What is the plural of 'mouse'?", "options":["mouses","mice","mousees"], "answer":"mice"},
        {"type":"mcq", "q":"Choose correct verb: He ____ to school every day.", "options":["go","goes","going"], "answer":"goes"},
        {"type":"text", "q":"Translate to Arabic: 'Good morning' ", "answer":"صباح الخير"},
    ],
    "اللغة الفرنسية": [
        {"type":"mcq", "q":"Bonjour means:", "options":["Good night","Hello","Goodbye"], "answer":"Hello"},
        {"type":"text", "q":"Translate to French: 'Thank you'", "answer":"merci"},
    ]
}

# -------------------------
# تهيئة حالة الجلسة
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "points" not in st.session_state:
    st.session_state.points = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_active_date" not in st.session_state:
    st.session_state.last_active_date = None
if "current_course" not in st.session_state:
    st.session_state.current_course = None
if "lesson_index" not in st.session_state:
    st.session_state.lesson_index = 0
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "user" not in st.session_state:
    st.session_state.user = "زائر"

# رسالة ترحيب أولية
if not st.session_state.messages:
    st.session_state.messages.append({
        "sender":"bot",
        "text":"👋 أهلاً! أنا بوت المساعدة التعليمي. اختَر اقتراحاً أو اكتب سؤالك. عندك دورات، دروس وتحديات بسيطة هنا.",
        "time": datetime.now().strftime("%H:%M")
    })

# -------------------------
# وظائف مساعدة
# -------------------------
def add_message(sender, text):
    st.session_state.messages.append({
        "sender": sender,
        "text": text,
        "time": datetime.now().strftime("%H:%M")
    })

def award_points(n):
    st.session_state.points += n
    today = date.today().isoformat()
    if st.session_state.last_active_date != today:
        st.session_state.streak = st.session_state.streak + 1 if st.session_state.last_active_date else 1
        st.session_state.last_active_date = today

def simple_bot_reply(user_text):
    txt = user_text.strip().lower()
    # أوامر محددة
    if txt in ["ابدأ دورة", "ابدأ دورة انجليزية", "ابدأ الان", "start english"]:
        st.session_state.current_course = "اللغة الإنجليزية"
        st.session_state.lesson_index = 0
        return "✔️ تم فتح دورة اللغة الإنجليزية — اضغط 'ابدأ الدرس' للبدء."
    if txt.startswith("درس"):
        return "اضغط زر 'ابدأ الدرس' لفتح السؤال التالي."
    # إذا النص مطابق لأحد الاقتراحات
    for s in SUGGESTIONS:
        if txt == s.lower():
            return "حسناً — سأُجيب على هذا الاقتراح: " + s
    # إجابات عامة وتجريبية
    if any(k in txt for k in ["كيف", "وش", "شلون", "ماذا", "what", "how", "why"]):
        return "🔎 سؤال جيد — جرّب صياغة السؤال بوضوح أو اختر أحد الاقتراحات الجاهزة."
    # fallback
    return "🙂 فهمت. جرّب اقتراحاً من القائمة أو اكتب 'ابدأ دورة' لبدء درس."

def start_next_lesson():
    course = st.session_state.current_course
    if not course or course not in COURSES:
        add_message("bot", "لم تختَر دورة بعد — استخدم لوحة الدورات الجانبية أو اكتب 'ابدأ دورة'.")
        return
    idx = st.session_state.lesson_index
    lessons = COURSES[course]
    if idx >= len(lessons):
        add_message("bot", f"🎉 انتهت الدروس في {course}. لقد أكملت الدورة!")
        return
    q = lessons[idx]
    # عرض السؤال
    if q["type"] == "mcq":
        # سنخزن السؤال القائم في session_state لكي نتحقق لاحقاً
        st.session_state.current_question = q
        add_message("bot", f"سؤال {idx+1}: {q['q']} \n(اختر الإجابة الصحيحة من الخيارات في اليمين)")
    elif q["type"] == "text":
        st.session_state.current_question = q
        add_message("bot", f"السؤال {idx+1}: {q['q']} \n(اكتب إجابتك ثم اضغط تحقق)")
    else:
        st.session_state.current_question = q
        add_message("bot", f"السؤال {idx+1}: {q['q']}")

def check_answer(user_ans):
    q = st.session_state.get("current_question")
    if not q:
        add_message("bot", "ما في سؤال مفعل الآن — اضغط 'ابدأ الدرس' لبدء سؤال.")
        return
    if q["type"] == "mcq":
        correct = (user_ans == q["answer"])
        if correct:
            award_points(10)
            add_message("bot", "✅ إجابة صحيحة! رصيدك زاد +10 نقاط.")
            st.session_state.lesson_index += 1
        else:
            add_message("bot", f"❌ ليست صحيحة. الإجابة الصحيحة: {q['answer']}. حاول التالي.")
            st.session_state.lesson_index += 1
    elif q["type"] == "text":
        # مقارنة صغيرة بحساسية بسيطة (lower & strip)
        if user_ans.strip().lower() == q["answer"].strip().lower():
            award_points(12)
            add_message("bot", "✅ ممتاز! إجابة صحيحة — +12 نقاط.")
        else:
            add_message("bot", f"❌ يبدو أن الإجابة مختلفة. الإجابة المتوقعة: {q['answer']}")
        st.session_state.lesson_index += 1
    else:
        add_message("bot", "نوع سؤال غير معروف.")
    # بعد التحقق ننهي السؤال الحالي
    st.session_state.current_question = None

# -------------------------
# الشريط الجانبي
# -------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#fff'>📚 الدورات والتقدم</h2>", unsafe_allow_html=True)
    selected_course = st.selectbox("اختر دورة", ["(لا شيء)"] + list(COURSES.keys()), index=0)
    if selected_course != "(لا شيء)":
        st.session_state.current_course = selected_course
    st.write("")
    st.metric("نقاطك", st.session_state.points)
    st.metric("سلسلة يومية (streak)", st.session_state.streak)
    st.write("---")
    st.markdown("### أدوات")
    if st.button("⬇️ تنزيل التقدّم (JSON)"):
        data = {
            "user": st.session_state.user,
            "points": st.session_state.points,
            "streak": st.session_state.streak,
            "course": st.session_state.current_course,
            "lesson_index": st.session_state.lesson_index,
            "messages": st.session_state.messages
        }
        st.download_button("Download progress.json", data=json.dumps(data, ensure_ascii=False, indent=2), file_name="progress.json", mime="application/json")
    if st.button("مسح المحادثة/إعادة تعيين"):
        st.session_state.messages = []
        st.session_state.current_question = None
        st.session_state.lesson_index = 0
        st.session_state.points = 0
        st.session_state.streak = 0
        st.session_state.last_active_date = None
        add_message("bot", "🧹 تم إعادة التهيئة — مرحباً مجدداً!")
    st.write("---")
    st.markdown("### مساعدة سريعة")
    st.markdown("- اكتب سؤال أو اختر اقتراحًا\n- ابحث عن: `ابدأ دورة` لبدء دروس\n- استخدم أزرار الاقتراحات أسفل الصفحة")

# -------------------------
# الواجهة الرئيسية: العنوان + لوحة الدردشة + الاقتراحات
# -------------------------
st.markdown("<h1>💬 البوت الشاب — منصة تعليمية بسيطة</h1>", unsafe_allow_html=True)
cols = st.columns((3,1))

with cols[0]:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    # عرض الرسائل
    for m in st.session_state.messages:
        if m["sender"] == "bot":
            st.markdown(f'<div class="msg-bot">{m["text"]}<span class="msg-time"> {m["time"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-user">{m["text"]}<span class="msg-time"> {m["time"]}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")  # مسافة

    # صندوق الادخال (نستخدم فورم)
    with st.form("chat_form", clear_on_submit=False):
        user_input = st.text_input("...اكتب رسالتك (أو اضغط اقتراح)", value=st.session_state.input_text, key="input_box")
        submitted = st.form_submit_button("✈️ إرسال")
        if submitted and user_input.strip():
            st.session_state.input_text = ""
            # أضف رسالة المستخدم فوراً
            add_message("user", user_input.strip())
            # إذا هناك سؤال MCQ ظاهر، تحقق منه
            cur_q = st.session_state.get("current_question")
            if cur_q and cur_q["type"] == "mcq":
                # إذا المستخدم كتب النص ويطلب مقارنة مع الإجابة
                check_answer(user_input.strip())
            else:
                # رد بوت عام
                reply = simple_bot_reply(user_input)
                add_message("bot", reply)

with cols[1]:
    st.markdown("### ✨ اقتراحات سريعة")
    # عرض الاقتراحات كأزرار
    # نعرضها في شريطين عموديين
    for i, s in enumerate(SUGGESTIONS):
        if st.button(s, key=f"sugg_{i}", help="اضغط لإرسال/وضع في صندوق النص"):
            # عند الضغط نضيف كرسالة مستخدم ونرد برد مناسب
            add_message("user", s)
            # توليد رد سريع
            add_message("bot", simple_bot_reply(s))
    st.write("---")
    st.markdown("### 🎯 الدروس والاختبارات")
    if st.button("ابدأ الدرس التالي"):
        start_next_lesson()

    # لو كان هناك سؤال MCQ فعلاً، عرض عناصر اختيارية للتحقق
    q = st.session_state.get("current_question")
    if q and q.get("type") == "mcq":
        st.markdown(f"**السؤال:** {q['q']}")
        choice = st.radio("اختر:", q["options"], key="mcq_choice")
        if st.button("تحقق من الإجابة", key="check_mcq"):
            # تحقق
            check_answer(choice)
    elif q and q.get("type") == "text":
        st.markdown(f"**السؤال (اكتب نص):** {q['q']}")
        txt = st.text_input("إجابتك هنا:", key="text_answer")
        if st.button("تحقق من الإجابة (نص)", key="check_text"):
            check_answer(txt)

    st.write("---")
    st.markdown("### أدوات سريعة")
    if st.button("أضف 10 نقاط (تجربة)"):
        award_points(10)
        add_message("bot", "✅ تم إعطاؤك 10 نقاط (تجربة).")
    if st.button("احفظ محادثة كملف نصي"):
        logtxt = "\n".join([f"[{m['time']}] {m['sender'].upper()}: {m['text']}" for m in st.session_state.messages])
        st.download_button("تنزيل المحادثة", data=logtxt, file_name="chat.txt", mime="text/plain")

# -------------------------
# نهاية الكود — ملاحظات مهمة
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:rgba(255,255,255,0.7)'>ملاحظة: التقدّم محفوظ أثناء الجلسة. لإضافة محتوى ودروس أكثر، حدّث القاموس <code>COURSES</code> داخل الكود.</div>", unsafe_allow_html=True)
