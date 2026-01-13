from flask import Flask, request, jsonify
import os
import logging
from flow_service import process_user_input, get_user_state, UserState
from whatsapp_utils import send_message, get_text_message_input, process_whatsapp_message

app = Flask(__name__)

# Configuración directa - MÁS SIMPLE
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '04082025')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
APP_SECRET = os.getenv('APP_SECRET')

# Logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook principal para WhatsApp - VERSIÓN SIMPLIFICADA"""
    
    # VERIFICACIÓN (GET)
    if request.method == 'GET':
        hub_mode = request.args.get('hub.mode')
        hub_token = request.args.get('hub.verify_token') 
        hub_challenge = request.args.get('hub.challenge')
        
        logging.info(f"🔐 Verificación: token_recibido={hub_token}, token_esperado={VERIFY_TOKEN}")
        
        if hub_mode == 'subscribe' and hub_token == VERIFY_TOKEN:
            logging.info("✅ Webhook verificado exitosamente")
            return hub_challenge, 200
        else:
            logging.error("❌ Falla en verificación - tokens no coinciden")
            return jsonify({"error": "Verification failed"}), 403
    
    # MENSAJES (POST)
    if request.method == 'POST':
        try:
            data = request.get_json()
            logging.info(f"📨 Mensaje recibido de WhatsApp")
            
            # Procesar el mensaje
            process_whatsapp_message(data)
            
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para Cloud Run"""
    return jsonify({
        "status": "healthy", 
        "service": "whatsapp-bot",
        "verify_token_set": bool(VERIFY_TOKEN),
        "access_token_set": bool(ACCESS_TOKEN)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🚀 Iniciando WhatsApp Bot en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
