import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 使用Hugging Face的API
HF_API_KEY = os.getenv('HF_DEEPSEEK_API_KEY')
HF_API_URL = "https://api-inference.huggingface.co/models/google/gemini-2.0-flash-exp"

SYSTEM_PROMPT = """你是一个专业的教育顾问助手，专门帮助学生规划他们的学习路径和课程选择。你应该：
1. 基于学生已修课程和兴趣提供个性化建议
2. 考虑课程难度、先修要求和职业发展方向
3. 给出具体的课程推荐和学习规划
4. 使用友好专业的语气，提供详细的解释
请用中文回答问题。"""

class ChatService:
    def __init__(self):
        if not HF_API_KEY:
            print("Warning: HF_API_KEY not found in environment variables")
            self.headers = None
        else:
            self.headers = {
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            }
    
    def chat(self, message):
        if not self.headers:
            return "API密钥未配置，请联系管理员设置API密钥。"
            
        try:
            # 构建带有系统提示词的输入
            formatted_input = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ]
            }
            
            response = requests.post(
                HF_API_URL,
                headers=self.headers,
                json=formatted_input,
                timeout=30
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Request payload: {formatted_input}")  # 打印请求内容
            
            if response.status_code == 401:
                print("API密钥无效或已过期")
                return "API密钥验证失败，请联系管理员检查API密钥。"
            elif response.status_code == 503:
                print("模型正在加载中")
                return "模型正在加载中，请稍后再试（通常需要30秒）。"
            elif response.status_code != 200:
                print(f"API返回错误状态码: {response.status_code}")
                print(f"Response content: {response.text}")  # 打印错误响应内容
                return f"服务器返回错误（状态码：{response.status_code}），请稍后再试。"
            
            print(f"Raw response: {response.text}")
            
            try:
                data = response.json()
                print(f"Parsed JSON response: {data}")
                
                if isinstance(data, dict) and "generated_text" in data:
                    return data["generated_text"]
                elif isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and "generated_text" in data[0]:
                        return data[0]["generated_text"]
                    return str(data[0])
                else:
                    return "抱歉，未能获取到有效回复。"
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return response.text if response.text else "抱歉，未能获取到有效回复。"
            
        except requests.exceptions.Timeout:
            print("API请求超时")
            return "抱歉，请求超时。模型可能正在加载，请稍后再试。"
        except requests.exceptions.RequestException as e:
            print(f"Error calling API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "抱歉，处理请求时发生意外错误。"

# 创建单例实例
chat_service = ChatService() 