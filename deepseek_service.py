import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 使用Hugging Face的API
HF_API_KEY = os.getenv('HF_DEEPSEEK_API_KEY')  # 复用已有的环境变量
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # 使用最基础的GPT-2模型

class ChatService:
    def __init__(self):
        if not HF_API_KEY:
            print("Warning: HF_API_KEY not found in environment variables")
            self.headers = None
        else:
            self.headers = {
                "Authorization": f"Bearer {HF_API_KEY}"  # 移除Content-Type
            }
    
    def chat(self, message):
        if not self.headers:
            return "API密钥未配置，请联系管理员设置API密钥。"
            
        try:
            # 使用纯文本作为输入
            response = requests.post(
                HF_API_URL,
                headers=self.headers,
                json={"inputs": message},
                timeout=30
            )
            
            print(f"Response status code: {response.status_code}")  # 调试日志
            print(f"Response headers: {response.headers}")  # 添加响应头信息的调试
            
            if response.status_code == 401:
                print("API密钥无效或已过期")
                return "API密钥验证失败，请联系管理员检查API密钥。"
            elif response.status_code == 503:
                print("模型正在加载中")
                return "模型正在加载中，请稍后再试。"
            
            # 打印原始响应内容
            print(f"Raw response: {response.text}")
            
            # 尝试解析JSON响应
            try:
                data = response.json()
                print(f"Parsed JSON response: {data}")
                
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('generated_text', '抱歉，未能获取到有效回复。')
                else:
                    return str(data)
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                # 如果JSON解析失败，直接返回文本响应
                return response.text if response.text else "抱歉，未能获取到有效回复。"
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return f"抱歉，调用API时出现错误：{str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "抱歉，处理请求时发生意外错误。"

# 创建单例实例
chat_service = ChatService() 