import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# First load environment variables from .env file
load_dotenv()

# Add delay to ensure environment variables have time to load
time.sleep(1)

# For Hugging Face deployment, use a hardcoded key
# In production, this should be set as an environment variable
GOOGLE_API_KEY = "AIzaSyDJC5a7hQxfvXRLNFzpTGfnAdOGjLYjHpI"
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

print("GOOGLE_API_KEY loaded:", bool(GOOGLE_API_KEY))  # Only print if exists, not the actual value

# Configure Gemini
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Error configuring Gemini API: {str(e)}")
else:
    print("WARNING: GOOGLE_API_KEY is missing! Set it as an environment variable.")

SYSTEM_PROMPT = """You are a professional educational consultant assistant, specializing in helping students plan their learning paths and course selections. You should:
1. Provide personalized recommendations based on students' completed courses and interests
2. Consider course difficulty, prerequisites, and career development directions
3. Give specific course recommendations and learning plans
4. Use a friendly and professional tone, providing detailed explanations"""

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
                # Ensure API key is configured
                genai.configure(api_key=self.api_key)
                
                # Try different model name formats
                model_names = [
                    "gemini-1.5-pro",
                    "models/gemini-1.5-pro",
                    "gemini-pro",
                    "models/gemini-pro",
                    "gemini-1.5-flash",
                    "models/gemini-1.5-flash"
                ]
                
                # Try each model name until successful
                for model_name in model_names:
                    try:
                        print(f"Trying model: {model_name}")
                        self.model = genai.GenerativeModel(model_name=model_name)
                        self.chat_session = self.model.start_chat(history=[])
                        print(f"Successfully initialized with model: {model_name}")
                        
                        # Send system prompt
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
            return "API key not configured. Please contact the administrator to set up the Google API key."
        
        if self.chat_session is None:
            try:
                # Try to reinitialize chat session
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
                    return "Unable to initialize chat service, please try again later."
            except Exception as e:
                return f"Chat service initialization failed: {str(e)}"
        
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return f"Error sending message: {str(e)}"

# Create a singleton instance
print("Creating ChatService instance...")
chat_service = ChatService()
print("ChatService instance created") 