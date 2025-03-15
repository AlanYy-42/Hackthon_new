import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 优先使用Hugging Face Secrets中的API密钥
DEEPSEEK_API_KEY = os.getenv('HF_DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 这是示例URL，需要根据实际API文档修改

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
                "model": "deepseek-chat",  # 需要根据实际API文档修改
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
            
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            # 根据实际API响应格式调整
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling DeepSeek API: {str(e)}")
            return "抱歉，调用API时出现错误，请稍后再试。"

# 创建单例实例
deepseek_service = DeepSeekService() 