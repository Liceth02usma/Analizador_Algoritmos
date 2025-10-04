from pydantic import BaseModel

class Algorithm(BaseModel):
    name: str
    pseudocode: str

