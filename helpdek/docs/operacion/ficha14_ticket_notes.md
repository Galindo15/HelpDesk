# Ficha 14: notas de seguimiento (TicketNote)

## Archivos

- `app/models/notes.py`: entidad de dominio.
- `app/repositories/notes.py`: modelo SQLAlchemy y consultas.
- `app/services/notes.py`: reglas de permisos y visibilidad.
- `app/schemas/notes.py`: validación de entrada y salida.
- `app/api/routes/notes.py`, `app/main.py`: rutas REST registradas bajo `/api`.
- `app/web/static/js/api.js`, `app/web/static/js/pages/ticket.js`: formulario e historial.
- `docs/database/database.sql`: tabla incluida en instalaciones NUEVAS.
- `tests/test_ficha14_notes.py`: pruebas de negocio e integración.

## Seguridad de la base

El esquema `docs/database/database.sql` actualizado SOLO se ejecuta automáticamente al
crear una base vacía; Docker NO lo ejecuta contra un volumen ya existente.
**No ejecutes `database.sql` completo ni `docker compose down -v` contra tus datos habituales.**

Si la base de prácticas habitual ya existe y deseas posteriormente usar el módulo allí,
respáldala primero y aplica únicamente `docs/database/migrations/001_ticket_notes.sql`
en esa base, tras comprobar el destino. Para evaluar el examen utiliza `helpdesk_test`
con `TEST_DATABASE_URL` apuntando exclusivamente a una base de pruebas.

## Pruebas

- `uv sync --group dev` (instala las dependencias, si tienes acceso a ellas).
- `uv run pytest -m "not integration" -q`
- Con PostgreSQL de PRUEBAS disponible y `TEST_DATABASE_URL` verificado:
  `uv run pytest tests/test_ficha14_notes.py -q`
- `uv run pytest -m integration -q` también ejecuta las pruebas antiguas y **recrea helpdesk_test**.

## Uso local

1. Abre `helpdek` en VS Code; confirma `DATABASE_URL`, `TEST_DATABASE_URL` y `SECRET_KEY` en tu `.env` local.
2. Para iniciar la aplicación local, instala las dependencias y ejecuta `uv run uvicorn app.main:app --reload --env-file .env`.
3. Entra a `/app` con cuenta técnica, abre el detalle del ticket y busca **Notas de seguimiento**.
4. Crea una nota con **Nota interna** marcada y otra nota pública.
5. Ingresa con la cuenta solicitante del ticket: debe verse solo la pública, incluso después de recargar.
6. Captura evidencia de interfaz, API y resultados de pytest. Anota tu rama con `git branch --show-current`.


