"""
classifier — Módulo de classificação e filtragem de objetos detectados.

Elimina automaticamente objetos inválidos (ruído, aglomerados, impurezas)
antes da etapa de medição, baseando-se em critérios geométricos.
Futuramente poderá ser estendido com classificadores ML (Random Forest, SVM, MLP).
"""

from .filter import ObjectClassifier

__all__ = ["ObjectClassifier"]
