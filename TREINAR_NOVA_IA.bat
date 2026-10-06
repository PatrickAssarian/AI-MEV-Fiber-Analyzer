@echo off
title Treinamento da Inteligencia Artificial (MEV)
echo ========================================================
echo       TREINANDO UMA NOVA VERSAO DA IA
echo ========================================================
echo.
echo O computador vai comecar a estudar as novas fotos do banco de dados agora.
echo Isso pode demorar alguns minutos ou ate horas, dependendo do numero de fotos.
echo.
echo Por favor, nao feche esta janela. Ela se fechara sozinha quando terminar.
echo.

call .venv\Scripts\activate
python train.py

echo.
echo TREINAMENTO CONCLUIDO! O programa ja vai usar a versao mais inteligente.
pause
