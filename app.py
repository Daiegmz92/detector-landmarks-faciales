# app.py
"""
Aplicación Streamlit para detección de landmarks faciales.
"""
import streamlit as st
from PIL import Image
import cv2
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import mediapipe as mp

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


# Configuración de MediaPipe para la detección en tiempo real
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)  # Puntos verdes


class FaceMeshTransformer(VideoTransformerBase):
    def __init__(self):
        # Inicializa FaceMesh DENTRO de la clase
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        # Convierte el cuadro de video a un array de numpy
        image = frame.to_ndarray(format="bgr24")

        # Procesa la imagen con MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)

        # Dibuja los landmarks si se detecta una cara
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec
                )

        # Devuelve el cuadro procesado
        return av.VideoFrame.from_ndarray(image, format="bgr24")


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

    /* Título del sidebar más pequeño */
    .sidebar .sidebar-content h2 {
        font-size: 1.2rem !important;
        margin-bottom: 1rem;
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
st.markdown('<p class="subtitle">¿Te gustaría ver cómo te "ve" la IA?<br>¿Sabías que la inteligencia artificial puede mapear cientos de puntos en tu rostro?<br>Esta aplicación detecta <strong>478 puntos clave</strong> en rostros humanos usando MediaPipe.<br>Descubre la magia de la visión por computadora en acción.</p>', unsafe_allow_html=True)

# Selector de modo (simplificado para evitar errores de DOM)
modo = st.selectbox(
    "Seleccioná el modo de detección:",
    ["Subir imagen", "Cámara en tiempo real"],
    help="Elegí entre subir una imagen o usar la cámara en vivo"
)

# Sidebar con información mejorada usando expanders
with st.sidebar:
    st.title("🧠 Información Técnica", help="Información detallada sobre landmarks faciales y aplicaciones")

    # Expander para la Información Técnica
    with st.expander("🎯 ¿Qué son los Landmarks?", expanded=True):
        st.write("Son **478 puntos de referencia** que mapean:")
        st.markdown("""
        👁️ **Ojos:** iris, párpados, cejas
        👃 **Nariz:** puente, fosas, base
        👄 **Boca:** labios, comisuras, dientes
        😊 **Contorno facial:** mandíbula, pómulos
        """)

    # Expander para las Aplicaciones
    with st.expander("🚀 Aplicaciones", expanded=True):
        st.markdown("""
        📸 **Filtros AR:** Instagram, Snapchat
        🎭 **Análisis emocional:** expresiones faciales
        🎬 **Animación:** películas, videojuegos
        🔐 **Biometría:** autenticación facial
        🏥 **Medicina:** análisis anatómico
        """)

    if modo == "Cámara en tiempo real":
        with st.expander("📹 Consejos para la Cámara", expanded=True):
            st.markdown("""
            ✅ **Iluminación:** buena luz natural
            🎯 **Posición:** rostro centrado
            🏃 **Movimiento:** evita sacudidas bruscas
            👀 **Orientación:** mira de frente a la cámara
            📏 **Distancia:** 30-50 cm de la lente
            """)

    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #bcbcbc; font-size: 0.9rem;'>
        🏫 <strong>Proyecto Académico - Laboratorio 2</strong><br>
        Instituto de Formación Técnica Superior N°24<br>
        👨‍🏫 <strong>Profesor:</strong> Matías Barreto<br>
        👩‍💻 <strong class='developer-name'>Desarrolladora:</strong> <span class='developer-name'>Daiana Gómez</span><br>
        📅 <strong>Fecha:</strong> Octubre 2025
    </div>
    """, unsafe_allow_html=True)

if modo == "Subir imagen":
    # Uploader de imagen con control de errores
    uploaded_file = st.file_uploader(
        "Subí una imagen con un rostro",
        type=["jpg", "jpeg", "png"],
        help="Formatos aceptados: JPG, JPEG, PNG. Sube una imagen válida para detectar landmarks faciales."
    )

    if uploaded_file is not None:
        # Control de errores: manejo de archivos inválidos
        try:
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

        except Exception as e:
            # Error genérico: archivo corrupto o inválido
            st.error(
                "❌ ¡Ups! Hubo un error al procesar la imagen. " +
                "Asegúrate de que sea un archivo JPG o PNG válido y vuelve a intentarlo."
            )
            st.info("💡 Tip: Si el archivo es muy grande, intenta con una imagen más pequeña.")

        with col2:
            st.markdown("### 🎯 Landmarks Detectados")
            st.image(cv2_to_pil(imagen_procesada), caption="478 puntos faciales detectados")

        # Mostrar información de detección
        st.divider()

        if info["deteccion_exitosa"]:
            # ÉXITO: Mostrar mensaje verde y estadísticas
            st.success("✅ ¡Detección exitosa! Se encontraron landmarks faciales.")

            st.markdown("### 📊 Estadísticas de Detección")
            col1, col2, col3 = st.columns(3)

            with col1:
                with st.container(border=True):
                    st.metric("👥 Rostros detectados", info["rostros_detectados"])

            with col2:
                with st.container(border=True):
                    st.metric("🎯 Landmarks detectados", f"{info['total_landmarks']}/{TOTAL_LANDMARKS}")

            with col3:
                with st.container(border=True):
                    try:
                        TOTAL_LANDMARKS = get_config()
                        porcentaje = (info['total_landmarks'] / TOTAL_LANDMARKS) * 100
                        color = "🟢" if porcentaje > 90 else "🟡" if porcentaje > 70 else "🔴"
                        st.metric(f"{color} Precisión", f"{porcentaje:.1f}%")
                    except:
                        st.metric("📊 Estado", "Completado")
        else:
            # ERROR: Mostrar mensaje rojo y sugerencias
            st.error("❌ No se detectó ningún rostro en la imagen. Por favor, sube una imagen diferente.")

            with st.expander("💡 Sugerencias para mejorar la detección"):
                st.markdown("""
                👀 Asegúrate de que haya un rostro claramente visible en la imagen
                💡 El rostro debe estar bien iluminado y mirando hacia la cámara
                📸 Evita imágenes borrosas o de baja calidad
                🔍 Prueba con una imagen más cercana al rostro
                """)

elif modo == "Cámara en tiempo real":
    st.header("📹 Detección en Tiempo Real")
    st.info("Haz clic en 'START'. Tu navegador te pedirá permiso para usar la cámara. Asegúrate de seleccionar la cámara correcta cuando aparezca el selector de dispositivos.")

    webrtc_streamer(
        key="face_mesh_detector",
        video_processor_factory=FaceMeshTransformer,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
    )

else:
    # Mensaje de bienvenida mejorado
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #2a2a35 0%, #3a3a45 100%); border-radius: 20px; margin: 20px 0; border: 1px solid #444; color: #ffffff;'>
        <h3 style='color: #667eea; margin-bottom: 1rem;'>🎯 ¡Bienvenido!</h3>
        <p style='font-size: 1.1rem; color: #bcbcbc;'>Seleccioná un modo arriba para comenzar el análisis facial</p>
    </div>
    """, unsafe_allow_html=True)

    # Información técnica mejorada
    st.markdown("### 🔬 Información Técnica")

    col_tech1, col_tech2 = st.columns(2)

    with col_tech1:
        with st.container(border=True):
            st.markdown("### 🧠 Tecnología Principal")
            st.markdown("""
            - **MediaPipe**: Framework de ML de Google
            - **478 Landmarks**: Precisión médica
            - **OpenCV**: Procesamiento de imágenes
            - **Streamlit**: Interfaz web moderna
            """)

    with col_tech2:
        with st.container(border=True):
            st.markdown("### 📊 Capacidades del Sistema")
            st.markdown("""
            - **Detección múltiple**: Varios rostros
            - **Mapeo anatómico**: Detalle profesional
            - **Aplicaciones AR**: Filtros en tiempo real
            - **Análisis emocional**: Expresiones faciales
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