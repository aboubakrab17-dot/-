import streamlit as st
import random, time, base64, io

# ============== إعدادات عامة ==============
st.set_page_config(page_title="واتساب بوت المتعة", page_icon="💬", layout="wide")

# -------- محاولـة تفعيل الصوت (اختياري) --------
TTS_AVAILABLE = False
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

# ============== ثيم وخلفية ==============
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"  # "dark" أو "light"

THEME = st.session_state.theme_mode

BG_URL = "https://images.unsplash.com/photo-1535223289827-42f1e9919769?q=80&w=1600&auto=format&fit=crop"
# ستايل فقاعات واتساب + خلفية + أزرار
base_css = f"""
<style>
/* خلفية عامة */
.stApp {{
  background: url('{BG_URL}') center/cover fixed no-repeat;
}}
/* طبقة شفافة لتسهيل القراءة */
.main-block {{
  background: rgba(0,0,0,0.35);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,.25);
}}
/* شريط علوي */
.header {{
  display:flex; align-items:center; gap:12px;
  padding:10px 14px; border-radius:14px;
  background: rgba(255,255,255,.08);
  backdrop-filter: blur(6px);
  margin-bottom: 10px;
}}
.header .title {{
  font-weight:800; font-size: 1.2rem;
}}
/* تبديل الوضع */
.theme-chip {{
  display:inline-block; padding:6px 10px; border-radius:10px; cursor:pointer;
  background: rgba(255,255,255,.12);
  margin-left: 8px; user-select:none;
}}
/* حاوية الدردشة */
.chat-box {{
  height: 440px; overflow-y: auto; padding: 10px 6px 0 6px;
  background: rgba(255,255,255,.06);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,.12);
}}
/* فقاعة المستخدم */
.bubble-user {{
  max-width: 78%; padding:10px 12px; border-radius:14px 14px 4px 14px;
  margin: 6px 0; background: #25D366; color:#0b1f0e; 
  align-self:flex-end; margin-left:auto; box-shadow:0 4px 10px rgba(0,0,0,.15);
}}
/* فقاعة البوت */
.bubble-bot {{
  max-width: 78%; padding:10px 12px; border-radius:14px 14px 14px 4px;
  margin: 6px 0; background: #0B93F6; color:#eaf3ff;
  align-self:flex-start; margin-right:auto; box-shadow:0 4px 10px rgba(0,0,0,.15);
}}
/* صف لكل رسالة */
.chat-row {{ display:flex; flex-direction:column; }}
/* بطاقة النقاط */
.points-card {{
  background: rgba(255,255,255,.08); padding:8px 12px; border-radius:12px;
  border: 1px solid rgba(255,255,255,.12);
}}
/* مدخل الكتابة */
.input-row {{
  display:flex; gap:8px; margin-top:8px;
}}
.wh-btn {{
  border-radius: 12px; font-weight:700;
}}
/* درجات ألوان حسب الثيم */
:root {{
  --fg: {"#e9eef4" if THEME=="dark" else "#0f172a"};
  --sub: {"#cfd6dd" if THEME=="dark" else "#334155"};
}}
h1,h2,h3,h4,h5,p,span,div,li,small,strong,em {{
  color: var(--fg);
}}
.note {{ color: var(--sub); }}
/* بطاقات الألعاب */
.game-card {{
  background: rgba(255,255,255,.08); padding:12px; border-radius:14px;
  border: 1px solid rgba(255,255,255,.12); margin-bottom:8px;
}}
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# ============== حالة الجلسة ==============
if "chat" not in st.session_state:
    st.session_state.chat = []  # [{role: "user"/"bot", text:str}]
if "points" not in st.session_state:
    st.session_state.points = 0
if "name" not in st.session_state:
    st.session_state.name = ""
if "avatar" not in st.session_state:
    st.session_state.avatar = "🧑"

# ============== رأس الصفحة ==============
colA, colB = st.columns([0.72, 0.28])
with colA:
    st.markdown(
        f"""
        <div class="header">
            <div style="font-size:28px">💬</div>
            <div class="title">واتساب بوت المتعة</div>
            <div class="theme-chip">الوضع: {"🌙 غامق" if THEME=="dark" else "🔆 فاتح"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with colB:
    with st.container():
        st.markdown("<div class='points-card'>🏆 نقاطك: <b>{}</b></div>".format(st.session_state.points), unsafe_allow_html=True)

# زر تبديل الثيم
if st.button("🔁 تبديل الوضع (فاتح/غامق)", use_container_width=True):
    st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
    st.rerun()

st.markdown("<div class='main-block'>", unsafe_allow_html=True)

# ============== إعداد المستخدم ==============
with st.expander("👤 إعدادات المستخدم", expanded=(st.session_state.name == "")):
    st.info("مرحبًا! عرّفنا بنفسك باش نخلو الدردشة أجمل 😉")
    col1, col2 = st.columns([0.6,0.4])
    with col1:
        st.session_state.name = st.text_input("اسمك:", value=st.session_state.name, placeholder="اكتب اسم مستعار جميل")
    with col2:
        st.session_state.avatar = st.selectbox("اختر أفاتار:", ["🧑","🧕","👨‍💻","👩‍💻","🦸","🐼","🐯","🦊","🐵"])
    st.caption("📝 تقدر تبدلهم في أي وقت من نفس المكان.")

# ============== القائمة الجانبية ==============
st.sidebar.title("📌 القائمة")
menu = [
    "💬 الدردشة",
    "🎮 ألعاب سريعة",
    "😂 نكت",
    "💡 أقوال محفزة",
    "🎲 أسئلة ودردشة",
]
choice = st.sidebar.radio("اختر وضعًا:", menu)

# ============== وظائف مساعدة ==============
def add_bot_msg(text: str):
    st.session_state.chat.append({"role":"bot","text":text})

def add_user_msg(text: str):
    st.session_state.chat.append({"role":"user","text":text})

def tts_audio_tag(text: str):
    """ إرجاع وسم <audio> لو الصوت متاح. """
    if not TTS_AVAILABLE:
        return ""
    try:
        tts = gTTS(text=text, lang="ar")
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"<audio controls autoplay style='width:100%'><source src='data:audio/mp3;base64,{b64}' type='audio/mp3'></audio>"
    except Exception:
        return ""

def render_chat():
    chat_html = "<div class='chat-box'>"
    for m in st.session_state.chat[-200:]:
        if m["role"] == "user":
            chat_html += f"<div class='chat-row'><div class='bubble-user'>{st.session_state.avatar} <b>{st.session_state.name or 'أنا'}</b><br/>{m['text']}</div></div>"
        else:
            chat_html += f"<div class='chat-row'><div class='bubble-bot'>🤖 <b>البوت</b><br/>{m['text']}</div></div>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

def award_points(n=1, reason="نشاط"):
    st.session_state.points += n
    st.toast(f"🏆 +{n} نقطة ({reason})", icon="🎉")

# ردود ذكية قصيرة (بدون API)
SMART_REPLIES = [
    "فهمت قصدك 😉 خليني نزيدلك فكرة: جرّب تقسّم الهدف لخطوات صغيرة وتبدا بأبسط وحدة.",
    "كلام جميل! لو نطبّق هذا عمليًا راح يعطينا نتيجة قوية 💪",
    "اقتراح: سجّل النقاط المهمة وخطط بسرعة، التنفيذ يجي بعدها 🚀",
    "ممتاز! نقدر نحوله لتحدّي صغير وتبدأ تجرب 😎",
    "يعجبني أسلوبك… استمر وخلّي الفضول يقودك 🙌"
]

FUN_GIFS = [
    "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
    "https://media.giphy.com/media/3oz8xKaR836UJOYeOc/giphy.gif",
]

RIDDLES = [
    ("شيء كلما أخذت منه كبر؟", "الحفرة"),
    ("لديك شيء لك، يستخدمه الناس أكثر منك. ما هو؟", "اسمك"),
    ("ما هو الذي يمشي بلا قدمين؟", "الوقت"),
    ("بيت بلا أبواب ولا نوافذ؟", "البيض"),
    ("شيء إذا ذكرته كسرته؟", "الصمت"),
]

SCRAMBLE_WORDS = [
    ("برمجة", "مـربـجـة"),
    ("حاسوب", "حـاـسوـب"),
    ("إنترنت", "إـنـترنـت"),
    ("ذكاء", "ذكـا ء"),
    ("هاتف", "هـاتـف"),
]

# ============== واجهات الأوضاع ==============

if choice == "💬 الدردشة":
    st.subheader("💬 محادثة على طريقة واتساب")
    render_chat()

    # اقتراحات سريعة
    st.markdown("<div class='note'>✍️ اقتراحات سريعة:</div>", unsafe_allow_html=True)
    colq1, colq2, colq3, colq4 = st.columns(4)
    sug = [
        "اعطني خطة دراسة أسبوعية",
        "أعطني فكرة مشروع بسيط",
        "حكمة اليوم",
        "خليني نضحك 😄",
    ]
    if colq1.button(sug[0]):
        add_user_msg(sug[0]); add_bot_msg("أكيد! ✍️ خطة سريعة: \n- يوميًا: 45 دقيقة دراسة + 15 مراجعة.\n- يومي الراحة: تطبيق عملي لمشروع صغير.\n- نهاية الأسبوع: تلخيص وتقييم التقدم."); award_points(2,"تفاعل")
        st.rerun()
    if colq2.button(sug[1]):
        add_user_msg(sug[1]); add_bot_msg("جرّب موقع صغير بالـStreamlit: حاسبة مصاريف يومية + تصدير CSV. سهل ومفيد 👍"); award_points(2,"تفاعل"); st.rerun()
    if colq3.button(sug[2]):
        add_user_msg(sug[2]); add_bot_msg("💡 حكمة: من جدّ وجد، ومن سار على الدرب وصل. خلّي خطواتك ثابتة!"); award_points(1,"قراءة"); st.rerun()
    if colq4.button(sug[3]):
        add_user_msg(sug[3]); add_bot_msg("😂 مرّة واحد نسى يتغدى… فطّر بالمغرب!"); award_points(1,"مزاح"); st.rerun()

    # إدخال أسفل
    st.markdown("<br/>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        msg = st.text_input("اكتب رسالتك…", placeholder="سولني أي حاجة…")
    with c2:
        send = st.button("إرسال ✈️", use_container_width=True)

    if send:
        text = msg.strip()
        if text:
            add_user_msg(text)
            # رد ذكي + احتمال GIF
            reply = random.choice(SMART_REPLIES)
            add_bot_msg(reply)
            if "ضحك" in text or "ضحكني" in text or "نكتة" in text:
                add_bot_msg(f"<img src='{random.choice(FUN_GIFS)}' width='220'/>")
            award_points(1, "مراسلة")
            # صوت (اختياري)
            if TTS_AVAILABLE:
                st.markdown(tts_audio_tag(reply), unsafe_allow_html=True)
            st.rerun()
        else:
            st.warning("اكتب رسالة أولاً يا بطل 😉")

elif choice == "🎮 ألعاب سريعة":
    st.subheader("🎮 ألعاب خفيفة وممتعة")

    # حجر/ورقة/مقص
    with st.container():
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.markdown("**✊🖐️✌️ حجر - ورقة - مقص**")
        opt = ["✊ حجر", "🖐️ ورقة", "✌️ مقص"]
        pick = st.radio("اختر:", opt, horizontal=True)
        if st.button("العب الآن 🎲"):
            bot = random.choice(opt)
            st.write(f"🤖 البوت اختار: **{bot}**")
            if pick == bot:
                st.info("تعادل! 😅")
            elif (pick=="✊ حجر" and bot=="✌️ مقص") or (pick=="🖐️ ورقة" and bot=="✊ حجر") or (pick=="✌️ مقص" and bot=="🖐️ ورقة"):
                st.success("🎉 ربحت +2 نقاط"); award_points(2,"فوز")
            else:
                st.error("😂 خسرت! المرة الجاية تفوز")
        st.markdown("</div>", unsafe_allow_html=True)

    # ألغاز
    with st.container():
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.markdown("**🧩 لغز اليوم**")
        if "riddle_idx" not in st.session_state:
            st.session_state.riddle_idx = random.randint(0, len(RIDDLES)-1)
        q, a = RIDDLES[st.session_state.riddle_idx]
        st.write("السؤال:", q)
        ans = st.text_input("جوابك هنا:")
        if st.button("تحقق ✅"):
            if ans.strip() == "":
                st.warning("اكتب إجابة 😉")
            elif ans.strip().replace(" ", "") == a.replace(" ", ""):
                st.success("صحّيت! ✅ +3 نقاط"); award_points(3,"لغز")
                st.session_state.riddle_idx = random.randint(0, len(RIDDLES)-1)
                st.rerun()
            else:
                st.error("غلط! جرّب تلميح: فكّر ببساطة.")
        st.markdown("</div>", unsafe_allow_html=True)

    # خلط كلمات
    with st.container():
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.markdown("**🔤 خمن الكلمة**")
        if "scr_idx" not in st.session_state:
            st.session_state.scr_idx = random.randint(0, len(SCRAMBLE_WORDS)-1)
        w, scrambled = SCRAMBLE_WORDS[st.session_state.scr_idx]
        st.write("المرتّب المخلوط:", f"**{scrambled}**")
        guess = st.text_input("الكلمة الأصلية:")
        if st.button("تأكيد 📌"):
            if guess.strip() == "":
                st.warning("اكتب تخمينك.")
            elif guess.strip().replace(" ","") == w.replace(" ",""):
                st.success("برافو! ✅ +2 نقاط"); award_points(2,"كلمات")
                st.session_state.scr_idx = random.randint(0, len(SCRAMBLE_WORDS)-1)
                st.rerun()
            else:
                st.error("مش هي! حاول مرة أخرى.")
        st.markdown("</div>", unsafe_allow_html=True)

elif choice == "😂 نكت":
    st.subheader("😂 نكت عشوائية")
    jokes = [
        "مرة واحد نسى هاتفو في الفريزر… وكي لقاه، كان على (الوضع البارد) 😂",
        "قالك الكمبيوتر تعب… حب يدير Restart للعطلة! 🤣",
        "واحد سأل صاحبو: واش هدفك؟ قلو: نلقى Wi-Fi بلا كلمة سر 😅",
        "مرة بروغرامر فرح بزاف… كتب: print('أنا سعيد!') 😆",
    ]
    if st.button("هات نكتة 😂"):
        j = random.choice(jokes)
        st.info(j)
        if TTS_AVAILABLE:
            st.markdown(tts_audio_tag(j), unsafe_allow_html=True)
        award_points(1,"نكتة")

elif choice == "💡 أقوال محفزة":
    st.subheader("💡 طاقة إيجابية")
    quotes = [
        "لا تنتظر الفرصة… اصنعها! 🚀",
        "التقدم الصغير اليوم أفضل من المثالي غدًا. 💪",
        "اعمل بصمت، ونجاحك سيتكلم. 🌟",
        "كل يوم فرصة جديدة لتكون أفضل. ✨",
        "الفكرة بدون تنفيذ مجرد حلم. ابدأ الآن. 🔥",
    ]
    if st.button("أعطني قولًا 💡"):
        q = random.choice(quotes)
        st.success(q)
        if TTS_AVAILABLE:
            st.markdown(tts_audio_tag(q), unsafe_allow_html=True)
        award_points(1,"تحفيز")

elif choice == "🎲 أسئلة ودردشة":
    st.subheader("🎲 أسئلة تفتح النقاش")
    qs = [
        "لو عندك 3 عادات جديدة تبدأها اليوم، واش تختار؟",
        "شنو أحسن كتاب/دورة غيرتك للأفضل؟",
        "لو تبدأ مشروع صغير هذا الأسبوع، واش راح يكون؟",
        "شنو أفضل عادة صباحية جربتها؟",
        "لو ترجع لعام فات، نصيحة وحدة لنفسك؟",
    ]
    if st.button("سؤال عشوائي 🎲"):
        s = random.choice(qs)
        add_bot_msg(f"سؤال للنقاش: **{s}**")
        st.rerun()

# ============== تذييل ==============
st.markdown("---")
st.caption("🎯 تجربة ممتعة! اجمع النقاط من اللعب والدردشة. الوضع الغامق/الفاتح، خلفية ألعاب ثابتة، ونطق صوتي اختياري (لو توفر gTTS).")
st.markdown("</div>", unsafe_allow_html=True)
