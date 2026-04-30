"""
Script de ejemplo para usar la aplicación como librería Python
Sin Streamlit - Uso programático
"""

import logging
from utils.document_loader import DocumentLoader
from utils.text_processor import TextProcessor
from utils.vector_store import VectorStore
from utils.qa_system import QASystem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_rag_system():
    """Ejemplo completo del sistema RAG."""
    
    # Configuración
    API_KEY = "tu-api-key-aqui"  # Reemplazar con tu API Key
    DOCUMENT_PATH = "data/informes/ejemplo.pdf"  # Ruta al documento
    
    print("="*60)
    print("EJEMPLO DE SISTEMA RAG - ANÁLISIS DE POZOS")
    print("="*60)
    
    try:
        # 1. Cargar documento
        print("\n[1] Cargando documento...")
        loader = DocumentLoader()
        document_content, doc_name = loader.load_document(DOCUMENT_PATH)
        print(f"✓ Documento cargado: {doc_name}")
        print(f"  Tamaño: {len(document_content)} caracteres")
        
        # 2. Procesar texto
        print("\n[2] Procesando texto...")
        processor = TextProcessor(chunk_size=1000, chunk_overlap=150)
        chunks = processor.chunk_text(document_content)
        well_data = processor.extract_well_data(document_content)
        
        print(f"✓ Texto dividido en {len(chunks)} chunks")
        print(f"  Datos del pozo:")
        for key, value in well_data.items():
            if value:
                print(f"    - {key}: {value}")
        
        # 3. Crear base vectorial
        print("\n[3] Creando base vectorial...")
        vector_store = VectorStore(persist_dir="./vector_db", api_key=API_KEY)
        vector_store.create_or_get_collection("ejemplo_pozo")
        vector_store.add_chunks(chunks, doc_name)
        print("✓ Base vectorial creada y poblada")
        
        # 4. Crear sistema QA
        print("\n[4] Inicializando sistema QA...")
        qa_system = QASystem(api_key=API_KEY, vector_store=vector_store)
        print("✓ Sistema QA listo")
        
        # 5. Hacer preguntas
        print("\n[5] Haciendo preguntas...")
        
        questions = [
            "¿Cuál es la profundidad total del pozo?",
            "¿Cuáles son los problemas operacionales?",
            "Resume el estado del pozo",
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n  Pregunta {i}: {question}")
            result = qa_system.answer_question(question, n_context=3)
            
            print(f"  Respuesta: {result['respuesta'][:200]}...")
            print(f"  Confianza: {result['confianza']:.1%}")
            print(f"  Fuentes: {len(result['fuentes'])} fragmentos utilizados")
        
        # 6. Generar resumen
        print("\n[6] Generando resumen...")
        summary = qa_system.summarize_document(document_content[:5000])
        print(f"  Resumen:\n  {summary[:300]}...")
        
        print("\n" + "="*60)
        print("✓ Ejemplo completado exitosamente")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        logger.exception("Error en ejemplo")

if __name__ == "__main__":
    example_rag_system()
