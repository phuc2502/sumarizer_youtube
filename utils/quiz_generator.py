"""
Quiz Generator Module
Tạo câu hỏi trắc nghiệm từ nội dung video sử dụng AI
"""

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

QUAN TRỌNG: Trả về CHÍNH XÁC theo format JSON sau, không thêm text khác:
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

# Difficulty levels
DIFFICULTY_LEVELS = {
    "easy": "Dễ - Câu hỏi cơ bản, dễ nhớ",
    "medium": "Trung bình - Câu hỏi cần suy luận",
    "hard": "Khó - Câu hỏi phân tích, tổng hợp"
}

# Difficulty translations
DIFFICULTY_VI = {
    "easy": "dễ",
    "medium": "trung bình", 
    "hard": "khó"
}


def generate_quiz(client, summary: str, num_questions: int = 5, 
                  difficulty: str = "medium", language: str = "Việt") -> dict:
    """
    Tạo quiz từ nội dung tóm tắt video.
    
    Args:
        client: Groq client
        summary: Bản tóm tắt video
        num_questions: Số lượng câu hỏi (5, 10, 15, 20)
        difficulty: Độ khó (easy, medium, hard)
        language: Ngôn ngữ output
    
    Returns:
        dict: Quiz data với format chuẩn
    """
    
    # Format prompt
    prompt = QUIZ_PROMPT_TEMPLATE.format(
        summary=summary,
        num_questions=num_questions,
        difficulty=DIFFICULTY_VI.get(difficulty, "trung bình"),
        language=language
    )
    
    try:
        # Gọi API để tạo quiz
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
            max_tokens=4096,
            top_p=1,
        )
        
        # Lấy response
        response_text = completion.choices[0].message.content
        
        # Parse JSON từ response
        quiz_data = parse_quiz_response(response_text)
        
        if quiz_data and "questions" in quiz_data:
            return quiz_data
        else:
            st.error("❌ Không thể parse quiz data. Đang thử lại...")
            return generate_quiz_fallback(client, summary, num_questions, difficulty, language)
            
    except Exception as e:
        st.error(f"❌ Lỗi tạo quiz: {str(e)}")
        return None


def parse_quiz_response(response_text: str) -> dict:
    """
    Parse JSON từ response của AI.
    Xử lý các trường hợp AI trả về text kèm JSON.
    """
    try:
        # Thử parse trực tiếp
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Tìm JSON trong response
    json_patterns = [
        r'\{[\s\S]*"questions"[\s\S]*\}',  # Tìm object có "questions"
        r'```json\s*([\s\S]*?)\s*```',      # Tìm trong code block
        r'```\s*([\s\S]*?)\s*```',          # Code block không có language
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response_text)
        for match in matches:
            try:
                # Nếu match là tuple (từ group), lấy phần tử đầu
                json_str = match[0] if isinstance(match, tuple) else match
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue
    
    return None


def generate_quiz_fallback(client, summary: str, num_questions: int,
                           difficulty: str, language: str) -> dict:
    """
    Fallback method nếu parse JSON thất bại.
    Yêu cầu AI trả về format đơn giản hơn.
    """
    
    simple_prompt = f"""Tạo {num_questions} câu hỏi trắc nghiệm từ nội dung:

{summary}

Trả về JSON với format:
{{"questions": [{{"id": 1, "question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "correct": "A", "explanation": "..."}}]}}

CHỈ trả về JSON, không có text khác."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Model nhẹ hơn, nhanh hơn
            messages=[{"role": "user", "content": simple_prompt}],
            temperature=0.5,
            max_tokens=3000,
        )
        
        response = completion.choices[0].message.content
        return parse_quiz_response(response)
        
    except Exception:
        # Trả về quiz mẫu nếu thất bại hoàn toàn
        return {
            "questions": [
                {
                    "id": 1,
                    "question": "Không thể tạo quiz. Vui lòng thử lại.",
                    "options": ["A. Thử lại", "B. Thử lại", "C. Thử lại", "D. Thử lại"],
                    "correct": "A",
                    "explanation": "Vui lòng refresh và thử lại."
                }
            ]
        }


def validate_quiz(quiz_data: dict) -> bool:
    """
    Kiểm tra quiz data có hợp lệ không.
    """
    if not quiz_data or "questions" not in quiz_data:
        return False
    
    for q in quiz_data["questions"]:
        required_fields = ["id", "question", "options", "correct", "explanation"]
        if not all(field in q for field in required_fields):
            return False
        if len(q["options"]) != 4:
            return False
        if q["correct"] not in ["A", "B", "C", "D"]:
            return False
    
    return True


def get_quiz_stats(answers: dict, quiz_data: dict) -> dict:
    """
    Tính toán thống kê kết quả quiz.
    
    Args:
        answers: Dict {question_id: user_answer}
        quiz_data: Quiz data gốc
    
    Returns:
        dict: Thống kê kết quả
    """
    questions = quiz_data.get("questions", [])
    total = len(questions)
    correct = 0
    results = []
    
    for q in questions:
        q_id = q["id"]
        user_answer = answers.get(q_id, "")
        is_correct = user_answer == q["correct"]
        
        if is_correct:
            correct += 1
        
        results.append({
            "id": q_id,
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["correct"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })
    
    percentage = (correct / total * 100) if total > 0 else 0
    
    # Đánh giá
    if percentage >= 80:
        grade = "🏆 Xuất sắc!"
        grade_color = "green"
    elif percentage >= 60:
        grade = "👍 Tốt!"
        grade_color = "blue"
    elif percentage >= 40:
        grade = "📚 Cần cải thiện"
        grade_color = "orange"
    else:
        grade = "💪 Cố gắng hơn nhé!"
        grade_color = "red"
    
    return {
        "total": total,
        "correct": correct,
        "percentage": percentage,
        "grade": grade,
        "grade_color": grade_color,
        "results": results
    }
