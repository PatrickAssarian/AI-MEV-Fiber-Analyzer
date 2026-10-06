@echo off
title Sistema de Analise de Fibras em MEV
echo ========================================================
echo       INICIANDO O SISTEMA DE ANALISE DE FIBRAS
echo ========================================================
echo.
echo Abrindo o aplicativo no seu navegador...
echo Por favor, nao feche esta janela preta enquanto estiver usando o sistema.
echo.

call .venv\Scripts\activate
streamlit run interface/app.py

pause
