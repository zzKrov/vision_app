import os
import streamlit as st
import base64
from openai import OpenAI

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------
st.set_page_config(
    page_title="Análisis de Imagen // Krov Industries",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# ESTILOS VISUALES
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #030712 !important;
    color: #f3f4f6 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #38bdf8;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.main-title {
    text-align: center;
    font-size: 2.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1.5rem;
}

div.stButton > button {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    background: #0284c7 !important;
    color: #ffffff !important;
    border: 1px solid #38bdf8 !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.25s ease !important;
}

div.stButton > button:hover {
    background: #0369a1 !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
    transform: translateY(-2px);
}

.response-card {
    background: #0b1329;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 1.5rem;
    line-height: 1.6;
    color: #f1f5f9;
}
</style>
""", unsafe_allow_html=True)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.markdown('<div class="brand-signature">Krov Industries · Visión Multimodal</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Análisis de Imagen con IA</div>', unsafe_allow_html=True)

ke = st.text_input(
    'Clave de API de OpenAI',
    type="password",
    placeholder="sk-...",
    help="Ingresa tu clave de OpenAI para habilitar la visión por computadora."
)
if ke:
    os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ.get('OPENAI_API_KEY', '')

client = None
if api_key:
    client = OpenAI(api_key=api_key)

uploaded_file = st.file_uploader(
    "Selecciona o arrastra una imagen:",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:
    with st.expander("Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

show_details = st.toggle("Hacer una pregunta específica sobre la imagen", value=False)

additional_details = ""
if show_details:
    additional_details = st.text_area(
        "Escribe aquí tu pregunta o contexto complementario:",
        placeholder="Ejemplo: ¿Qué tipo de arquitectura aparece en la fotografía?",
        disabled=not show_details
    )

analyze_button = st.button("Analizar imagen", use_container_width=True)

if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando la imagen con GPT-4o..."):
        base64_image = encode_image(uploaded_file)
    
        prompt_text = "Describe en español y de forma clara lo que observas en la imagen."
    
        if show_details and additional_details.strip():
            prompt_text += f"\n\nContexto o pregunta complementaria del usuario:\n{additional_details}"
    
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
    
        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,   
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(
                        f'<div class="response-card">{full_response}▌</div>',
                        unsafe_allow_html=True
                    )
            message_placeholder.markdown(
                f'<div class="response-card">{full_response}</div>',
                unsafe_allow_html=True
            )
    
        except Exception as e:
            st.error(f"Ocurrió un error al procesar la solicitud con OpenAI: {e}")
else:
    if not uploaded_file and analyze_button:
        st.warning("Por favor, sube una imagen antes de solicitar el análisis.")
    if not api_key and analyze_button:
        st.warning("Por favor, ingresa tu clave de API de OpenAI para continuar.")
