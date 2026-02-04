"""
Mind Map Display Component
Hiển thị Mind Map interactive với Markmap
"""

import streamlit as st
import streamlit.components.v1 as components
from utils.mindmap_generator import (
    generate_mindmap_markdown,
    get_markmap_html,
    get_markmap_html_light,
    generate_mermaid_mindmap,
    get_sample_mindmap
)


def display_mindmap_generator(client):
    """
    Hiển thị giao diện tạo và xem Mind Map.
    """
    st.markdown("### 🧠 Mind Map - Sơ Đồ Tư Duy")
    st.markdown("*Hệ thống hóa kiến thức video thành sơ đồ tư duy trực quan*")
    
    # Kiểm tra đã có summary chưa
    if "follow_up_summary" not in st.session_state or not st.session_state.follow_up_summary:
        st.warning("⚠️ Vui lòng tạo bản tóm tắt video trước khi tạo Mind Map!")
        st.info("👉 Quay lại tab **Tóm tắt** và nhấn **Tạo Bản Tóm Tắt**")
        
        # Hiển thị demo
        st.divider()
        st.markdown("#### 🎯 Mind Map Mẫu")
        display_sample_mindmap()
        return
    
    # Generate button
    if st.button("🧠 Tạo Mind Map", type="primary", use_container_width=True):
        with st.spinner("🤖 Đang phân tích và tạo Mind Map..."):
            markdown = generate_mindmap_markdown(
                client=client,
                summary=st.session_state.follow_up_summary
            )
            
            if markdown:
                st.session_state.mindmap_markdown = markdown
                st.success("✅ Đã tạo Mind Map thành công!")
                st.rerun()
            else:
                st.error("❌ Không thể tạo Mind Map. Vui lòng thử lại!")
    
    # Display Mind Map if available
    if "mindmap_markdown" in st.session_state and st.session_state.mindmap_markdown:
        st.divider()
        
        # Main Mind Map View - FULL WIDTH
        display_markmap_fullwidth(st.session_state.mindmap_markdown)
        
        st.divider()
        
        # Export and other options in expanders
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("📝 Xem Markdown Source"):
                st.code(st.session_state.mindmap_markdown, language="markdown")
        
        with col2:
            with st.expander("📊 Xem Mermaid Code"):
                mermaid_code = generate_mermaid_mindmap(st.session_state.mindmap_markdown)
                if mermaid_code:
                    st.code(mermaid_code, language="mermaid")
        
        # Export buttons
        st.markdown("#### 📥 Tải xuống")
        display_export_options(st.session_state.mindmap_markdown)
        
        # Reset button
        st.divider()
        if st.button("🔄 Tạo Mind Map mới", use_container_width=True):
            st.session_state.mindmap_markdown = None
            st.rerun()


def display_markmap_fullwidth(markdown: str):
    """
    Hiển thị Markmap interactive FULL WIDTH.
    """
    st.markdown("#### 🗺️ Mind Map Interactive")
    st.caption("💡 Tip: Kéo để di chuyển • Scroll để zoom • Click node để expand/collapse")
    
    # Full width, larger height
    html = get_markmap_html_light(markdown, 550)
    
    # Render with full width
    components.html(html, height=570, scrolling=False)


def display_export_options(markdown: str):
    """
    Hiển thị các tùy chọn export.
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📄 Tải Markdown",
            data=markdown,
            file_name="mindmap.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        # Export as HTML (interactive)
        html_content = get_markmap_html_light(markdown, 700)
        st.download_button(
            label="🌐 Tải HTML",
            data=html_content,
            file_name="mindmap.html",
            mime="text/html",
            use_container_width=True
        )
    
    with col3:
        mermaid_code = generate_mermaid_mindmap(markdown)
        if mermaid_code:
            st.download_button(
                label="📊 Tải Mermaid",
                data=mermaid_code,
                file_name="mindmap_mermaid.txt",
                mime="text/plain",
                use_container_width=True
            )


def display_sample_mindmap():
    """
    Hiển thị Mind Map mẫu.
    """
    sample = get_sample_mindmap()
    
    st.caption("*Ví dụ Mind Map: Học Lập Trình Python*")
    
    html = get_markmap_html_light(sample, 450)
    components.html(html, height=470, scrolling=False)


def reset_mindmap():
    """
    Reset Mind Map state.
    """
    if "mindmap_markdown" in st.session_state:
        del st.session_state.mindmap_markdown
