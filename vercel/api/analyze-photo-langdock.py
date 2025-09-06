import os
import json
import base64
import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Получаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Получаем изображение
            image_data = data.get('image')
            if not image_data:
                self.send_error(400, "No image data provided")
                return
            
            # Настройки Langdock
            api_key = os.environ.get('LANGDOCK_API_KEY')
            if not api_key:
                self.send_error(500, "Langdock API key not configured")
                return
            
            # Подготавливаем запрос к Langdock
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Проанализируй это изображение еды и предоставь информацию о питательной ценности, калориях и ингредиентах на русском языке. Структурируй ответ следующим образом:\n\n🍽️ **Блюдо**: [название]\n📊 **Калории**: [примерное количество на порцию]\n🥗 **Основные ингредиенты**: [список]\n💪 **Белки**: [граммы]\n🍞 **Углеводы**: [граммы]\n🥑 **Жиры**: [граммы]\n🧂 **Полезные свойства**: [краткое описание]\n⚠️ **Рекомендации**: [если есть]"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            # Отправляем запрос к Langdock
            response = requests.post(
                'https://api.langdock.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response_data = {
                    'success': True,
                    'analysis': analysis,
                    'model': 'langdock-gpt-4-vision',
                    'timestamp': int(__import__('time').time())
                }
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error(500, f"Langdock API error: {response.status_code}")
                
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {
            'service': 'Langdock Photo Analysis API',
            'status': 'running',
            'version': '1.0.0',
            'model': 'gpt-4-vision-preview'
        }
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
