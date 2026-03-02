from groq import Groq
from secret_config import CHAT_BOT_KEY  

PROMPT_DONANTE = (
    "Eres un asistente de soporte para RedPulse (banco de sangre). "
    "Tu usuario es DONANTE. Responde como soporte para donantes. "
    "Enfócate en: donaciones, requisitos, frecuencia, notificaciones, puntos y redención de bonos. "
    "Responde solo preguntas relacionadas con estas funcionalidades y sobre la donación de sangre en general."
)

PROMPT_SOLICITANTE = (
    "Eres un asistente de soporte para RedPulse (banco de sangre). "
    "Tu usuario es SOLICITANTE. Responde como soporte para solicitantes. "
    "Enfócate en: cómo crear solicitud, estados (pendiente/aceptada/denegada), requisitos generales y procesos. "
    "Responde solo preguntas relacionadas con estas funcionalidades y sobre la donación de sangre en general."
)

def _prompt_por_rol(rol: str) -> str:
    if rol == "DONANTE":
        return PROMPT_DONANTE
    return PROMPT_SOLICITANTE

def generate_response(usuario_mensaje: str, user_data: dict = None, rol_forzado: str = None) -> str:
    rol = rol_forzado if rol_forzado else "SOLICITANTE"
    prompt = _prompt_por_rol(rol)

    client = Groq(api_key=CHAT_BOT_KEY)

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": usuario_mensaje}
        ],
        temperature=1,
        max_tokens=2000,
        top_p=1,
        stream=False,
        stop=None,
    )

    mensaje_obtenido = respuesta.choices[0].message.content

    nombre = (user_data or {}).get("nombre")
    if nombre:
        saludo = f"Hola, {nombre}. Tu rol es {rol}."
    else:
        saludo = f"Hola. Tu rol es {rol}."

    return f"{saludo}\n\n{mensaje_obtenido}"