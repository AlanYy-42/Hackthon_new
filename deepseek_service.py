import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 使用Google AI API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
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
        if not GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
            self.model = None
            self.chat_session = None
        else:
            try:
                print("Initializing chat service with API key...")
                # 列出可用模型
                models = genai.list_models()
                print("Available models:", [m.name for m in models])
                
                # 使用gemini-pro模型
                print("Creating GenerativeModel instance...")
                self.model = genai.GenerativeModel('gemini-pro')
                
                # 初始化对话
                print("Starting chat session...")
                self.chat_session = self.model.start_chat(history=[])
                print("Chat initialized successfully")
                
                # 发送系统提示词
                print("Sending system prompt...")
                response = self.chat_session.send_message(SYSTEM_PROMPT)
                print("System prompt sent:", response.text if response else "No response")
                
            except Exception as e:
                print(f"Error initializing chat service: {str(e)}")
                self.model = None
                self.chat_session = None
    
    def send_message(self, message):
        if not self.model or not self.chat_session:
            print("Error: model or chat_session is None")
            print("model exists:", bool(self.model))
            print("chat_session exists:", bool(self.chat_session))
            return "API密钥未配置或初始化失败，请联系管理员。"
            
        try:
            print(f"Sending message: {message}")
            # 发送用户消息并获取响应
            response = self.chat_session.send_message(message)
            print("Response received")
            
            if response and response.text:
                print("Response text:", response.text[:100] + "..." if len(response.text) > 100 else response.text)
                return response.text
            else:
                print("No valid response received")
                return "抱歉，未能获取到有效回复。"
            
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"

# 创建单例实例
print("Creating ChatService instance...")
chat_service = ChatService()
print("ChatService instance created") 