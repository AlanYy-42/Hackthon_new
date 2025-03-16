import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 使用Hugging Face的API
HF_API_KEY = os.getenv('HF_DEEPSEEK_API_KEY')  # 复用已有的环境变量
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"  # 换用Llama 2模型

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
            # 使用更简单的输入格式
            payload = {
                "inputs": message,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            print(f"Sending request to Hugging Face API")  # 调试日志
            print(f"Request payload: {payload}")  # 调试日志
            
            response = requests.post(
                HF_API_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"Response status code: {response.status_code}")  # 调试日志
            
            if response.status_code == 401:
                print("API密钥无效或已过期")
                return "API密钥验证失败，请联系管理员检查API密钥。"
            
            try:
                print(f"Response content: {response.text}")  # 调试日志
            except:
                print("Unable to print response content")
                
            response.raise_for_status()
            data = response.json()
            
            print(f"Parsed response data: {data}")  # 调试日志
            
            # 解析Hugging Face的响应格式
            if isinstance(data, list) and len(data) > 0:
                # 如果响应是列表格式
                return data[0].get('generated_text', '抱歉，未能获取到有效回复。')
            elif isinstance(data, dict):
                # 如果响应是字典格式
                return data.get('generated_text', data.get('answer', '抱歉，未能获取到有效回复。'))
            else:
                return "抱歉，未能获取到有效回复。"
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "抱歉，处理请求时发生意外错误。"

# 创建单例实例
chat_service = ChatService() 