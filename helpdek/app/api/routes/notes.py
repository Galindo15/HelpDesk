
from fastapi import APIRouter, status
from app.api.dependencies import CurrentUser, DbSession, FacadeDep
from app.repositories.notes import SqlAlchemyTicketNoteRepository
from app.schemas.notes import NoteCreate, NoteResponse
from app.services.notes import TicketNoteService

router = APIRouter(prefix="/tickets", tags=["ticket-notes"])

def _service(db: DbSession, facade: FacadeDep) -> TicketNoteService:
    return TicketNoteService(SqlAlchemyTicketNoteRepository(db), facade)

@router.post("/{ticket_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(ticket_id: int, body: NoteCreate, db: DbSession, facade: FacadeDep, actor: CurrentUser):
    return _service(db, facade).create(actor, ticket_id, body.texto, body.es_interno)

@router.get("/{ticket_id}/notes", response_model=list[NoteResponse])
def list_notes(ticket_id: int, db: DbSession, facade: FacadeDep, actor: CurrentUser):
    return _service(db, facade).list_for(actor, ticket_id)
