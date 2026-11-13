
from sqlalchemy import Boolean, ForeignKey, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from datetime import datetime
from app.models.notes import TicketNote
from app.repositories.sqlalchemy import Base

class TicketNoteORM(Base):
    __tablename__ = "ticket_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    es_interno: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fecha_creacion: Mapped[datetime] = mapped_column(nullable=False)

def _to_domain(row: TicketNoteORM) -> TicketNote:
    return TicketNote(id=row.id, ticket_id=row.ticket_id, autor_id=row.autor_id,
                      texto=row.texto, es_interno=row.es_interno, fecha_creacion=row.fecha_creacion)

class SqlAlchemyTicketNoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, note: TicketNote) -> TicketNote:
        row = TicketNoteORM(ticket_id=note.ticket_id, autor_id=note.autor_id,
                            texto=note.texto, es_interno=note.es_interno,
                            fecha_creacion=note.fecha_creacion)
        self.session.add(row)
        self.session.flush()
        return _to_domain(row)

    def for_ticket(self, ticket_id: int, *, include_internal: bool) -> list[TicketNote]:
        stmt = select(TicketNoteORM).where(TicketNoteORM.ticket_id == ticket_id)
        if not include_internal:
            stmt = stmt.where(TicketNoteORM.es_interno.is_(False))
        stmt = stmt.order_by(TicketNoteORM.fecha_creacion, TicketNoteORM.id)
        return [_to_domain(row) for row in self.session.scalars(stmt).all()]
