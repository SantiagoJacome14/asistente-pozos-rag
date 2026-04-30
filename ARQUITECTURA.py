"""
DOCUMENTACIÓN TÉCNICA - ARQUITECTURA DEL SISTEMA
Asistente Técnico de Pozos Petroleros
"""

# ============================================================================
# 1. ARQUITECTURA GENERAL DEL SISTEMA
# ============================================================================

"""
El sistema implementa un arquitectura RAG (Retrieval Augmented Generation) 
modular y escalable:

┌─────────────────────────────────────────────────────────────────────┐
│                        INTERFAZ STREAMLIT                            │
│  (app.py) - UI interactiva para usuario final                        │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
    ┌────▼───────────┐          ┌─────────▼─────────┐
    │ DOCUMENT LOAD  │          │   QA SYSTEM       │
    │   (entrada)    │          │  (salida)         │
    └────┬───────────┘          └─────────▲─────────┘
         │                              │
    ┌────▼──────────────┐          ┌────┴──────────┐
    │ TEXT PROCESSOR    │          │  VECTOR SEARCH│
    │ - Chunks         │          │  (Búsqueda)   │
    │ - Extracción     │          └────▲──────────┘
    │ - Análisis       │               │
    └────┬─────────────┘          ┌────┴──────────────┐
         │                        │   VECTOR STORE    │
         │                        │   ChromaDB + Cache│
         └──────────┬─────────────┤                   │
                    │             └──────┬────────────┘
         ┌──────────▼──────┐            │
         │  OPENAI EMBEDDINGS ◄─────────┘
         │  (Generación)
         └──────────────────┘
"""

# ============================================================================
# 2. FLUJO DE PROCESAMIENTO DE DOCUMENTOS
# ============================================================================

"""
ENTRADA (Usuario carga archivo)
    │
    ▼
[DocumentLoader]
- Detecta formato (PDF/DOCX/XLSX)
- Extrae texto y tablas
- Normaliza contenido
- Retorna: (texto, nombre_archivo)
    │
    ▼
[TextProcessor]
- Limpia y normaliza texto
- Divide en chunks (1000 chars, overlap 150)
- Extrae datos clave (profundidad, presión, etc.)
- Retorna: [chunks], {well_data}
    │
    ▼
[Generador de Embeddings]
- Envía chunks a OpenAI
- Genera vectors (embedding model)
- Retorna: [embeddings]
    │
    ▼
[VectorStore - ChromaDB]
- Almacena vectors + metadatos
- Indexa para búsqueda rápida
- Persiste en disco
"""

# ============================================================================
# 3. FLUJO DE PREGUNTA Y RESPUESTA (RAG)
# ============================================================================

"""
ENTRADA (Usuario hace pregunta)
    │
    ▼
[Generar Embedding de Pregunta]
- Convierte pregunta a vector
- Mismo modelo que documentos
    │
    ▼
[Búsqueda Vectorial]
- ChromaDB busca los K chunks más similares
- Usa similitud coseno (HNSW)
- Retorna: Top-5 chunks relevantes
    │
    ▼
[Contexto Agrupado]
- Une chunks en contexto
- Añade metadatos (fuente, relevancia)
- Limita tamaño (~2000 chars)
    │
    ▼
[Generación de Respuesta]
- Prompt: Contexto + Pregunta
- Env a GPT-3.5-turbo
- Temperature: 0.2 (determinístico)
- Max tokens: 1000
    │
    ▼
[Post-procesamiento]
- Calcula confianza
- Extrae fuentes
- Formatea respuesta
    │
    ▼
SALIDA (Respuesta + Metadatos)
"""

# ============================================================================
# 4. MÓDULOS Y SUS RESPONSABILIDADES
# ============================================================================

"""
📁 APP.PY (2000+ líneas)
├─ Interfaz Streamlit completa
├─ Gestión de sesiones (st.session_state)
├─ Uploads y validaciones
├─ Rendering de UI
└─ Integración de módulos

📦 UTILS/DOCUMENT_LOADER.PY (~180 líneas)
├─ Clase: DocumentLoader
├─ Métodos:
│  ├─ load_document(file_path) → (content, name)
│  ├─ _load_pdf()
│  ├─ _load_docx()
│  ├─ _load_excel()
│  └─ validate_file()
└─ Manejo: PDF, DOCX, XLSX

📦 UTILS/TEXT_PROCESSOR.PY (~250 líneas)
├─ Clase: TextProcessor
├─ Métodos:
│  ├─ chunk_text() → [chunks]
│  ├─ extract_well_data() → {datos}
│  ├─ extract_summary_section() → str
│  ├─ get_statistics() → {stats}
│  └─ _clean_text()
└─ Responsables: División, análisis, extracción

📦 UTILS/VECTOR_STORE.PY (~300 líneas)
├─ Clase: VectorStore
├─ Métodos:
│  ├─ create_or_get_collection()
│  ├─ add_chunks() → persistencia
│  ├─ search(query) → [(doc, score, meta)]
│  ├─ list_collections()
│  ├─ get_collection_info()
│  └─ delete_collection()
├─ Motor: ChromaDB
├─ Embeddings: OpenAI API
└─ Storage: Persistente en disco

📦 UTILS/QA_SYSTEM.PY (~350 líneas)
├─ Clase: QASystem
├─ Métodos:
│  ├─ answer_question() → {respuesta}
│  ├─ summarize_document() → resumen
│  ├─ extract_key_points() → {puntos}
│  ├─ _generate_response()
│  ├─ _calculate_confidence()
│  └─ _prepare_context()
├─ Modelo: GPT-3.5-turbo
└─ Retorna: Respuesta + Metadatos
"""

# ============================================================================
# 5. TECNOLOGÍAS UTILIZADAS
# ============================================================================

"""
FRONTEND:
- Streamlit 1.28.1
  └─ Framework web Python para UI interactiva
  └─ Sin necesidad de HTML/CSS/JS
  └─ Hot-reload automático
  
PROCESAMIENTO DE DOCUMENTOS:
- PyPDF2 3.0.1
  └─ Extracción de texto de PDFs
  └─ Manejo de metadatos
  
- python-docx 0.8.11
  └─ Lectura de archivos Word (.docx)
  └─ Extracción de texto y tablas
  
- openpyxl 3.10.10 + pandas 2.0.3
  └─ Lectura de Excel (.xlsx, .xls)
  └─ Conversión a strings
  
EMBEDDINGS Y LLM:
- OpenAI 1.3.5
  └─ API oficial de OpenAI
  └─ Embedding: text-embedding-3-small
  └─ Chat: gpt-3.5-turbo
  
BASE DE DATOS VECTORIAL:
- ChromaDB 0.4.10
  └─ Vector database local
  └─ Storage: DuckDB + Parquet
  └─ Búsqueda HNSW (rápida)
  └─ Persistencia automática
  
UTILIDADES:
- LangChain 0.1.0
  └─ (Instalado pero opc. en v1)
  └─ Futuras integraciones RAG
  
- NumPy 1.24.3
  └─ Cálculos numéricos
  └─ Operaciones de arrays
"""

# ============================================================================
# 6. FLUJO DE DATOS DETALLADO
# ============================================================================

"""
ETAPA 1: CARGA DE DOCUMENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Usuario selecciona archivo
        ↓
Validación de formato
        ↓
Lectura a bytes temporales
        ↓
DocumentLoader.load_document()
        ├─ Detecta extensión
        ├─ Llama método específico (_load_pdf, etc.)
        └─ Retorna texto limpio
        
Salida: String de 10,000-100,000+ caracteres


ETAPA 2: PROCESAMIENTO
━━━━━━━━━━━━━━━━━━━━━
TextProcessor.chunk_text()
    - Input: Texto 100K caracteres
    - Split: 1000 char chunks, 150 char overlap
    - Lógica: Rompe en puntos/líneas nuevas
    - Output: 80-150 chunks
    
TextProcessor.extract_well_data()
    - Búsqueda con regex:
      ├─ \d+ metros → profundidad
      ├─ \d+ psi → presión
      ├─ formación|Formation → geología
      └─ etc...
    - Output: {depth, pressure, formation...}
    
Salida: [chunks], {well_data}


ETAPA 3: EMBEDDINGS
━━━━━━━━━━━━━━━━━━
Para cada chunk:
    1. Envía a OpenAI API
    2. Model: text-embedding-3-small
    3. Retorna vector 1536 dims
    4. Costo: ~$0.02 / 1M tokens
    
Batch: 80 chunks ≈ 2-5 segundos


ETAPA 4: ALMACENAMIENTO VECTORIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ChromaDB:
    ├─ Crea collection "well_xxxxx"
    ├─ Añade IDs: "nombre_doc_0", "nombre_doc_1"...
    ├─ Guarda embeddings (1536 dims c/u)
    ├─ Almacena metadatos:
    │  ├─ document_name
    │  ├─ chunk_index
    │  ├─ chunk_text (preview)
    │  └─ timestamp
    ├─ Indexa con HNSW
    └─ Persiste en ./vector_db/*.parquet


ETAPA 5: RESPUESTA A PREGUNTAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Usuario: "¿Profundidad del pozo?"
        ↓
1. Generar embedding de pregunta (OpenAI)
   └─ Vector 1536 dims
        ↓
2. Búsqueda en ChromaDB
   ├─ HNSW busca vecinos más cercanos
   ├─ Calcula similitud coseno
   ├─ Retorna Top-5 chunks + score
        ↓
3. Preparar contexto
   ├─ Unir fragmentos
   ├─ Limitar tamaño (~2000 chars)
   ├─ Adicionar metadatos
        ↓
4. Generar respuesta
   ├─ Crear prompt:
   │  ├─ System: "Eres experto técnico..."
   │  └─ User: "[CONTEXTO]\n¿Pregunta?"
   ├─ Enviar a GPT-3.5-turbo
   │  ├─ Temperature: 0.2
   │  ├─ Max tokens: 1000
   ├─ Retorna: "La profundidad es 3,500m..."
        ↓
5. Post-procesamiento
   ├─ Calcular confianza (70-95%)
   ├─ Extraer fuentes
   └─ Formatear para UI


ETAPA 6: VISUALIZACIÓN
━━━━━━━━━━━━━━━━━━━━━
Streamlit renderiza:
    ├─ Respuesta en texto
    ├─ Medidor de confianza
    ├─ Expandibles de fuentes
    ├─ Historial de chat
    └─ Metadatos
"""

# ============================================================================
# 7. COMPLEJIDAD Y RENDIMIENTO
# ============================================================================

"""
TIEMPO DE PROCESAMIENTO:
┌──────────────────────┬──────────┬─────────────┐
│ Operación            │ Latencia │ Notas       │
├──────────────────────┼──────────┼─────────────┤
│ Carga de PDF (10pag) │ 5-10s    │ Rápido      │
│ Procesamiento texto  │ 2-3s     │ Local       │
│ Generar embeddings   │ 30-60s   │ ~80 chunks  │
│ Upload a ChromaDB    │ 5-10s    │ Indexado    │
│ Búsqueda vectorial   │ 0.5-1s   │ Local HNSW  │
│ Generar respuesta    │ 5-10s    │ OpenAI API  │
├──────────────────────┼──────────┼─────────────┤
│ TOTAL                │ 1-2 min  │ Primera vez │
│ Preguntas siguientes │ 10-15s   │ Solo API    │
└──────────────────────┴──────────┴─────────────┘

MEMORIA:
- ChromaDB: 100-500 MB (variable)
- Embeddings en RAM: ~150 MB (80 chunks)
- Streamlit cache: 50-100 MB

COSTOS (OpenAI):
- Embeddings: ~$1-3 por 100 documentos
- Chat: ~$0.10-0.50 por 100 preguntas
- Ejemplo: 1000 docs + 1000 preguntas ≈ $10-15
"""

# ============================================================================
# 8. PATRONES DE DISEÑO
# ============================================================================

"""
✓ MÓDULOS INDEPENDIENTES
  └─ Cada utilidad es importable por separado
  └─ No hay dependencias circulares
  
✓ SEPARACIÓN DE CONCEPTOS
  ├─ DocumentLoader: solo I/O
  ├─ TextProcessor: solo lógica de texto
  ├─ VectorStore: solo persistencia vectorial
  └─ QASystem: solo lógica RAG
  
✓ INYECCIÓN DE DEPENDENCIAS
  └─ VectorStore y QASystem reciben api_key
  └─ Facilita testing y mocking
  
✓ MANEJO DE ERRORES
  ├─ Try/except en operaciones críticas
  ├─ Logging de errores
  ├─ Mensajes amigables al usuario
  
✓ CONFIGURACIÓN EXTERNALIZADA
  └─ config.py para parámetros ajustables
  
✓ ESTADO PERSISTENTE
  └─ ChromaDB persiste entre sesiones
  └─ Streamlit session_state para UI
  
✓ PROMPTS OPTIMIZADOS
  ├─ System role: Define comportamiento
  ├─ Temperature: Control determinístico
  └─ Max tokens: Límite de respuesta
"""

# ============================================================================
# 9. EXTENSIBILIDAD
# ============================================================================

"""
AGREGAR NUEVO FORMATO DE DOCUMENTO:
1. Crear método en DocumentLoader: _load_xyz()
2. Importar librería (pypptx, etc.)
3. Retornar string de texto
4. Actualizar SUPPORTED_FORMATS

CAMBIAR MODELO LLM:
1. En qa_system.py: self.model = "gpt-4"
2. Ajustar temperature/tokens según modelo
3. Requiere mayor API key balance

USAR OTRO VECTOR DB:
1. Crear clase WeaviateStore similar a VectorStore
2. Implementar add_chunks(), search()
3. Cambiar import en app.py

AGREGAR BASES DE DATOS SQL:
1. Usar SQLAlchemy
2. Guardar historial de preguntas/respuestas
3. Estadísticas de uso
4. Autenticación de usuarios
"""

# ============================================================================
# 10. LIMITACIONES Y CONSIDERACIONES
# ============================================================================

"""
⚠️ LIMITACIONES ACTUALES:

1. API Key expuesta en sesión
   └─ Solución: Backend separado con auth

2. ChromaDB local (no distribuido)
   └─ Solución: Migrar a Weaviate/Pinecone

3. Límite de tamaño de contexto (GPT-3.5)
   └─ Max 4K tokens entrada
   └─ Solución: Usar GPT-4 (8K-128K)

4. Costo por API calls
   └─ ~$10-15/100 documentos + 100 preguntas
   └─ Solución: Embeddings locales (Ollama)

5. No hay multi-usuario
   └─ Solución: Agregar autenticación + BD

6. Datos no encriptados
   └─ Solución: Encripción de vector_db

7. Sin cache de embeddings repetidos
   └─ Solución: Redis cache

⚠️ CONSIDERACIONES:

- ChromaDB requiere reindexación para cambios
- OpenAI API tiene rate limits
- Documentos muy grandes pueden tardar minutos
- La calidad depende del modelo elegido
- Hallucinations posibles (siempre presentes)
"""

# ============================================================================
# 11. ROADMAP DE MEJORAS
# ============================================================================

"""
🎯 CORTO PLAZO (semanas):
  ✓ Cache de embeddings locales
  ✓ Soporte para .txt y .csv
  ✓ Exportar respuestas a PDF
  ✓ Dark mode para interfaz

🎯 MEDIANO PLAZO (meses):
  ✓ Backend API (FastAPI)
  ✓ Base de datos SQL para historial
  ✓ Autenticación de usuarios
  ✓ Embeddings locales (Ollama/Hugging Face)
  ✓ Soporte para GPT-4

🎯 LARGO PLAZO (trimestres):
  ✓ Integración con Pinecone (distribuido)
  ✓ Fine-tuning con datos específicos de pozos
  ✓ Mobile app (React Native)
  ✓ Enterprise features (SSO, SAML)
  ✓ Analytics dashboard
"""

# ============================================================================
# 12. REFERENCIAS Y RECURSOS
# ============================================================================

"""
DOCUMENTACIÓN:
- OpenAI API: https://platform.openai.com/docs
- Streamlit: https://docs.streamlit.io
- ChromaDB: https://docs.trychroma.com
- LangChain: https://python.langchain.com

TUTORIALES:
- RAG Workflows: https://docs.llamaindex.ai
- Vector Databases: https://www.youtube.com/@VectorPodcast

MODELOS ALTERNATIVOS:
- Ollama: Embeddings locales (https://ollama.ai)
- GPT-4: Mejor calidad (~10x costo)
- Claude: Anthropic (contexto 100K)

HERRAMIENTAS RELACIONADAS:
- LlamaIndex: Alternativa a LangChain
- Semantic Router: Routing inteligente
- LLMChain Monitoring: Depuración
"""

# FIN DE DOCUMENTACIÓN TÉCNICA
