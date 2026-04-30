"""
Archivo de configuración para la aplicación
"""

# Configuración de Chunks
CHUNK_SIZE = 1000  # Tamaño de cada chunk en caracteres
CHUNK_OVERLAP = 150  # Solapamiento entre chunks

# Configuración de Búsqueda
N_SEARCH_RESULTS = 5  # Número de fragmentos a recuperar
SEARCH_THRESHOLD = 0.3  # Umbral de similitud mínima

# Configuración de OpenAI
OPENAI_MODEL_CHAT = "gpt-3.5-turbo"  # Modelo para chat
OPENAI_MODEL_EMBEDDING = "text-embedding-3-small"  # Modelo para embeddings
OPENAI_TEMPERATURE = 0.2  # 0 = determinístico, 1 = creativo
OPENAI_MAX_TOKENS = 1000  # Máximo de tokens en respuesta

# Configuración de ChromaDB
CHROMADB_PATH = "./vector_db"  # Ruta de almacenamiento
CHROMADB_COLLECTION_PREFIX = "well_"  # Prefijo para colecciones

# Configuración de Streamlit
STREAMLIT_THEME = "light"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_MAX_UPLOAD_SIZE = 200  # MB

# Extracción de Datos del Pozo
EXTRACT_WELL_DEPTH = True
EXTRACT_WELL_PRESSURE = True
EXTRACT_WELL_FORMATION = True
EXTRACT_WELL_PRODUCERS = True
EXTRACT_WELL_STATUS = True

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"

# Patrones de Regex para Extracción
DEPTH_UNITS = ["m", "metros", "ft", "pies", "m.b.s.l."]
PRESSURE_UNITS = ["psi", "bar", "kpa", "atm"]
