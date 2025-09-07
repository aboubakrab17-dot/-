import streamlit as st
from transformers import pipeline

# 🚀 تحميل الموديل من HuggingFace (بدون API KEY)
generator = pipeline("text-generation", model="gpt2")

# 🎨 إعدادات الصفحة
st.set_page_config(page_title="💬 بوت الدردشة الممتع", page_icon="✨", layout="centered")
st.markdown(
    """
    <h1 style='text-align: center; color: #4CAF50;'>
        🤖 مرحبا بك في بوت الدردشة الممتع 🎉
    </h1>
    <p style='text-align: center; font-size:18px; color: gray;'>
        تفضل بكتابة أي رسالة وسأرد عليك بطريقة ذكية ومسلية 👇
    </p>
    """, unsafe_allow_html=True
)

# 📝 تخزين المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ عرض المحادثة السابقة
for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(
            f"""
            <div style='display:flex; justify-content:flex-end; margin:8px 0;'>
                <div style='background:#DCF8C6; padding:10px 15px; border-radius:20px; max-width:70%; font-size:16px;'>
                    👤 {msg}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='display:flex; justify-content:flex-start; margin:8px 0;'>
                <div style='background:#E6E6E6; padding:10px 15px; border-radius:20px; max-width:70%; font-size:16px;'>
                    🤖 {msg}
                </div>
            </div>
            """, unsafe_allow_html=True
        )

# ✍️ إدخال المستخدم
st.markdown("<br>", unsafe_allow_html=True)
user_input = st.text_input("✍️ اكتب رسالتك هنا:", "", key="input_box")

# 🚀 الأزرار
col1, col2, col3 = st.columns([3,1,1])
with col1:
    pass
with col2:
    send = st.button("🚀 إرسال")
with col3:
    clear = st.button("🗑️ مسح")

# ⚡ معالجة الإدخال
if send and user_input.strip():
    # ➕ إضافة رسالة المستخدم
    st.session_state.messages.append(("user", user_input))

    # 🤖 توليد رد البوت
    response = generator(user_input, max_length=80, num_return_sequences=1)[0]["generated_text"]
    bot_reply = response[len(user_input):].strip().split(".")[0] + "."

    # ➕ إضافة رد البوت
    st.session_state.messages.append(("bot", bot_reply))

    # إعادة تحميل
    st.experimental_rerun()

# 🗑️ زر مسح المحادثة
if clear:
    st.session_state.messages = []
    st.experimental_rerun()
