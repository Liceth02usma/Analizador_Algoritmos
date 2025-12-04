# from typing import Optional, Dict, Any, List, Union
# from datetime import datetime
# from sqlmodel import SQLModel, Field, Column, JSON

# class AnalysisJob(SQLModel, table=True):
#     id: str = Field(primary_key=True)
#     status: str = Field(default="pending")  # pending, processing, completed, failed
#     created_at: datetime = Field(default_factory=datetime.utcnow)
    
#     # Mensaje para mostrar en la UI ("Analizando árboles...", etc.)
#     current_step: str = Field(default="Encolado")
    
#     # Progreso numérico para barra de carga (0-100)
#     progress: int = Field(default=0)

#     # AQUÍ guardamos tu objeto Solution completo como JSON
#     # sa_column=Column(JSON) le dice a SQLite que trate esto como un objeto flexible
#     result: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
#     error_message: Optional[str] = None