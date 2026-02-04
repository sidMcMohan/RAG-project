# 📂 Project Directory Structure

## Complete File Listing

```
ff2/
│
├─ 🎯 CORE APPLICATION FILES
│  ├─ chatbot_app.py                    [Main Streamlit Application]
│  │  ├─ Chat Interface
│  │  ├─ Analytics Dashboard
│  │  ├─ Settings Management
│  │  └─ Session State Management
│  │
│  ├─ rag_pipeline.py                   [RAG Pipeline Implementation]
│  │  ├─ Case Retrieval
│  │  ├─ Similarity Search
│  │  ├─ Response Generation
│  │  └─ Embedding Management
│  │
│  ├─ email_handler.py                  [Email Processing]
│  │  ├─ IMAP Gmail Integration
│  │  ├─ Email Parsing
│  │  ├─ SMTP Response Sending
│  │  └─ Error Handling
│  │
│  ├─ email_service.py                  [Background Email Service]
│  │  ├─ Continuous Monitoring
│  │  ├─ Scheduled Checking
│  │  └─ Error Handling
│  │
│  └─ utils.py                          [Database & Utilities]
│     ├─ Database Operations
│     ├─ Logging Functions
│     ├─ Query Statistics
│     └─ Configuration Management
│
├─ 📊 DATA FILES
│  ├─ preprocessed_bitext_casesS.csv    [17,134 Support Cases]
│  │  └─ Columns: case_number, product_name, description, resolution
│  │
│  ├─ bitext_cases_with_embeddings.pkl  [Pre-computed Embeddings]
│  │  └─ 384-dimensional vectors for 17,134 cases
│  │
│  ├─ chatbot_config.json               [Configuration (Auto-created)]
│  │  ├─ Gmail Credentials
│  │  ├─ RAG Settings
│  │  └─ Service Configuration
│  │
│  └─ chatbot_logs.db                   [SQLite Database (Auto-created)]
│     ├─ query_logs table
│     ├─ email_tracking table
│     └─ user_feedback table
│
├─ 📖 DOCUMENTATION FILES
│  ├─ README.md                         [Complete Documentation]
│  │  ├─ Features
│  │  ├─ Installation
│  │  ├─ Configuration
│  │  ├─ Usage Guide
│  │  ├─ Troubleshooting
│  │  ├─ Database Schema
│  │  ├─ API Reference
│  │  └─ Deployment Guide
│  │
│  ├─ QUICK_START.md                    [5-Minute Setup Guide]
│  │  ├─ Installation Steps
│  │  ├─ Email Setup
│  │  ├─ Running Commands
│  │  └─ Troubleshooting
│  │
│  ├─ DEPLOYMENT.md                     [Production Deployment]
│  │  ├─ Streamlit Cloud
│  │  ├─ Google Cloud Run
│  │  ├─ AWS EC2
│  │  ├─ Docker Setup
│  │  ├─ Monitoring
│  │  └─ Scaling Guide
│  │
│  ├─ IMPLEMENTATION_SUMMARY.md          [Feature Checklist]
│  │  ├─ All 20 Features
│  │  ├─ File Mapping
│  │  ├─ Workflow Diagrams
│  │  ├─ Configuration Guide
│  │  └─ Testing Checklist
│  │
│  ├─ ARCHITECTURE_DIAGRAMS.md          [Visual Documentation]
│  │  ├─ System Overview
│  │  ├─ Data Flow Diagrams
│  │  ├─ Component Dependencies
│  │  ├─ Database Schema
│  │  └─ Performance Metrics
│  │
│  ├─ PROJECT_DELIVERABLES.md           [Project Overview]
│  │  ├─ File Descriptions
│  │  ├─ Feature Mapping
│  │  ├─ Quick Reference
│  │  └─ Next Steps
│  │
│  └─ DIRECTORY_TREE.txt                [This File]
│     └─ Complete structure overview
│
├─ 🚀 SETUP & TESTING FILES
│  ├─ requirements.txt                  [Python Dependencies]
│  │  └─ 8 packages for full functionality
│  │
│  ├─ test_system.py                    [System Testing]
│  │  ├─ Dependency Testing
│  │  ├─ Data Validation
│  │  ├─ RAG Pipeline Test
│  │  ├─ Database Test
│  │  └─ Comprehensive Report
│  │
│  └─ SETUP.bat                         [Windows One-Click Setup]
│     ├─ Dependency Installation
│     ├─ Database Initialization
│     ├─ System Testing
│     └─ Next Steps
│
├─ 📝 LOG FILES (Auto-created)
│  ├─ email_handler.log                 [Email Processing Logs]
│  │  └─ IMAP/SMTP operations, errors
│  │
│  └─ email_service.log                 [Background Service Logs]
│     └─ Scheduled checks, results
│
└─ 📋 OPTIONAL FILES
   ├─ run_email_service.bat             [Windows batch file]
   │  └─ For Task Scheduler integration
   │
   ├─ Dockerfile                        [Container definition]
   │  └─ For Docker deployment
   │
   ├─ docker-compose.yml                [Multi-container setup]
   │  └─ For local testing
   │
   └─ .github/workflows/                [GitHub Actions]
      └─ CI/CD automation (optional)
```

---

## File Count Summary

| Category | Count | Purpose |
|----------|-------|---------|
| Application | 5 | Core chatbot logic |
| Data | 4 | Case data + embeddings |
| Documentation | 7 | Complete guides |
| Setup/Testing | 3 | Installation & validation |
| Logs | 2 | Runtime logging |
| **TOTAL** | **21** | **Complete system** |

---

## File Sizes (Approximate)

| File | Size | Type |
|------|------|------|
| chatbot_app.py | ~12 KB | Python |
| rag_pipeline.py | ~8 KB | Python |
| email_handler.py | ~10 KB | Python |
| email_service.py | ~7 KB | Python |
| utils.py | ~8 KB | Python |
| requirements.txt | <1 KB | Text |
| test_system.py | ~10 KB | Python |
| SETUP.bat | <1 KB | Batch |
| README.md | ~30 KB | Markdown |
| QUICK_START.md | ~5 KB | Markdown |
| DEPLOYMENT.md | ~20 KB | Markdown |
| IMPLEMENTATION_SUMMARY.md | ~15 KB | Markdown |
| ARCHITECTURE_DIAGRAMS.md | ~25 KB | Markdown |
| PROJECT_DELIVERABLES.md | ~15 KB | Markdown |
| preprocessed_bitext_casesS.csv | ~2.5 MB | CSV |
| bitext_cases_with_embeddings.pkl | ~25 MB | Pickle |
| **TOTAL** | **~2.7 GB** | **Complete** |

---

## Dependencies Tree

```
chatbot_app.py
├── streamlit              (UI framework)
├── pandas                 (Data handling)
├── numpy                  (Numerical computing)
├── rag_pipeline           (RAG logic)
├── utils                  (Database functions)
└── json                   (Configuration)

rag_pipeline.py
├── pickle                 (Load embeddings)
├── pandas                 (Data processing)
├── numpy                  (Vector operations)
├── sentence_transformers  (Embeddings)
├── sklearn.metrics        (Similarity)
└── json                   (Configuration)

email_handler.py
├── imaplib                (Gmail IMAP)
├── smtplib                (Gmail SMTP)
├── email                  (Email parsing)
├── json                   (Configuration)
├── rag_pipeline           (Query processing)
└── utils                  (Database logging)

email_service.py
├── schedule               (Periodic tasks)
├── email_handler          (Email operations)
├── utils                  (Database functions)
└── json                   (Configuration)

utils.py
├── sqlite3                (Database)
├── json                   (Configuration)
└── datetime               (Timestamps)
```

---

## Data Flow Dependencies

```
User Input (Chat or Email)
    ↓
chatbot_app.py or email_handler.py
    ↓
rag_pipeline.py
    ↓
    ├─ Load: bitext_cases_with_embeddings.pkl
    ├─ Use: sentence_transformers model
    └─ Return: response + metadata
    ↓
Database (via utils.py)
    ↓
Store in: chatbot_logs.db
```

---

## Configuration Dependency

```
chatbot_config.json
    ↓
    ├─ Read by: rag_pipeline.py
    ├─ Read by: email_handler.py
    ├─ Read by: email_service.py
    ├─ Read by: chatbot_app.py
    └─ Updated by: chatbot_app.py (Settings page)
```

---

## Startup Sequence

```
1. python chatbot_app.py  OR  streamlit run chatbot_app.py
   ├─ Load config from chatbot_config.json
   ├─ Initialize session state
   ├─ Load RAG pipeline (cached)
   │  ├─ Load model (all-MiniLM-L6-v2)
   │  ├─ Load embeddings from pickle
   │  └─ Load CSV data
   ├─ Initialize database
   └─ Display UI

2. python email_service.py
   ├─ Load config
   ├─ Initialize database
   ├─ Create scheduler
   ├─ Schedule email checks
   └─ Wait for scheduled events
   
3. When event triggers:
   ├─ email_handler.py runs
   ├─ Connect to Gmail (IMAP)
   ├─ Process unread emails
   ├─ Run RAG pipeline
   ├─ Send responses (SMTP)
   └─ Log results
```

---

## Key Directories

### Application Directory
```
ff2/
├── Core Python files (5 files)
├── Configuration files (1 file)
└── Data files (3 large files)
```

### Documentation Directory (within ff2/)
```
docs/ (conceptual - all in root)
├── README.md                   (Main guide)
├── QUICK_START.md              (Setup guide)
├── DEPLOYMENT.md               (Prod deployment)
└── ARCHITECTURE_DIAGRAMS.md    (Visual reference)
```

### Data Directory (within ff2/)
```
data/ (conceptual - all in root)
├── preprocessed_bitext_casesS.csv
├── bitext_cases_with_embeddings.pkl
└── chatbot_logs.db (created)
```

---

## File Modification Timeline

```
Initial Setup:
├─ 1. Run SETUP.bat
│  └─ Creates: chatbot_config.json, chatbot_logs.db
│
├─ 2. Run chatbot_app.py
│  └─ Creates: None (reads existing files)
│
└─ 3. Run email_service.py
   └─ Creates: email_handler.log, email_service.log

During Operation:
├─ chatbot_logs.db (grows with each query)
├─ email_handler.log (appends logs)
├─ email_service.log (appends logs)
└─ chatbot_config.json (updated when settings change)
```

---

## File Permissions Recommended

```
Python Files (read/execute):
├─ chatbot_app.py          (755)
├─ rag_pipeline.py         (755)
├─ email_handler.py        (755)
├─ email_service.py        (755)
├─ utils.py                (755)
└─ test_system.py          (755)

Data Files (read-only):
├─ preprocessed_bitext_casesS.csv  (644)
└─ bitext_cases_with_embeddings.pkl (644)

Config/Database (read/write):
├─ chatbot_config.json     (644) - contains passwords
└─ chatbot_logs.db         (644) - user data

Documentation (read-only):
├─ *.md files              (644)
└─ requirements.txt        (644)
```

---

## Total Project Statistics

| Metric | Value |
|--------|-------|
| Python Files | 5 |
| Data Files | 3 |
| Documentation | 7 |
| Setup/Test Files | 3 |
| Total Code Lines | ~1,500 |
| Total Doc Lines | ~3,000 |
| CSV Rows | 17,134 |
| Embeddings | 384-dim × 17,134 |
| Database Tables | 3 |

---

## This Directory Structure Provides:

✅ Clear organization
✅ Easy navigation
✅ Scalable structure
✅ Documentation at root level
✅ Data files co-located
✅ All necessary tools included

---

**Directory Structure**: ✅ Complete and Organized
**All Files**: ✅ Created and Documented
**Ready for**: ✅ Deployment
