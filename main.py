from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Groq API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Configure headers for Groq API
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# System message to define SolveMate AI's behavior
SYSTEM_MESSAGE = {
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

# Dictionary to store session data and timestamps
session_data = {}
SESSION_TIMEOUT = 60 * 60 * 12  # 12 hours in seconds

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message', '')
        
        if not session_id:
            return jsonify({'status': 'error', 'message': 'Session ID is required'}), 400
        
        # Initialize session history if it doesn't exist
        if session_id not in session_data:
            session_data[session_id] = {
                "messages": [SYSTEM_MESSAGE],
                "last_active": time.time()
            }
        
        # Check if the session has expired
        last_active_time = session_data[session_id]["last_active"]
        if time.time() - last_active_time > SESSION_TIMEOUT:
            # Session expired, reset the session history
            session_data[session_id] = {
                "messages": [SYSTEM_MESSAGE],
                "last_active": time.time()
            }
            return jsonify({
                'status': 'error',
                'message': 'Session expired, please start a new conversation.'
            }), 400
        
        # Update last active time
        session_data[session_id]["last_active"] = time.time()
        
        # Append the user's message to the conversation history
        session_data[session_id]["messages"].append({"role": "user", "content": user_message})
        
        # Prepare the request to Groq API
        payload = {
            "model": "llama-3.3-70b-versatile",  # Using LLaMA model
            "messages": session_data[session_id]["messages"],
            "temperature": 0.7,
            "max_completion_tokens": 500,
            "top_p": 0.9,
            "stream": False
        }
        
        # Make request to Groq API
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            ai_message = response_data['choices'][0]['message']['content']
            
            # Append the assistant's response to the conversation history
            session_data[session_id]["messages"].append({"role": "assistant", "content": ai_message})
            
            return jsonify({
                'status': 'success',
                'message': ai_message,
                'usage': response_data.get('usage', {})
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Groq API Error: {response.text}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@app.route('/api/chat/<session_id>', methods=['DELETE'])
def delete_chat(session_id):
    try:
        if session_id in session_data:
            del session_data[session_id]
        return jsonify({
            'status': 'success',
            'message': 'Chat session deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'SolveMate AI backend is running'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)