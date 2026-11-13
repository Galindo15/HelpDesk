
from types import SimpleNamespace
import pytest
from app.domain.errors import PermissionDeniedError, TicketNotFoundError, ValidationError
from app.models.enums import Role
from app.models.notes import TicketNote
from app.services.notes import TicketNoteService

class FakeNoteRepository:
    def __init__(self):
        self.notes = []
    def add(self, note):
        note.id = len(self.notes) + 1
        self.notes.append(note)
        return note
    def for_ticket(self, ticket_id, *, include_internal):
        return [note for note in self.notes if note.ticket_id == ticket_id and
                (include_internal or not note.es_interno)]

class FakeTickets:
    def get_ticket(self, actor, ticket_id):
        if ticket_id != 12 or (not actor.is_staff and actor.id != 1):
            raise TicketNotFoundError(ticket_id)
        return SimpleNamespace(id=ticket_id)

def actor(id, role):
    return SimpleNamespace(id=id, role=role, is_staff=role != Role.REQUESTER)

def test_notes_private_visibility_and_rejection_without_mutation():
    repo = FakeNoteRepository()
    service = TicketNoteService(repo, FakeTickets())
    tech = actor(2, Role.TECHNICIAN)
    requester = actor(1, Role.REQUESTER)
    private = service.create(tech, 12, "  Diagnóstico del switch  ", True)
    service.create(tech, 12, "Avance informado al solicitante", False)
    assert private.texto == "Diagnóstico del switch"
    assert len(service.list_for(tech, 12)) == 2
    visible = service.list_for(requester, 12)
    assert len(visible) == 1
    assert visible[0].es_interno is False
    assert len(repo.notes) == 2  # filtrar no borra la nota privada
    with pytest.raises(PermissionDeniedError):
        service.create(requester, 12, "Nota no permitida", False)
    with pytest.raises(ValidationError):
        service.create(tech, 12, "  ", False)
    with pytest.raises(TicketNotFoundError):
        service.list_for(actor(99, Role.REQUESTER), 12)
    assert len(repo.notes) == 2


def test_notes_api_persist_between_sessions(committed_db):
    from fastapi.testclient import TestClient
    from sqlalchemy import select
    from app.main import create_app
    from app.repositories.notes import TicketNoteORM
    from tests.helpers import TEST_PASSWORD

    with TestClient(create_app()) as client:
        def login(email):
            response = client.post('/api/auth/login', json={'email': email, 'password': TEST_PASSWORD})
            assert response.status_code == 200
            return {'Authorization': f"Bearer {response.json()['access_token']}"}

        requester = login('requester@example.com')
        technician = login('technician@example.com')
        created = client.post('/api/tickets', headers=requester, json={
            'title': 'Switch sin conexión', 'description': 'Revisar switch de aula',
            'category': 'Network', 'priority': 'Low'
        })
        assert created.status_code == 201, created.text
        ticket_id = created.json()['id']
        private = client.post(f'/api/tickets/{ticket_id}/notes', headers=technician,
                              json={'texto': 'Revisión de cableado', 'es_interno': True})
        assert private.status_code == 201, private.text
        public = client.post(f'/api/tickets/{ticket_id}/notes', headers=technician,
                             json={'texto': 'Estamos revisando la red', 'es_interno': False})
        assert public.status_code == 201, public.text
        staff_view = client.get(f'/api/tickets/{ticket_id}/notes', headers=technician)
        requester_view = client.get(f'/api/tickets/{ticket_id}/notes', headers=requester)
        assert len(staff_view.json()) == 2
        assert len(requester_view.json()) == 1
        assert requester_view.json()[0]['es_interno'] is False
        denied = client.post(f'/api/tickets/{ticket_id}/notes', headers=requester,
                             json={'texto': 'No autorizada', 'es_interno': False})
        assert denied.status_code == 403
        blank = client.post(f'/api/tickets/{ticket_id}/notes', headers=technician,
                            json={'texto': '   ', 'es_interno': True})
        assert blank.status_code == 422

       
        with client.app.state.database.session_scope() as session:
            notes = session.scalars(select(TicketNoteORM).where(TicketNoteORM.ticket_id == ticket_id)).all()
            assert len(notes) == 2
            assert sum(note.es_interno for note in notes) == 1
