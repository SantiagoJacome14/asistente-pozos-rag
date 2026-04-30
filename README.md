# 🛢️ Asistente Técnico de Pozos Petroleros - Sistema RAG

Sistema completo de análisis de informes técnicos de pozos usando Retrieval Augmented Generation (RAG). Procesamiento inteligente de documentos con respuestas basadas en el contenido del documento.

## 📋 Características Principales

✅ **Carga de Múltiples Formatos**
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx, .xls)

✅ **Procesamiento Inteligente**
- Extracción de texto y tablas
- División en chunks con solapamiento
- Generación de embeddings con OpenAI
- Almacenamiento vectorial persistente con ChromaDB

✅ **Sistema de Preguntas y Respuestas (RAG)**
- Búsqueda semántica de contexto relevante
- Respuestas generadas con GPT-3.5-turbo
- Indicador de confianza
- Visualización de fuentes utilizadas

✅ **Extracción de Datos Clave**
- Profundidad total del pozo
- Presión
- Formación geológica
- Intervalos productores
- Estado del pozo

✅ **Herramientas Avanzadas**
- Resumen automático de documentos
- Extracción de puntos clave
- Historial de preguntas y respuestas

## 🎯 Requisitos Previos

- **Python 3.8+** instalado
- **API Key de OpenAI** (obtener en https://platform.openai.com/api-keys)
- **pip** o **conda** para gestionar paquetes
- **Git** (opcional, para clonar el proyecto)

## 🚀 Instalación Rápida

### 1. Clonar o Descargar el Proyecto

```bash
# Opción 1: Si tienes Git
git clone <url-del-repo>
cd asistente_pozos

# Opción 2: Descargar y extraer manualmente
# Ya tienes la carpeta asistente_pozos
cd asistente_pozos
```

### 2. Crear Entorno Virtual (Recomendado)

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
python -m pip install -r requirements.txt
```

**Nota**: La primera instalación puede tardar unos minutos, especialmente por ChromaDB.

### 4. Ejecutar la Aplicación

```bash
streamlit run app.py
```

Si el comando `streamlit` no se reconoce, usa:

```bash
python -m streamlit run app.py
```

El navegador se abrirá automáticamente en `http://localhost:8501`

## 📊 Estructura del Proyecto

```
asistente_pozos/
│
├── app.py                    # Aplicación principal (Streamlit)
├── requirements.txt          # Dependencias de Python
├── README.md                 # Este archivo
│
├── data/
│   └── informes/            # Carpeta para documentos (opcional)
│
├── vector_db/               # Base de datos vectorial (autocreat)
│   └── (archivos de ChromaDB)
│
└── utils/
    ├── __init__.py
    ├── document_loader.py   # Carga de archivos multiformato
    ├── text_processor.py    # Procesamiento y análisis de texto
    ├── vector_store.py      # Gestión de ChromaDB y embeddings
    └── qa_system.py         # Sistema RAG de preguntas/respuestas
```

## 📝 Explicación de Archivos

### `app.py` - Aplicación Principal
- Interfaz Streamlit completa
- Gestión de sesiones de usuario
- Flujo de carga y procesamiento de documentos
- Sistema de chat con historial
- Herramientas avanzadas

### `utils/document_loader.py` - Cargador de Documentos
- Clase `DocumentLoader` para cargar múltiples formatos
- Extracción de texto desde PDF, DOCX, XLSX
- Manejo de errores y validación de archivos

### `utils/text_processor.py` - Procesador de Texto
- Clase `TextProcessor` para dividir texto en chunks
- Extracción de datos clave del pozo (profundidad, presión, etc.)
- Limpieza y normalización de texto
- Extracción de secciones de resumen
- Estadísticas del documento

### `utils/vector_store.py` - Base Vectorial
- Clase `VectorStore` que gestiona ChromaDB
- Generación de embeddings con OpenAI
- Búsqueda semántica de chunks similares
- Persistencia de datos vectoriales

### `utils/qa_system.py` - Sistema RAG
- Clase `QASystem` para pregunt-respuesta
- Integración con GPT-3.5-turbo
- Cálculo de confianza en respuestas
- Generación de resúmenes
- Extracción de puntos clave

## 💻 Guía de Uso

### Paso 1: Configurar API Key

1. Abre la aplicación (ya está corriendo en `http://localhost:8501`)
2. En la barra lateral izquierda, ingresa tu **API Key de OpenAI**
3. Haz clic en "✅ Validar API Key"
4. Verás un mensaje de éxito si la key es válida

### Paso 2: Cargar Documento

1. En la sección "📁 Cargar Informe Técnico", haz clic en "Selecciona un archivo"
2. Elige un archivo en formato PDF, DOCX o XLSX
3. Haz clic en "🚀 Procesar Documento"
4. Espera a que se procese (mostrará barra de progreso)
5. Verás un mensaje de éxito cuando termine

### Paso 3: Hacer Preguntas

1. En la sección "💬 Haz tu Pregunta", escribe tu pregunta en lenguaje natural
2. Haz clic en "🔍 Buscar"
3. La aplicación busca fragmentos relevantes y genera una respuesta
4. Verás:
   - La respuesta completa
   - Un indicador de confianza (🟢🟡🔴)
   - Fragmentos de fuentes utilizadas

### Paso 4: Usar Herramientas Avanzadas

En la sección "🔧 Herramientas Avanzadas" puedes:
- **📋 Resumir Documento**: Genera un resumen ejecutivo
- **🎯 Extraer Puntos Clave**: Extrae los 5 puntos más importantes

## 🔧 Configuración Avanzada

### Ajustar Parámetros de Chunks

En `utils/text_processor.py`, línea ~14:

```python
processor = TextProcessor(
    chunk_size=1000,      # Tamaño de cada chunk
    chunk_overlap=150     # Solapamiento entre chunks
)
```

**Recomendaciones:**
- `chunk_size=1000`: Bueno para documentos técnicos largos
- `chunk_size=500`: Mejor para documentos cortos
- `chunk_overlap=150`: Balance entre contexto y eficiencia

### Cambiar Modelo de OpenAI

En `utils/qa_system.py`, línea ~18:

```python
self.model = "gpt-3.5-turbo"  # Cambiar a "gpt-4" para mejor calidad
self.temperature = 0.2         # 0=determinístico, 1=creativo
self.max_tokens = 1000         # Máximo de tokens en respuesta
```

### Cambiar Tamaño de Embeddings

En `utils/vector_store.py`, línea ~72:

```python
response = self.client.embeddings.create(
    model="text-embedding-3-small",  # O "text-embedding-3-large"
    input=chunk
)
```

## 🐛 Solución de Problemas

### Error: "API Key inválida"
- ✅ Verifica que la key sea correcta en https://platform.openai.com/api-keys
- ✅ Asegúrate de que tengas créditos disponibles en OpenAI
- ✅ La key debe empezar con "sk-"

### Error: "ModuleNotFoundError: No module named..."
```bash
# Reinstala las dependencias desde el intérprete correcto
python -m pip install -r requirements.txt --force-reinstall
```

### Error: "Archivo PDF/DOCX corrupto"
- ✅ Intenta abrir el archivo en su aplicación nativa (Adobe, Word, Excel)
- ✅ Si falla, el archivo está corrupto
- ✅ Prueba con otro archivo

### La aplicación es lenta
- ✅ Los embeddings tardan tiempo (especialmente la primera vez)
- ✅ ChromaDB se optimiza después de la primera consulta
- ✅ Usa `chunk_size` más pequeño en `text_processor.py`

### No encuentra información relevante
- ✅ Prueba hacer preguntas más específicas
- ✅ Aumenta `n_results` en `qa_system.py` línea ~39
- ✅ Asegúrate de que el documento contiene la información

## 📚 Ejemplos de Uso

### Ejemplo 1: Análisis Básico

```
Pregunta: ¿Cuál es la profundidad total del pozo?
Respuesta: La profundidad total es de 3,500 metros.
Confianza: 95%
```

### Ejemplo 2: Análisis de Problemas

```
Pregunta: ¿Cuáles son los problemas operacionales identificados?
Respuesta: Se identificaron los siguientes problemas:
1. Corrosión en la tubería de revestimiento
2. Depósito de parafina en la línea de flujo
3. Baja presión en el pozo
Confianza: 85%
```

### Ejemplo 3: Análisis Técnico

```
Pregunta: Resume el estado del pozo
Respuesta: El pozo se encuentra en producción normal...
Confianza: 90%
```

## 🔐 Seguridad y Privacidad

- ⚠️ **API Key**: Se transmite solo a OpenAI, no se guarda en la app
- ⚠️ **Documentos**: Se almacenan en `vector_db/` localmente
- ⚠️ **Embeddings**: Se generan con OpenAI (envía texto a sus servidores)
- ✅ Todos los datos se procesan localmente en tu máquina

## 💰 Costos de OpenAI

- **Embeddings** (text-embedding-3-small): ~$0.02 por 1M tokens
- **GPT-3.5-turbo**: ~$0.0005 por 1K tokens (entrada)
- **Ejemplo**: Procesar 100 documentos típicos: ~$5-10

## 📊 Rendimiento Esperado

| Operación | Tiempo |
|-----------|--------|
| Procesar PDF de 10 páginas | 30-60 segundos |
| Generar respuesta | 5-15 segundos |
| Búsqueda semántica | 1-3 segundos |
| Resumen de documento | 10-20 segundos |

## 🚀 Mejoras Futuras

- [ ] Soporte para más formatos (PPT, RTF, TXT)
- [ ] Chat multiusuario con bases de datos
- [ ] Caché de embeddings para acelerar
- [ ] Integración con modelos locales (Ollama, LLaMA)
- [ ] Exportar respuestas a PDF/Word
- [ ] Visualización de tablas extraídas
- [ ] Integración con bases de datos SQL

## 🤝 Contribuir

Si encuentras bugs o tienes sugerencias:
1. Crea un issue describiendo el problema
2. Envía un pull request con tu solución

## 📄 Licencia

Este proyecto es de código abierto bajo licencia MIT.

## 👨‍💻 Autor

Desarrollado como herramienta especializada para análisis de informes técnicos en la industria petrolera.

## 📞 Soporte

Si tienes problemas:
- 📧 Revisa el archivo de logs en el terminal
- 🐛 Consulta la sección "Solución de Problemas" arriba
- 📚 Lee la documentación de [Streamlit](https://docs.streamlit.io)
- 🔗 Consulta [OpenAI API Docs](https://platform.openai.com/docs)

---

**¡Disfruta analizando tus informes de pozos!** 🛢️⚡
