import streamlit as st
import sqlite3
import json
import re
import random
from datetime import datetime
from textwrap import dedent

# ============ إعدادات أساسية ============
st.set_page_config(
    page_title="البوت الشاب — دردشة ستايل واتساب",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============ قاعدة البيانات المحليّة (SQLite) ============
@st.cache_resource
def get_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,            -- user / bot / system
            content TEXT,
            ts TEXT               -- ISO time
        )
    """)
    conn.commit()
    return conn

conn = get_db()

def db_add(role, content):
    conn.execute("INSERT INTO messages(role, content, ts) VALUES(?,?,?)",
                 (role, content, datetime.now().isoformat(timespec="seconds")))
    conn.commit()

def db_all():
    cur = conn.execute("SELECT role, content, ts FROM messages ORDER BY id ASC")
    return cur.fetchall()

def db_clear():
    conn.execute("DELETE FROM messages")
    conn.commit()

# ============ ثيم & CSS ============

THEMES = {
    "واتساب": {
        "bg": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "bubble_user": "#d4f8c2",
        "bubble_bot": "#eaf2ff",
        "text": "#0b1b22",
        "accent": "#25D366",
        "chip": "#ffffffcc",
        "chip_text": "#0b1b22",
    },
    "غامق أنيق": {
        "bg": "linear-gradient(135deg,#141e30,#243b55)",
        "bubble_user": "#273c3f",
        "bubble_bot": "#2b2f3a",
        "text": "#e8eef2",
        "accent": "#7bd389",
        "chip": "#3a4052",
        "chip_text": "#e8eef2",
    },
    "فاتح مرح": {
        "bg": "linear-gradient(135deg,#f9f9fb,#e6f0ff)",
        "bubble_user": "#eaffea",
        "bubble_bot": "#ffffff",
        "text": "#1c2b3a",
        "accent": "#5b8def",
        "chip": "#f0f4ff",
        "chip_text": "#1c2b3a",
    },
}

def inject_css(theme_name):
    th = THEMES[theme_name]
    css = f"""
    <style>
      html, body, [data-testid="stAppViewContainer"] {{
        background: {th['bg']} !important;
        color: {th['text']} !important;
      }}
      .title-hero {{
        text-align:center; margin-top:8px; margin-bottom:6px;
      }}
      .subtitle {{
        text-align:center; opacity:.92; margin:-2px 0 18px 0;
      }}
      .bubble {{
        max-width: 92%;
        padding: 12px 14px;
        border-radius: 16px;
        margin: 6px 0 2px 0;
        line-height: 1.55;
        word-wrap: break-word;
        box-shadow: 0 2px 10px rgba(0,0,0,.08);
        border: 1px solid rgba(255,255,255,.09);
      }}
      .user {{ background:{th['bubble_user']}; margin-left:auto; }}
      .bot  {{ background:{th['bubble_bot']}; margin-right:auto; }}
      .meta {{ font-size:12px; opacity:.7; margin:0 4px; }}
      .row {{ display:flex; align-items:flex-end; gap:8px; }}
      .avatar {{
        width:34px; height:34px; border-radius:50%;
        background:#fff3; box-shadow:0 2px 6px #0003;
        display:flex; align-items:center; justify-content:center;
        font-size:18px;
      }}
      .chip {{
        display:inline-block; padding:8px 10px; margin:6px 8px 0 0;
        border-radius:999px; cursor:pointer; user-select:none;
        background:{th['chip']}; color:{th['chip_text']};
        border:1px solid #ffffff30;
        transition: all .15s ease;
        font-size:13.5px;
      }}
      .chip:hover {{ transform: translateY(-1px); box-shadow:0 3px 10px #0002; }}
      .chips-wrap {{
        display:flex; flex-wrap:wrap; align-items:center;
        margin:2px 0 10px 0;
      }}
      .tools {{
        display:flex; gap:6px; flex-wrap:wrap; margin:8px 0 4px 0;
      }}
      .btn {{
        border:none; border-radius:10px; padding:8px 10px;
        background:{th['accent']}; color:#071b12; font-weight:600;
        box-shadow:0 2px 10px rgba(0,0,0,.15); cursor:pointer;
      }}
      .searchbox input {{
        border-radius:10px !important; border:1px solid #ffffff40 !important;
      }}
      .footer-note {{ text-align:center; opacity:.6; font-size:12px; margin-top:10px; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ============ اقتراحات جاهزة (50+) ============
SUGGESTIONS = [
    "اعطني خطة دراسة أسبوعية",
    "خطة للتحضير للبكالوريا/الثانوية",
    "خطّة صباحية للياقة والصحة",
    "افكار مشروع صغير برأس مال قليل",
    "كيف نزيد الإنتاجية ونركز أكثر؟",
    "جدول مذاكرة مع فترات راحة",
    "كيف نتعلم لغة إنجليزية بسرعة؟",
    "أفضل عادات قبل النوم",
    "نصائح لإدارة الوقت في الجامعة",
    "طريقة بسيطة لتعلّم البرمجة",
    "كيف نطلق متجر إلكتروني صغير؟",
    "اقتراحات محتوى لتيك توك/رييلز",
    "عناوين جذابة لفيديو يوتيوب",
    "كيف نواجه التسويف؟",
    "طريقة عمل CV ممتاز",
    "نموذج رسالة بريد احترافية",
    "ملخص كتاب (اختر كتابًا مشهورًا)",
    "روتين أسبوعي للتطور الذاتي",
    "نظام غذائي مبسط وصحي",
    "تمارين منزلية بدون أدوات",
    "أفضل مصادر لتعلم بايثون",
    "مشروع تخرج أفكار عملية",
    "أفكار لمحتوى انستغرام",
    "قائمة أهداف شهرية ذكية",
    "كيف نوفّر المال للطلاب؟",
    "خطوات فتح قناة يوتيوب ناجحة",
    "كيف نتغلب على القلق قبل الامتحان؟",
    "طرق فعالة للحفظ السريع",
    "أفكار تطبيق بسيط بالموبايل",
    "كيف نبدأ فريلانسينغ؟",
    "استراتيجية تعلّم من الصفر لأي مجال",
    "قائمة كتب في تطوير الذات",
    "اسمع نكتة خفيفة 😂",
    "احكِ لي حكمة اليوم 😉",
    "ألغاز سهلة مع الحل",
    "مقولات تحفيزية",
    "كيف أحسن خطّي في الكتابة؟",
    "مذكرات يومية: نموذج بسيط",
    "قائمة مهام أسبوعية",
    "افكار صور ومنشورات",
    "كيف أتعامل مع الضغط النفسي؟",
    "أفضل طريقة لتلخيص الدروس",
    "قواعد ذهبية للتفوق",
    "هل يمكنك اختبار معلوماتي؟",
    "اختبرني مفردات إنجليزية",
    "تعليمات السلامة الرقمية",
    "كيف أنظّم ملفاتي وجهازي؟",
    "ألعاب ذهنية سريعة",
    "خطة تعلم Excel للمبتدئين",
    "خطة تعلم تصميم (Canva)",
    "نصائح لبداية مشروع تعليمي",
    "قائمة مشاريع برمجية بسيطة",
    "كيفية بناء عادة جديدة",
]

# ============ ذكاء محلي (بدون API) ============
FAQ = {
    r"(سلام|مرحبا|اهلا)": "مرحبا بيك! شنو حاب دير اليوم؟ نقدر نعاونك بخطة، نصيحة، أو حتى نكتة 😄",
    r"(خطة|plan).*دراسة": "هذه خطة سريعة: يوميًا 45 دقيقة دراسة + 15 مراجعة، وخرّج تلخيص أسبوعي. حدد 3 مواد أساسية وابدأ بأصعب وحدة.",
    r"(مشروع|بيزنس|متجر)": "افكار سريعة: دروبشيبينغ بسيط، بيع خدمات رقمية (تصميم/كتابة)، دروس خصوصية أونلاين، أو إدارة حسابات سوشيال.",
    r"(انجليز|english|تعلم لغة)": "ابدأ بـ 20 كلمة/يوم، شاهد فيديوهات قصيرة بترجمة، وقلّد النطق. استعمل مبدأ الـ Spaced Repetition.",
    r"(تركيز|إنتاجية|تسويف)": "قسّم وقتك إلى جلسات 25 دقيقة (Pomodoro) + 5 راحة. اقفل الإشعارات وحدد هدفًا واحدًا واضحًا.",
    r"(رجيم|غذاء|صحي)": "نظام بسيط: 2 لتر ماء، سكر أقل، بروتين في كل وجبة، ومشي 20–30 دقيقة يوميًا.",
    r"(برمجة|بايثون|python)": "ابدأ بـ input/print/variables ثم if/for/functions. طبّق تمارين صغيرة يوميًا. مشروع بسيط أفضل من 100 درس!",
    r"(cv|سيرة ذاتية)": "خليها صفحة واحدة، عنوان واضح، مهارات قابلة للقياس، وروابط أعمالك. اكتب الإنجازات بالأرقام.",
    r"(نكت|ضحك)": random.choice([
        "مرة واحد غبي فتح باب الثلاجة… لقا النور، قالها: ما شاء الله حتى أنتي مقريّة! 😂",
        "قالوا للبخيل: عندكم زيت؟ قالهم: لا، قالوا: والضو؟ قالهم: منجيبوه من الشمس! 😅",
        "واحد راح للطبيب قاله: كل ما نشرب شاي نوجع عيني! قاله: جرّب تحيد الملعقة من الكاس! 🤭",
    ]),
    r"(حكمة|اقتباس)": random.choice([
        "من جدّ وجد، ومن زرع حصد.",
        "ابدأ حيث أنت، استعمل ما لديك، وافعل ما تستطيع.",
        "ما تركز عليه يكبر — فركّز على الحلول لا على المشاكل.",
    ]),
    r"(اختبرني|quiz|اختبار).*انجلي": "ترجم: ‘Consistent effort beats talent when talent doesn’t try.’",
    r"(تلخيص|ملخص)": "أرسل نص قصير وأنا نلخصهولك في نقاط بسيطة ومباشرة.",
}

def simple_reply(msg: str) -> str:
    text = msg.strip().lower()
    # تخصيص سريع
    if len(text) <= 2:
        return "اكتبلي سؤالك بأكثر تفاصيل شوية باش نجاوبك مليح 🙏"
    # ملخص يدوي
    if text.startswith("لخص:") or "لخص" in text:
        body = re.sub(r"^لخص[:：]\s*", "", msg, flags=re.I)
        if not body.strip():
            return "ابعث النص بعد كلمة (لخص:) مثال: لخص: [النص]"
        parts = [p.strip() for p in re.split(r"[\.!\n]", body) if p.strip()]
        bullets = "\n".join([f"• {p}" for p in parts][:7]) or "• النص قصير بزاف للتلخيص."
        return f"تلخيص سريع:\n{bullets}"
    # بحث داخل المحادثة
    if text.startswith("ابحث:"):
        q = msg.split(":",1)[-1].strip()
        if not q:
            return "اكتب: ابحث: [كلمة/جملة]"
        rows = db_all()
        hits = [f"- ({r[2]}) {r[0]}: {r[1][:80]}..." for r in rows if q in r[1]]
        return "نتائج داخل المحادثة:\n" + ("\n".join(hits[:10]) if hits else "لا توجد نتائج.")
    # ردود من القاموس
    for pattern, answer in FAQ.items():
        if re.search(pattern, text):
            return answer
    # رد افتراضي ذكي بسيط
    return (
        "فهمت سؤالك ✅\n"
        "نقدر نقترح عليك خطة أو خطوات عملية: اختصرلي المطلوب (الهدف/المدة/المستوى)، "
        "ونعطيك جدول أو نقاط تنفيذ مباشرة."
    )

# ============ عناصر الواجهة العلوية ============
if "theme" not in st.session_state:
    st.session_state.theme = "واتساب"

inject_css(st.session_state.theme)

colA, colB = st.columns([1,1])
with colA:
    st.markdown(
        f'<h1 class="title-hero">💬 البوت الشاب — دردشة ستايل واتساب</h1>',
        unsafe_allow_html=True
    )
with colB:
    st.selectbox("🎨 اختر الثيم", list(THEMES.keys()), key="theme", on_change=lambda: inject_css(st.session_state.theme))

st.markdown(
    '<p class="subtitle">اكتب سؤالك أو اختر من الاقتراحات الجاهزة (أكثر من 50 فكرة) 👇</p>',
    unsafe_allow_html=True
)

# ============ أدوات سريعة ============
tcol1, tcol2, tcol3, tcol4 = st.columns(4)
with tcol1:
    if st.button("🧹 مسح المحادثة", use_container_width=True):
        db_clear()
        st.experimental_rerun()
with tcol2:
    if st.button("💾 تصدير JSON", use_container_width=True):
        data = [{"role": r, "content": c, "ts": ts} for (r,c,ts) in db_all()]
        st.download_button("⬇️ حمّل المحادثة", data=json.dumps(data, ensure_ascii=False, indent=2),
                           file_name="chat_export.json", mime="application/json", use_container_width=True)
with tcol3:
    st.write("")  # spacer
    st.markdown('<div class="tools"></div>', unsafe_allow_html=True)
with tcol4:
    st.write("")  # spacer

# ============ شريط البحث داخل المحادثة ============
with st.expander("🔎 بحث داخل المحادثة"):
    q = st.text_input("اكتب كلمة للبحث:")
    if q:
        rows = db_all()
        hits = [f"- ({ts}) {role}: {content}" for (role, content, ts) in rows if q in content]
        st.write("\n".join(hits[:25]) if hits else "لا توجد نتائج.")

# ============ اقتراحات (50+) ============
st.markdown('<div class="chips-wrap">', unsafe_allow_html=True)
for s in SUGGESTIONS:
    st.markdown(f"""<span class="chip" onclick="window.parent.postMessage({{'type':'chip','text':{json.dumps(s)}}}, '*')">{s}</span>""",
                unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# JS لالتقاط ضغطات الشيبس (اقتراحات) + مايك + TTS
st.components.v1.html(dedent(f"""
<script>
  // استقبال ضغطات الاقتراحات
  window.addEventListener("message", (e) => {{
    const data = e.data || {{}};
    if (data.type === "chip" && data.text) {{
      const inp = window.parent.document.querySelector('textarea');
      if (inp) {{
        inp.value = data.text;
        inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
      }}
    }}
  }}, false);

  // واجهة صوتية (إملاء + نطق)
  window.ST_VOICE = {{
    speak: (txt) => {{
      try {{
        const u = new SpeechSynthesisUtterance(txt);
        u.lang = "ar";
        speechSynthesis.cancel();
        speechSynthesis.speak(u);
      }} catch(_) {{}}
    }},
    listen: () => {{
      try {{
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) return "UNSUPPORTED";
        const r = new SR(); r.lang = "ar-DZ"; r.interimResults = false;
        r.onresult = (ev) => {{
          const t = ev.results[0][0].transcript;
          window.parent.postMessage({{type:"voice_text", text:t}}, "*");
        }};
        r.start();
        return "STARTED";
      }} catch(_) {{ return "ERROR"; }}
    }}
  }};
</script>
"""), height=0)

# إظهار أزرار مايك/نطق
cc1, cc2, cc3 = st.columns([1,1,2])
with cc1:
    start_voice = st.button("🎙️ إملاء صوتي")
with cc2:
    last_bot_to_say = st.session_state.get("last_bot", "")
    say_voice = st.button("🔊 نطق آخر رد")

voice_event = st.experimental_get_query_params().get("voice", None)

# ============ إدخال الرسالة ============
msg = st.text_area("…اكتب رسالتك", height=72, label_visibility="collapsed", key="msg_box")
send = st.button("إرسال ✈️", use_container_width=True)

# تفعيل الإملاء الصوتي
if start_voice:
    st.components.v1.html("""
    <script>
      const s = (window.parent.ST_VOICE && window.parent.ST_VOICE.listen()) || "UNSUPPORTED";
      window.parent.postMessage({type:"voice_state", state:s}, "*");
    </script>
    """, height=0)

# استقبال نص المايك (hack بسيط)
st.components.v1.html("""
<script>
  window.addEventListener("message", (e) => {
    const d = e.data || {};
    if (d.type === "voice_text" && d.text){
      const inp = window.parent.document.querySelector('textarea');
      if (inp){
        inp.value = d.text;
        inp.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
  }, false);
</script>
""", height=0)

# نطق آخر رد
if say_voice and last_bot_to_say:
    st.components.v1.html(f"""
    <script>
      if (window.parent.ST_VOICE) {{
        window.parent.ST_VOICE.speak({json.dumps(last_bot_to_say)});
      }}
    </script>
    """, height=0)

# ============ منطق الإرسال ============
def push_user(text):
    db_add("user", text)

def push_bot(text):
    db_add("bot", text)
    st.session_state["last_bot"] = text

if send and msg.strip():
    push_user(msg.strip())
    reply = simple_reply(msg)
    push_bot(reply)
    st.experimental_rerun()

# ============ عرض المحادثة (ستايل واتساب) ============
rows = db_all()
if not rows:
    # رسالة ترحيب أولية
    welcome = "أهلا وسهلا! أنا البوت الشاب 👋 — اسقسي على أي حاجة: خطة، تلخيص، إنتاجية، دراسة، أو دقائق ضحك.\nجرّب من الاقتراحات فوق أو ابعث سؤالك مباشرة."
    db_add("bot", welcome)
    rows = db_all()

for role, content, ts in rows:
    who = "bot" if role != "user" else "user"
    avatar_emoji = "🤖" if who == "bot" else "🧑‍💻"
    time_str = datetime.fromisoformat(ts).strftime("%H:%M")
    col1, col2 = st.columns([1,9]) if who == "bot" else st.columns([9,1])

    if who == "bot":
        with col1: st.markdown(f'<div class="avatar">{avatar_emoji}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="bubble bot">{content}</div><div class="meta">البوت • {time_str}</div>',
                        unsafe_allow_html=True)
    else:
        with col1:
            st.markdown(f'<div style="text-align:right;"><div class="bubble user">{content}</div><div class="meta">أنا • {time_str}</div></div>',
                        unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="avatar">{avatar_emoji}</div>', unsafe_allow_html=True)

st.markdown('<p class="footer-note">لا تحتاج لأي مفاتيح API — كل شيء محلي 💚</p>', unsafe_allow_html=True)
