"""
ocr — Módulo de leitura óptica de caracteres da barra de escala.

Utiliza EasyOCR para extrair o texto da barra de escala recortada
e regex para separar valor numérico e unidade.
Converte automaticamente qualquer unidade para micrômetros (µm).
"""

from .reader import ScaleOCR

__all__ = ["ScaleOCR"]
