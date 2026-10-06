"""
measurements — Módulo de medição geométrica de fibras.

Implementa o pipeline completo de medição sem uso de IA:
    Máscara binária → Distance Transform → Esqueletização →
    Diâmetros locais → Estatísticas por fibra

Também inclui a geração do mapa de espessura colorido.
"""

from .analyzer import FiberAnalyzer
from .thickness_map import ThicknessMapGenerator

__all__ = ["FiberAnalyzer", "ThicknessMapGenerator"]
