@echo off
title Instalacao do Sistema de Fibras
echo ========================================================
echo       CONFIGURANDO O SISTEMA NESTE NOVO COMPUTADOR
echo ========================================================
echo.
echo Isso so precisa ser feito uma vez!
echo.
echo Passo 1: Apagando configuracoes antigas (se existirem)...
if exist ".venv" rmdir /s /q ".venv"

echo Passo 2: Criando um novo ambiente virtual para este PC...
python -m venv .venv
if %errorlevel% neq 0 (
    echo.
    echo [ERRO FATAL] O Python nao esta instalado neste computador!
    echo Por favor, baixe e instale o Python (https://www.python.org/downloads/)
    echo Durante a instalacao do Python, certifique-se de marcar a caixa "Add Python to PATH".
    pause
    exit /b
)

echo Passo 3: Ativando o ambiente e instalando as bibliotecas...
call .venv\Scripts\activate
pip install -r requirements.txt

echo.
echo ========================================================
echo TUDO PRONTO! INICIANDO O PROGRAMA...
echo ========================================================
streamlit run interface/app.py

pause
