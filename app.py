from flask import Flask, jsonify, request, render_template
import os
from dotenv import load_dotenv
from models import db, Course, Student, Enrollment
from ml_service import recommender
from deepseek_service import chat_service
import requests
from bs4 import BeautifulSoup
import re
import json
from flask_cors import CORS

# Load environment variables at the start
load_dotenv()

# Print environment variables (without actual values) for debugging
print("Environment variables loaded:")
print("API exists:", "API" in os.environ)
print("All environment variables:", list(os.environ.keys()))  # 打印所有环境变量名称（不打印值）

# Initialize Flask app
app = Flask(__name__)

# 确保数据库使用内存模式
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 添加CORS支持
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
db.init_app(app)

# 定义一个数据库初始化函数
def init_database():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")
        
        # 这里添加数据库种子数据（不再从 seed_db.py 导入）
        from models import Course, Student
        
        # 添加课程
        courses = [
            Course(code="CS101", name="Introduction to Computer Science", credits=3, description="Basic concepts of computer science"),
            Course(code="CS201", name="Data Structures", credits=4, description="Advanced data structures and algorithms"),
            Course(code="MATH101", name="Calculus I", credits=4, description="Introduction to calculus"),
            # 添加更多课程...
        ]
        
        # 添加学生
        students = [
            Student(username="Alice Smith", email="alice@example.com", major="Computer Science"),
            Student(username="Bob Johnson", email="bob@example.com", major="Mathematics"),
            # 添加更多学生...
        ]
        
        # 将数据添加到数据库
        for course in courses:
            existing = Course.query.filter_by(code=course.code).first()
            if not existing:
                db.session.add(course)
        
        for student in students:
            existing = Student.query.filter_by(email=student.email).first()
            if not existing:
                db.session.add(student)
        
        db.session.commit()
        print("Database seeded successfully!")

# 初始化数据库
init_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/courses')
def get_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])

@app.route('/api/crawl-program', methods=['POST'])
def crawl_program():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url = data['url']
    
    # 不再检查API密钥，直接尝试爬取
    try:
        print(f"尝试爬取URL: {url}")
        # 使用更友好的请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        # Fetch the webpage content
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        print(f"成功获取网页内容，长度: {len(response.text)}")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取所有文本内容，用于更全面的分析
        all_text = soup.get_text()
        print(f"提取的文本内容长度: {len(all_text)}")
        
        # Extract program information
        program_info = {
            "title": "",
            "description": "",
            "courses": [],
            "requirements": [],
            "credits": "",
            "raw_text_sample": all_text[:1000]  # 添加原始文本样本用于调试
        }
        
        # 尝试多种方式提取标题
        title_candidates = []
        # 方法1: 常见标题标签
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            for el in elements:
                title_text = el.get_text().strip()
                if len(title_text) > 5 and len(title_text) < 100:  # 合理的标题长度
                    title_candidates.append(title_text)
        
        # 方法2: 包含"program"、"degree"、"major"等关键词的元素
        for keyword in ['program', 'degree', 'major', 'bachelor', 'master', 'computer science', 'curriculum']:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for el in elements:
                if el.parent.name in ['h1', 'h2', 'h3', 'h4', 'strong', 'b', 'div', 'p']:
                    title_text = el.parent.get_text().strip()
                    if len(title_text) > 5 and len(title_text) < 100:  # 合理的标题长度
                        title_candidates.append(title_text)
        
        # 选择最可能的标题
        if title_candidates:
            program_info["title"] = title_candidates[0]
            print(f"找到标题: {program_info['title']}")
        
        # 提取课程信息 - 使用多种模式
        course_patterns = [
            r'[A-Z]{2,4}\s*\d{3,4}[A-Z]?',  # 如 CS101, MATH101A
            r'[A-Z]{2,4}\s*\d{3,4}[A-Z]?\s*[-:]\s*[A-Za-z\s]+',  # 如 CS101 - Introduction to Programming
            r'[A-Za-z\s]+\s*\(\s*[A-Z]{2,4}\s*\d{3,4}[A-Z]?\s*\)'  # 如 Introduction to Programming (CS101)
        ]
        
        all_courses = []
        for pattern in course_patterns:
            # 在文本中查找
            matches = re.findall(pattern, all_text)
            if matches:
                for match in matches:
                    match = match.strip()
                    if match not in all_courses and len(match) > 3:
                        all_courses.append(match)
        
        # 限制课程数量
        program_info["courses"] = all_courses[:20]  # 最多20门课程
        print(f"找到课程数量: {len(program_info['courses'])}")
        
        # 如果没有找到课程，尝试查找列表项
        if not program_info["courses"]:
            list_items = soup.find_all('li')
            for item in list_items:
                item_text = item.get_text().strip()
                # 如果列表项看起来像课程（包含数字和字母）
                if re.search(r'\d+', item_text) and len(item_text) > 10 and len(item_text) < 200:
                    program_info["courses"].append(item_text)
                    if len(program_info["courses"]) >= 20:
                        break
        
        # 提取学分要求
        credit_patterns = [
            r'\d+\s*credits',
            r'\d+\s*credit\s*hours',
            r'total\s*of\s*\d+\s*credits',
            r'minimum\s*of\s*\d+\s*credits',
            r'requires\s*\d+\s*credits'
        ]
        
        for pattern in credit_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                program_info["credits"] = matches[0]
                print(f"找到学分要求: {program_info['credits']}")
                break
        
        # 提取描述 - 尝试找到介绍段落
        desc_candidates = []
        
        # 查找包含关键词的段落
        for keyword in ['overview', 'introduction', 'about', 'description', 'program', 'curriculum']:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for el in elements:
                if el.parent.name == 'p':
                    desc_text = el.parent.get_text().strip()
                    if len(desc_text) > 50:  # 只考虑较长的段落
                        desc_candidates.append(desc_text)
                elif el.parent.parent and el.parent.parent.name == 'p':
                    desc_text = el.parent.parent.get_text().strip()
                    if len(desc_text) > 50:
                        desc_candidates.append(desc_text)
        
        # 如果没有找到，使用前几个段落
        if not desc_candidates:
            paragraphs = soup.find_all('p')
            for p in paragraphs[:5]:
                p_text = p.get_text().strip()
                if len(p_text) > 50:  # 只考虑较长的段落
                    desc_candidates.append(p_text)
        
        if desc_candidates:
            program_info["description"] = desc_candidates[0]
            print(f"找到描述: {program_info['description'][:100]}...")
        
        # 提取要求
        req_candidates = []
        req_keywords = ['requirement', 'prerequisite', 'admission', 'criteria', 'eligibility']
        
        for keyword in req_keywords:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for el in elements:
                parent = el.parent
                # 尝试获取包含要求的段落或列表
                if parent.name == 'p':
                    req_candidates.append(parent.get_text().strip())
                elif parent.name in ['li', 'div']:
                    req_candidates.append(parent.get_text().strip())
                # 尝试获取父元素后的列表项
                next_ul = parent.find_next('ul')
                if next_ul:
                    for li in next_ul.find_all('li'):
                        req_text = li.get_text().strip()
                        if len(req_text) > 10:
                            req_candidates.append(req_text)
        
        # 限制要求数量
        program_info["requirements"] = req_candidates[:10]  # 最多10个要求
        
        # 如果仍然没有找到足够的信息，使用默认值
        if not program_info["title"]:
            program_info["title"] = "Computer Science Program"
            print("未找到标题，使用默认值")
        
        if not program_info["description"]:
            program_info["description"] = "A comprehensive program covering fundamental and advanced topics in computer science."
            print("未找到描述，使用默认值")
        
        if not program_info["courses"]:
            print("未找到课程信息，使用默认数据")
            program_info["courses"] = [
                "Introduction to Computer Science - CS101",
                "Data Structures - CS201",
                "Algorithms - CS301",
                "Database Systems - CS401",
                "Software Engineering - CS501"
            ]
        
        if not program_info["credits"]:
            program_info["credits"] = "120 credits required for graduation"
            print("未找到学分要求，使用默认值")
        
        return jsonify(program_info)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {str(e)}")
        return jsonify({
            "error": f"Failed to fetch URL: {str(e)}",
            "title": "Computer Science Program",
            "description": "A comprehensive program covering fundamental and advanced topics in computer science.",
            "courses": [
                "Introduction to Computer Science - CS101",
                "Data Structures - CS201",
                "Algorithms - CS301",
                "Database Systems - CS401",
                "Software Engineering - CS501"
            ],
            "credits": "120 credits required for graduation"
        }), 200  # 返回200而不是500，这样前端仍然可以继续
    except Exception as e:
        print(f"Error processing webpage: {str(e)}")
        return jsonify({
            "error": f"Error processing webpage: {str(e)}",
            "title": "Computer Science Program",
            "description": "A comprehensive program covering fundamental and advanced topics in computer science.",
            "courses": [
                "Introduction to Computer Science - CS101",
                "Data Structures - CS201",
                "Algorithms - CS301",
                "Database Systems - CS401",
                "Software Engineering - CS501"
            ],
            "credits": "120 credits required for graduation"
        }), 200  # 返回200而不是500，这样前端仍然可以继续

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # 直接使用传入的数据
    student_data = {
        'major': data.get('major', ''),
        'completed_courses': data.get('completed_courses', []),
        'gpa': data.get('gpa', 3.0)
    }
    
    # 调用推荐器
    recommendations = recommender.recommend_courses(student_data)
    
    # 如果recommendations是课程代码列表，尝试获取完整课程信息
    if recommendations and isinstance(recommendations[0], str):
        # 尝试从数据库获取课程信息
        try:
            recommended_courses = Course.query.filter(Course.code.in_(recommendations)).all()
            if recommended_courses:
                return jsonify([course.to_dict() for course in recommended_courses])
        except Exception as e:
            print(f"Error fetching courses from database: {str(e)}")
    
    # 如果无法从数据库获取，或者推荐不是课程代码列表，返回简单的课程代码列表
    return jsonify([{"code": code, "name": f"Course {code}", "credits": 3} for code in recommendations])

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    message = data['message']
    response = chat_service.send_message(message)
    
    if response is None:
        return jsonify({"error": "Failed to get response from API"}), 500
    
    return jsonify({"response": response})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Logic for saving feedback to database can be added here
    return jsonify({"message": "Thank you for your feedback!"})

@app.route('/api/student/<int:student_id>/progress')
def get_student_progress(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    
    total_credits = sum(e.course.credits for e in enrollments)
    completed_credits = sum(e.course.credits for e in enrollments if e.status == "completed")
    
    return jsonify({
        "total_credits": total_credits,
        "completed_credits": completed_credits,
        "completion_percentage": (completed_credits / total_credits * 100) if total_credits > 0 else 0
    })

if __name__ == '__main__':
    # Get port, Hugging Face Space uses port 7860
    port = int(os.environ.get('PORT', 7860))
    # Set host to 0.0.0.0 to allow external access
    app.run(host='0.0.0.0', port=port, debug=False)
