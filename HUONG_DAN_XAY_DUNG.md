# 📘 HƯỚNG DẪN XÂY DỰNG PROJECT AI YOUTUBE SUMMARIZER

## Từ A đến Z - Hướng dẫn chi tiết xây dựng ứng dụng tóm tắt video YouTube với AI

---

## 📑 Mục Lục

1. [Tổng Quan Project](#1-tổng-quan-project)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Thiết Lập Môi Trường](#3-thiết-lập-môi-trường)
4. [Xây Dựng Từng Module](#4-xây-dựng-từng-module)
5. [Tích Hợp Mô Hình AI](#5-tích-hợp-mô-hình-ai)
6. [Giao Diện Người Dùng](#6-giao-diện-người-dùng)
7. [Caching và Tối Ưu](#7-caching-và-tối-ưu)
8. [Xử Lý Lỗi và Fallback](#8-xử-lý-lỗi-và-fallback)
9. [Triển Khai Ứng Dụng](#9-triển-khai-ứng-dụng)

---

## 1. Tổng Quan Project

### 1.1 Mục Đích

Đây là ứng dụng web giúp người dùng:
- **Tóm tắt** nội dung video YouTube bằng AI
- **Trò chuyện** với AI về nội dung video
- **Tạo câu hỏi trắc nghiệm** (Quiz) để kiểm tra kiến thức

### 1.2 Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Mục đích |
|------------|-----------|----------|
| **Frontend** | Streamlit | Framework UI Python |
| **AI/LLM** | Groq API + LLaMA 3.3-70B | Xử lý ngôn ngữ tự nhiên |
| **Trích xuất phụ đề** | yt-dlp | Lấy subtitle từ YouTube |
| **Parse HTML** | BeautifulSoup4 | Xử lý HTML |
| **HTTP Requests** | requests | Gọi API |
| **Environment** | python-dotenv | Quản lý biến môi trường |

### 1.3 Luồng Hoạt Động Chính

```
Người dùng nhập URL video
        ↓
Kiểm tra URL hợp lệ (url_validation.py)
        ↓
Trích xuất phụ đề (yt-dlp)
        ↓
Gửi lên Groq API với model LLaMA 3.3-70B
        ↓
Nhận kết quả và hiển thị
        ↓
Cho phép Chat hoặc Tạo Quiz
```

---

## 2. Kiến Trúc Hệ Thống

### 2.1 Cấu Trúc Thư Mục

```
ai-youtube-summarizer/
│
├── 📄 app.py                      # File chính - điều phối toàn bộ ứng dụng
├── 📄 requirements.txt            # Danh sách thư viện cần cài
├── 📄 .env                        # Biến môi trường (API Key)
│
├── 📂 components/                 # Các component UI
│   ├── 📄 __init__.py            # Đánh dấu là Python package
│   ├── 📄 chatbot.py             # Module chat AI
│   ├── 📄 quiz_display.py        # Module hiển thị quiz
│   ├── 📄 intro.py               # Màn hình giới thiệu
│   ├── 📄 sidebar.py             # Thanh sidebar (nhập API Key)
│   └── 📄 url_validation.py      # Kiểm tra URL YouTube
│
├── 📂 utils/                      # Các hàm xử lý logic
│   ├── 📄 __init__.py
│   ├── 📄 summarization.py       # Tạo bản tóm tắt với AI
│   ├── 📄 quiz_generator.py      # Tạo câu hỏi trắc nghiệm
│   └── 📄 youtube_transcript.py  # Trích xuất phụ đề (nếu có)
│
├── 📂 config/                     # Cấu hình
│   ├── 📄 __init__.py
│   └── 📄 settings.py            # Load API key
│
└── 📂 styles/                     # CSS styles
    ├── 📄 __init__.py
    └── 📄 styles.py              # Custom CSS cho UI
```

### 2.2 Sơ Đồ Tương Tác Giữa Các Module

```
                    ┌─────────────────────────────────┐
                    │           app.py                │
                    │     (Điều phối chính)           │
                    └─────────────┬───────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│ components/   │       │    utils/     │       │   config/     │
│ - sidebar.py  │       │ - summarize   │       │ - settings.py │
│ - chatbot.py  │       │ - quiz_gen    │       └───────────────┘
│ - quiz_disp   │       └───────────────┘
│ - url_valid   │               │
└───────────────┘               ▼
                        ┌───────────────┐
                        │   Groq API    │
                        │ (LLaMA 3.3)   │
                        └───────────────┘
```

---

## 3. Thiết Lập Môi Trường

### 3.1 Bước 1: Tạo Thư Mục Project

```bash
mkdir ai-youtube-summarizer
cd ai-youtube-summarizer
```

### 3.2 Bước 2: Tạo Môi Trường Ảo Python

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Tại sao dùng môi trường ảo?**
- Cách ly các thư viện riêng cho từng project
- Tránh xung đột phiên bản giữa các project
- Dễ dàng quản lý và tái tạo môi trường

### 3.3 Bước 3: Tạo File requirements.txt

```txt
yt-dlp
streamlit
groq
python-dotenv
pathlib
pyperclip
beautifulsoup4
requests
```

**Giải thích từng thư viện:**

| Thư viện | Mục đích |
|----------|----------|
| `yt-dlp` | Trích xuất phụ đề và thông tin video YouTube |
| `streamlit` | Framework tạo giao diện web nhanh chóng |
| `groq` | Client để gọi Groq API (chạy model LLaMA) |
| `python-dotenv` | Đọc biến môi trường từ file .env |
| `pathlib` | Xử lý đường dẫn file |
| `pyperclip` | Copy text vào clipboard |
| `beautifulsoup4` | Parse HTML để lấy tiêu đề video |
| `requests` | Gửi HTTP requests |

### 3.4 Bước 4: Cài Đặt Thư Viện

```bash
pip install -r requirements.txt
```

### 3.5 Bước 5: Tạo File .env

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Lấy API Key từ đâu?**
1. Truy cập https://console.groq.com/keys
2. Đăng ký tài khoản (miễn phí)
3. Tạo API Key mới
4. Copy và dán vào file .env

⚠️ **Lưu ý bảo mật:** Không commit file .env lên Git!

---

## 4. Xây Dựng Từng Module

### 4.1 Module Config (config/settings.py)

**Mục đích:** Load API key từ biến môi trường

```python
import os
from dotenv import load_dotenv

def load_api_key():
    """Load API key từ file .env hoặc biến môi trường."""
    load_dotenv()  # Đọc file .env
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API Key not found. Please set it in your environment.")
    return api_key
```

**Giải thích:**
- `load_dotenv()` đọc tất cả biến trong file .env và load vào environment
- `os.getenv("GROQ_API_KEY")` lấy giá trị của biến GROQ_API_KEY
- Nếu không tìm thấy → raise lỗi để người dùng biết

---

### 4.2 Module Kiểm Tra URL (components/url_validation.py)

**Mục đích:** Xác thực URL có phải YouTube hay không

```python
import re

def is_valid_youtube_url(url):
    """
    Kiểm tra URL có phải link YouTube hợp lệ không.
    
    Hỗ trợ các format:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    """
    youtube_patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False
```

**Giải thích:**
- Sử dụng regex (Regular Expression) để match pattern URL
- Hỗ trợ nhiều format URL khác nhau của YouTube
- Trả về `True/False` để xác định URL hợp lệ

---

### 4.3 Module Tóm Tắt (utils/summarization.py)

**Mục đích:** Gọi AI để tóm tắt nội dung video

```python
from groq import Groq
import streamlit as st

# Prompt template cho việc tóm tắt
prompt_template = """Summarize the given YouTube video transcript in bullet points, 
focusing only on the most important information. The summary should be clear, 
concise, and within 250 words. Please summarize it in {language}."""

# Giới hạn độ dài transcript để tránh vượt token limit
MAX_TRANSCRIPT_LENGTH = 15000  # ~4000 tokens

def truncate_transcript(transcript_text, max_length=MAX_TRANSCRIPT_LENGTH):
    """Cắt transcript nếu quá dài để tránh vượt token limit của API."""
    if len(transcript_text) > max_length:
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
    truncated_transcript = truncate_transcript(transcript_text)
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Model LLaMA 3.3 70B
            messages=[
                {
                    "role": "user",
                    "content": formatted_prompt + "\n\nTranscript:\n" + truncated_transcript
                }
            ],
            temperature=0.7,    # Độ sáng tạo (0-1)
            max_tokens=1024,    # Số token tối đa cho output
            top_p=1,
            stream=True,        # Streaming response
        )
        
        # Nhận response theo từng chunk (streaming)
        summary = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                summary += chunk.choices[0].delta.content
        
        return summary
        
    except Exception as e:
        # Xử lý lỗi và thử model dự phòng
        error_msg = str(e)
        if "rate_limit" in error_msg.lower():
            st.error("⚠️ Đã vượt quá giới hạn API. Vui lòng đợi vài phút.")
        elif "model" in error_msg.lower():
            return generate_with_fallback_model(client, formatted_prompt, truncated_transcript)
        return None
```

**Giải thích chi tiết:**

1. **Prompt Template:**
   - Template được thiết kế để AI tóm tắt theo dạng bullet points
   - Giới hạn 250 từ để output gọn gàng
   - Hỗ trợ đa ngôn ngữ qua biến `{language}`

2. **Truncate Transcript:**
   - API có giới hạn token (~4000 tokens cho input)
   - Cắt transcript thông minh tại cuối câu để không mất ngữ nghĩa

3. **Streaming Response:**
   - `stream=True` cho phép nhận response theo từng phần
   - Giúp hiển thị kết quả nhanh hơn, UX tốt hơn

4. **Parameters quan trọng:**
   - `temperature=0.7`: Cân bằng giữa sáng tạo và chính xác
   - `max_tokens=1024`: Đủ dài cho bản tóm tắt chi tiết

---

### 4.4 Module Quiz Generator (utils/quiz_generator.py)

**Mục đích:** Tạo câu hỏi trắc nghiệm từ nội dung video

```python
import json
import re
import streamlit as st

# Prompt template để tạo quiz
QUIZ_PROMPT_TEMPLATE = """Dựa trên nội dung tóm tắt video sau:

{summary}

Hãy tạo {num_questions} câu hỏi trắc nghiệm bằng tiếng {language} với độ khó {difficulty}.

YÊU CẦU:
1. Mỗi câu hỏi có 4 đáp án A, B, C, D
2. Chỉ có 1 đáp án đúng
3. Câu hỏi phải liên quan trực tiếp đến nội dung video
4. Giải thích ngắn gọn tại sao đáp án đó đúng

QUAN TRỌNG: Trả về CHÍNH XÁC theo format JSON sau:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Nội dung câu hỏi?",
            "options": ["A. Đáp án A", "B. Đáp án B", "C. Đáp án C", "D. Đáp án D"],
            "correct": "A",
            "explanation": "Giải thích ngắn gọn"
        }}
    ]
}}
"""

def generate_quiz(client, summary: str, num_questions: int = 5, 
                  difficulty: str = "medium", language: str = "Việt") -> dict:
    """
    Tạo quiz từ nội dung tóm tắt video.
    """
    prompt = QUIZ_PROMPT_TEMPLATE.format(
        summary=summary,
        num_questions=num_questions,
        difficulty=difficulty,
        language=language
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia tạo câu hỏi trắc nghiệm giáo dục. Luôn trả về JSON hợp lệ."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,  # Cần nhiều token hơn cho quiz dài
        )
        
        response_text = completion.choices[0].message.content
        quiz_data = parse_quiz_response(response_text)
        
        return quiz_data
        
    except Exception as e:
        st.error(f"❌ Lỗi tạo quiz: {str(e)}")
        return None


def parse_quiz_response(response_text: str) -> dict:
    """
    Parse JSON từ response của AI.
    Xử lý các trường hợp AI trả về text kèm JSON.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Tìm JSON trong response bằng regex
    json_patterns = [
        r'\{[\s\S]*"questions"[\s\S]*\}',  # Tìm object có "questions"
        r'```json\s*([\s\S]*?)\s*```',      # Tìm trong code block
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response_text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None
```

**Giải thích chi tiết:**

1. **System Prompt:**
   - Định nghĩa AI là "chuyên gia tạo câu hỏi"
   - Yêu cầu trả về JSON hợp lệ

2. **Format JSON nghiêm ngặt:**
   - Mỗi câu hỏi có: id, question, options, correct, explanation
   - 4 đáp án A, B, C, D
   - Có giải thích cho từng câu

3. **Parse Response:**
   - AI đôi khi trả về text + JSON
   - Sử dụng regex để tìm và extract JSON
   - Fallback nếu parse thất bại

---

### 4.5 Module Chatbot (components/chatbot.py)

**Mục đích:** Chat AI về nội dung video

```python
import streamlit as st
from groq import Groq

# System prompt cho chatbot
CHATBOT_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh, thân thiện và hữu ích. 
Bạn có nhiệm vụ giúp người dùng hiểu sâu hơn về nội dung video YouTube.

NGUYÊN TẮC:
1. Trả lời dựa trên nội dung video đã được tóm tắt
2. Nếu câu hỏi nằm ngoài nội dung video, thông báo lịch sự
3. Sử dụng ngôn ngữ dễ hiểu, thân thiện
4. Có thể đưa ra ví dụ minh họa khi cần
5. Trả lời bằng tiếng Việt

NỘI DUNG VIDEO ĐÃ TÓM TẮT:
{summary}
"""

def generate_chatbot_response(client, user_question, use_context=True):
    """
    Tạo câu trả lời từ chatbot.
    """
    summary = st.session_state.get('follow_up_summary', "")
    
    if not summary and use_context:
        return "⚠️ Chưa có bản tóm tắt video. Vui lòng tạo bản tóm tắt trước!"
    
    # Build messages với conversation history
    messages = []
    
    # System message với context từ summary
    if use_context and summary:
        system_content = CHATBOT_SYSTEM_PROMPT.format(summary=summary)
        messages.append({"role": "system", "content": system_content})
    
    # Thêm lịch sử chat (giữ 10 tin nhắn gần nhất)
    history = st.session_state.get('chat_messages', [])[-10:]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Thêm câu hỏi hiện tại
    messages.append({"role": "user", "content": user_question})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            stream=True,
        )
        
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
        
        return response
        
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"
```

**Giải thích:**

1. **Context-Aware:**
   - Chatbot biết nội dung video thông qua summary
   - Trả lời dựa trên ngữ cảnh cụ thể

2. **Conversation History:**
   - Lưu lịch sử 10 tin nhắn gần nhất
   - Giúp AI hiểu ngữ cảnh cuộc hội thoại

3. **Role-based Messages:**
   - `system`: Định nghĩa behavior của AI
   - `user`: Tin nhắn từ người dùng
   - `assistant`: Câu trả lời của AI

---

## 5. Tích Hợp Mô Hình AI

### 5.1 Các Model Sử Dụng

| Model | Mục đích | Đặc điểm |
|-------|----------|----------|
| **llama-3.3-70b-versatile** | Model chính | 70 tỷ parameters, đa năng |
| **llama-3.1-70b-versatile** | Fallback 1 | Phiên bản trước, ổn định |
| **llama-3.1-8b-instant** | Fallback 2 | Nhẹ, nhanh, cho task đơn giản |
| **mixtral-8x7b-32768** | Fallback 3 | Model backup khi cần |

### 5.2 Cơ Chế Chuyển Đổi Model (Fallback)

```python
def generate_with_fallback_model(client, prompt, transcript):
    """Sử dụng model dự phòng nếu model chính không khả dụng."""
    fallback_models = [
        "llama-3.1-70b-versatile",   # Fallback 1
        "llama-3.1-8b-instant",       # Fallback 2 (nhanh hơn)
        "mixtral-8x7b-32768"          # Fallback 3
    ]
    
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
            continue  # Thử model tiếp theo
    
    st.error("❌ Tất cả các model đều không khả dụng.")
    return None
```

**Tại sao cần Fallback?**
- API có thể bị quá tải (rate limit)
- Model cụ thể có thể đang bảo trì
- Đảm bảo ứng dụng luôn hoạt động

### 5.3 Cách Gọi API Groq

```python
from groq import Groq

# Khởi tạo client
client = Groq(api_key="your_api_key")

# Gọi API
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Bạn là trợ lý AI hữu ích."},
        {"role": "user", "content": "Xin chào!"}
    ],
    temperature=0.7,      # 0 = chính xác, 1 = sáng tạo
    max_tokens=1024,      # Độ dài tối đa output
    top_p=1,              # Nucleus sampling
    stream=True,          # Nhận response theo chunk
)
```

### 5.4 Giải Thích Các Tham Số

| Tham số | Giá trị | Ý nghĩa |
|---------|---------|---------|
| `temperature` | 0.0 - 1.0 | Độ sáng tạo. 0 = deterministic, 1 = random |
| `max_tokens` | int | Số token tối đa cho output |
| `top_p` | 0.0 - 1.0 | Nucleus sampling threshold |
| `stream` | bool | True = nhận response từng phần |
| `stop` | list | Chuỗi để dừng generate |

---

## 6. Giao Diện Người Dùng

### 6.1 Cấu Trúc App Chính (app.py)

```python
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="🎬",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Session State - Lưu trạng thái qua các lần rerun
def init_session_state():
    defaults = {
        "accepted_terms": False,       # Đã đồng ý điều khoản
        "cached_summary": None,        # Bản tóm tắt đã cache
        "quiz_data": None,             # Dữ liệu quiz
        "chat_messages": [],           # Lịch sử chat
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Layout chính với Tabs
if st.session_state.accepted_terms and client:
    # Input URL
    youtube_link = st.text_input("🔗 Nhập URL Video YouTube:")
    
    if youtube_link:
        # Hiển thị video
        st.video(youtube_link)
        
        # 3 Tabs
        tab1, tab2, tab3 = st.tabs([
            "📝 Tóm Tắt",
            "💬 Trò Chuyện", 
            "📚 Quiz Học Tập"
        ])
        
        with tab1:
            display_summary_tab(client, youtube_link, selected_language)
        
        with tab2:
            display_chat_enhanced(client)
        
        with tab3:
            display_quiz_generator(client)
```

### 6.2 Session State

**Session State là gì?**
- Streamlit rerun toàn bộ script mỗi khi có interaction
- Session State lưu giữ dữ liệu qua các lần rerun
- Giống như "memory" của ứng dụng

```python
# Lưu vào session state
st.session_state.cached_summary = "Nội dung tóm tắt..."

# Đọc từ session state
summary = st.session_state.get('cached_summary', None)

# Kiểm tra tồn tại
if 'cached_summary' in st.session_state:
    print("Đã có summary")
```

### 6.3 Các Component UI

**Sidebar (thanh bên):**
```python
with st.sidebar:
    st.image("logo.png")
    api_key = st.text_input("🔑 API Key:", type="password")
    st.divider()
    st.info("Nhập Groq API Key để sử dụng")
```

**Text Input với placeholder:**
```python
youtube_link = st.text_input(
    "🔗 Nhập URL Video YouTube:",
    placeholder="https://www.youtube.com/watch?v=example",
    label_visibility="visible"
)
```

**Button với trạng thái:**
```python
if st.button("📓 Tạo Bản Tóm Tắt", type="primary", use_container_width=True):
    with st.spinner("🔄 Đang xử lý..."):
        # Logic xử lý
        pass
    st.success("✅ Hoàn thành!")
```

**Radio buttons cho quiz:**
```python
selected = st.radio(
    "Chọn đáp án:",
    options=["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"],
    index=None,  # Không chọn mặc định
)
```

---

## 7. Caching và Tối Ưu

### 7.1 Streamlit Caching

```python
@st.cache_data(show_spinner=True)
def get_summary(_client, transcript_text, language, video_id):
    """
    Cache bản tóm tắt để tránh gọi API lại.
    
    _client có dấu _ đầu để không được hash (unhashable object)
    """
    cache_key = f"summary_{video_id}_{language}"
    
    # Kiểm tra cache trong session state
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Tạo mới và cache
    summary = generate_llama3_content(_client, transcript_text, prompt_template, language)
    st.session_state[cache_key] = summary
    
    return summary
```

**Giải thích:**
- `@st.cache_data`: Decorator để cache kết quả function
- `_client`: Dấu `_` đầu cho Streamlit biết không hash parameter này
- Tiết kiệm API calls khi user refresh trang

### 7.2 Cache Expiry

```python
current_time = time.time()
cache_expiry = 3600  # 1 giờ

need_regenerate = (
    st.session_state.cached_summary is None or
    current_time - st.session_state.cached_summary_timestamp > cache_expiry or
    st.session_state.current_video_url != youtube_link
)

if need_regenerate:
    # Tạo mới
    pass
else:
    # Dùng cache
    pass
```

---

## 8. Xử Lý Lỗi và Fallback

### 8.1 Các Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Xử lý |
|-----|-------------|-------|
| `rate_limit` | Vượt quota API | Chờ và retry |
| `invalid_api_key` | API key sai | Thông báo user |
| `model_not_available` | Model đang bảo trì | Chuyển fallback model |
| `token_limit` | Input quá dài | Truncate transcript |

### 8.2 Error Handling Pattern

```python
try:
    # Gọi API
    completion = client.chat.completions.create(...)
    
except Exception as e:
    error_msg = str(e).lower()
    
    if "rate_limit" in error_msg:
        st.warning("⚠️ Đã vượt giới hạn. Đợi 1 phút...")
        time.sleep(60)
        # Retry
        
    elif "invalid_api_key" in error_msg:
        st.error("❌ API Key không hợp lệ!")
        st.stop()  # Dừng ứng dụng
        
    elif "model" in error_msg:
        # Thử fallback model
        return generate_with_fallback_model(...)
        
    else:
        st.error(f"❌ Lỗi không xác định: {error_msg}")
        return None
```

### 8.3 Graceful Degradation

```python
def generate_quiz_fallback(client, summary, num_questions, difficulty, language):
    """Fallback khi không parse được JSON từ AI."""
    
    # Thử với prompt đơn giản hơn
    simple_prompt = f"Tạo {num_questions} câu hỏi. Chỉ trả về JSON."
    
    try:
        # Thử model nhẹ hơn
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Model nhanh hơn
            messages=[{"role": "user", "content": simple_prompt}],
            temperature=0.5,  # Ít random hơn
        )
        return parse_quiz_response(completion.choices[0].message.content)
        
    except Exception:
        # Trả về quiz mẫu nếu thất bại hoàn toàn
        return {
            "questions": [{
                "id": 1,
                "question": "Không thể tạo quiz. Vui lòng thử lại.",
                "options": ["A. Thử lại", "B. Thử lại", "C. Thử lại", "D. Thử lại"],
                "correct": "A",
                "explanation": "Vui lòng refresh trang."
            }]
        }
```

---

## 9. Triển Khai Ứng Dụng

### 9.1 Chạy Local

```bash
# Kích hoạt môi trường ảo
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Chạy ứng dụng
python -m streamlit run app.py

# Mở trình duyệt
# http://localhost:8501
```

### 9.2 Deploy lên Streamlit Cloud

1. **Push code lên GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

2. **Cấu hình .streamlit/config.toml**
```toml
[server]
headless = true
port = 8501
enableCORS = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

3. **Deploy trên streamlit.io**
   - Truy cập https://share.streamlit.io
   - Kết nối GitHub repo
   - Cấu hình secrets (API Key)
   - Deploy!

### 9.3 Cấu Hình Secrets

Trên Streamlit Cloud, thêm secrets trong dashboard:

```toml
# .streamlit/secrets.toml (local) hoặc Dashboard (cloud)
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxx"
```

Truy cập trong code:
```python
import streamlit as st

api_key = st.secrets["GROQ_API_KEY"]
```

---

## 📚 Tổng Kết

### Quy Trình Xây Dựng Tóm Tắt

1. **Thiết lập môi trường** → Python venv + requirements.txt
2. **Config** → API key, settings
3. **Utils** → Logic xử lý (summarization, quiz_generator)
4. **Components** → UI modules (chatbot, quiz_display, sidebar)
5. **App.py** → Điều phối và kết nối tất cả
6. **Testing** → Chạy local, debug
7. **Deploy** → Streamlit Cloud

### Kỹ Thuật Quan Trọng

- **Prompt Engineering**: Viết prompt rõ ràng, có cấu trúc
- **Error Handling**: Xử lý mọi trường hợp lỗi
- **Fallback Models**: Backup khi model chính fail
- **Caching**: Tối ưu API calls và tốc độ
- **Session State**: Duy trì trạng thái ứng dụng

### Mở Rộng Trong Tương Lai

- Export PDF cho quiz và summary
- Hỗ trợ playlist YouTube
- User authentication
- Lưu lịch sử học tập
- Mobile app

---

**Tác giả:** AI YouTube Summarizer Team  
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** Tháng 2, 2026

---

*Nếu có câu hỏi, vui lòng tạo Issue trên GitHub hoặc liên hệ qua email!* 🚀
