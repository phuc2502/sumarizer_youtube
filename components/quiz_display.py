"""
Quiz Display Component
Hiển thị quiz và xử lý tương tác người dùng
"""

import streamlit as st
from utils.quiz_generator import (
    generate_quiz, 
    validate_quiz, 
    get_quiz_stats,
    DIFFICULTY_LEVELS
)


def display_quiz_generator(client):
    """
    Hiển thị giao diện tạo quiz.
    """
    st.markdown("### 📚 Tạo Câu Hỏi Trắc Nghiệm")
    
    # Kiểm tra đã có summary chưa
    if "follow_up_summary" not in st.session_state or not st.session_state.follow_up_summary:
        st.warning("⚠️ Vui lòng tạo bản tóm tắt video trước khi tạo quiz!")
        st.info("👉 Quay lại tab **Tóm tắt** và nhấn **Get Detailed Notes**")
        return
    
    # Cấu hình quiz
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.selectbox(
            "📊 Số lượng câu hỏi:",
            options=[5, 10, 15, 20],
            index=0,
            help="Chọn số câu hỏi muốn tạo"
        )
    
    with col2:
        difficulty = st.selectbox(
            "📈 Độ khó:",
            options=list(DIFFICULTY_LEVELS.keys()),
            format_func=lambda x: DIFFICULTY_LEVELS[x],
            index=1,
            help="Chọn mức độ khó của câu hỏi"
        )
    
    # Nút tạo quiz
    if st.button("🎯 Tạo Quiz", type="primary", use_container_width=True):
        with st.spinner("🤖 Đang tạo câu hỏi trắc nghiệm..."):
            quiz_data = generate_quiz(
                client=client,
                summary=st.session_state.follow_up_summary,
                num_questions=num_questions,
                difficulty=difficulty,
                language="Việt"
            )
            
            if quiz_data and validate_quiz(quiz_data):
                st.session_state.quiz_data = quiz_data
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.success(f"✅ Đã tạo {len(quiz_data['questions'])} câu hỏi!")
                st.rerun()
            else:
                st.error("❌ Không thể tạo quiz. Vui lòng thử lại!")
    
    # Hiển thị quiz nếu đã tạo
    if "quiz_data" in st.session_state and st.session_state.quiz_data:
        st.divider()
        display_quiz_questions()


def display_quiz_questions():
    """
    Hiển thị các câu hỏi quiz.
    """
    quiz_data = st.session_state.quiz_data
    questions = quiz_data.get("questions", [])
    
    if not questions:
        st.warning("Không có câu hỏi nào.")
        return
    
    # Header
    st.markdown(f"### 📝 Bài Quiz ({len(questions)} câu hỏi)")
    
    # Progress bar
    if "quiz_answers" in st.session_state:
        answered = len(st.session_state.quiz_answers)
        progress = answered / len(questions)
        st.progress(progress, text=f"Đã trả lời: {answered}/{len(questions)}")
    
    # Hiển thị từng câu hỏi
    for i, q in enumerate(questions):
        display_single_question(q, i)
    
    st.divider()
    
    # Nút submit
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.get("quiz_submitted", False):
            if st.button("✅ Nộp bài", type="primary", use_container_width=True):
                if len(st.session_state.get("quiz_answers", {})) < len(questions):
                    st.warning("⚠️ Bạn chưa trả lời hết tất cả câu hỏi!")
                else:
                    st.session_state.quiz_submitted = True
                    st.rerun()
        else:
            if st.button("🔄 Làm lại Quiz", use_container_width=True):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
            
            if st.button("📚 Tạo Quiz mới", use_container_width=True):
                st.session_state.quiz_data = None
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
    
    # Hiển thị kết quả nếu đã submit
    if st.session_state.get("quiz_submitted", False):
        display_quiz_results()


def display_single_question(question: dict, index: int):
    """
    Hiển thị một câu hỏi.
    """
    q_id = question["id"]
    is_submitted = st.session_state.get("quiz_submitted", False)
    user_answer = st.session_state.get("quiz_answers", {}).get(q_id, "")
    correct_answer = question["correct"]
    
    # Container cho câu hỏi
    with st.container():
        # Tiêu đề câu hỏi
        if is_submitted:
            if user_answer == correct_answer:
                st.markdown(f"#### ✅ Câu {index + 1}: {question['question']}")
            else:
                st.markdown(f"#### ❌ Câu {index + 1}: {question['question']}")
        else:
            st.markdown(f"#### Câu {index + 1}: {question['question']}")
        
        # Các đáp án
        options = question["options"]
        
        if is_submitted:
            # Hiển thị kết quả sau khi submit
            for opt in options:
                opt_letter = opt[0]  # A, B, C, D
                
                if opt_letter == correct_answer:
                    st.success(f"✓ {opt}")
                elif opt_letter == user_answer and user_answer != correct_answer:
                    st.error(f"✗ {opt}")
                else:
                    st.write(f"   {opt}")
            
            # Hiển thị giải thích
            with st.expander("💡 Xem giải thích"):
                st.info(question["explanation"])
        else:
            # Radio buttons để chọn đáp án
            selected = st.radio(
                f"Chọn đáp án cho câu {index + 1}:",
                options=options,
                key=f"q_{q_id}",
                index=None,
                label_visibility="collapsed"
            )
            
            if selected:
                # Lưu đáp án (lấy chữ cái đầu A, B, C, D)
                answer_letter = selected[0]
                if "quiz_answers" not in st.session_state:
                    st.session_state.quiz_answers = {}
                st.session_state.quiz_answers[q_id] = answer_letter
        
        st.write("")  # Spacing


def display_quiz_results():
    """
    Hiển thị kết quả quiz.
    """
    st.divider()
    st.markdown("## 📊 Kết Quả Quiz")
    
    quiz_data = st.session_state.quiz_data
    answers = st.session_state.get("quiz_answers", {})
    
    # Tính toán kết quả
    stats = get_quiz_stats(answers, quiz_data)
    
    # Hiển thị điểm số
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📝 Tổng câu hỏi",
            value=stats["total"]
        )
    
    with col2:
        st.metric(
            label="✅ Số câu đúng",
            value=stats["correct"],
            delta=f"{stats['percentage']:.0f}%"
        )
    
    with col3:
        st.metric(
            label="🎯 Đánh giá",
            value=stats["grade"]
        )
    
    # Progress bar
    st.progress(stats["percentage"] / 100)
    
    # Chi tiết từng câu
    with st.expander("📋 Xem chi tiết từng câu", expanded=False):
        for result in stats["results"]:
            if result["is_correct"]:
                st.success(f"✅ Câu {result['id']}: Đúng")
            else:
                st.error(
                    f"❌ Câu {result['id']}: Sai (Bạn chọn: {result['user_answer']}, "
                    f"Đáp án đúng: {result['correct_answer']})"
                )
                st.info(f"💡 {result['explanation']}")
    
    # Thông báo khuyến khích
    if stats["percentage"] >= 80:
        st.balloons()
        st.success("🎉 Tuyệt vời! Bạn đã nắm vững nội dung video!")
    elif stats["percentage"] >= 60:
        st.info("👍 Khá tốt! Xem lại video để hiểu sâu hơn nhé!")
    else:
        st.warning("💪 Đừng nản! Xem lại video và thử lại quiz nhé!")
