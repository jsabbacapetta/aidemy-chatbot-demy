# Aidemy Chatbot - Deployment Guide

Complete step-by-step guide to deploy the Aidemy chatbot (Demy) on your VPS.

## Prerequisites

✅ VPS with Docker and Docker Compose installed
✅ Traefik reverse proxy already running
✅ n8n already configured at `n8n.jacoposabbacapetta.it`
✅ Domain/subdomain configured: `demy.aidemy.jacoposabbacapetta.it`

## Step 1: Setup Environment Variables

```bash
cd /home/jack/docker-services/aidemy-chatbot-demy
cp .env.example .env
nano .env
```

Configure these required variables:
```bash
POSTGRES_PASSWORD=your_secure_password_here
OPENROUTER_API_KEY=sk-or-v1-your-key-here  # For both GPT-4o AND embeddings
```

## Step 2: Start Docker Services

```bash
# Start all services
docker compose up -d

# Verify services are running
docker compose ps

# Check logs
docker compose logs -f
```

Expected containers:
- `demy-postgres` (PostgreSQL database)
- `demy-qdrant` (Vector database)
- `demy-widget` (Nginx serving the chat widget)
- `demy-rag-processor` (For manual RAG processing)

## Step 3: Initialize Database

The database schema will be automatically applied on first startup (via docker-entrypoint-initdb.d).

Verify:
```bash
docker exec -it demy-postgres psql -U demy_user -d demy_chatbot -c "\dt"
```

You should see tables: conversations, messages, leads, metrics, knowledge_documents

## Step 4: Prepare Knowledge Base Documents

```bash
# Create documents directory
mkdir -p /home/jack/docker-services/aidemy-chatbot-demy/documents

# Copy your knowledge base files (PDFs, DOCX, MD) here
cp /path/to/your/documents/*.pdf /home/jack/docker-services/aidemy-chatbot-demy/documents/
```

Supported formats:
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Markdown (.md, .markdown)
- Plain Text (.txt)

## Step 5: Process Documents and Generate Embeddings

```bash
# Process documents (chunking)
docker compose run --rm rag-processor python document-processor.py

# Generate embeddings and store in Qdrant
docker compose run --rm rag-processor python embeddings-generator.py
```

This will:
1. Extract text from all documents
2. Chunk them into 500-token pieces with 50-token overlap
3. Generate embeddings using OpenAI
4. Store vectors in Qdrant

Verify Qdrant has data:
```bash
curl http://localhost:6333/collections/aidemy_knowledge
```

## Step 6: Import n8n Workflows

1. Open n8n UI: https://n8n.jacoposabbacapetta.it

2. Configure credentials in n8n:
   - **PostgreSQL**:
     - Host: `demy-postgres` (via Docker network)
     - Port: `5432`
     - Database: `demy_chatbot`
     - User: `demy_user`
     - Password: (from .env)

   - **OpenRouter API**:
     - API Key: Your OpenRouter key

   - **Google Calendar** (optional for MVP):
     - OAuth2 or Service Account credentials

   - **SMTP/Email**:
     - Your email provider settings

3. Import workflows from `/home/jack/aidemy-chatbot/aidemy-chatbot-demy/n8n/workflows/`:
   - Start with `chat-handler.json`
   - Import others as needed

4. Update the chat-handler workflow:
   - Configure PostgreSQL nodes with your credential
   - Configure Qdrant HTTP request (should work as-is with `http://demy-qdrant:6333`)
   - Configure OpenRouter node
   - Activate the workflow

5. Note the webhook URL (should be):
   ```
   https://n8n.jacoposabbacapetta.it/webhook/chat
   ```

## Step 7: Update Widget Configuration

Edit the widget config if needed:
```bash
nano /home/jack/aidemy-chatbot/aidemy-chatbot-demy/frontend/widget/config.js
```

Ensure `webhookUrl` matches your n8n webhook:
```javascript
webhookUrl: 'https://n8n.jacoposabbacapetta.it/webhook/chat',
```

## Step 8: Test the Chat Widget

### Local Test:
```bash
# The widget is already served at: https://demy.aidemy.jacoposabbacapetta.it
# Open in browser to test
```

Or test locally:
```bash
cd /home/jack/aidemy-chatbot/aidemy-chatbot-demy/frontend/widget
python -m http.server 8080
# Open http://localhost:8080/index.html
```

### Test the n8n Webhook:
```bash
curl -X POST https://n8n.jacoposabbacapetta.it/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Come funzionano i vostri servizi?",
    "user_id": "test-user"
  }'
```

Expected response:
```json
{
  "message": "Risposta del chatbot...",
  "session_id": "test-123",
  "timestamp": "2025-01-30T..."
}
```

## Step 9: Embed on Landingi

1. Copy the embed code from `frontend/widget/embed-snippet.html`

2. In Landingi, add a **Custom HTML** element

3. Paste this code:
```html
<link rel="stylesheet" href="https://demy.aidemy.jacoposabbacapetta.it/chat-widget.css">
<script src="https://demy.aidemy.jacoposabbacapetta.it/config.js"></script>
<script src="https://demy.aidemy.jacoposabbacapetta.it/chat-widget.js"></script>
```

4. Place it just before the closing `</body>` tag

5. Publish and test!

## Step 10: Monitor and Verify

### Check Docker containers:
```bash
docker compose ps
docker compose logs -f demy-widget
docker compose logs -f demy-postgres
```

### Check n8n executions:
- Go to n8n UI → Executions
- Verify chat-handler executions are successful

### Check database:
```bash
# Check conversations
docker exec -it demy-postgres psql -U demy_user -d demy_chatbot -c "SELECT * FROM conversations LIMIT 5;"

# Check messages
docker exec -it demy-postgres psql -U demy_user -d demy_chatbot -c "SELECT * FROM messages LIMIT 10;"
```

### Check Qdrant:
```bash
curl http://localhost:6333/collections/aidemy_knowledge
```

## Troubleshooting

### Widget not loading
1. Check nginx container: `docker logs demy-widget`
2. Verify Traefik routing: `docker logs traefik | grep demy`
3. Check DNS: `nslookup demy.aidemy.jacoposabbacapetta.it`
4. Test direct access: `curl https://demy.aidemy.jacoposabbacapetta.it/config.js`

### Chat not responding
1. Check n8n workflow is activated
2. Check n8n execution logs for errors
3. Verify webhook URL in widget config matches n8n
4. Test webhook with curl (see Step 8)

### RAG not finding documents
1. Verify documents were processed: `ls /home/jack/docker-services/aidemy-chatbot-demy/rag_documents`
2. Check Qdrant collection exists: `curl http://localhost:6333/collections`
3. Rerun embeddings generator if needed

### Database connection errors
1. Check postgres container is running
2. Verify credentials in n8n match .env
3. Test connection: `docker exec demy-postgres pg_isready`

## Next Steps (Post-MVP)

- [ ] Setup Google Calendar integration workflow
- [ ] Configure email sender workflow
- [ ] Implement lead qualifier workflow with BANEC scoring
- [ ] Setup weekly knowledge sync cron job
- [ ] Configure analytics and monitoring
- [ ] A/B test widget positioning on Landingi

## Maintenance

### Weekly Knowledge Base Update:
```bash
# Add new documents to documents folder
cp new-document.pdf /home/jack/docker-services/aidemy-chatbot-demy/documents/

# Reprocess
docker compose run --rm rag-processor python document-processor.py
docker compose run --rm rag-processor python embeddings-generator.py
```

### Backup Database:
```bash
docker exec demy-postgres pg_dump -U demy_user demy_chatbot > backup_$(date +%Y%m%d).sql
```

### Update Docker Images:
```bash
docker compose pull
docker compose up -d
```

## Support

For issues or questions:
- Email: j.sabbacapetta@gmail.com
- Check logs: `docker compose logs -f`
- Check n8n executions in UI
