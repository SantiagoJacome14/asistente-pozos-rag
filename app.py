"""
Asistente Técnico de Pozos Petroleros - Aplicación Principal
Sistema RAG para análisis de informes técnicos con Streamlit
"""

import streamlit as st
import os
import tempfile
import logging
from pathlib import Path

from utils.document_loader import DocumentLoader
from utils.text_processor import TextProcessor
from utils.vector_store import VectorStore
from utils.qa_system import QASystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Asistente de Pozos Petroleros",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77d4;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
        font-size: 14px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #1f77d4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None

    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = None

    if 'document_loaded' not in st.session_state:
        st.session_state.document_loaded = False

    if 'current_document' not in st.session_state:
        st.session_state.current_document = None

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'well_data' not in st.session_state:
        st.session_state.well_data = None

    if 'document_text' not in st.session_state:
        st.session_state.document_text = None


initialize_session_state()


def setup_api_key(api_key: str) -> bool:
    if not api_key or len(api_key) < 10:
        st.error("❌ API Key de OpenAI inválida")
        return False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        client.models.list()

        st.session_state.api_key = api_key

        st.session_state.vector_store = VectorStore(
            persist_dir="./vector_db",
            api_key=api_key
        )

        st.session_state.qa_system = QASystem(
            api_key=api_key,
            vector_store=st.session_state.vector_store
        )

        return True

    except Exception as e:
        st.error(f"❌ Error validando API Key: {str(e)}")
        logger.error(f"API Key validation error: {str(e)}")
        return False


def process_document(uploaded_file, api_key: str) -> bool:
    if not st.session_state.vector_store:
        st.error("❌ Sistema no inicializado. Configura la API Key primero.")
        return False

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("📄 Cargando documento...")
        progress_bar.progress(20)

        loader = DocumentLoader()
        document_content, doc_name = loader.load_document(tmp_path)

        if not document_content:
            st.error("❌ No se pudo extraer contenido del documento")
            return False

        status_text.text("✂️ Procesando y dividiendo texto...")
        progress_bar.progress(40)

        processor = TextProcessor(chunk_size=1000, chunk_overlap=150)
        chunks = processor.chunk_text(document_content)

        if not chunks:
            st.error("❌ No se pudieron crear chunks del documento")
            return False

        well_data = processor.extract_well_data(document_content)
        st.session_state.well_data = well_data
        st.session_state.document_text = document_content

        status_text.text("🧠 Generando embeddings y almacenando...")
        progress_bar.progress(60)

        collection_name = Path(uploaded_file.name).stem.replace(" ", "_").lower()[:50]
        st.session_state.vector_store.create_or_get_collection(collection_name)

        metadata = {
            "well_data": well_data,
            "total_chunks": len(chunks),
            "document_size": len(document_content)
        }

        st.session_state.vector_store.add_chunks(chunks, doc_name, metadata)
        progress_bar.progress(100)

        st.session_state.document_loaded = True
        st.session_state.current_document = doc_name
        st.session_state.chat_history = []

        os.unlink(tmp_path)

        return True

    except Exception as e:
        st.error(f"❌ Error procesando documento: {str(e)}")
        logger.error(f"Document processing error: {str(e)}")
        return False


def get_well_summary() -> str:
    if not st.session_state.well_data:
        return "No se encontraron datos del pozo"

    data = st.session_state.well_data
    summary_parts = []

    if data.get('depth'):
        summary_parts.append(f"🔷 **Profundidad**: {data['depth']}")
    if data.get('pressure'):
        summary_parts.append(f"📊 **Presión**: {data['pressure']}")
    if data.get('formation'):
        summary_parts.append(f"🪨 **Formación**: {data['formation']}")
    if data.get('producers'):
        summary_parts.append(f"⛰️ **Intervalo productor**: {data['producers']}")
    if data.get('status'):
        summary_parts.append(f"👁️ **Estado**: {data['status']}")

    return "\n\n".join(summary_parts) if summary_parts else "No se extrajeron datos específicos"


def main():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            '<h1 class="main-title">🛢️ Asistente Técnico de Pozos Petroleros</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="subtitle">Sistema RAG para análisis inteligente de informes técnicos</p>',
            unsafe_allow_html=True
        )

    with st.sidebar:
        st.markdown("## ⚙️ Configuración")

        st.markdown("### 🔑 OpenAI API Key")
        api_key_input = st.text_input(
            "Ingresa tu API Key de OpenAI",
            value=st.session_state.api_key,
            type="password",
            help="Tu API Key se usa solo en esta sesión y no se guarda"
        )

        if api_key_input != st.session_state.api_key:
            if st.button("✅ Validar API Key", use_container_width=True):
                if setup_api_key(api_key_input):
                    st.success("✅ API Key validada correctamente")
                    st.rerun()

        if st.session_state.api_key:
            st.success("✅ API Key configurada")

        st.markdown("---")
        st.markdown("### 📊 Estado de la Sesión")

        if st.session_state.document_loaded:
            st.success(f"✅ Documento cargado: {st.session_state.current_document}")

            if st.session_state.vector_store and st.session_state.vector_store.collection:
                info = st.session_state.vector_store.get_collection_info()
                if info:
                    st.info(f"📚 Chunks indexados: {info.get('total_items', 0)}")
        else:
            st.info("⏳ Carga un documento para comenzar")

        st.markdown("---")
        st.markdown("### 🛠️ Herramientas")

        if st.session_state.document_loaded:
            if st.button("🗑️ Limpiar Sesión", use_container_width=True):
                st.session_state.document_loaded = False
                st.session_state.current_document = None
                st.session_state.chat_history = []
                st.session_state.well_data = None
                st.session_state.document_text = None

                if st.session_state.vector_store and st.session_state.vector_store.collection:
                    st.session_state.vector_store.clear_collection()

                st.rerun()

    if not st.session_state.api_key:
        st.info("ℹ️ **Primera vez?** Sigue estos pasos:")
        st.markdown("""
        1. **Obtén una API Key de OpenAI**
        2. **Configura la key** en la barra lateral izquierda
        3. **Carga un documento** en la sección de upload
        4. **Haz preguntas** sobre el contenido del documento

        ---

        ### 📋 Formatos soportados:
        - **PDF** (.pdf)
        - **Word** (.docx)
        - **Excel** (.xlsx, .xls)

        ### 💡 Ejemplos de preguntas:
        - "¿Cuál es la profundidad total del pozo?"
        - "¿Cuáles son los problemas operacionales identificados?"
        - "Resume el estado actual del pozo"
        - "¿Cuáles son los intervalos productores?"
        """)

    else:
        st.markdown("## 📁 Cargar Informe Técnico")

        col1, col2 = st.columns(2)

        with col1:
            uploaded_file = st.file_uploader(
                "Selecciona un archivo",
                type=["pdf", "docx", "xlsx", "xls"],
                help="Carga un informe técnico de pozo"
            )

        with col2:
            if uploaded_file and st.session_state.api_key:
                if st.button("🚀 Procesar Documento", use_container_width=True):
                    with st.spinner("Procesando documento..."):
                        if process_document(uploaded_file, st.session_state.api_key):
                            st.success("✅ Documento procesado exitosamente")
                            st.rerun()

        st.markdown("---")

        if st.session_state.document_loaded:
            with st.expander("📊 Datos del Pozo Extraídos", expanded=False):
                st.markdown(get_well_summary())

            st.markdown("## 💬 Haz tu Pregunta")

            col1, col2 = st.columns([0.85, 0.15])

            with col1:
                user_question = st.text_input(
                    "¿Qué deseas saber del documento?",
                    placeholder="Ejemplo: ¿Cuál es la profundidad total del pozo?",
                    key="user_question"
                )

            with col2:
                ask_button = st.button("🔍 Buscar", use_container_width=True)

            if ask_button:
                if user_question.strip():
                    with st.spinner("🤔 Buscando respuesta..."):
                        try:
                            result = st.session_state.qa_system.answer_question(
                                user_question,
                                n_context=5
                            )

                            if not result or result.get("confianza", 0) == 0:
                                texto = st.session_state.document_text or ""
                                result = {
                                    "respuesta": (
                                        "No encontré una respuesta exacta con el RAG, "
                                        "pero el documento sí fue cargado. Revisa este fragmento:\n\n"
                                        f"{texto[:1500]}"
                                    ),
                                    "confianza": 0.2,
                                    "fuentes": []
                                }

                            st.session_state.chat_history.append({
                                "pregunta": user_question,
                                "respuesta": result
                            })

                        except Exception as e:
                            st.error(f"❌ Error real al responder: {e}")
                else:
                    st.warning("⚠️ Escribe una pregunta primero")

            if st.session_state.chat_history:
                st.markdown("---")
                st.markdown("## 📝 Historial de Preguntas")

                for i, item in enumerate(reversed(st.session_state.chat_history), 1):
                    with st.container():
                        st.markdown(f"### Pregunta {len(st.session_state.chat_history) - i + 1}")
                        st.markdown(f"**❓ {item['pregunta']}**")

                        result = item["respuesta"]

                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.markdown(f"**✅ Respuesta:**\n\n{result.get('respuesta', 'Sin respuesta')}")
                        st.markdown('</div>', unsafe_allow_html=True)

                        confidence = result.get("confianza", 0)
                        confianza_color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                        st.text(f"{confianza_color} Confianza: {confidence:.1%}")

                        sources = result.get("fuentes", [])
                        if sources:
                            st.markdown("**📚 Fuentes utilizadas:**")
                            for j, source in enumerate(sources, 1):
                                with st.expander(
                                    f"Fragmento {j} - {source.get('documento', 'Desconocido')} "
                                    f"({source.get('relevancia', 'N/A')})"
                                ):
                                    st.text(source.get("preview", "Sin preview"))

                        st.markdown("---")

            with st.expander("🔧 Herramientas Avanzadas", expanded=False):
                st.markdown("### 📝 Herramientas Disponibles")

                tool_col1, tool_col2 = st.columns(2)

                with tool_col1:
                    if st.button("📋 Resumir Documento", use_container_width=True):
                        if not st.session_state.document_text:
                            st.warning("⚠️ Primero procesa un documento para generar el resumen.")
                        else:
                            with st.spinner("Generando resumen..."):
                                try:
                                    summary = st.session_state.qa_system.summarize_document(
                                        st.session_state.document_text
                                    )

                                    if not summary or "error" in str(summary).lower():
                                        summary = st.session_state.document_text[:2500]

                                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                                    st.markdown(f"**Resumen del Documento:**\n\n{summary}")
                                    st.markdown('</div>', unsafe_allow_html=True)

                                except Exception as e:
                                    st.error(f"❌ Error real al generar resumen: {e}")
                                    st.markdown("### Vista rápida del documento")
                                    st.write(st.session_state.document_text[:2500])

                with tool_col2:
                    if st.button("🎯 Extraer Puntos Clave", use_container_width=True):
                        if st.session_state.chat_history:
                            last_question = st.session_state.chat_history[-1]["pregunta"]

                            with st.spinner("Extrayendo puntos clave..."):
                                try:
                                    key_points = st.session_state.qa_system.extract_key_points(
                                        last_question,
                                        n_context=3
                                    )

                                    if isinstance(key_points, dict):
                                        texto_puntos = key_points.get(
                                            "puntos_clave",
                                            "No se encontraron puntos clave."
                                        )
                                    else:
                                        texto_puntos = str(key_points)

                                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                                    st.markdown(f"**Puntos Clave:**\n\n{texto_puntos}")
                                    st.markdown('</div>', unsafe_allow_html=True)

                                except Exception as e:
                                    st.error(f"❌ Error real al extraer puntos clave: {e}")
                        else:
                            st.warning("⚠️ Haz una pregunta primero")
        else:
            st.info("⏳ Carga un documento para comenzar")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px'>
    <p>🛢️ Asistente Técnico de Pozos</p>
    <p>Desarrollado por Santiago Jacome para la loca de Jeronimo Alvarez    </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()