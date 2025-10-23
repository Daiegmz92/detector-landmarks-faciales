# app.py
"""
Aplicación Streamlit para detección de landmarks faciales.
"""
import streamlit as st
from PIL import Image
import cv2
import numpy as np

# Lazy imports to avoid initialization issues
def get_detector():
    from src.detector import FaceLandmarkDetector
    return FaceLandmarkDetector()

def get_utils():
    from src.utils import pil_to_cv2, cv2_to_pil, resize_image
    return pil_to_cv2, cv2_to_pil, resize_image

def get_config():
    from src.config import TOTAL_LANDMARKS
    return TOTAL_LANDMARKS


# Configuración de la página
st.set_page_config(
    page_title="Detector de Landmarks Faciales",
    layout="wide",
    page_icon="🤖"
)

# Estilos CSS personalizados mejorados
st.markdown("""
<style>
    /* Fondo principal con degradado sutil */
    .main {
        background: linear-gradient(180deg, #0e0e12 0%, #1b1b22 100%);
        color: #ffffff;
    }

    /* Header principal centrado */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }

    /* Subtítulo mejorado */
    .subtitle {
        text-align: center;
        color: #bcbcbc;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    /* Botones con gradiente */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* Tarjetas métricas */
    .metric-card {
        background: linear-gradient(135deg, #2a2a35 0%, #3a3a45 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #444;
        color: #ffffff;
    }

    /* Sidebar mejorada */
    .sidebar-content {
        background: linear-gradient(180deg, #1e1e25 0%, #2a2a35 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid #444;
        color: #ffffff;
    }

    /* Separadores sutiles */
    .section-separator {
        border: 0.5px solid #555;
        margin: 15px 0;
    }

    /* Footer institucional elegante */
    .footer {
        background: linear-gradient(135deg, #1e1e25 0%, #2a2a35 100%);
        text-align: center;
        color: #bcbcbc;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #444;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Transiciones suaves para imágenes */
    img {
        transition: opacity 0.5s ease-in-out, transform 0.3s ease;
    }
    img:hover {
        transform: scale(1.02);
    }

    /* Mejorar radio buttons */
    .stRadio > div {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
    }

    /* Mejorar file uploader */
    .stFileUploader > div {
        background: rgba(255,255,255,0.05);
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 20px;
    }

    /* Nombre de desarrolladora en violeta */
    .developer-name {
        color: #764ba2;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Título y descripción con estilo
st.markdown('<h1 class="main-header">🤖 Detector de Landmarks Faciales</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Esta aplicación detecta <strong>478 puntos clave</strong> en rostros humanos usando MediaPipe.<br>Subí una imagen con un rostro y mirá la magia de la visión por computadora.</p>', unsafe_allow_html=True)

# Selector de modo (simplificado para evitar errores de DOM)
modo = st.selectbox(
    "Seleccioná el modo de detección:",
    ["Imagen subida", "Cámara en tiempo real"],
    help="Elegí entre subir una imagen o usar la cámara en vivo"
)

# Sidebar con información mejorada
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

    st.markdown("## 🧠 Información Técnica")
    st.markdown('<hr class="section-separator">', unsafe_allow_html=True)

    st.markdown("### 🎯 ¿Qué son los Landmarks?")
    st.markdown("""
    Son **478 puntos de referencia** que mapean:
    - 👁️ **Ojos**: iris, párpados, cejas
    - 👃 **Nariz**: puente, fosas, base
    - 👄 **Boca**: labios, comisuras, dientes
    - 😊 **Contorno facial**: mandíbula, pómulos
    """)

    st.markdown('<hr class="section-separator">', unsafe_allow_html=True)

    st.markdown("### 🚀 Aplicaciones")
    st.markdown("""
    - 📸 **Filtros AR**: Instagram, Snapchat
    - 🎭 **Análisis emocional**: expresiones faciales
    - 🎬 **Animación**: películas, videojuegos
    - 🔐 **Biometría**: autenticación facial
    - 🏥 **Medicina**: análisis anatómico
    """)

    if modo == "Cámara en tiempo real":
        st.markdown('<hr class="section-separator">', unsafe_allow_html=True)
        st.markdown("### 📹 Consejos para la Cámara")
        st.markdown("""
        ✅ **Iluminación**: buena luz natural
        🎯 **Posición**: rostro centrado
        🏃 **Movimiento**: evita sacudidas bruscas
        👀 **Orientación**: mira de frente a la cámara
        📏 **Distancia**: 30-50 cm de la lente
        """)

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #bcbcbc; font-size: 0.9rem;'>
        🏫 <strong>Laboratorio 2</strong><br>
        Instituto de Formación Técnica Superior N°24<br>
        👨‍🏫 <strong>Profesor:</strong> Matías Barreto<br>
        👩‍💻 <strong class='developer-name'>Desarrolladora:</strong> <span class='developer-name'>Daiana Gómez</span><br>
        📅 <strong>Fecha:</strong> Octubre 2025
    </div>
    """, unsafe_allow_html=True)

if modo == "Imagen subida":
    # Uploader de imagen
    uploaded_file = st.file_uploader(
        "Subí una imagen con un rostro",
        type=["jpg", "jpeg", "png"],
        help="Formatos aceptados: JPG, JPEG, PNG"
    )

    if uploaded_file is not None:
        # Cargar imagen
        imagen_original = Image.open(uploaded_file)

        # Convertir a formato OpenCV
        pil_to_cv2, cv2_to_pil, resize_image = get_utils()
        imagen_cv2 = pil_to_cv2(imagen_original)

        # Redimensionar si es muy grande
        imagen_cv2 = resize_image(imagen_cv2, max_width=800)

        # Columnas para mostrar antes/después con mejor diseño
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("### 📸 Imagen Original")
            st.image(cv2_to_pil(imagen_cv2), caption="Imagen subida por el usuario")

        # Detectar landmarks con mejor feedback
        with st.spinner("🔍 Analizando imagen y detectando landmarks..."):
            try:
                detector = get_detector()
                pil_to_cv2, cv2_to_pil, resize_image = get_utils()
                TOTAL_LANDMARKS = get_config()
                imagen_procesada, landmarks, info = detector.detect(imagen_cv2)
                detector.close()
            except Exception as e:
                st.error(f"Error en la detección: {str(e)}")
                st.stop()

        with col2:
            st.markdown("### 🎯 Landmarks Detectados")
            st.image(cv2_to_pil(imagen_procesada), caption="478 puntos faciales detectados")

        # Mostrar información de detección
        st.divider()

        if info["deteccion_exitosa"]:
            st.success("✅ ¡Detección exitosa! Se encontraron landmarks faciales.")

            # Métricas mejoradas con estilo
            st.markdown("### 📊 Estadísticas de Detección")
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("👥 Rostros detectados", info["rostros_detectados"])
                st.markdown('</div>', unsafe_allow_html=True)

            with metric_col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("🎯 Landmarks detectados", f"{info['total_landmarks']}/{TOTAL_LANDMARKS}")
                st.markdown('</div>', unsafe_allow_html=True)

            with metric_col3:
                try:
                    TOTAL_LANDMARKS = get_config()
                    porcentaje = (info['total_landmarks'] / TOTAL_LANDMARKS) * 100
                    color = "🟢" if porcentaje > 90 else "🟡" if porcentaje > 70 else "🔴"
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric(f"{color} Precisión", f"{porcentaje:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                except:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("📊 Estado", "Completado")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("No se detectó ningún rostro en la imagen")
            st.info("""
            **Consejos**:
            - Asegurate de que el rostro esté bien iluminado
            - El rostro debe estar mirando hacia la cámara
            - Probá con una imagen de mayor calidad
            """)

elif modo == "Cámara en tiempo real":
    st.markdown("### 📹 Detección en Tiempo Real")
    st.info("🎥 Esta funcionalidad requiere acceso a la cámara de tu dispositivo para análisis en vivo.")

    # Información sobre limitaciones en la nube
    st.warning("⚠️ **Nota**: El modo de cámara en tiempo real no está disponible en Streamlit Cloud debido a restricciones de seguridad del navegador. Esta funcionalidad solo funciona cuando ejecutás la aplicación localmente.")

    # Mostrar información alternativa
    st.markdown("""
    ### 📹 Modo Cámara en Tiempo Real

    Esta funcionalidad requiere acceso directo a la cámara de tu dispositivo y solo funciona cuando ejecutás la aplicación localmente.

    **Para usar la detección en tiempo real:**
    1. **Descargá el proyecto** desde GitHub
    2. **Instalá las dependencias** localmente
    3. **Ejecutá** `run_app.bat` (Windows) o `python run_app.py` (Linux/Mac)
    4. **Seleccioná** "Cámara en tiempo real"
    5. **Permití el acceso** a la cámara cuando el navegador lo solicite

    **Características del modo local:**
    - ✅ Detección en tiempo real a 30 FPS
    - ✅ Procesamiento de video frame por frame
    - ✅ Controles de inicio/detención
    - ✅ Visualización de landmarks en vivo
    """)

    # Información técnica
    with st.expander("🔧 Detalles Técnicos del Modo Cámara"):
        st.markdown("""
        **Tecnología utilizada:**
        - OpenCV para captura de video
        - MediaPipe para detección de landmarks
        - Procesamiento en tiempo real
        - Optimización para 640x480 resolución

        **Limitaciones en la nube:**
        - Streamlit Cloud no permite acceso directo a hardware
        - Restricciones de seguridad del navegador
        - Solo funciona en entornos locales
        """)

    # Placeholder para evitar errores de DOM
    FRAME_WINDOW = st.empty()
    FRAME_WINDOW.info("🎥 **Modo no disponible en la nube** - Ejecutá localmente para usar la cámara")

else:
    # Mensaje de bienvenida mejorado
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 20px; margin: 20px 0;'>
        <h3>🎯 ¡Bienvenido al Detector de Landmarks Faciales!</h3>
        <p style='font-size: 1.1rem; color: #555;'>Seleccioná un modo arriba para comenzar el análisis facial</p>
    </div>
    """, unsafe_allow_html=True)

    # Información técnica
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧠 Tecnología")
        st.markdown("""
        - **MediaPipe**: Framework de Google para ML
        - **478 Landmarks**: Puntos faciales de precisión
        - **Tiempo real**: Procesamiento en vivo
        - **OpenCV**: Visión por computadora
        """)

    with col2:
        st.markdown("### 📊 Capacidades")
        st.markdown("""
        - **Detección facial**: Rostros múltiples
        - **Mapeo anatómico**: Detalle médico
        - **Aplicaciones AR**: Filtros y efectos
        - **Análisis emocional**: Expresiones
        """)

    # Ejemplo visual mejorado
    st.markdown("### 🎨 Ejemplo de Detección")
    st.image(
        "https://ai.google.dev/static/mediapipe/images/solutions/face_landmarker_keypoints.png?hl=es-419",
        caption="MediaPipe detecta 478 landmarks faciales con precisión médica",
        width=500
    )

# Footer institucional mejorado
st.markdown("""
<div style='background-color:#1e1e25;padding:15px;border-radius:15px;text-align:center;color:#bcbcbc;font-size:0.9rem;margin-top:2rem;border:1px solid #444;'>
<small>🏫 <strong>Proyecto Académico - Laboratorio 2</strong><br>
Instituto de Formación Técnica Superior N°24<br>
👨‍🏫 <strong>Profesor:</strong> Matías Barreto<br>
👩‍💻 <strong style='color:#764ba2;'>Desarrolladora:</strong> <span style='color:#764ba2;font-weight:600;'>Daiana Gómez</span><br>
📅 <strong>Fecha:</strong> Octubre 2025</small>
</div>
""", unsafe_allow_html=True)