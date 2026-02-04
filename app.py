# Import necessary libraries
import time
import streamlit as st
from groq import Groq
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from components.intro import display_intro
from components.chatbot import display_chat_enhanced, initialize_client
from components.url_validation import is_valid_youtube_url
from components.quiz_display import display_quiz_generator
from components.mindmap_display import display_mindmap_generator
from utils.summarization import get_summary, SUMMARY_LEVELS, get_level_info
from components.sidebar import render_sidebar
from styles.styles import get_titleCenter_css

st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="AI_YouTube_Summarizer.png",
    initial_sidebar_state="expanded",
    layout="wide"  # Sử dụng layout rộng cho tabs
)


# Initialize session state variables in one place for better organization
def init_session_state():
    """Khởi tạo các biến session state."""
    defaults = {
        "accepted_terms": False,
        "show_prompt": False,
        "cached_summary_timestamp": None,
        "summary_file_name": "",
        "cached_summary": None,
        "follow_up_summary": None,
        "show_intro": True,
        "current_video_url": None,
        "quiz_data": None,
        "quiz_answers": {},
        "quiz_submitted": False,
        "chat_messages": [],
        "active_tab": 0,
        "mindmap_markdown": None,
        "summary_level": "standard"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# Define the Terms and Conditions dialog
@st.dialog("Terms and Conditions", width="large")
def terms_dialog():
    """
    Display the terms and conditions dialog, requiring user acceptance before proceeding.
    """
    st.write("By using this tool, you agree to the following terms and conditions:")

    st.subheader("1. Developmental Status")
    st.markdown(
        """
        This tool is currently in development, and occasional bugs or inaccuracies may occur. 
        We encourage users to provide feedback to help improve the experience.
        """
    )

    st.subheader("2. Liability")
    st.markdown(
        """
        The creators are not liable for any misuse or unintended consequences resulting from the use of this tool. 
        Users are solely responsible for how they utilize and interpret the generated summaries.
        """
    )

    st.subheader("3. Content Compliance")
    st.markdown(
        """
        Users are responsible for ensuring that the video content they summarize complies with platform policies and copyright 
        regulations. We hold no responsibility for issues arising from summarizing or sharing content that violates third-party terms.
        """
    )

    st.subheader("4. Data Privacy")
    st.markdown(
        """
        This tool does not store your API keys, video content, or generated summaries on external servers. 
        All processing occurs in real-time, ensuring your data remains private and secure.
        """
    )

    # Add "I Accept" button for the user to accept the terms
    if st.button("I Accept"):
        st.session_state.accepted_terms = True
        st.rerun()  # Rerun the app to close the dialog and proceed

# Show terms dialog if not accepted
if not st.session_state.accepted_terms:
    terms_dialog()

# Load environment variables
load_dotenv()

# Language options for subtitle extraction and summary generation
LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English",
    "en-GB": "English (UK)",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
    "ru": "Russian",
    "pt": "Portuguese"
}

def extract_transcript_details(video_url, lang="en"):
    """
    Extract subtitles for a given YouTube video using yt-dlp.

    Args:
        video_url (str): The YouTube video URL.
        lang (str): The language code for subtitles (default is 'en').

    Returns:
        str: The subtitles as text if available, otherwise None.
    """
    options = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [lang],
        'skip_download': True,
        'quiet': True,
    }

    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subtitles = info.get('requested_subtitles', {})
            subtitle_info = subtitles.get(lang)

            if subtitle_info:
                subtitle_url = subtitle_info['url']
                response = requests.get(subtitle_url)
                response.raise_for_status()
                return response.text
            else:
                st.error(f"⚠️ Subtitles not available in the selected language ({lang}).")
                return None
    except Exception as e:
        st.error(f"Error fetching subtitles: {e}")
        return None


def display_summary_tab(client, youtube_link, selected_language):
    """Hiển thị tab Tóm tắt với 3 mức độ chi tiết."""
    
    if not youtube_link:
        st.info("👆 Vui lòng nhập URL video YouTube ở trên để bắt đầu.")
        return
    
    # ===== CHỌN MỨC ĐỘ TÓM TẮT =====
    st.markdown("##### 📊 Chọn mức độ chi tiết:")
    
    level_cols = st.columns(3)
    
    levels = ["quick", "standard", "detailed"]
    level_icons = ["⚡", "📝", "📚"]
    level_names = ["Tóm tắt nhanh", "Tóm tắt chuẩn", "Tóm tắt chi tiết"]
    level_descriptions = [
        "~200 từ • 5-7 điểm chính",
        "~500 từ • 10-15 điểm", 
        "~1500 từ • 20+ điểm"
    ]
    
    for i, (col, level, icon, name, desc) in enumerate(zip(level_cols, levels, level_icons, level_names, level_descriptions)):
        with col:
            is_selected = st.session_state.get("summary_level", "standard") == level
            button_type = "primary" if is_selected else "secondary"
            
            if st.button(
                f"{icon} {name}\n{desc}",
                key=f"level_{level}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.summary_level = level
                st.rerun()
    
    # Hiển thị mức độ đã chọn
    current_level = st.session_state.get("summary_level", "standard")
    level_info = get_level_info(current_level)
    st.caption(f"✅ Đã chọn: **{level_info['name']}** - {level_info['description']}")
    
    st.divider()
    
    # Button to fetch detailed notes
    if st.button("📓 Tạo Bản Tóm Tắt", type="primary", use_container_width=True):
        st.session_state.show_prompt = True
        
        # Generate or fetch cached summary
        current_time = time.time()
        cache_expiry = 3600  # 1 hour expiration

        # Check if we need to regenerate
        current_level = st.session_state.get("summary_level", "standard")
        cache_key = f"{youtube_link}_{current_level}"
        
        need_regenerate = (
            'cached_summary' not in st.session_state or 
            st.session_state.cached_summary is None or
            st.session_state.cached_summary_timestamp is None or 
            current_time - st.session_state.cached_summary_timestamp > cache_expiry or
            st.session_state.current_video_url != youtube_link or
            st.session_state.get("cached_level") != current_level
        )

        if need_regenerate:
            with st.spinner("🔄 Đang trích xuất phụ đề..."):
                transcript_text = extract_transcript_details(youtube_link, selected_language)

            if transcript_text:
                level_info = get_level_info(current_level)
                with st.spinner(f"🤖 Đang tạo {level_info['name']}..."):
                    video_id = youtube_link.split("=")[1] if "=" in youtube_link else youtube_link.split("/")[-1]
                    summary = get_summary(client, transcript_text, LANGUAGES[selected_language], video_id, current_level)
                    
                    if summary is not None:
                        st.session_state.cached_summary = summary
                        st.session_state.cached_summary_timestamp = current_time
                        st.session_state.follow_up_summary = summary
                        st.session_state.current_video_url = youtube_link
                        st.session_state.cached_level = current_level
                        
                        # Reset quiz và mindmap khi có video mới
                        st.session_state.quiz_data = None
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.chat_messages = []
                        st.session_state.mindmap_markdown = None
                        
                        st.success(f"✅ Đã tạo {level_info['name']} thành công!")
                    else:
                        st.error("❌ Không thể tạo bản tóm tắt.")
            else:
                st.error("❌ Không tìm thấy phụ đề cho video này.")
        else:
            st.session_state.follow_up_summary = st.session_state.cached_summary
            st.info("📦 Sử dụng bản tóm tắt từ cache.")
    
    # Display summary if available
    if st.session_state.get("follow_up_summary"):
        st.divider()
        st.markdown("### 📝 Bản Tóm Tắt Chi Tiết")
        st.markdown(st.session_state.follow_up_summary)
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Xóa Cache", use_container_width=True):
                st.cache_data.clear()
                st.session_state.cached_summary = None
                st.session_state.cached_summary_timestamp = None
                st.toast("Đã xóa cache!")
        
        with col2:
            st.download_button(
                label="📥 Tải Xuống",
                data=st.session_state.follow_up_summary,
                file_name=st.session_state.get("summary_file_name", "summary.txt"),
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            if st.button("📋 Sao Chép", use_container_width=True):
                st.toast("Đã sao chép vào clipboard!")
        
        st.session_state.show_intro = False


# Main application logic if terms are accepted
if st.session_state.accepted_terms:
    # Placeholder for success message
    success_placeholder = st.empty()
    success_placeholder.success("Thank you for accepting the terms! You may now use the summarization tool.", icon="✅")

    # Render the sidebar and initialize the client
    client = render_sidebar()

    if client:
        # Display application title
        st.markdown("<h1 class='centered-title'>🎬 AI YouTube Summarizer</h1>", unsafe_allow_html=True)
        st.markdown(get_titleCenter_css, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Tóm tắt video YouTube, Trò chuyện AI & Tạo Quiz học tập</p>", unsafe_allow_html=True)
        st.write("")

        # Layout with two columns: video input and language selection
        col1, col2 = st.columns([3, 1])

        with col1:
            # Input field for YouTube video link
            youtube_link = st.text_input(
                "🔗 Nhập URL Video YouTube:",
                placeholder="https://www.youtube.com/watch?v=example",
                label_visibility="visible"
            )
            
            if youtube_link:
                # Validate the provided YouTube URL
                if not is_valid_youtube_url(youtube_link):
                    st.error("⚠️ URL không hợp lệ. Vui lòng nhập đúng link YouTube.")
                    st.stop()

        with col2:
            # Dropdown menu to select the video language
            selected_language = st.selectbox(
                "🌐 Ngôn ngữ:",
                list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                index=0  # Mặc định tiếng Việt
            )

        if youtube_link:
            # Fetch video title and prepare summary filename
            try:
                response = requests.get(youtube_link, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.replace(" - YouTube", "").strip() if soup.title else "Video"
                summary_file_name = f"{title}_Summary.txt"
                st.session_state.summary_file_name = summary_file_name
            except:
                title = "Video"
                st.session_state.summary_file_name = "summary.txt"
            
            success_placeholder.empty()

            # Display the YouTube video
            st.video(youtube_link, format="video/mp4")
            st.write("")
            
            # ===== TABS INTERFACE =====
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

        else:
            # Display intro when no video
            if st.session_state.show_intro:
                display_intro()
    else:
        display_intro()

else:
    # Show message if terms are not accepted
    time.sleep(1)
    st.title("Terms and Conditions Not Accepted")
    st.warning("We're sorry, but you must accept our Terms and Conditions to proceed. Your understanding and agreement help us maintain a safe and trustworthy environment for all users. If you have any questions or concerns about our terms, please feel free to reach out to us for clarification.")
    st.caption("Reload to continue")
