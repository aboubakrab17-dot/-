# app.py
# تطبيق أذكار إسلامية كامل — Streamlit
# متطلبات: streamlit
# تشغيل: pip install streamlit
#         streamlit run app.py

import streamlit as st
import json
from io import BytesIO
from datetime import datetime

# ---------------------------
# بيانات الأذكار (نص عربي، مصدر عام، وفائدة قصيرة)
# ملاحظة: المصادر ذكرت بصفة "القرآن" أو "السنة/حصن المسلم" بشكل عام.
# إن أردت مراجع دقيقة (اسم الكتاب/الراوي/رقم الحديث/سورة:آية) أضيفها لاحقاً.
# ---------------------------

ZIKR_DATA = {
    "فضل الأذكار": [
        {
            "title": "فضل الذكر وطمأنينة القلب",
            "text": "ألا بذكر الله تطمئن القلوب.",
            "source": "القرآن الكريم — السورة: الرعد (13:28)",
            "benefit": "طمأنينة القلب والسكينة بقرب الله."
        },
        {
            "title": "مثل الذاكر والغير ذاكِر",
            "text": "مثل الذي يذكر ربه والذي لا يذكر ربه مثل الحي والميت.",
            "source": "السنة النبوية (مأثور)",
            "benefit": "بيان فضل الذكر وأنه حياة القلب."
        },
        {
            "title": "الذكر عماد العبادة",
            "text": "الذكر سبب لربح الدنيا والآخرة وذخر للمؤمن.",
            "source": "السنة النبوية / الأذكار المأثورة",
            "benefit": "تقوية العلاقة مع الله وزيادة الأجر."
        }
    ],
    "أذكار الصباح": [
        {
            "title": "بسم الله الذي لا يضر مع اسمه شيء",
            "text": "بِسْمِ اللَّهِ الَّذِي لا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الأَرْضِ وَلا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ",
            "source": "السنة النبوية (حصن المسلم)",
            "benefit": "حفظ من المكروه خلال اليوم."
        },
        {
            "title": "أصبحنا وأمسى",
            "text": "أَصْبَحْنَا وأَمْسَيْنَا وَبِنِعْمَةِ اللَّهِ...",
            "source": "أذكار الصباح المأثورة (حصن المسلم)",
            "benefit": "شكر على النعمة واستعانة بالله طوال اليوم."
        },
        {
            "title": "آية الكرسي",
            "text": "اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ...",
            "source": "القرآن الكريم — سورة البقرة (2:255)",
            "benefit": "حماية وفضل عظيم عند الصباح والمساء."
        },
        {
            "title": "سورة الإخلاص والمعوذات",
            "text": "قُلْ هُوَ اللَّهُ أَحَدٌ ... قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ ... قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
            "source": "القرآن الكريم",
            "benefit": "حفظ وحماية من الشرور."
        },
        {
            "title": "دعاء الحفظ",
            "text": "اللَّهُمَّ إِنِّي أَصْبَحْتُ أُشْهِدُكَ ...",
            "source": "أذكار الصباح المتعارف عليها",
            "benefit": "طلب الحماية والبركة في اليوم."
        }
    ],
    "أذكار المساء": [
        {
            "title": "أمسينا وأمسى الملك لله",
            "text": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ ...",
            "source": "أذكار المساء المأثورة",
            "benefit": "شكر وحفظ في المساء."
        },
        {
            "title": "آية الكرسي",
            "text": "اللَّهُ لَا إِلَهَ إِلَّا هُوَ ...",
            "source": "القرآن الكريم — سورة البقرة",
            "benefit": "حماية وراحة في المساء."
        },
        {
            "title": "سورة الإخلاص والمعوذات",
            "text": "قُلْ هُوَ اللَّهُ أَحَدٌ ...",
            "source": "القرآن الكريم",
            "benefit": "وقاية من الشرور قبل النوم."
        },
        {
            "title": "الحمد لله الذي أطعمنا وسقانا",
            "text": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا ...",
            "source": "أذكار المساء المتعارف عليها",
            "benefit": "شكر على النعم والاستعداد للاسترخاء."
        }
    ],
    "أذكار النوم": [
        {
            "title": "اللهم باسمك أموت وأحيا",
            "text": "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وأَحْيَا",
            "source": "أذكار النوم المأثورة",
            "benefit": "توكل على الله عند النوم."
        },
        {
            "title": "آية الكرسي قبل النوم",
            "text": "اللَّهُ لَا إِلَهَ إِلَّا هُوَ ...",
            "source": "القرآن الكريم",
            "benefit": "حفظ من الشيطان والحماية أثناء النوم."
        },
        {
            "title": "اللهم قني عذابك يوم تبعث عبادك",
            "text": "اللَّهُمَّ قِنِي عَذَابَكَ يَوْمَ تَبْعَثُ عِبَادَكَ",
            "source": "أذكار النوم المأثورة",
            "benefit": "طلب أمان من عذاب الآخرة."
        }
    ],
    "أذكار الخروج من المنزل": [
        {
            "title": "بسم الله توكلت على الله ولا حول ولا قوة إلا بالله",
            "text": "بِسْمِ اللَّهِ، تَوَكَّلْتُ عَلَى اللَّهِ، لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ",
            "source": "أذكار مأثورة للخروج",
            "benefit": "الاستعانة بالله والثقة في قدرته."
        },
        {
            "title": "دعاء الاستعانة والحفظ",
            "text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ أَنْ أَضِلَّ ...",
            "source": "أذكار مأثورة",
            "benefit": "طلب الحفظ والهداية عند الخروج."
        }
    ],
    "أذكار الدخول إلى المنزل": [
        {
            "title": "السلام على أهل البيت",
            "text": "اللَّهُمَّ بَارِكْ لِي فِيمَنْ دَخَلْتُ وَاغْفِرْ لِي",
            "source": "أذكار الدخول المتعارف عليها",
            "benefit": "طلب البركة والسلامة للمنزل."
        },
        {
            "title": "اللهم أعنا على شكر نعمتك",
            "text": "سَبْحَانَ اللَّهِ ...",
            "source": "أذكار مأثورة",
            "benefit": "شكر الله على العودة للمنزل."
        }
    ],
    "أذكار الوضوء": [
        {
            "title": "بسم الله والحمد لله",
            "text": "بِسْمِ اللَّهِ ... الْحَمْدُ لِلَّهِ",
            "source": "أذكار الوضوء المأثورة",
            "benefit": "استحضار النية والطهارة الروحية."
        },
        {
            "title": "اللهم اجعلني من التوابين",
            "text": "اللَّهُمَّ اجْعَلْنِي مِنَ التَّوَّابِينَ",
            "source": "أذكار مأثورة بعد الوضوء",
            "benefit": "طلب الثبات والتوبة."
        }
    ],
    "أذكار الأكل": [
        {
            "title": "بسم الله",
            "text": "بِسْمِ اللَّهِ",
            "source": "القرآن والسنة",
            "benefit": "بركة للأكل وتجنب الإسراف."
        },
        {
            "title": "الحمد لله الذي أطعمنا",
            "text": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا ...",
            "source": "أذكار الطعام المأثورة",
            "benefit": "شكر الله على النعمة."
        },
        {
            "title": "الحمد لله الذي أطعمني وسقاني",
            "text": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا...",
            "source": "أذكار مأثورة",
            "benefit": "شكر وذكر الله بعد الأكل."
        }
    ],
    "أذكار بعد الصلاة": [
        {
            "title": "سبحان الله والحمد لله",
            "text": "سُبْحَانَ اللَّهِ وَالْحَمْدُ لِلَّهِ",
            "source": "أذكار ما بعد الصلاة",
            "benefit": "تمجيد الله وشكر الأعمال."
        },
        {
            "title": "أستغفر الله",
            "text": "أَسْتَغْفِرُ اللَّهَ",
            "source": "أذكار ما بعد الصلاة",
            "benefit": "طلب المغفرة بعد الصلاة."
        }
    ],
    "أذكار دخول المسجد": [
        {
            "title": "اللهم افتح لي أبواب رحمتك",
            "text": "اللَّهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ",
            "source": "أذكار دخول المسجد",
            "benefit": "طلب قبول العبادة والخشوع."
        },
        {
            "title": "السلام على أهل المسجد",
            "text": "السلام على أهل الذكر",
            "source": "أذكار مأثورة",
            "benefit": "آداب دخول المسجد وتحبيب المصلين."
        }
    ],
    "أذكار السفر": [
        {
            "title": "اللهم أنت الصاحب في السفر",
            "text": "اللَّهُمَّ أَنْتَ الصَّاحِبُ فِي السَّفَرِ ...",
            "source": "أذكار السفر المأثورة",
            "benefit": "طلب السلامة والحفظ في السفر."
        },
        {
            "title": "اللهم إني أعوذ بك من وعثاء السفر",
            "text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ وَعْثَاءِ السَّفَرِ ...",
            "source": "أذكار السفر",
            "benefit": "الحماية من مشاق السفر."
        }
    ],
    "أذكار الكرب والهم": [
        {
            "title": "اللهم إني عبدك ابن عبدك",
            "text": "اللَّهُمَّ إِنِّي عَبْدُكَ ابْنُ عَبْدِكَ ...",
            "source": "أذكار الكرب المأثورة",
            "benefit": "التفريغ والرجوع إلى الله في الشدائد."
        },
        {
            "title": "يا حي يا قيوم",
            "text": "يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيذُ",
            "source": "ذكر الاستعاذة والرجاء بالله",
            "benefit": "طلب النصر والفرج."
        }
    ]
}

# ---------------------------
# دوال مساعدة للواجهة
# ---------------------------

def init_state():
    """تهيئة session_state للمتغيرات الضرورية"""
    if "page" not in st.session_state:
        st.session_state.page = "welcome"  # welcome, home, section:<name>
    if "last_visit" not in st.session_state:
        st.session_state.last_visit = None
    if "font_size" not in st.session_state:
        st.session_state.font_size = 18
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "search" not in st.session_state:
        st.session_state.search = ""

def go_home():
    st.session_state.page = "home"

def open_section(name):
    st.session_state.page = f"section::{name}"

def download_section_json(section_name):
    """إرجاع ملف JSON جاهز للتحميل لمحتوى القسم"""
    items = ZIKR_DATA.get(section_name, [])
    data = {"section": section_name, "items": items, "exported_at": datetime.now().isoformat()}
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


# ---------------------------
# واجهة CSS والخلفية
# ---------------------------

PAGE_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Cairo', sans-serif;
    color: #0b2b1d;
}

/* الخلفية الإسلامية الخفيفة */
[data-testid="stAppViewContainer"] {
    background-image: url('https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1400&auto=format&fit=crop&ixlib=rb-4.0.3&s=9b6b7b3b2d2a3a5b1c2f1d1d2d3c4b5e');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* تغشية خفيفة لتوضيح النص */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.85));
    z-index: 0;
}

/* الحاوية الأساسية */
main .block-container {
    max-width: 900px;
    margin: 2rem auto;
    position: relative;
    z-index: 1;
}

/* العناوين */
h1 { font-size: 36px; color: #0b3b2f; font-weight:700; margin-bottom: 0.2rem; }
h2 { color: #0b3b2f; }

/* البطاقة */
.section-card {
    background: rgba(255,255,255,0.92);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(11, 43, 31, 0.08);
    color: #012318;
}

/* زر كبير */
.big-button {
    display: inline-block;
    background: linear-gradient(90deg,#2fb67a,#1e9d63);
    color: white;
    padding: 12px 20px;
    border-radius: 12px;
    font-weight:700;
    text-decoration: none;
    margin-top: 12px;
}

/* قائمة الخيارات */
.option-btn {
    background: linear-gradient(90deg,#f0f7ef,#e6faf0);
    border-radius: 12px;
    padding: 12px;
    color: #004d32;
    margin-bottom: 10px;
}

/* النص داخل Expander */
.stExpanderHeader {
    font-weight:700;
}

/* أزرار صغيرة لنسخ وتنزيل */
.small-btn {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    color: #083a2e;
    padding: 6px 10px;
    border-radius: 8px;
    font-weight:600;
}

/* تحسين مبدئي لحجم النص */
.zikr-text { font-size: 18px; line-height: 1.8; color:#013826; }
.small-muted { color:#396b57; font-size:14px; }
</style>
"""

# ---------------------------
# بناء الواجهات
# ---------------------------

def show_welcome():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)
    st.write("")  # spacing
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h1>بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</h1>", unsafe_allow_html=True)
    st.markdown("<h2>مرحبًا بك في بوت الأذكار الإسلامية 🌿</h2>", unsafe_allow_html=True)
    st.markdown("<p class='small-muted'>صلِّ على النبي محمد ﷺ — <b>اللهم صلِّ وسلِّم على نبينا محمد</b> 🌺</p>", unsafe_allow_html=True)
    st.markdown("<p class='small-muted'>هذا التطبيق يجمع الأذكار المأثورة من القرآن والسنة (مجموعات الأذكار المعروفة مثل \"حصن المسلم\" وغيرها) مع فوائد موجزة.</p>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; gap:12px; align-items:center;'>", unsafe_allow_html=True)
    if st.button("🔸 الدخول إلى الصفحات الرئيسية", key="enter_btn"):
        go_home()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def show_home():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h1>القائمة الرئيسية — الأذكار</h1>", unsafe_allow_html=True)
    st.markdown("<p class='small-muted'>اختر القسم الذي تريد الاطلاع عليه. جميع النصوص بالعربية مع مصادر عامة وفوائد مختصرة.</p>", unsafe_allow_html=True)

    # Search box
    search = st.text_input("🔎 ابحث في الأذكار (كلمة أو جزء):", value=st.session_state.get("search", ""))
    st.session_state.search = search

    st.markdown("<hr/>", unsafe_allow_html=True)

    # List sections plus small extras
    cols = st.columns([1,1])
    with cols[0]:
        if st.button("🌸 فضل الأذكار"):
            open_section("فضل الأذكار")
        if st.button("🌅 أذكار الصباح"):
            open_section("أذكار الصباح")
        if st.button("🌙 أذكار المساء"):
            open_section("أذكار المساء")
        if st.button("😴 أذكار النوم"):
            open_section("أذكار النوم")
        if st.button("🏡 أذكار الخروج من المنزل"):
            open_section("أذكار الخروج من المنزل")
        if st.button("🏠 أذكار الدخول إلى المنزل"):
            open_section("أذكار الدخول إلى المنزل")
    with cols[1]:
        if st.button("💧 أذكار الوضوء"):
            open_section("أذكار الوضوء")
        if st.button("🍽 أذكار الأكل"):
            open_section("أذكار الأكل")
        if st.button("🙏 أذكار بعد الصلاة"):
            open_section("أذكار بعد الصلاة")
        if st.button("🕌 أذكار دخول المسجد"):
            open_section("أذكار دخول المسجد")
        if st.button("✈️ أذكار السفر"):
            open_section("أذكار السفر")
        if st.button("😥 أذكار الكرب والهم"):
            open_section("أذكار الكرب والهم")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>يمكنك تحميل أي قسم كامل كملف JSON من داخل صفحة كل قسم.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # quick jump to top searched results (if any)
    if search and len(search.strip()) >= 2:
        results = []
        for sec, items in ZIKR_DATA.items():
            for it in items:
                if search.strip() in it.get("text", "") or search.strip() in it.get("title", ""):
                    results.append((sec, it))
        if results:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.subheader(f"نتائج البحث ({len(results)})")
            for sec, it in results:
                st.markdown(f"**{sec}** — **{it['title']}**")
                st.markdown(f"<div class='zikr-text'>{it['text']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='small-muted'>المصدر: {it['source']} — الفائدة: {it['benefit']}</div>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("لم تُعثر على نتائج مطابقة.")

def show_section(section_name):
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown(f"<h1>📚 {section_name}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='small-muted'>فيما يلي الأذكار الواردة في قسم: <b>{section_name}</b>. جميع النصوص مأثورة عن القرآن أو الأذكار المأثورة في السنة.</p>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; gap:8px; margin-bottom:12px;'>", unsafe_allow_html=True)
    if st.button("◀️ العودة للقائمة الرئيسية"):
        go_home()
    # تحميل ال json
    data_bytes = download_section_json(section_name)
    st.download_button("⬇️ تحميل هذا القسم (JSON)", data=data_bytes, file_name=f"{section_name}.json", mime="application/json")
    st.markdown("</div>", unsafe_allow_html=True)

    items = ZIKR_DATA.get(section_name, [])
    if not items:
        st.info("لا توجد عناصر في هذا القسم حالياً.")
    else:
        for i, it in enumerate(items, start=1):
            with st.expander(f"{i}. {it['title']}", expanded=False):
                st.markdown(f"<div class='zikr-text'>{it['text']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='small-muted'>المصدر: {it['source']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='small-muted'>الفائدة: {it['benefit']}</div>", unsafe_allow_html=True)
                # أزرار نسخ ومشاركة
                cols = st.columns([1,1,1])
                with cols[0]:
                    if st.button("نسخ الذكر", key=f"copy_{section_name}_{i}"):
                        st.experimental_set_query_params()  # مجرد تشغيل لتفادي إعادة التقديم الغير مرغوب
                        st.success("تم نسخ الذكر! انسخه من الحقل أدناه إن لم يعمل الزر.")
                        st.text_area("الذكر (انسخ منه):", value=it['text'], height=80)
                with cols[1]:
                    if st.button("مشاهدة الفائدة والمصدر", key=f"show_{section_name}_{i}"):
                        st.info(f"المصدر: {it['source']}\n\nالفائدة: {it['benefit']}")
                with cols[2]:
                    # تنزيل ذكر واحد كملف نصي
                    single = json.dumps({"title": it['title'], "text": it['text'], "source": it['source'], "benefit": it['benefit']}, ensure_ascii=False)
                    st.download_button("⬇️ تنزيل ذكر", data=single.encode('utf-8'), file_name=f"{section_name}_{i}.json", mime="application/json")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# التطبيق الرئيسي
# ---------------------------

def run():
    init_state()
    page = st.session_state.page

    if page == "welcome":
        show_welcome()
    elif page == "home":
        show_home()
    elif page.startswith("section::"):
        _, sec = page.split("::", 1)
        show_section(sec)
    else:
        show_home()

if __name__ == "__main__":
    run()
