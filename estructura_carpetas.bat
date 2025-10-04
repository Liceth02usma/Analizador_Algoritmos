 
@echo off
REM ======================================
REM Script para crear estructura de proyecto
REM Analizador de Complejidades
REM ======================================

mkdir AnalizadorComplejidades
cd AnalizadorComplejidades

REM ================== BACKEND ==================
mkdir backend
cd backend

mkdir app
cd app

echo. > __init__.py
echo. > main.py
echo. > dependencies.py

REM Routers
mkdir routers
cd routers
echo. > __init__.py
echo. > input_algorithm.py
echo. > analysis.py
echo. > classification.py
echo. > recursion.py
echo. > iterative.py
echo. > output_solution.py
cd ..

REM CRUD
mkdir crud
cd crud
echo. > __init__.py
echo. > algorithm.py
echo. > complexity.py
echo. > classification.py
cd ..

REM Schemas
mkdir schemas
cd schemas
echo. > __init__.py
echo. > algorithm.py
echo. > complexity.py
echo. > classification.py
cd ..

REM Models
mkdir models
cd models
echo. > __init__.py
echo. > algorithm.py
echo. > recursive.py
echo. > iterative.py
echo. > complexity.py
echo. > flowdiagram.py
echo. > tree.py
echo. > recurrence_method.py
echo. > algorithm_pattern.py
cd ..

REM Parsers
mkdir parsers
cd parsers
echo. > __init__.py
echo. > parser.py
echo. > pseudocode.lark
cd ..

REM External Services
mkdir external_services
cd external_services
echo. > __init__.py
echo. > llm_service.py
echo. > graphviz_service.py
cd ..

REM Utils
mkdir utils
cd utils
echo. > __init__.py
echo. > validation.py
echo. > helpers.py
echo. > math_tools.py
cd ..

cd ..
REM Tests
mkdir tests
cd tests
echo. > __init__.py
echo. > test_parser.py
echo. > test_analysis.py
echo. > test_classification.py
echo. > test_recursion.py
echo. > test_iterative.py
echo. > test_output.py
cd ..

echo. > requirements.txt
echo. > .gitignore
echo. > README.md

cd ..

REM ================== FRONTEND ==================
mkdir frontend
cd frontend

mkdir public
cd public
echo. > index.html
echo. > favicon.ico
cd ..

mkdir src
cd src

REM API
mkdir api
cd api
echo. > APIUtils.js
echo. > AlgorithmAPI.js
echo. > AnalysisAPI.js
echo. > ClassificationAPI.js
echo. > ParserAPI.js
echo. > LLMAPI.js
cd ..

REM Components
mkdir components
cd components
echo. > InputAlgorithm.js
echo. > InputAlgorithm.css
echo. > OutputSolution.js
echo. > OutputSolution.css
echo. > FlowDiagram.js
echo. > FlowDiagram.css
echo. > RecursionTree.js
echo. > RecursionTree.css
echo. > ComplexityResult.js
echo. > ComplexityResult.css
echo. > ClassificationResult.js
echo. > ClassificationResult.css
cd ..

REM Pages
mkdir pages
cd pages
echo. > HomePage.js
echo. > AnalysisPage.js
echo. > ResultsPage.js
cd ..

REM Utils
mkdir utils
cd utils
echo. > helpers.js
echo. > constants.js
cd ..

echo. > App.js
echo. > index.js
echo. > App.css

cd ..
echo. > package.json
echo. > .gitignore
echo. > README.md

cd ..

echo ======================================
echo ✅ Proyecto creado con éxito.
echo ======================================
pause
