@echo off
REM ===========================
REM Script para crear estructura de AnalizadorComplejidades
REM ===========================

mkdir AnalizadorComplejidades
cd AnalizadorComplejidades

REM ----- FRONTEND -----
mkdir frontend
cd frontend
mkdir src
mkdir src\components
mkdir src\components\InputAlgorithm
mkdir src\components\OutputSolution
echo {} > package.json
cd ..

REM ----- BACKEND -----
mkdir backend
cd backend
mkdir app
cd app

REM Controladores
mkdir controllers
cd controllers
echo. > control_input.py
echo. > control_analysis.py
echo. > control_recursive.py
echo. > control_iterative.py
echo. > control_solution.py
echo. > control_classification.py
cd ..

REM Modelos
mkdir models
cd models
echo. > algorithm.py
echo. > recursive.py
echo. > iterative.py
echo. > flowdiagram.py
echo. > tree.py
echo. > recurrence_method.py
echo. > complexity.py
echo. > algorithm_pattern.py
cd ..

REM Parser
mkdir parsers
cd parsers
echo. > parser.py
echo. > pseudocode.lark
cd ..

REM Servicios (ej: integración LLM)
mkdir services
cd services
echo. > llm_service.py
cd ..

echo. > __init__.py
echo. > main.py

cd ..
echo. > requirements.txt
echo. > README.md

cd ..
echo. > README.md

echo Estructura creada con exito.
pause
