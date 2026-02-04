# 📘 HƯỚNG DẪN XÂY DỰNG PROJECT AI YOUTUBE SUMMARIZER

## Từ A đến Z - Hướng dẫn chi tiết xây dựng ứng dụng tóm tắt video YouTube với AI

---

## 📑 Mục Lục

1. [Tổng Quan Project](#1-tổng-quan-project)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Thiết Lập Môi Trường](#3-thiết-lập-môi-trường)
4. [Module Tóm Tắt 3 Mức Độ](#4-module-tóm-tắt-3-mức-độ)
5. [Module Quiz Generator](#5-module-quiz-generator)
6. [Module Mind Map](#6-module-mind-map)
7. [Module Chatbot](#7-module-chatbot)
8. [Giao Diện Người Dùng](#8-giao-diện-người-dùng)
9. [Xử Lý Lỗi và Tối Ưu](#9-xử-lý-lỗi-và-tối-ưu)

---

## 1. Tổng Quan Project

### 1.1 Mục Đích

Đây là ứng dụng web giúp người dùng:
- **Tóm tắt** nội dung video YouTube với 3 mức độ chi tiết
- **Trò chuyện** với AI về nội dung video
- **Tạo câu hỏi trắc nghiệm** (Quiz) để kiểm tra kiến thức
- **Tạo Mind Map** sơ đồ tư duy từ nội dung video

### 1.2 Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Mục đích |
|------------|-----------|----------|
| **Frontend** | Streamlit | Framework UI Python |
| **AI/LLM** | Groq API + LLaMA 3.3-70B | Xử lý ngôn ngữ tự nhiên |
| **Trích xuất phụ đề** | yt-dlp | Lấy subtitle từ YouTube |
| **Mind Map** | Markmap.js | Render sơ đồ tư duy interactive |
| **Parse HTML** | BeautifulSoup4 | Xử lý HTML |
| **HTTP Requests** | requests | Gọi API |

### 1.3 Luồng Hoạt Động Chính

```
Người dùng nhập URL video
         ↓
Kiểm tra URL hợp lệ (url_validation.py)
         ↓
Trích xuất phụ đề (yt-dlp)
         ↓
Chọn mức độ tóm tắt (⚡ Nhanh / 📝 Chuẩn / 📚 Chi tiết)
         ↓
Gửi lên Groq API với model LLaMA 3.3-70B
         ↓
Nhận kết quả và hiển thị
         ↓
Cho phép: Chat / Quiz / Mind Map
```

---

## 2. Kiến Trúc Hệ Thống

### 2.1 Cấu Trúc Thư Mục Mới

```
ai-youtube-summarizer/
│
├── 📄 app.py                      # File chính - 4 Tabs UI
├── 📄 requirements.txt            # Danh sách thư viện
├── 📄 .env                        # Biến môi trường (API Key)
│
├── 📂 components/                 # Các component UI
│   ├── 📄 __init__.py
│   ├── 📄 chatbot.py             # 💬 Module chat AI nâng cao
│   ├── 📄 quiz_display.py        # 📚 Module hiển thị quiz
│   ├── 📄 mindmap_display.py     # 🧠 Module hiển thị mind map
│   ├── 📄 intro.py               # 👋 Màn hình giới thiệu
│   ├── 📄 sidebar.py             # Thanh sidebar
│   └── 📄 url_validation.py      # Kiểm tra URL YouTube
│
├── 📂 utils/                      # Các hàm xử lý logic
│   ├── 📄 __init__.py
│   ├── 📄 summarization.py       # 🤖 Tóm tắt 3 mức độ
│   ├── 📄 quiz_generator.py      # 📚 Tạo câu hỏi trắc nghiệm
│   └── 📄 mindmap_generator.py   # 🧠 Tạo cấu trúc mind map
│
├── 📂 config/                     # Cấu hình
│   └── 📄 settings.py
│
└── 📂 styles/                     # CSS styles
    └── 📄 styles.py
```

### 2.2 Sơ Đồ 4 Tabs

```
┌─────────────────────────────────────────────────────────────────────┐
│                       🎬 AI YouTube Summarizer                       │
├─────────────────────────────────────────────────────────────────────┤
│  [🔗 URL Video]                               [🌐 Ngôn ngữ ▼]       │
├─────────────────────────────────────────────────────────────────────┤
│  [📺 Video Player]                                                   │
├─────────────────────────────────────────────────────────────────────┤
│  📝 Tóm Tắt  │  💬 Trò Chuyện  │  📚 Quiz  │  🧠 Mind Map          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                    [Nội dung Tab hiện tại]                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Thiết Lập Môi Trường

### 3.1 Cài Đặt

```bash
# Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate  # Windows

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3.2 File requirements.txt

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

### 3.3 File .env

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 4. Module Tóm Tắt 3 Mức Độ

### 4.1 Cấu Hình 3 Mức Độ (utils/summarization.py)

```python
SUMMARY_LEVELS = {
    "quick": {
        "name": "⚡ Tóm tắt nhanh",
        "description": "~200 từ • 5-7 điểm chính",
        "words": 200,
        "max_tokens": 600,
        "max_transcript": 12000,  # ~15-20 phút video
        "prompt": """Tóm tắt video YouTube sau trong khoảng 200 từ...
        
YÊU CẦU:
- Chỉ trích xuất 5-7 điểm chính QUAN TRỌNG NHẤT
- Mỗi điểm ngắn gọn, súc tích (1-2 câu)

FORMAT:
## 📌 Tóm tắt nhanh
• [Điểm 1]
• [Điểm 2]
...
💡 Kết luận: [1 câu tóm lại]
"""
    },
    
    "standard": {
        "name": "📝 Tóm tắt chuẩn",
        "description": "~500 từ • 10-15 điểm",
        "words": 500,
        "max_tokens": 1200,
        "max_transcript": 18000,  # ~25-35 phút video
        "prompt": """Tóm tắt chi tiết video YouTube sau trong khoảng 500 từ...
        
YÊU CẦU:
- Trích xuất 10-15 điểm quan trọng
- Nhóm các điểm theo chủ đề

FORMAT:
## 📝 Tóm tắt nội dung
### 🎯 Ý chính
### 📚 Chi tiết
### 💡 Kết luận
"""
    },
    
    "detailed": {
        "name": "📚 Tóm tắt chi tiết",
        "description": "~1500 từ • 20+ điểm",
        "words": 1500,
        "max_tokens": 3500,
        "max_transcript": 28000,  # ~40-50 phút video
        "prompt": """Tóm tắt RẤT CHI TIẾT video YouTube sau trong khoảng 1500 từ...
        
YÊU CẦU:
- Trích xuất TẤT CẢ thông tin quan trọng (20+ điểm)
- Giải thích đầy đủ với ví dụ

FORMAT:
## 📚 Tóm tắt chi tiết
### 📌 Tổng quan
### 🎯 Nội dung chính (nhiều sections)
### 📊 Số liệu/Ví dụ
### 💡 Kết luận & Áp dụng
### 🔗 Gợi ý tìm hiểu thêm
"""
    }
}
```

### 4.2 Hàm Tạo Tóm Tắt

```python
def generate_summary_with_level(client, transcript_text, language, level="standard"):
    """
    Tạo bản tóm tắt với mức độ chi tiết được chọn.
    """
    config = SUMMARY_LEVELS.get(level, SUMMARY_LEVELS["standard"])
    
    # Format prompt với ngôn ngữ
    formatted_prompt = config["prompt"].format(language=language)
    
    # Cắt transcript theo giới hạn của level
    truncated_transcript = truncate_transcript(transcript_text, config["max_transcript"])
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"Bạn là chuyên gia tóm tắt nội dung video."
            },
            {
                "role": "user",
                "content": formatted_prompt + "\n\n--- TRANSCRIPT ---\n" + truncated_transcript
            }
        ],
        temperature=0.7,
        max_tokens=config["max_tokens"],
        stream=True,
    )
    
    # ... xử lý response
```

### 4.3 Giới Hạn Video

| Mức độ | max_transcript | Video ước tính |
|--------|----------------|----------------|
| ⚡ Nhanh | 12,000 ký tự | ~15-20 phút |
| 📝 Chuẩn | 18,000 ký tự | ~25-35 phút |
| 📚 Chi tiết | 28,000 ký tự | ~40-50 phút |

**Công thức ước tính:**
```
Tốc độ nói trung bình: ~150 từ/phút
1 từ ≈ 6 ký tự (bao gồm khoảng trắng)
→ ~900 ký tự/phút
→ 18,000 ký tự ÷ 900 ≈ 20-35 phút
```

---

## 5. Module Quiz Generator

### 5.1 Tạo Quiz (utils/quiz_generator.py)

```python
QUIZ_PROMPT_TEMPLATE = """Dựa trên nội dung tóm tắt video sau:

{summary}

Hãy tạo {num_questions} câu hỏi trắc nghiệm với độ khó {difficulty}.

QUAN TRỌNG: Trả về CHÍNH XÁC theo format JSON:
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

DIFFICULTY_LEVELS = {
    "easy": "Dễ - Câu hỏi cơ bản",
    "medium": "Trung bình - Cần hiểu nội dung",
    "hard": "Khó - Yêu cầu phân tích"
}
```

### 5.2 Hiển Thị Quiz (components/quiz_display.py)

```python
def display_quiz_generator(client):
    """Hiển thị giao diện tạo và làm quiz."""
    
    # Cấu hình
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.selectbox("Số câu:", [5, 10, 15, 20])
    with col2:
        difficulty = st.selectbox("Độ khó:", ["easy", "medium", "hard"])
    
    # Tạo quiz
    if st.button("🎯 Tạo Quiz"):
        quiz_data = generate_quiz(client, summary, num_questions, difficulty)
        st.session_state.quiz_data = quiz_data
    
    # Hiển thị câu hỏi
    if st.session_state.quiz_data:
        for q in quiz_data["questions"]:
            st.markdown(f"**Câu {q['id']}:** {q['question']}")
            selected = st.radio("Chọn đáp án:", q["options"], key=f"q_{q['id']}")
    
    # Nộp bài và xem kết quả
    if st.button("✅ Nộp bài"):
        stats = get_quiz_stats(answers, quiz_data)
        st.metric("Điểm số", f"{stats['percentage']}%")
```

---

## 6. Module Mind Map

### 6.1 Tạo Cấu Trúc Mind Map (utils/mindmap_generator.py)

```python
MINDMAP_PROMPT_TEMPLATE = """Dựa trên nội dung tóm tắt video sau:

{summary}

Hãy phân tích và tạo cấu trúc Mind Map với format Markdown:

# [Tiêu đề chính - Chủ đề video]

## [Nhánh 1]
- Chi tiết 1.1
- Chi tiết 1.2

## [Nhánh 2]
- Chi tiết 2.1
- Chi tiết 2.2

YÊU CẦU:
- Tối đa 5-7 nhánh chính
- Mỗi nhánh 2-5 chi tiết
"""

def generate_mindmap_markdown(client, summary: str) -> str:
    """Tạo Mind Map dạng Markdown từ nội dung tóm tắt."""
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Bạn là chuyên gia tạo Mind Map giáo dục."
            },
            {
                "role": "user",
                "content": MINDMAP_PROMPT_TEMPLATE.format(summary=summary)
            }
        ],
        temperature=0.7,
        max_tokens=2000,
    )
    
    return completion.choices[0].message.content
```

### 6.2 Render Mind Map với Markmap

```python
def get_markmap_html(markdown: str, height: int = 600) -> str:
    """Tạo HTML với Markmap để render Mind Map interactive."""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html, body {{
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }}
            .container {{
                width: 100%;
                height: {height}px;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.15.4"></script>
    </head>
    <body>
        <div class="container">
            <div class="markmap">
                <script type="text/template">
{markdown}
                </script>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
```

### 6.3 Hiển Thị Mind Map (components/mindmap_display.py)

```python
import streamlit.components.v1 as components

def display_mindmap_generator(client):
    """Hiển thị giao diện tạo và xem Mind Map."""
    
    st.markdown("### 🧠 Mind Map - Sơ Đồ Tư Duy")
    
    if st.button("🧠 Tạo Mind Map", type="primary"):
        markdown = generate_mindmap_markdown(client, summary)
        st.session_state.mindmap_markdown = markdown
    
    if st.session_state.mindmap_markdown:
        # Render với Markmap
        html = get_markmap_html(st.session_state.mindmap_markdown, 550)
        components.html(html, height=570)
        
        # Export options
        st.download_button("📄 Tải Markdown", markdown, "mindmap.md")
        st.download_button("🌐 Tải HTML", html, "mindmap.html")
```

---

## 7. Module Chatbot

### 7.1 Chatbot Nâng Cao (components/chatbot.py)

```python
CHATBOT_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh.
Bạn có nhiệm vụ giúp người dùng hiểu sâu hơn về nội dung video YouTube.

NGUYÊN TẮC:
1. Trả lời dựa trên nội dung video đã được tóm tắt
2. Sử dụng ngôn ngữ dễ hiểu, thân thiện
3. Có thể đưa ra ví dụ minh họa
4. Trả lời bằng tiếng Việt

NỘI DUNG VIDEO:
{summary}
"""

SUGGESTED_QUESTIONS = [
    "📝 Tóm tắt lại ngắn gọn trong 3 câu",
    "🔑 Những điểm chính quan trọng nhất là gì?",
    "💡 Giải thích chi tiết hơn về chủ đề này",
    "📚 Có thể áp dụng kiến thức này như thế nào?",
    "❓ Còn điều gì tôi cần biết thêm không?",
]

def generate_chatbot_response(client, user_question):
    """Tạo câu trả lời với context từ video."""
    
    summary = st.session_state.get('follow_up_summary', "")
    
    messages = [
        {"role": "system", "content": CHATBOT_SYSTEM_PROMPT.format(summary=summary)}
    ]
    
    # Thêm lịch sử chat (10 tin gần nhất)
    history = st.session_state.get('chat_messages', [])[-10:]
    messages.extend(history)
    
    # Thêm câu hỏi hiện tại
    messages.append({"role": "user", "content": user_question})
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
        stream=True,
    )
    
    # ... xử lý response
```

---

## 8. Giao Diện Người Dùng

### 8.1 Cấu Trúc App Chính (app.py)

```python
import streamlit as st
from utils.summarization import get_summary, SUMMARY_LEVELS, get_level_info
from components.chatbot import display_chat_enhanced
from components.quiz_display import display_quiz_generator
from components.mindmap_display import display_mindmap_generator

st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
def init_session_state():
    defaults = {
        "accepted_terms": False,
        "cached_summary": None,
        "quiz_data": None,
        "chat_messages": [],
        "mindmap_markdown": None,
        "summary_level": "standard"  # Mức độ mặc định
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Main layout với 4 Tabs
if client and youtube_link:
    st.video(youtube_link)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Tóm Tắt",
        "💬 Trò Chuyện",
        "📚 Quiz Học Tập",
        "🧠 Mind Map"
    ])
    
    with tab1:
        display_summary_tab(client, youtube_link, selected_language)
    
    with tab2:
        display_chat_enhanced(client)
    
    with tab3:
        display_quiz_generator(client)
    
    with tab4:
        display_mindmap_generator(client)
```

### 8.2 Tab Tóm Tắt với 3 Mức Độ

```python
def display_summary_tab(client, youtube_link, selected_language):
    """Hiển thị tab Tóm tắt với 3 mức độ chi tiết."""
    
    # Chọn mức độ
    st.markdown("##### 📊 Chọn mức độ chi tiết:")
    
    level_cols = st.columns(3)
    levels = ["quick", "standard", "detailed"]
    
    for col, level in zip(level_cols, levels):
        with col:
            is_selected = st.session_state.summary_level == level
            if st.button(
                f"{level_info['name']}\n{level_info['description']}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                st.session_state.summary_level = level
                st.rerun()
    
    # Tạo tóm tắt
    if st.button("📓 Tạo Bản Tóm Tắt", type="primary"):
        current_level = st.session_state.summary_level
        summary = get_summary(client, transcript, language, video_id, current_level)
        st.session_state.follow_up_summary = summary
    
    # Hiển thị kết quả
    if st.session_state.follow_up_summary:
        st.markdown(st.session_state.follow_up_summary)
```

---

## 9. Xử Lý Lỗi và Tối Ưu

### 9.1 Fallback Models

```python
def generate_with_fallback(client, prompt, transcript, max_tokens):
    """Sử dụng model dự phòng nếu model chính không khả dụng."""
    fallback_models = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    
    for model in fallback_models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt + transcript}],
                max_tokens=max_tokens,
            )
            return completion.choices[0].message.content
        except:
            continue
    
    return None
```

### 9.2 Cache Management

```python
@st.cache_data(show_spinner=True)
def get_summary(_client, transcript_text, language, video_id, level="standard"):
    """Cache bản tóm tắt theo video_id và level."""
    cache_key = f"summary_{video_id}_{language}_{level}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    summary = generate_summary_with_level(_client, transcript_text, language, level)
    st.session_state[cache_key] = summary
    
    return summary
```

### 9.3 Error Handling

```python
try:
    completion = client.chat.completions.create(...)
except Exception as e:
    error_msg = str(e)
    
    if "rate_limit" in error_msg.lower():
        st.error("⚠️ Đã vượt quá giới hạn API. Vui lòng đợi vài phút.")
    elif "invalid_api_key" in error_msg.lower():
        st.error("❌ API Key không hợp lệ.")
    elif "model" in error_msg.lower():
        # Thử model dự phòng
        return generate_with_fallback(...)
    else:
        st.error(f"❌ Lỗi: {error_msg}")
```

---

## 📝 Tổng Kết

### Các Module Đã Xây Dựng

| Module | File | Chức năng |
|--------|------|-----------|
| Tóm tắt 3 mức | `utils/summarization.py` | Quick/Standard/Detailed |
| Quiz Generator | `utils/quiz_generator.py` | Tạo câu hỏi trắc nghiệm |
| Mind Map | `utils/mindmap_generator.py` | Tạo sơ đồ tư duy |
| Chatbot | `components/chatbot.py` | Chat AI về video |
| Quiz UI | `components/quiz_display.py` | Giao diện làm quiz |
| Mind Map UI | `components/mindmap_display.py` | Hiển thị mind map |

### Giới Hạn Kỹ Thuật

| Mức độ | Transcript | Video | max_tokens |
|--------|------------|-------|------------|
| ⚡ Nhanh | 12,000 | ~20 phút | 600 |
| 📝 Chuẩn | 18,000 | ~35 phút | 1,200 |
| 📚 Chi tiết | 28,000 | ~50 phút | 3,500 |

---

**© 2026 AI YouTube Summarizer - Hướng dẫn xây dựng chi tiết**
