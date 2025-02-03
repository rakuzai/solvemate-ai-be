# app/utils.py
import time
from config import Config

class SessionManager:
    def __init__(self):
        self.session_data = {}
        self.system_message = {
            "role": "system",
            "content": """You are SolveMate AI, a helpful educational assistant designed to help students with their homework. 
            Your approach should be:
            1. Guide students to understand concepts rather than just providing answers
            2. Use clear explanations with examples
            3. Break down complex problems into simpler steps
            4. Encourage critical thinking
            5. Provide helpful resources when appropriate
            Never solve the homework directly - instead, help students learn how to solve it themselves."""
        }
    
    def get_session(self, session_id):
        if session_id not in self.session_data:
            self.session_data[session_id] = {
                "messages": [self.system_message],
                "last_active": time.time()
            }
        return self.session_data[session_id]
    
    def update_session(self, session_id):
        self.session_data[session_id]["last_active"] = time.time()
    
    def delete_session(self, session_id):
        if session_id in self.session_data:
            del self.session_data[session_id]
    
    def is_session_expired(self, session_id):
        session = self.get_session(session_id)
        return time.time() - session["last_active"] > Config.SESSION_TIMEOUT