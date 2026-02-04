"""
Summarization Module - Hỗ trợ 3 mức độ tóm tắt
"""

from groq import Groq
import streamlit as st

client = None

# ========================================
# CẤU HÌNH 3 MỨC ĐỘ TÓM TẮT
# ========================================

SUMMARY_LEVELS = {
    "quick": {
        "name": "⚡ Tóm tắt nhanh",
        "description": "~200 từ • 5-7 điểm chính • Xử lý nhanh",
        "words": 200,
        "max_tokens": 600,
        "max_transcript": 12000,
        "prompt": """Tóm tắt video YouTube sau trong khoảng 200 từ bằng {language}.
        
YÊU CẦU:
- Chỉ trích xuất 5-7 điểm chính QUAN TRỌNG NHẤT
- Mỗi điểm ngắn gọn, súc tích (1-2 câu)
- Sử dụng bullet points (•)
- Không lặp lại thông tin

FORMAT:
## 📌 Tóm tắt nhanh

• [Điểm 1]
• [Điểm 2]
...

**💡 Kết luận:** [1 câu tóm lại]
"""
    },
    
    "standard": {
        "name": "📝 Tóm tắt chuẩn",
        "description": "~500 từ • 10-15 điểm • Cân bằng",
        "words": 500,
        "max_tokens": 1200,
        "max_transcript": 18000,
        "prompt": """Tóm tắt chi tiết video YouTube sau trong khoảng 500 từ bằng {language}.
        
YÊU CẦU:
- Trích xuất 10-15 điểm quan trọng
- Giải thích ngắn gọn từng điểm
- Nhóm các điểm theo chủ đề nếu có thể
- Sử dụng bullet points và sub-bullets

FORMAT:
## 📝 Tóm tắt nội dung

### 🎯 Ý chính
• [Điểm chính 1]
• [Điểm chính 2]

### 📚 Chi tiết
• [Chi tiết 1]
  - [Giải thích]
• [Chi tiết 2]
  - [Giải thích]

### 💡 Kết luận
[Tóm tắt và nhận xét]
"""
    },
    
    "detailed": {
        "name": "📚 Tóm tắt chi tiết",
        "description": "~1500 từ • 20+ điểm • Đầy đủ nhất",
        "words": 1500,
        "max_tokens": 3500,
        "max_transcript": 28000,
        "prompt": """Tóm tắt RẤT CHI TIẾT video YouTube sau trong khoảng 1500 từ bằng {language}.
        
YÊU CẦU:
- Trích xuất TẤT CẢ thông tin quan trọng (20+ điểm)
- Giải thích đầy đủ từng điểm với ví dụ nếu có
- Tổ chức theo cấu trúc logic, phân chia sections rõ ràng
- Bao gồm các chi tiết, số liệu, ví dụ được đề cập
- Thêm nhận xét và gợi ý áp dụng

FORMAT:
## 📚 Tóm tắt chi tiết

### 📌 Tổng quan
[Giới thiệu chủ đề, bối cảnh của video]

### 🎯 Nội dung chính

#### 1. [Phần 1]
• [Điểm 1.1]: [Giải thích chi tiết]
• [Điểm 1.2]: [Giải thích chi tiết]

#### 2. [Phần 2]
• [Điểm 2.1]: [Giải thích chi tiết]
• [Điểm 2.2]: [Giải thích chi tiết]

#### 3. [Phần 3]
• [Điểm 3.1]: [Giải thích chi tiết]

### 📊 Số liệu/Ví dụ quan trọng
• [Số liệu hoặc ví dụ 1]
• [Số liệu hoặc ví dụ 2]

### 💡 Kết luận & Áp dụng
[Tóm tắt, nhận xét, và cách áp dụng vào thực tế]

### 🔗 Gợi ý tìm hiểu thêm
• [Chủ đề liên quan 1]
• [Chủ đề liên quan 2]
"""
    }
}


def truncate_transcript(transcript_text, max_length):
    """Cắt transcript nếu quá dài để tránh vượt token limit."""
    if len(transcript_text) > max_length:
        truncated = transcript_text[:max_length]
        # Tìm vị trí kết thúc câu gần nhất
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.8:
            truncated = truncated[:last_period + 1]
        return truncated + "\n\n[Transcript đã được rút gọn do quá dài]"
    return transcript_text


def generate_summary_with_level(client, transcript_text, language, level="standard"):
    """
    Tạo bản tóm tắt với mức độ chi tiết được chọn.
    
    Args:
        client: Groq client
        transcript_text: Nội dung transcript
        language: Ngôn ngữ output
        level: Mức độ chi tiết ("quick", "standard", "detailed")
    
    Returns:
        str: Bản tóm tắt
    """
    config = SUMMARY_LEVELS.get(level, SUMMARY_LEVELS["standard"])
    
    # Format prompt với ngôn ngữ
    formatted_prompt = config["prompt"].format(language=language)
    
    # Cắt transcript theo giới hạn của level
    truncated_transcript = truncate_transcript(transcript_text, config["max_transcript"])
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"Bạn là chuyên gia tóm tắt nội dung video. Luôn trả lời bằng {language} với format Markdown rõ ràng."
                },
                {
                    "role": "user",
                    "content": formatted_prompt + "\n\n--- TRANSCRIPT ---\n" + truncated_transcript
                }
            ],
            temperature=0.7,
            max_tokens=config["max_tokens"],
            top_p=1,
            stream=True,
        )
        
        summary = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                summary += chunk.choices[0].delta.content
        
        return summary
        
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower():
            st.error("⚠️ Đã vượt quá giới hạn API. Vui lòng đợi vài phút và thử lại.")
        elif "invalid_api_key" in error_msg.lower():
            st.error("❌ API Key không hợp lệ. Vui lòng kiểm tra lại.")
        elif "model" in error_msg.lower():
            st.warning("⚠️ Model chính không khả dụng. Đang thử model dự phòng...")
            return generate_with_fallback(client, formatted_prompt, truncated_transcript, config["max_tokens"])
        else:
            st.error(f"❌ Lỗi API: {error_msg}")
        return None


def generate_with_fallback(client, prompt, transcript, max_tokens):
    """Sử dụng model dự phòng nếu model chính không khả dụng."""
    fallback_models = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    
    for model in fallback_models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt + "\n\nTranscript:\n" + transcript}],
                temperature=0.7,
                max_tokens=max_tokens,
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


# ========================================
# LEGACY SUPPORT - Giữ tương thích ngược
# ========================================

prompt_template = """Summarize the given YouTube video transcript in bullet points, focusing only on the most important information. The summary should be clear, concise, and within 250 words. Please summarize it in {language}."""

MAX_TRANSCRIPT_LENGTH = 15000

def generate_llama3_content(client, transcript_text, prompt, language):
    """Legacy function - Sử dụng generate_summary_with_level với level standard."""
    return generate_summary_with_level(client, transcript_text, language, "standard")


@st.cache_data(show_spinner=True)
def get_summary(_client, transcript_text, language, video_id, level="standard"):
    """Generate and cache the summary based on the transcript and level."""
    cache_key = f"summary_{video_id}_{language}_{level}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    summary = generate_summary_with_level(_client, transcript_text, language, level)
    
    st.session_state[cache_key] = summary
    
    return summary


def get_level_info(level):
    """Lấy thông tin về một level cụ thể."""
    return SUMMARY_LEVELS.get(level, SUMMARY_LEVELS["standard"])


def get_all_levels():
    """Lấy tất cả các levels."""
    return SUMMARY_LEVELS
