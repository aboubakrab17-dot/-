# app.py
# لعبة أسئلة عربية تشتغل على Streamlit
# - يقرأ ملف questions.json إن وُجد
# - إذا ماكانش الملف، يستخدم بيانات احتياطية مُدمَجة
# - يمنع تكرار الأسئلة، يدير عداد لكل سؤال، ويدعم تلميح وشرح
# - تصميم واجهة عربية وخلفية متدرجة CSS
# - لا يعتمد على صور/أصوات خارجية لتشغيله الأساسي

import streamlit as st
import json, random, time, os
from pathlib import Path
from copy import deepcopy

# ---------------------- تهيئة الصفحة والستايـل ----------------------
st.set_page_config(page_title="لعبة الألغاز - عربي", layout="centered", initial_sidebar_state="collapsed")

# CSS لتحسين الواجهة وجعلها "شابة"
st.markdown(
    """
    <style>
    :root{
      --bg1: #0f1724;
      --bg2: #0b2231;
      --accent: #00d4ff;
      --card: rgba(255,255,255,0.04);
      --text: #e6eef6;
    }
    html, body, [data-testid="stAppViewContainer"] {
      background: linear-gradient(135deg, var(--bg1) 0%, #0b1220 50%, #091226 100%);
      color: var(--text);
      font-family: "Segoe UI", Tahoma, Arial, "Noto Naskh Arabic", sans-serif;
    }
    .big-title {
      font-size: 44px;
      font-weight: 700;
      margin-bottom: 0.1rem;
    }
    .subtitle {
      color: #c8d6df;
      margin-top: 0;
      margin-bottom: 1rem;
    }
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 6px 18px rgba(2,6,23,0.6);
      margin-bottom: 12px;
    }
    .btn {
      background: linear-gradient(90deg,#ffb86b,#ff6d6d);
      color: white;
      padding: 8px 14px;
      border-radius: 10px;
      border: none;
      font-weight: 600;
    }
    .small-muted { color: #b8c4cb; font-size: 13px; }
    .center { text-align: center; }
    .question-box { padding: 20px; border-radius: 12px; background: rgba(0,0,0,0.25); margin-bottom: 12px; }
    .option-btn { width:100%; text-align: right; padding: 14px; border-radius: 10px; background: rgba(255,255,255,0.02); color: var(--text); margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------- إعدادات المسارات والـ assets ----------------------
BASE_DIR = Path(__file__).parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
# لو عندك ملفات صوت أو صورة ضيف المسارات هنا داخل المجلد assets
ASSETS_DIR = BASE_DIR / "assets"
BACKGROUND_IMG = ""  # لو عندك صورة خلفية، ضع المسار "assets/background.jpg" أو URL
SOUND_CORRECT = ""    # مثال: "assets/correct.mp3" أو URL
SOUND_WRONG = ""      # مثال: "assets/wrong.mp3" أو URL
# إذا ماكانوش موجودين، الكود يتخطاهم بدون أخطاء.

# ---------------------- بيانات اسئلة احتياطية (fallback) بالعربية ----------------------
# كل عنصر: {"id": int, "question": "...", "choices":[...], "answer": index_of_correct_choice, "explain": "...", "hint": "..."}
FALLBACK_DATA = [
    {"id":1, "question":"ما هي أصغر كوكب في المجموعة الشمسية؟",
     "choices":["المشتري","الزهرة","عطارد","المريخ"],
     "answer":2, "explain":"عطارد هو أصغر كواكب المجموعة الشمسية من حيث القُطر.", "hint":"هو أقرب كوكب إلى الشمس."},
    {"id":2, "question":"ما هو رمز العنصر الكيميائي الحديد؟",
     "choices":["Au","Fe","Ag","Cu"],
     "answer":1, "explain":"الحديد يرمز له بالرمز Fe.", "hint":"يبدأ بحرف F."},
    {"id":3, "question":"ما هي عاصمة اليابان؟",
     "choices":["بكين","سيول","طوكيو","بانكوك"],
     "answer":2, "explain":"طوكيو هي عاصمة اليابان.", "hint":"تبدأ بحرف ط."},
    {"id":4, "question":"ما لغة البرمجة الشهيرة المستخدمة لتعلم المبتدئين وسيرفرات الويب؟",
     "choices":["بايثون","جافا","سي","روبي"],
     "answer":0, "explain":"بايثون بسيطة ومناسبة للمبتدئين ولها مكتبات لويب.", "hint":"اسمها يُنطق 'باي-ثون'."},
    {"id":5, "question":"ما اسم الطبقة العليا من الغلاف الجوي للأرض؟",
     "choices":["الستراتوسفير","التروبوسفير","الميزوسفير","الميزوسفير الخارجي (الثيرموسفير)"],
     "answer":3, "explain":"الثيرموسفير (Thermosphere) هي من الطبقات العليا.", "hint":"توجد أعلاه الفضاء الخارجي."},
    {"id":6, "question":"ما هو أسرع حيوان بري؟",
     "choices":["الأسد","الفهد","الضبع","الكنغر"],
     "answer":1, "explain":"الفهد (Cheetah) هو أسرع حيوان بري قادراً على الوصول لسرعات كبيرة قصيرة.", "hint":"يُعرف بسرعته الكبيرة جداً على مسافات قصيرة."},
    {"id":7, "question":"ما هي أكبر قارة من حيث المساحة؟",
     "choices":["أفريقيا","أوروبا","آسيا","أمريكا الشمالية"],
     "answer":2, "explain":"آسيا هي أكبر القارات مساحة وسكانًا.", "hint":"تضم الصين والهند واليابان."},
    {"id":8, "question":"أي عنصر يُستخدم في صنع الرقاقات الإلكترونية (Chips) بكثرة؟",
     "choices":["الذهب","السيليكون","الحديد","الألومنيوم"],
     "answer":1, "explain":"السيليكون مادة أساسية في تصنيع أشباه الموصلات.", "hint":"اسمه يشبه 'سيليكون'."},
    {"id":9, "question":"ما هو المصطلح المعبر عن سرعة انتقال الضوء تقريبا؟",
     "choices":["300 ألف كلم/س","300 ألف كم/ث","30 ألف كم/ث","3 آلاف كم/ث"],
     "answer":1, "explain":"سرعة الضوء ≈ 300,000 كم/ثانية.", "hint":"سرعة الضوء تُقاس بالكم/ثانية."},
    {"id":10, "question":"ما هو العضو الذي يضخ الدم في جسم الإنسان؟",
     "choices":["الرئتين","المخ","القلب","الطحال"],
     "answer":2, "explain":"القلب هو مضخة الدم الرئيسية في جسم الإنسان.", "hint":"ينبض ويشعر بالنبض في الصدر."},
    # أضف هنا المزيد حسب الحاجة — يمكنك لاحقًا تحميل questions.json خاص بك
]

# ---------------------- وظائف مساعدة ----------------------
def load_questions_from_file(path: Path):
    """يحاول قراءة ملف JSON وإعادة قائمة الأسئلة"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # توفّر توافق بسيط بالتحقق من النموذج
        cleaned = []
        for i, r in enumerate(data):
            if isinstance(r, dict) and "question" in r and "choices" in r and "answer" in r:
                cleaned.append({
                    "id": r.get("id", i+1),
                    "question": r["question"],
                    "choices": r["choices"],
                    "answer": int(r["answer"]),
                    "explain": r.get("explain", ""),
                    "hint": r.get("hint", "")
                })
        return cleaned
    except Exception as e:
        return None

def init_session():
    """تهيئة مفاتيح session_state اللازمة"""
    if "game_ready" not in st.session_state:
        st.session_state.game_ready = False
    if "data" not in st.session_state:
        st.session_state.data = []
    if "pool" not in st.session_state:
        st.session_state.pool = []
    if "current" not in st.session_state:
        st.session_state.current = None
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "index" not in st.session_state:
        st.session_state.index = 0
    if "num_questions" not in st.session_state:
        st.session_state.num_questions = 10
    if "time_per_q" not in st.session_state:
        st.session_state.time_per_q = 30
    if "question_start_time" not in st.session_state:
        st.session_state.question_start_time = None
    if "used_ids" not in st.session_state:
        st.session_state.used_ids = set()
    if "last_answer_correct" not in st.session_state:
        st.session_state.last_answer_correct = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "hints_used" not in st.session_state:
        st.session_state.hints_used = 0
    if "played" not in st.session_state:
        st.session_state.played = False
    if "choices_selected" not in st.session_state:
        st.session_state.choices_selected = {}
    if "sound" not in st.session_state:
        st.session_state.sound = True

def prepare_game(num_questions:int):
    """خلي قائمة أسئلة عشوائية (بدون تكرار) جاهزة للعب"""
    data = deepcopy(st.session_state.data)
    if not data:
        return False, "لا توجد أسئلة متاحة. حمل ملف questions.json أو املأ بيانات داخل التطبيق."
    # فلترة الأسئلة حسب اللغة/شرط اذا حبيت لاحقًا
    # مزج القائمة واختيار n عناصر
    random.shuffle(data)
    pool = data[:num_questions] if num_questions <= len(data) else data[:]
    st.session_state.pool = pool
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.used_ids = set()
    st.session_state.hints_used = 0
    st.session_state.choices_selected = {}
    st.session_state.game_ready = True
    st.session_state.played = True
    return True, "جاهز"

def start_question():
    """ضبط بداية سؤال جديد"""
    if st.session_state.index >= len(st.session_state.pool):
        st.session_state.current = None
        return
    q = st.session_state.pool[st.session_state.index]
    st.session_state.current = deepcopy(q)
    st.session_state.question_start_time = time.time()
    # توليد مفتاح عشوائي لكل سؤال session-local
    st.session_state.choices_selected[st.session_state.index] = None

def time_left():
    """تُعيد الوقت المتبقي (بالثواني) للسؤال الحالي"""
    if st.session_state.question_start_time is None:
        return st.session_state.time_per_q
    elapsed = time.time() - st.session_state.question_start_time
    left = int(st.session_state.time_per_q - elapsed)
    return max(0, left)

def check_answer(selected_index:int):
    """تتحقّق الإجابة، تُحدّث النتيجة وتُرجع (is_correct, explanation)"""
    q = st.session_state.current
    if q is None: return False, ""
    correct = (selected_index == q["answer"])
    if correct:
        st.session_state.score += 1
        st.session_state.last_answer_correct = True
    else:
        st.session_state.last_answer_correct = False
    return correct, q.get("explain","")

# ---------------------- تحميل البيانات ----------------------
init_session()

# محاولة قراءة ملف الخارجي إذا موجود
loaded = None
if QUESTIONS_FILE.exists():
    loaded = load_questions_from_file(QUESTIONS_FILE)
    if loaded is None:
        # لو فشل التحميل أظهر تحذير للمستخدم لكن استمر مع fallback
        st.warning("ملف questions.json موجود لكن لم أستطع قراءته بشكل صحيح. سأستخدم بيانات احتياطية.")
else:
    # لا توجد ملف، نعرض لاحقاً زر لرفع الملف
    pass

if loaded:
    st.session_state.data = loaded
else:
    # استخدام قائمة احتياطية
    st.session_state.data = deepcopy(FALLBACK_DATA)

# ---------------------- واجهة المستخدم (الصفحة الرئيسية) ----------------------
st.markdown('<div class="big-title">لعبة الألغاز ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">اختبر معلوماتك في مواضيع مختلفة — واجهة عربية كاملة.</div>', unsafe_allow_html=True)

# شريط جانبي أو إعدادات سريعة
with st.sidebar:
    st.markdown("<h3>الإعدادات</h3>", unsafe_allow_html=True)
    # اسم اللاعب
    st.session_state.username = st.text_input("اكتب اسمك للبدء:", value=st.session_state.username or "")
    # تفعيل أو تعطيل الأصوات
    st.session_state.sound = st.checkbox("الصوت 🔊", value=st.session_state.sound)
    # تحميل ملف أسئلة جديد
    uploaded = st.file_uploader("حمّل ملف questions.json (اختياري)", type=["json"])
    if uploaded is not None:
        try:
            data_uploaded = json.load(uploaded)
            cleaned = []
            for i, r in enumerate(data_uploaded):
                if isinstance(r, dict) and "question" in r and "choices" in r and "answer" in r:
                    cleaned.append({
                        "id": r.get("id", i+1),
                        "question": r["question"],
                        "choices": r["choices"],
                        "answer": int(r["answer"]),
                        "explain": r.get("explain", ""),
                        "hint": r.get("hint", "")
                    })
            if cleaned:
                st.session_state.data = cleaned
                st.success(f"تم تحميل {len(cleaned)} سؤال بنجاح.")
            else:
                st.error("ملف JSON لا يحتوي على أسئلة بصيغة صحيحة.")
        except Exception as e:
            st.error("خطأ في قراءة الملف. تأكد من صيغته (UTF-8 JSON).")

    st.markdown("---")
    st.markdown("معلومات:")
    st.markdown("- التطبيق يدعم تحميل ملف JSON بصيغة معينة.\n- إن لم تقم بالتحميل، يستخدم بيانات احتياطية.")
    st.markdown("---")

# إعدادات اللعبة في الصفحة الرئيسية
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    # عدد الأسئلة
    num_q = st.slider("عدد الأسئلة:", min_value=5, max_value=min(50, len(st.session_state.data) if st.session_state.data else 50), value=st.session_state.num_questions)
    st.session_state.num_questions = num_q

    # وقت لكل سؤال
    t_q = st.slider("مدة كل سؤال (بالثواني):", min_value=10, max_value=180, value=st.session_state.time_per_q)
    st.session_state.time_per_q = t_q

    # زر البدء
    start_clicked = st.button("▶ ابدأ اللعبة", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# رسالة عدد الأسئلة المتاحة
st.write(f"الأسئلة المتاحة الآن: **{len(st.session_state.data)}**")

# عند الضغط على بدأ — نجهّز اللعبة
if start_clicked:
    ok, msg = prepare_game(st.session_state.num_questions)
    if not ok:
        st.error(msg)
    else:
        start_question()
        # إعادة تحميل الصفحة لضمان ظهور السؤال
        st.experimental_rerun()

# إذا اللعبة جاهزة، نعرض سؤال / ساحة اللعب
if st.session_state.game_ready and st.session_state.current:
    qidx = st.session_state.index
    total = len(st.session_state.pool)
    st.markdown(f'<div class="card"><div class="small-muted">السؤال {qidx+1} من {total}</div>', unsafe_allow_html=True)

    # شريط التقدّم
    progress = int(((qidx)/total) * 100)
    st.progress(progress)

    # المساحة الرئيسية للسؤال
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='direction:rtl'>{st.session_state.current['question']}</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # الوقت المتبقي
    left = time_left()
    st.markdown(f"⏱️ الوقت المتبقي: **{left} ث**")
    # إعادة حساب لو انتهى الوقت
    if left <= 0:
        # تعامل كأن المستخدم أخطأ أو تخطى (نمر للسؤال التالي مع عدم إضافة نقطة)
        st.success("انتهى الوقت! يتم الانتقال للسؤال التالي.")
        st.session_state.index += 1
        if st.session_state.index < len(st.session_state.pool):
            start_question()
            st.experimental_rerun()
        else:
            st.session_state.current = None
            st.experimental_rerun()

    # اختيارات المستخدم (radio)
    choices = st.session_state.current["choices"]
    # نحفظ اختيار المستخدم في session state
    sel_key = f"sel_{st.session_state.index}"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = None

    # عرض كل اختيار كزر راديو/زر مع تصميم
    selected = st.radio("الاختيارات:", options=list(range(len(choices))), format_func=lambda i: choices[i], index=st.session_state[sel_key] if st.session_state[sel_key] is not None else 0, key=sel_key, horizontal=False)

    # أزرار: تأكيد، تخطّي، تلميح
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("✅ تأكيد", key=f"confirm_{st.session_state.index}"):
            st.session_state[sel_saved] = None if False else None  # dummy line to avoid linter
            # تحقق من الاجابة
            correct, explanation = check_answer(selected)
            if correct:
                st.success("إجابة صحيحة! ✅")
            else:
                st.error("إجابة خاطئة ❌")
            # عرض الشرح
            if explanation:
                st.info(f"توضيح: {explanation}")
            # بعد التأكيد نمر للسؤال التالي بعد تأخير بسيط
            time.sleep(0.6)
            st.session_state.index += 1
            if st.session_state.index < len(st.session_state.pool):
                start_question()
                st.experimental_rerun()
            else:
                st.session_state.current = None
                st.experimental_rerun()

    with col2:
        if st.button("⏭ تخطّي", key=f"skip_{st.session_state.index}"):
            st.info("تم تخطي السؤال.")
            st.session_state.index += 1
            if st.session_state.index < len(st.session_state.pool):
                start_question()
                st.experimental_rerun()
            else:
                st.session_state.current = None
                st.experimental_rerun()

    with col3:
        if st.button("💡 تلميح", key=f"hint_{st.session_state.index}"):
            hint = st.session_state.current.get("hint","لا يوجد تلميح متاح.")
            st.info(f"تلميح: {hint}")
            st.session_state.hints_used += 1

    # عرض نقاط ومعلومات صغيرة
    st.markdown("---")
    st.write(f"النقاط الحالية: **{st.session_state.score}**  —  التلميحات المستخدمة: **{st.session_state.hints_used}**")
    st.markdown("---")

# لو اللعبة انتهت
elif st.session_state.played and (not st.session_state.current):
    st.markdown('<div class="card center">', unsafe_allow_html=True)
    st.markdown(f"<h2>انتهت الجولة 🎉</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='small-muted'>النتيجة: <strong>{st.session_state.score}</strong> من <strong>{st.session_state.num_questions}</strong></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # إعادة تشغيل / لعب جديد
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 العب مرة أخرى"):
            ok, msg = prepare_game(st.session_state.num_questions)
            if ok:
                start_question()
                st.experimental_rerun()
            else:
                st.error(msg)
    with col2:
        if st.button("🏠 العودة للرئيسية"):
            st.session_state.game_ready = False
            st.experimental_rerun()

# لو اللعبة لم تبدأ بعد (الصفحة الرئيسية الأولية)
else:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='center'><strong>قواعد اللعبة:</strong></div>", unsafe_allow_html=True)
    st.markdown("- اضغط 'ابدأ اللعبة' لبدء الجولات.\n- يمكنك تحميل ملف questions.json في الشريط الجانبي.\n- كل سؤال له وقت محدد يمكنك تغييره.\n- سيتم منع تكرار الأسئلة ضمن الجولة الحالية.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- نهاية الملف ----------------------
# تنبيه: لو تحب تضيف أصوات، ضع روابط ملفات mp3 في المتغيرات SOUND_CORRECT و SOUND_WRONG،
# واستعمل st.audio(URL) عند الحاجة بعد كل إجابة.
# كذلك لو تريد أن تحفظ سجل أعلى النقاط في ملف leaderboard.json يمكن إضافته بسهولة.
