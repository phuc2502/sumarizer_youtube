<div align="center">

# 🎬 AI YouTube Summarizer

### Ứng dụng tóm tắt video YouTube với AI, Trò chuyện thông minh, Quiz học tập & Mind Map

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq%20AI-F55036?style=for-the-badge)](https://groq.com)
[![LLaMA](https://img.shields.io/badge/LLaMA-3.3--70B-blueviolet?style=for-the-badge)](https://ai.meta.com/llama/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

<img src="AI_YouTube_Summarizer.png" alt="AI YouTube Summarizer Logo" width="180"/>

**Tóm tắt • Trò chuyện • Quiz • Mind Map - Tất cả trong một ứng dụng**

[🚀 Bắt đầu ngay](#-cài-đặt) • [✨ Tính năng](#-tính-năng-chính) • [📖 Hướng dẫn](#-hướng-dẫn-sử-dụng) • [🤝 Đóng góp](#-hướng-dẫn-đóng-góp)

---

</div>

## 📖 Giới thiệu

**AI YouTube Summarizer** là ứng dụng web đa năng được xây dựng trên nền tảng **Streamlit**, tích hợp sức mạnh của **LLaMA 3.3-70B** thông qua **Groq API** để mang đến trải nghiệm học tập và tiếp thu nội dung video YouTube một cách hiệu quả nhất.

### 🎯 Bốn chức năng chính trong một ứng dụng

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      🎬 AI YouTube Summarizer                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  📝 TÓM TẮT        💬 TRÒ CHUYỆN      📚 QUIZ         🧠 MIND MAP      │
│  ──────────        ─────────────      ──────          ──────────        │
│  • 3 mức độ        • Chat AI          • Trắc nghiệm   • Sơ đồ tư duy   │
│  • Đa ngôn ngữ     • Gợi ý câu hỏi    • 3 độ khó      • Interactive    │
│  • Tải xuống       • Lịch sử chat     • Giải thích    • Export đa dạng │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Tính năng chính

### 📝 Tab Tóm Tắt (3 Mức Độ Chi Tiết)

| Mức độ | Từ | Điểm chính | Thời gian | Mục đích |
|--------|-----|------------|-----------|----------|
| ⚡ **Tóm tắt nhanh** | ~200 | 5-7 | ~5 giây | Nắm ý chính nhanh |
| 📝 **Tóm tắt chuẩn** | ~500 | 10-15 | ~10 giây | Cân bằng |
| 📚 **Tóm tắt chi tiết** | ~1500 | 20+ | ~15 giây | Học sâu, đầy đủ |

**Tính năng:**
- ✅ Chọn 1 trong 3 mức độ chi tiết
- ✅ Hỗ trợ 11+ ngôn ngữ (Việt, Anh, Pháp, Đức,...)
- ✅ Format Markdown đẹp với headings và bullet points
- ✅ Cache thông minh (1 giờ)
- ✅ Tải xuống bản tóm tắt (.txt)

### 💬 Tab Trò Chuyện (Chat AI)

**Tính năng:**
- ✅ Chat AI thông minh về nội dung video
- ✅ Context-aware - Hiểu ngữ cảnh video
- ✅ 5 câu hỏi gợi ý
- ✅ Lưu lịch sử conversation
- ✅ Tải xuống lịch sử chat

### 📚 Tab Quiz Học Tập

**Tính năng:**
- ✅ Tạo câu hỏi trắc nghiệm từ AI
- ✅ 4 mức số lượng: 5, 10, 15, 20 câu
- ✅ 3 độ khó: Dễ, Trung bình, Khó
- ✅ Mỗi câu 4 đáp án A, B, C, D
- ✅ Hiển thị kết quả chi tiết
- ✅ Giải thích đáp án đúng
- ✅ Đánh giá điểm số (%, Grade)

### 🧠 Tab Mind Map

**Tính năng:**
- ✅ Tự động tạo sơ đồ tư duy từ AI
- ✅ Interactive: zoom, pan, expand/collapse
- ✅ 3 chế độ xem: Interactive, Markdown, Mermaid
- ✅ Export: Markdown, HTML, Mermaid

---

## 🚀 Cài đặt

### 📋 Yêu cầu hệ thống

| Yêu cầu | Chi tiết |
|---------|----------|
| 🐍 Python | 3.8 trở lên |
| 📦 pip | Phiên bản mới nhất |
| 🌐 Internet | Kết nối ổn định |
| 🔑 Groq API Key | [Đăng ký miễn phí](https://console.groq.com/keys) |

### 📥 Các bước cài đặt

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/ai-youtube-summarizer.git
cd ai-youtube-summarizer

# 2. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate  # Windows
# hoặc: source venv/bin/activate  # macOS/Linux

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Tạo file .env
echo "GROQ_API_KEY=your_api_key_here" > .env

# 5. Chạy ứng dụng
python -m streamlit run app.py
```

### 🌐 Truy cập

```
🏠 Local:    http://localhost:8501
🌍 Network:  http://<your-ip>:8501
```

---

## 📊 Giới hạn kỹ thuật

### Độ dài video hỗ trợ

| Mức độ tóm tắt | Transcript tối đa | Video ước tính |
|----------------|-------------------|----------------|
| ⚡ Nhanh | 12,000 ký tự | ~15-20 phút |
| 📝 Chuẩn | 18,000 ký tự | ~25-35 phút |
| 📚 Chi tiết | 28,000 ký tự | ~40-50 phút |

---

## 📁 Cấu trúc thư mục

```
ai-youtube-summarizer/
│
├── 📄 app.py                      # 🚀 Main Application (4 Tabs)
├── 📄 requirements.txt            # 📦 Dependencies
├── 📄 .env                        # 🔐 Environment variables
├── 📄 readme.md                   # 📖 Documentation
├── 📄 HUONG_DAN_XAY_DUNG.md      # 📘 Hướng dẫn chi tiết
│
├── 📂 components/                 # 🧩 UI Components
│   ├── 📄 chatbot.py              # 💬 Enhanced Chatbot
│   ├── 📄 quiz_display.py         # 📚 Quiz Display UI
│   ├── 📄 mindmap_display.py      # 🧠 Mind Map Display
│   ├── 📄 intro.py                # 👋 Welcome Screen
│   ├── 📄 sidebar.py              # 📊 API Key Sidebar
│   └── 📄 url_validation.py       # ✅ URL Validator
│
├── 📂 utils/                      # 🔧 Utilities
│   ├── 📄 summarization.py        # 🤖 AI Summarization (3 levels)
│   ├── 📄 quiz_generator.py       # 📚 Quiz Generator
│   └── 📄 mindmap_generator.py    # 🧠 Mind Map Generator
│
├── 📂 config/                     # ⚙️ Configuration
│   └── 📄 settings.py             # 🔐 Settings Manager
│
└── 📂 styles/                     # 🎨 CSS Styles
    └── 📄 styles.py               # 💅 Custom CSS
```

---

## 📋 Hướng dẫn sử dụng

### Bước 1: Nhập URL và chọn ngôn ngữ

### Bước 2: Chọn mức độ tóm tắt

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│       ⚡        │  │       📝        │  │       📚        │
│  TÓM TẮT NHANH  │  │  TÓM TẮT CHUẨN  │  │ TÓM TẮT CHI TIẾT│
│  ~200 từ        │  │  ~500 từ        │  │  ~1500 từ       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Bước 3: Sử dụng các tabs

| Tab | Chức năng |
|-----|-----------|
| 📝 Tóm Tắt | Xem và tải bản tóm tắt |
| 💬 Trò Chuyện | Chat với AI về video |
| 📚 Quiz | Làm bài kiểm tra |
| 🧠 Mind Map | Xem sơ đồ tư duy |

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Frontend | Streamlit |
| AI/LLM | Groq API + LLaMA 3.3-70B |
| Video Processing | yt-dlp |
| Mind Map | Markmap.js |
| Styling | Custom CSS |

---

## 📜 Giấy phép

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

---

## 🗺️ Lộ trình phát triển

### ✅ Phiên bản 1.0.0 (Hiện tại)

- [x] Tóm tắt 3 mức độ
- [x] Enhanced Chatbot
- [x] Quiz Generator
- [x] Mind Map Interactive
- [x] 11+ ngôn ngữ

### 🔜 Phiên bản 1.1.0

- [ ] Export Quiz sang PDF
- [ ] Flashcards từ nội dung
- [ ] Dark/Light theme
- [ ] Lịch sử video đã xem

---

<div align="center">

**Made with ❤️ for Vietnamese Learners**

**© 2026 AI YouTube Summarizer**

</div>
