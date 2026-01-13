import logging
import json
import requests
import os
from flow_service import process_user_input, get_user_state, UserState

# Configuración desde variables de entorno
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
VERSION = os.getenv('VERSION', 'v19.0')

def get_text_message_input(recipient, text):
    """Crear mensaje de texto para WhatsApp"""
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual", 
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    })

def send_message(data):
    """Enviar mensaje a WhatsApp API"""
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ Mensaje enviado exitosamente")
            return response
        else:
            logging.error(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Error enviando mensaje: {e}")
        return None

def get_clean_phone_number(wa_id):
    """Limpiar número de teléfono - SOLO LIMPIAR, NO HARDCODEAR"""
    # Remover todo excepto números y +
    cleaned = ''.join(c for c in wa_id if c.isdigit() or c == '+')
    
    # Si empieza con 521 (México con 1 extra), corregir a 52
    if cleaned.startswith('521') and len(cleaned) > 3:
        cleaned = '52' + cleaned[3:]
    
    return cleaned

def send_welcome_template(recipient):
    """Enviar plantilla de bienvenida"""
    try:
        recipient_clean = recipient.replace('+', '').replace(' ', '')
        
        template_data = json.dumps({
            "messaging_product": "whatsapp", 
            "to": recipient_clean,
            "type": "template",
            "template": {
                "name": "inicio",
                "language": {"code": "es_MX"}
            }
        })
        
        logging.info(f"🎯 Enviando plantilla 'inicio' a {recipient_clean}")
        return send_message(template_data)
            
    except Exception as e:
        logging.error(f"❌ Error enviando plantilla: {e}")
        return None

def process_whatsapp_message(body):
    """Procesar mensajes de WhatsApp - VERSIÓN MEJORADA CON MANEJO DE ARCHIVOS"""
    try:
        logging.info(f"🔍 INICIANDO PROCESAMIENTO - Body recibido: {body}")
        
        # Validación básica
        if not body.get("entry") or not body["entry"][0].get("changes"):
            logging.error("❌ Estructura de webhook inválida")
            return

        entry = body["entry"][0]
        value = entry["changes"][0]["value"]
        
        # Obtener información del contacto
        contacts = value.get("contacts", [])
        if not contacts:
            logging.error("❌ No hay información de contacto")
            return

        wa_id = contacts[0]["wa_id"]
        name = contacts[0].get("profile", {}).get("name", "Usuario")
        
        # Obtener mensajes
        messages = value.get("messages", [])
        if not messages:
            logging.info("📊 Actualización de estado, ignorando")
            return

        message = messages[0]
        message_type = message.get("type")
        
        # ✅ USAR SIEMPRE EL NÚMERO REAL - LIMPIADO CORRECTAMENTE
        wa_id_to_use = get_clean_phone_number(wa_id)
        
        logging.info(f"📱 Mensaje de {name} ({wa_id} -> {wa_id_to_use}) - Tipo: {message_type}")
        
        current_state = get_user_state(wa_id_to_use)
        logging.info(f"🔄 Estado del usuario: {current_state}")
        
        # ✅ MANEJO ESPECIAL PARA ARCHIVOS EN ESTADO CANDIDATO_CV
        if message_type == "document" and current_state == UserState.CANDIDATO_CV:
            logging.info("📄 Documento recibido en estado CANDIDATO_CV - Procesando CV")
            # Confirmar recepción del CV
            response_text = "✅ *Hemos recibido tu CV*\n\nGracias por enviarnos tu documento. Será revisado por nuestros reclutadores y nos pondremos en contacto contigo pronto.\n\n¡Agradecemos tu interés en ARMO! 🎉"
            data = get_text_message_input(wa_id_to_use, response_text)
            send_message(data)
            return
        
        # Procesar mensaje según tipo
        if message_type == "text":
            message_body = message["text"]["body"]
            logging.info(f"💬 Texto: {message_body}")
            
            logging.info(f"📝 LLAMANDO process_user_input con: wa_id={wa_id_to_use}, mensaje='{message_body}'")
            
            response_text = process_user_input(wa_id_to_use, message_body)
            
            logging.info(f"📤 RESPUESTA GENERADA: '{response_text}'")
            
            # ✅ SOLO ENVIAR RESPUESTA SI process_user_input DEVUELVE ALGO
            if response_text:
                data = get_text_message_input(wa_id_to_use, response_text)
                send_message(data)
            else:
                logging.info("🤐 No se envía respuesta (conversación terminada o ventana de 3 días activa)")
        
        elif message_type == "button":
            button_text = message["button"]["text"]
            logging.info(f"🔘 Botón: {button_text}")
            
            logging.info(f"📝 LLAMANDO process_user_input con: wa_id={wa_id_to_use}, mensaje='{button_text}'")
            
            response_text = process_user_input(wa_id_to_use, button_text)
            
            logging.info(f"📤 RESPUESTA GENERADA: '{response_text}'")
            
            if response_text:
                data = get_text_message_input(wa_id_to_use, response_text)
                send_message(data)
            else:
                logging.info("🤐 No se envía respuesta (conversación terminada o ventana de 3 días activa)")
            
        elif message_type == "document":
            # Para documentos en otros estados, ignorar silenciosamente
            logging.info("📄 Documento recibido en estado no CANDIDATO_CV - Ignorando")
            # NO enviar mensaje de error
            
        else:
            # Para otros tipos de mensaje no soportados, ignorar silenciosamente
            logging.warning(f"⚠️ Tipo no soportado: {message_type} - Ignorando")
            # NO enviar mensaje de error
            
    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}")
