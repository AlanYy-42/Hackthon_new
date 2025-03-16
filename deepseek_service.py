import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# 首先加载.env文件中的环境变量
load_dotenv()

# 使用Google AI API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# 添加延迟，确保环境变量有时间加载
time.sleep(1)

# 再次尝试获取API密钥（以防第一次尝试失败）
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

print("GOOGLE_API_KEY loaded:", bool(GOOGLE_API_KEY))  # 只打印是否存在，不打印实际值

# 配置Gemini
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Error configuring Gemini API: {str(e)}")

SYSTEM_PROMPT = """你是一个专业的教育顾问助手，专门帮助学生规划他们的学习路径和课程选择。你应该：
1. 基于学生已修课程和兴趣提供个性化建议
2. 考虑课程难度、先修要求和职业发展方向
3. 给出具体的课程推荐和学习规划
4. 使用友好专业的语气，提供详细的解释
请用中文回答问题。"""

class ChatService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.api_key_loaded = self.api_key is not None
        print(f"GOOGLE_API_KEY loaded: {self.api_key_loaded}")
        
        # Initialize chat session
        self.chat_session = None
        
        if self.api_key_loaded:
            try:
                print("Initializing chat service with API key...")
                genai.configure(api_key=self.api_key)
                
                # List available models
                models = genai.list_models()
                model_names = [model.name for model in models]
                print(f"Available models: {model_names}")
                
                # Create a generative model instance
                print("Creating GenerativeModel instance...")
                self.model = genai.GenerativeModel(model_name="gemini-pro")
                
                # Start a chat session
                print("Starting chat session...")
                self.chat_session = self.model.start_chat(history=[])
                print("Chat initialized successfully")
                
                # Send system prompt
                print("Sending system prompt...")
                system_prompt = """You are StudyPath AI, an academic planning assistant. 
                Your goal is to help students plan their academic journey, recommend courses, 
                and provide guidance on career paths. Be helpful, informative, and supportive."""
                
                self.chat_session.send_message(system_prompt)
                
            except Exception as e:
                print(f"Error initializing chat service: {str(e)}")
                self.chat_session = None
        else:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
    
    def send_message(self, message):
        if not self.api_key_loaded:
            return "API密钥未配置。请联系管理员设置Google API密钥。"
        
        if self.chat_session is None:
            try:
                # Try to reinitialize the chat session
                self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
                self.chat_session = self.model.start_chat(history=[])
            except Exception as e:
                return f"聊天服务初始化失败: {str(e)}"
        
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            # If error occurs, try with a different model
            try:
                # Try with a different model
                self.model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
                self.chat_session = self.model.start_chat(history=[])
                response = self.chat_session.send_message(message)
                return response.text
            except Exception as e2:
                return f"发送消息时出错: {str(e2)}"

# Create a singleton instance
chat_service = ChatService()
print("ChatService instance created") 