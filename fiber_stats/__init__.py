"""
fiber_stats — Módulo de estatísticas e visualização gráfica.

Calcula estatísticas descritivas completas (média, mediana, moda, desvio
padrão, CV%) para os dados das fibras medidas, e gera histogramas,
boxplots e violin plots com ajuste de distribuição normal.
"""

from .calculator import StatsCalculator
from .plots import PlotGenerator

__all__ = ["StatsCalculator", "PlotGenerator"]
