# app.py
# لعبة / أداة: مولد صور بالذكاء الصناعي (واجهة عربية، تجربة مُحسّنة)
# تعليمات: ضع مفتاح OpenAI في Streamlit Secrets باسم OPENAI_API_KEY
# ملف requirements: streamlit, openai, requests, Pillow

import streamlit as st
import io
import base64
import time
import json
from typing import List

# محاولة استدعاء مكتبة ال-OpenAI الحديثة أولا ثم العودة للـ legacy إذا لزم
def get_openai_wrapper(api_key: str):
    """
    يرجع كائن يحوي دالة generate_images(prompt, size, n) -> list of bytes_or_urls
    نتعامل مع احتمالات: response.data[].url أو .b64_json
    """
    try:
        # new client (openai>=1.0 style)
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        def generate(prompt: str, size: str, n: int):
            resp = client.images.generate(model="gpt-image-1", prompt=prompt, size=size, n=n)
            results = []
            # resp.data قد تكون list من objects أو dicts
            for item in getattr(resp, "data", resp.get("data", [])):
                # محاولة الوصول لخاصية url
                url = None
                b64 = None
                if isinstance(item, dict):
                    url = item.get("url")
                    b64 = item.get("b64_json") or item.get("b64")
                else:
                    # object-like
                    url = getattr(item, "url", None)
                    b64 = getattr(item, "b64_json", None) or getattr(item, "b64", None)
                if url:
                    results.append({"url": url})
                elif b64:
                    results.append({"b64": b64})
                else:
                    # fallback: stringify
                    results.append({"raw": str(item)})
            return results
        return generate
    except Exception:
        # legacy openai package
        try:
            import openai
            openai.api_key = api_key
            def generate(prompt: str, size: str, n: int):
                resp = openai.Image.create(prompt=prompt, n=n, size=size)
                results = []
                for item in resp.get("data", []):
                    url = item.get("url")
                    b64 = item.get("b64_json") or item.get("b64")
                    if url:
                        results.append({"url": url})
                    elif b64:
                        results.append({"b64": b64})
                    else:
                        results.append({"raw": str(item)})
                return results
            return generate
        except Exception as e:
            raise RuntimeError("لم يتم العثور على مكتبة OpenAI مناسبة. ثبّت مكتبة openai.") from e

# --- مساعدة لتغليف رسائل الأخطاء (نخفي أي مفتاح ممكن يظهر داخل رسالة الخطأ) ---
import re
def mask_api_key(s: str) -> str:
    if not s:
        return s
    # استبدال أي سلسلة تبدو كمفتاح sk-... إلى sk-********
    return re.sub(r"sk-[A-Za-z0-9\-_]{10,}", "sk-********", str(s))

# --- CSS (خلفية جميلة، RTL، عناصر أنيقة) ---
PAGE_CSS = """
<style>
:root{
  --accent:#28a7c5;
  --card-bg: rgba(255,255,255,0.03);
  --glass: rgba(255,255,255,0.04);
}
html,body, [class*="css"]  {
    direction: rtl;
}
.stApp {
    background: linear-gradient(135deg, #0f1724 0%, #1f2937 40%, #2b3138 100%);
    color: #f3f4f6;
    background-attachment: fixed;
    font-family: "Segoe UI", Tahoma, "Helvetica Neue", Arial;
}
.app-header {
    padding: 18px 16px;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    box-shadow: 0 6px 18px rgba(5,7,10,0.4);
    margin-bottom: 16px;
}
.container-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 8px 26px rgba(2,6,12,0.45);
    margin-bottom: 16px;
}
.big-title {
    font-size: 40px;
    font-weight: 700;
    color: #fff;
}
.lead {
    color: #dbeafe;
    opacity: 0.95;
}
.btn-primary {
    background: linear-gradient(90deg,#ff7a18,#af002d 60%);
    color: white !important;
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 700;
}
.small-muted { color: #cbd5e1; opacity: 0.85; font-size: 14px; }
.prompt-suggestion { margin:4px; display:inline-block; background: rgba(255,255,255,0.03); padding:6px 10px; border-radius:8px; cursor:pointer; }
.result-img { border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6);}
.success-box { background: linear-gradient(90deg,#06b6d4,#3b82f6); padding:10px 12px; color:#fff; border-radius:8px; display:inline-block; }
.error-box { background: rgba(255,50,50,0.12); padding:10px 12px; color:#ffb4b4; border-radius:8px; }
</style>
"""

# --- صفحة ---
st.set_page_config(page_title="مولد الصور بالذكاء الاصطناعي", page_icon="🎨", layout="centered")
st.markdown(PAGE_CSS, unsafe_allow_html=True)

# Header
st.markdown('<div class="app-header container-card"><div class="big-title">🎨 مولد الصور بالذكاء الاصطناعي</div>'
            '<div class="lead">اكتب وصفًا، واختر الإعدادات، ودع الذكاء الاصطناعي يرسم خيالك بجودة عالية.</div></div>',
            unsafe_allow_html=True)

# Sidebar: اقتراحات وإعدادات
with st.sidebar:
    st.header("الإعدادات")
    st.write("ضع مفتاح OpenAI في Settings → Secrets باسم `OPENAI_API_KEY` (بدون نشره عام).")
    st.caption("⚠️ إن نُشر المفتاح من قبل، احذفه (Revoke) وولّد واحد جديد.")

    ENABLE_SOUND = st.checkbox("تشغيل صوت عند النجاح (يمكن رفع ملف صوتي)", value=False)
    uploaded_sound = None
    if ENABLE_SOUND:
        uploaded_sound = st.file_uploader("رفع ملف صوت (mp3/wav) أو اتركه للتغاضي", type=["mp3","wav"], accept_multiple_files=False)

    st.write("---")
    st.subheader("اقتراحات جاهزة")
    examples = [
        "مشهد غروب شمس فوق بحر هادئ، ألوان دافئة، تفاصيل واقعية",
        "قطة ترتدي زي رائد فضاء بجودة سينمائية",
        "مدينة مستقبلية مطلة على نهر ليلًا، نيون، تفاصيل عالية",
        "منظر جبلي مُغطّى بالثلج مع إنعكاس ضوء الشمس",
        "بطاقة تهنئة بسيطة مع نباتات وخط عربي جميل"
    ]
    # عرض أمثلة قابلة للضغط لإدخالها في المحرر
    for ex in examples:
        if st.button(f"✦ {ex}", key=f"ex_{ex[:8]}"):
            st.session_state["suggestion_to_insert"] = ex

# main UI: prompt + options
col1, col2 = st.columns([3,1])

with col1:
    prompt = st.text_area("📝 اكتب وصف الصورة هنا:", height=140, value=st.session_state.get("suggestion_to_insert",""))
    # قليل من الأمثلة السريعة تحت مربع النص
    st.markdown('<div class="small-muted">نصيحة: صِف التفاصيل، الأسلوب (photorealistic, oil painting), الأجواء، ووجهة النظر.</div>', unsafe_allow_html=True)

with col2:
    st.markdown("<div style='padding:6px;border-radius:8px;background:rgba(255,255,255,0.02)'>"
                "<b>إعدادات سريعة</b></div>", unsafe_allow_html=True)
    size = st.radio("📐 الحجم:", ("256x256", "512x512", "1024x1024"), index=1)
    num = st.slider("عدد الصور:", 1, 4, 1)
    download_after = st.checkbox("أتمكّن المستخدم من تنزيل الصورة؟", value=True)

# خيارات متقدمة قابلة للطي
with st.expander("خيارات متقدمة (اختياري)"):
    style_hint = st.text_input("🎨 نمط فني (مثال: photorealistic, oil painting, cartoon):", value="")
    seed_hint = st.text_input("🔢 مفتاح (seed) عشوائي (اختياري):", value="")
    show_history = st.checkbox("عرض معرض الصور السابقة (session)", value=True)

# أزرار مساعدة: ادراج مثال/مسح
col_a, col_b, col_c = st.columns([1,1,1])
with col_a:
    if st.button("✨ أدخل مثال سريع"):
        st.session_state["suggestion_to_insert"] = examples[0]
        st.experimental_rerun()
with col_b:
    if st.button("🔄 امسح"):
        st.session_state["suggestion_to_insert"] = ""
        st.experimental_rerun()
with col_c:
    if st.button("🖼️ معرض الصور"):
        # يمر إلى أسفل حيث المعرض
        st.markdown("<div id='gallery'></div>", unsafe_allow_html=True)

st.write("---")

# عرض حالة المفتاح وتهيئة العميل
if "OPENAI_API_KEY" not in st.secrets:
    st.error("مفتاح OPENAI_API_KEY غير مُعرف. اذهب إلى Settings → Secrets في Streamlit وأضفه بصيغة:\n\n`OPENAI_API_KEY = \"sk-...\"`")
    st.stop()

api_key = st.secrets["OPENAI_API_KEY"]

# أنشئ wrapper للـ OpenAI
try:
    generate_images = get_openai_wrapper(api_key)
except Exception as e:
    st.error("حدث خطأ عند تهيئة مكتبة OpenAI. الرجاء تثبيت مكتبة openai وإعادة نشر التطبيق.")
    st.exception(e)
    st.stop()

# تحويل استجابة Image (url or b64) إلى bytes جاهزة للعرض والتحميل
import requests
from PIL import Image
def fetch_image_bytes(item):
    # item: dict with keys 'url' or 'b64' or 'raw'
    if "url" in item and item["url"]:
        try:
            r = requests.get(item["url"], timeout=20)
            r.raise_for_status()
            return r.content
        except Exception:
            return None
    if "b64" in item and item["b64"]:
        try:
            b = base64.b64decode(item["b64"])
            return b
        except Exception:
            return None
    return None

# تخزين المعرض في الجلسة
if "gallery" not in st.session_state:
    st.session_state["gallery"] = []

# زر التوليد
if st.button("🚀 توليد الصورة", key="generate_btn"):
    if not prompt or not prompt.strip():
        st.error("⚠️ من فضلك اكتب وصفًا للصورة في الخانة أعلاه.")
    else:
        # ندمج الوصف مع hint للأسلوب إن زُود
        full_prompt = prompt.strip()
        if style_hint:
            full_prompt += " | style: " + style_hint
        # خيار seed يضاف فقط كملاحظة (بعض الAPIs لا تدع seed)
        if seed_hint:
            full_prompt += f" | seed:{seed_hint}"

        with st.spinner("⏳ جاري توليد الصورة — قد يستغرق الأمر قليلًا..."):
            try:
                results = generate_images(full_prompt, size, num)
            except Exception as e:
                masked = mask_api_key(str(e))
                st.error("❌ حصل خطأ أثناء الاتصال بخدمة OpenAI. (" + masked + ")")
                st.stop()

        # لو لم تُرجع نتائج
        if not results:
            st.error("لم تُرسل الخدمة أي نتيجة. جرّب تغيير الوصف أو الحجم ثم حاول مرة أخرى.")
        else:
            cols = st.columns(min(len(results), 3))
            saved_any = 0
            for idx, item in enumerate(results):
                img_bytes = fetch_image_bytes(item)
                col = cols[idx % len(cols)]
                if img_bytes:
                    # عرض مصغّر
                    try:
                        col.image(img_bytes, use_column_width=True, caption=f"الصورة {idx+1}", output_format='PNG')
                    except Exception:
                        # محاولة حفظ كملف ثم عرض
                        try:
                            img = Image.open(io.BytesIO(img_bytes))
                            col.image(img, use_column_width=True, caption=f"الصورة {idx+1}")
                        except Exception:
                            col.write("الصورة (لم تُعرض)")

                    # زر تحميل
                    if download_after:
                        filename = f"ai_image_{int(time.time())}_{idx+1}.png"
                        col.download_button("⬇️ تحميل", data=img_bytes, file_name=filename, mime="image/png")

                    # حفظ المعرض في الجلسة
                    st.session_state["gallery"].append({"time": time.time(), "bytes": img_bytes, "prompt": full_prompt})
                    saved_any += 1
                else:
                    col.error("لم نستطع تنزيل الصورة (تحقق من الاستجابة).")

            if saved_any:
                st.success(f"تم توليد {saved_any} صورة وحفظها في المعرض (session).")
                # شغّل صوت النجاح إذا رفع المستخدم واحدًا
                try:
                    if uploaded_sound:
                        st.audio(uploaded_sound.read())
                except Exception:
                    pass

# معرض الصور (history)
if show_history:
    st.write("---")
    st.subheader("🖼️ معرض الصور (جلسة العمل)")
    if st.session_state["gallery"]:
        # عرض أحدث 6 صور
        recent = list(reversed(st.session_state["gallery"]))[:12]
        cols = st.columns(min(3, len(recent)))
        for i, entry in enumerate(recent):
            c = cols[i % len(cols)]
            try:
                c.image(entry["bytes"], use_column_width=True, caption=f"الوصف: {entry['prompt'][:80]}...")
            except Exception:
                c.write("صورة")
            # زر حذف فردي
            if c.button("🗑️ حذف", key=f"del_{i}"):
                st.session_state["gallery"].remove(entry)
                st.experimental_rerun()
    else:
        st.info("لا توجد صور محفوظة في هذه الجلسة بعد — أنشئ بعض الصور!")

# روابط وإرشادات إضافية
st.write("---")
st.markdown("""
**ملاحظات سريعة وطرق حل أخطاء شائعة**
- إن ظهر لك `401 Invalid API key` تأكد أنك وضعت المفتاح في **Settings → Secrets** بصيغة:
