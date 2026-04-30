"""
Módulo para el sistema de preguntas y respuestas (RAG).
Combina retrieval y generación de respuestas.
"""

from typing import List, Dict, Tuple, Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class QASystem:
    """Sistema de preguntas y respuestas con contexto (RAG)."""

    def __init__(self, api_key: str, vector_store):
        """
        Inicializa el sistema QA.
        
        Args:
            api_key: Clave API de OpenAI
            vector_store: Instancia de VectorStore
        """
        self.client = OpenAI(api_key=api_key)
        self.vector_store = vector_store
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.2
        self.max_tokens = 1000

    def answer_question(self, question: str, n_context: int = 5) -> Dict:
        """
        Responde una pregunta basada en el contexto del documento.
        
        Args:
            question: Pregunta del usuario
            n_context: Número de chunks para contexto
            
        Returns:
            Diccionario con respuesta y fuentes
        """
        try:
            # 1. Buscar contexto relevante
            search_results = self.vector_store.search(question, n_results=n_context)
            
            if not search_results:
                return {
                    "respuesta": "No encontré información relevante en el documento para responder tu pregunta.",
                    "confianza": 0,
                    "fuentes": [],
                    "tokens_utilizados": 0
                }
            
            # 2. Preparar contexto
            context_text = self._prepare_context(search_results)
            sources = self._extract_sources(search_results)
            
            # 3. Generar respuesta
            response = self._generate_response(question, context_text)
            
            return {
                "respuesta": response["answer"],
                "confianza": response["confidence"],
                "fuentes": sources,
                "tokens_utilizados": response["tokens_used"],
                "contexto_utilizado": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error respondiendo pregunta: {str(e)}")
            return {
                "respuesta": f"Error procesando tu pregunta: {str(e)}",
                "confianza": 0,
                "fuentes": [],
                "tokens_utilizados": 0,
                "error": str(e)
            }

    def _prepare_context(self, search_results: List[Tuple[str, float, Dict]]) -> str:
        """Prepara el contexto para el modelo."""
        context_parts = []
        
        for i, (chunk, similarity, metadata) in enumerate(search_results, 1):
            source_info = metadata.get("document_name", "Desconocido")
            chunk_idx = metadata.get("chunk_index", "?")
            
            # Limitar tamaño del chunk mostrado
            display_chunk = chunk[:800] if len(chunk) > 800 else chunk
            
            context_parts.append(
                f"[FRAGMENTO {i} - {source_info} (Relevancia: {similarity:.2%})]\n"
                f"{display_chunk}\n"
            )
        
        return "\n".join(context_parts)

    def _extract_sources(self, search_results: List[Tuple[str, float, Dict]]) -> List[Dict]:
        """Extrae información de fuentes de los resultados."""
        sources = []
        
        for chunk, similarity, metadata in search_results:
            source = {
                "documento": metadata.get("document_name", "Desconocido"),
                "chunk_index": metadata.get("chunk_index", -1),
                "relevancia": f"{similarity:.1%}",
                "preview": metadata.get("chunk_text", "")[:200]
            }
            sources.append(source)
        
        return sources

    def _generate_response(self, question: str, context: str) -> Dict:
        """
        Genera una respuesta usando OpenAI.
        
        Args:
            question: Pregunta del usuario
            context: Contexto de los documentos
            
        Returns:
            Diccionario con respuesta y metadatos
        """
        system_prompt = """Eres un experto técnico en análisis de pozos petroleros. 
Tu tarea es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado.

IMPORTANTES:
1. Si la información no está en el contexto, di claramente: "No encuentro esta información en los documentos disponibles"
2. Sé específico y técnico en tu lenguaje
3. Incluye números, medidas y unidades cuando sea relevante
4. Si hay múltiples fragmentos relevantes, sintetiza la información
5. Mantén tu respuesta concisa y enfocada
6. Responde en español

Contexto del documento:
"""

        user_message = f"""Pregunta: {question}

{context}

Por favor, responde la pregunta basándote SOLO en la información del contexto anterior."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Calcular confianza basada en varios factores
            confidence = self._calculate_confidence(answer, tokens_used)
            
            return {
                "answer": answer,
                "confidence": confidence,
                "tokens_used": tokens_used
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            raise

    def _calculate_confidence(self, answer: str, tokens_used: int) -> float:
        """
        Calcula un score de confianza para la respuesta.
        
        Args:
            answer: Texto de la respuesta
            tokens_used: Tokens utilizados
            
        Returns:
            Score de confianza entre 0 y 1
        """
        confidence = 0.7  # Baseline
        
        # Reducir confianza si dice "no encuentro" o "no está"
        negative_phrases = [
            "no encuentro",
            "no está",
            "no disponible",
            "sin información",
            "no menciona",
            "no aparece"
        ]
        
        answer_lower = answer.lower()
        if any(phrase in answer_lower for phrase in negative_phrases):
            confidence = 0.3
        
        # Aumentar confianza si usa datos específicos
        if any(char.isdigit() for char in answer):
            confidence += 0.15
        
        # Normalizar entre 0 y 1
        confidence = min(max(confidence, 0.0), 1.0)
        
        return confidence

    def summarize_document(self, document_text: str, max_length: int = 500) -> str:
        """
        Genera un resumen del documento.
        
        Args:
            document_text: Texto completo del documento
            max_length: Longitud máxima del resumen
            
        Returns:
            Resumen del documento
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de informes técnicos de pozos petroleros. "
                                 "Resume el documento de forma concisa, destacando los puntos clave."
                    },
                    {
                        "role": "user",
                        "content": f"Resume el siguiente documento técnico en máximo {max_length} caracteres:\n\n{document_text[:3000]}"
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return "Error al generar el resumen"

    def extract_key_points(self, question: str, n_context: int = 5) -> Dict:
        """
        Extrae puntos clave asociados a una pregunta.
        
        Args:
            question: Pregunta del usuario
            n_context: Número de chunks para análisis
            
        Returns:
            Diccionario con puntos clave
        """
        search_results = self.vector_store.search(question, n_results=n_context)
        
        if not search_results:
            return {"puntos_clave": [], "documento": None}
        
        context = "\n".join([chunk for chunk, _, _ in search_results])
        documento = search_results[0][2].get("document_name")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de informes técnicos. "
                                 "Extrae los puntos clave en formato de lista."
                    },
                    {
                        "role": "user",
                        "content": f"Extrae los 5 puntos clave sobre: {question}\n\nContexto:\n{context}"
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            key_points = response.choices[0].message.content
            
            return {
                "puntos_clave": key_points,
                "documento": documento,
                "pregunta": question
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo puntos clave: {str(e)}")
            return {
                "puntos_clave": f"Error: {str(e)}",
                "documento": documento
            }
