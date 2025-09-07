# app.py
# ─────────────────────────────────────────────────────────────────────
# بوت دردشة ستايل واتساب/مسنجر — بدون API — streamlit فقط
# “نسخة كبيرة” مليانة إضافات مرقّمة داخل الكود للتنظيم
# ─────────────────────────────────────────────────────────────────────
import streamlit as st
import time, datetime, random, ast, re

# 0) إعداد الصفحة
st.set_page_config(page_title="البوت الشاب — دردشة واتساب", page_icon="💬", layout="wide")

# 1) حالة الجلسة
SS = st.session_state
def ss_init():
    if "messages" not in SS: SS["messages"] = []               # رسائل الدردشة
    if "typing"   not in SS: SS["typing"]   = False            # مؤشر يكتب…
    if "dark"     not in SS: SS["dark"]     = False            # وضع داكن
    if "theme"    not in SS: SS["theme"]    = "fresh"          # اختيار خلفية/ألوان
    if "font_scale" not in SS: SS["font_scale"] = 18           # حجم الخط في البابل
    if "todo"     not in SS: SS["todo"]     = []               # قائمة مهام
    if "todo_done"not in SS: SS["todo_done"]= []               # مهام منجزة
    if "timer_end"not in SS: SS["timer_end"]= 0                # مؤقت (ثواني unix)
    if "reminders"not in SS: SS["reminders"]= []               # تذكيرات [(ts,text)]
    if "stars"    not in SS: SS["stars"]    = set()            # رسائل مفضلة indices
    if "sfilter"  not in SS: SS["sfilter"]  = ""               # فلتر اقتراحات
    if "counter"  not in SS: SS["counter"]  = 0                # عداد رسائل
    if "palette"  not in SS: SS["palette"]  = ["#25D366","#0084FF","#FF9800","#E91E63","#673AB7"]
ss_init()

# 2) CSS — خلفية + واتساب بابل + إزالة هوامش بيضاء للأزرار
def inject_style():
    dark = "dark" if SS["dark"] else "light"
    fs   = SS["font_scale"]
    theme = SS["theme"]
    # لوحات ألوان وخلفيات
    bg = {
      "fresh": "linear-gradient(135deg,#c9eaff 0%, #fdfbfb 40%, #ffe9f0 100%)",
      "night": "linear-gradient(135deg,#111 0%, #222 50%, #333 100%)",
      "sunset":"linear-gradient(135deg,#ff9a9e 0%,#fecfef 40%,#feada6 100%)",
      "forest":"linear-gradient(135deg,#a8e6cf 0%,#dcedc1 50%,#ffd3b6 100%)",
      "ocean" :"linear-gradient(135deg,#2193b0 0%,#6dd5ed 100%)"
    }
    user_bubble = "#dcf8c6" if not SS["dark"] else "#056162"
    bot_bubble  = "#e1f0ff" if not SS["dark"] else "#262d31"
    text_color  = "#111" if not SS["dark"] else "#fff"
    sub_color   = "#222" if not SS["dark"] else "#eee"

    st.markdown(f"""
    <style>
    #MainMenu, header, footer {{visibility: hidden;}}
    html, body {{
      background: {bg[theme]} !important;
      font-family: 'Segoe UI', Tahoma, sans-serif;
    }}
    .block-container {{ padding-top: 8px !important; }}

    .chat-wrap {{
      max-width: 960px; margin: 0 auto;
      padding: 8px 6px 30px; direction: rtl;
    }}
    .header-title {{ text-align:center; color: #0b5cff; font-weight: 900; font-size: 30px; }}
    .header-sub  {{ text-align:center; color: {sub_color}; font-size: 16px; }}

    .msg {{
      padding: 12px 16px; border-radius: 18px; margin: 10px 0;
      max-width: 86%; font-size: {fs}px; line-height: 1.65; word-wrap: break-word;
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }}
    .msg.user {{
      margin-left: auto; background: {user_bubble}; color: {text_color}; text-align: right;
    }}
    .msg.bot  {{
      margin-right: auto; background: {bot_bubble}; color: {text_color}; text-align: left;
    }}
    .msg .time {{ font-size: 12px; color: #666; margin-top: 6px; opacity: .9; text-align: right; }}
    .msg.bot .time {{ text-align: left; }}

    .stButton>button {{
      margin: 6px 0 !important;
      background: #25D366; color: #fff;
      border: none !important; border-radius: 26px;
      padding: 10px 16px; font-size: 16px; font-weight: 700;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
      transition: transform .08s, background .12s;
    }}
    .stButton>button:hover {{ background: #128C7E; transform: translateY(-1px); }}
    .stButton {{ background: transparent !important; }}

    .suggestion button {{
      background: #0084FF !important; box-shadow: 0 4px 10px rgba(0,132,255,0.20) !important;
      border: none !important; color: #fff !important; font-weight: 800;
    }}
    .suggestion button:hover {{ background: #0a6ddc !important; }}
    .sugg-title {{ font-size: 18px; font-weight: 900; color: {sub_color}; margin: 8px 0 4px; }}

    .typing {{ font-size: 14px; color: #666; margin: 6px 0 4px; }}
    .clear button {{ background: #e9e9e9 !important; color: #333 !important; }}
    .clear button:hover {{ background: #d8d8d8 !important; }}

    .palette button {{
      border: none !important; height: 32px; border-radius: 18px;
    }}

    .star span {{ color: #ffb400; }}
    </style>
    """,  True)
inject_style()

# 3) helper
def now_ts():  return time.time()
def fmt_time(ts): return datetime.datetime.fromtimestamp(ts).strftime("%H:%m:%S").replace(":", ":", 1) # keep rtl
def add_user(text):  SS["messages"].append({"role":"user","content":text,"ts":now_ts()}); SS["counter"]+=1
def add_bot(text):   SS["messages"].append({"role":"bot" ,"content":text,"ts":now_ts()});  SS["counter"]+=1
def render_chat():
    i = 0
    for m in SS["messages"]:
        css = "user" if m["role"]=="user" else "bot"
        star = "⭐" if i in SS["stars"] else ""
        html = f"<div class='msg {css}'><div style='float:left' class='star'>{star}</div>{m['content']}<div class='time'>{fmt_time(m['ts'])}</div></div>"
        st.markdown(html, True)
        i+=1

def export_txt():
    lines=[]
    for m in SS["messages"]:
      who = "أنا" if m["role"]=="user" else "البوت"
      lines.append(f"[{fmt_time(m['ts'])}] {who}: {m['content']}")
    return "\n".sap(["a"])

# 100 add-on helpers: arithmetic safe eval
class SafeEval(ast.NodeVisitor):
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Pow,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.USub,
               ast.Num, ast.Load, ast.Constant, ast.FloorDiv, ast.LShift, ast.RShift)
    def visit(self, node):
        if not isinstance(node, self.allowed):
            raise ValueError("op")
        return super().visit(node)

def calc_expr(expr):
    tree = ast.parse(expr, mode="eval")
    SafeEval().visit(tree)
    return eval(compile(tree, "<calc>", "eval"), {}, {})

# 4) suggestions: 60+ items
suggestions = [
 "خطة دراسة أسبوعية","تعلم الإنجليزية من الصفر","تعلم البرمجة خطوة خطوة","HTML/CSS/JS بسرعة",
 "مصادر مجانية للتعلم","حكمة اليوم","نكتة لطيفة","تمارين بيتية","وصفة صحية سريعة","تنظيم وقت الدراسة",
 "طرق التركيز","زيادة الثقة بالنفس","تحسين الذاكرة","أفضل تطبيقات هاتف","10 أفكار محتوى",
 "مشروع متجر بسيط","الربح من النت","بناء موقع شخصي","صفحة سيرة ذاتية","قائمة مهام يومية",
 "خطة حفظ قرآن أسبوعية","روتين صباحي قوي","روتين مسائي هادئ","إدارة الديون","ميزانية شهرية",
 "تعلم بايثون","تعلم جافا","تعلم قواعد البيانات","تعلم Git/GitHub","مقدمة أمن سيبراني",
 "تصميم واجهات مواقع","التسويق الرقمي","مهارات التواصل","التحدث أمام جمهور","إدارة مشروع صغير",
 "خريطة تعلم AI","خريطة تعلم ML","تصميم لوجو بسيط","أفكار قنوات يوتيوب","أفكار تيك توك",
 "افتح متجر تيشيرت","أفكار تطبيقات","قائمة قراءة شهرية","10 نصائح مذاكرة","خطة نزول وزن",
 "خطة زيادة وزن","نوم صحي","كيف أبدأ الصلاة","تنظيم السفر","أفكار هدايا بسيطة",
 "رسالة تحفيزية","كلمات إنجليزية مهمة","مصطلحات برمجة","أوامر شات مفيدة","حل مسألة رياضيات",
 "عدّاد رسائل","القائمات المفضلة","أختار العشوائي","مؤقت تركيز 25","مؤقت راحة 5",
 "كلمات مرور قوية","اقتراح اسم إنستغرام","اقتراح username","فكرة بورصة وقت","فكرة ماركيت بليس"
]
random.seed(777)

# 5) reply logic: rules & commands
def reply_logic(q):
    q = q.strip()
    # a) commands
    if q.startswith("/help"):
        return "أوامي الرئيسية:\n" \
               "1) /calc 2+3*5 — آلة حاسبة.\n" \
               "2) /todo add نص… /todo list /todo done# /todo del#\n" \
               "3) /timer 15 — يبدأ عدّ تنازلي.\n" \
               "4) /dark /light /clear /star# /unst#\n" \
               "5) /suggest filter:كلمة — يفلتر الاقتراحات.\n" \
               "6) /export — ملف نصي للمحادثة.\n" \
               "7) /random — اقتراح عشوائي.\n" \
               "8) /quote /joke /plan\n" \
               "9) /password 12  — يولّد كلمة مرور.\n" \
               "10) /name hint:dev — اقتراح username."
    if q.startswith("/calc"):
        expr = q.replace("/calc","",1).strip()
        if not expr: return "أكتب: /calc 2+3*5"
        try:  res = calc_expr(expr); return f"🧮 الناتج: {res}"
        except: return "تعبير غير صالح."
    if q.startswith("/clear"):
        SS["messages"] = []; return "تم مسح الدردشة."
    if q.startswith("/dark"):
        SS["dark"]=True;  return "تم تفعيل الوضع الداكن."
    if q.startswith("/light"):
        SS["dark"]=False; return "تم تفعيل الوضع الفاتح."
    if q.startswith("/export"):
        return "اضغط زر ‘تحميل المحادثة’ أسفل الصفحة."
    if q.startswith("/random"):
        s = random.choice(suggestions); add_user(s); SS["typing"]=True; st.experimental_rerun()

    if q.startswith("/suggest"):
        m = re.search(r"filter\:(.+)", q)
        if m:
            SS["sfilter"] = m.group(1).strip()
            return f"✅ ضبط فلتر الاقتراحات: {SS['sfilter']}"
        return "اكتب: /suggest filter:حفظ"
    if q.startswith("/todo"):
        parts = q.split(" ",2)
        if len(parts)==1: return "أوامر todo: add/list/done#/del#"
        sub = parts[1]
        if sub=="add":
            text = parts[2] if len(parts)>2 else ""
            if text.strip()=="": return "اكتب نص المهمة بعد add."
            SS["todo"].append(text.strip()); return f"➕ أُضيفت مهمة: {text}"
        if sub=="list":
            if not SS["todo"] and not SS["todo_done"]: return "لا مهام حالياً."
            out = ["📋 المهام الجارية:"]
            for i,t in enumerate(SS["todo"],1): out.append(f"{i}. {t}")
            out.append("\n✅ المنتهية:")
            for i,t in enumerate(SS["todo_done"],1): out.append(f"{i}. {t}")
            return "\n".join(out)
        if sub.startswith("done"):
            m = re.search(r"done(\d+)", sub)
            if not m: return "اكتب: /todo done3"
            i = int(m.group(1))-1
            if 0<=i<len(SS["todo"]):
                t = SS["todo"].pop(i); SS["todo_done"].append(t)
                return f"✅ تم إنهاء: {t}"
            return "رقم غير صحيح."
        if sub.startswith("del"):
            m = re.search(r"del(\d+)", sub)
            if not m: return "اكتب: /todo del2"
            i = int(m.group(1))-1
            if 0<=i<len(SS["todo"]):
                t = SS["todo"].pop(i)
                return f"🗑️ حُذفت: {t}"
            return "رقم غير صحيح."
        return "صيغة todo غير صحيحة."
    if q.startswith("/star"):
        m = re.search(r"(\d+)", q)
        if m:
            idx = int(m.group(1))
            if 0<=idx<len(SS["messages"]):
                SS["stars"].add(idx); return "⭐ تم تعليم الرسالة."
        return "اكتب: /star 5"
    if q.startswith("/unst"):
        m = re.search(r"(\d+)", q)
        if m:
            idx = int(m.group(1))
            if idx in SS["stars"]: SS["stars"].remove(idx); return "⭐ أزيلت."
        return "اكتب: /unst 5"
    if q.startswith("/timer"):
        m = re.search(r"(\d+)", q)
        if not m: return "اكتب: /timer 15"
        sec = int(m.group(1))
        SS["timer_end"] = now_ts() + sec
        return f"⏳ بدأ مؤقت: {sec} ثانية."
    if q.startswith("/quote"):
        QU = ["ابقَ لطيفًا والقلب يزدهر.","خطوة صغيرة كل يوم تصنع فارقًا كبيرًا.","تعلّم اليوم، تحصد غدًا."]
        return "✨ " + random.choice(QU)
    if q.startswith("/joke"):
        JK = ["قال لصاحبه: عندي ذاكرة ضعيفة… قاله متى؟ 😂","مراتي قالت لي نظف المطبخ، قلتلها streamlit يعمل كل شيء 😂"]
        return random.choice(JK)
    if q.startswith("/plan"):
        return "🗓️ خطة سريعة: يوميًا 45 دقيقة دراسة + 15 مراجعة.\nنهاية الأسبوع: تلخيص وتقييم."
    if q.startswith("/password"):
        m = re.search(r"(\d+)", q); L = 12 if not m else max(6,min(40,int(m.group(1))))
        chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789#$!?"
        return "🔒 " + "".join(random.choice(chars) for _ in range(L))
    if q.startswith("/name"):
        m = re.search(r"hint:(.+)", q)
        hint = m.group(1).strip() if m else "dev"
        base = ["nova","spark","pulse","orbit","flow","dash","snap","rise"]
        return "🔖 اقتراحات:\n" + "\n".join([f"{hint}_{b}_{random.randint(10,99)}" for b in base])

    # b) keyword rules (offline)
    text = q.lower()
    if "انجليز" in text or "انجليزية" in text:
        return "تعلم الإنجليزية:\n1. استماع يوميًا 15د.\n2. Du〇ling〇 — قراءة/ترجمة.\n3. مفردات 10 يوميًا.\n4. تحدث مع نفسك 5د."
    if "دراسة" in text or "مذاكرة" in text:
        return "خطة دراسة:\n- Pomodoro 25/5 ×4.\n- آخر اليوم: تلخيص.\n- نهاية الأسبوع: نموذج امتحان قصير."
    if "python" in text or "بايثون" in text:
        return "خريطة بايثون:\n1. syntax\n2. listas/dicts\n3. functions\n4. files\n5. streamlit مشروع صغير."
    if "وقت" in text or "تركيز" in text:
        return "نصائح تركيز: وضع هاتف بعيد، مؤقت 25د، أذُن سماعة، شرب ماء، مهمة واحدة."
    if "git" in text:
        return "خطوات Git:\ninit → add → commit → push\nوفرع feature/test."
    # fallback
    return "✅ استلمت: " + q + "\n(رد تجريبي — يمكنك التوسع حسب حاجة السؤال)"

# 6) header
st.markdown(f"<div class='chat_wrap'>", True)
st.markdown("<div class='header-title'>💬 البوت الشاب — دردشة ستايل واتساب</div>", True)
st.markdown("<div class='header-sub'>اكتب سؤلاً أو اختر من الاقتراحات ⬇️</div>", True)

# 7) render chat
render_chat()
if SS["typing"]:
    st.markdown("<div class='typing'>البوت يكتب…</div>", True)

# 8) form input
with st.form("send_form", clear_on_submit=True):
    user_text = st.text_input("✍️ اكتب رسالتك هنا...", "", help="اختر اقتراحًا أو اكتب أمر /help")
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    send  = c1.form_submit_button("إرسال ✈️")
    clear = c2.form_submit_button("مسح 🗑️")
    exbtn = c3.form_submit_button("تحميل المحادثة ⬇️")
    star  = c4.form_submit_button("⭐ تعليم آخر رسالة")

if clear:
    SS["messages"] = []; st.experimental_rerun()
if exbtn:
    data = "\n".join([f"[{fmt_time(m['ts'])}] {( 'أنا' if m['role']=='user' else 'البوت' )}: {m['content']}" for m in SS["messages"]])
    st.download_button("تحميل الآن - txt", data=data.encode("utf-8"), file_name=f"chat_{int(time.time())}.txt", mime="text/plain")

if star:
    idx = len(SS["messages"]) - 1
    if idx >= 0: SS["stars"].add(idx); st.experimental_rerun()

if send and user_text.strip():
    add_user(user_text)
    SS["typing"] = True
    st.experimental_rerun()

# 9) process typing
if SS["typing"]:
    time.sleep(0.25)
    # last user
    last = None
    for m in reversed(SS["messages"]):
        if m["role"]=="user": last = m["content"]; break
    add_bot( reply_logic(last or "") )
    SS["typing"] = False
    st.experimental_rerun()

# 10) suggestions panel — filter & grid
st.markdown("<div class='sugg-title'>✨ اقتراحات مرتبة (60+)</div>", True)
sf = st.text_input("🔍 ابحث في الاقتراحات…", SS["sfilter"])
SS["sfilter"] = sf
filtered = [s for s in suggestions if sf.strip()=="" or sf.lower() in s.lower()]
cols = st.columns(6)
for i, s in enumerate(filtered):
    with cols[i % 6]:
        b = st.button(s, key=f"sugg_{i}", use_container_width=True)
        if b:
            add_user(s); SS["typing"]=True; st.experimental_rerun()

# 11) sidebar — settings / todo / timer / palette
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    colt = st.columns(2)
    with colt[0]:
        dark = st.checkbox("🌙 داكن", SS["dark"]); SS["dark"]=dark
        fs   = st.slider("حجم الكتابة", 12, 28, SS["font_scale"]); SS["font_scale"]=fs
    with colt[1]:
        theme = st.selectbox("🎨 خلفية", ["fresh","sunset","forest","ocean","night"], index=["fresh","sunset","forest","ocean","night"].index(SS["theme"]))
        SS["theme"]=theme
        st.markdown("**لوحات سريعة**")
        for i, c in enumerate(SS["palette"]):
            st.button("", key=f"pal_{i}", use_container_width=True)
    st.markdown("---")
    st.markdown("### 📋 Todo")
    ta = st.text_input("مهمة جديدة…", "")
    c1,c2 = st.columns(2)
    if c1.button("➕ إضافة", use_container_width=True):
        if ta.strip()!="": SS["todo"].append(ta.strip()); st.experimental_rerun()
    if c2.button("🗑️ مسح جميع المهام", use_container_width=True):
        SS["todo"].clear(); SS["todo_done"].clear(); st.experimental_rerun()
    for i,t in enumerate(SS["todo"]):
        c = st.columns([8,1,1])
        c[0].markdown(f"- {t}")
        if c[1].button("✅", key=f"td_{i}"): 
            SS["todo_done"].append(SS["todo"].pop(i)); st.experimental_rerun()
        if c[2].button("❌", key="del_"+str(i)):
            SS["todo"].pop(i); st.experimental_rerun()
    if SS["todo_done"]:
        st.markdown("**منتهية:**")
        for t in SS["todo_done"]: st.markdown(f"✅ {t}")
    st.markdown("---")
    st.markdown("### ⏳ مؤقت")
    sec = st.number_input("ثواني:", 5, 3600, 25)
    c1,c2 = st.columns(2)
    if c1.button("بدء المؤقت", use_container_width=True):
        SS["timer_end"] = now_ts() + int(sec); st.experimental_rerun()
    if c2.button("مسح المؤقت", use_container_width=True):
        SS["timer_end"] = 0; st.experimental_rerun()
    if SS["timer_end"]>0:
        left = int(SS["timer_end"] - now_ts())
        left = max(0,left)
        st.markdown(f"**باقي:** {left} sec")
        if left==0: st.success("⏰ انتهى المؤقت!")
    st.markdown("---")
    st.markdown(f"📊 عدد الرسائل: **{SS['counter']}**")
    if st.button("⭐ اظهار الرسائل المفضلة"):
        out = []
        for i in sorted(SS["stars"]):
            m = SS["messages"][i]
            who = "أنا" if m["role"]=="user" else "البوت"
            out.append(f"{i}. [{fmt_time(m['ts'])}] {who}: {m['content']}")
        st.text("\n".to_list())

# 12) reminders quick — rule based
st.marky=1
st.markdown("<hr style='opacity:.2'/>", True)
st.markdown("<div class='sugg-title'>🚨 تذكيرات سريعة</div>", True)
rc1, rc2, rc3 = st.columns([3,2,1])
rem_text = rc1.text_input("اكتب تذكيرًا… (مثل: ذاكر 20د)")
rem_sec  = rc2.number_input("بعد (ثواني):", 10, 7200, 60)
if rc3.button("🔔 اضبط", use_container_width=True):
    SS["reminders"].append((now_ts()+rem_sec, rem_text))
    st.success("تم إضافة تذكير.")
# check reminders
due = [r for r in SS["reminders"] if r[0]<=now_ts()]
if due:
    for d in due: st.warning(f"🔔 تذكير: {d[1]}")
    SS["reminders"] = [r for r in SS["reminders"] if r[0]>now_ts()]

# 13) export button outside form
st.markdown("<hr style='opacity:.15'/>", True)
data = "\n".join([f"[{fmt_time(m['ts'])}] {( 'أنا' if m['role']=='user' )}"],)

st.markdown("</div>", True)
```0
