# Tasks: Aidemy Chatbot Implementation

## Relevant Files

### Backend (n8n Workflows)
- `n8n/workflows/chat-handler.json` - Main workflow handling incoming chat messages and orchestrating responses
- `n8n/workflows/rag-processor.json` - Workflow for processing documents and performing similarity search
- `n8n/workflows/lead-qualifier.json` - Workflow for evaluating conversation and assigning BANEC score
- `n8n/workflows/calendar-booking.json` - Workflow for Google Calendar integration and appointment scheduling
- `n8n/workflows/email-sender.json` - Workflow for sending documentation and notifications
- `n8n/workflows/analytics-tracker.json` - Workflow for tracking usage metrics
- `n8n/workflows/knowledge-sync.json` - Cron job workflow for syncing Google Drive documents

### Frontend (Chat Widget)
- `frontend/widget/chat-widget.js` - Main JavaScript file for the embeddable chat widget
- `frontend/widget/chat-widget.css` - Styling for the chat widget
- `frontend/widget/chat-widget.html` - HTML template for widget UI
- `frontend/widget/config.js` - Configuration file for n8n webhook URLs and settings

### RAG System
- `rag/embeddings-generator.py` - Script for generating embeddings from documents
- `rag/document-processor.py` - Script for chunking and preprocessing documents
- `rag/qdrant-setup.sh` - Setup script for Qdrant vector database
- `rag/requirements.txt` - Python dependencies for RAG system
- `docker/qdrant/docker-compose.yml` - Docker compose configuration for Qdrant

### Database & Storage
- `database/schema.sql` - PostgreSQL schema for conversations and leads
- `database/migrations/` - Directory for database migrations

### Configuration
- `.env.example` - Example environment variables file
- `config/prompts.yaml` - System prompts and LLM configuration
- `config/calendar-settings.yaml` - Calendar booking configuration

### Documentation
- `docs/PRD.md` - Product Requirements Document
- `docs/API.md` - API documentation for n8n webhooks
- `docs/DEPLOYMENT.md` - Deployment guide
- `README.md` - Project overview and quick start guide

### Testing
- `tests/widget/chat-widget.test.js` - Unit tests for chat widget
- `tests/n8n/workflow-tests.json` - Test cases for n8n workflows
- `tests/integration/end-to-end.test.js` - End-to-end integration tests

---

## Tasks

### [ ] 1.0 Setup Infrastruttura e Ambiente

#### [ ] 1.1 Configurazione VPS e Docker
- Verificare risorse VPS disponibili (RAM, storage, CPU)
- Installare Docker e Docker Compose se non già presente
- Configurare rete Docker per comunicazione tra container
- Setup basic security (firewall rules, fail2ban)

#### [ ] 1.2 Setup Qdrant Vector Database
- Creare `docker/qdrant/docker-compose.yml` per Qdrant
- Avviare container Qdrant su porta dedicata
- Configurare persistent volume per dati vettoriali
- Testare connessione e API Qdrant
- Creare collection per embeddings con configurazione appropriata (dimensione vettori, distance metric)

#### [ ] 1.3 Setup PostgreSQL Database
- Installare PostgreSQL o usare container Docker
- Creare database `aidemy_chatbot`
- Creare schema con tabelle: `conversations`, `messages`, `leads`, `metrics`
- Definire `database/schema.sql` con struttura completa
- Setup backup automatico giornaliero

#### [ ] 1.4 Configurazione Ambiente e Secrets
- Creare `.env.example` con tutte le variabili necessarie
- Configurare secrets su VPS (OpenRouter API key, Google credentials)
- Setup variabili ambiente per n8n (se non già fatto)
- Documentare tutte le chiavi API necessarie

#### [ ] 1.5 Setup Repository GitHub
- Creare struttura directory progetto
- Configurare `.gitignore` per secrets e file temporanei
- Setup GitHub Actions (opzionale) per CI/CD
- Creare branch `development` e `production`

---

### [ ] 2.0 Implementazione RAG e Knowledge Base

#### [ ] 2.1 Estrazione Documenti da Google Drive
- Configurare accesso Google Drive API con service account
- Creare script Python per listing files da cartella Drive specifica
- Implementare download automatico documenti (PDF, DOCX, MD)
- Salvare documenti in directory locale `/data/raw-docs`

#### [ ] 2.2 Document Processing e Chunking
- Sviluppare `rag/document-processor.py` per:
  - Estrazione testo da PDF (usando PyPDF2 o pdfplumber)
  - Estrazione testo da DOCX (usando python-docx)
  - Parsing Markdown files
- Implementare chunking semantico (500 token/chunk, overlap 50 token)
- Estrarre metadata da documenti (tipo, data, categoria, fonte)
- Salvare chunks processati in formato JSON

#### [ ] 2.3 Generazione Embeddings
- Sviluppare `rag/embeddings-generator.py`
- Integrare OpenAI API per text-embedding-3-small
- Generare embeddings per ogni chunk
- Gestire rate limiting e retry logic

#### [ ] 2.4 Storage Embeddings in Qdrant
- Creare script per upload embeddings + metadata in Qdrant
- Implementare indexing efficiente
- Testare similarity search con query di esempio
- Verificare performance retrieval (latency <500ms)

#### [ ] 2.5 Workflow n8n Knowledge Sync
- Creare `n8n/workflows/knowledge-sync.json`
- Configurare cron trigger (ogni domenica notte)
- Orchestrare: download Drive → process → embed → store
- Implementare notifica email a Jack su successo/errore
- Logging dettagliato del processo

---

### [ ] 3.0 Sviluppo Workflow n8n Core

#### [ ] 3.1 Chat Handler Workflow - Setup Base
- Creare `n8n/workflows/chat-handler.json`
- Configurare webhook endpoint (POST `/chat`)
- Definire schema input: `{user_id, message, session_id}`
- Implementare validazione input
- Setup risposta immediata con status "processing"

#### [ ] 3.2 Chat Handler - Gestione Conversazione
- Implementare recupero conversazione esistente da DB (basato su `session_id`)
- Append nuovo messaggio user a history
- Limitare history a ultimi 10 messaggi per context window management
- Implementare state management (nuova conversazione vs. ongoing)

#### [ ] 3.3 Chat Handler - RAG Integration
- Chiamare Qdrant per similarity search con query utente
- Recuperare top 3-5 chunks più rilevanti
- Formattare chunks come context per LLM prompt
- Implementare fallback se no results (<threshold similarity)

#### [ ] 3.4 Chat Handler - LLM Call
- Creare file `config/prompts.yaml` con system prompt master
- Implementare chiamata OpenRouter API (GPT-4o)
- Costruire prompt con: system + context RAG + chat history + user message
- Gestire parametri: temperature 0.7, max_tokens 500
- Implementare retry logic e error handling

#### [ ] 3.5 Chat Handler - Response Processing
- Estrarre risposta LLM
- Identificare intent nella risposta (info, booking, email_docs, etc.)
- Salvare messaggio assistant in DB
- Triggerare sub-workflows se necessario (booking, email)
- Ritornare risposta a frontend via webhook response

#### [ ] 3.6 RAG Processor Workflow
- Creare `n8n/workflows/rag-processor.json` come sub-workflow
- Input: query string
- Eseguire similarity search Qdrant
- Formattare results con citazioni
- Output: formatted context per LLM

---

### [ ] 4.0 Implementazione Widget Chat Frontend

#### [ ] 4.1 HTML Structure del Widget
- Creare `frontend/widget/chat-widget.html`
- Struttura: container minimizzato + container espanso
- Container espanso: header, message list, input area, footer
- Accessibilità: ARIA labels, keyboard navigation
- Placeholder per avatar Aidemy

#### [ ] 4.2 CSS Styling
- Creare `frontend/widget/chat-widget.css`
- Styling per stati: minimizzato, espanso, loading
- Responsive design (mobile-first)
- Animazioni smooth per apertura/chiusura
- Typing indicator animation
- Badge notifica (se chat non ancora aperta)
- Colori brand Aidemy (da integrare con design esistente)

#### [ ] 4.3 JavaScript Core Logic
- Sviluppare `frontend/widget/chat-widget.js`
- Gestione apertura/chiusura widget
- Gestione session_id (generazione UUID e storage localStorage)
- Event listeners per input utente (submit, enter key)
- Invio messaggi a n8n webhook via fetch()
- Gestione risposte e append a message list
- Scroll automatico a ultimo messaggio

#### [ ] 4.4 Suggerimenti Iniziali (Quick Replies)
- Implementare rendering suggerimenti al primo carico:
  - "Come funzionano i vostri servizi?"
  - "Voglio prenotare una call"
  - "Avete case study?"
- Click su suggerimento popola input e invia automaticamente

#### [ ] 4.5 Typing Indicator
- Mostrare "typing..." quando in attesa risposta LLM
- Implementare debouncing per evitare flickering
- Timeout safety (se no response dopo 30s, mostra errore)

#### [ ] 4.6 Configuration File
- Creare `frontend/widget/config.js`
- Parametri configurabili:
  - `n8nWebhookUrl`: URL endpoint n8n
  - `brandColor`: colore primario
  - `position`: 'bottom-right' | 'bottom-left'
  - `initialMessage`: messaggio benvenuto bot
- Permettere override configurazione via script tag attributes

#### [ ] 4.7 Embed Script
- Creare snippet embed per Landingi:
```html
<script src="https://[VPS_URL]/chat-widget.js"></script>
<script>
  AidemyChat.init({
    webhookUrl: 'https://[VPS_URL]/webhook/chat',
    brandColor: '#[COLOR]'
  });
</script>
```
- Testare inject su pagina Landingi di test

---

### [ ] 5.0 Integrazione Servizi Esterni (Calendar, Email)

#### [ ] 5.1 Google Calendar Integration - Setup
- Abilitare Google Calendar API nel progetto GCP
- Creare OAuth2 credentials o service account
- Configurare scopes necessari (calendar.events)
- Testare autenticazione da n8n

#### [ ] 5.2 Calendar Booking Workflow
- Creare `n8n/workflows/calendar-booking.json`
- Input trigger da chat-handler (quando user richiede booking)
- Query disponibilità calendario Jack (filtro per orari lavorativi)
- Proporre 3 slot disponibili nei prossimi 7 giorni
- Creare evento Calendar con:
  - Titolo: "Esplorazione Strategica - [Nome Lead]"
  - Durata: 30 min
  - Link videoconferenza (Google Meet auto)
  - Descrizione con info lead

#### [ ] 5.3 Calendar Booking - Conferma e Notifiche
- Inviare email conferma a lead con:
  - Dettagli appuntamento
  - Link calendario (.ics attachment)
  - Link meet
  - Breve questionario preparatorio (link Google Form)
- Inviare notifica email a Jack con sintesi lead
- Aggiornare lead in DB con flag `call_booked: true`

#### [ ] 5.4 Configurazione Email Sender
- Setup SMTP o integrazione SendGrid in n8n
- Creare template email (HTML responsive)
- Configurare sender: `noreply@aidemy.it` o email Jack

#### [ ] 5.5 Email Documentation Workflow
- Creare `n8n/workflows/email-sender.json`
- Input: lead email + lista documenti richiesti
- Recuperare PDF da storage (Google Drive o locale)
- Comporre email con:
  - Messaggio personalizzato
  - Attachments o link download
  - CTA: "Prenota una call"
- Tracciare invio in DB (`docs_sent: true`, `docs_sent_at: timestamp`)

#### [ ] 5.6 Fallback / Escalation Workflow
- Implementare logica in chat-handler per riconoscere "domanda senza risposta"
- Se confidence LLM < threshold o user esprime frustrazione
- Triggerare escalation:
  - Messaggio bot: "Non ho trovato info specifiche. Vuoi che Jack ti contatti?"
  - Se sì → salva lead con flag `escalated: true`
  - Invio email alert a Jack con transcript conversazione

---

### [ ] 6.0 Sistema di Qualificazione Lead

#### [ ] 6.1 Lead Qualifier Workflow - Setup
- Creare `n8n/workflows/lead-qualifier.json`
- Trigger: chiamata da chat-handler a fine conversazione o su richiesta

#### [ ] 6.2 Estrazione Informazioni da Conversazione
- Implementare parsing LLM-based per estrarre:
  - Nome, email, azienda, ruolo
  - Dimensione azienda (se menzionata)
  - Sfida/bisogno principale
  - Timeline (urgenza)
  - Budget hints (da domande su costi)
- Usare structured output GPT-4o se possibile
- Fallback: regex patterns per email/nome

#### [ ] 6.3 Scoring BANEC
- Implementare logica scoring per ogni criterio:
  - **Budget (1-5)**: inferito da dimensione azienda + domande costi
  - **Autorità (1-5)**: da ruolo dichiarato (CEO/fondatore=5, altro=3)
  - **Necessità (1-5)**: da chiarezza sfida descritta
  - **Emergenza (1-5)**: da timeline menzionata (subito=5, esplorazione=2)
  - **Compatibilità (1-5)**: da qualità conversazione (num messaggi, tono)
- Somma totale: 5-11=freddo, 12-17=tiepido, 18-25=caldo

#### [ ] 6.4 Storage Lead in Database
- Salvare in tabella `leads`:
  - Tutti campi estratti
  - Score BANEC (totale + breakdown per criterio)
  - Timestamp
  - Session ID per link a conversazione
  - Status: 'new' | 'contacted' | 'converted' | 'lost'

#### [ ] 6.5 Notifica Lead Caldi
- Se score BANEC >= 18 (caldo)
- Inviare email alert immediata a Jack:
  - Riepilogo lead
  - Link a conversazione completa
  - Suggerimento azione rapida

---

### [ ] 7.0 Testing, Monitoring e Deploy

#### [ ] 7.1 Unit Testing Frontend Widget
- Setup Jest per testing JavaScript
- Test `chat-widget.test.js`:
  - Apertura/chiusura widget
  - Invio messaggio
  - Gestione sessione
  - Rendering messaggi
- Coverage target: >80%

#### [ ] 7.2 Integration Testing n8n Workflows
- Creare file `tests/n8n/workflow-tests.json`
- Test scenari:
  - User fa domanda → riceve risposta con RAG
  - User richiede booking → riceve slot disponibili
  - User chiede docs → riceve email
  - Conversazione senza info → escalation
- Usare n8n API per trigger test workflows

#### [ ] 7.3 End-to-End Testing
- Setup Playwright o Cypress
- Test `tests/integration/end-to-end.test.js`:
  - Carica pagina Landingi → apre chat → conversa → prenota call
  - Verifica email ricevute
  - Verifica evento creato in Calendar
  - Verifica lead salvato in DB

#### [ ] 7.4 Monitoring e Logging Setup
- Creare workflow `n8n/workflows/analytics-tracker.json`
- Tracciare metriche:
  - Conversazioni avviate
  - Messaggi per conversazione (avg)
  - Lead qualificati per score
  - Call prenotate
  - Docs inviati
  - Latency LLM calls
- Salvare metriche in tabella `metrics` con timestamp
- Dashboard Grafana (opzionale) o script Python per report settimanale

#### [ ] 7.5 Error Handling e Alerting
- Implementare error catching in tutti workflow n8n
- Setup Sentry o log aggregator per errori
- Configurare email alerts per:
  - n8n workflow failures
  - Database connection errors
  - OpenRouter API errors (rate limit, downtime)
  - Qdrant connection issues

#### [ ] 7.6 Performance Optimization
- Implementare caching per chunks RAG frequenti (Redis opzionale)
- Ottimizzare query DB con indici appropriati
- Compressione response HTTP per widget
- Lazy loading script widget per non impattare page load

#### [ ] 7.7 Documentation Completa
- Scrivere `docs/API.md`: documentare tutti webhook n8n
- Scrivere `docs/DEPLOYMENT.md`: guida step-by-step deploy VPS
- Aggiornare `README.md` con:
  - Quick start
  - Architettura sistema
  - Come testare localmente
  - FAQ troubleshooting

#### [ ] 7.8 Security Audit
- Implementare rate limiting su webhook n8n (prevent abuse)
- Sanitize input utente (prevent injection attacks)
- HTTPS enforcement su tutti endpoint
- Rotazione secrets periodica
- Review GDPR compliance (storage conversazioni, data retention)

#### [ ] 7.9 Deploy su Landingi Production
- Test su staging Landingi
- Deploy script widget su produzione
- Verificare analytics tracking funzionante
- A/B test posizione widget (se applicabile)
- Monitoring primi 48h intensivo

#### [ ] 7.10 Post-Launch Review
- Dopo 1 settimana: review metriche vs. target
- Identificare top 5 domande frequenti non coperte da KB
- Analizzare conversazioni con escalation → improve KB
- Raccogliere feedback qualitativo da primi lead
- Iterazione su system prompt se necessario
- Planning fase 2 features (supporto clienti esistenti)

---

## Notes

### Timeline Stimata
- **Fase 1 (Setup)**: 2-3 giorni
- **Fase 2 (RAG)**: 3-4 giorni
- **Fase 3 (n8n Core)**: 3-4 giorni
- **Fase 4 (Frontend)**: 2-3 giorni
- **Fase 5 (Integrazioni)**: 2 giorni
- **Fase 6 (Qualificazione)**: 1-2 giorni
- **Fase 7 (Testing & Deploy)**: 2-3 giorni

**Totale stimato: 15-21 giorni** (3-4 settimane con buffer)

Per target 2 settimane (MVP essenziale), prioritizzare:
- Tasks 1.1-1.4, 2.1-2.4, 3.1-3.5, 4.1-4.3, 5.1-5.3, 6.1-6.4, 7.9

### Dipendenze Critiche
- Setup Qdrant (1.2) prima di RAG implementation (2.0)
- Knowledge base processata (2.0) prima di test n8n workflows (3.0)
- Frontend widget (4.0) può procedere in parallelo a backend
- Calendar integration (5.1-5.3) può essere sviluppata indipendentemente

### Risorse Necessarie
- VPS: minimo 4GB RAM, 2 CPU, 50GB storage
- OpenRouter credits: stimati $20-50/mese per testing + primi mesi
- Google Workspace (per Calendar API)
- Dominio o subdomain per hosting widget

### Success Criteria per MVP
- [ ] Widget funzionante su Landingi
- [ ] Conversazioni salvate in DB
- [ ] RAG risponde correttamente a 80%+ domande test
- [ ] Booking call funzionante con conferma email
- [ ] Lead qualificati salvati con score BANEC
- [ ] Latency <3s per risposta
- [ ] Zero errori critici in 24h test

---

**Next Action**: Iniziare con Task 1.1 - Configurazione VPS e Docker! 🚀

**Workflow Suggerito**:
1. Completare Phase 1 (Setup) interamente prima di procedere
2. Phase 2 (RAG) può iniziare non appena Qdrant è up (dopo 1.2)
3. Phase 3 (n8n) richiede almeno documentazione base processata (2.2)
4. Phase 4 (Frontend) può essere sviluppato in parallelo da task 1.5 in poi
5. Testing continuo durante sviluppo, non solo alla fine

**Important Reminders**:
- Commit frequentemente su GitHub con messaggi descrittivi
- Testare ogni workflow n8n individualmente prima di integrazione
- Documentare decisioni tecniche significative in `docs/DECISIONS.md`
- Backup database prima di migration o cambiamenti schema
- Non committare secrets (.env, credentials) - usare .gitignore
