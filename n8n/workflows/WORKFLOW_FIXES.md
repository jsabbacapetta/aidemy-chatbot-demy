# N8N Workflow Fixes and Improvements

**Date**: 2025-01-30
**Status**: ✅ Completed

## Overview

Fixed critical issues in existing workflows and created 6 missing workflows to complete the Demy chatbot orchestration system.

---

## 🔧 Fixed: chat-handler.json

### Problems Identified

1. **Missing embedding generation** - Qdrant search referenced `$json.query_embedding` but no node generated it
2. **Unformatted chat history** - Raw JSON array passed to GPT-4o prompt instead of formatted text
3. **Filesystem dependency** - System prompt loaded via `fs.readFileSync` which may fail in Docker
4. **Hardcoded workflow ID** - Lead qualifier referenced placeholder ID instead of env variable

### Solutions Implemented

1. ✅ **Added "Generate Query Embedding" node** (position: 1250, 300)
   - Uses OpenRouter API with `text-embedding-3-small` model
   - Generates embedding from user message
   - Outputs to `$json.data[0].embedding`

2. ✅ **Added "Format Chat History" node** (position: 1250, 450)
   - Converts message array to readable format
   - Output: `"Utente: ... \n Assistente: ..."`
   - Handles empty/null history gracefully

3. ✅ **Improved "Load System Prompt" node**
   - Embedded full prompt text directly in function code
   - Removed filesystem dependency
   - More reliable in containerized environment

4. ✅ **Updated "Call GPT-4o" prompt structure**
   - Now uses `$node['Format Chat History'].json.formatted_history`
   - Context and history properly separated
   - Cleaner, more readable prompt

5. ✅ **Fixed "Trigger Lead Qualification"**
   - Changed from hardcoded ID to `$env.LEAD_QUALIFIER_WORKFLOW_ID`
   - Added session_id and conversation_id parameters

6. ✅ **Updated workflow connections**
   - "Get Chat History" now connects to both embedding and formatting nodes
   - Both paths merge at "Call GPT-4o"
   - Proper data flow maintained

---

## ✨ Created: lead-qualifier.json

**Purpose**: Analyze conversations, extract lead info, calculate BANEC score

### Features

- Extracts lead information using GPT-4o (structured JSON output)
- Calculates BANEC score (Budget, Authority, Necessity, Emergency, Compatibility)
- Scores range: 5-25 points (hot ≥18, warm 12-17, cold 5-11)
- Saves lead data to PostgreSQL
- Triggers hot lead email alert if score ≥18
- Returns JSON with lead_id, status, banec_total

### Key Nodes

1. Webhook Trigger (POST `/lead-qualifier`)
2. Get Conversation (PostgreSQL with message aggregation)
3. Extract Lead Info (GPT-4o with JSON mode)
4. Calculate BANEC Score (GPT-4o with detailed criteria)
5. Save Lead (PostgreSQL upsert)
6. Is Hot Lead? (conditional routing)
7. Send Hot Lead Alert (calls email-sender workflow)

---

## 📧 Created: email-sender.json

**Purpose**: Unified email sending system for all notification types

### Features

- Three email templates: `hot_lead_alert`, `call_confirmation`, `docs_request`
- HTML formatted emails with consistent branding
- Dynamic content injection from workflow parameters
- SMTP integration
- Template routing via Switch node

### Templates

1. **Hot Lead Alert** → Jack (internal notification)
   - Lead details, BANEC score, action items
   - Styled with Aidemy colors

2. **Call Confirmation** → Lead
   - Appointment details, meeting link
   - Preparation tips and expectations

3. **Docs Request** → Lead
   - Links to materials, next steps
   - Call-to-action buttons

---

## 📅 Created: calendar-booking.json

**Purpose**: Google Calendar integration for Strategic Exploration calls

### Features

- Two actions: `get_slots` and `create`
- Generates available slots (next 7 days, 9:00-18:00, weekdays only)
- Creates Google Calendar events with video conferencing
- Saves bookings to PostgreSQL
- Sends confirmation email via email-sender workflow
- 30-minute appointment duration

### Key Nodes

1. Route by Action (switch: get_slots vs create)
2. Generate Available Slots (function with business hours logic)
3. Create Calendar Event (Google Calendar API)
4. Parse Event (extract meeting link and formatted datetime)
5. Save Booking (PostgreSQL)
6. Send Confirmation Email (async call)

---

## 📊 Created: analytics-tracker.json

**Purpose**: Track and aggregate chatbot metrics

### Features

- Logs all events: conversation_started, lead_qualified, call_booked, etc.
- Stores raw events in `analytics_events` table
- Updates daily stats in `analytics_daily_stats` table
- Event routing for specific stat updates
- Supports custom metadata (JSON field)

### Event Types Tracked

- `conversation_started` → increments daily conversation counter
- `lead_qualified` → increments daily lead counter
- `call_booked` → increments daily call counter
- Others → logged but no stat update

---

## 🔄 Created: knowledge-sync.json

**Purpose**: Weekly sync of knowledge base from Google Drive to Qdrant

### Features

- Cron trigger: Every Sunday at 2:00 AM
- Lists files from Google Drive folder
- Filters supported types (PDF, Docs, TXT, MD)
- Downloads and converts to plain text
- Chunks documents (500 tokens, 50 overlap)
- Generates embeddings via OpenRouter
- Uploads to Qdrant vector database
- Logs sync operations to PostgreSQL
- Optional email report

### Processing Pipeline

1. List Drive Files → Filter → Download → Chunk → Generate Embeddings → Upload to Qdrant
2. Each chunk becomes a point in Qdrant with metadata
3. Point ID format: `{source_id}_{chunk_index}`

---

## 🔍 Created: rag-processor.json

**Purpose**: Standalone RAG query processor (optional, for testing/debugging)

### Features

- POST endpoint for RAG queries
- Generates embedding for query
- Searches Qdrant with configurable parameters
- Returns formatted results with relevance scores
- Configurable: limit, threshold, collection name

### Use Cases

- Testing RAG independently from chat
- Debugging knowledge base quality
- External integrations
- Future: Advanced search features

---

## 📋 Summary of Changes

| Workflow | Status | Changes |
|----------|--------|---------|
| chat-handler.json | ✅ Fixed | 4 critical bugs fixed, 2 nodes added, connections updated |
| lead-qualifier.json | ✨ Created | Complete BANEC qualification system |
| email-sender.json | ✨ Created | 3 templates, HTML formatting, SMTP |
| calendar-booking.json | ✨ Created | Google Calendar + booking management |
| analytics-tracker.json | ✨ Created | Event logging + daily stats |
| knowledge-sync.json | ✨ Created | Weekly Google Drive → Qdrant sync |
| rag-processor.json | ✨ Created | Standalone RAG endpoint |

**Total**: 1 workflow fixed, 6 workflows created

---

## 🔑 Environment Variables Required

Add these to n8n environment or `.env`:

```bash
# Workflow IDs (get after importing to n8n)
LEAD_QUALIFIER_WORKFLOW_ID=<id>
EMAIL_SENDER_WORKFLOW_ID=<id>
CALENDAR_BOOKING_WORKFLOW_ID=<id>

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=<folder-id>
```

---

## 📝 Next Steps

1. **Import workflows to n8n**
   - Go to n8n UI → Workflows → Import
   - Import each JSON file
   - Note the workflow IDs

2. **Configure credentials**
   - PostgreSQL (id: 1, name: "Demy PostgreSQL")
   - OpenRouter API (id: 2, name: "OpenRouter API")
   - SMTP (id: 3, name: "SMTP Account")
   - Google Calendar (id: 4, name: "Google Calendar")
   - Google Drive (id: 5, name: "Google Drive")

3. **Update environment variables**
   - Set workflow IDs in n8n environment
   - Set Google Drive folder ID

4. **Test workflows**
   - Test chat-handler with curl
   - Verify RAG retrieval works
   - Test lead qualification
   - Test calendar booking
   - Test email sending
   - Run knowledge-sync manually once

5. **Activate workflows**
   - Enable all workflows in n8n
   - Verify cron trigger for knowledge-sync

---

## 🐛 Known Limitations

1. **Chat history ordering**: Currently DESC in query, reversed in formatter (verify correct order in UI)
2. **Embedding rate limits**: No retry logic if OpenRouter API fails
3. **Calendar slots**: Simple algorithm, doesn't check existing appointments
4. **Document chunking**: Word-based approximation, not token-accurate
5. **No webhook authentication**: Should add API key validation

---

## 📚 Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Project overview and setup
- [README.md](../../README.md) - General documentation
- [database/schema.sql](../../database/schema.sql) - Database schema
- [config/prompts.yaml](../../config/prompts.yaml) - System prompts

---

**Author**: Claude (Anthropic)
**Reviewed by**: Jack Sabba Capetta
**Version**: 1.0
