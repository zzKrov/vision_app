import os
import streamlit as st
import streamlit.components.v1 as components
import base64
from openai import OpenAI

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL (LAYOUT WIDE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Análisis de Imagen // Krov Industries",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# LÍNEA BASE VISUAL: GRADIENTES COBALTO Y FLUIDOS
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #030712 !important;
    color: #f3f4f6 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }

/* 1. Gradiente multicolor animado */
.stApp {
    background: linear-gradient(135deg, #030712 0%, #06122e 30%, #09204c 60%, #04091a 100%) !important;
    background-size: 300% 300% !important;
    animation: cobaltGradient 20s ease infinite alternate !important;
}

@keyframes cobaltGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Esferas orgánicas de plasma azul y cian */
.fluid-plasma-1 {
    position: fixed;
    top: 10%;
    left: -150px;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, rgba(0, 240, 255, 0.14) 0%, rgba(37, 99, 235, 0.04) 60%, transparent 75%);
    border-radius: 40% 60% 70% 30% / 50% 60% 40% 50%;
    filter: blur(85px);
    animation: plasmaDrift1 22s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

.fluid-plasma-2 {
    position: fixed;
    bottom: 5%;
    right: -120px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, rgba(0, 240, 255, 0.03) 60%, transparent 75%);
    border-radius: 60% 40% 50% 50% / 40% 50% 60% 50%;
    filter: blur(95px);
    animation: plasmaDrift2 26s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

@keyframes plasmaDrift1 {
    0% { transform: translate(0, 0) rotate(0deg); }
    50% { transform: translate(140px, 80px) rotate(180deg) scale(1.15); }
    100% { transform: translate(50px, 160px) rotate(360deg); }
}

@keyframes plasmaDrift2 {
    0% { transform: translate(0, 0) rotate(0deg); }
    50% { transform: translate(-120px, -90px) rotate(-180deg) scale(1.2); }
    100% { transform: translate(-40px, -140px) rotate(-360deg); }
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
    font-size: 2.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1rem;
    text-shadow: 0 0 25px rgba(56, 189, 248, 0.35);
}

.preview-frame {
    background: #080f24;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 20px rgba(56, 189, 248, 0.1);
}

.response-card {
    background: rgba(9, 18, 44, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 1.4rem;
    line-height: 1.65;
    color: #f1f5f9;
    font-size: 1.02rem;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6);
    min-height: 220px;
}

.status-indicator {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #38bdf8;
    margin-bottom: 8px;
}
</style>

<div class="fluid-plasma-1"></div>
<div class="fluid-plasma-2"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PARTÍCULAS CIAN Y EFECTO MOUSE
# ---------------------------------------------------------
components.html(
    """
    <script>
    const pDoc = window.parent.document;
    if (!pDoc.getElementById('gpt-particles-canvas')) {
        const canvas = pDoc.createElement('canvas');
        canvas.id = 'gpt-particles-canvas';
        canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:1;opacity:0.55;';
        pDoc.body.prepend(canvas);

        const ctx = canvas.getContext('2d');
        let w = canvas.width = window.parent.innerWidth;
        let h = canvas.height = window.parent.innerHeight;

        window.parent.addEventListener('resize', () => {
            w = canvas.width = window.parent.innerWidth;
            h = canvas.height = window.parent.innerHeight;
        });

        const particles = [];
        for (let i = 0; i < 45; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                r: Math.random() * 2 + 0.6,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                alpha: Math.random() * 0.7 + 0.2
            });
        }

        let mouse = { x: -1000, y: -1000 };
        window.parent.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        function loop() {
            ctx.clearRect(0, 0, w, h);
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;
                if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(0, 240, 255, ${p.alpha})`;
                ctx.shadowBlur = 8;
                ctx.shadowColor = '#00f0ff';
                ctx.fill();

                const d = Math.hypot(p.x - mouse.x, p.y - mouse.y);
                if (d < 120) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = `rgba(56, 189, 248, ${0.45 * (1 - d / 120)})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
            requestAnimationFrame(loop);
        }
        loop();
    }
    </script>
    """,
    height=0,
    width=0
)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.markdown('<div class="brand-signature">Krov Industries · Visión Multimodal</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Análisis de Imagen con IA</div>', unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1.25], gap="large")

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
            placeholder="Ejemplo: ¿Qué modelo de arquitectura o qué elementos clave destacan en la toma?",
            height=100
        )

    analyze_button = st.button("Analizar imagen con GPT-4o", use_container_width=True)

with col_output:
    st.markdown('<div class="status-indicator">● RESULTADOS DE LA INFERENCIA</div>', unsafe_allow_html=True)

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
