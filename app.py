# app.py
import streamlit as st
import openai
import os
import base64
import requests
from io import BytesIO

# -------------------------
# إعداد الصفحة + ستايل خلفية ثابتة
# -------------------------
st.set_page_config(page_title="مولّد الصور (AI)", page_icon="🎨", layout="centered")

# خلفية ثابتة من Unsplash (تقدر تغيّر الرابط لصورة تحبها)
BG_URL = "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1400&q=80"

st.markdown(
    f"""
    <style>
      .stApp {{ background-image: url("{BG_URL}"); background-size: cover; background-attachment: fixed; }}
      .overlay {{ background: rgba(0,0,0,0.55); padding: 22px; border-radius: 12px; color: #f3f4f6; }}
      .title-big {{ font-size: 34px; font-weight:800; color:#fff; margin-bottom:6px; }}
      .sub {{ color:#e6e7e8; }}
      .grad-btn {{
        background: linear-gradient(90deg,#ff6b6b,#ff9a6b);
        color: white; padding: 12px 20px; border-radius: 12px; border: none;
      }}
      .small-box {{ background: rgba(255,255,255,0.06); padding:12px; border-radius:10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="overlay">', unsafe_allow_html=True)
st.markdown('<div style="display:flex; align-items:center; gap:16px;"><div style="flex:1;">'
            '<div class="title-big">🎨 مولّد الصور بالذكاء الاصطناعي</div>'
            '<div class="sub">اكتب وصفاً واضحاً للصورة وخلّي الذكاء الاصطناعي يرسمها لك. يمكنك تحميل الناتج مباشرة.</div>'
            '</div></div>', unsafe_allow_html=True)

# -------------------------
# جلب مفتاح الـ API (من Secrets أو متغير بيئة)
# -------------------------
OPENAI_API_KEY = None
# Streamlit secrets (مفضّل)
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ مفتاح OpenAI غير موجود. ضع OPENAI_API_KEY في Settings → Secrets (Streamlit) أو كمتغير بيئة.")
    st.stop()

openai.api_key = OPENAI_API_KEY

# -------------------------
# واجهة المستخدم
# -------------------------
with st.form("gen_form"):
    prompt = st.text_area("✍️ اكتب وصف الصورة (بالعربية):", height=140, placeholder="مثال: مشهد غروب على شاطئ مع طائر النورس...")
    style = st.selectbox("🎨 اختر أسلوب الرسم:", ["واقعي", "كرتوني", "لوحة زيتية", "خيال علمي", "بيكسل (8-bit)"])
    # خيارات الأحجام المدعومة للموديل gpt-image-1
    size_label_map = {
        "1024 × 1024 (مناسب)": "1024x1024",
        "1024 × 1536 (طولي)": "1024x1536",
        "1536 × 1024 (عرضي)": "1536x1024",
        "auto (اختيار تلقائي)": "auto",
    }
    size_choice = st.radio("📐 اختر حجم الصورة (مسموح فقط بالقيم التالية):", list(size_label_map.keys()), index=0)
    filename = st.text_input("🖼️ اسم الملف عند التحميل (بدون امتداد):", "my_image")
    generate_btn = st.form_submit_button("🚀 إنشاء الصورة")

# -------------------------
# دوال مساعدة لاستخراج الصورة من الـ response
# -------------------------
def extract_image_bytes(resp):
    """
    يحاول الحصول على البايت من الاستجابة:
    - يفضّل b64_json (مباشر).
    - إن لم يوجد، يحاول تحميل الصورة من URL إن وُجد.
    يعيد bytes أو None.
    """
    if resp is None:
        return None
    # Response قد يكون object أو dict
    data0 = None
    if isinstance(resp, dict):
        data = resp.get("data")
        if data:
            data0 = data[0]
    else:
        # مكتبة openai غالباً تعطي obj مع .data
        try:
            data0 = resp.data[0]
        except Exception:
            try:
                data0 = resp["data"][0]
            except Exception:
                data0 = None

    if not data0:
        return None

    # b64
    b64 = None
    if isinstance(data0, dict):
        b64 = data0.get("b64_json") or data0.get("b64")
        url = data0.get("url")
    else:
        # object with attributes
        b64 = getattr(data0, "b64_json", None) or getattr(data0, "b64", None)
        url = getattr(data0, "url", None)

    if b64:
        return base64.b64decode(b64)
    if url:
        # نحاول تحميله
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.content
    return None

# -------------------------
# تنفيذ الطلب عند الضغط
# -------------------------
if generate_btn:
    if not prompt.strip():
        st.warning("✍️ من فضلك اكتب وصف الصورة أولاً.")
    else:
        chosen_size = size_label_map[size_choice]
        # تحاشي أحجام غير مدعومة (واضح أيضاً في الواجهة)
        allowed = {"1024x1024", "1024x1536", "1536x1024", "auto"}
        if chosen_size not in allowed:
            st.error("الحجم المختار غير مدعوم من قبل الموديل. اختَر حجم مدعوم.")
        else:
            with st.spinner("⏳ جاري التوليد — انتظر لحظات..."):
                try:
                    final_prompt = f"{prompt.strip()} -- style: {style}"
                    # نستخدم واجهة الصور (تختلف حسب إصدار المكتبة، الكود أدناه يوافق الAPI الجديد)
                    response = openai.images.generate(
                        model="gpt-image-1",
                        prompt=final_prompt,
                        size=chosen_size
                    )
                    img_bytes = extract_image_bytes(response)
                    if not img_bytes:
                        st.error("❌ لم نستلم صورة من السرفر. حاول مجدداً أو راجع إعدادات المفتاح والرصيد.")
                    else:
                        st.image(img_bytes, caption="✅ الصورة الناتجة", use_column_width=True)
                        st.download_button("⬇️ تحميل الصورة كـ PNG", data=img_bytes, file_name=f"{filename}.png", mime="image/png")
                        st.success("تم التوليد بنجاح! 🎉")
                except Exception as e:
                    # نفصل الأخطاء الشائعة ونعطي حلول مقترحة
                    err_text = str(e)
                    # حالات شائعة
                    if "invalid_api_key" in err_text.lower() or "incorrect api key" in err_text.lower():
                        st.error("🔐 مفتاح الـ API غير صحيح أو مُلغى. تأكد من OPENAI_API_KEY في Secrets.")
                    elif "billing hard limit" in err_text.lower() or "billing" in err_text.lower():
                        st.error("💳 حدّ الفوترة لديك وصل أو الحساب موقوف. حلّ المشكلة من لوحة OpenAI (أضف وسيلة دفع أو افتح تذكرة).")
                    elif "invalid value" in err_text.lower() and "size" in err_text.lower():
                        st.error("⚠️ الحجم غير مدعوم. اختَر واحداً من الأحجام المتاحة في الواجهة.")
                    else:
                        # رسالة عامة + عرض نص الخطأ (مخفف)
                        st.error("❌ حصل خطأ أثناء التواصل مع OpenAI. حاول مرة أخرى فيما بعد.")
                        st.info(f"تفاصيل الخطأ: {err_text[:100]}...")

st.markdown("</div>", unsafe_allow_html=True)
