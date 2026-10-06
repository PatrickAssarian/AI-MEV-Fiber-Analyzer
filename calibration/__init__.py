"""
calibration — Módulo de calibração de imagens MEV.

Converte medidas em pixels para micrômetros utilizando a barra
de escala detectada e o valor lido pelo OCR.
"""

from .calibrator import ImageCalibrator

__all__ = ["ImageCalibrator"]
