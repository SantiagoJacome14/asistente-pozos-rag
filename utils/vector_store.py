"""
Módulo para gestionar el almacenamiento vectorial con ChromaDB.
Maneja embeddings y recuperación de documentos.
"""

from typing import List, Dict, Tuple, Optional
import chromadb
from openai import OpenAI
import os
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class VectorStore:
    """Gestor de base de datos vectorial con ChromaDB."""

    def __init__(self, persist_dir: str = "./vector_db", api_key: str = ""):
        """
        Inicializa el almacén vectorial.
        
        Args:
            persist_dir: Directorio para persistencia de datos
            api_key: Clave API de OpenAI para embeddings
        """
        self.persist_dir = persist_dir
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None
        
        # Crear directorio si no existe
        os.makedirs(persist_dir, exist_ok=True)
        
        # Inicializar ChromaDB con persistencia
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)
        
        self.collection = None
        self.current_document_id = None
        
        logger.info(f"Vector store inicializado en {persist_dir}")

    def create_or_get_collection(self, collection_name: str) -> None:
        """
        Crea o obtiene una colección en ChromaDB.
        
        Args:
            collection_name: Nombre de la colección
        """
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Colección obtenida o creada: {collection_name}")
        except Exception as e:
            logger.error(f"Error creando u obteniendo colección: {str(e)}")
            raise
        
        self.current_document_id = collection_name

    def add_chunks(self, chunks: List[str], document_name: str, 
                   metadata: Optional[Dict] = None) -> None:
        """
        Añade chunks de texto a la colección.
        
        Args:
            chunks: Lista de chunks de texto
            document_name: Nombre del documento fuente
            metadata: Metadatos adicionales del documento
        """
        if not self.client:
            raise ValueError("API key de OpenAI no configurada")
        
        if not self.collection:
            raise ValueError("Colección no inicializada")
        
        ids = []
        embeddings = []
        metadatas = []
        
        logger.info(f"Generando embeddings para {len(chunks)} chunks...")
        
        for i, chunk in enumerate(chunks):
            try:
                # Generar embedding usando OpenAI
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk
                )
                embedding = response.data[0].embedding
                
                # Preparar ID y metadatos
                chunk_id = f"{document_name}_{i}"
                chunk_metadata = {
                    "document_name": document_name,
                    "chunk_index": i,
                    "chunk_text": chunk[:500],  # Primeros 500 chars como preview
                    "timestamp": datetime.now().isoformat(),
                }
                
                if metadata:
                    chunk_metadata.update(metadata)
                
                ids.append(chunk_id)
                embeddings.append(embedding)
                metadatas.append(chunk_metadata)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Embeddings generados: {i + 1}/{len(chunks)}")
                    
            except Exception as e:
                logger.error(f"Error generando embedding para chunk {i}: {str(e)}")
                continue
        
        # Añadir a la colección
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            logger.info(f"Añadidos {len(ids)} chunks a la colección")

    def search(self, query: str, n_results: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Busca chunks similares a la consulta.
        
        Args:
            query: Consulta de búsqueda
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de tuplas (texto_chunk, similaridad, metadatos)
        """
        if not self.client:
            raise ValueError("API key de OpenAI no configurada")
        
        if not self.collection:
            raise ValueError("Colección no inicializada")
        
        try:
            # Generar embedding de la consulta
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = response.data[0].embedding
            
            # Buscar en ChromaDB
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    include=["documents", "distances", "metadatas"]
                )
            except Exception as fallback_error:
                logger.warning(f"Error con query_embeddings, reintentando con query_texts: {fallback_error}")
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents", "distances", "metadatas"]
                )
            
            # Procesar resultados
            search_results = []
            
            if results and results['documents'] and len(results['documents']) > 0:
                for doc, distance, metadata in zip(
                    results['documents'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                ):
                    # Convertir distancia a similaridad (cosine)
                    similarity = 1 - distance
                    search_results.append((doc, similarity, metadata))
            
            logger.info(f"Búsqueda completada: {len(search_results)} resultados")
            return search_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            return []

    def delete_collection(self, collection_name: str) -> None:
        """Elimina una colección."""
        try:
            self.chroma_client.delete_collection(name=collection_name)
            self.collection = None
            logger.info(f"Colección eliminada: {collection_name}")
        except Exception as e:
            logger.error(f"Error eliminando colección: {str(e)}")

    def list_collections(self) -> List[str]:
        """Lista todas las colecciones disponibles."""
        try:
            collections = self.chroma_client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Error listando colecciones: {str(e)}")
            return []

    def get_collection_info(self) -> Dict:
        """Obtiene información sobre la colección actual."""
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            return {
                "nombre": self.collection.name,
                "total_items": count,
                "metadatos": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de colección: {str(e)}")
            return {}

    def clear_collection(self) -> None:
        """Limpia todos los elementos de la colección actual."""
        if not self.collection:
            return
        
        try:
            # Obtener todos los IDs
            all_data = self.collection.get()
            if all_data and all_data['ids']:
                self.collection.delete(ids=all_data['ids'])
                logger.info("Colección limpiada")
        except Exception as e:
            logger.error(f"Error limpiando colección: {str(e)}")
