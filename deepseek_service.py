import os
import requests
import json
from dotenv import load_dotenv
import time

# First load environment variables from .env file
load_dotenv()

# Add delay to ensure environment variables have time to load
time.sleep(1)

# Safely get API key from environment variables
API_KEY = os.getenv('API')

print("API key loaded:", bool(API_KEY))  # Only print if exists, not the actual value

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
        self.api_key = API_KEY
        self.api_key_loaded = self.api_key is not None
        self.api_key_valid = False
        self.chat_history = []
        
        # Test API key connection
        if self.api_key_loaded:
            try:
                print("Testing DeepSeek API connection...")
                self._test_api_connection()
                self.api_key_valid = True
                print("DeepSeek API connection successful")
            except Exception as e:
                print(f"Error connecting to DeepSeek API: {str(e)}")
                self.api_key_valid = False
        else:
            print("Warning: API key not found in environment variables")
    
    def _test_api_connection(self):
        """Test API connection"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    def send_message(self, message):
        """Send message to DeepSeek API and get reply"""
        if not self.api_key_loaded or not self.api_key_valid:
            return self._get_mock_response(message)
        
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
                "temperature": 0.7
            }
            
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                assistant_message = response_data["choices"][0]["message"]["content"]
                
                # Add assistant reply to history
                self.chat_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
            else:
                print(f"API request failed with status code {response.status_code}: {response.text}")
                return self._get_mock_response(message)
                
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return self._get_mock_response(message)
    
    def _get_mock_response(self, message):
        """Provide a mock response based on the message content"""
        message_lower = message.lower()
        
        # Extract key information from the message
        current_semester = ""
        program = ""
        career_goal = ""
        interests = ""
        
        # Try to extract semester information
        if "semester" in message_lower:
            semester_index = message_lower.find("semester")
            semester_end = message_lower.find("\n", semester_index)
            if semester_end == -1:
                semester_end = len(message_lower)
            current_semester = message_lower[semester_index-20:semester_end].strip()
            if ":" in current_semester:
                current_semester = current_semester.split(":")[-1].strip()
        
        # Try to extract program information
        if "program" in message_lower:
            program_index = message_lower.find("program")
            program_end = message_lower.find("\n", program_index)
            if program_end == -1:
                program_end = len(message_lower)
            program = message_lower[program_index-20:program_end].strip()
            if ":" in program:
                program = program.split(":")[-1].strip()
        
        # Try to extract career goal
        if "career" in message_lower:
            career_index = message_lower.find("career")
            career_end = message_lower.find("\n", career_index)
            if career_end == -1:
                career_end = len(message_lower)
            career_goal = message_lower[career_index-20:career_end].strip()
            if ":" in career_goal:
                career_goal = career_goal.split(":")[-1].strip()
        elif "job" in message_lower:
            job_index = message_lower.find("job")
            job_end = message_lower.find("\n", job_index)
            if job_end == -1:
                job_end = len(message_lower)
            career_goal = message_lower[job_index-20:job_end].strip()
            if ":" in career_goal:
                career_goal = career_goal.split(":")[-1].strip()
        
        # Try to extract interests
        if "interest" in message_lower:
            interest_index = message_lower.find("interest")
            interest_end = message_lower.find("\n", interest_index)
            if interest_end == -1:
                interest_end = len(message_lower)
            interests = message_lower[interest_index-20:interest_end].strip()
            if ":" in interests:
                interests = interests.split(":")[-1].strip()
        
        # If we couldn't extract specific information, look for common keywords
        if not any([current_semester, program, career_goal, interests]):
            keywords = ["computer science", "software", "web", "data", "ai", "machine learning", 
                       "engineering", "business", "math", "science", "art", "design", "medicine"]
            found_keywords = []
            for keyword in keywords:
                if keyword in message_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                if not interests:
                    interests = ", ".join(found_keywords)
                if not program and "computer" in found_keywords:
                    program = "Computer Science"
                elif not program and "business" in found_keywords:
                    program = "Business Administration"
                elif not program and "engineering" in found_keywords:
                    program = "Engineering"
        
        # Default values if we couldn't extract anything
        if not current_semester:
            current_semester = "Fall 2025"
        if not program:
            program = "Computer Science"
        if not career_goal:
            career_goal = "Software Developer"
        if not interests:
            interests = "programming, web development, AI"
        
        # Generate appropriate response based on message content
        if "course plan" in message_lower or "academic" in message_lower or "courses" in message_lower:
            return self._generate_course_plan(current_semester, program, career_goal, interests)
        elif "career" in message_lower or "job" in message_lower or "profession" in message_lower:
            return self._generate_career_advice(program, career_goal, interests)
        elif "feedback" in message_lower:
            return "Thank you for your feedback! We appreciate your input and will use it to improve our services."
        else:
            # Default response
            return f"""Thank you for your message. I'm StudyPath AI, your academic planning assistant.

Based on what I understand, you're interested in {program} with a focus on {interests}.

I can help you with:
- Course planning and recommendations for {program}
- Career path guidance toward becoming a {career_goal}
- Academic resources for {interests}
- Study strategies for success in {current_semester}

Please provide more details about your academic background and goals so I can give you more personalized advice."""
    
    def _generate_course_plan(self, semester, program, career, interests):
        """使用DeepSeek API生成完整的课程推荐计划"""
        # 如果API可用，直接使用DeepSeek生成课程计划
        if self.api_key_valid:
            prompt = f"""
Design a full university course plan for a {program} major.
- Assume the student is starting from {semester}.
- Balance each semester with 15-18 credits.
- Include both core and elective courses.
- Align electives with career goal: {career} and interests: {interests}.
- Output in structured Markdown format with:
  - Each semester section MUST start with '### **Semester Name**'
  - Each course MUST be listed as '1. **Course Name** (COURSE101) - 3 credits'
  - Include a short description for each course
  - Include 'Total Credits: XX' for each semester
  - Include an 'Additional Recommendations' section
  - Include a 'Summary' section
"""
            return self.send_message(prompt)
        
        # 如果API不可用，使用简化的模拟响应
        # 解析用户输入的学期，格式应为"Fall 2025"或"Spring 2026"等
        current_semester = semester
        if not current_semester or "semester" in current_semester.lower():
            current_semester = "Fall 2025"
        
        # 提取学期和年份
        parts = current_semester.split()
        if len(parts) >= 2:
            term = parts[0].lower()  # fall或spring
            try:
                year = int(parts[1])
            except ValueError:
                year = 2025
        else:
            term = "fall"
            year = 2025
        
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
        
        # 构建简化的响应
        response = f"""# Personalized Course Plan for {program}

Based on your interests in {interests} and career goal as a {career}, here's a comprehensive course plan from {semesters[0]} through graduation:

"""
        
        # 为每个学期添加简化的课程信息 - 确保格式与parseAIResponse函数匹配
        for i, semester in enumerate(semesters):
            total_credits = 16  # 默认学分总数
            response += f"""### **{semester}**
Total Credits: {total_credits}

1. **Core {program} Course {i*2+1}** (CORE{201+i*100}) - 4 credits
   - Essential course covering fundamental concepts in {program}.

2. **Core {program} Course {i*2+2}** (CORE{202+i*100}) - 3 credits
   - Advanced topics building on previous knowledge in {program}.

3. **Elective related to {career}** (ELEC{203+i*100}) - 3 credits
   - Specialized course aligned with your career goals.

4. **General Education Course** (GEN{204+i*100}) - 3 credits
   - Broadens your knowledge beyond your major.

5. **Professional Development** (PROF{205+i*100}) - 3 credits
   - Builds essential skills for your future career.

"""
        
        # 添加额外建议 - 确保格式与parseAIResponse函数匹配
        response += f"""## Additional Recommendations

### Internships
Apply for internships related to {career} to gain practical experience.

### Certifications
Consider professional certifications that will enhance your marketability in {career}.

### Extracurriculars
Join student organizations related to {program} to build your network.

## Summary

This plan provides a balanced approach to your {program} education, with courses that will prepare you for a career as a {career}. Adjust as needed based on your university's specific requirements.

Note: This is a simplified plan generated without API access. For a more detailed and personalized plan, please ensure the API key is configured correctly.
"""
        
        return response
    
    def _generate_career_advice(self, program, career, interests):
        """使用DeepSeek API生成个性化职业发展建议"""
        # 如果API可用，直接使用DeepSeek生成职业建议
        if self.api_key_valid:
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
        
        # 如果API不可用，使用简化的模拟响应
        response = f"""# Career Development Plan for {career}

Based on your background in {program} and interests in {interests}, here's a personalized career development plan:

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
   - Skill-building courses in {interests}

2. **Books**
   - Industry-standard texts for {program}
   - Career development guides for {career} professionals
   - Technical references related to your field

## Career Path Milestones

1. **Short-term (0-1 years)**
   - Complete fundamental courses in {program}
   - Build a portfolio showcasing {interests}
   - Obtain an entry-level position related to {career}

2. **Medium-term (1-3 years)**
   - Gain experience in your chosen field
   - Develop specialized expertise in {interests}
   - Expand your professional network

3. **Long-term (3-5 years)**
   - Move into more senior roles
   - Consider advanced degrees or certifications
   - Develop leadership skills

Note: This is a simplified plan generated without API access. For a more detailed and personalized plan, please ensure the API key is configured correctly.
"""
        
        return response

def get_courses_for_program(program_name):
    """从数据库或外部API获取指定专业的课程"""
    # 首先检查数据库中是否有该专业的课程
    courses = database.query_courses(program_name)
    
    if courses:
        return courses
    else:
        # 如果数据库中没有，使用AI生成合理的课程建议
        ai_generated_courses = generate_courses_with_ai(program_name)
        # 可选：将生成的课程保存到数据库中以供将来使用
        database.save_courses(program_name, ai_generated_courses)
        return ai_generated_courses

# Create a singleton instance
print("Creating ChatService instance...")
chat_service = ChatService()
print("ChatService instance created") 