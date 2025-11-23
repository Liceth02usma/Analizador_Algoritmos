from fastapi import APIRouter

# Aquí definimos el router
router = APIRouter(
    prefix="/analysis",
    tags=["analysis"]
)

@router.get("/")
def get_analysis():
    return {"message": "Endpoint de análisis funcionando ✅"}

