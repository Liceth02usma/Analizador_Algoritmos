from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    algorithm_name: str = Field(..., example="BúsquedaSecuencial")
    pseudocode: str = Field(
        ...,
        example="for i 🡨 0 to n do\nbegin\n    for j 🡨 0 to n do\n    begin\n        matriz 🡨 0\n    end\nend"
    )