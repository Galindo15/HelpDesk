CREATE TABLE IF NOT EXISTS ticket_notes (
  id SERIAL PRIMARY KEY,
  ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  autor_id INTEGER NOT NULL REFERENCES users(id),
  texto TEXT NOT NULL CHECK (length(btrim(texto)) > 0),
  es_interno BOOLEAN NOT NULL DEFAULT FALSE,
  fecha_creacion TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ticket_notes_ticket ON ticket_notes(ticket_id);