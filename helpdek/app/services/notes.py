"""Reglas de visibilidad de notas (nunca confiar en filtros del navegador)."""
from app.domain.errors import PermissionDeniedError, ValidationError
from app.models.enums import Role
from app.models.notes import TicketNote

class TicketNoteService:
    def __init__(self, repository, tickets):
        self.repository = repository
        self.tickets = tickets

    def create(self, actor, ticket_id: int, texto: str, es_interno: bool = False) -> TicketNote:
        # Verifica acceso/existencia con las mismas reglas del resto de HelpDesk.
        self.tickets.get_ticket(actor, ticket_id)
        if Role(actor.role) != Role.TECHNICIAN:
            raise PermissionDeniedError("only technicians may create notes")
        cleaned = texto.strip()
        if not cleaned:
            raise ValidationError("note text is required", field="texto")
        return self.repository.add(TicketNote(ticket_id=ticket_id, autor_id=actor.id,
                                              texto=cleaned, es_interno=es_interno))

    def list_for(self, actor, ticket_id: int) -> list[TicketNote]:
        self.tickets.get_ticket(actor, ticket_id)
        # No entregar notas privadas al solicitante ni a usuarios sin acceso.
        return self.repository.for_ticket(ticket_id, include_internal=actor.is_staff)
