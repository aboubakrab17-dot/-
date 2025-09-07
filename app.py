import streamlit as st
import json, random, time, os
from pathlib import Path

# ---------------- إعدادات الصفحة + ثيم عام ----------------
st.set_page_config(page_title="لعبة الألغاز العربية", page_icon="🎮", layout="centered")

# ---------------- تنسيقات CSS (خلفية + بطاقات) ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

:root {
  --accent: #ffcc00;
  --accent2: #00e0ff;
}

html, body, .stApp {
  height: 100%;
  background: radial-gradient(1200px 600px at 20% 10%, rgba(255,255,255,0.08), transparent 40%),
              radial-gradient(1000px 500px at 90% 20%, rgba(0,224,255,0.10), transparent 45%),
              linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0b1324 100%);
  color: #f8fafc;
  font-family: "Cairo", sans-serif;
}

h1,h2,h3 { color: var(--accent); text-shadow: 0 2px 14px rgba(255,204,0,.15); }
.small { font-size: 0.9rem; opacity:.85 }

.card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  backdrop-filter: blur(6px);
}

.badge {
  display:inline-block; padding:6px 10px; border-radius:999px;
  background: linear-gradient(135deg, var(--accent), #ffa600);
  color:#111; font-weight:700; font-size:.9rem; margin-left:8px;
}

.button-primary .stButton>button {
  width: 100%;
  background: linear-gradient(135deg, #ffcc00, #ffa600);
  border: none; color: #111; font-weight:800; font-size:18px;
  padding: 12px 18px; border-radius: 12px;
  box-shadow: 0 8px 24px rgba(255,204,0,.25);
}
.button-primary .stButton>button:hover { filter: brightness(1.1); }

.button-ghost .stButton>button {
  width: 100%;
  background: transparent; border: 1px solid rgba(255,255,255,0.25);
  color: #fff; font-weight:700; font-size:16px; padding:10px 14px; border-radius:12px;
}
.button-ghost .stButton>button:hover { background: rgba(255,255,255,0.08); }

.timer {
  background: linear-gradient(90deg, #00e0ff, #00ffa6);
  color:#111; padding:6px 14px; border-radius:999px; font-weight:800; display:inline-block;
  box-shadow: 0 6px 18px rgba(0, 224, 255, .3);
}

.progress-wrap {
  background: rgba(255,255,255,0.12); height:10px; border-radius:999px; overflow:hidden;
}
.progress-bar {
  height:10px; background: linear-gradient(90deg, #00ffa6, #00e0ff);
  width:0%; transition: width .3s ease;
}

.option-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius:12px; padding:12px; margin-bottom:8px;
}
.footer-note { opacity:.75; font-size:.85rem; text-align:center; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- تحميل الأسئلة ----------------
def load_questions(path="questions.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    random.shuffle(data)
    return data

# ---------------- أدوات الصوت (تشغيل/إيقاف) ----------------
def audio_tag(src, autoplay=True, loop=False, volume=0.6):
    auto = "autoplay" if autoplay else ""
    loop_attr = "loop" if loop else ""
    vol = max(0, min(volume, 1))
    return f"""
    <audio {auto} {loop_attr} style="display:none" id="bgm" volume="{vol}">
      <source src="{src}" type="audio/mpeg">
    </audio>
    """

def play_sfx(src):
    st.markdown(
        f"""
        <audio autoplay style="display:none">
          <source src="{src}" type="audio/mpeg">
        </audio>
        """,
        unsafe_allow_html=True
    )

# ---------------- تهيئة الحالة ----------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.q_idx = 0
    st.session_state.questions = []
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.deadline = 0.0
    st.session_state.music_on = True
    st.session_state.best_scores = []  # ترتيب محلي داخل الجلسة

Q_TIME = 20  # ثواني لكل سؤال

# ---------------- ترويسة ----------------
colA, colB = st.columns([1,1])
with colA:
    st.markdown("### 🎮 لعبة الألغاز العربية")
with colB:
    # زر الصوت
    lab = "🔊 إيقاف الموسيقى" if st.session_state.music_on else "🔈 تشغيل الموسيقى"
    if st.button(lab):
        st.session_state.music_on = not st.session_state.music_on

# موسيقى الخلفية
if st.session_state.music_on and Path("background.mp3").exists():
    st.markdown(audio_tag("background.mp3", autoplay=True, loop=True, volume=0.4), unsafe_allow_html=True)

st.markdown(
    '<div class="card">'
    'اختبر معلوماتك في التاريخ، الجغرافيا، العلوم، الدين، والثقافة عامة. جاوب بسرعة قبل ما يخلص الوقت ⏱️ '
    '<span class="badge">تحدّي ممتع</span>'
    '</div>', unsafe_allow_html=True
)

# ---------------- شاشة البداية ----------------
if not st.session_state.started:
    c1, c2 = st.columns([1,1])
    with c1:
        st.selectbox("🎯 اختر نمط اللعب", ["عادي (20 ثانية/سؤال)"], key="mode")
        st.slider("🔢 عدد الأسئلة", min_value=5, max_value=20, value=10, key="n_questions")
    with c2:
        st.text_input("📝 اسم اللاعب (اختياري):", key="player_name", placeholder="اكتب اسمك هنا")
        with st.container():
            st.markdown('<div class="button-primary">', unsafe_allow_html=True)
            start_clicked = st.button("▶️ ابدأ الآن")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-note">نصيحة: جرّب تحط سماعات 🎧 لسطوع المؤثرات الصوتية.</div>', unsafe_allow_html=True)

    if start_clicked:
        # تحميل الأسئلة وتصفية العدد المطلوب
        st.session_state.questions = load_questions()[:st.session_state.n_questions]
        st.session_state.q_idx = 0
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.started = True
        st.session_state.deadline = time.time() + Q_TIME
        st.rerun()

# ---------------- شاشة اللعبة ----------------
if st.session_state.started and st.session_state.q_idx < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.q_idx]

    # العداد
    time_left = max(0, int(st.session_state.deadline - time.time()))
    pct = int((time_left / Q_TIME) * 100) if Q_TIME > 0 else 0
    st.markdown(f"**⏱️ الوقت:** <span class='timer'>{time_left} ث</span>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="progress-wrap"><div class="progress-bar" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)

    # نص السؤال
    st.markdown(f"<div class='card'><h3>🧩 {q['question']}</h3></div>", unsafe_allow_html=True)

    # الخيارات
    # نجبر ترتيب عشوائي ثابت للسؤال الحالي
    if "shuffled" not in q:
        opts = q["options"][:]
        random.shuffle(opts)
        q["shuffled"] = opts

    choice = st.radio("اختر إجابة:", options=q["shuffled"], index=0, key=f"opt_{st.session_state.q_idx}", label_visibility="visible")

    # أزرار التحكم
    cA, cB, cC = st.columns([1,1,1])
    with cA:
        confirm = st.button("✅ تأكيد")
    with cB:
        skip = st.button("⏭️ تخطي")
    with cC:
        hint = st.button("💡 تلميح")

    # تلميح (يحذف خيارين خطأ إن أمكن)
    if hint:
        wrongs = [o for o in q["shuffled"] if o != q["answer"]]
        if len(wrongs) >= 2:
            to_remove = set(random.sample(wrongs, 2))
            q["shuffled"] = [o for o in q["shuffled"] if o not in to_remove or o == q["answer"]]
            st.info("تم حذف خيارين خاطئين 😉")
        else:
            st.info("لا يمكن حذف المزيد.")

    # انتهاء الوقت تلقائياً
    if time_left == 0 and not confirm:
        # وقت انتهى = إجابة خاطئة
        if Path("wrong.mp3").exists(): play_sfx("wrong.mp3")
        st.error(f"انتهى الوقت! الإجابة الصحيحة: **{q['answer']}**")
        st.session_state.streak = 0
        st.session_state.q_idx += 1
        if st.session_state.q_idx < len(st.session_state.questions):
            st.session_state.deadline = time.time() + Q_TIME
        st.button("التالي ▶️")  # زر وهمي يظهر لحظة
        st.rerun()

    # تأكيد الإجابة
    if confirm:
        if choice == q["answer"]:
            if Path("correct.mp3").exists(): play_sfx("correct.mp3")
            st.success("👏 رائع! إجابة صحيحة.")
            st.session_state.score += 1
            st.session_state.streak += 1
            if st.session_state.streak and st.session_state.streak % 3 == 0:
                st.balloons()
                st.info(f"🔥 سلسلة صحيحة: {st.session_state.streak}")
        else:
            if Path("wrong.mp3").exists(): play_sfx("wrong.mp3")
            st.error(f"❌ خاطئة! الجواب الصحيح: **{q['answer']}**")
            st.session_state.streak = 0

        st.session_state.q_idx += 1
        if st.session_state.q_idx < len(st.session_state.questions):
            st.session_state.deadline = time.time() + Q_TIME
        st.rerun()

    # تخطي
    if skip:
        st.session_state.streak = 0
        st.session_state.q_idx += 1
        if st.session_state.q_idx < len(st.session_state.questions):
            st.session_state.deadline = time.time() + Q_TIME
        st.rerun()

    # عرض إحصائيات صغيرة
    st.markdown(
        f"<div class='small'>النقــاط: <b>{st.session_state.score}</b> · "
        f"السؤال: <b>{st.session_state.q_idx+1}/{len(st.session_state.questions)}</b> · "
        f"السلسلة: <b>{st.session_state.streak}</b></div>", unsafe_allow_html=True)

# ---------------- شاشة النهاية ----------------
elif st.session_state.started and st.session_state.q_idx >= len(st.session_state.questions):
    name = st.session_state.get("player_name") or "لاعب"
    total = len(st.session_state.questions)
    score = st.session_state.score
    st.markdown(f"## 🏆 أحسنت يا {name}!")
    st.markdown(
        f"<div class='card'><h3>نتيجتك: {score} / {total}</h3>"
        f"<p class='small'>جرّب مرة أخرى وحسّن رقمك 👑</p></div>", unsafe_allow_html=True)

    # حفظ في ترتيب محلي
    st.session_state.best_scores.append({"name": name, "score": score, "total": total, "time": int(time.time())})
    st.session_state.best_scores = sorted(st.session_state.best_scores, key=lambda x: (-x["score"], x["time"]))[:10]

    st.subheader("🏅 أفضل النتائج (داخل هذه الجلسة)")
    for i, row in enumerate(st.session_state.best_scores, 1):
        st.write(f"{i}. {row['name']} — {row['score']} / {row['total']}")

    st.markdown('<div class="button-primary">', unsafe_allow_html=True)
    if st.button("🔄 العب من جديد"):
        st.session_state.started = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
