from groq import Groq
import streamlit as st

client = None  # This should be set in your main app.py after loading the API key

prompt_template = """Summarize the given YouTube video transcript in bullet points, focusing only on the most important information. The summary should be clear, concise, and within 250 words. Please summarize it in {language}."""

# Giới hạn ký tự transcript để tránh vượt token limit
MAX_TRANSCRIPT_LENGTH = 15000  # ~4000 tokens

def truncate_transcript(transcript_text, max_length=MAX_TRANSCRIPT_LENGTH):
    """Cắt transcript nếu quá dài để tránh vượt token limit."""
    if len(transcript_text) > max_length:
        # Cắt và thêm thông báo
        truncated = transcript_text[:max_length]
        # Tìm vị trí kết thúc câu gần nhất
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.8:
            truncated = truncated[:last_period + 1]
        return truncated + "\n\n[Transcript đã được rút gọn do quá dài]"
    return transcript_text

def generate_llama3_content(client, transcript_text, prompt, language):
    """Tạo bản tóm tắt sử dụng Groq API."""
    formatted_prompt = prompt.format(language=language)
    
    # Cắt transcript nếu quá dài
    truncated_transcript = truncate_transcript(transcript_text)
    
    try:
        completion = client.chat.completions.create(
            # Sử dụng model mới nhất của Groq (2024-2025)
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": formatted_prompt + "\n\nTranscript:\n" + truncated_transcript
                }
            ],
            temperature=0.7,  # Giảm temperature để output ổn định hơn
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        
        summary = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                summary += chunk.choices[0].delta.content
        
        return summary
        
    except Exception as e:
        error_msg = str(e)
        # Xử lý các lỗi phổ biến
        if "rate_limit" in error_msg.lower():
            st.error("⚠️ Đã vượt quá giới hạn API. Vui lòng đợi vài phút và thử lại.")
        elif "invalid_api_key" in error_msg.lower():
            st.error("❌ API Key không hợp lệ. Vui lòng kiểm tra lại.")
        elif "model" in error_msg.lower():
            st.error("❌ Model không khả dụng. Đang thử model dự phòng...")
            # Thử với model dự phòng
            return generate_with_fallback_model(client, formatted_prompt, truncated_transcript)
        else:
            st.error(f"❌ Lỗi API: {error_msg}")
        return None

def generate_with_fallback_model(client, prompt, transcript):
    """Sử dụng model dự phòng nếu model chính không khả dụng."""
    fallback_models = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    
    for model in fallback_models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt + "\n\nTranscript:\n" + transcript}],
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
            
            summary = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    summary += chunk.choices[0].delta.content
            
            st.success(f"✅ Đã sử dụng model dự phòng: {model}")
            return summary
            
        except Exception:
            continue
    
    st.error("❌ Tất cả các model đều không khả dụng. Vui lòng thử lại sau.")
    return None


# Caching function for generating summary
@st.cache_data(show_spinner=True)
def get_summary(_client, transcript_text, language, video_id):
    """Generate and cache the summary based on the transcript."""
    # Create a unique cache key based on video ID and language to avoid regenerating the summary
    cache_key = f"summary_{video_id}_{language}"
    
    # Check if the summary is already in Streamlit's session state cache
    if cache_key in st.session_state:
        # Return the cached summary
        return st.session_state[cache_key]
    
    # Generate a new summary and cache it in session state
    summary = generate_llama3_content(_client, transcript_text, prompt_template, language)
    
    # Store the generated summary in session state for future use
    st.session_state[cache_key] = summary
    
    return summary
