
from dataclasses import dataclass, field
from datetime import datetime
from app.domain.clock import now

@dataclass
class TicketNote:
    ticket_id: int
    autor_id: int
    texto: str
    es_interno: bool = False
    fecha_creacion: datetime = field(default_factory=now)
    id: int | None = field(default=None, kw_only=True)
