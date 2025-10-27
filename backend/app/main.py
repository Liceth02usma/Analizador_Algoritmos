from fastapi import FastAPI
from app.routers import analysis
from app.routers import recursive
from app.routers import iterative  # importamos el módulo

app = FastAPI()

# Incluimos el router
app.include_router(analysis.router)
app.include_router(iterative.router)
app.include_router(recursive.router)

@app.get("/")
def read_root():
    return {"message": "Hola, FastAPI está corriendo 🚀"}


