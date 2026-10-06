"""
utils — Utilitários de exportação e geração de relatórios.

Fornece:
    - DataExporter: salva resultados em CSV, Excel, JSON e imagens.
    - PDFReport:    gera relatórios PDF com tabela de resumo e gráficos.
"""

from .exporter import DataExporter, PDFReport

__all__ = ["DataExporter", "PDFReport"]
