# app.py
import streamlit as st
import sqlite3
import hashlib
from io import BytesIO
import base64
from PIL import Image
import textwrap
import datetime

# -----------------------
# إعداد قاعدة البيانات
# -----------------------
DB_PATH = "lingo_mvp.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # جدول المستخدمين
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            password_hash TEXT,
            points INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    # جدول تقدم المستخدم في الدروس
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course TEXT,
            lesson_index INTEGER,
            score INTEGER DEFAULT 0,
            updated_at TEXT,
            UNIQUE(user_id, course)
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(name, email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
                  (email, name, hash_password(password), datetime.datetime.utcnow().isoformat()))
        conn.commit()
        return True, "تم التسجيل بنجاح!"
    except sqlite3.IntegrityError:
        return False, "الإيميل مستخدم من قبل."
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, password_hash, points FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, "المستخدم غير موجود."
    uid, name, pw_hash, points = row
    if pw_hash == hash_password(password):
        return True, {"id": uid, "name": name, "email": email, "points": points}
    return False, "كلمة المرور خاطئة."

def get_user_by_id(uid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, email, points FROM users WHERE id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "points": row[3]}
    return None

def update_user_points(uid, delta):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE id = ?", (delta, uid))
    conn.commit()
    conn.close()

def get_progress(uid, course):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT lesson_index, score FROM progress WHERE user_id = ? AND course = ?", (uid, course))
    row = c.fetchone()
    conn.close()
    if row:
        return {"lesson_index": row[0], "score": row[1]}
    return {"lesson_index": 0, "score": 0}

def save_progress(uid, course, lesson_index, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT OR REPLACE INTO progress (id, user_id, course, lesson_index, score, updated_at) VALUES (COALESCE((SELECT id FROM progress WHERE user_id=? AND course=?), NULL), ?, ?, ?, ?, ?)",
              (uid, course, uid, course, lesson_index, score, now))
    conn.commit()
    conn.close()

# -----------------------
# محتوى الدروس (MVP صغير)
# -----------------------
COURSES = {
    "English Basics": {
        "title_ar": "الإنجليزية للمبتدئين",
        "lessons": [
            {
                "title": "Greetings",
                "text": "Hello = مرحبا\nGoodbye = وداعا\nPlease = من فضلك\nThank you = شكرا",
                "quiz": {
                    "question": "What does 'Hello' mean?",
                    "options": ["وداعا", "مرحبا", "شكرا", "من فضلك"],
                    "answer": 1
                }
            },
            {
                "title": "Simple verbs",
                "text": "I eat = أنا آكل\nI go = أنا أذهب\nI read = أنا أقرأ",
                "quiz": {
                    "question": "Which means 'I go'?",
                    "options": ["أنا أقرأ", "أنا أذهب", "أنا آكل", "أنا ألعب"],
                    "answer": 1
                }
            },
            {
                "title": "Numbers",
                "text": "One = 1\nTwo = 2\nThree = 3\nFour = 4",
                "quiz": {
                    "question": "What is 'Three'?",
                    "options": ["2", "3", "4", "1"],
                    "answer": 1
                }
            },
        ]
    },

    # يمكنك إضافة دورات أخرى لاحقاً بنفس الصيغة
    "Travel Arabic": {
        "title_ar": "العربية للسفر",
        "lessons": [
            {
                "title": "At the airport",
                "text": "Passport = جواز السفر\nTicket = تذكرة\nGate = بوابة",
                "quiz": {
                    "question": "What is 'Passport'?",
                    "options": ["تذكرة", "جواز السفر", "بوابة", "جواز سفر؟"],
                    "answer": 1
                }
            }
        ]
    }
}

# قائمة اقتراحات (مثال 40 اقتراح) - المستخدم يقدر يضغط على اقتراح ويبدأ درس/سؤال
SUGGESTIONS = [
    "تعلم التحيات بالإنجليزية",
    "تمارين على الأرقام",
    "جمل يومية قصيرة",
    "أفعال أساسية",
    "محادثة سريعة: تقديم نفسك",
    "تعلّم كلمات السفر",
    "سؤال/جواب للترجمة",
    "اختبار سريع 5 أسئلة",
    "قواعد بسيطة: زمن المضارع",
    "أسماء الأماكن في المدينة",
    "محادثة مطولة 10 جمل",
    "تعلم 20 كلمة جديدة",
    "تمارين استماع (نص)",
    "ترجمة جملة من العربية للإنجليزية",
    "جمل المحادثة في المطعم",
    "أسئلة مقابلة عمل بسيطة",
    "قائمة الصفات الشائعة",
    "مفردات العمل والمكتب",
    "تعلم أيام الأسبوع",
    "سؤال/جواب: الهوايات",
    "نطق الحروف الإنجليزية",
    "تمارين على صيغة السؤال",
    "ترتيب الكلمات",
    "اربط الصور بكلمات (صوري)",
    "مرحلة مراجعة: دروس 1-3",
    "لعبة مطابقة كلمات",
    "تحدي حفظ قائمة كلمات 10",
    "محادثة هاتفية بسيطة",
    "اختبار القواعد: اختيار متعدد",
    "سيرة ذاتية قصيرة بالإنجليزية",
    "أمثلة على استخدام 'can' و 'could'",
    "محادثة: في الفندق",
    "تعلّم أزمنة الماضي البسيط",
    "جمل للتسوق",
    "قواعد الجمع",
    "أسئلة قصيرة: لماذا؟ متى؟",
    "تمارين ترجمة عكسي",
    "تحدي 7 أيام تعلم جديد",
    "مراجعة عامة سريعة"
]

# -----------------------
# تصميم CSS والخلفية
# -----------------------
def local_css():
    # خلفية جميلة عبر صورة URL (يمكن تغييره)
    bg_url = "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1400&q=80"
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {{
        font-family: 'Cairo', sans-serif;
    }}
    .stApp {{
        background-image: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("{bg_url}");
        background-size: cover;
        background-attachment: fixed;
        color: #07203a;
    }}
    .title-area {{
        background: rgba(255,255,255,0.6);
        padding: 18px;
        border-radius: 12px;
        text-align: center;
    }}
    .chat-bubble-user {{
        background: #dff7e8;
        padding: 12px;
        border-radius: 12px;
        margin: 8px 0;
        max-width: 90%;
    }}
    .chat-bubble-bot {{
        background: #dbeeff;
        padding: 12px;
        border-radius: 12px;
        margin: 8px 0;
        max-width: 90%;
    }}
    .suggestion-btn {{
        margin:4px;
        background: #fff;
        color: #07203a;
        border-radius: 999px;
        padding: 8px 14px;
        display:inline-block;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------
# واجهة التطبيق واللوجيك
# -----------------------
def render_header():
    st.markdown('<div class="title-area">', unsafe_allow_html=True)
    st.markdown("<h1>🌟 LingoDZ — منصة تعليمية بسيطة</h1>", unsafe_allow_html=True)
    st.markdown("<p>ابدأ بتعلّم كلمة أو درس صغير — سريع، ممتع، وفعّال.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    init_db()
    local_css()

    if "user" not in st.session_state:
        st.session_state.user = None

    # تخطيط القوائم
    menu = ["الصفحة الرئيسية", "الدورات", "اقتراحات سريعة", "حسابي/تسجيل"]
    choice = st.sidebar.selectbox("القائمة", menu)

    render_header()

    # الصفحة الرئيسية
    if choice == "الصفحة الرئيسية":
        st.subheader("مرحباً بك! اختر درس سريع من الاقتراحات أو سجل/سجل دخول للمتابعة.")
        # عرض شريط اقتراحات (بعضها)
        st.markdown("### اقتراحات سريعة")
        cols = st.columns(4)
        for i, s in enumerate(SUGGESTIONS[:12]):
            col = cols[i % 4]
            if col.button(s):
                # اختر درس (نحو الدورات) إذا نص الاقتراح يتوافق
                st.session_state["selected_suggestion"] = s
                st.experimental_rerun()

        st.markdown("---")
        st.markdown("### الدورات المتاحة")
        for k, v in COURSES.items():
            st.markdown(f"**{k}** - {v['title_ar']}")
            if st.button(f"ابدأ {k}", key=f"start_{k}"):
                st.session_state.selected_course = k
                st.experimental_rerun()

    # صفحة الدورات
    elif choice == "الدورات":
        st.header("الدورات")
        for k, v in COURSES.items():
            st.subheader(f"{k} — {v['title_ar']}")
            st.caption(f"عدد الدروس: {len(v['lessons'])}")
            if st.button(f"دخول {k}", key=f"enter_{k}"):
                st.session_state.selected_course = k
                st.experimental_rerun()

        # إذا اخترت دورة
        if "selected_course" in st.session_state:
            course_key = st.session_state.selected_course
            course = COURSES[course_key]
            st.markdown("---")
            st.markdown(f"## دورة: {course_key} — {course['title_ar']}")
            # تأكد من تسجيل الدخول لتخزين التقدم
            if st.session_state.user:
                uid = st.session_state.user["id"]
                prog = get_progress(uid, course_key)
                lesson_index = prog["lesson_index"]
            else:
                lesson_index = 0

            # عرض الدرس الحالي
            lesson = course["lessons"][lesson_index]
            st.markdown(f"### الدرس {lesson_index + 1}: {lesson['title']}")
            st.markdown(f"**المعلومة:**\n{lesson['text']}")
            st.markdown("---")
            st.markdown("#### الاختبار")
            q = lesson["quiz"]
            st.write(q["question"])
            choice_idx = st.radio("اختر الإجابة الصحيحة:", q["options"], key=f"quiz_{course_key}_{lesson_index}")
            if st.button("تأكد الإجابة", key=f"check_{course_key}_{lesson_index}"):
                selected_index = q["options"].index(choice_idx)
                correct = (selected_index == q["answer"])
                if correct:
                    st.success("✅ إجابة صحيحة!")
                    # نقاط وتقدم
                    if st.session_state.user:
                        uid = st.session_state.user["id"]
                        update_user_points(uid, 10)
                        # حفظ التقدم للدرس التالي
                        new_idx = min(len(course["lessons"]) - 1, lesson_index + 1)
                        save_progress(uid, course_key, new_idx, 10)
                        # تحديث جلسة المستخدم
                        st.session_state.user = get_user_by_id(uid)
                    else:
                        st.info("سجّل الدخول لحفظ تقدمك وكسب النقاط.")
                else:
                    st.error("❌ للأسف الإجابة خاطئة. جرّب مرة أخرى!")
            # أزرار للتنقّل بين الدروس
            cols = st.columns(3)
            if cols[0].button("السابق") and lesson_index > 0:
                if st.session_state.user:
                    save_progress(st.session_state.user["id"], course_key, lesson_index - 1, 0)
                st.experimental_rerun()
            if cols[1].button("التالي") and lesson_index < len(course["lessons"]) - 1:
                if st.session_state.user:
                    save_progress(st.session_state.user["id"], course_key, lesson_index + 1, 0)
                    st.session_state.user = get_user_by_id(st.session_state.user["id"])
                else:
                    st.info("سجّل الدخول لحفظ تقدمك.")
                st.experimental_rerun()
            if cols[2].button("اختر درس معين"):
                idx = st.number_input("رقم الدرس (1-based):", min_value=1, max_value=len(course["lessons"]), value=lesson_index+1)
                if st.button("اذهب للدرس"):
                    target = idx - 1
                    if st.session_state.user:
                        save_progress(st.session_state.user["id"], course_key, target, 0)
                        st.session_state.user = get_user_by_id(st.session_state.user["id"])
                    st.experimental_rerun()

    # صفحة الاقتراحات
    elif choice == "اقتراحات سريعة":
        st.header("اختر اقتراح أو ابحث")
        query = st.text_input("ابحث في الاقتراحات")
        filtered = [s for s in SUGGESTIONS if query.strip().lower() in s.lower()] if query else SUGGESTIONS
        for s in filtered:
            if st.button(s):
                st.success(f"اخترت: {s}")
                # ممكن تحويل بعض الاقتراحات لدورة أو درس
                st.info("قريبًا سنربط بعض الاقتراحات بدروس حقيقية. الآن يمكنك اختيار دورة من قائمة 'الدورات'.")
        st.markdown("---")
        st.markdown("اقتراحات شائعة:")
        st.write(", ".join(SUGGESTIONS[:20]))

    # صفحة الحساب / التسجيل
    elif choice == "حسابي/تسجيل":
        st.header("حسابي")
        if st.session_state.user:
            user = get_user_by_id(st.session_state.user["id"])
            st.markdown(f"**مرحباً، {user['name']}**")
            st.markdown(f"📧 {user['email']}")
            st.markdown(f"⭐ نقاطك: {user['points']}")
            if st.button("تسجيل الخروج"):
                st.session_state.user = None
                st.experimental_rerun()
        else:
            st.subheader("تسجيل جديد")
            with st.form("register_form"):
                r_name = st.text_input("الاسم الكامل")
                r_email = st.text_input("الإيميل")
                r_password = st.text_input("كلمة المرور", type="password")
                register_sub = st.form_submit_button("سجل الآن")
                if register_sub:
                    ok, msg = register_user(r_name.strip(), r_email.strip(), r_password)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

            st.subheader("أو سجّل الدخول")
            with st.form("login_form"):
                l_email = st.text_input("الإيميل (للدخول)")
                l_password = st.text_input("كلمة المرور", type="password")
                login_sub = st.form_submit_button("دخول")
                if login_sub:
                    ok, payload = login_user(l_email.strip(), l_password)
                    if ok:
                        st.session_state.user = payload
                        st.success("تم تسجيل الدخول!")
                        st.experimental_rerun()
                    else:
                        st.error(payload)

    # قسم أفكار/مميزات أخرى صغير
    st.markdown("---")
    st.markdown("### ملاحظات سريعة")
    st.markdown("- هذا إصدار MVP: نعطيك قاعدة تشتغل عليها.\n- فيما بعد نضيف تسجيل عبر Google، آداء صوتي، تمارين سماع، ومحتوى متدرّج.")
    st.markdown("إذا أردت إضافة دروس جديدة أو تحسين واجهة ابعث لي وسنطوّرها سوا ❤️")

if __name__ == "__main__":
    main()
