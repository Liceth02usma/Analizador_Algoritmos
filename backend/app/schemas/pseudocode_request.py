from pydantic import BaseModel


class PseudocodeRequest(BaseModel):
    pseudocode: str
