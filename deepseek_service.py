import os
import requests
import json
from dotenv import load_dotenv
import time
import re

# First load environment variables from .env file
load_dotenv()

# Add delay to ensure environment variables have time to load
time.sleep(1)

# Safely get API key from environment variables
# 尝试多种可能的环境变量名称
API_KEY = os.getenv('API') or os.getenv('DEEPSEEK_API_KEY') or os.getenv('DEEPSEEK_API')

# 调试信息
print("API key loaded:", bool(API_KEY))  # Only print if exists, not the actual value
print("API key前10个字符:", API_KEY[:10] if API_KEY else "None")  # 只打印前10个字符，保护API密钥
print("Environment variables:", list(os.environ.keys()))  # 打印所有环境变量名称（不打印值）

# DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"  # Alternatively, use "deepseek-coder" for code-related tasks

# System prompt
SYSTEM_PROMPT = """You are a professional educational consultant assistant, specializing in helping students plan their learning paths and course selections. 

Your primary goal is to create highly personalized academic plans based on the student's specific situation. When responding:

1. ANALYZE the student's background information:
   - Current semester and academic year
   - Program/major and specialization
   - Completed courses and current knowledge level
   - Career goals and professional aspirations
   - Personal interests and learning preferences

2. PROVIDE a comprehensive learning plan that includes:
   - Detailed course recommendations for the next 3-4 semesters
   - Course codes, names, credit hours, and brief descriptions
   - Balanced course load (15-18 credits per semester)
   - Clear prerequisites and course sequencing
   - Elective suggestions aligned with career goals

3. EXPLAIN the rationale behind your recommendations:
   - How courses build on each other
   - Connection to career objectives
   - Skills development progression
   - Balance between required and elective courses

4. INCLUDE additional resources and opportunities:
   - Relevant internships and when to apply
   - Research projects or capstone experiences
   - Professional certifications to consider
   - Extracurricular activities that enhance learning

5. FORMAT your response using clear Markdown structure:
   - Separate sections for each semester
   - Bulleted lists for course details
   - Tables for schedule visualization
   - Bold text for important deadlines or requirements

Use a friendly, encouraging, and professional tone throughout your response, providing detailed explanations while remaining concise and focused on actionable advice."""

class ChatService:
    def __init__(self):
        """Initialize the chat service with API key and empty chat history"""
        self.api_key = API_KEY
        self.api_key_loaded = bool(self.api_key)
        self.api_key_valid = False
        self.chat_history = []
        
        print("Creating ChatService instance...")
        print(f"API密钥加载状态: {self.api_key_loaded}")
        print(f"API密钥前10个字符: {self.api_key[:10] if self.api_key else 'None'}")
        
        # Test API connection
        if self.api_key_loaded:
            try:
                print("Testing DeepSeek API connection...")
                self._test_api_connection()
                self.api_key_valid = True
                print("DeepSeek API connection successful!")
            except Exception as e:
                print(f"Error connecting to DeepSeek API: {str(e)}")
                self.api_key_valid = False
        
        print("ChatService instance created")
    
    def _test_api_connection(self):
        """Test connection to DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working?"}
            ],
            "max_tokens": 10
        }
        
        print(f"发送测试请求到DeepSeek API: URL={DEEPSEEK_API_URL}")
        print(f"请求头: {json.dumps(headers, default=str)}")
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    def send_message(self, message):
        """Send message to DeepSeek API and get reply"""
        if not self.api_key_loaded or not self.api_key_valid:
            # 不再使用硬编码的mock response，而是返回明确的错误信息
            print(f"API密钥问题: loaded={self.api_key_loaded}, valid={self.api_key_valid}")
            return self._generate_fallback_response(message)
        
        try:
            # Add user message to history
            self.chat_history.append({"role": "user", "content": message})
            
            # Prepare full message history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.chat_history
            
            # Call DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.9  # 提高temperature以增加多样性
            }
            
            print(f"发送请求到DeepSeek API: URL={DEEPSEEK_API_URL}, 模型={DEEPSEEK_MODEL}")
            print(f"请求头: {json.dumps(headers, default=str)}")
            print(f"请求数据: {json.dumps(data, default=str)[:200]}...")  # 只打印部分数据
            
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
            
            print(f"API响应状态码: {response.status_code}")
            if response.status_code != 200:
                print(f"API响应内容: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                assistant_message = response_data["choices"][0]["message"]["content"]
                
                # Add assistant reply to history
                self.chat_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
            else:
                print(f"API request failed with status code {response.status_code}: {response.text}")
                return self._generate_fallback_response(message)
                
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return self._generate_fallback_response(message)
    
    def _generate_fallback_response(self, message):
        """生成备用响应，当API不可用时使用"""
        # 提取关键信息
        message_lower = message.lower()
        
        # 提取URL（如果存在）
        program_url = ""
        if "http" in message_lower:
            url_match = re.search(r'https?://[^\s]+', message_lower)
            if url_match:
                program_url = url_match.group(0)
        
        # 提取当前课程（如果存在）
        current_courses = []
        course_pattern = r'\b[A-Z]{2,4}\s*\d{3,4}[A-Z]?\b'
        if re.search(course_pattern, message_lower, re.IGNORECASE):
            current_courses = re.findall(course_pattern, message_lower, re.IGNORECASE)
        
        # 提取学期信息
        current_semester = ""
        if "semester" in message_lower:
            semester_pattern = r'(?:current\s+semester|semester)[:\s]+([a-zA-Z]+\s+\d{4})'
            semester_match = re.search(semester_pattern, message_lower, re.IGNORECASE)
            if semester_match:
                current_semester = semester_match.group(1)
            else:
                # 尝试更宽松的匹配
                semester_pattern = r'(?:spring|fall|summer|winter)\s+\d{4}'
                semester_match = re.search(semester_pattern, message_lower, re.IGNORECASE)
                if semester_match:
                    current_semester = semester_match.group(0)
        
        if not current_semester:
            current_semester = "Fall 2025"  # 默认值
        
        # 提取专业信息
        program = ""
        program_patterns = [
            r'(?:program|major)[:\s]+([a-zA-Z\s]+)',
            r'studying\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+(?:degree|program|major)'
        ]
        
        for pattern in program_patterns:
            program_match = re.search(pattern, message_lower, re.IGNORECASE)
            if program_match:
                program = program_match.group(1).strip()
                break
        
        if not program:
            # 尝试从URL中提取
            if "computer" in program_url.lower() or "cs" in program_url.lower():
                program = "Computer Science"
            elif "business" in program_url.lower():
                program = "Business Administration"
            elif "engineering" in program_url.lower():
                program = "Engineering"
            else:
                program = "Computer Science"  # 默认值
        
        # 提取职业目标
        career = ""
        career_patterns = [
            r'(?:career|job)[:\s]+([a-zA-Z\s]+)',
            r'become\s+(?:a|an)\s+([a-zA-Z\s]+)',
            r'work\s+as\s+(?:a|an)\s+([a-zA-Z\s]+)'
        ]
        
        for pattern in career_patterns:
            career_match = re.search(pattern, message_lower, re.IGNORECASE)
            if career_match:
                career = career_match.group(1).strip()
                break
        
        if not career:
            if "ml" in message_lower or "machine learning" in message_lower:
                career = "Machine Learning Engineer"
            elif "web" in message_lower:
                career = "Web Developer"
            elif "data" in message_lower:
                career = "Data Scientist"
            elif "security" in message_lower or "cyber" in message_lower:
                career = "Cybersecurity Specialist"
            else:
                career = "Software Developer"  # 默认值
        
        # 提取学分限制（如果存在）
        credit_limit = None
        credit_pattern = r'maximum\s+credit.*?(\d+)\s+credit'
        if re.search(credit_pattern, message_lower, re.IGNORECASE):
            credit_match = re.search(credit_pattern, message_lower, re.IGNORECASE)
            if credit_match:
                credit_limit = int(credit_match.group(1))
        
        # 根据消息内容确定需要生成的内容类型
        if "course plan" in message_lower or "academic" in message_lower or "courses" in message_lower:
            return self._generate_course_plan_fallback(current_semester, program, career, current_courses, credit_limit, program_url)
        elif "career" in message_lower or "job" in message_lower or "profession" in message_lower:
            return self._generate_career_advice_fallback(program, career, message)
        else:
            # 默认响应
            return f"""# API Connection Issue

I apologize, but I'm currently unable to connect to the DeepSeek API to provide a fully personalized response. Here's what I understand from your request:

- **Current Semester**: {current_semester}
- **Program/Major**: {program}
- **Career Goal**: {career}
- **Current Courses**: {', '.join(current_courses) if current_courses else 'None specified'}

To get a personalized academic plan or career advice, please ensure the API key is configured correctly in the environment variables.

In the meantime, I can still help with general questions about academic planning, course selection strategies, or career development. Please feel free to ask!"""
    
    def _generate_course_plan_fallback(self, semester, program, career, current_courses, credit_limit, program_url):
        """生成备用课程计划，当API不可用时使用"""
        # 解析学期和年份
        parts = semester.split()
        if len(parts) >= 2:
            term = parts[0].lower()  # fall或spring
            try:
                year = int(parts[1])
            except ValueError:
                year = 2025
        else:
            term = "fall"
            year = 2025
        
        # 确定学分限制
        max_credits = 16  # 默认值
        if credit_limit:
            max_credits = credit_limit
        
        # 生成未来6个学期
        semesters = []
        for i in range(6):
            if i == 0:
                semesters.append(f"{term.capitalize()} {year}")
            else:
                if term.lower() == "fall":
                    term = "Spring"
                    year += 1
                else:  # spring
                    term = "Fall"
                semesters.append(f"{term} {year}")
        
        # 构建响应
        response = f"""# Personalized Course Plan for {program}

## API Connection Issue

I apologize, but I'm currently unable to connect to the DeepSeek API to provide a fully personalized course plan. However, I've created a simplified plan based on the information you provided:

- **Program URL**: {program_url if program_url else 'Not provided'}
- **Current Semester**: {semester}
- **Career Goal**: {career}
- **Current Courses**: {', '.join(current_courses) if current_courses else 'None specified'}
- **Credit Limit**: {f'{credit_limit} credits per semester' if credit_limit else 'Standard load (15-18 credits)'}

Here's a general course plan that might help guide your academic journey:

"""
        
        # 为每个学期添加课程信息
        for i, semester in enumerate(semesters):
            # 调整每学期的课程数量，确保不超过学分限制
            courses_per_semester = max(1, int(max_credits / 4))  # 假设平均每门课4学分
            total_credits = min(max_credits, courses_per_semester * 4)
            
            response += f"""### **{semester}**
Total Credits: {total_credits}

"""
            # 添加课程
            for j in range(1, courses_per_semester + 1):
                if i == 0 and j <= len(current_courses):
                    # 使用用户当前正在修的课程
                    course_code = current_courses[j-1].upper()
                    response += f"""{j}. **Current Course {j}** ({course_code}) - 4 credits
   - Current course you are taking.

"""
                else:
                    # 根据职业目标和学期生成课程
                    if "machine learning" in career.lower() or "ml" in career.lower() or "ai" in career.lower() or "data" in career.lower():
                        course_types = ["AI", "ML", "Data", "Algorithm", "Statistics"]
                    elif "web" in career.lower() or "frontend" in career.lower() or "backend" in career.lower():
                        course_types = ["Web", "UI/UX", "Database", "Network", "Security"]
                    elif "security" in career.lower() or "cyber" in career.lower():
                        course_types = ["Security", "Network", "Cryptography", "Systems", "Ethics"]
                    else:
                        course_types = ["Core", "Advanced", "Specialized", "Project", "Research"]
                    
                    course_type = course_types[(i + j) % len(course_types)]
                    course_level = 100 * (i + 1) + j * 10
                    
                    # 随机生成不同的学分值，使图表更有变化
                    credit_value = 3 if j % 2 == 0 else 4
                    
                    response += f"""{j}. **{course_type} Course {j}** ({program[:2].upper()}{course_level}) - {credit_value} credits
   - {'Advanced' if i > 2 else 'Fundamental'} course related to {course_type.lower()} concepts in {program}.

"""
        
        # 添加额外建议
        response += f"""## Additional Recommendations

### Internships
Apply for internships related to {career} to gain practical experience.

### Certifications
Consider professional certifications that will enhance your marketability in {career}.

### Extracurriculars
Join student organizations related to {program} to build your network.

## Summary

This is a simplified course plan based on limited information. For a more detailed and personalized plan, please ensure the API key is configured correctly.

To get a fully personalized course plan that takes into account specific program requirements, prerequisites, and your individual goals, please try again when the API connection is restored.
"""
        
        return response
    
    def _generate_career_advice_fallback(self, program, career, interests):
        """生成备用职业建议，当API不可用时使用"""
        response = f"""# Career Development Plan for {career}

## API Connection Issue

I apologize, but I'm currently unable to connect to the DeepSeek API to provide fully personalized career advice. However, I've created a simplified career development plan based on the information you provided:

- **Program/Major**: {program}
- **Career Goal**: {career}

Here's a general career development plan that might help guide your professional journey:

## Key Skills to Develop

1. **Technical Skills**
   - Core {program} knowledge and principles
   - Specialized skills related to {career}
   - Tools and technologies commonly used in {career} roles

2. **Soft Skills**
   - Communication and teamwork
   - Problem-solving and critical thinking
   - Time management and organization

## Learning Resources

1. **Online Courses**
   - Courses related to {program} fundamentals
   - Specialized courses for {career} roles

2. **Books**
   - Industry-standard texts for {program}
   - Career development guides for {career} professionals

## Career Path Milestones

1. **Short-term (0-1 years)**
   - Complete fundamental courses in {program}
   - Build a portfolio showcasing relevant projects
   - Obtain an entry-level position related to {career}

2. **Medium-term (1-3 years)**
   - Gain experience in your chosen field
   - Develop specialized expertise
   - Expand your professional network

3. **Long-term (3-5 years)**
   - Move into more senior roles
   - Consider advanced degrees or certifications
   - Develop leadership skills

For a more detailed and personalized career development plan, please ensure the API key is configured correctly and try again when the API connection is restored.
"""
        
        return response
    
    def _generate_course_plan(self, semester, program, career, interests):
        """使用DeepSeek API生成完整的课程推荐计划"""
        # 提取URL（如果存在）
        program_url = ""
        if "http" in interests:
            url_match = re.search(r'https?://[^\s]+', interests)
            if url_match:
                program_url = url_match.group(0)
        
        # 提取当前课程（如果存在）
        current_courses = []
        course_pattern = r'\b[A-Z]{2,4}\s*\d{3,4}[A-Z]?\b'
        if re.search(course_pattern, interests, re.IGNORECASE):
            current_courses = re.findall(course_pattern, interests, re.IGNORECASE)
        
        # 提取学分限制（如果存在）
        credit_limit = None
        credit_pattern = r'maximum\s+credit.*?(\d+)\s+credit'
        if re.search(credit_pattern, interests, re.IGNORECASE):
            credit_match = re.search(credit_pattern, interests, re.IGNORECASE)
            if credit_match:
                credit_limit = int(credit_match.group(1))
        
        # 使用DeepSeek API生成课程计划
        prompt = f"""
You are an academic planning assistant. Based on the following information, create a personalized course plan:

PROGRAM URL: {program_url}
CURRENT SEMESTER: {semester}
CURRENT COURSES: {', '.join(current_courses) if current_courses else 'None specified'}
CAREER GOAL: {career}
ADDITIONAL REQUIREMENTS: {interests}
{f'CREDIT LIMIT PER SEMESTER: {credit_limit} credits' if credit_limit else ''}

Instructions:
1. Analyze the program URL to understand degree requirements, course offerings, and prerequisites.
2. Create a semester-by-semester plan starting from {semester} through graduation.
3. For each semester, recommend specific courses with their codes, names, and credit hours.
4. Ensure prerequisites are met and courses are balanced each semester.
5. Align elective choices with the career goal of becoming a {career}.
6. If a credit limit per semester is specified, ensure each semester doesn't exceed that limit.
7. Include recommendations for internships, certifications, and extracurricular activities.

Format your response in Markdown with:
- Each semester section MUST start with '### **Semester Name**'
- Each course MUST be listed as '1. **Course Name** (COURSE101) - X credits'
- Include a short description for each course
- Include 'Total Credits: XX' for each semester
- Include an 'Additional Recommendations' section
- Include a 'Summary' section
"""
        return self.send_message(prompt)
    
    def _generate_career_advice(self, program, career, interests):
        """使用DeepSeek API生成个性化职业发展建议"""
        # 使用DeepSeek API生成职业建议
        prompt = f"""
Based on a {program} background, generate a detailed career development plan for becoming a {career}.
- Include key technical and soft skills needed.
- Recommend specific online courses, books, and resources.
- Outline short-term, mid-term, and long-term career goals.
- Provide practical advice on gaining industry experience.
- Include information about interests in: {interests}
- Use a professional but friendly tone.
- Format the response in Markdown with clear sections.
"""
        return self.send_message(prompt)

# Create a singleton instance
print("Creating ChatService instance...")
chat_service = ChatService()
print("ChatService instance created") 