import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 使用Hugging Face的API
HF_API_KEY = os.getenv('HF_DEEPSEEK_API_KEY')  # 复用已有的环境变量
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"  # 使用完全开放的模型

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
            # 直接使用文本作为输入
            payload = {
                "inputs": message
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
            elif response.status_code == 503:
                print("模型正在加载中")
                return "模型正在加载中，请稍后再试。"
            
            try:
                print(f"Response content: {response.text}")  # 调试日志
            except:
                print("Unable to print response content")
                
            response.raise_for_status()
            data = response.json()
            
            print(f"Parsed response data: {data}")  # 调试日志
            
            # 直接返回生成的文本
            if isinstance(data, list):
                return data[0]
            else:
                return str(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "抱歉，处理请求时发生意外错误。"

# 创建单例实例
chat_service = ChatService() 