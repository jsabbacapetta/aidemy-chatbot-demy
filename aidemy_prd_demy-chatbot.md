# PRD: Chatbot Conversazionale Aidemy v1.0

## 1. Introduction/Overview

Questo progetto mira a creare un chatbot conversazionale per il sito aidemy.it che dimostri concretamente la capacità di Aidemy di implementare tecnologie di AI generativa in modo efficace. Il chatbot fungerà da dimostratore tecnologico e strumento di qualificazione lead, rispondendo alle domande più frequenti dei potenziali clienti e guidandoli verso l'Esplorazione Strategica.

**Problema risolto:** I potenziali clienti (come Mario) visitano il sito ma hanno domande specifiche sui servizi, costi, tempistiche e modalità operative prima di decidere di contattare Aidemy. Attualmente potrebbero non trovare risposta immediata o abbandonare il sito senza ingaggiamento.

**Goal principale:** Qualificare automaticamente i lead e facilitare la prenotazione di call di Esplorazione Strategica, dimostrando al contempo l'expertise di Aidemy nell'implementazione di AI generativa.

## 2. Goals

1. **Qualificazione Lead Automatizzata:** Identificare e qualificare potenziali clienti attraverso conversazioni naturali
2. **Riduzione Friction:** Rispondere istantaneamente alle domande più comuni sui servizi Aidemy
3. **Generazione Appuntamenti:** Facilitare la prenotazione di call di Esplorazione Strategica
4. **Dimostrazione Tecnologica:** Showcasare le competenze di Aidemy nell'implementazione di AI generativa
5. **Efficienza Operativa:** Ridurre il volume di email ripetitive con domande base

## 3. User Stories

**US1:** Come potenziale cliente (Mario), voglio capire rapidamente come funzionano i servizi Aidemy senza dover leggere tutto il sito, così posso decidere velocemente se approfondire il contatto.

**US2:** Come visitatore del sito, voglio conoscere i costi indicativi dei servizi Aidemy senza dover necessariamente chiamare, così posso valutare se rientrano nel mio budget.

**US3:** Come imprenditore interessato, voglio prenotare facilmente una call di Esplorazione Strategica direttamente dalla conversazione, così non devo navigare ulteriormente o inviare email.

**US4:** Come potenziale cliente, voglio ricevere materiali di approfondimento (case study, documentazione) via email, così posso valutare meglio i servizi offline.

**US5:** Come visitatore dubbioso, voglio vedere referenze e case study pertinenti alla mia situazione, così posso costruire fiducia in Aidemy.

## 4. Functional Requirements

### 4.1 Conversazione e Risposta

**FR1.1:** Il sistema DEVE rispondere alle seguenti domande frequenti basandosi sulla knowledge base:
- Come funzionano i servizi Aidemy?
- Devo fare tutti i pacchetti o posso partire da uno?
- Quali sono i costi indicativi?
- Quanto tempo serve per attivare un servizio?
- Operate in tutta Italia?
- Portate/implementate tecnologia?
- Serve un background specifico per lavorare con voi?
- Avete referenze o case study?

**FR1.2:** Il sistema DEVE mantenere il tono di voce del brand Aidemy: un angelo custode con elementi del mago (saggezza senza pedanteria, empatia diretta, autorevolezza informale)

**FR1.3:** Il sistema DEVE essere in grado di comprendere varianti delle domande frequenti e sinonimi

**FR1.4:** Il sistema DEVE citare le fonti quando fornisce informazioni dalla knowledge base

### 4.2 Qualificazione Lead

**FR2.1:** Il sistema DEVE raccogliere durante la conversazione:
- Nome
- Email
- Azienda (opzionale)
- Dimensione azienda (opzionale: <50, 50-250, >250 dipendenti)
- Sfida/bisogno principale
- Timeline prevista

**FR2.2:** Il sistema DEVE valutare implicitamente i criteri BANEC basandosi sulla conversazione:
- Budget (inferito da domande su costi e dimensione azienda)
- Autorità (inferita da ruolo e descrizione)
- Necessità (esplicitata nella sfida)
- Emergenza (inferita da timeline)
- Compatibilità (valutata dalla qualità della conversazione)

**FR2.3:** Il sistema DEVE assegnare un punteggio di qualificazione (caldo/tiepido/freddo) basato sui criteri BANEC

### 4.3 Prenotazione Call

**FR3.1:** Il sistema DEVE permettere di prenotare una call di Esplorazione Strategica direttamente dalla chat

**FR3.2:** Il sistema DEVE integrarsi con un calendario (Google Calendar di Jack, configurabile per Tidycal/Calendly) per proporre slot disponibili

**FR3.3:** Il sistema DEVE inviare conferma via email sia all'utente che a Jack dopo la prenotazione

**FR3.4:** Il sistema DEVE includere nella conferma:
- Data e ora dell'appuntamento
- Link videoconferenza
- Breve questionario preparatorio (se applicabile)

### 4.4 Invio Documentazione

**FR4.1:** Il sistema DEVE poter inviare via email:
- PDF di approfondimento sui servizi
- Case study rilevanti basati sulla conversazione
- One-pager Esplorazione Strategica

**FR4.2:** Il sistema DEVE chiedere conferma email prima dell'invio se non già raccolta

**FR4.3:** Il sistema DEVE tracciare quali materiali sono stati inviati a quale lead

### 4.5 Knowledge Base e RAG

**FR5.1:** Il sistema DEVE utilizzare come knowledge base:
- Descrizioni dei servizi (6 pacchetti core)
- Case study e progetti completati
- Articoli e contenuti formativi (newsletter Substack)
- FAQ strutturate (PR/FAQ)
- Metodologie (LEGO SERIOUS PLAY, Design Thinking, OKR, etc.)

**FR5.2:** Il sistema DEVE pre-processare i documenti tramite RAG con:
- Chunking semantico dei contenuti
- Embedding vettoriali per similarity search
- Metadata per filtraggio contestuale

**FR5.3:** Il sistema DEVE poter essere aggiornato con nuovi contenuti settimanalmente senza riavvio

**FR5.4:** Il sistema DEVE recuperare i 3-5 chunks più rilevanti per ogni query utente

### 4.6 Interfaccia Utente

**FR6.1:** Il chatbot DEVE apparire come widget in basso a destra del sito aidemy.it

**FR6.2:** Il widget DEVE:
- Essere minimizzabile
- Mostrare uno stato "typing" durante l'elaborazione
- Visualizzare avatar/icona del brand Aidemy
- Mostrare un badge di notifica se non ancora aperto

**FR6.3:** Il widget DEVE essere responsive e funzionare su mobile

**FR6.4:** L'interfaccia DEVE mostrare suggerimenti di domande frequenti all'avvio della conversazione

### 4.7 Integrazione n8n

**FR7.1:** L'intero sistema DEVE essere orchestrato tramite workflow n8n ospitati sulla VPS di Jack

**FR7.2:** Il sistema DEVE utilizzare OpenRouter come provider LLM con modello GPT-4o

**FR7.3:** Il sistema DEVE memorizzare:
- Conversazioni (per analisi e miglioramento)
- Lead qualificati (con punteggio BANEC)
- Metriche di utilizzo

**FR7.4:** Il sistema DEVE integrarsi con:
- Google Drive (per accesso knowledge base)
- Google Calendar (per booking, configurabile per Tidycal/Calendly)
- Email (per invio documentazione e notifiche)

## 5. Non-Goals (Out of Scope)

**NG1:** Trasferimento in tempo reale a operatore umano (feature fase 2)

**NG2:** Supporto a clienti esistenti su progetti in corso (feature fase 2)

**NG3:** Promozione proattiva di servizi specifici durante la conversazione (il bot risponde, non vende attivamente)

**NG4:** Educazione approfondita su concetti (feature fase 3)

**NG5:** Multi-lingua (solo italiano nella v1.0)

**NG6:** Integrazione con CRM esterno (per ora gestione manuale dei lead)

**NG7:** Chat vocale o video

## 6. Design Considerations

### 6.1 Tono di Voce

Il chatbot deve incarnare l'archetipo "Angelo Custode con elementi del Mago":

- **Angelo Custode:** Accogliente, rassicurante, orientato al benessere dell'utente
- **Mago:** Saggio ma non pedante, capace di rendere semplice il complesso
- **Voice traits:** 
  - Empatia diretta (non paternalismo)
  - Saggezza accessibile (non accademismo)
  - Autorevolezza informale (non imposizione)

### 6.2 Esempio di Interazione

```
Bot: Ciao! Sono l'assistente di Aidemy. Mi occupo di aiutare le organizzazioni 
a navigare il cambiamento. Come posso esserti utile oggi?

[Suggerimenti rapidi: "Come funzionano i vostri servizi?" | "Voglio prenotare una call" | "Avete case study?"]

User: Quanto costano i vostri servizi?

Bot: Ottima domanda! I nostri servizi sono progettati per essere accessibili e scalabili. 
Il punto d'ingresso più comune è l'Esplorazione Strategica, che parte da €1.500. 
Ti trasforma il disorientamento in chiarezza strategica in circa 2 settimane.

Da lì puoi scegliere percorsi più ampi (come la Pianificazione Strategica a €5.500) 
o interventi mirati (Decisioni Rapide da €800).

Vuoi che ti invii un PDF con i dettagli di tutti i pacchetti?
```

### 6.3 Visual Design

- **Colori:** Coerenti con brand Aidemy (da definire con materiali esistenti)
- **Avatar:** Icona rappresentativa dell'Angelo Custode/Mago
- **Typography:** Leggibile e professionale ma non fredda
- **Animazioni:** Sottili, non distraenti

## 7. Technical Considerations

### 7.1 Architettura Proposta

```
[Sito Aidemy.it] 
    ↓ (Widget Chat - Script JS)
[n8n Webhook] 
    ↓
[n8n Workflow Orchestration]
    ↓ ↙ ↘
[OpenRouter GPT-4o] [Qdrant Vector DB] [Google Services]
```

### 7.2 Stack Tecnologico

- **Frontend Widget:** Script JavaScript embeddabile
- **Backend Orchestration:** n8n (self-hosted su VPS)
- **LLM Provider:** OpenRouter (GPT-4o)
- **Vector Database:** Qdrant (Docker su VPS)
- **Knowledge Base:** Google Drive (fonte documentazione)
- **Storage Conversazioni:** Database PostgreSQL su VPS
- **Calendar:** Google Calendar API (configurabile per Tidycal/Calendly)
- **Email:** SMTP o SendGrid

### 7.3 Flusso RAG

1. **Preprocessing (settimanale via cron n8n):**
   - Estrazione documenti da Google Drive
   - Chunking semantico (500 token per chunk con overlap 50)
   - Generazione embeddings (OpenAI text-embedding-3-small)
   - Storage in Qdrant con metadata (tipo doc, data, categoria)

2. **Query time (per ogni domanda utente):**
   - Generazione embedding della query
   - Similarity search (top 3-5 chunks)
   - Context injection nel prompt LLM
   - Generazione risposta con citazioni

### 7.4 Prompt System (bozza)

```
Sei l'assistente AI di Aidemy, un consulente che aiuta le organizzazioni 
a navigare il cambiamento. Il tuo ruolo è qualificare lead e guidarli verso 
l'Esplorazione Strategica.

TONO: Angelo custode con elementi del mago - saggio ma accessibile, 
empatico ma non paternalistico, autorevole ma informale.

OBIETTIVI:
1. Rispondere alle domande sui servizi Aidemy
2. Qualificare il lead (raccogliere: nome, email, azienda, sfida, timeline)
3. Proporre prenotazione call Esplorazione Strategica quando appropriato

KNOWLEDGE BASE:
{retrieved_chunks}

CONVERSAZIONE PRECEDENTE:
{chat_history}

DOMANDA UTENTE:
{user_message}

Rispondi in modo naturale, cita le fonti quando usi la knowledge base, 
e guida gentilmente verso l'azione (prenotare call o ricevere materiali).
```

### 7.5 Integrazioni n8n

**Workflow principali da creare:**

1. **Chat Handler:** Gestisce messaggi in/out, mantiene stato conversazione
2. **RAG Processor:** Preprocessing documenti e similarity search
3. **Lead Qualifier:** Valuta conversazione e assegna punteggio BANEC
4. **Calendar Booking:** Integrazione Google Calendar per scheduling
5. **Email Sender:** Invio documentazione e notifiche
6. **Analytics Tracker:** Tracciamento metriche d'uso
7. **Knowledge Sync:** Cron job settimanale per aggiornamento knowledge base

## 8. Success Metrics

### 8.1 Metriche Primarie

**M1: Conversazioni Avviate**
- Target: 50+ conversazioni/mese entro 2 mesi
- Metrica: Numero di utenti che inviano almeno 1 messaggio

**M2: Call di Esplorazione Prenotate**
- Target: 10% conversion rate (conversazioni → call prenotate)
- Metrica: Numero di appuntamenti confermati via chatbot

### 8.2 Metriche Secondarie

**M3: Lead Qualificati**
- Target: 30+ lead "caldi" (punteggio BANEC >18) al mese
- Metrica: Numero di conversazioni con dati completi e alto score

**M4: Engagement Rate**
- Target: >5 messaggi per conversazione in media
- Metrica: Messaggi totali / conversazioni

**M5: Tempo Risposta**
- Target: <3 secondi per risposta
- Metrica: Latency media endpoint LLM + RAG

**M6: Satisfaction Score**
- Target: >80% feedback positivo
- Metrica: Pollice su/giù a fine conversazione (opzionale in v1)

### 8.3 Business Impact (stimato)

- Riduzione 50% email ripetitive su domande base
- Aumento 20% lead qualificati (rispetto a form statico)
- Riduzione 30% tempo Jack in chiamate explorative non qualificate

## 9. Decisioni Tecniche Finalizzate

### Risposte alle Open Questions

**Q1 - Modello LLM:** GPT-4o su OpenRouter
- **Rationale:** Bilanciamento ottimale tra qualità, latenza e costo

**Q2 - Vector Database:** Qdrant (Docker su VPS)
- **Rationale:** Ottimo balance tra performance, semplicità gestione e costo zero (self-hosted)

**Q3 - Sync Knowledge Base:** Cron job n8n settimanale
- **Rationale:** Automazione completa senza intervento manuale

**Q4 - Fallback senza risposta:** Escalation a Jack
- **Implementazione:** Messaggio "Non ho trovato info specifiche, vuoi che Jack ti contatti?" + salvataggio lead con flag escalated

**Q5 - Tracking pagine visitate:** No
- **Rationale:** Semplificazione MVP, analytics già presenti su landing

**Q6 - Hosting widget:** Script JS che comunica con n8n webhook
- **Rationale:** Massima flessibilità e semplicità embed

**Q7 - Moderazione input:** Nessun filtro preventivo
- **Rationale:** Fiducia negli utenti, possibilità monitoraggio post-hoc

**Q8 - GDPR/Privacy:** Già gestito sulla landing page esistente
- **Action:** Verificare che policy copra storage conversazioni

**Q9 - Analytics:** Già presenti sulla landing Landingi
- **Action:** Aggiungere eventi custom per tracking chatbot specifico

**Q10 - Calendario:** Parametro configurabile
- **Implementazione:** Google Calendar inizialmente, preparare per integrazione Tidycal/Calendly futura

## 10. Timeline e Roadmap

### Fase 1 - MVP (Target: 2 settimane)
**Obiettivo:** Chatbot funzionante con funzionalità core

**Features:**
- Widget chat embeddabile
- Conversazione con RAG su knowledge base
- Qualificazione lead base
- Prenotazione call via Google Calendar
- Invio documentazione via email

**Out of Scope MVP:**
- Dashboard analytics avanzata
- A/B testing widget
- Integrazione Tidycal/Calendly

### Fase 2 - Enhancement (Settimane 3-6)
**Features aggiuntive:**
- Supporto clienti esistenti su progetti
- Dashboard Grafana per metriche
- Ottimizzazioni performance
- A/B testing posizionamento widget

### Fase 3 - Advanced (Mesi 2-3)
**Features educative:**
- Content delivery educativo approfondito
- Multi-lingua (inglese)
- Integrazione CRM
- Voice/video capabilities (se ROI positivo)

## 11. Risks & Mitigation

### Risk 1: Qualità risposte insufficiente
- **Probabilità:** Media
- **Impatto:** Alto
- **Mitigazione:** Test approfondito prompt engineering, iterazione su feedback primi utenti, fallback escalation

### Risk 2: Latency >3 secondi
- **Probabilità:** Media
- **Impatto:** Medio
- **Mitigazione:** Caching chunks frequenti, ottimizzazione query Qdrant, upgrade VPS se necessario

### Risk 3: Costi OpenRouter eccessivi
- **Probabilità:** Bassa
- **Impatto:** Medio
- **Mitigazione:** Monitoring usage, rate limiting per user, switch a modello più economico se necessario

### Risk 4: Bassa adoption da utenti
- **Probabilità:** Media
- **Impatto:** Alto
- **Mitigazione:** A/B test posizionamento, ottimizzazione messaggio iniziale, promozione proattiva

### Risk 5: Privacy/GDPR issues
- **Probabilità:** Bassa
- **Impatto:** Alto
- **Mitigazione:** Review legale, data retention policy chiara, opt-in esplicito storage conversazioni

## 12. Next Steps

1. ✅ **PRD Approvato** da Jack
2. ✅ **Decisioni Tecniche Finalizzate**
3. ⏳ **Generazione Task List Dettagliata**
4. ⏳ **Setup Repository e Infrastruttura**
5. ⏳ **Sviluppo MVP (2 settimane)**
6. ⏳ **Testing e Deploy su Staging**
7. ⏳ **Deploy Produzione su Landingi**
8. ⏳ **Monitoring e Iterazione**

---

**Autore:** Claude (AI Assistant) + Jack Sabba Capetta  
**Data Creazione:** 2025-01-30  
**Ultima Modifica:** 2025-01-30  
**Versione:** 1.0 Final  
**Status:** Approved ✅
