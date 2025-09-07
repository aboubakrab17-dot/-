import streamlit as st

# ----- إعدادات الصفحة -----
st.set_page_config(page_title="البوت الشاب", page_icon="🤖", layout="wide")

# ----- تنسيق CSS -----
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .chat-container {
        max-width: 700px;
        margin: auto;
    }
    .user-msg {
        background-color: #25D366; /* أخضر واتساب */
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px;
        text-align: right;
        font-size: 18px;
    }
    .bot-msg {
        background-color: #0084FF; /* أزرق مسنجر */
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px;
        text-align: left;
        font-size: 18px;
    }
    .suggestion-btn {
        display: inline-block;
        background-color: #ffffff;
        border: 2px solid #0084FF;
        color: #0084FF;
        padding: 10px 18px;
        margin: 5px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }
    .suggestion-btn:hover {
        background-color: #0084FF;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ----- تهيئة جلسة -----
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ----- عنوان -----
st.markdown("<h2 style='text-align: center;'>💬 مرحبا بك في البوت الشاب 🤖</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>بوت تفاعلي يعطيك خطط، نصائح، نكت، وصفات، معلومات والكثير! 🚀</p>", unsafe_allow_html=True)

# ----- عرض المحادثة -----
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for sender, text in st.session_state["messages"]:
    if sender == "user":
        st.markdown(f"<div class='user-msg'>🧑‍💻 {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>🤖 {text}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----- صندوق الإدخال -----
user_input = st.text_input("...اكتب رسالتك هنا", "")

# ----- المنطق -----
def bot_reply(msg):
    msg = msg.strip()
    if "خطة" in msg:
        return "📝 خطة سريعة: 45 دقيقة دراسة + 15 مراجعة يومياً. نهاية الأسبوع: تلخيص وتقييم ✅"
    elif "حكمة" in msg:
        return "💡 الحكمة: العلم نور والجهل ظلام."
    elif "نكتة" in msg:
        return "😂 نكتة: واحد راح للطبيب قالو عندي دوخة، قالو الطبيب روح دور حتى تتعود!"
    elif "وصفة" in msg:
        return "🍲 وصفة: سلطة سهلة = خيار + طماطم + زيت زيتون + ليمون."
    elif "مشروع" in msg:
        return "🚀 مشروع: مدونة شخصية تنشر فيها مقالاتك أو أعمالك."
    elif "تمرين" in msg:
        return "💪 تمرين: 20 ضغط + 20 بطن + 15 سكوات كل صباح."
    elif "نصيحة" in msg:
        return "🧠 نصيحة: نظم وقتك، صحتك أولاً، ولا تقارن نفسك بغيرك."
    elif "تحفيز" in msg:
        return "🔥 تذكر: كل يوم صغير يساوي خطوة نحو هدفك الكبير!"
    elif "معلومة" in msg:
        return "📘 معلومة: قلب الإنسان يضخ حوالي 7000 لتر دم يومياً!"
    else:
        return "🙂 مرحبا! أرسل كلمة مثل (خطة، حكمة، نكتة، وصفة، مشروع، تمرين، نصيحة، تحفيز، معلومة)."

# ----- معالجة الإدخال -----
if user_input:
    st.session_state["messages"].append(("user", user_input))
    reply = bot_reply(user_input)
    st.session_state["messages"].append(("bot", reply))
    st.experimental_rerun()

# ----- أزرار الاقتراحات -----
st.markdown("<h4>✍️ اقتراحات سريعة:</h4>", unsafe_allow_html=True)
cols = st.columns(3)
suggestions = ["اعطيني خطة", "حكمة اليوم", "خليني نضحك 😁", 
               "وصفة سريعة", "اعطيني فكرة مشروع", "تمرين بسيط", 
               "نصيحة", "تحفيز", "معلومة"]

for i, s in enumerate(suggestions):
    if cols[i % 3].button(s):
        st.session_state["messages"].append(("user", s))
        reply = bot_reply(s)
        st.session_state["messages"].append(("bot", reply))
        st.experimental_rerun()
