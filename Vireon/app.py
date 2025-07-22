from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from supabase import create_client  # 🔹 NUEVO

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

JWT_SECRET = os.getenv('JWT_SECRET', 'default_secret')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'gmail-extension-backend'
    })

@app.route('/api/gmail/messages', methods=['POST'])
def get_gmail_messages():
    """Get Gmail messages and send to webhook"""
    try:
        data = request.get_json()
        access_token = data.get('token')
        
        if not access_token:
            return jsonify({'error': 'Access token required'}), 400
        
        # Get messages from Gmail API
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5',
            headers=headers
        )
        
        if not response.ok:
            return jsonify({'error': 'Failed to fetch Gmail messages'}), response.status_code
        
        messages_data = response.json()
        
        # Process each message
        processed_messages = []
        for message in messages_data.get('messages', []):
            message_details = get_message_details(access_token, message['id'])
            if message_details:
                processed_messages.append(message_details)
                send_to_webhook(message_details)
        
        return jsonify({
            'success': True,
            'processed_messages': len(processed_messages),
            'messages': processed_messages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_message_details(access_token, message_id):
    """Get detailed message information"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full',
            headers=headers
        )
        
        if not response.ok:
            return None
        
        message_data = response.json()
        headers = message_data['payload']['headers']
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
        
        body = get_body_from_payload(message_data['payload'])
        
        return {
            'messageId': message_id,
            'subject': subject,
            'from': sender,
            'body': body,
            'snippet': message_data.get('snippet', ''),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting message details: {e}")
        return None

def get_body_from_payload(payload):
    """Extract body from Gmail payload"""
    try:
        if payload.get('body') and payload['body'].get('data'):
            return payload['body']['data']
        
        if payload.get('parts'):
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    return part['body']['data']
                if part.get('parts'):
                    nested_body = get_body_from_payload(part)
                    if nested_body:
                        return nested_body
        
        return ""
        
    except Exception as e:
        print(f"Error extracting body: {e}")
        return ""

def send_to_webhook(message_data):
    """Send message data to webhook"""
    try:
        webhook_data = {
            'subject': message_data['subject'],
            'body': message_data['body'],
            'from': message_data['from'],
            'messageId': message_data['messageId'],
            'timestamp': message_data['timestamp']
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.ok:
            print(f"Webhook sent successfully for message: {message_data['messageId']}")
        else:
            print(f"Webhook failed for message: {message_data['messageId']}")
            
    except Exception as e:
        print(f"Error sending to webhook: {e}")

@app.route('/api/auth/validate', methods=['POST'])
def validate_token():
    """Validate Gmail access token"""
    try:
        data = request.get_json()
        access_token = data.get('token')
        
        if not access_token:
            return jsonify({'valid': False, 'error': 'Token required'}), 400
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://gmail.googleapis.com/gmail/v1/users/me/profile',
            headers=headers
        )
        
        if response.ok:
            profile_data = response.json()
            return jsonify({
                'valid': True,
                'email': profile_data.get('emailAddress'),
                'messagesTotal': profile_data.get('messagesTotal')
            })
        else:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

# 🔹 NUEVA RUTA PARA GUARDAR USUARIO EN SUPABASE
@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data.get('email')
        access_token = data.get('access_token')

        if not email or not access_token:
            return jsonify({'status': 'error', 'message': 'Faltan datos'}), 400

        supabase.table("users").insert({
            "email": email,
            "access_token": access_token
        }).execute()

        return jsonify({'status': 'ok', 'message': 'Usuario registrado'}), 200

    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
