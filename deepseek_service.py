import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# 首先加载.env文件中的环境变量
load_dotenv()

# 添加延迟，确保环境变量有时间加载
time.sleep(1)

# 尝试多种方式获取API密钥
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
# 如果仍然没有找到，尝试从文件读取
if not GOOGLE_API_KEY:
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GOOGLE_API_KEY='):
                    GOOGLE_API_KEY = line.strip().split('=', 1)[1].strip('"\'')
                    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
                    break
    except Exception as e:
        print(f"Error reading .env file: {str(e)}")

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
        self.api_key = GOOGLE_API_KEY
        self.api_key_loaded = self.api_key is not None
        print(f"GOOGLE_API_KEY loaded: {self.api_key_loaded}")
        
        # Initialize chat session
        self.chat_session = None
        
        if self.api_key_loaded:
            try:
                print("Creating ChatService instance...")
                # 确保API密钥已配置
                genai.configure(api_key=self.api_key)
                
                # 列出可用模型
                try:
                    models = genai.list_models()
                    print("Available models:", [m.name for m in models])
                except Exception as e:
                    print(f"Error listing models: {str(e)}")
                
                # 尝试使用不同的模型名称格式
                model_names = [
                    "gemini-1.5-pro",
                    "models/gemini-1.5-pro",
                    "gemini-pro",
                    "models/gemini-pro",
                    "gemini-1.5-flash",
                    "models/gemini-1.5-flash"
                ]
                
                # 尝试每个模型名称，直到成功
                for model_name in model_names:
                    try:
                        print(f"Trying model: {model_name}")
                        self.model = genai.GenerativeModel(model_name=model_name)
                        self.chat_session = self.model.start_chat(history=[])
                        print(f"Successfully initialized with model: {model_name}")
                        
                        # 发送系统提示词
                        system_prompt = """You are StudyPath AI, an academic planning assistant. 
                        Your goal is to help students plan their academic journey, recommend courses, 
                        and provide guidance on career paths. Be helpful, informative, and supportive."""
                        
                        self.chat_session.send_message(system_prompt)
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
        if not self.api_key_loaded:
            return "API密钥未配置。请联系管理员设置Google API密钥。"
        
        if self.chat_session is None:
            try:
                # 尝试重新初始化聊天会话
                model_names = [
                    "gemini-1.5-pro",
                    "models/gemini-1.5-pro",
                    "gemini-pro",
                    "models/gemini-pro",
                    "gemini-1.5-flash",
                    "models/gemini-1.5-flash"
                ]
                
                for model_name in model_names:
                    try:
                        print(f"Trying to reinitialize with model: {model_name}")
                        self.model = genai.GenerativeModel(model_name=model_name)
                        self.chat_session = self.model.start_chat(history=[])
                        print(f"Successfully reinitialized with model: {model_name}")
                        break
                    except Exception as e:
                        print(f"Failed to reinitialize with model {model_name}: {str(e)}")
                        continue
                
                if not self.chat_session:
                    return "无法初始化聊天服务，请稍后再试。"
            except Exception as e:
                return f"聊天服务初始化失败: {str(e)}"
        
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return f"发送消息时出错: {str(e)}"

# Create a singleton instance
print("Creating ChatService instance...")
chat_service = ChatService()
print("ChatService instance created") 