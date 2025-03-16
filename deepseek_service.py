import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# First load environment variables from .env file
load_dotenv()

# Add delay to ensure environment variables have time to load
time.sleep(1)

# Safely get API key from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

print("GOOGLE_API_KEY loaded:", bool(GOOGLE_API_KEY))  # Only print if exists, not the actual value

# Configure Gemini
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Error configuring Gemini API: {str(e)}")
else:
    print("WARNING: GOOGLE_API_KEY is missing! Set it as an environment variable.")

SYSTEM_PROMPT = """You are a professional educational consultant assistant, specializing in helping students plan their learning paths and course selections. You should:
1. Provide personalized recommendations based on students' completed courses and interests
2. Consider course difficulty, prerequisites, and career development directions
3. Give specific course recommendations and learning plans
4. Use a friendly and professional tone, providing detailed explanations"""

# Mock responses for when API key is invalid
MOCK_RESPONSES = {
    "course_plan": """# Personalized Course Plan

Based on your information, here's a customized course plan:

## Recommended Courses

1. **Data Structures & Algorithms** (CS201) - 4 credits
   - This is a fundamental course for any programming-related career

2. **Software Engineering** (SE301) - 3 credits
   - Learn software development lifecycle and project management skills

3. **Web Development** (WD401) - 4 credits
   - Learn frontend and backend development technologies

4. **Introduction to AI** (AI301) - 3 credits
   - Based on your interest in AI, this course will provide AI fundamentals

## Learning Path

Current semester:
- Data Structures & Algorithms
- Software Engineering

Next semester:
- Web Development
- Introduction to AI

## Career Advice

As a future software developer, I recommend:
1. Participate in open-source projects to gain practical experience
2. Build a personal project portfolio to showcase your skills
3. Look for internship opportunities to gain industry experience

Good luck with your studies!""",

    "career_advice": """# Career Development Plan

Based on your educational background and interests, here's a personalized career development plan:

## Key Skills to Develop

1. **Technical Skills**
   - Programming languages: Python, JavaScript, Java
   - Web development: HTML/CSS, React, Node.js
   - Database management: SQL, MongoDB

2. **Soft Skills**
   - Communication and teamwork
   - Problem-solving and critical thinking
   - Time management and organization

## Learning Resources

1. **Online Courses**
   - Coursera: "Machine Learning" by Stanford University
   - Udemy: "The Complete Web Developer Bootcamp"
   - edX: "CS50's Introduction to Computer Science" by Harvard

2. **Books**
   - "Clean Code" by Robert C. Martin
   - "Cracking the Coding Interview" by Gayle Laakmann McDowell
   - "The Pragmatic Programmer" by Andrew Hunt and David Thomas

## Career Path Milestones

1. **Short-term (0-1 years)**
   - Complete fundamental programming courses
   - Build a portfolio with 2-3 projects
   - Obtain an internship or entry-level position

2. **Medium-term (1-3 years)**
   - Gain experience in a specific technology stack
   - Contribute to open-source projects
   - Consider specialization in AI, cloud, or cybersecurity

3. **Long-term (3-5 years)**
   - Move into a senior role or technical leadership
   - Consider advanced degrees if aligned with goals
   - Develop mentorship and leadership skills

Good luck with your career journey!""",

    "feedback_response": "Thank you for your feedback! We appreciate your input and will use it to improve our services."
}

class ChatService:
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.api_key_loaded = self.api_key is not None
        self.api_key_valid = False
        print(f"GOOGLE_API_KEY loaded: {self.api_key_loaded}")
        
        # Initialize chat session
        self.chat_session = None
        
        if self.api_key_loaded:
            try:
                print("Creating ChatService instance...")
                # Ensure API key is configured
                genai.configure(api_key=self.api_key)
                
                # Try different model name formats
                model_names = [
                    "gemini-1.5-pro",
                    "models/gemini-1.5-pro",
                    "gemini-pro",
                    "models/gemini-pro",
                    "gemini-1.5-flash",
                    "models/gemini-1.5-flash"
                ]
                
                # Try each model name until successful
                for model_name in model_names:
                    try:
                        print(f"Trying model: {model_name}")
                        self.model = genai.GenerativeModel(model_name=model_name)
                        self.chat_session = self.model.start_chat(history=[])
                        print(f"Successfully initialized with model: {model_name}")
                        
                        # Send system prompt
                        system_prompt = """You are StudyPath AI, an academic planning assistant. 
                        Your goal is to help students plan their academic journey, recommend courses, 
                        and provide guidance on career paths. Be helpful, informative, and supportive."""
                        
                        self.chat_session.send_message(system_prompt)
                        self.api_key_valid = True
                        break
                    except Exception as e:
                        print(f"Failed to initialize with model {model_name}: {str(e)}")
                        continue
                
                if not self.chat_session:
                    print("Failed to initialize with any model")
            except Exception as e:
                print(f"Error initializing chat service: {str(e)}")
                self.chat_session = None
        else:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
    
    def send_message(self, message):
        # Check if API key is valid and chat session is initialized
        if self.api_key_valid and self.chat_session:
            try:
                response = self.chat_session.send_message(message)
                return response.text
            except Exception as e:
                print(f"Error sending message: {str(e)}")
                return self._get_mock_response(message)
        else:
            # Use mock responses when API key is invalid
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
        """Generate a personalized course plan based on extracted information"""
        
        # Define courses based on program
        courses = {
            "Computer Science": [
                {"name": "Data Structures & Algorithms", "code": "CS201", "credits": 4},
                {"name": "Software Engineering", "code": "SE301", "credits": 3},
                {"name": "Web Development", "code": "WD401", "credits": 4},
                {"name": "Introduction to AI", "code": "AI301", "credits": 3},
                {"name": "Database Systems", "code": "DB401", "credits": 3},
                {"name": "Computer Networks", "code": "CN301", "credits": 3}
            ],
            "Business Administration": [
                {"name": "Principles of Management", "code": "BUS201", "credits": 3},
                {"name": "Financial Accounting", "code": "ACC301", "credits": 4},
                {"name": "Marketing Fundamentals", "code": "MKT301", "credits": 3},
                {"name": "Business Analytics", "code": "BA401", "credits": 3},
                {"name": "Organizational Behavior", "code": "ORG301", "credits": 3}
            ],
            "Engineering": [
                {"name": "Engineering Mathematics", "code": "EM201", "credits": 4},
                {"name": "Mechanics of Materials", "code": "MM301", "credits": 3},
                {"name": "Thermodynamics", "code": "TD301", "credits": 4},
                {"name": "Control Systems", "code": "CS401", "credits": 3},
                {"name": "Engineering Design", "code": "ED401", "credits": 4}
            ]
        }
        
        # Select program courses or default to Computer Science
        program_courses = courses.get(program, courses["Computer Science"])
        
        # Select courses based on interests and career
        selected_courses = []
        for course in program_courses:
            course_name_lower = course["name"].lower()
            if any(interest.lower() in course_name_lower for interest in interests.split(", ")):
                selected_courses.append(course)
        
        # If we couldn't match interests, just take the first 4 courses
        if len(selected_courses) < 2:
            selected_courses = program_courses[:4]
        else:
            selected_courses = selected_courses[:4]  # Limit to 4 courses
        
        # Generate the response
        response = f"""# Personalized Course Plan for {program}

Based on your information (Semester: {semester}, Career Goal: {career}, Interests: {interests}), here's a customized course plan:

## Recommended Courses

"""
        
        # Add course details
        for i, course in enumerate(selected_courses, 1):
            response += f"{i}. **{course['name']}** ({course['code']}) - {course['credits']} credits\n"
            
            # Add course description based on name
            if "data" in course["name"].lower():
                response += "   - Learn fundamental data structures and algorithm design principles\n\n"
            elif "software" in course["name"].lower():
                response += "   - Master software development lifecycle and project management skills\n\n"
            elif "web" in course["name"].lower():
                response += "   - Develop skills in frontend and backend web technologies\n\n"
            elif "ai" in course["name"].lower() or "machine" in course["name"].lower():
                response += "   - Explore artificial intelligence concepts and applications\n\n"
            elif "database" in course["name"].lower():
                response += "   - Learn database design, SQL, and data management principles\n\n"
            elif "network" in course["name"].lower():
                response += "   - Understand computer networking protocols and architecture\n\n"
            elif "management" in course["name"].lower():
                response += "   - Develop fundamental management and leadership skills\n\n"
            elif "accounting" in course["name"].lower():
                response += "   - Master financial accounting principles and practices\n\n"
            elif "marketing" in course["name"].lower():
                response += "   - Learn key marketing strategies and consumer behavior analysis\n\n"
            elif "analytics" in course["name"].lower():
                response += "   - Develop data analysis skills for business decision-making\n\n"
            elif "mathematics" in course["name"].lower():
                response += "   - Build strong mathematical foundations for engineering applications\n\n"
            elif "mechanics" in course["name"].lower():
                response += "   - Study the behavior of materials under various loading conditions\n\n"
            elif "thermodynamics" in course["name"].lower():
                response += "   - Understand energy transfer and conversion principles\n\n"
            elif "control" in course["name"].lower():
                response += "   - Learn to design and analyze control systems\n\n"
            elif "design" in course["name"].lower():
                response += "   - Apply engineering principles to practical design challenges\n\n"
            else:
                response += "   - Essential course for your program and career goals\n\n"
        
        # Add learning path
        response += f"""## Learning Path

{semester}:
- {selected_courses[0]['name']}
- {selected_courses[1]['name']}

Next semester:
- {selected_courses[2]['name'] if len(selected_courses) > 2 else 'Elective course based on performance'}
- {selected_courses[3]['name'] if len(selected_courses) > 3 else 'Elective course based on interests'}

## Career Advice

As a future {career}, I recommend:
1. Participate in projects that demonstrate your skills in {interests}
2. Build a portfolio showcasing your work in {selected_courses[0]['name']} and {selected_courses[1]['name']}
3. Look for internship opportunities related to {career}

Good luck with your studies in {program}!"""
        
        return response
    
    def _generate_career_advice(self, program, career, interests):
        """Generate personalized career advice based on extracted information"""
        
        # Define skills based on career
        skills = {
            "Software Developer": [
                "Programming (Python, JavaScript, Java)",
                "Web development frameworks (React, Angular, Vue)",
                "Version control (Git)",
                "Problem-solving and algorithms",
                "Database management"
            ],
            "Data Scientist": [
                "Statistical analysis",
                "Machine learning algorithms",
                "Python and R programming",
                "Data visualization",
                "Big data technologies"
            ],
            "Business Analyst": [
                "Data analysis",
                "Requirements gathering",
                "SQL and database querying",
                "Business process modeling",
                "Communication and presentation"
            ],
            "Engineer": [
                "Technical design and documentation",
                "CAD software proficiency",
                "Mathematical modeling",
                "Problem-solving",
                "Project management"
            ]
        }
        
        # Select career skills or default to Software Developer
        career_skills = skills.get(career, skills["Software Developer"])
        
        # Generate the response
        response = f"""# Career Development Plan for {career}

Based on your background in {program} and interests in {interests}, here's a personalized career development plan:

## Key Skills to Develop

1. **Technical Skills**
"""
        
        # Add technical skills
        for i, skill in enumerate(career_skills[:3], 1):
            response += f"   - {skill}\n"
        
        response += f"""
2. **Soft Skills**
   - Communication and teamwork
   - Problem-solving and critical thinking
   - Time management and organization

## Learning Resources

1. **Online Courses**
"""
        
        # Add course recommendations based on interests and career
        if "software" in career.lower() or "developer" in career.lower() or "programming" in interests.lower():
            response += """   - Coursera: "Full-Stack Web Development with React" by Johns Hopkins University
   - Udemy: "The Complete Web Developer Bootcamp"
   - edX: "CS50's Introduction to Computer Science" by Harvard
"""
        elif "data" in career.lower() or "machine learning" in interests.lower() or "ai" in interests.lower():
            response += """   - Coursera: "Machine Learning" by Stanford University
   - Udemy: "Python for Data Science and Machine Learning Bootcamp"
   - edX: "Data Science Essentials" by Microsoft
"""
        elif "business" in career.lower() or "management" in interests.lower():
            response += """   - Coursera: "Business Foundations" by Wharton
   - Udemy: "Business Analysis Fundamentals"
   - edX: "Business Analytics for Decision Making" by Columbia
"""
        elif "engineer" in career.lower():
            response += """   - Coursera: "Engineering Systems in Motion" by Georgia Tech
   - Udemy: "The Complete Engineering Drawing Course"
   - edX: "Engineering Mechanics" by MIT
"""
        else:
            response += """   - Coursera: "Professional Skills for the Workplace"
   - Udemy: "The Complete Job, Interview, Resume & Network Guide"
   - edX: "Career Development: Skills for Success"
"""
        
        response += f"""
2. **Books**
   - "The Pragmatic Programmer" by Andrew Hunt and David Thomas
   - "Cracking the Coding Interview" by Gayle Laakmann McDowell
   - "Soft Skills: The Software Developer's Life Manual" by John Sonmez

## Career Path Milestones

1. **Short-term (0-1 years)**
   - Complete fundamental courses in {program}
   - Build a portfolio with 2-3 projects showcasing {interests}
   - Obtain an internship or entry-level position related to {career}

2. **Medium-term (1-3 years)**
   - Gain experience in {interests}
   - Contribute to open-source or community projects
   - Consider specialization in {interests.split(", ")[0] if ", " in interests else interests}

3. **Long-term (3-5 years)**
   - Move into a senior {career} role
   - Consider advanced degrees or certifications if aligned with goals
   - Develop mentorship and leadership skills

Good luck with your career journey as a {career}!"""
        
        return response

# Create a singleton instance
print("Creating ChatService instance...")
chat_service = ChatService()
print("ChatService instance created") 