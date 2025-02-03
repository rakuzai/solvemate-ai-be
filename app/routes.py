# app/routes.py
from flask import Blueprint, request, jsonify
import requests
from config import Config
from app.utils import SessionManager

main = Blueprint('main', __name__)
session_manager = SessionManager()

@main.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message', '')
        
        if not session_id:
            return jsonify({'status': 'error', 'message': 'Session ID is required'}), 400
        
        if session_manager.is_session_expired(session_id):
            session_manager.delete_session(session_id)
            return jsonify({
                'status': 'error',
                'message': 'Session expired, please start a new conversation.'
            }), 400
        
        session = session_manager.get_session(session_id)
        session_manager.update_session(session_id)
        
        session["messages"].append({"role": "user", "content": user_message})
        
        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": Config.MODEL_NAME,
            "messages": session["messages"],
            "temperature": 0.7,
            "max_completion_tokens": 500,
            "top_p": 0.9,
            "stream": False
        }
        
        response = requests.post(Config.GROQ_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            ai_message = response_data['choices'][0]['message']['content']
            session["messages"].append({"role": "assistant", "content": ai_message})
            
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

@main.route('/api/chat/<session_id>', methods=['DELETE'])
def delete_chat(session_id):
    try:
        session_manager.delete_session(session_id)
        return jsonify({
            'status': 'success',
            'message': 'Chat session deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'SolveMate AI backend is running'
    })