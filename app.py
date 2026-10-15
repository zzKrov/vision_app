import os
import streamlit as st
import base64
from openai import OpenAI

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL (LAYOUT WIDE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Análisis de Imagen con IA // Krov Industries",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# ESTILOS PANORÁMICOS Y RESPONSIVOS
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
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #38bdf8;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1.2rem;
}

.preview-frame {
    background: #080f24;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
}

.response-card {
    background: #09122c;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 1.4rem;
    line-height: 1.65;
    color: #f1f5f9;
    font-size: 1.02rem;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5);
    min-height: 220px;
}

.status-indicator {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #38bdf8;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.markdown('<div class="brand-signature">Krov Industries · Visión Multimodal</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Análisis de Imagen con IA</div>', unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown('<div class="status-indicator">● ENTRADA DE IMAGEN Y CONTEXTO</div>', unsafe_allow_html=True)
    
    ke = st.text_input(
        'Clave de API de OpenAI',
        type="password",
        placeholder="sk-...",
        value=os.environ.get("OPENAI_API_KEY", "")
    )
    if ke:
        os.environ['OPENAI_API_KEY'] = ke

    api_key = os.environ.get('OPENAI_API_KEY', '')
    client = OpenAI(api_key=api_key) if api_key else None

    uploaded_file = st.file_uploader(
        "Seleccionar archivo de imagen:",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file:
        st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    show_details = st.toggle("Añadir pregunta o contexto complementario", value=False)
    additional_details = ""
    if show_details:
        additional_details = st.text_area(
            "Escribe aquí tu consulta específica:",
            placeholder="Ejemplo: ¿Qué modelo de vehículo o qué tipo de paisaje se observa?",
            height=100
        )

    analyze_button = st.button("Analizar imagen con GPT-4o", use_container_width=True)

with col_output:
    st.markdown('<div class="status-indicator">● RESULTADOS DEL ANÁLISIS</div>', unsafe_allow_html=True)

    if uploaded_file is not None and api_key and analyze_button:
        with st.spinner("Procesando imagen con GPT-4o..."):
            base64_image = encode_image(uploaded_file)
            prompt_text = "Describe en español de forma analítica, precisa y estructurada lo que observas en la imagen."
            if show_details and additional_details.strip():
                prompt_text += f"\n\nContexto o pregunta complementaria del usuario:\n{additional_details}"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
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
                st.error(f"Error durante la inferencia con OpenAI: {e}")
    else:
        if not uploaded_file and analyze_button:
            st.warning("Selecciona una imagen antes de solicitar el análisis.")
        elif not api_key and analyze_button:
            st.warning("Ingresa una clave de API de OpenAI válida para continuar.")
        else:
            st.markdown(
                """
                <div class="response-card" style="display:flex; justify-content:center; align-items:center; text-align:center; color:#94a3b8;">
                    <div>
                        <div style="font-size:1.1rem; color:#38bdf8; margin-bottom:4px;">Panel de análisis en reposo</div>
                        <div style="font-size:0.85rem;">Carga una imagen y presiona el botón para generar la descripción analítica.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
