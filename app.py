import streamlit as st
import random

# ------------------------ إعداد الصفحة ------------------------
st.set_page_config(page_title="لعبة الأسئلة والأجوبة", page_icon="🎮", layout="centered")

# خلفية نيون ستايل ألعاب
NEON_BG = """
<style>
.stApp {
    background-image: url('https://wallpapercave.com/wp/wp9116622.jpg');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}
.block-container{
    backdrop-filter: blur(6px);
    background: rgba(0,0,0,0.35);
    padding: 2rem 2rem;
    border-radius: 16px;
}
h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown {
    color: #ffffff !important;
}
.stRadio > div { gap: .75rem; }
.button-like {
    border-radius: 12px;
    padding: 0.75rem 1rem;
    border: 1px solid rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.08);
}
</style>
"""
st.markdown(NEON_BG, unsafe_allow_html=True)

# ------------------------ بنك الأسئلة (عدل كما تحب) ------------------------
QUESTIONS = [
    {
        "question": "ما هي عاصمة الجزائر؟",
        "options": ["الجزائر", "وهران", "قسنطينة", "عنابة"],
        "answer": "الجزائر",
        "explanation": "الجزائر العاصمة هي المركز السياسي والاقتصادي للبلاد."
    },
    {
        "question": "ما هو الكوكب المعروف بالكوكب الأحمر؟",
        "options": ["عطارد", "الزهرة", "المريخ", "زحل"],
        "answer": "المريخ",
        "explanation": "يُسمّى بالمريخ بسبب لون تربته المائل إلى الأحمر."
    },
    {
        "question": "من اخترع المصباح الكهربائي عملياً؟",
        "options": ["نيكولا تسلا", "ألكسندر غراهام بيل", "توماس إديسون", "ألبرت أينشتاين"],
        "answer": "توماس إديسون",
        "explanation": "ساهم إديسون في تطوير المصباح وجعله عملياً للاستخدام."
    },
    {
        "question": "كم عدد قارات العالم؟",
        "options": ["5", "6", "7", "8"],
        "answer": "7",
        "explanation": "آسيا، إفريقيا، أوروبا، أمريكا الشمالية، أمريكا الجنوبية، أوقيانوسيا، القارة القطبية الجنوبية."
    },
    {
        "question": "ما هي عاصمة فرنسا؟",
        "options": ["مدريد", "روما", "برلين", "باريس"],
        "answer": "باريس",
        "explanation": "باريس تُعرف بمدينة النور وهي العاصمة الفرنسية."
    },
    {
        "question": "ما هي اللغة الخاصة بتنسيق صفحات الويب؟",
        "options": ["HTML", "CSS", "Python", "SQL"],
        "answer": "CSS",
        "explanation": "CSS مسؤولة عن تنسيق الشكل والتصميم في صفحات الويب."
    },
    {
        "question": "كم نتيجة 8 × 7 ؟",
        "options": ["54", "56", "58", "64"],
        "answer": "56",
        "explanation": "8 ضرب 7 يساوي 56."
    },
    {
        "question": "أكبر كوكب في المجموعة الشمسية هو:",
        "options": ["زحل", "نبتون", "المشتري", "أورانوس"],
        "answer": "المشتري",
        "explanation": "المشتري هو الأكبر حجماً وكتلةً بين كواكب المجموعة."
    },
    {
        "question": "ما هي وحدة قياس القدرة الكهربائية؟",
        "options": ["فولت", "أوم", "واط", "أمبير"],
        "answer": "واط",
        "explanation": "الواط تقيس القدرة (معدل استهلاك أو إنتاج الطاقة)."
    },
    {
        "question": "أي من التالي لغة برمجة؟",
        "options": ["HTTP", "CSS", "Python", "DNS"],
        "answer": "Python",
        "explanation": "HTTP وDNS بروتوكولات، CSS للتنسيق، وPython لغة برمجة."
    }
]

# ------------------------ حالة الجلسة ------------------------
if "player" not in st.session_state:
    st.session_state.player = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "remaining" not in st.session_state:
    # ننسخ ونخلط الأسئلة مرة واحدة
    st.session_state.remaining = random.sample(QUESTIONS, k=len(QUESTIONS))
if "current" not in st.session_state:
    st.session_state.current = None
if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False
if "selected" not in st.session_state:
    st.session_state.selected = None

# ------------------------ دوال مساعدة ------------------------
def new_question():
    """يجلب سؤالاً جديداً (بدون تكرار) من القائمة المتبقية."""
    if st.session_state.remaining:
        st.session_state.current = st.session_state.remaining.pop(0)
        st.session_state.awaiting_answer = True
        st.session_state.selected = None
    else:
        st.session_state.current = None
        st.session_state.awaiting_answer = False

def reset_game():
    st.session_state.score = 0
    st.session_state.remaining = random.sample(QUESTIONS, k=len(QUESTIONS))
    st.session_state.current = None
    st.session_state.awaiting_answer = False
    st.session_state.selected = None

def play_sound(url: str):
    """يشغل صوت (قد يتطلب تفاعل المستخدم للسماح بالتشغيل التلقائي في بعض المتصفحات)."""
    st.markdown(
        f"""
        <audio autoplay style="display:none;">
            <source src="{url}">
        </audio>
        """,
        unsafe_allow_html=True
    )

# ------------------------ إدخال اسم اللاعب ------------------------
st.title("🎮 لعبة الأسئلة والأجوبة")
if not st.session_state.player:
    name = st.text_input("✨ أدخل اسمك للبدء", value="")
    start = st.button("🚀 ابدأ اللعبة")
    if start:
        if name.strip():
            st.session_state.player = name.strip()
            reset_game()
            new_question()
            st.rerun()
        else:
            st.warning("⚠️ من فضلك أدخل اسم صالح")
    st.stop()

# ------------------------ شريط التقدم والنقاط ------------------------
total = len(QUESTIONS)
answered = total - len(st.session_state.remaining) - (1 if st.session_state.current else 0)
progress = (answered) / total if total else 0
st.progress(progress, text=f"التقدّم: {answered}/{total}")
st.write(f"👋 مرحبًا **{st.session_state.player}** — نقاطك الحالية: **{st.session_state.score}**")

# ------------------------ عرض السؤال الحالي ------------------------
if st.session_state.current is None:
    # إذا لا يوجد سؤال حالي، نجيب واحد جديد أو ننهي اللعبة
    new_question()

if st.session_state.current:
    q = st.session_state.current
    st.markdown(f"## ❓ {q['question']}")

    # نضيف خياراً تمهيدياً لتفادي اختيار تلقائي (متوافق مع كل إصدارات ستريملت)
    display_options = ["— اختر إجابة —"] + q["options"]
    choice = st.radio("الاختيارات:", options=display_options, index=0, key=f"q_{answered}")

    col1, col2 = st.columns([1,1])
    with col1:
        confirm = st.button("✅ تأكيد الإجابة", use_container_width=True)
    with col2:
        skip = st.button("⏭️ تخطي هذا السؤال", use_container_width=True)

    if confirm:
        if choice == "— اختر إجابة —":
            st.warning("⚠️ اختر إجابة أولاً.")
        else:
            st.session_state.selected = choice
            st.session_state.awaiting_answer = False
            # تصحيح
            if choice == q["answer"]:
                st.success("🎉 إجابة صحيحة! أحسنت 👏")
                st.session_state.score += 1
                play_sound("https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg")
                st.balloons()
            else:
                st.error(f"❌ إجابة خاطئة! الصحيحة هي: **{q['answer']}**")
                play_sound("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg")
            # شرح إن وُجد
            if q.get("explanation"):
                st.info(f"ℹ️ شرح: {q['explanation']}")
            # زر التالي
            if st.button("➡️ السؤال التالي", use_container_width=True):
                new_question()
                st.rerun()

    if skip and st.session_state.awaiting_answer:
        # تخطي السؤال بدون تصحيح
        new_question()
        st.rerun()

else:
    # ------------------------ نهاية اللعبة ------------------------
    st.success(f"🎉 مبروك {st.session_state.player}! أنهيت كل الأسئلة.")
    st.write(f"🔢 مجموع نقاطك: **{st.session_state.score}** / **{total}**")
    if st.button("🔄 إعادة اللعب", use_container_width=True):
        reset_game()
        new_question()
        st.rerun()
