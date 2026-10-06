"""
fiber_segmenter — Módulo de segmentação de instâncias de fibras.

Utiliza um modelo YOLOv11-Seg treinado para gerar máscaras binárias
individuais de cada fibra presente na imagem MEV.
Quando o modelo não está disponível, opera em modo mock para testes.
"""

from .segmenter import FiberSegmenter

__all__ = ["FiberSegmenter"]
