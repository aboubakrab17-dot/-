# --------------------------- app.py (FULL) ---------------------------
import streamlit as st
import json
import random
import time
from typing import List, Dict, Any

# ====================== إعدادات عامة للصفحة + ستايل ======================
st.set_page_config(page_title="🎮 لعبة الألغاز", page_icon="🧠", layout="wide")

# خلفية (صورة ألعاب) + تصحيح شفافية البلوكات البيضاء
GAME_BG_URL = "https://images.unsplash.com/photo-1605901309584-818e25960a8b?q=80&w=1600&auto=format&fit=crop"
DARK_GLASS = """
<style>
/* خلفية الصفحة */
[data-testid="stAppViewContainer"]{
  background: url('""" + GAME_BG_URL + """') no-repeat center center fixed;
  background-size: cover;
}

/* طبقة شفافة داكنة */
.block-container{
  backdrop-filter: blur(3px);
  background: rgba(0,0,0,0.25) !important;
  border-radius: 16px;
  padding: 1.2rem 1.5rem;
}

/* نص أبيض واضح */
h1,h2,h3,h4,h5,h6, p, label, span, div{
  color: #f7f7fb !important;
}

/* أزرار */
.stButton>button{
  border-radius: 12px;
  padding: 0.6rem 1rem;
  font-weight: 700;
}

/* راديو خيارات */
div[role="radiogroup"] > label {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 12px;
  padding: 0.5rem 0.75rem;
  margin: 0.25rem 0;
}

/* إشعارات */
.stAlert{
  background: rgba(0,0,0,0.45) !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
}
</style>
"""
st.markdown(DARK_GLASS, unsafe_allow_html=True)

# ====================== وظائف مساعدة ======================
def safe_load_questions(path: str = "questions.json") -> Dict[str, List[Dict[str, Any]]]:
    """
    يحمّل ملف الأسئلة ويتأكد من البنية الصحيحة.
    يرجع {"ar": [...], "en":[...]} حتى لو فشل (بس قوائم فارغة) مع رسالة خطأ واضحة.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            st.error("❌ ملف questions.json يجب أن يحتوي مفاتيح لغات (ar, en).")
            return {"ar": [], "en": []}
        # تأكيد وجود المفاتيح
        ar = data.get("ar", [])
        en = data.get("en", [])
        if not isinstance(ar, list) or not isinstance(en, list):
            st.error("❌ مفاتيح ar/en يجب أن تكون قوائم أسئلة.")
            return {"ar": [], "en": []}
        # تنظيف كل سؤال والتأكد من الحقول
        def normalize(lst: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            norm = []
            for q in lst:
                if not isinstance(q, dict):
                    continue
                question = str(q.get("question", "")).strip()
                options = q.get("options", [])
                answer = str(q.get("answer", "")).strip()
                hint = str(q.get("hint", "")).strip() if q.get("hint") else ""
                if question and isinstance(options, list) and len(options) >= 2 and answer:
                    if answer not in options:
                        # إذا الإجابة الصح مش في الخيارات نضيفها ونخلط
                        options = list(dict.fromkeys(options + [answer]))
                    norm.append({
                        "question": question,
                        "options": options,
                        "answer": answer,
                        "hint": hint
                    })
            return norm
        return {"ar": normalize(ar), "en": normalize(en)}
    except FileNotFoundError:
        st.error("❌ لم يتم العثور على questions.json. ضع الملف بجانب app.py.")
        return {"ar": [], "en": []}
    except json.JSONDecodeError as e:
        st.error(f"❌ خطأ JSON في questions.json: {e}")
        return {"ar": [], "en": []}
    except Exception as e:
        st.error(f"⚠️ خطأ غير متوقع أثناء تحميل الأسئلة: {e}")
        return {"ar": [], "en": []}

def init_state():
    """تهيئة كل مفاتيح الحالة مرة واحدة."""
    defaults = {
        "screen": "menu",           # menu | game | result
        "lang": "ar",               # ar | en
        "num_questions": 10,        # عدد الأسئلة
        "time_per_q": 20,           # بالثواني لكل سؤال
        "questions": [],            # قائمة الأسئلة بعد الخلط والقص
        "q_index": 0,               # رقم السؤال الحالي
        "score": 0,                 # النقاط
        "start_ts": None,           # وقت بداية السؤال (ثواني)
        "show_hint": False,         # هل التلميح ظاهر؟
        "used_5050": set(),         # أسئلة استُعمل فيها 50/50
        "removed_opts": {},         # map: q_index -> set(options removed)
        "skipped": set(),           # أسئلة تم تخطيها
        "answered": set(),          # أسئلة جاوبها
        "progress": 0,              # نسبة التقدم
        "DATA": {"ar": [], "en": []}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_game():
    """إرجاع اللعبة للإعدادات الأولية مع إعادة اختيار الأسئلة."""
    DATA = st.session_state["DATA"]
    lang = st.session_state["lang"]
    all_q = DATA.get(lang, [])
    if not all_q:
        st.error("لا توجد أسئلة لهذه اللغة.")
        return
    # نخلط ونقص على قد المطلوب
    pool = all_q[:]
    random.shuffle(pool)
    count = max(1, min(st.session_state["num_questions"], len(pool)))
    st.session_state["questions"] = pool[:count]
    st.session_state["q_index"] = 0
    st.session_state["score"] = 0
    st.session_state["start_ts"] = time.time()
    st.session_state["show_hint"] = False
    st.session_state["used_5050"] = set()
    st.session_state["removed_opts"] = {}
    st.session_state["skipped"] = set()
    st.session_state["answered"] = set()
    st.session_state["progress"] = 0
    st.session_state["screen"] = "game"

def get_current_question() -> Dict[str, Any]:
    """يرجع السؤال الحالي بأمان."""
    idx = st.session_state["q_index"]
    qs = st.session_state["questions"]
    if 0 <= idx < len(qs):
        return qs[idx]
    return {}

def seconds_left() -> int:
    """الوقت المتبقي للسؤال الحالي."""
    per_q = st.session_state["time_per_q"]
    start = st.session_state["start_ts"]
    if not start:
        return per_q
    elapsed = int(time.time() - start)
    left = max(0, per_q - elapsed)
    return left

def next_question(auto=False):
    """الانتقال للسؤال التالي، وتحديث التقدم والوقت."""
    total = len(st.session_state["questions"])
    st.session_state["q_index"] += 1
    st.session_state["show_hint"] = False
    st.session_state["start_ts"] = time.time()
    st.session_state["progress"] = int((st.session_state["q_index"] / max(1, total)) * 100)
    if st.session_state["q_index"] >= total:
        st.session_state["screen"] = "result"
        if not auto:
            st.balloons()

def apply_5050(q_idx: int, question: Dict[str, Any]) -> List[str]:
    """
    50/50: يحذف خيارين خاطئين.
    يُخزّن المحذوف في removed_opts لكي يبقوا مخفيين عند إعادة الرسم.
    """
    options = question["options"][:]
    answer = question["answer"]
    wrongs = [o for o in options if o != answer]
    random.shuffle(wrongs)
    to_remove = set(wrongs[:max(1, len(options)//2 - 1)])  # حذف نصف الخاطئ تقريبا
    removed_map = st.session_state["removed_opts"]
    removed_map[q_idx] = to_remove
    st.session_state["removed_opts"] = removed_map
    st.session_state["used_5050"].add(q_idx)
    # نرجّع قائمة الخيارات المسموحة بعد الحذف
    return [o for o in options if o not in to_remove]

# ====================== تحميل الأسئلة ======================
init_state()
if not st.session_state["DATA"]["ar"] and not st.session_state["DATA"]["en"]:
    st.session_state["DATA"] = safe_load_questions()

# ====================== واجهة: القائمة الرئيسية ======================
def render_menu():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("## 🧠 لعبة الألغاز والأسئلة")
        st.write("إختبر معلوماتك وتحدَّ نفسك! اختر اللغة، عدد الأسئلة ومدة كل سؤال.")
    with col2:
        st.selectbox("🌐 Language / اللغة",
                     options=[("ar", "العربية"), ("en", "English")],
                     index=0,
                     format_func=lambda x: x[1],
                     key="lang")
        st.slider("🔢 عدد الأسئلة", min_value=5, max_value=30, value=10, step=1, key="num_questions")
        st.slider("⏳ مدة كل سؤال (ثانية)", min_value=10, max_value=60, value=20, step=5, key="time_per_q")

    DATA = st.session_state["DATA"]
    lang = st.session_state["lang"]
    avail = len(DATA.get(lang, []))
    st.info(f"الأسئلة المتاحة للغة المختارة: **{avail}**")

    c1, c2, _ = st.columns([1,1,2])
    with c1:
        if st.button("▶️ ابدأ اللعبة", use_container_width=True):
            if avail == 0:
                st.error("لا توجد أسئلة لهذه اللغة. تأكد من ملف questions.json.")
            else:
                reset_game()
    with c2:
        if st.button("🔄 إعادة التحميل (JSON)", use_container_width=True):
            st.session_state["DATA"] = safe_load_questions()
            st.success("تم تحديث الأسئلة من الملف.")

# ====================== واجهة: اللعب ======================
def render_game():
    q_idx = st.session_state["q_index"]
    total = len(st.session_state["questions"])
    question = get_current_question()
    if not question:
        st.error("لا يوجد سؤال حالي.")
        return

    # رأس اللعبة: تقدم + نقاط + عداد يتحرك
    top1, top2, top3 = st.columns([2,1,1])
    with top1:
        st.progress(st.session_state["progress"] / 100.0)
        st.caption(f"{q_idx+1} / {total}")

    with top2:
        st.metric("⭐ النقاط", f"{st.session_state['score']}")

    with top3:
        # عداد يتحرك
        place_timer = st.empty()
        left = seconds_left()
        place_timer.metric("⏱️ الوقت", f"{left}s")
        # تحديث تلقائي بسيط للعداد
        if left > 0:
            # force small sleep + rerun trick
            time.sleep(0.4)
            st.experimental_rerun()
        else:
            # الوقت انتهى → تخطي تلقائي
            st.warning("⏰ انتهى الوقت لهذا السؤال!")
            st.session_state["skipped"].add(q_idx)
            next_question(auto=True)
            st.experimental_rerun()

    # نص السؤال
    st.markdown(f"### ❓ {question['question']}")

    # خيارات (مع احترام 50/50 إن كانت مفعلة)
    current_options = question["options"][:]
    # إذا سبق طبقنا 50/50 في هذا السؤال
    if q_idx in st.session_state["removed_opts"]:
        removed = st.session_state["removed_opts"][q_idx]
        current_options = [o for o in current_options if o not in removed]

    # نخلط العرض فقط (لا نغيّر الأصل)
    shuffled = current_options[:]
    random.shuffle(shuffled)

    # راديو للاختيار
    pick_key = f"pick_{q_idx}"
    choice = st.radio("اختر الإجابة:", shuffled, key=pick_key, index=0 if shuffled else None)

    # أزرار التحكم
    bcol1, bcol2, bcol3, bcol4 = st.columns(4)

    # زر تلميح
    with bcol1:
        hint_label = "💡 إظهار التلميح" if not st.session_state["show_hint"] else "💡 إخفاء التلميح"
        if st.button(hint_label, use_container_width=True):
            st.session_state["show_hint"] = not st.session_state["show_hint"]

    # زر 50/50
    with bcol2:
        if q_idx in st.session_state["used_5050"]:
            st.button("🧪 50/50 (مُستخدم)", disabled=True, use_container_width=True)
        else:
            if st.button("🧪 50/50", use_container_width=True):
                new_opts = apply_5050(q_idx, question)
                st.info("تم حذف خيارين خاطئين.")
                st.experimental_rerun()

    # زر تخطي
    with bcol3:
        if st.button("⏭️ تخطي", use_container_width=True):
            st.session_state["skipped"].add(q_idx)
            next_question()
            st.experimental_rerun()

    # زر تأكيد
    with bcol4:
        if st.button("✅ تأكيد الإجابة", use_container_width=True):
            correct = question["answer"]
            if choice == correct:
                st.success("✔️ إجابة صحيحة!")
                st.session_state["score"] += 1
            else:
                st.error(f"❌ خاطئة. الإجابة الصحيحة: **{correct}**")
            st.session_state["answered"].add(q_idx)
            next_question()
            st.experimental_rerun()

    # عرض التلميح إن مفعّل
    if st.session_state["show_hint"]:
        if question.get("hint"):
            st.info(f"💬 تلميح: {question['hint']}")
        else:
            st.info("💬 لا يوجد تلميح لهذا السؤال.")

# ====================== واجهة: النتيجة ======================
def render_result():
    total = len(st.session_state["questions"])
    score = st.session_state["score"]
    skipped = len(st.session_state["skipped"])
    answered = len(st.session_state["answered"])

    st.markdown("## 🏁 النتيجة النهائية")
    st.success(f"النقاط: **{score} / {total}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("✅ أُجيبت", f"{answered}")
    with c2:
        st.metric("⏭️ مُتخطّاة", f"{skipped}")
    with c3:
        percent = int((score / total) * 100) if total else 0
        st.metric("📊 نسبة النجاح", f"{percent}%")

    # تقييم بسيط
    if percent == 100:
        st.balloons()
        st.info("🎉 ممتاز! أداء أسطوري.")
    elif percent >= 70:
        st.info("💪 رائع! معلوماتك قوية.")
    elif percent >= 40:
        st.warning("🙂 جيد، مزيد من التدريب يفيد.")
    else:
        st.error("😅 تحتاج مراجعة أكثر، جرّب مرة أخرى.")

    st.divider()
    r1, r2 = st.columns(2)
    with r1:
        if st.button("🔁 إعادة اللعب بنفس الإعدادات", use_container_width=True):
            reset_game()
            st.experimental_rerun()
    with r2:
        if st.button("🏠 عودة للقائمة الرئيسية", use_container_width=True):
            st.session_state["screen"] = "menu"
            st.experimental_rerun()

# ====================== التوجيه العام ======================
screen = st.session_state["screen"]
if screen == "menu":
    render_menu()
elif screen == "game":
    render_game()
elif screen == "result":
    render_result()
else:
    st.session_state["screen"] = "menu"
    st.experimental_rerun()
# ------------------------ END app.py ------------------------
