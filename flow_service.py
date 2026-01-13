import logging
import time
from enum import Enum

class UserState(Enum):
    INIT = "init"
    CANDIDATO = "candidato"
    COLABORADOR = "colaborador"
    EX_COLABORADOR = "ex_colaborador"
    ENVIAR_INFO = "enviar_info"
    CONFIRMAR_TIPO = "confirmar_tipo"
    
    # Nuevos estados para el flujo candidato
    CANDIDATO_DATOS = "candidato_datos"
    CANDIDATO_OPCIONES = "candidato_opciones"
    CANDIDATO_VACANTES = "candidato_vacantes"
    CANDIDATO_POSTULACION = "candidato_postulacion"
    CANDIDATO_CV = "candidato_cv"
    CANDIDATO_ESTATUS = "candidato_estatus"
    CANDIDATO_RECLUTADOR = "candidato_reclutador"
    CANDIDATO_DESPEDIDA = "candidato_despedida"

    #Estados para el flujo de colaborador
    COLABORADOR_CAPACITACION = "colaborador_capacitacion"
    COLABORADOR_CONOCER = "colaborador_conocer"
    COLABORADOR_CONTACTAR = "colaborador_contactar"
    COLABORADOR_JUSTIFICAR = "colaborador_justificar"
    COLABORADOR_USO = "colaborador_uso"

    #Estados para el flujo de ex-colaborador
    EX_COLABORADOR_CONSTANCIAS = "ex_colaborador_constancias"
    EX_COLABORADOR_FINIQUITO = "ex_colaborador_finiquito"
    EX_COLABORADOR_DESARROLLO = "ex_colaborador_desarrollo"

    # Nuevo estado para terminar conversación
    CONVERSACION_TERMINADA = "conversacion_terminada"

# Mapeo de palabras clave - EXPANDIDO PARA MÁS FLEXIBILIDAD
KEYWORD_MAPPING = {
    # Para el menú principal de candidato - VACANTES
    "vacantes": "vacantes",
    "postularme": "vacantes", 
    "postular": "vacantes",
    "buscar trabajo": "vacantes",
    "empleo": "vacantes",
    "trabajo": "vacantes",
    "revisar": "vacantes",
    "revisar y postularme": "vacantes",
    "revisar vacantes": "vacantes",
    "ver vacantes": "vacantes",
    "ofertas": "vacantes",
    
    # Para el menú principal de candidato - ESTATUS
    "estatus": "estatus",
    "mi postulación": "estatus", 
    "seguimiento": "estatus",
    "proceso": "estatus",
    "donde voy": "estatus",
    "avance": "estatus",
    "conocer estatus": "estatus",
    "estado": "estatus",
    
    # Para el menú principal de candidato - RECLUTADOR
    "reclutador": "reclutador",
    "contactar": "reclutador",
    "humano": "reclutador",
    "persona": "reclutador",
    "agente": "reclutador",
    "asesor": "reclutador",
    "hablar con alguien": "reclutador",
    "contactar reclutador": "reclutador",
    
    # Para respuestas Sí/No
    "sí": "si",
    "si": "si", 
    "yes": "si",
    "claro": "si",
    "por supuesto": "si",
    "afirmativo": "si",
    "ok": "si",
    "dale": "si",
    "vamos": "si",
    "de acuerdo": "si",
    
    "no": "no",
    "nah": "no",
    "ahorita no": "no",
    "después": "no",
    "negativo": "no",
    "cancelar": "no",
    "mejor no": "no",
    
    # Palabras clave para reactivar
    "consultar chatbot": "reactivar",
    "chatbot": "reactivar",
    "bot": "reactivar",
    "asistente": "reactivar",
    "menu": "reactivar",
    "inicio": "reactivar",
    "volver": "reactivar",
    
    # Palabras clave para terminar
    "terminar": "terminar",
    "finalizar": "terminar",
    "salir": "terminar",
    "adiós": "terminar",
    "chao": "terminar"
}

FLOW_RESPONSES = {
    UserState.INIT: {
        "message": "¡Bienvenido! Gracias por comunicarte a ARMO. Para continuar, por favor selecciona una opción:",
        "options": [
            {"text": "📌 Candidato", "next_state": UserState.CANDIDATO},
            {"text": "📌 Colaborador", "next_state": UserState.COLABORADOR},
            {"text": "📌 Ex-Colaborador", "next_state": UserState.EX_COLABORADOR}
        ]
    },
    
    UserState.CANDIDATO: {
        "message": "Has seleccionado: *Candidato*\n\nPara continuar ingresa los siguientes datos:\n• Nombre completo\n• Edad\n• Domicilio, Colonia, Municipio/Alcaldía\n\nConsulta nuestro aviso de privacidad y conoce cómo protegemos tu información personal en: https://ejemplo.com/privacidad",
        "options": []
    },
    
    UserState.CANDIDATO_DATOS: {
        "message": "✅ *Datos recibidos correctamente*\n\n¿Qué opción te describe mejor?",
        "options": [
            {"text": "Revisar y postularme a vacantes disponibles", "next_state": UserState.CANDIDATO_VACANTES},
            {"text": "Conocer el estatus de mi postulación", "next_state": UserState.CANDIDATO_ESTATUS},
            {"text": "Quisiera contactar a un reclutador", "next_state": UserState.CANDIDATO_RECLUTADOR}
        ]
    },
    
    UserState.CANDIDATO_VACANTES: {
        "message": "🔍 *Vacantes Disponibles*\n\nConsulta nuestras vacantes disponibles en:\nhttps://sites.google.com/view/tecnojaque-tc2-a1/inicio\n\n¿Deseas postularte para alguna vacante? (sí/no)",
        "options": []
    },
    
    UserState.CANDIDATO_POSTULACION: {
        "message": "📝 *Formulario de Postulación*\n\nEnlace para redireccionar a formulario con cuestionario:\nhttps://sites.google.com/view/tecnojaque-tc2-a1/inicio\n\n¿Deseas enviar tu CV para una evaluación personalizada? (sí/no)",
        "options": []
    },
    
    UserState.CANDIDATO_CV: {
        "message": "📎 *Envía tu CV*\n\nPuedes adjuntar los archivos necesarios (PDF, Word, etc.). Serán revisados por nuestros reclutadores.\n\nAgradecemos tu tiempo e interés por trabajar en ARMO. Espera noticias pronto.",
        "options": [
            {"text": "🔄 Volver al inicio", "next_state": UserState.INIT},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },
    
    UserState.CANDIDATO_ESTATUS: {
        "message": "📊 *Estatus de Postulación*\n\nRevisaremos tu CV o solicitud de empleo y, si continuas en el proceso, te contactaremos para poder agendar una entrevista y prueba técnica (si aplica).",
        "options": [
            {"text": "🔄 Volver al inicio", "next_state": UserState.INIT},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },
    
    UserState.CANDIDATO_RECLUTADOR: {
        "message": "👨‍💼 *Contactar Reclutador*\n\nEn breve un reclutador se pondrá en contacto contigo.",
        "options": [
            {"text": "🔄 Volver al inicio", "next_state": UserState.INIT},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },
    
    UserState.CANDIDATO_DESPEDIDA: {
        "message": "👋 *Gracias por tu interés*\n\nAgradezco tu tiempo. Esperamos saber de ti pronto de nuevo.",
        "options": [
            {"text": "🔄 Volver al inicio", "next_state": UserState.INIT},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    #***************** DEFINIR ESTADOS PARA COLABORADORES
    
    UserState.COLABORADOR: {
        "message": "Has seleccionado: *Colaborador*\n\n¡Hola equipo! ¿En qué podemos ayudarte hoy?",
        "options": [
            {"text": "🔍 Quisiera conocer mis prestaciones y beneficios.", "next_state": UserState.COLABORADOR_CONOCER},
            {"text": "🔄 Quisera hacer uso de uno de mis beneficios", "next_state": UserState.COLABORADOR_USO},
            {"text": "📤 Acceder a Capacitación y Desarrollo", "next_state": UserState.COLABORADOR_CAPACITACION},
            {"text": "🤒 Quiero justificar una ausencia", "next_state": UserState.COLABORADOR_JUSTIFICAR},
            {"text": "📊 Contactar a Desarrollo Organizacional", "next_state": UserState.COLABORADOR_CONTACTAR}
        ]
    },

    UserState.COLABORADOR_CONOCER: {
        "message": "En la siguiente liga podrás conocer tus beneficios: \nhttps://sites.google.com/view/tecnojaque-tc2-a1/inicio\n\n Si deseas hacer uso de alguno, estoy para ayudarte.",
        "options": [
            {"text": "📤 Quiero hacer uso de algún beneficio", "next_state": UserState.COLABORADOR_USO},
            {"text": "🔄 Cambiar opción", "next_state": UserState.COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },    

    UserState.COLABORADOR_USO: {
        "message": "🫱🏻‍🫲🏽 Por favor escribe el beneficio del cual deseas hacer uso, y en breve el personal de Desarrollo Organizacional te contactará.\n\n 👩🏽‍💻 Si deseas acceder a otra parte del menú, selecciona la opción deseada.",
        "options": [
            {"text": "📤 Consultar información", "next_state": UserState.COLABORADOR_CONOCER},
            {"text": "🔄 Cambiar opción", "next_state": UserState.COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    UserState.COLABORADOR_CAPACITACION: {
        "message": "Armo piensa en todos sus colaboradores, por lo que se está trabajando en este módulo.\n\n 🗞️ Espera noticias pronto.",
        "options": [
            {"text": "🔄 Cambiar opción", "next_state": UserState.COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    UserState.COLABORADOR_JUSTIFICAR: {
        "message": "👩🏻‍⚕️ *Para justificar tu ausencia considera lo siguiente:* \n\n 🤕 Si es un tema médico, por favor envía un mensaje al número 5525124928, explicando la situación al Servicio Médico\n 😟 Si es por otro motivo, por favor deja tu mensaje para canalizarte al área correspondiente o llama directo a las Oficinas de Armo al número 5541617500.",
        "options": [
            {"text": "🔄 Cambiar opción", "next_state": UserState.COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    UserState.COLABORADOR_CONTACTAR: {
        "message": "Puedes escribirnos tu situación detallada por este medio y en breve te responderemos.",
        "options": [
            {"text": "🔄 Cambiar opción", "next_state": UserState.COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    #***************** DEFINIR ESTADOS PARA EX-COLABORADOR - CORREGIDO

    UserState.EX_COLABORADOR: {
        "message": "Has seleccionado: *Ex-Colaborador*\n\n¡Hola! Agradecemos tu tiempo en ARMO. ¿En qué podemos asistirte?",
        "options": [
            {"text": "📤 Solicitar una constancia laboral", "next_state": UserState.EX_COLABORADOR_CONSTANCIAS},
            {"text": "💰 Cuestiones con mi finiquito/liquidación.", "next_state": UserState.EX_COLABORADOR_FINIQUITO},
            {"text": "📊 Contactar a Desarrollo Organizacional.", "next_state": UserState.EX_COLABORADOR_DESARROLLO},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    UserState.EX_COLABORADOR_CONSTANCIAS: {
        "message": "🫱🏻‍🫲🏽 Para solicitar constancia laboral canalizaremos tu mensaje al área correspondiente. \n También puedes comunicarte a las Oficinas de Armo para dar seguimiento, al número 5541617500.\n\n Si deseas realizar alguna otra opción seleccionala.",
        "options": [
            {"text": "🔄 Cambiar opción", "next_state": UserState.EX_COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },

    UserState.EX_COLABORADOR_FINIQUITO: {
        "message": "💰💵Para dar seguimiento a la entrega de tu finiquito/liquidación canalizaremos tu mensaje al área correspondiente. \n\n También puedes comunicarte directamente a las Oficinas de Armo, al número 5541617500.",
        "options": [
            {"text": "🔄 Cambiar opción", "next_state": UserState.EX_COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },    

    UserState.EX_COLABORADOR_DESARROLLO: {
        "message": "📊 Puedes escribirnos tu situación detallada por este medio y en breve te responderemos.",
        "options": [
            {"text": "🔄 Cambiar opción", "next_state": UserState.EX_COLABORADOR},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },
    
    UserState.ENVIAR_INFO: {
        "message": "📤 *Procesando tu solicitud...*\n\nHemos recibido tu información. Antes de continuar, ¿confirmas que seleccionaste el tipo correcto?",
        "options": [
            {"text": "✅ Sí, es correcto", "next_state": UserState.CONFIRMAR_TIPO},
            {"text": "❌ No, cambiar tipo", "next_state": UserState.INIT},
            {"text": "📝 Agregar más detalles", "next_state": UserState.ENVIAR_INFO},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },
    
    UserState.CONFIRMAR_TIPO: {
        "message": "✅ *¡Proceso completado!*\n\nTu información ha sido registrada exitosamente. El equipo de ARMO diseño se contactará contigo pronto.\n\n¡Gracias por confiar en nosotros! 🎉",
        "options": [
            {"text": "🔄 Iniciar nuevo proceso", "next_state": UserState.INIT},
            {"text": "❌ Terminar conversación", "next_state": UserState.CONVERSACION_TERMINADA}
        ]
    },
    
    UserState.CONVERSACION_TERMINADA: {
        "message": "👋 *¡Gracias por contactarnos!*\n\nAgradecemos tu tiempo. Si necesitas asistencia en el futuro, no dudes en escribir *Consultar chatbot* para volver al menú principal.\n\n¡Que tengas un excelente día! 🌟",
        "options": []
    }
}

# Manejo de estados y datos del usuario - MEJORADO
user_sessions = {}
user_data = {}
user_last_interaction = {}  # Para control de tiempo
conversation_ended = {}  # Para marcar conversaciones terminadas

def get_user_state(wa_id):
    return user_sessions.get(wa_id, UserState.INIT)

def set_user_state(wa_id, state):
    user_sessions[wa_id] = state
    # Actualizar última interacción
    user_last_interaction[wa_id] = time.time()
    
    # Marcar si la conversación ha terminado
    if state == UserState.CONVERSACION_TERMINADA:
        conversation_ended[wa_id] = True

def save_user_data(wa_id, key, value):
    if wa_id not in user_data:
        user_data[wa_id] = {}
    user_data[wa_id][key] = value

def get_user_data(wa_id, key=None):
    if key:
        return user_data.get(wa_id, {}).get(key)
    return user_data.get(wa_id, {})

def should_respond(wa_id):
    """Verifica si el bot debe responder basado en el tiempo transcurrido"""
    # Si la conversación fue terminada explícitamente, no responder por 3 días
    if conversation_ended.get(wa_id, False):
        if wa_id not in user_last_interaction:
            return False
        
        last_time = user_last_interaction[wa_id]
        current_time = time.time()
        time_diff_hours = (current_time - last_time) / 3600  # Diferencia en horas
        
        # Si han pasado más de 72 horas (3 días), permitir reactivación
        if time_diff_hours > 72:
            conversation_ended[wa_id] = False  # Resetear estado
            return True
        else:
            return False
    
    # Para conversaciones normales, usar la lógica original
    if wa_id not in user_last_interaction:
        return True
    
    last_time = user_last_interaction[wa_id]
    current_time = time.time()
    time_diff_hours = (current_time - last_time) / 3600
    
    # Si han pasado más de 72 horas (3 días), no responder
    if time_diff_hours > 72:
        return False
    
    return True

def validate_user_selection(wa_id, user_message):
    current_state = get_user_state(wa_id)
    user_message_lower = user_message.lower().strip()
    
    # Validación para estado INIT
    if current_state == UserState.INIT:
        valid_options = ["candidato", "colaborador", "ex-colaborador", "1", "2", "3","1.", "2.", "3."]
        is_valid = any(opt in user_message_lower for opt in valid_options)
        
        if not is_valid:
            return "❌ *Por favor selecciona una opción válida:*\n\n" + generate_response(wa_id, show_options=True)
    
    # Validación para estados que esperan sí/no
    elif current_state in [UserState.CANDIDATO_VACANTES, UserState.CANDIDATO_POSTULACION]:
        if not any(word in user_message_lower for word in ["si", "sí", "no", "yes"]):
            return "❌ *Por favor responde con 'Sí' o 'No':*"
    
    return None

def find_best_option_match(user_message_lower, options_keywords):
    """Encuentra la mejor coincidencia para las opciones del menú"""
    user_words = set(user_message_lower.split())
    
    best_match = None
    best_score = 0
    
    for option_key, keywords in options_keywords.items():
        keyword_set = set(keywords)
        # Calcular coincidencia
        common_words = user_words.intersection(keyword_set)
        score = len(common_words)
        
        if score > best_score:
            best_score = score
            best_match = option_key
    
    # Si hay al menos 1 palabra en común, considerar como match
    return best_match if best_score >= 1 else None

def process_user_input(wa_id, user_message):
    current_state = get_user_state(wa_id)
    user_message_lower = user_message.lower().strip()
    
    logging.info(f"🔄 Procesando mensaje: '{user_message}' en estado: {current_state}")
    
    # ✅ VERIFICAR SI DEBEMOS RESPONDER (ventana de 3 días MEJORADA)
    if not should_respond(wa_id):
        if any(keyword in user_message_lower for keyword in ["consultar chatbot", "chatbot", "bot", "asistente"]):
            if conversation_ended.get(wa_id, False):
                conversation_ended[wa_id] = False
            set_user_state(wa_id, UserState.INIT)
            return generate_response(wa_id)
        else:
            logging.info(f"🤐 No respondiendo - Conversación terminada o ventana de 3 días activa para {wa_id}")
            return None
    
    # ✅ PALABRAS CLAVE PARA REACTIVAR DESDE CUALQUIER ESTADO
    if any(keyword in user_message_lower for keyword in ["consultar chatbot", "chatbot", "bot", "asistente", "menu", "inicio"]):
        if conversation_ended.get(wa_id, False):
            conversation_ended[wa_id] = False
        set_user_state(wa_id, UserState.INIT)
        return generate_response(wa_id)
    
    # ✅ MANEJO ESPECIAL PARA CONVERSACIÓN TERMINADA - MEJORADO
    if current_state == UserState.CONVERSACION_TERMINADA:
        conversation_ended[wa_id] = True
        
        if any(keyword in user_message_lower for keyword in ["consultar chatbot", "chatbot", "bot", "asistente", "menu", "inicio"]):
            conversation_ended[wa_id] = False
            set_user_state(wa_id, UserState.INIT)
            return generate_response(wa_id)
        else:
            return None
    
    # ✅ MANEJO ESPECIAL PARA ESTADO INIT 
    if current_state == UserState.INIT:
        valid_options = ["candidato", "colaborador", "ex-colaborador", "ex colaborador", "1", "2", "3", "1.", "2.", "3."]
        is_valid = any(opt in user_message_lower for opt in valid_options)
        
        
        if not is_valid:
            return generate_response(wa_id, show_options=True)
        
        # Procesar la selección del menú principal
        if "candidato" in user_message_lower or "1" in user_message_lower or "1." in user_message_lower:
            save_user_data(wa_id, "tipo_usuario", "candidato")
            set_user_state(wa_id, UserState.CANDIDATO)
        elif "colaborador" in user_message_lower or "2" in user_message_lower or "2." in user_message_lower:
            save_user_data(wa_id, "tipo_usuario", "colaborador")
            set_user_state(wa_id, UserState.COLABORADOR)
        elif "ex-colaborador" in user_message_lower or "ex colaborador" in user_message_lower or "3" in user_message_lower or "2." in user_message_lower:
            save_user_data(wa_id, "tipo_usuario", "ex-colaborador")
            set_user_state(wa_id, UserState.EX_COLABORADOR)
        
        return generate_response(wa_id)
    
    # Validación específica por estado para otros casos
    validation_error = validate_user_selection(wa_id, user_message)
    if validation_error:
        return validation_error
    
    # Sistema de reconocimiento flexible
    matched_intent = None
    for keyword, intent in KEYWORD_MAPPING.items():
        if keyword in user_message_lower:
            matched_intent = intent
            logging.info(f"🎯 Intención detectada: '{intent}' para palabra clave: '{keyword}'")
            break
    
    # ✅ MANEJO DE "VOLVER AL INICIO" Y "TERMINAR" DESDE OPCIONES
    if matched_intent == "reactivar" or "volver" in user_message_lower or "inicio" in user_message_lower:
        set_user_state(wa_id, UserState.INIT)
        return generate_response(wa_id)
    
    if matched_intent == "terminar" or "terminar" in user_message_lower or "finalizar" in user_message_lower:
        set_user_state(wa_id, UserState.CONVERSACION_TERMINADA)
        return generate_response(wa_id)
    
    # Lógica de transición de estados para CANDIDATO
    if current_state == UserState.CANDIDATO:
        save_user_data(wa_id, "tipo_usuario", "candidato")
        set_user_state(wa_id, UserState.CANDIDATO_DATOS)
        return generate_response(wa_id)
    
    elif current_state == UserState.CANDIDATO_DATOS:
        save_user_data(wa_id, "datos_personales", user_message)
        set_user_state(wa_id, UserState.CANDIDATO_OPCIONES)
        return generate_response(wa_id)
    
    elif current_state == UserState.CANDIDATO_OPCIONES:
        options_keywords = {
            "vacantes": ["revisar", "postularme", "vacantes", "disponibles", "trabajo", "empleo", "1", "1.", "uno"],
            "estatus": ["estatus", "postulación", "seguimiento", "proceso", "mi postulación", "2", "2.", "dos"],
            "reclutador": ["reclutador", "contactar", "humano", "persona", "agente", "3", "3.", "tres"]
        }
        
        best_match = find_best_option_match(user_message_lower, options_keywords)
        
        if best_match == "vacantes" or matched_intent == "vacantes":
            set_user_state(wa_id, UserState.CANDIDATO_VACANTES)
        elif best_match == "estatus" or matched_intent == "estatus":
            set_user_state(wa_id, UserState.CANDIDATO_ESTATUS)
        elif best_match == "reclutador" or matched_intent == "reclutador":
            set_user_state(wa_id, UserState.CANDIDATO_RECLUTADOR)
        else:
            return "❌ No entendí tu respuesta. Por favor elige una de las opciones:\n\n" + generate_response(wa_id, show_options=True)
        return generate_response(wa_id)
    
    elif current_state == UserState.CANDIDATO_VACANTES:
        if matched_intent == "si":
            set_user_state(wa_id, UserState.CANDIDATO_POSTULACION)
            return generate_response(wa_id)
        elif matched_intent == "no":
            # ✅ CORREGIDO: Cambiar estado primero, luego generar respuesta
            set_user_state(wa_id, UserState.CANDIDATO_DESPEDIDA)
            return generate_response(wa_id)
        else:
            return "❌ Por favor responde con 'sí' o 'no'."
    
    elif current_state == UserState.CANDIDATO_POSTULACION:
        if matched_intent == "si":
            set_user_state(wa_id, UserState.CANDIDATO_CV)
            return generate_response(wa_id)
        elif matched_intent == "no":
            set_user_state(wa_id, UserState.CANDIDATO_DESPEDIDA)
            return generate_response(wa_id)
        else:
            return "❌ Por favor responde con 'sí' o 'no'."
    
    # ✅ CORREGIDO: Manejo de estados COLABORADOR
    elif current_state == UserState.COLABORADOR:
        options_keywords = {
            "conocer": ["conocer", "prestaciones", "beneficios", "1", "1.","1 .", "uno"],
            "uso": ["uso", "beneficio", "2", "2.", "2 ." , "dos"],
            "capacitacion": ["capacitación", "desarrollo", "3", "3.", "3 .", "tres"],
            "justificar": ["justificar", "ausencia", "4", "4.", "4 ." , "cuatro"],
            "contactar": ["contactar", "desarrollo organizacional", "5", "5.", "5 ." , "cinco"]
        }
        
        best_match = find_best_option_match(user_message_lower, options_keywords)
        
        if best_match == "conocer":
            set_user_state(wa_id, UserState.COLABORADOR_CONOCER)
        elif best_match == "uso":
            set_user_state(wa_id, UserState.COLABORADOR_USO)
        elif best_match == "capacitacion":
            set_user_state(wa_id, UserState.COLABORADOR_CAPACITACION)
        elif best_match == "justificar":
            set_user_state(wa_id, UserState.COLABORADOR_JUSTIFICAR)
        elif best_match == "contactar":
            set_user_state(wa_id, UserState.COLABORADOR_CONTACTAR)
        else:
            return "❌ No entendí tu respuesta. Por favor elige una de las opciones:\n\n" + generate_response(wa_id, show_options=True)
        return generate_response(wa_id)

    # ✅ CORREGIDO: Manejo de estados EX_COLABORADOR
    elif current_state == UserState.EX_COLABORADOR:
        options_keywords = {
            "constancia": ["solicitar", "constancia", "laboral", "certificado", "1", "1.", "uno"],
            "finiquito": ["finiquito", "liquidación", "pago", "dinero", "2", "2.", "dos"],
            "desarrollo": ["contactar", "desarrollo", "organizacional", "rh", "3", "3.", "tres"],
            "terminar": ["terminar", "4", "4.", "cuatro"]
        }
        
        best_match = find_best_option_match(user_message_lower, options_keywords)
        
        if best_match == "constancia":
            set_user_state(wa_id, UserState.EX_COLABORADOR_CONSTANCIAS)
        elif best_match == "finiquito":
            set_user_state(wa_id, UserState.EX_COLABORADOR_FINIQUITO)
        elif best_match == "desarrollo":
            set_user_state(wa_id, UserState.EX_COLABORADOR_DESARROLLO)
        elif best_match == "terminar":
            set_user_state(wa_id, UserState.CONVERSACION_TERMINADA)  # ✅ CORREGIDO: TERMINADA
        else:
            return "❌ No entendí tu respuesta. Por favor elige una de las opciones:\n\n" + generate_response(wa_id, show_options=True)
        return generate_response(wa_id)

    # Manejar los subestados (solo muestran opciones)
    elif current_state in [UserState.COLABORADOR_CONOCER, UserState.COLABORADOR_USO, 
                          UserState.COLABORADOR_CAPACITACION, UserState.COLABORADOR_JUSTIFICAR,
                          UserState.COLABORADOR_CONTACTAR, UserState.EX_COLABORADOR_CONSTANCIAS,
                          UserState.EX_COLABORADOR_FINIQUITO, UserState.EX_COLABORADOR_DESARROLLO,
                          UserState.ENVIAR_INFO, UserState.CONFIRMAR_TIPO]:
        return generate_response(wa_id, show_options=True)
    
    # Para cualquier otro estado no manejado explícitamente
    return generate_response(wa_id, show_options=True)

def generate_response(wa_id, show_options=True):
    current_state = get_user_state(wa_id)
    flow_data = FLOW_RESPONSES.get(current_state, {})
    
    message = flow_data.get("message", "Lo siento, no entiendo tu mensaje.")
    
    user_info = get_user_data(wa_id)
    if "tipo_usuario" in user_info and current_state != UserState.INIT:
        tipo = user_info["tipo_usuario"].replace("-", " ").title()
        message = message.replace("*Candidato*", f"*{tipo}*")
        message = message.replace("*Colaborador*", f"*{tipo}*")
        message = message.replace("*Ex-Colaborador*", f"*{tipo}*")
    
    if show_options:
        options = flow_data.get("options", [])
        if options:
            message += "\n\n💡 *Opciones:*\n"
            for i, option in enumerate(options, 1):
                message += f"\n{i}. {option['text']}"
            message += "\n\nResponde con el número o texto de la opción."
    
    return message
