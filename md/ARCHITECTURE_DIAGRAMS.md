# 🎯 System Architecture & Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHATBOT SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │  USER INTERFACES │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
          ┌─────────▼────┐  ┌────▼──────┐  ┌───▼──────┐
          │ STREAMLIT    │  │  GMAIL    │  │ ANALYTICS│
          │ WEB CHAT     │  │  INBOX    │  │DASHBOARD │
          └────────┬─────┘  └────┬──────┘  └──────────┘
                   │             │
                   └─────────────┬──────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   CHATBOT APPLICATION   │
                    │  (chatbot_app.py)       │
                    │  (email_handler.py)     │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │    RAG PIPELINE         │
                    │  (rag_pipeline.py)      │
                    │                         │
                    │ • Embedding Gen         │
                    │ • Similarity Search     │
                    │ • Response Gen          │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   DATA & STORAGE        │
                    │                         │
                    │ • Vector DB (pickle)    │
                    │ • Query Logs (SQLite)   │
                    │ • Case Data (CSV)       │
                    └─────────────────────────┘

                    ┌─────────────────────────┐
                    │  BACKGROUND SERVICE     │
                    │ (email_service.py)      │
                    │                         │
                    │ • Email Monitoring      │
                    │ • Response Sending      │
                    │ • Error Handling        │
                    └─────────────────────────┘
```

---

## Chat Query Flow

```
User Types Question
    │
    ▼
┌─────────────────────────────┐
│ STREAMLIT INTERFACE         │
│ (chatbot_app.py)            │
│ Display in chat              │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│ RAG PIPELINE                │
│ (rag_pipeline.py)           │
└────────────┬────────────────┘
             │
             ├─ Generate embedding of query
             │
             ├─ Load pre-computed embeddings
             │  from pickle file
             │
             ├─ Calculate similarity scores
             │  (cosine similarity)
             │
             ├─ Get top-3 similar cases
             │
             ├─ Generate response with
             │  context from best case
             │
             └─ Return response + metadata
                     │
                     ▼
         ┌──────────────────────┐
         │ Display response in  │
         │ chat interface       │
         │ Show confidence      │
         │ Show related cases   │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Log to database      │
         │ (utils.py)           │
         │ • query_logs         │
         │ • metadata           │
         │ • timestamp          │
         └──────────────────────┘
```

---

## Email Query Flow

```
Customer Sends Email
    │
    ▼ (to Gmail inbox)
┌────────────────────────────┐
│ GMAIL INBOX (IMAP)         │
│ (Gmail Server)             │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ EMAIL SERVICE              │
│ (email_service.py)         │
│ • Runs every 60 seconds    │
│ • Checks for unread mail   │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ EMAIL HANDLER              │
│ (email_handler.py)         │
│                            │
│ 1. Connect to IMAP         │
│ 2. Fetch unread emails     │
│ 3. Parse message           │
│    - Extract sender        │
│    - Extract subject       │
│    - Extract body          │
│ 4. Mark as read            │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ RAG PIPELINE               │
│ (rag_pipeline.py)          │
│                            │
│ Process query through      │
│ semantic search            │
│ Generate response          │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ SMTP EMAIL SENDER          │
│ (email_handler.py)         │
│                            │
│ 1. Create MIME message     │
│ 2. Add HTML template       │
│ 3. Include original query  │
│ 4. Send via SMTP           │
│ 5. Handle errors           │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Response Email Sent        │
│ Back to Customer           │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ DATABASE LOGGING           │
│ (utils.py)                 │
│ • Email tracking           │
│ • Query logs               │
│ • Response records         │
└────────────────────────────┘
```

---

## Data Flow Architecture

```
┌──────────────────────────────────────────────────────┐
│            INPUT DATA SOURCES                        │
└────┬─────────────────────────────────────────────────┘
     │
     ├─ CSV File (preprocessed_bitext_casesS.csv)
     │  └─ 17,134 support cases with descriptions
     │
     └─ User Queries (via Web or Email)
        └─ Real-time customer questions

        ┌──────────────────────────────────┐
        │  PROCESSING LAYER                │
        └────┬─────────────────────────────┘
             │
             ├─ Embedding Generation
             │  └─ Sentence Transformers (all-MiniLM-L6-v2)
             │
             ├─ Similarity Calculation
             │  └─ Cosine similarity between vectors
             │
             ├─ Case Retrieval
             │  └─ Top-K most similar cases
             │
             └─ Response Generation
                └─ Context-aware responses

        ┌──────────────────────────────────┐
        │  STORAGE LAYER                   │
        └────┬─────────────────────────────┘
             │
             ├─ Vector Database
             │  └─ bitext_cases_with_embeddings.pkl
             │     └─ Pre-computed 384-dim vectors
             │
             ├─ Query Logs Database
             │  └─ chatbot_logs.db (SQLite)
             │     ├─ query_logs (all queries)
             │     ├─ email_tracking (email status)
             │     └─ user_feedback (ratings)
             │
             └─ Case Data
                └─ preprocessed_bitext_casesS.csv
                   └─ Product, description, resolution

        ┌──────────────────────────────────┐
        │  OUTPUT DELIVERY                 │
        └────┬─────────────────────────────┘
             │
             ├─ Web Interface
             │  └─ Streamlit chat display
             │
             ├─ Email Response
             │  └─ HTML formatted email
             │
             └─ Analytics
                └─ Dashboard with statistics
```

---

## Component Dependencies

```
┌─────────────────────────────────────────────┐
│        DEPENDENCY GRAPH                     │
└─────────────────────────────────────────────┘

chatbot_app.py (Main Interface)
    ├─ imports: rag_pipeline.py
    ├─ imports: utils.py
    └─ imports: streamlit, pandas, numpy

email_service.py (Background Service)
    ├─ imports: email_handler.py
    ├─ imports: utils.py
    └─ imports: schedule

email_handler.py (Email Processing)
    ├─ imports: rag_pipeline.py
    ├─ imports: utils.py
    └─ imports: imaplib, smtplib, email

rag_pipeline.py (RAG Logic)
    ├─ imports: pandas, numpy
    ├─ imports: sentence_transformers
    ├─ imports: sklearn.metrics.pairwise
    └─ uses: bitext_cases_with_embeddings.pkl

utils.py (Database & Utils)
    ├─ imports: sqlite3, json
    └─ creates: chatbot_logs.db

Configuration:
    └─ chatbot_config.json (read by all modules)

Data Files:
    ├─ preprocessed_bitext_casesS.csv
    ├─ bitext_cases_with_embeddings.pkl
    └─ chatbot_logs.db
```

---

## Database Schema

```
┌────────────────────────────────────────┐
│       CHATBOT_LOGS.DB (SQLite)        │
└────────────────────────────────────────┘

TABLE: query_logs
┌────────────────────────────────────────┐
│ id (PRIMARY KEY)                       │
│ timestamp (AUTO)                       │
│ query_type (TEXT): 'chat'/'email'      │
│ query_text (TEXT)                      │
│ response (TEXT)                        │
│ source (TEXT): 'streamlit'/'email'     │
│ email_sender (TEXT): sender if email   │
│ user_rating (INT): 1-5 rating          │
│ feedback (TEXT): user feedback         │
│ case_ids (TEXT): JSON array            │
│ confidence_score (REAL): 0-1           │
└────────────────────────────────────────┘

TABLE: email_tracking
┌────────────────────────────────────────┐
│ id (PRIMARY KEY)                       │
│ timestamp (AUTO)                       │
│ sender_email (TEXT)                    │
│ subject (TEXT)                         │
│ status (TEXT)                          │
│ response_sent (BOOLEAN)                │
│ error_message (TEXT)                   │
└────────────────────────────────────────┘

TABLE: user_feedback
┌────────────────────────────────────────┐
│ id (PRIMARY KEY)                       │
│ timestamp (AUTO)                       │
│ query_id (FOREIGN KEY)                 │
│ rating (INT): 1-5                      │
│ feedback_text (TEXT)                   │
└────────────────────────────────────────┘
```

---

## Configuration Hierarchy

```
Default Config (hardcoded in code)
        │
        ▼
┌──────────────────────────────────────┐
│   chatbot_config.json                │
│   (JSON file on disk)                │
│                                      │
│   • top_k: 3                         │
│   • similarity_threshold: 0.5        │
│   • gmail_address: ""                │
│   • gmail_app_password: ""           │
│   • smtp_server: smtp.gmail.com      │
│   • smtp_port: 587                   │
│   • db_path: chatbot_logs.db        │
│   • max_email_check_interval: 60    │
│   • enable_email_service: true      │
└──────────────────────────────────────┘
        │
        ▼
Streamlit Settings Page
(UI override for some settings)
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│            DEPLOYMENT OPTIONS                       │
└──────┬──────────────────────────────────────────────┘
       │
       ├─ LOCAL DEVELOPMENT
       │  └─ python chatbot_app.py
       │     streamlit run chatbot_app.py
       │
       ├─ STREAMLIT CLOUD
       │  └─ streamlit run chatbot_app.py
       │     (hosted on share.streamlit.io)
       │
       ├─ DOCKER + CLOUD RUN (GCP)
       │  └─ Dockerfile
       │     └─ GCP Cloud Run
       │
       ├─ DOCKER + EC2 (AWS)
       │  └─ Dockerfile
       │     ├─ EC2 Instance
       │     └─ Nginx Reverse Proxy
       │
       └─ SELF-HOSTED
          ├─ Background Service (systemd)
          ├─ Web Server (Streamlit)
          ├─ Email Service (scheduler)
          └─ Database (SQLite/PostgreSQL)

Background Services:
    ├─ Email Service (email_service.py)
    │  └─ Runs continuously or scheduled
    │
    ├─ Web Interface (chatbot_app.py)
    │  └─ Streamlit server
    │
    └─ Optional: Web API (future)
       └─ FastAPI wrapper
```

---

## Similarity Search Visualization

```
User Query: "How do I cancel my order?"
           │
           ▼
       EMBEDDING
    [384 dimensions]
           │
           ▼
   ┌─────────────────────┐
   │ VECTOR DATABASE     │
   │ (all 17,134 cases)  │
   │                     │
   │ [case_1 embedding]  │ ─ similarity: 0.89
   │ [case_2 embedding]  │ ─ similarity: 0.85
   │ [case_3 embedding]  │ ─ similarity: 0.82
   │ [case_4 embedding]  │ ─ similarity: 0.71
   │ ... (more cases)    │ ─ similarity: 0.x
   └─────────────────────┘
           │
           ▼
   ┌─────────────────────────────┐
   │ TOP-K RETRIEVAL (k=3)       │
   │                             │
   │ 1. Case #1234 (0.89) ✓      │
   │ 2. Case #5678 (0.85) ✓      │
   │ 3. Case #9012 (0.82) ✓      │
   │                             │
   │ Threshold: 0.50             │
   │ All passed: YES             │
   └─────────────────────────────┘
           │
           ▼
   ┌─────────────────────────────┐
   │ EXTRACT RESOLUTION TEXT     │
   │ FROM TOP CASES              │
   │                             │
   │ "To cancel order:           │
   │  1. Go to Orders            │
   │  2. Click Cancel            │
   │  3. Confirm cancellation"   │
   └─────────────────────────────┘
           │
           ▼
   Display Response to User
```

---

## Timing Diagram

```
┌──────────────────────────────────────────────────────┐
│         USER INTERACTION TIMELINE                    │
└──────────────────────────────────────────────────────┘

Chat Query Path:
────────────────
[User Types] ─┐
              ├─→ [Load RAG] (cached) ~100ms
              │
              ├─→ [Encode Query] ~50ms
              │
              ├─→ [Search Embeddings] ~100ms
              │
              ├─→ [Generate Response] ~50ms
              │
              ├─→ [Log to DB] ~10ms
              │
              └─→ [Display Response] ~50ms
                  TOTAL: ~300-500ms

Email Processing Path:
──────────────────────
[Email Received] ─┐
                  ├─→ [Check Email] (every 60s)
                  │
                  ├─→ [Parse Email] ~20ms
                  │
                  ├─→ [RAG Pipeline] ~300-500ms
                  │
                  ├─→ [Send SMTP] ~500-1000ms
                  │
                  ├─→ [Log Results] ~10ms
                  │
                  └─→ [Mark Read] ~10ms
                      TOTAL: ~1-2 seconds
```

---

## Scalability Considerations

```
┌─────────────────────────────────────────┐
│    CURRENT CAPACITY & BOTTLENECKS       │
└─────────────────────────────────────────┘

✓ Small Scale (Single Server)
  ├─ Up to 1,000 queries/day
  ├─ 17,134 cases in DB
  ├─ ~500ms response time
  └─ 1-2GB RAM usage

⚠ Medium Scale (Optimization Needed)
  ├─ 10,000+ queries/day
  ├─ Add caching (embeddings in RAM)
  ├─ Use GPU for faster encoding
  └─ Database indexing

⚠ Large Scale (Infrastructure)
  ├─ 100,000+ queries/day
  ├─ Load balancing (multiple instances)
  ├─ Distributed cache (Redis)
  ├─ Cloud DB (PostgreSQL with pgvector)
  └─ Message queue (for emails)

Bottlenecks (in order):
  1. Embedding generation (~50% of time)
  2. Database writes (~10%)
  3. Network requests (~15%)
  4. Email sending (~25%)
```

---

## Security Architecture

```
┌──────────────────────────────────────────┐
│         SECURITY LAYERS                  │
└──────────────────────────────────────────┘

Input Validation
├─ Email parsing validation
├─ Query text sanitization
└─ Database query parameterization

Authentication
├─ Gmail App Password (not account password)
├─ OAuth 2.0 for Gmail API (optional future)
└─ TLS/SSL for all connections

Data Protection
├─ IMAP4_SSL for Gmail connection
├─ SMTP TLS for email sending
├─ No credentials in code/logs
└─ Database file permissions

Access Control
├─ Anyone can send emails (by design)
├─ Configurable via email address filter
└─ Optional: IP whitelist for web interface

Logging & Monitoring
├─ All queries logged
├─ Email activities tracked
├─ Error logging
└─ No sensitive data in logs
```

---

## Performance Metrics

```
┌─────────────────────────────────────────────┐
│        KEY PERFORMANCE INDICATORS           │
└─────────────────────────────────────────────┘

Response Time:
├─ Chat Query: 300-500ms
├─ Email Processing: 1-2 seconds
└─ RAG Pipeline: 200-400ms

Throughput:
├─ Concurrent Chat Users: 10-50
├─ Emails/minute: 1-10
└─ Queries/day: 100-5,000

Resource Usage:
├─ Memory: 200-500MB normal
├─ CPU: <5% idle, 20-40% under load
├─ Disk: 100MB+ for database
└─ Network: <1MB per query

Reliability:
├─ Uptime Target: 99.5%
├─ Error Rate: <1%
├─ Email Success Rate: >98%
└─ Data Backup: Daily
```

---

## This diagram-based documentation helps visualize:
✓ System architecture
✓ Data flows (chat vs email)
✓ Component dependencies
✓ Database schema
✓ Configuration hierarchy
✓ Deployment options
✓ Similarity search process
✓ Timeline/performance
✓ Scalability planning
✓ Security layers
✓ Performance metrics

---

**Visual Architecture Documentation Created** ✅
