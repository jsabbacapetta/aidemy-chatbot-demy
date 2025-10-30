# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Demy** is an AI-powered conversational chatbot for aidemy.it that demonstrates Aidemy's expertise in implementing generative AI solutions. The chatbot automatically qualifies leads using the BANEC framework (Budget, Authority, Necessity, Emergency, Compatibility), facilitates booking Strategic Exploration calls, and serves as a technical showcase.

**Key objectives:**
- Respond intelligently to questions about Aidemy services using RAG (Retrieval-Augmented Generation)
- Automatically qualify leads with BANEC scoring (hot: 18-25, warm: 12-17, cold: 5-11)
- Enable booking of Strategic Exploration calls via Google Calendar integration
- Send personalized documentation via email based on conversation context

## Architecture

The system follows an event-driven, fully Dockerized architecture orchestrated by n8n:

```
[Landingi Website]
    ↓ (Embeddable JS Widget)
[n8n Webhook - Docker Container]
    ↓
[n8n Workflow Orchestration]
    ↓ ↙ ↘ ↓
[GPT-4o]  [Qdrant/Chroma]  [PostgreSQL]  [Google APIs]
(OpenRouter)  (Docker)      (Docker)      (Calendar/Drive)
```

**Infrastructure:**
- **Reverse Proxy**: Traefik (handles SSL with Cloudflare, routes all services)
- **Orchestration**: n8n (already running in Docker at `n8n.jacoposabbacapetta.it`)
- **Networks**: Traefik network (external) + project internal network
- **Deployment Location**: `/home/jack/docker-services/aidemy-chatbot-demy/`

**Core components:**
1. **Frontend Widget** - Vanilla JavaScript (embeddable, no frameworks)
2. **n8n Workflows** - 7 workflows for complete chatbot orchestration
3. **RAG System** - Docker container with Python scripts for document processing
4. **Vector Database** - Qdrant or ChromaDB (Docker), semantic search with 500 token chunks
5. **PostgreSQL** - Docker container for conversations, leads, metrics
6. **LLM** - GPT-4o via OpenRouter API

## VPS Infrastructure Context

This VPS already runs multiple Dockerized services:
- **n8n**: Running at port 5678, accessible via `n8n.jacoposabbacapetta.it`
- **Traefik**: Reverse proxy handling SSL (Cloudflare) on ports 80/443
- **PostgreSQL instances**: Multiple postgres:15-alpine containers for various projects
- **Redis**: Available at redis:7-alpine if caching needed
- **Typebot, Jitsi, custom apps**: Other services on the VPS

**Docker pattern to follow:**
- Create `docker-compose.yml` in `/home/jack/docker-services/aidemy-chatbot-demy/`
- Use `traefik` external network for routing
- Create dedicated internal network (e.g., `demy_internal`)
- Add Traefik labels for SSL/routing if exposing HTTP endpoints
- Bind only to localhost (127.0.0.1) for non-Traefik ports
- Include health checks for all services

## Tech Stack

- **Orchestration:** n8n (Docker, already running)
- **LLM:** OpenRouter GPT-4o
- **Vector DB:** Qdrant (Docker) - *Note: ChromaDB is also configured but not running*
- **Database:** PostgreSQL 15-alpine (Docker)
- **Frontend:** Vanilla JavaScript (performance-optimized, embeddable)
- **Knowledge Base:** Google Drive API
- **Calendar:** Google Calendar API
- **Email:** SMTP/SendGrid
- **Reverse Proxy:** Traefik (handles all SSL/routing)

## Development Commands

### Docker Services Management

**Start all services:**
```bash
cd /home/jack/docker-services/aidemy-chatbot-demy
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f          # All services
docker compose logs -f qdrant   # Specific service
```

**Stop services:**
```bash
docker compose down             # Stop all
docker compose down -v          # Stop and remove volumes (careful!)
```

**Rebuild after changes:**
```bash
docker compose up -d --build
```

### Qdrant Vector Database

```bash
# Qdrant runs in Docker, accessible at localhost:6333
curl http://localhost:6333/collections  # List collections
```

### PostgreSQL Database

```bash
# Connect to the Demy PostgreSQL container
docker exec -it demy-postgres psql -U demy_user -d demy_chatbot

# Run schema migrations
docker exec -i demy-postgres psql -U demy_user -d demy_chatbot < database/schema.sql
```

### RAG System (Dockerized Python)

The RAG scripts run in a Docker container:

```bash
# Process documents and generate embeddings
docker compose run --rm rag-processor python document-processor.py
docker compose run --rm rag-processor python embeddings-generator.py

# Or enter the container for development
docker compose run --rm rag-processor sh
```

### n8n Workflows

n8n is already running. Access it at:
- **UI**: https://n8n.jacoposabbacapetta.it
- **Webhooks**: https://n8n.jacoposabbacapetta.it/webhook/...

**Import workflows:**
1. Open n8n UI
2. Go to Workflows → Import
3. Select JSON files from `n8n/workflows/`

**Test webhook locally:**
```bash
curl -X POST https://n8n.jacoposabbacapetta.it/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Ciao","session_id":"test-123"}'
```

### Frontend Widget Testing

```bash
# Serve widget locally for testing
cd frontend/widget
python -m http.server 8080
# Open http://localhost:8080/test.html
```

The production widget will be served via Docker (nginx container with Traefik routing).

## Docker Compose Structure

Create `/home/jack/docker-services/aidemy-chatbot-demy/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: demy-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: demy_chatbot
      POSTGRES_USER: demy_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - demy_internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U demy_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: demy-qdrant
    restart: unless-stopped
    ports:
      - "127.0.0.1:6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - traefik
      - demy_internal
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/"]
      interval: 10s
      timeout: 5s
      retries: 5

  rag-processor:
    build:
      context: ../../aidemy-chatbot/aidemy-chatbot-demy/rag
      dockerfile: Dockerfile
    container_name: demy-rag-processor
    volumes:
      - ../../aidemy-chatbot/aidemy-chatbot-demy/rag:/app
      - rag_documents:/app/documents
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    networks:
      - demy_internal
    depends_on:
      qdrant:
        condition: service_healthy

  widget-server:
    image: nginx:alpine
    container_name: demy-widget
    restart: unless-stopped
    volumes:
      - ../../aidemy-chatbot/aidemy-chatbot-demy/frontend/widget:/usr/share/nginx/html:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    networks:
      - traefik
      - demy_internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.demy-widget.entrypoints=websecure"
      - "traefik.http.routers.demy-widget.rule=Host(`demy.aidemy.jacoposabbacapetta.it`)"
      - "traefik.http.routers.demy-widget.tls=true"
      - "traefik.http.routers.demy-widget.tls.certresolver=cloudflare"
      - "traefik.http.services.demy-widget.loadbalancer.server.port=80"

volumes:
  postgres_data:
  qdrant_data:
  rag_documents:

networks:
  traefik:
    external: true
  demy_internal:
    driver: bridge
```

## n8n Workflows

The system uses 7 n8n workflows in `n8n/workflows/`:

1. **chat-handler.json** - Main webhook handler for chat messages
2. **rag-processor.json** - Document processing and similarity search
3. **lead-qualifier.json** - BANEC scoring and lead evaluation
4. **calendar-booking.json** - Google Calendar integration
5. **email-sender.json** - Documentation and notifications
6. **analytics-tracker.json** - Metrics tracking
7. **knowledge-sync.json** - Weekly Google Drive sync (cron)

### n8n Integration Notes

- n8n connects to services via Docker networks
- Use service names as hostnames (e.g., `http://demy-qdrant:6333`)
- To connect n8n to this project's network: add `demy_internal` to n8n networks or use `traefik` network
- Credentials stored in n8n: OpenRouter, Google APIs, SMTP

## Important Implementation Details

### Brand Voice

The chatbot embodies the "Guardian Angel with elements of the Wizard" archetype:
- **Guardian Angel**: Welcoming, reassuring, user-focused
- **Wizard**: Wise but not pedantic, simplifies complexity
- **Tone**: Wisdom without pedantry, direct empathy, informal authority

System prompt defined in `config/prompts.yaml`.

### Lead Qualification (BANEC)

Evaluates leads using 5 criteria (1-5 points each, total 5-25):
- **Budget**: Company size + cost questions
- **Authority**: Role (CEO/founder=5, other=3)
- **Necessity**: Challenge clarity
- **Emergency**: Timeline (immediate=5, exploration=2)
- **Compatibility**: Conversation quality

**Hot leads (≥18)** trigger immediate email alerts.

### RAG Configuration

- **Chunk size**: 500 tokens with 50 token overlap
- **Retrieval**: Top 3-5 chunks per query
- **Embeddings**: OpenAI text-embedding-3-small
- **Target latency**: <500ms for retrieval
- **Sync schedule**: Weekly (Sunday nights)

**Knowledge sources:**
- Service descriptions (6 core packages)
- Case studies and projects
- Newsletter articles (Substack)
- Structured FAQs
- Methodologies (LEGO SERIOUS PLAY, Design Thinking, OKR)

### Response Time Requirements

- **Target**: <3 seconds end-to-end
- **Timeout**: 30 seconds (show error after)

### Security & Privacy

- **HTTPS**: Traefik handles all SSL
- **Rate limiting**: Implement in n8n webhooks
- **Input sanitization**: Prevent injection attacks
- **Port binding**: Only localhost (127.0.0.1) for non-proxied ports
- **GDPR compliance**: Data retention policies configured

**Data retention:**
- Conversations: 90 days
- Qualified leads: Indefinite (until conversion/opt-out)
- Logs: 30 days
- Metrics: Indefinite

## Configuration & Secrets

Create `.env` file in `/home/jack/docker-services/aidemy-chatbot-demy/.env`:

```bash
# Database
DB_PASSWORD=secure_password_here

# OpenRouter API (for both LLM and embeddings)
OPENROUTER_API_KEY=sk-or-v1-...

# Google APIs
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Email
SMTP_HOST=smtp.example.com
SMTP_USER=...
SMTP_PASSWORD=...
```

**Never commit `.env` to git!** Use the `.env.example` template.

## Success Metrics (Month 2 Targets)

**Primary KPIs:**
- Conversations started: 50+/month
- Conversion rate (conversations → calls): 10%
- Hot qualified leads (BANEC >18): 30+/month

**Secondary KPIs:**
- Engagement rate: >5 messages/conversation
- Response time: <3 seconds
- Satisfaction score: >80% positive feedback

## Testing

### Unit Tests
```bash
cd frontend/widget
npm install
npm test  # Jest tests (>80% coverage target)
```

### Integration Tests
Test n8n workflows using n8n's built-in testing or:
```bash
cd tests/n8n
node workflow-tests.js
```

### E2E Tests
```bash
cd tests/integration
npm install
npx playwright test  # or npx cypress run
```

## Deployment Workflow

1. **Development**: Work in this repository (`/home/jack/aidemy-chatbot/aidemy-chatbot-demy/`)
2. **Docker setup**: Create/update services in `/home/jack/docker-services/aidemy-chatbot-demy/`
3. **Start services**: `docker compose up -d`
4. **Import n8n workflows**: Via n8n UI at https://n8n.jacoposabbacapetta.it
5. **Deploy widget**: Widget served via nginx container with Traefik SSL
6. **Embed on Landingi**: Use embed snippet pointing to `https://demy.aidemy.jacoposabbacapetta.it`

## Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation updates
- `refactor:` code refactoring
- `test:` adding tests
- `docker:` Docker configuration changes

**Branch naming:**
- `feature/feature-name`
- `fix/bug-name`
- `docs/doc-name`

## Troubleshooting

### Widget not appearing
1. Check browser console for errors
2. Verify nginx container is running: `docker ps | grep demy-widget`
3. Check Traefik routing: `docker logs traefik`
4. Test URL directly: `curl https://demy.aidemy.jacoposabbacapetta.it`

### Chatbot not responding
1. Check n8n workflow is active: https://n8n.jacoposabbacapetta.it
2. Check n8n logs: `docker logs n8n`
3. Test webhook directly with curl
4. Verify OpenRouter API key in n8n credentials

### RAG not finding documents
1. Check Qdrant is running: `docker ps | grep qdrant`
2. Verify collections exist: `curl http://localhost:6333/collections`
3. Check RAG processor logs: `docker compose logs rag-processor`
4. Verify knowledge-sync workflow ran successfully

### Database connection issues
1. Check PostgreSQL is running: `docker ps | grep demy-postgres`
2. Test connection: `docker exec demy-postgres pg_isready`
3. Check n8n can reach DB via `demy_internal` network
4. Verify credentials in n8n match `.env`

### Docker network issues
1. List networks: `docker network ls`
2. Inspect network: `docker network inspect demy_internal`
3. Verify services are on correct networks: `docker inspect <container>`
4. Recreate network if needed: `docker compose down && docker compose up -d`

## Important Notes

- **Vector DB decision**: PRD specifies Qdrant, but ChromaDB infrastructure exists. Stick with Qdrant as per PRD unless explicitly changed.
- **n8n network access**: Ensure n8n can access Demy services - may need to add `demy_internal` network to n8n container or use `traefik` network for communication.
- **RAG Python version**: Use Python 3.11+ for optimal performance
- **Widget caching**: Configure nginx cache headers for static assets
- **Monitoring**: Consider adding health check endpoints for external monitoring

## Contact

- **Owner**: Jack Sabba Capetta (Aidemy)
- **Email**: j.sabbacapetta@gmail.com
- **LinkedIn**: [Jack Sabba Capetta](https://www.linkedin.com/in/sabbacapetta)
- **Website**: [aidemy.it](https://aidemy.it)
