from fastapi import FastAPI
from app.routers import analysis  # importamos el módulo

app = FastAPI()

# Incluimos el router
app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "Hola, FastAPI está corriendo 🚀"}


