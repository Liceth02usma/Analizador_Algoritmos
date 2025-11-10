from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import input_algorithm
from app.routers import analysis
from app.routers import recursive
from app.routers import iterative  # importamos el módulo

app = FastAPI(title="Analizador de Complejidades")

# CORS para permitir llamadas desde el frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router
app.include_router(input_algorithm.router)
app.include_router(iterative.router)
app.include_router(recursive.router)
app.include_router(input_algorithm.router)

@app.get("/")
def root():
    return {"message": "API del Analizador de Complejidades lista 🚀"}
