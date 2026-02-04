# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize System
```bash
python utils.py
```

This creates:
- `chatbot_logs.db` - Query database
- `chatbot_config.json` - Configuration file

### Step 3: Verify Installation
```bash
python test_system.py
```

You should see all tests pass with ✅

### Step 4: Run the Chatbot
```bash
streamlit run chatbot_app.py
```

Open your browser to `http://localhost:8501` and start chatting!

---

## Email Setup (Optional - 5 more minutes)

### Get Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" → "Windows Computer"
5. Copy the 16-character password

### Configure Chatbot
1. Open `chatbot_config.json`
2. Update:
```json
{
  "gmail_address": "your-email@gmail.com",
  "gmail_app_password": "paste-16-char-password-here",
  "enable_email_service": true
}
```

### Start Email Service
```bash
python email_service.py
```

---

## Using the Chatbot

### Via Web
1. Open http://localhost:8501
2. Type your question
3. Click "Send"
4. View AI-generated response with related cases

### Via Email
1. Send an email to your configured Gmail address
2. Email service checks every 60 seconds
3. Response sent automatically

### View Analytics
1. Open Streamlit app
2. Select "📊 Analytics" 
3. See all your queries and statistics

---

## Common Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Port 8501 in use | Run `streamlit run chatbot_app.py --server.port 8502` |
| Gmail login fails | Check app password, enable 2FA |
| No similar cases found | Increase similarity threshold in Settings |

---

## Project Structure
```
chatbot_app.py          ← Run this to start web interface
email_handler.py        ← Run once to process emails
email_service.py        ← Run to check emails continuously
rag_pipeline.py         ← RAG logic (imported by other files)
utils.py                ← Database & helpers (imported by other files)
chatbot_config.json     ← Edit for configuration
chatbot_logs.db         ← Your query database
preprocessed_bitext_casesS.csv  ← Your case data
bitext_cases_with_embeddings.pkl ← Pre-computed embeddings
```

---

## Next Steps

1. **Customize responses** - Edit `rag_pipeline.py` → `_construct_response()`
2. **Add more data** - Update CSV file and regenerate embeddings
3. **Deploy to cloud** - Follow README.md deployment section
4. **Monitor queries** - Check Analytics tab regularly
5. **Collect feedback** - Users can rate responses (1-5 stars)

---

## Commands Reference

```bash
# Start web chatbot
streamlit run chatbot_app.py

# Process emails once
python email_handler.py

# Run email service continuously
python email_service.py

# Run system tests
python test_system.py

# Export query logs
sqlite3 chatbot_logs.db "SELECT * FROM query_logs" > queries.csv
```

---

**Questions?** See full README.md for detailed documentation.
