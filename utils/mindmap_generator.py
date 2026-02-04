"""
Mind Map Generator Module
Tạo cấu trúc Mind Map từ nội dung video sử dụng AI
"""

import json
import re
import streamlit as st

# Prompt template để tạo Mind Map
MINDMAP_PROMPT_TEMPLATE = """Dựa trên nội dung tóm tắt video sau:

{summary}

Hãy phân tích và tạo cấu trúc Mind Map với format Markdown sau:

# [Tiêu đề chính - Chủ đề video]

## [Nhánh 1 - Ý chính đầu tiên]
- Chi tiết 1.1
- Chi tiết 1.2
- Chi tiết 1.3

## [Nhánh 2 - Ý chính thứ hai]
- Chi tiết 2.1
- Chi tiết 2.2

## [Nhánh 3 - Ý chính thứ ba]
- Chi tiết 3.1
- Chi tiết 3.2

... (tiếp tục với các nhánh khác)

YÊU CẦU:
1. Tối đa 5-7 nhánh chính (##)
2. Mỗi nhánh có 2-5 chi tiết (-)
3. Có thể có chi tiết con (thụt lề thêm với 2 dấu cách)
4. Ngắn gọn, súc tích, dễ hiểu
5. Sử dụng tiếng Việt
6. CHỈ trả về Markdown, không thêm text giải thích

Ví dụ output:
# API Testing với Postman

## API là gì?
- Giao diện lập trình ứng dụng
- Kết nối các hệ thống với nhau
  - REST API
  - SOAP API
  - GraphQL

## Tại sao cần test API?
- Phát hiện lỗi sớm
- Đảm bảo chất lượng
- Tự động hóa testing
"""


def generate_mindmap_markdown(client, summary: str) -> str:
    """
    Tạo Mind Map dạng Markdown từ nội dung tóm tắt.
    
    Args:
        client: Groq client
        summary: Bản tóm tắt video
    
    Returns:
        str: Mind Map dạng Markdown
    """
    
    if not summary:
        return None
    
    prompt = MINDMAP_PROMPT_TEMPLATE.format(summary=summary)
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia tạo Mind Map giáo dục. Luôn trả về Markdown hợp lệ với cấu trúc heading (#, ##) và bullet points (-)."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
        )
        
        markdown_content = completion.choices[0].message.content
        
        # Clean up the response
        markdown_content = clean_markdown(markdown_content)
        
        return markdown_content
        
    except Exception as e:
        st.error(f"❌ Lỗi tạo Mind Map: {str(e)}")
        return None


def clean_markdown(content: str) -> str:
    """
    Làm sạch Markdown output từ AI.
    """
    # Loại bỏ code blocks nếu có
    content = re.sub(r'```markdown\s*', '', content)
    content = re.sub(r'```\s*$', '', content)
    content = re.sub(r'^```\s*', '', content)
    
    # Đảm bảo bắt đầu bằng heading
    lines = content.strip().split('\n')
    
    # Tìm dòng heading đầu tiên
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            lines = lines[i:]
            break
    
    return '\n'.join(lines)


def markdown_to_json(markdown: str) -> dict:
    """
    Chuyển đổi Markdown sang JSON structure cho việc xử lý.
    """
    lines = markdown.strip().split('\n')
    result = {
        "title": "",
        "branches": []
    }
    
    current_branch = None
    current_subitems = []
    
    for line in lines:
        line = line.rstrip()
        
        if line.startswith('# '):
            result["title"] = line[2:].strip()
        
        elif line.startswith('## '):
            # Save previous branch
            if current_branch:
                result["branches"].append({
                    "name": current_branch,
                    "children": current_subitems
                })
            current_branch = line[3:].strip()
            current_subitems = []
        
        elif line.strip().startswith('- '):
            item = line.strip()[2:].strip()
            current_subitems.append(item)
    
    # Save last branch
    if current_branch:
        result["branches"].append({
            "name": current_branch,
            "children": current_subitems
        })
    
    return result


def generate_mermaid_mindmap(markdown: str) -> str:
    """
    Chuyển đổi Markdown sang Mermaid mindmap syntax.
    """
    json_data = markdown_to_json(markdown)
    
    if not json_data["title"]:
        return None
    
    mermaid_lines = ["mindmap"]
    
    # Root node
    title = json_data["title"][:30]  # Limit length
    mermaid_lines.append(f"  root(({title}))")
    
    for branch in json_data["branches"]:
        branch_name = branch["name"][:25]
        mermaid_lines.append(f"    {branch_name}")
        
        for child in branch["children"][:4]:  # Limit to 4 children
            child_text = child[:30]
            mermaid_lines.append(f"      {child_text}")
    
    return '\n'.join(mermaid_lines)


def get_markmap_html(markdown: str, height: int = 600) -> str:
    """
    Tạo HTML với Markmap để render Mind Map interactive.
    
    Args:
        markdown: Nội dung Markdown
        height: Chiều cao của mind map (px)
    
    Returns:
        str: HTML code để render
    """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            html, body {{
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                overflow: hidden;
            }}
            .container {{
                width: 100%;
                height: {height}px;
                background: #ffffff;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                margin: 0;
            }}
            #mindmap {{
                width: 100%;
                height: 100%;
            }}
            .markmap {{
                width: 100%;
                height: 100%;
            }}
            .markmap-node-circle {{
                fill: #667eea !important;
                stroke: #764ba2 !important;
                stroke-width: 2px !important;
            }}
            .markmap-node-text {{
                fill: #2d3748 !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
                font-size: 14px !important;
                font-weight: 500 !important;
            }}
            .markmap-link {{
                stroke: #a0aec0 !important;
                stroke-width: 2px !important;
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.15.4"></script>
    </head>
    <body>
        <div class="container">
            <div id="mindmap" class="markmap">
                <script type="text/template">
{markdown}
                </script>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def get_markmap_html_light(markdown: str, height: int = 600) -> str:
    """
    Tạo HTML với Markmap theme sáng đẹp.
    """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            html, body {{
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                overflow: hidden;
            }}
            .container {{
                width: 100%;
                height: {height}px;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                border: 1px solid #e2e8f0;
            }}
            #mindmap {{
                width: 100%;
                height: 100%;
            }}
            .markmap {{
                width: 100%;
                height: 100%;
            }}
            .markmap-node-circle {{
                fill: #4299e1 !important;
                stroke: #2b6cb0 !important;
                stroke-width: 2px !important;
            }}
            .markmap-node-text {{
                fill: #1a202c !important;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
                font-size: 14px !important;
                font-weight: 500 !important;
            }}
            .markmap-link {{
                stroke: #90cdf4 !important;
                stroke-width: 2px !important;
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.15.4"></script>
    </head>
    <body>
        <div class="container">
            <div id="mindmap" class="markmap">
                <script type="text/template">
{markdown}
                </script>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def export_mindmap_svg(markdown: str) -> str:
    """
    Tạo SVG từ markdown (đơn giản hóa).
    Trả về markdown để user copy.
    """
    return markdown


def get_sample_mindmap() -> str:
    """
    Trả về một Mind Map mẫu để test.
    """
    return """# Học Lập Trình Python

## Cơ bản
- Biến và kiểu dữ liệu
- Cấu trúc điều khiển
  - if/else
  - for/while
- Hàm và module

## Nâng cao
- OOP - Lập trình hướng đối tượng
- File I/O
- Exception handling
- Decorators

## Thư viện phổ biến
- NumPy - Tính toán số học
- Pandas - Xử lý dữ liệu
- Matplotlib - Vẽ biểu đồ

## Ứng dụng
- Web Development
  - Flask
  - Django
- Data Science
- Machine Learning
"""
