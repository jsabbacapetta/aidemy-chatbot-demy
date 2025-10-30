# 🤖 Aidemy Chatbot - Demy

> Un chatbot conversazionale intelligente per aidemy.it che dimostra l'expertise di Aidemy nell'implementazione di AI generativa, qualifica lead automaticamente e facilita la prenotazione di call di Esplorazione Strategica.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-orange)](https://github.com/sabbacapetta/aidemy-chatbot-demy)
[![n8n](https://img.shields.io/badge/Powered%20by-n8n-blue)](https://n8n.io)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter%20GPT--4o-green)](https://openrouter.ai)

---

## 📋 Indice

- [Overview](#-overview)
- [Features](#-features)
- [Architettura](#-architettura)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Documentazione](#-documentazione)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Demy** (nome interno del progetto) è un assistente conversazionale AI che rappresenta Aidemy sul sito web. Il chatbot:

- 💬 **Risponde in modo intelligente** alle domande sui servizi Aidemy utilizzando RAG (Retrieval-Augmented Generation)
- 🎯 **Qualifica automaticamente i lead** con il sistema BANEC (Budget, Autorità, Necessità, Emergenza, Compatibilità)
- 📅 **Facilita la prenotazione** di call di Esplorazione Strategica integrandosi con Google Calendar
- 📧 **Invia documentazione personalizzata** via email in base alla conversazione
- 🧠 **Impara continuamente** attraverso aggiornamenti settimanali della knowledge base

### 🎨 Archetipo del Brand

Il chatbot incarna l'archetipo di **"Angelo Custode con elementi del Mago"**:
- **Angelo Custode**: Accogliente, rassicurante, orientato al benessere dell'utente
- **Mago**: Saggio ma non pedante, capace di rendere semplice il complesso

**Tono di voce**: Saggezza senza pedanteria, empatia diretta, autorevolezza informale

---

## ✨ Features

### MVP (Fase 1) - Target: 2 settimane
- [x] **Chat Widget Embeddabile** - Script JS che si integra su Landingi
- [x] **Conversazioni Intelligenti** - Powered by GPT-4o + RAG su knowledge base Aidemy
- [x] **Qualificazione Lead** - Sistema automatico con scoring BANEC (caldo/tiepido/freddo)
- [x] **Booking Call** - Integrazione Google Calendar per prenotazioni Esplorazione Strategica
- [x] **Invio Documentazione** - Email automatiche con PDF, case study e materiali
- [x] **Escalation a Jack** - Fallback intelligente per domande senza risposta

### Fase 2 (Settimane 3-6)
- [ ] Supporto clienti esistenti su progetti in corso
- [ ] Dashboard Grafana per metriche e analytics avanzate
- [ ] Ottimizzazioni performance (caching, query optimization)
- [ ] A/B testing posizionamento widget

### Fase 3 (Mesi 2-3)
- [ ] Content delivery educativo approfondito
- [ ] Multi-lingua (inglese)
- [ ] Integrazione CRM
- [ ] Voice/video capabilities (se ROI positivo)

---

## 🏗️ Architettura

```
┌─────────────────┐
│  Sito Aidemy.it │
│   (Landingi)    │
└────────┬────────┘
         │ (Widget JS)
         ↓
┌─────────────────┐
│  n8n Webhook    │
│  (VPS Docker)   │
└────────┬────────┘
         │
         ↓
┌────────────────────────────────────────┐
│       n8n Workflow Orchestration       │
├────────────────────────────────────────┤
│ • Chat Handler                         │
│ • RAG Processor                        │
│ • Lead Qualifier (BANEC)               │
│ • Calendar Booking                     │
│ • Email Sender                         │
│ • Knowledge Sync (Cron)                │
└──┬──────────┬──────────┬──────────┬───┘
   │          │          │          │
   ↓          ↓          ↓          ↓
┌──────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│ GPT4o│ │ Qdrant │ │ Postgres│ │  Google  │
│(LLM) │ │(Vector)│ │   (DB)  │ │ Services │
└──────┘ └────────┘ └─────────┘ └──────────┘
```

### Componenti Principali

1. **Frontend Widget** (`frontend/widget/`)
   - Chat interface embeddabile via script JS
   - Responsive design, accessibile, mobile-first

2. **Backend Orchestration** (`n8n/workflows/`)
   - 7 workflow n8n per gestione completa chatbot
   - Event-driven architecture

3. **RAG System** (`rag/`)
   - Document processing da Google Drive
   - Chunking semantico (500 token/chunk)
   - Embeddings con OpenAI text-embedding-3-small
   - Vector search con Qdrant

4. **Database** (`database/`)
   - PostgreSQL per conversazioni, lead, metriche
   - Schema ottimizzato per analytics

---

## 🛠️ Tech Stack

### Core Technologies
- **Orchestration**: [n8n](https://n8n.io) (self-hosted su VPS)
- **LLM**: [OpenRouter](https://openrouter.ai) GPT-4o
- **Vector DB**: [Qdrant](https://qdrant.tech) (Docker)
- **Database**: PostgreSQL
- **Frontend**: Vanilla JavaScript (no framework, max performance)

### Integrations
- **Knowledge Base**: Google Drive API
- **Calendar**: Google Calendar API (futuro: Tidycal/Calendly)
- **Email**: SMTP / SendGrid
- **Embeddings**: OpenAI text-embedding-3-small

### Development Tools
- **Version Control**: Git + GitHub
- **Testing**: Jest (frontend), Playwright (E2E)
- **Deployment**: Docker Compose
- **Monitoring**: n8n logs + Grafana (opzionale)

---

## 🚀 Quick Start

### Prerequisites

- **VPS** con minimo 4GB RAM, 2 CPU, 50GB storage
- **Docker** e **Docker Compose** installati
- **n8n** installato e configurato
- **Account necessari**:
  - OpenRouter (per GPT-4o)
  - Google Cloud Platform (per Drive e Calendar API)
  - SMTP o SendGrid (per email)

### Installazione

```bash
# 1. Clone del repository
git clone https://github.com/sabbacapetta/aidemy-chatbot-demy.git
cd aidemy-chatbot-demy

# 2. Setup environment variables
cp .env.example .env
# Editare .env con le proprie credenziali

# 3. Avvio Qdrant Vector DB
cd docker/qdrant
docker-compose up -d

# 4. Setup database PostgreSQL
psql -U postgres -f database/schema.sql

# 5. Installazione dipendenze RAG
cd rag
pip install -r requirements.txt

# 6. Processing iniziale knowledge base
python document-processor.py
python embeddings-generator.py

# 7. Import workflow n8n
# Importare manualmente i file da n8n/workflows/ nella UI di n8n

# 8. Deploy widget su Landingi
# Copiare lo snippet da frontend/widget/embed-snippet.html
```

### Test Locale

```bash
# Test widget in locale
cd frontend/widget
python -m http.server 8080
# Aprire http://localhost:8080/test.html

# Test workflow n8n
# Usare Postman o curl per testare webhook
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Ciao","session_id":"test-123"}'
```

---

## 📂 Struttura del Progetto

```
aidemy-chatbot-demy/
├── docs/                          # Documentazione completa
│   ├── PRD.md                     # Product Requirements Document
│   ├── API.md                     # Documentazione API n8n webhooks
│   └── DEPLOYMENT.md              # Guida deployment step-by-step
│
├── tasks/                         # Task list per implementazione
│   └── tasks-0001-prd-aidemy-chatbot.md
│
├── n8n/                           # n8n workflows
│   └── workflows/
│       ├── chat-handler.json
│       ├── rag-processor.json
│       ├── lead-qualifier.json
│       ├── calendar-booking.json
│       ├── email-sender.json
│       ├── analytics-tracker.json
│       └── knowledge-sync.json
│
├── frontend/                      # Chat widget frontend
│   └── widget/
│       ├── chat-widget.js
│       ├── chat-widget.css
│       ├── chat-widget.html
│       ├── config.js
│       └── embed-snippet.html
│
├── rag/                           # RAG system
│   ├── document-processor.py     # Document chunking e preprocessing
│   ├── embeddings-generator.py   # Generazione embeddings
│   ├── qdrant-setup.sh           # Setup script Qdrant
│   └── requirements.txt
│
├── database/                      # Database schema e migrations
│   ├── schema.sql
│   └── migrations/
│
├── docker/                        # Docker configurations
│   └── qdrant/
│       └── docker-compose.yml
│
├── config/                        # Configuration files
│   ├── prompts.yaml              # System prompts LLM
│   └── calendar-settings.yaml    # Calendar booking config
│
├── tests/                         # Test suite
│   ├── widget/
│   ├── n8n/
│   └── integration/
│
├── .env.example                   # Example environment variables
├── .gitignore
├── README.md                      # Questo file
└── LICENSE
```

---

## 📚 Documentazione

### Documenti Principali

- **[PRD.md](docs/PRD.md)** - Product Requirements Document completo con decisioni tecniche
- **[TASKS.md](tasks/tasks-0001-prd-aidemy-chatbot.md)** - Task list dettagliato per implementazione (50+ tasks)
- **[API.md](docs/API.md)** - Documentazione API endpoints n8n (da creare)
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Guida deployment passo-passo (da creare)

### Guide Rapide

- [Come aggiungere nuovi documenti alla knowledge base](#)
- [Come modificare il tono di voce del chatbot](#)
- [Come interpretare lo score BANEC dei lead](#)
- [Troubleshooting comuni](#)

---

## 🎯 Metriche di Successo

### KPI Primari (Target Mese 2)

| Metrica | Target | Status |
|---------|--------|--------|
| Conversazioni Avviate | 50+/mese | 🔄 |
| Conversion Rate (conversazioni → call) | 10% | 🔄 |
| Lead Qualificati "Caldi" (BANEC >18) | 30+/mese | 🔄 |

### KPI Secondari

| Metrica | Target | Status |
|---------|--------|--------|
| Engagement Rate | >5 msg/conversazione | 🔄 |
| Tempo Risposta | <3 secondi | 🔄 |
| Satisfaction Score | >80% feedback positivo | 🔄 |

### Business Impact (Stimato)

- ✅ Riduzione 50% email ripetitive su domande base
- ✅ Aumento 20% lead qualificati vs. form statico
- ✅ Riduzione 30% tempo Jack in call explorative non qualificate

---

## 🗓️ Roadmap

### ✅ Q4 2024 - Setup e Planning
- [x] Definizione requisiti e PRD
- [x] Setup repository GitHub
- [x] Decisioni tecniche finalizzate

### 🔄 Q1 2025 - MVP Development (Settimane 1-2)
- [ ] Setup infrastruttura VPS e Docker
- [ ] Implementazione RAG system
- [ ] Sviluppo workflow n8n core
- [ ] Implementazione widget frontend
- [ ] Integrazione Google Calendar e Email
- [ ] Sistema qualificazione lead BANEC
- [ ] Testing e deploy su Landingi

### 📅 Q1 2025 - Enhancement (Settimane 3-6)
- [ ] Supporto clienti esistenti
- [ ] Dashboard analytics avanzata
- [ ] Ottimizzazioni performance
- [ ] A/B testing widget

### 📅 Q2 2025 - Advanced Features
- [ ] Content delivery educativo
- [ ] Multi-lingua (inglese)
- [ ] Integrazione CRM
- [ ] Analisi sentiment conversazioni

---

## 🤝 Contributing

Questo è un progetto privato di Aidemy. Per contribuire:

1. Crea un branch dal `development`
2. Implementa la tua feature seguendo il task list
3. Testa localmente
4. Crea una Pull Request verso `development`
5. Dopo review, merge su `main` per deploy produzione

### Convenzioni

- **Commit messages**: Segui [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` nuove feature
  - `fix:` bug fix
  - `docs:` aggiornamenti documentazione
  - `refactor:` refactoring codice
  - `test:` aggiunta test
  
- **Branch naming**:
  - `feature/nome-feature`
  - `fix/nome-bug`
  - `docs/nome-doc`

### Code Style

- **JavaScript**: [StandardJS](https://standardjs.com/)
- **Python**: [PEP 8](https://peps.python.org/pep-0008/)
- **n8n workflows**: Nomenclatura chiara e descrittiva dei nodi

---

## 🔒 Security & Privacy

- ✅ **HTTPS enforcement** su tutti gli endpoint
- ✅ **Rate limiting** su webhook per prevenire abuse
- ✅ **Input sanitization** per prevenire injection attacks
- ✅ **GDPR compliance** - storage conversazioni con data retention policy
- ✅ **Secrets management** - mai committare credenziali (.env in .gitignore)

### Data Retention

- **Conversazioni**: 90 giorni (configurable)
- **Lead qualificati**: Indefinito (fino a conversione o opt-out)
- **Logs**: 30 giorni
- **Metriche aggregate**: Indefinito

---

## 🐛 Troubleshooting

### Widget non appare su Landingi
1. Verifica che lo script sia stato inserito correttamente
2. Controlla la console browser per errori JavaScript
3. Verifica che l'URL webhook n8n sia raggiungibile

### Chatbot non risponde
1. Verifica che il workflow `chat-handler` sia attivo in n8n
2. Controlla i logs n8n per errori
3. Verifica credenziali OpenRouter
4. Testa la connessione Qdrant

### RAG non trova documenti rilevanti
1. Verifica che il workflow `knowledge-sync` sia stato eseguito
2. Controlla che i documenti siano stati processati correttamente
3. Testa la similarity search direttamente su Qdrant
4. Verifica la qualità degli embeddings

### Booking non crea eventi in Calendar
1. Verifica le credenziali Google Calendar API
2. Controlla i permessi del service account
3. Verifica i logs del workflow `calendar-booking`

---

## 📞 Support

Per supporto o domande:

- **Email**: j.sabbacapetta@gmail.com
- **LinkedIn**: [Jack Sabba Capetta](https://www.linkedin.com/in/sabbacapetta)
- **Issues GitHub**: Usa il tab Issues per bug reports e feature requests

---

## 📄 License

Questo progetto è proprietà di **Aidemy** (Jacopo Sabba Capetta).

Copyright © 2025 Aidemy. Tutti i diritti riservati.

Per informazioni su licenze e utilizzo, contattare j.sabbacapetta@gmail.com

---

## 🙏 Acknowledgments

- **n8n** - Per la fantastica piattaforma di workflow automation
- **OpenRouter** - Per l'accesso semplificato ai modelli LLM
- **Qdrant** - Per il vector database performante e facile da usare
- **OpenAI** - Per i modelli GPT-4o e text-embedding

---

## 🚀 Status

**Current Version**: v0.1.0-alpha (In Development)  
**Target MVP Release**: Fine Gennaio 2025  
**Production Release**: Febbraio 2025

**Last Updated**: 30 Gennaio 2025

---

<p align="center">
  Made with ❤️ by <a href="https://www.jacoposabbacapetta.it">Jack Sabba Capetta</a> @ Aidemy
</p>

<p align="center">
  <a href="https://aidemy.it">🌐 aidemy.it</a> •
  <a href="https://sabbacapetta.substack.com">📧 Newsletter</a> •
  <a href="https://www.linkedin.com/in/sabbacapetta">💼 LinkedIn</a>
</p>
