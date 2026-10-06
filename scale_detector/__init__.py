"""
scale_detector — Módulo de detecção automática da barra de escala.

Utiliza um modelo YOLOv11 treinado para localizar a barra de escala
na imagem MEV e retornar seu bounding box e recorte.
Quando o modelo não está disponível, opera em modo mock para testes.
"""

from .detector import ScaleBarDetector

__all__ = ["ScaleBarDetector"]
