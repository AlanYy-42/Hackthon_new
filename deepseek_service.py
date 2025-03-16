import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 使用Google AI API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# 配置Gemini
genai.configure(api_key=GOOGLE_API_KEY)

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
        else:
            try:
                # 列出可用模型
                print("Available models:", [m.name for m in genai.list_models()])
                
                # 使用text-bison-001模型
                self.model = genai.GenerativeModel('gemini-1.0-pro')
                
                # 初始化对话
                self.chat = self.model.start_chat(history=[])
                print("Chat initialized successfully")
                
                # 发送系统提示词
                response = self.chat.send_message(SYSTEM_PROMPT)
                print("System prompt sent:", response.text)
                
            except Exception as e:
                print(f"Error initializing chat service: {str(e)}")
                self.model = None
    
    def chat(self, message):
        if not self.model:
            return "API密钥未配置或初始化失败，请联系管理员。"
            
        try:
            # 发送用户消息并获取响应
            response = self.chat.send_message(message)
            
            if response and response.text:
                return response.text
            else:
                return "抱歉，未能获取到有效回复。"
            
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"

# 创建单例实例
chat_service = ChatService() 