# n8n Workflows for Aidemy Chatbot

This directory contains the n8n workflow JSON files for the Aidemy chatbot system.

## Workflows Overview

1. **chat-handler.json** - Main webhook handler for chat messages
2. **rag-processor.json** - Document processing and similarity search
3. **lead-qualifier.json** - BANEC scoring and lead evaluation
4. **calendar-booking.json** - Google Calendar integration
5. **email-sender.json** - Documentation and notifications
6. **analytics-tracker.json** - Metrics tracking
7. **knowledge-sync.json** - Weekly Google Drive sync (cron)

## How to Import

1. Open n8n at https://n8n.jacoposabbacapetta.it
2. Go to **Workflows** → **Import from File**
3. Select the JSON file
4. Configure credentials:
   - OpenRouter API
   - PostgreSQL Database
   - Google Calendar API
   - SMTP/Email
5. Activate the workflow

## Workflow Dependencies

### chat-handler.json
- **Triggers**: Webhook (POST /webhook/chat)
- **Calls**: rag-processor, lead-qualifier
- **Databases**: PostgreSQL (conversations, messages)
- **APIs**: OpenRouter GPT-4o

### rag-processor.json
- **Triggers**: Called by chat-handler
- **Databases**: Qdrant (vector search)
- **Returns**: Top 3-5 relevant chunks

### lead-qualifier.json
- **Triggers**: Called by chat-handler
- **Databases**: PostgreSQL (leads table)
- **APIs**: OpenRouter (for extraction/scoring)
- **Actions**: Email alert for hot leads (BANEC ≥18)

### calendar-booking.json
- **Triggers**: Called by chat-handler
- **APIs**: Google Calendar
- **Actions**: Create event, send confirmation email

### email-sender.json
- **Triggers**: Called by various workflows
- **APIs**: SMTP/SendGrid
- **Actions**: Send emails with attachments

### analytics-tracker.json
- **Triggers**: Called by various workflows
- **Databases**: PostgreSQL (metrics table)

### knowledge-sync.json
- **Triggers**: Cron (weekly, Sunday 2 AM)
- **APIs**: Google Drive
- **Actions**: Trigger RAG processing container

## Environment Variables Needed

Make sure these are configured in n8n:

```bash
# Database
DB_HOST=demy-postgres
DB_PORT=5432
DB_NAME=demy_chatbot
DB_USER=demy_user
DB_PASSWORD=your_password

# Qdrant
QDRANT_HOST=demy-qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=aidemy_knowledge

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-...

# Google
GOOGLE_CALENDAR_ID=primary
```

## Testing Workflows

### Test chat-handler webhook:
```bash
curl -X POST https://n8n.jacoposabbacapetta.it/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "message": "Come funzionano i vostri servizi?",
    "user_id": "test-user",
    "timestamp": "2025-01-30T10:00:00Z"
  }'
```

Expected response:
```json
{
  "message": "Risposta del chatbot qui...",
  "session_id": "test-session-123",
  "timestamp": "2025-01-30T10:00:05Z"
}
```

## Notes

- The workflows are designed to work with the Docker setup in `/home/jack/docker-services/aidemy-chatbot-demy/`
- All service names (postgres, qdrant) match the docker-compose.yml configuration
- Workflows communicate via the `demy_internal` and `traefik` networks
- Hot leads (BANEC ≥18) trigger automatic email alerts to j.sabbacapetta@gmail.com
