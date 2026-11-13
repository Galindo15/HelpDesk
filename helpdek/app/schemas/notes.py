
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class NoteCreate(BaseModel):
    texto: str = Field(min_length=1, max_length=5000)
    es_interno: bool = False

class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    autor_id: int
    texto: str
    es_interno: bool
    fecha_creacion: datetime
