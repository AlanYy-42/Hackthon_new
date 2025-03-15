import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 优先使用Hugging Face Secrets中的API密钥
DEEPSEEK_API_KEY = os.getenv('HF_DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.ai/v1/chat/completions"  # 更新为正确的API URL

class DeepSeekService:
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            print("Warning: DEEPSEEK_API_KEY not found in environment variables")
            self.headers = None
        else:
            self.headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
    
    def chat(self, message):
        if not self.headers:
            return "API密钥未配置，请联系管理员设置API密钥。"
            
        try:
            payload = {
                "model": "deepseek-chat-v1",  # 更新为正确的模型名称
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=self.headers,
                json=payload,
                timeout=30  # 添加超时设置
            )
            
            if response.status_code == 401:
                print("API密钥无效或已过期")
                return "API密钥验证失败，请联系管理员检查API密钥。"
                
            response.raise_for_status()
            data = response.json()
            
            # 根据DeepSeek API的实际响应格式获取回复
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "抱歉，未能获取到有效回复。"
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling DeepSeek API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "抱歉，处理请求时发生意外错误。"

# 创建单例实例
deepseek_service = DeepSeekService() 