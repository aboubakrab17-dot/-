# app.py
# لعبة أسئلة وألغاز (واجهة عربية)
# متطلبات: streamlit
# لتشغيل محلياً: streamlit run app.py
#
# هذا الملف مصمم ليعمل لوحده إذا لم يوجد questions.json في المستودع:
# - يحاول تحميل questions.json من نفس المجلد.
# - إن لم يجده يستخدم قائمة أسئلة داخلية (افتراضية).
#
# مميزات الكود:
# - واجهة عربية كاملة.
# - خلفية متدرجة (CSS).
# - تتبع حالة اللعبة عبر st.session_state (بدون أخطاء إعادة التشغيل).
# - اختيار أسئلة عشوائية من دون تكرار أثناء الجلسة.
# - مؤقت لكل سؤال (قابل للتعديل).
# - أصوات اختيارية عبر روابط (يمكن تغييرها).
# - مؤثر احتفالي (st.balloons) عند الإجابة الصحيحة.
# - تحقّق من ملف الأسئلة وتجاهل الأسئلة غير المطابقة للبنية.
#
# ملاحظة: لتحسين الأصوات أو إضافة ملفات محلية، ضعها في المسار الصحيح أو استخدم روابط مباشرة إلى ملفات mp3.
#        الملف questions.json يجب أن يحتوي على بنية JSON مثل:
# [
#  {"id": 1, "question": "...", "choices": ["a","b","c","d"], "answer": "b", "hint": "تلميح ...", "lang":"ar"},
#  ...
# ]
#
# ------------------------------------------------------------

import streamlit as st
import random
import json
import time
from pathlib import Path

# -------------------------- إعداد الستايل العام --------------------------
st.set_page_config(page_title="لعبة الألغاز", layout="centered", initial_sidebar_state="collapsed")

# CSS للتصميم (خلفية متدرجة، أزرار مخصصة، خطوط أكبر)
page_css = """
<style>
:root{
  --bg1: #0f1724;
  --bg2: #211f31;
  --accent: linear-gradient(90deg,#ff7a18,#af002d,#319197);
}

/* خلفية الصفحة */
.main > div.block-container{
  padding-top: 20px;
  padding-bottom: 50px;
}

/* صندوق أسئلة */
.question-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.4);
  color: #fff;
  margin-bottom: 12px;
}

/* زر كبير */
.big-btn > button {
  background: linear-gradient(90deg,#ffd166,#ef476f);
  color: #021528;
  font-weight: 700;
  padding: 12px 18px;
  border-radius: 12px;
}

/* زر ثانوي */
.secondary-btn > button {
  background: rgba(255,255,255,0.04);
  color: #fff;
  border-radius: 10px;
}

/* شريط التقدّم */
.progress {
  height: 10px;
  border-radius: 999px;
}

/* نص عربي كبير */
.h1 {
  font-size: 34px;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 6px;
}

/* بطاقات الخيارات */
.choice {
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  padding: 14px;
  margin: 8px 0;
  color: #fff;
}

/* شريط معلومات */
.info-box {
  background: rgba(255,255,255,0.03);
  padding: 8px 12px;
  border-radius: 10px;
  color: #fff;
}

/* اضيف مساحة للزر الاساسي */
.play-btn {
  display: inline-block;
  width: 100%;
}

/* تصغير الخط */
.small {
  font-size: 13px;
  color: #d6d6d6;
}
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

# -------------------------- إعداد الأصوات (روابط قابلة للتعديل) --------------------------
# يمكنك تغيير هذه الروابط إلى ملفات صوتية خاصة بك أو روابط خارجية
SOUND_CORRECT = "https://actions.google.com/sounds/v1/human_voices/applause.ogg"
SOUND_WRONG = "https://actions.google.com/sounds/v1/cartoon/cartoon_boing.ogg"
SOUND_TICK = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"

# -------------------------- تحميل البيانات (questions.json) --------------------------
def load_questions_from_file(path="questions.json"):
    p = Path(path)
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate basic structure
        valid = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if "question" in item and "choices" in item and "answer" in item:
                # ensure choices is list and answer in choices
                if isinstance(item["choices"], list) and item["answer"] in item["choices"]:
                    # default fields
                    item.setdefault("hint", "")
                    item.setdefault("lang", "ar")
                    item.setdefault("id", random.randint(100000,999999))
                    valid.append(item)
        return valid
    except Exception as e:
        st.error("خطأ أثناء تحميل ملف الأسئلة: " + str(e))
        return None

# -------------------------- قائمة أسئلة افتراضية (عربية) --------------------------
DEFAULT_QUESTIONS_AR = [
    {"id":1, "question":"ما هو أصغر كوكب في نظامنا الشمسي؟",
     "choices":["عطارد","الزهرة","الارض","المريخ"], "answer":"عطارد", "hint":"أول كوكب من الشمس", "lang":"ar"},
    {"id":2, "question":"ما هي وحدة قياس التيار الكهربائي؟",
     "choices":["أوم","فولت","واط","أمبير"], "answer":"أمبير", "hint":"نستخدمه لقياس مرور الشحنة", "lang":"ar"},
    {"id":3, "question":"أي لغة برمجة تُستخدم بكثرة في تطوير الويب من جهة الخادم؟",
     "choices":["HTML","CSS","Python","Photoshop"], "answer":"Python", "hint":"تُستخدم كخلفية مع أطر مثل Django و Flask", "lang":"ar"},
    {"id":4, "question":"من هو مؤلف رواية 'البؤساء'؟",
     "choices":["فيكتور هوغو","مارك توين","تولستوي","نابليون"], "answer":"فيكتور هوغو", "hint":"كاتب فرنسي مشهور", "lang":"ar"},
    {"id":5, "question":"ما العنصر الكيميائي الذي يرمز له بالرمز Fe؟",
     "choices":["الذهب","الحديد","النحاس","الفضة"], "answer":"الحديد", "hint":"معدن مغناطيسي شائع", "lang":"ar"},
    {"id":6, "question":"ما هي عاصمة اليابان؟",
     "choices":["أوساكا","طوكيو","ناغويا","هيروشيما"], "answer":"طوكيو", "hint":"مدينة كبرى تقع في جزيرة هوكايدو", "lang":"ar"},
    {"id":7, "question":"أي من هذه الأطعمة يعتبر مصدرًا جيدًا للأوميغا-3؟",
     "choices":["السردين","السكر","الخيار","الخبز"], "answer":"السردين", "hint":"سمك غني بالزيوت الصحية", "lang":"ar"},
    {"id":8, "question":"ما كلمة المرور الأكثر أهمية لحماية الحساب (إجابتك)؟",
     "choices":["كلمة سر قصيرة","كلمة سر طويلة ومعقدة","1234","password"], "answer":"كلمة سر طويلة ومعقدة", "hint":"طويلة ومع أحرف وأرقام ورموز", "lang":"ar"},
    {"id":9, "question":"ما اسم أقرب نجم إلى الأرض بعد الشمس؟",
     "choices":["بروكسيما قنطورس","سيريوس","قنطورا","ألفا قنطورس"], "answer":"بروكسيما قنطورس", "hint":"جزء من نظام النجوم القريب", "lang":"ar"},
    {"id":10, "question":"ما هو العضو الرئيسي في الجهاز الدوري؟",
     "choices":["الرئتان","الكبد","القلب","المعدة"], "answer":"القلب", "hint":"ينبض ويضخ الدم في الجسم", "lang":"ar"},
    {"id":11, "question":"ما اسم العملة الرسمية لليابان؟",
     "choices":["الين","الدولار","اليوان","الروبل"], "answer":"الين", "hint":"رمزها ¥", "lang":"ar"},
    {"id":12, "question":"ما الحيوان الذي يعتبر أسرع حيوان بري؟",
     "choices":["الفهد","الأسد","الزرافة","الكلب"], "answer":"الفهد", "hint":"قادر على سرعات هائلة عند المطاردة", "lang":"ar"},
    {"id":13, "question":"ما هي عاصمة مصر؟",
     "choices":["القاهرة","الإسكندرية","أسوان","الأقصر"], "answer":"القاهرة", "hint":"أكبر مدينة في مصر", "lang":"ar"},
    {"id":14, "question":"ما اسم أكبر محيط على الأرض؟",
     "choices":["المحيط الهندي","المحيط المتجمد الشمالي","المحيط الهادئ","المحيط الأطلسي"], "answer":"المحيط الهادئ", "hint":"يغطي ثلث سطح الكرة الأرضية", "lang":"ar"},
    {"id":15, "question":"في الحاسوب، ماذا تعني CPU؟",
     "choices":["وحدة تخزين","وحدة المعالجة المركزية","بطاقة الشاشة","الرام"], "answer":"وحدة المعالجة المركزية", "hint":"الدماغ الذي ينفذ التعليمات", "lang":"ar"},
    {"id":16, "question":"ما الشجرة التي تنتج ثمار الزيتون؟",
     "choices":["شجرة التين","شجرة الزيتون","شجرة الرمان","شجرة البرتقال"], "answer":"شجرة الزيتون", "hint":"رمز السلام في كثير من الثقافات", "lang":"ar"},
    {"id":17, "question":"ما اسم الغاز الذي نتنفسه ونحتاجه للبقاء؟",
     "choices":["النيتروجين","الأكسجين","ثاني أكسيد الكربون","الهيدروجين"], "answer":"الأكسجين", "hint":"رمزه O2", "lang":"ar"},
    {"id":18, "question":"ما لغة التواصل بين صفحات الويب (هيكلية المحتوى)؟",
     "choices":["Python","HTML","C++","SQL"], "answer":"HTML", "hint":"تحدد عناصر الصفحة (عناوين، فقرات، صور)", "lang":"ar"},
    {"id":19, "question":"من اكتشف قانون الجاذبية العامة؟",
     "choices":["نيوتن","أينشتاين","جاليليو","طومسون"], "answer":"نيوتن", "hint":"تفاح وسقوطه قصة مشهورة", "lang":"ar"},
    {"id":20, "question":"ما اسم أكبر قارة من حيث المساحة؟",
     "choices":["أفريقيا","آسيا","أمريكا الجنوبية","أستراليا"], "answer":"آسيا", "hint":"تضم الصين والهند وروسيا", "lang":"ar"},
    {"id":21, "question":"ما العضو الذي ينقي السموم في الجسم؟",
     "choices":["القلب","الكبد","الرئتين","الطحال"], "answer":"الكبد", "hint":"يخزن الطاقة ويعالج السموم", "lang":"ar"},
    {"id":22, "question":"أي من هذه البروتوكولات يُستخدم لتصفح الويب بشكل آمن؟",
     "choices":["HTTP","FTP","HTTPS","SMTP"], "answer":"HTTPS", "hint":"يحتوي على تشفير TLS/SSL", "lang":"ar"},
    {"id":23, "question":"من هو مؤسس شركة مايكروسوفت؟",
     "choices":["ستيف جوبز","بيل غيتس","مارك زوكربيرغ","لاري بايج"], "answer":"بيل غيتس", "hint":"شريك بول ألين", "lang":"ar"},
    {"id":24, "question":"ما اسم العملية التي تحول الطعام إلى طاقة في الخلايا؟",
     "choices":["التركيب الضوئي","التنفس الخلوي","الهضم","التخمير"], "answer":"التنفس الخلوي", "hint":"تتم في الميتوكوندريا", "lang":"ar"},
    {"id":25, "question":"ما هي اللغة الرسمية للدولة السويسرية؟",
     "choices":["العربية","الهولندية","الإنجليزية","السويسرية ليست لغة واحدة — لديها عدة لغات رسمية"], "answer":"السويسرية ليست لغة واحدة — لديها عدة لغات رسمية", "hint":"تتضمن الألمانية والفرنسية والإيطالية", "lang":"ar"},
    {"id":26, "question":"ما اسم أول امرأة فازت بجائزة نوبل؟",
     "choices":["ماري كوري","روزاليند فرانكلين","جين غودال","ماري لمبرت"], "answer":"ماري كوري", "hint":"حصلت عليها في الفيزياء ثم الكيمياء", "lang":"ar"},
    {"id":27, "question":"من كتب 'مائة عام من العزلة'؟",
     "choices":["غابرييل غارسيا ماركيز","باولو كويلو","نجيب محفوظ","إرنست همنغواي"], "answer":"غابرييل غارسيا ماركيز", "hint":"كاتب كولومبي وأحد رواد الواقعية السحرية", "lang":"ar"},
    {"id":28, "question":"في الرياضيات، ما ناتج 12 × 8؟",
     "choices":["96","88","108","100"], "answer":"96", "hint":"12 times 8", "lang":"ar"},
    {"id":29, "question":"ما اسم المركبة التي هبطت على سطح القمر لأول مرة تحمل رواد الفضاء؟",
     "choices":["أبوللو 11","أبوللو 13","فوياجر","مارينر"], "answer":"أبوللو 11", "hint":"هبط نيل أرمسترونغ وباز ألدرين", "lang":"ar"},
    {"id":30, "question":"ما هو أكبر حيوان بري؟",
     "choices":["الفيل الأفريقي","الحوت الأزرق","الركس","الجاموس"], "answer":"الفيل الأفريقي", "hint":"ثدي ضخم بأنياب كبيرة", "lang":"ar"},
    {"id":31, "question":"ما اسم أسرع طائر أثناء الطيران؟",
     "choices":["النسور","الصقر الشاهين","الحمامة","البطريق"], "answer":"الصقر الشاهين", "hint":"غالبًا في هجوم الغوص بسرعة عالية", "lang":"ar"},
    {"id":32, "question":"ما هي وحدة قياس التردد؟",
     "choices":["واط","هرتز","أوم","فولت"], "answer":"هرتز", "hint":"دورة في الثانية", "lang":"ar"},
    {"id":33, "question":"ما اسم البحر الذي يفصل بين السعودية ومصر؟",
     "choices":["البحر الأبيض المتوسط","البحر الأحمر","الخليج العربي","بحر قزوين"], "answer":"البحر الأحمر", "hint":"يمتد من خليج العقبة حتى باب المندب", "lang":"ar"},
    {"id":34, "question":"أي من هذه الأدوات تُستخدم لقياس درجة الحرارة؟",
     "choices":["ميزان الحرارة","البارومتر","الساعة","العداد"], "answer":"ميزان الحرارة", "hint":"يقاس بالدرجة مئوية أو فهرنهايت", "lang":"ar"},
    {"id":35, "question":"ما اسم العملة الرسمية في المملكة المتحدة؟",
     "choices":["اليورو","الجنيه الاسترليني","الدولار","الكرونة"], "answer":"الجنيه الاسترليني", "hint":"رمزه GBP", "lang":"ar"},
    {"id":36, "question":"من هو العالم المعروف بنظرية النسبية؟",
     "choices":["أينشتاين","نيوتن","جاليليو","ماكسويل"], "answer":"أينشتاين", "hint":"معادلة شهيرة E=mc^2", "lang":"ar"},
    {"id":37, "question":"ما اسم السائل الذي يدور داخل المحرك لتبريد المحرك؟",
     "choices":["الجازولين","زيت المحرك","ماء التبريد (مبرد)","الهواء"], "answer":"ماء التبريد (مبرد)", "hint":"يخلط أحيانًا بمضافات مضادة للتجمد", "lang":"ar"},
    {"id":38, "question":"أي من هذه الدول تقع في قارة أمريكا الجنوبية؟",
     "choices":["المغرب","الأرجنتين","مصر","النرويج"], "answer":"الأرجنتين", "hint":"بوينس آيرس عاصمة كبيرة", "lang":"ar"},
    {"id":39, "question":"ما اسم العملية التي تحول الضوء إلى طاقة في النبات؟",
     "choices":["التنفس الخلوي","التخمر","التركيب الضوئي","التحلل"], "answer":"التركيب الضوئي", "hint":"يحدث في أوراق النبات", "lang":"ar"},
    {"id":40, "question":"في البرمجة، ماذا يعني bug؟",
     "choices":["حشرة حقيقية","خطأ في البرنامج","نوع من الخوارزميات","لغة برمجة"], "answer":"خطأ في البرنامج", "hint":"يسبب سلوك غير متوقع", "lang":"ar"},
    {"id":41, "question":"ما اسم السلسلة التي تضم مصطلح 'النسبة الذهبية' غالبًا؟",
     "choices":["سلسلة فيبوناتشي","الأعداد الأولية","اللوغاريتمات","الأعداد المركبة"], "answer":"سلسلة فيبوناتشي", "hint":"كل رقم مجموع الاثنين السابقين", "lang":"ar"},
    {"id":42, "question":"ما اسم العامل المسبب لتلوث الهواء من السيارات؟",
     "choices":["الأكسجين","ثاني أكسيد الكربون","الهيدروجين","الهيليوم"], "answer":"ثاني أكسيد الكربون", "hint":"غاز ناتج عن احتراق الوقود", "lang":"ar"},
    {"id":43, "question":"في التاريخ، من هو الفاتح الإسلامي المعروف بفتح مصر؟",
     "choices":["عمر بن الخطاب","عمرو بن العاص","خالد بن الوليد","صلاح الدين"], "answer":"عمرو بن العاص", "hint":"قائد فتح مصر في القرن السابع", "lang":"ar"},
    {"id":44, "question":"ما اسم الجهاز المستخدم لقياس ضغط الدم؟",
     "choices":["ميزان الحرارة","مقياس الضغط (سفينومومانومتر)","مقياس الرطوبة","مقياس الصوت"], "answer":"مقياس الضغط (سفينومومانومتر)", "hint":"يوضع حول الذراع", "lang":"ar"},
    {"id":45, "question":"ما اسم أكبر قارة سكنياً؟",
     "choices":["أفريقيا","آسيا","أوروبا","أميركا الشمالية"], "answer":"آسيا", "hint":"تمتلك أكبر عدد سكان", "lang":"ar"},
    {"id":46, "question":"ما اسم المادة التي تعطي النبات لونه الأخضر؟",
     "choices":["الكلوروفيل","الليبيد","السكروز","الريبوز"], "answer":"الكلوروفيل", "hint":"يمتص الضوء في التركيب الضوئي", "lang":"ar"},
    {"id":47, "question":"ما اسم البروتين الذي يجعل الدم يتجلط؟",
     "choices":["الهيموغلوبين","الفيبرين","الإنزيم","الزلال"], "answer":"الفيبرين", "hint":"مسؤول عن تكوين شبكة تخثر", "lang":"ar"},
    {"id":48, "question":"ما اسم أول مكتشف للقارة الأمريكية (من الأوروبيين) الذي وصل عام 1492؟",
     "choices":["كريستوفر كولومبوس","فاسكو دا غاما","ماغللان","ماركو بولو"], "answer":"كريستوفر كولومبوس", "hint":"كان تحت راية إسبانيا", "lang":"ar"},
    {"id":49, "question":"ما اسم أكبر بحيرة في العالم من حيث المساحة؟",
     "choices":["بحيرة سوبيريور","بحر قزوين","بحيرة فيكتوريا","بحيرة بايكال"], "answer":"بحر قزوين", "hint":"يعتبر بحيرة من حيث المساحة لكنه مالح", "lang":"ar"},
    {"id":50, "question":"ما اسم أقصى سرعة يسجلها الصوت في الهواء تقريباً عند الظروف القياسية؟",
     "choices":["343 م/ث","150 م/ث","1000 م/ث","50 م/ث"], "answer":"343 م/ث", "hint":"تقريباً 343 متر/ث في الهواء عند 20°C", "lang":"ar"},
]

# -------------------------- تحميل البيانات (تحقق وجود ملف) --------------------------
DATA = load_questions_from_file()
if DATA is None:
    # استخدم القائمة الافتراضية
    DATA = DEFAULT_QUESTIONS_AR.copy()

# فقط الأسئلة العربية (lang=='ar') لضمان تطابق اختيار المستخدم (بما أن طلبت العربية فقط)
DATA = [q for q in DATA if q.get("lang", "ar") == "ar"]

# -------------------------- وظائف مساعدة --------------------------
def init_session():
    # تهيئة متغيرات الجلسة إذا لم تكن موجودة
    st.session_state.setdefault("started", False)
    st.session_state.setdefault("player_name", "")
    st.session_state.setdefault("language", "ar")
    st.session_state.setdefault("num_questions", 10)
    st.session_state.setdefault("question_time", 25)  # بالثواني
    st.session_state.setdefault("used_ids", set())
    st.session_state.setdefault("current_q", None)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("streak", 0)
    st.session_state.setdefault("question_index", 0)
    st.session_state.setdefault("shuffled_pool", [])
    st.session_state.setdefault("question_start_time", None)
    st.session_state.setdefault("last_feedback", "")
    st.session_state.setdefault("sound_on", True)
    st.session_state.setdefault("hints_used", 0)

def safe_choice_shuffle(pool, n):
    # إعادة ترتيب مختصرة - إرجاع n عناصر عشوائية بدون تكرار
    pool_copy = pool.copy()
    random.shuffle(pool_copy)
    return pool_copy[:n]

def prepare_game():
    # تحضير قائمة الأسئلة للعبة وفق إعدادات المستخدم
    pool = DATA.copy()
    # لو عدد الأسئلة أكبر من الموجود، خذ الموجود كله
    qcount = min(st.session_state.num_questions, len(pool))
    selected = safe_choice_shuffle(pool, qcount)
    st.session_state.shuffled_pool = selected
    st.session_state.used_ids = set()
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.hints_used = 0
    st.session_state.last_feedback = ""
    st.session_state.current_q = None
    st.session_state.question_start_time = None
    st.session_state.started = True

def get_next_question():
    idx = st.session_state.question_index
    if idx >= len(st.session_state.shuffled_pool):
        return None
    q = st.session_state.shuffled_pool[idx]
    st.session_state.current_q = q
    st.session_state.used_ids.add(q["id"])
    st.session_state.question_start_time = time.time()
    return q

def check_answer(q, chosen):
    if q is None:
        return False
    correct = (chosen == q["answer"])
    return correct

# -------------------------- واجهة المستخدم --------------------------
init_session()

# العنوان الرئيسي
st.markdown('<div class="h1">أفضل لعبة ألغاز بالعربية</div>', unsafe_allow_html=True)
st.markdown('<div class="small">اختبر معلوماتك واستمتع بتحدّي سريع — تصميم خفيف وموبايل-فرندلي</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# لوحة الإعدادات (المستخدم يملأ)
with st.container():
    col1, col2 = st.columns([2,1])
    with col1:
        name = st.text_input("✨ اكتب اسمك للبدء", value=st.session_state.player_name)
        st.session_state.player_name = name.strip()
    with col2:
        # التحكم بالصوت
        sound_toggle = st.checkbox("🔊 الصوت", value=st.session_state.sound_on)
        st.session_state.sound_on = sound_toggle

    st.markdown("<br>", unsafe_allow_html=True)

    # عدد الأسئلة
    num_q = st.slider("🧩 عدد الأسئلة", min_value=5, max_value=min(50,len(DATA)), value=st.session_state.num_questions)
    st.session_state.num_questions = num_q

    # وقت كل سؤال
    qtime = st.slider("⏱️ مدة كل سؤال (ثانية)", min_value=5, max_value=120, value=st.session_state.question_time)
    st.session_state.question_time = qtime

    # زر بدء / إعادة
    if not st.session_state.started:
        if st.button("▶️ ابدأ اللعبة", key="start_game"):
            if len(DATA) == 0:
                st.error("لا توجد أسئلة متاحة الآن. تأكد من ملف questions.json أو جرب لاحقاً.")
            else:
                if not st.session_state.player_name:
                    st.warning("ادخل اسمك أولاً لعرض التقدم والنتائج.")
                prepare_game()
                st.experimental_rerun()
    else:
        if st.button("🔁 إعادة تشغيل اللعبة"):
            prepare_game()
            st.experimental_rerun()

# -------------------------- شاشة اللعبة --------------------------
if st.session_state.started:
    # احضر السؤال التالي إن لم يوجد واحد حالياً
    if st.session_state.current_q is None:
        q = get_next_question()
    else:
        q = st.session_state.current_q

    # إذا انتهت الأسئلة
    if q is None:
        st.success("🎉 انتهت اللعبة!")
        st.markdown(f"**اللاعب:** {st.session_state.player_name}  \n**النقاط:** {st.session_state.score}  \n**السلسلة الأطول:** {st.session_state.streak}")
        # إعادة البداية
        if st.button("🔄 العودة للقائمة الرئيسية"):
            st.session_state.started = False
            st.session_state.current_q = None
            st.experimental_rerun()
    else:
        # عرض شريط المعلومات (الوقت المتبقي، نقاط، تقدم)
        total = len(st.session_state.shuffled_pool)
        idx = st.session_state.question_index + 1
        with st.container():
            # معلومات
            st.markdown(f'<div class="info-box">السؤال {idx} من {total} • اللاعب: <b>{st.session_state.player_name or "لاعب"}</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="height:8px"></div>', unsafe_allow_html=True)
            # شريط التقدّم
            progress = int((idx-1)/total*100)
            st.progress(progress)

        # عرض السؤال نفسه داخل بطاقة
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"### ❓ {q['question']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # حساب الوقت المتبقي
        now = time.time()
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = now
        elapsed = now - st.session_state.question_start_time
        remaining = max(0, int(st.session_state.question_time - elapsed))

        # شريط الوقت وتلميح التحذير قرب النهاية
        tcol1, tcol2 = st.columns([3,1])
        with tcol1:
            st.progress(int((st.session_state.question_time - remaining) / st.session_state.question_time * 100))
        with tcol2:
            st.markdown(f"**⏱ {remaining} ث**")

        # عرض الاختيارات (موزعة عشوائياً في كل مرة يظهر فيها السؤال)
        choices = q["choices"].copy()
        random.shuffle(choices)

        # زر تلميح
        hint_col, confirm_col = st.columns([2,1])
        with hint_col:
            show_hint = st.button("💡 تلميح", key=f"hint_{q['id']}")
            if show_hint:
                st.session_state.hints_used += 1
                st.info(q.get("hint", "لا يوجد تلميح متاح."))
        with confirm_col:
            pass

        # اختيار المستخدم
        choice_key = f"choice_{q['id']}"
        # نستخدم radio حتى لا نحدث الجلسة كثيراً
        selected = st.radio("اختر إجابة:", options=choices, key=choice_key, index=0, format_func=lambda x: x)

        # وضع زر التأكيد
        confirmed = st.button("✅ تأكيد الإجابة")
        # زر تخطي
        skipped = st.button("⏭ تخطّى السؤال")

        # معالجة ضغط التخطي
        if skipped:
            st.session_state.last_feedback = "تخطيت السؤال."
            st.session_state.question_index += 1
            st.session_state.current_q = None
            st.session_state.question_start_time = None
            st.experimental_rerun()

        # معالجة التأكد من الإجابة
        if confirmed:
            correct = check_answer(q, selected)
            if correct:
                st.success("✅ إجابة صحيحة!")
                st.session_state.score += 10
                st.session_state.streak += 1
                st.session_state.last_feedback = "صحيح! لقد ربحت 10 نقاط."
                if st.session_state.sound_on:
                    st.audio(SOUND_CORRECT)
                # مؤثر احتفالي
                st.balloons()
            else:
                st.error(f"❌ خطأ! الإجابة الصحيحة: **{q['answer']}**")
                st.session_state.streak = 0
                st.session_state.last_feedback = "خطأ! حاول السؤال التالي."
                if st.session_state.sound_on:
                    st.audio(SOUND_WRONG)

            # بعد المعالجة ننتقل للسؤال التالي
            st.session_state.question_index += 1
            st.session_state.current_q = None
            st.session_state.question_start_time = None
            st.experimental_rerun()

        # تحقق إن انتهى الوقت دون اختيار / تأكيد
        # (نستخدم زر افتراضي يضغط تلقائياً عند انتهاء الوقت — لكن streamlit لا يسمح بتنفيذ خلفية بدون rerun)
        # هنا سنعرض رسالة تنبيه عند انتهاء الوقت وندع المستخدم يضغط "تخطي" أو "تأكيد" بنفسه
        if remaining == 0:
            st.warning("انتهى وقت الإجابة! يمكنك تخطّي السؤال أو الضغط تأكيد (يحسب كإجابة خاطئة إذا لم تكن صحيحة).")

        # عرض تغذية راجعة سريعة
        if st.session_state.last_feedback:
            st.markdown(f"**الحالة:** {st.session_state.last_feedback}")

        # عرض نقاط وسلسلة
        st.markdown("---")
        st.markdown(f"**النقاط:** {st.session_state.score}  \n**السلسلة الحالية:** {st.session_state.streak}")

# -------------------------- شريط جانبي (ملاحظات وإرشادات) --------------------------
with st.sidebar:
    st.title("قائمة اللعبة")
    st.markdown("إعدادات سريعة ونصائح:")
    st.markdown("- اكتب اسمك واضغط ابدأ.")
    st.markdown("- اختر عدد الأسئلة ووقت السؤال حسب رغبتك.")
    st.markdown("- يمكنك إيقاف/تشغيل الأصوات من الأعلى.")
    st.markdown("---")
    st.markdown("حالة التطبيق:")
    st.markdown(f"- إجمالي الأسئلة المتاحة: **{len(DATA)}**")
    st.markdown(f"- أسئلة اللعبة الحالية: **{st.session_state.num_questions}**")
    st.markdown("---")
    st.markdown("مساعدة تقنية:")
    st.markdown("إن ظهرت رسالة خطأ، تأكد من وجود ملف questions.json في المجلد الجذري للمستودع وأنه يحتوي على بنية JSON صحيحة.")
    st.markdown("يمكنك تعديل ملف questions.json أو إضافة أسئلة إضافية بنفس البنية.")
    st.markdown("---")
    st.markdown("مصدر الأصوات (قابل للتغيير):")
    st.markdown(f"- صحيح: {SOUND_CORRECT}")
    st.markdown(f"- خطأ: {SOUND_WRONG}")

# -------------------------- نهاية الملف --------------------------
