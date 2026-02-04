# chatbot.py
# Enhanced Chatbot với context-aware và gợi ý câu hỏi

import os
import time
import streamlit as st
from groq import Groq

# System prompt nâng cao cho chatbot
CHATBOT_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh, thân thiện và hữu ích. 
Bạn có nhiệm vụ giúp người dùng hiểu sâu hơn về nội dung video YouTube.

NGUYÊN TẮC:
1. Trả lời dựa trên nội dung video đã được tóm tắt
2. Nếu câu hỏi nằm ngoài nội dung video, thông báo lịch sự và cố gắng liên hệ với chủ đề
3. Sử dụng ngôn ngữ dễ hiểu, thân thiện
4. Có thể đưa ra ví dụ minh họa khi cần
5. Trả lời bằng tiếng Việt (trừ khi được yêu cầu khác)

NỘI DUNG VIDEO ĐÃ TÓM TẮT:
{summary}
"""

# Gợi ý câu hỏi mẫu
SUGGESTED_QUESTIONS = [
    "📝 Tóm tắt lại ngắn gọn trong 3 câu",
    "🔑 Những điểm chính quan trọng nhất là gì?",
    "💡 Giải thích chi tiết hơn về chủ đề này",
    "📚 Có thể áp dụng kiến thức này như thế nào?",
    "❓ Còn điều gì tôi cần biết thêm không?",
]

# Initialize show_prompt if not already done
if 'show_prompt' not in st.session_state:
    st.session_state.show_prompt = False

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []


def initialize_client(api_key):
    """Initialize the Groq client with the provided API key."""
    return Groq(api_key=api_key)


def generate_chatbot_response(client, user_question, use_context=True):
    """
    Generate a response from the chatbot based on the cached summary and user question.
    
    Args:
        client: Groq client
        user_question: Câu hỏi của người dùng
        use_context: Có sử dụng context từ summary không
    
    Returns:
        str: Câu trả lời từ AI
    """
    # Retrieve summary from session state
    summary = st.session_state.get('follow_up_summary', "")
    
    if not summary and use_context:
        return "⚠️ Chưa có bản tóm tắt video. Vui lòng tạo bản tóm tắt trước khi trò chuyện!"

    # Build conversation history
    messages = []
    
    # System message với context
    if use_context and summary:
        system_content = CHATBOT_SYSTEM_PROMPT.format(summary=summary)
        messages.append({"role": "system", "content": system_content})
    
    # Add conversation history (last 10 messages to avoid token limit)
    history = st.session_state.get('chat_messages', [])[-10:]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current question
    messages.append({"role": "user", "content": user_question})

    try:
        # Generate response using the client
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            stream=True,
        )

        # Accumulate response chunks
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content

        return response
        
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower():
            return "⚠️ Đã vượt quá giới hạn API. Vui lòng đợi vài phút và thử lại."
        elif "invalid_api_key" in error_msg.lower():
            return "❌ API Key không hợp lệ. Vui lòng kiểm tra lại."
        else:
            return f"❌ Lỗi: {error_msg}"


@st.fragment
def display_download_button(content, file_name):
    """Display a download button for the assistant's response."""
    if st.download_button(
        label="💾 Lưu",
        data=content,
        file_name=file_name,
        mime="text/plain",
        icon=":material/download:"
    ):
        st.toast("Đã lưu thành công!", icon="✅")


def display_typing_simulation(text, delay=0.005):
    """Simulate typing effect for displaying responses."""
    response_placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        response_placeholder.markdown(displayed_text + "▌")
        time.sleep(delay)
    response_placeholder.markdown(displayed_text)
    return displayed_text


def display_suggested_questions():
    """Hiển thị các câu hỏi gợi ý."""
    st.markdown("##### 💡 Câu hỏi gợi ý:")
    
    cols = st.columns(2)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"suggest_{i}", use_container_width=True):
                return question.split(" ", 1)[1]  # Remove emoji prefix
    return None


def display_chat_enhanced(client):
    """
    Display the enhanced chat interface with better UX.
    """
    st.markdown("### 💬 Trò Chuyện Về Video")
    
    # Kiểm tra đã có summary chưa
    if "follow_up_summary" not in st.session_state or not st.session_state.follow_up_summary:
        st.warning("⚠️ Vui lòng tạo bản tóm tắt video trước khi trò chuyện!")
        st.info("👉 Quay lại tab **Tóm tắt** và nhấn **Get Detailed Notes**")
        return
    
    # Initialize chat messages
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Suggested questions (only show if no messages yet)
    if len(st.session_state.chat_messages) == 0:
        suggested = display_suggested_questions()
        if suggested:
            process_user_message(client, suggested)
            st.rerun()
    
    # Chat container
    chat_container = st.container(height=400)
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("💬 Nhập câu hỏi của bạn về video...")
    
    if user_input:
        process_user_message(client, user_input)
        st.rerun()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col2:
        if st.session_state.chat_messages:
            # Export chat history
            chat_export = "\n\n".join([
                f"{'👤 Bạn' if m['role'] == 'user' else '🤖 AI'}: {m['content']}"
                for m in st.session_state.chat_messages
            ])
            st.download_button(
                "📥 Tải lịch sử chat",
                data=chat_export,
                file_name="chat_history.txt",
                mime="text/plain",
                use_container_width=True
            )


def process_user_message(client, user_message: str):
    """
    Xử lý tin nhắn của người dùng và tạo response.
    """
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Generate response
    with st.spinner("🤔 Đang suy nghĩ..."):
        response = generate_chatbot_response(client, user_message)
    
    # Add assistant message
    st.session_state.chat_messages.append({
        "role": "assistant", 
        "content": response
    })


# Legacy function for backward compatibility
def display_chat(client):
    """Display the chat interface (legacy support)."""
    display_chat_enhanced(client)
