"""
Módulo para procesar y dividir texto en chunks.
Incluye extracción de datos clave del pozo.
"""

import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """Procesador de texto para documentos técnicos de pozos."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        """
        Inicializa el procesador de texto.
        
        Args:
            chunk_size: Tamaño máximo de cada chunk en caracteres
            chunk_overlap: Caracteres de solapamiento entre chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Divide el texto en chunks con solapamiento.
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks de texto
        """
        if not text or len(text) == 0:
            return []

        # Limpiar el texto
        text = self._clean_text(text)
        
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Determinar el final del chunk
            end = start + self.chunk_size
            
            # Si no es el último chunk, buscar el último punto o salto de línea
            if end < text_length:
                # Buscar un punto o salto de línea para romper propiciamente
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                
                cutoff = max(last_period, last_newline)
                if cutoff > start + self.chunk_size * 0.5:
                    end = cutoff + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Mover el inicio del próximo chunk con solapamiento
            start = end - self.chunk_overlap

        logger.info(f"Texto dividido en {len(chunks)} chunks")
        return chunks

    def _clean_text(self, text: str) -> str:
        """Limpia y normaliza el texto."""
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Remover caracteres especiales problemáticos
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text)
        
        return text.strip()

    def extract_well_data(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrae datos clave del pozo del texto.
        
        Args:
            text: Texto del documento
            
        Returns:
            Diccionario con datos del pozo identificados
        """
        well_data = {
            'depth': None,
            'pressure': None,
            'formation': None,
            'producers': None,
            'status': None,
            'location': None,
        }

        # Buscar profundidad (en metros o pies)
        depth_patterns = [
            r'profundidad\s+(?:total\s+)?[:\s]*(\d+(?:\.\d+)?)\s*(?:m|metros|ft|pies)',
            r'profundidad\s+[:\s]*(\d+(?:\.\d+)?)\s*(?:m|metros)',
            r'total\s+depth\s*[:\s]*(\d+(?:\.\d+)?)',
        ]
        for pattern in depth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                well_data['depth'] = match.group(1)
                break

        # Buscar presión
        pressure_patterns = [
            r'presión\s+(?:inicial\s+)?[:\s]*(\d+(?:\.\d+)?)\s*(?:psi|bar|kpa)',
            r'pressure\s*[:\s]*(\d+(?:\.\d+)?)',
        ]
        for pattern in pressure_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                well_data['pressure'] = match.group(1)
                break

        # Buscar formación geológica
        formation_patterns = [
            r'formación\s*[:\s]*([A-Za-z\s]+?)(?:\n|,)',
            r'geological\s+(?:unit|formation)\s*[:\s]*([A-Za-z\s]+?)(?:\n|,)',
        ]
        for pattern in formation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                well_data['formation'] = match.group(1).strip()
                break

        # Buscar intervalos productores
        producer_patterns = [
            r'intervalos?\s+productores?\s*[:\s]*([0-9\s\-]+)',
            r'producing\s+interval\s*[:\s]*([0-9\s\-]+)',
        ]
        for pattern in producer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                well_data['producers'] = match.group(1).strip()
                break

        # Buscar estado del pozo
        status_patterns = [
            r'estado\s*[:\s]*([A-Za-z]+)',
            r'status\s*[:\s]*([A-Za-z]+)',
        ]
        for pattern in status_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                well_data['status'] = match.group(1).strip()
                break

        logger.info(f"Datos del pozo extraídos: {well_data}")
        return well_data

    def extract_summary_section(self, text: str, max_chars: int = 2000) -> str:
        """
        Intenta extraer un resumen ejecutivo del documento.
        
        Args:
            text: Texto completo
            max_chars: Máximo de caracteres para el resumen
            
        Returns:
            Sección de resumen si existe, sino los primeros párrafos
        """
        summary_keywords = [
            'resumen ejecutivo',
            'executive summary',
            'abstract',
            'objetivos',
            'objectives',
            'introducción',
            'introduction',
        ]

        text_lower = text.lower()
        
        for keyword in summary_keywords:
            idx = text_lower.find(keyword)
            if idx != -1:
                # Extraer desde el keyword hasta encontrar la siguiente sección
                section_text = text[idx:]
                # Buscar el siguiente title/sección
                next_section = re.search(r'\n\n[A-Z][A-Z\s]{5,}:', section_text)
                if next_section:
                    return section_text[:next_section.start()][:max_chars]
                return section_text[:max_chars]

        # Si no encuentra resumen, retornar primeros párrafos
        paragraphs = text.split('\n\n')
        summary = '\n\n'.join(paragraphs[:5])
        return summary[:max_chars]

    def get_statistics(self, text: str) -> Dict[str, int]:
        """Obtiene estadísticas del texto."""
        words = text.split()
        
        return {
            'total_characters': len(text),
            'total_words': len(words),
            'total_paragraphs': len(text.split('\n\n')),
            'average_word_length': sum(len(w) for w in words) / len(words) if words else 0,
        }
