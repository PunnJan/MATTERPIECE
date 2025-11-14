import streamlit as st
from openai import OpenAI

# แสดงชื่อเรื่องและคำอธิบาย (ภาษาไทย)
st.title("💬 แชทบอท (ตอบเป็นภาษาไทย)")
st.write(
    "นี่คือแชทบอทตัวอย่างที่ใช้โมเดล GPT-4.1 ของ OpenAI ในการสร้างคำตอบ โดยแอปนี้จะตั้งค่าให้ตอบเป็นภาษาไทยเสมอ\n"
    "เพื่อใช้งาน ให้ใส่ OpenAI API Key ของคุณ (ดูได้ที่ https://platform.openai.com/account/api-keys) "
    "และสามารถเรียนรู้วิธีสร้างแอปนี้ได้จาก: https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps"
)

# รับ API Key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("กรุณากรอก OpenAI API Key เพื่อใช้งาน", icon="🗝️")
else:
    # สร้าง client ของ OpenAI
    client = OpenAI(api_key=openai_api_key)

    # สร้างตัวแปรใน session state สำหรับเก็บข้อความแชท
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ถ้าไม่มี system message ที่บอกให้ตอบเป็นภาษาไทย ให้แทรกเข้าไปเป็นข้อความแรก
    has_system = any(m.get("role") == "system" for m in st.session_state.messages)
    if not has_system:
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": "You are a helpful assistant. Please reply in Thai (ภาษาไทย) for all user messages."
        })

    # แสดงข้อความที่มีอยู่แล้ว ยกเว้น system messages (ไม่แสดงให้ผู้ใช้เห็น)
    for message in st.session_state.messages:
        if message.get("role") == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ฟิลด์ให้ผู้ใช้พิมพ์ (placeholder เป็นภาษาไทย)
    if prompt := st.chat_input("ถามฉันเป็นภาษาไทยได้เลย..."):
        # เก็บและแสดงข้อความของผู้ใช้
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # เรียก OpenAI เพื่อสร้างคำตอบ (รวมทุกข้อความรวมถึง system message)
        stream = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # สตรีมคำตอบกลับไปยังหน้า แล้วเก็บคำตอบลง session state
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
