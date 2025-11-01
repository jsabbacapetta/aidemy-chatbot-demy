# Aidemy Chatbot - Quick Start Guide

Get the chatbot running in 10 minutes!

## Prerequisites Check

```bash
# Verify Docker is running
docker --version
docker compose version

# Verify Traefik is running
docker ps | grep traefik

# Verify n8n is running
docker ps | grep n8n
```

All should show running services. ✅

## Step 1: Setup (2 minutes)

```bash
# Navigate to docker services
cd /home/jack/docker-services/aidemy-chatbot-demy

# Create environment file
cp .env.example .env

# Edit with your keys (required: POSTGRES_PASSWORD, OPENAI_API_KEY)
nano .env
```

Minimum required in `.env`:
```bash
POSTGRES_PASSWORD=your_secure_password
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

## Step 2: Start Services (1 minute)

```bash
# Start all containers
docker compose up -d

# Verify they're running
docker compose ps

# Should see:
# - demy-postgres (healthy)
# - demy-qdrant (healthy)
# - demy-widget (running)
```

## Step 3: Test Widget (30 seconds)

Open in browser:
```
https://demy.aidemy.jacoposabbacapetta.it/index.html
```

You should see the demo page with a blue chat button in bottom-right! 🎉

(It won't respond yet - need n8n workflow)

## Step 4: Configure n8n (3 minutes)

1. **Open n8n**: https://n8n.jacoposabbacapetta.it

2. **Add PostgreSQL Credential**:
   - Name: "Demy PostgreSQL"
   - Host: `demy-postgres`
   - Database: `demy_chatbot`
   - User: `demy_user`
   - Password: (from your .env)
   - Port: `5432`
   - SSL: Off

3. **Add OpenRouter Credential**:
   - Name: "OpenRouter API"
   - API Key: Your OpenRouter key (get from https://openrouter.ai)

4. **Import Workflow**:
   - Go to Workflows → Import from File
   - Select: `/home/jack/aidemy-chatbot/aidemy-chatbot-demy/n8n/workflows/chat-handler.json`
   - Update credential references to the ones you just created
   - **Activate the workflow**

5. **Note the webhook URL** (should be):
   ```
   https://n8n.jacoposabbacapetta.it/webhook/chat
   ```

## Step 5: Add Knowledge (3 minutes)

```bash
# Create documents directory
mkdir -p /home/jack/docker-services/aidemy-chatbot-demy/documents

# Add a test document (create a simple markdown file)
cat > /home/jack/docker-services/aidemy-chatbot-demy/documents/test.md << 'EOF'
# Aidemy Services

## Esplorazione Strategica
L'Esplorazione Strategica è il nostro servizio di consulenza iniziale.
Costa €1.500 e dura circa 2 settimane.

## Come Funzioniamo
Aiutiamo le organizzazioni a navigare il cambiamento attraverso:
- AI Generativa
- Strategia
- Innovazione

## Case Study
Abbiamo aiutato oltre 50 aziende in Italia.
EOF

# Process the document
cd /home/jack/docker-services/aidemy-chatbot-demy
docker compose run --rm rag-processor python /app/document-processor.py

# Generate embeddings
docker compose run --rm rag-processor python /app/embeddings-generator.py
```

## Step 6: Test Everything! (1 minute)

### Test the webhook directly:
```bash
curl -X POST https://n8n.jacoposabbacapetta.it/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Come funzionano i vostri servizi?",
    "user_id": "test"
  }'
```

Expected response:
```json
{
  "message": "Aiutiamo le organizzazioni a navigare il cambiamento attraverso...",
  "session_id": "test-123",
  "timestamp": "2025-..."
}
```

### Test the widget:
1. Open https://demy.aidemy.jacoposabbacapetta.it/index.html
2. Click the blue chat button
3. Type: "Come funzionano i vostri servizi?"
4. You should get a response! 🎉

## Troubleshooting

### Widget loads but chat doesn't work:
```bash
# Check n8n workflow is active
# Check n8n execution logs in UI
# Verify webhook URL in frontend/widget/config.js
```

### "No documents found" response:
```bash
# Verify Qdrant has data
curl http://localhost:6333/collections/aidemy_knowledge

# Rerun embeddings if needed
docker compose run --rm rag-processor python /app/embeddings-generator.py
```

### Container won't start:
```bash
# Check logs
docker compose logs -f demy-postgres
docker compose logs -f demy-qdrant

# Restart
docker compose down
docker compose up -d
```

### "there is no parameter $1" error in PostgreSQL nodes:
Se dopo aver importato il workflow ottieni questo errore, significa che la sintassi dei parametri non è compatibile con la tua versione di n8n:

1. **Edit the PostgreSQL nodes manually in n8n UI**:
   - Click on each PostgreSQL node
   - In "Query Parameters", set the mode to "Independently"
   - Add parameters one by one: `$json.session_id`, `$json.user_id`, etc.

Oppure:

2. **Test the workflow with a simple query first**:
   - Create a test PostgreSQL node
   - Query: `SELECT 1`
   - If that works, gradually add parameters

## Next Steps

Now that it works:

1. **Add Real Documents**: Replace test.md with your actual PDFs, DOCX files
2. **Improve Prompts**: Edit `config/prompts.yaml` to match your brand voice
3. **Add Lead Qualification**: Implement the lead-qualifier workflow
4. **Add Calendar**: Setup Google Calendar integration
5. **Embed on Landingi**: Use code from `frontend/widget/embed-snippet.html`

## Useful Commands

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop everything
docker compose down

# Check database
docker exec -it demy-postgres psql -U demy_user -d demy_chatbot

# Check Qdrant
curl http://localhost:6333/collections

# Reprocess documents
docker compose run --rm rag-processor python /app/document-processor.py
docker compose run --rm rag-processor python /app/embeddings-generator.py
```

## Success!

You now have:
- ✅ A working chat widget
- ✅ RAG-powered responses
- ✅ Database storing conversations
- ✅ Production-ready infrastructure

Total setup time: ~10 minutes ⚡

For detailed deployment info, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

*Need help? Email: j.sabbacapetta@gmail.com*
