# 🤖 AI-Powered Customer Support Chatbot with Email Integration

A comprehensive Streamlit-based chatbot that handles customer support queries via both web interface and email using RAG (Retrieval-Augmented Generation) pipeline.

## 📋 Features

### Chat Interface
- **Web-based UI** using Streamlit
- **Real-time chat** with support agent responses
- **RAG Pipeline** for intelligent case retrieval
- **Similarity Search** using semantic embeddings
- **Case Information Display** showing related historical cases
- **Chat History** management and clearing

### Email Integration
- **IMAP Support** for receiving queries from any Gmail address
- **SMTP Support** for automated response sending
- **Email Parsing** to extract content and sender information
- **HTML Email Templates** with formatted responses
- **Error Handling** and logging for email operations

### Data Management
- **SQLite Database** for query logging
- **User Feedback Collection** (1-5 rating system)
- **Email Tracking** and status monitoring
- **Analytics Dashboard** with query statistics and visualization
- **Data Export** to JSON format

### RAG Pipeline
- **Semantic Search** using Sentence Transformers
- **Pre-computed Embeddings** stored in pickle format
- **Configurable Similarity Threshold**
- **Top-K Case Retrieval**
- **Confidence Scoring**

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd ff2

# Install dependencies
pip install -r requirements.txt
```

### 2. Initial Setup

```bash
# Run setup script to initialize database and config
python utils.py
```

This creates:
- `chatbot_logs.db` - SQLite database for logging
- `chatbot_config.json` - Configuration template

### 3. Configure Gmail for Email Support

#### Generate Gmail App Password

1. Enable 2-Factor Authentication on your Gmail account
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. Generate App Password
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your device)
   - Copy the generated password

#### Update Configuration

Edit `chatbot_config.json`:

```json
{
  "top_k": 3,
  "similarity_threshold": 0.5,
  "gmail_address": "your-email@gmail.com",
  "gmail_app_password": "your-16-character-app-password",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "db_path": "chatbot_logs.db",
  "max_email_check_interval": 60,
  "enable_email_service": true
}
```

### 4. Run the Chatbot

#### Option A: Streamlit Web Interface

```bash
streamlit run chatbot_app.py
```

The app will open at `http://localhost:8501`

#### Option B: Email Service (Background)

```bash
python email_service.py
```

#### Option C: Manual Email Check

```bash
python email_handler.py
```

## 📁 Project Structure

```
ff2/
├── chatbot_app.py              # Main Streamlit application
├── rag_pipeline.py             # RAG pipeline implementation
├── email_handler.py            # Email processing logic
├── email_service.py            # Background email service
├── utils.py                    # Database and utility functions
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── preprocessed_bitext_casesS.csv    # Case data
├── bitext_cases_with_embeddings.pkl  # Pre-computed embeddings
├── chatbot_config.json         # Configuration (created on setup)
├── chatbot_logs.db            # SQLite database (created on first run)
├── email_handler.log          # Email service logs
└── email_service.log          # Background service logs
```

## 🎯 Usage Guide

### Chat Interface

1. **Start the app:**
   ```bash
   streamlit run chatbot_app.py
   ```

2. **Ask a question:**
   - Type your customer support question
   - Click "Send" button
   - View the AI-generated response with confidence level

3. **View Related Cases:**
   - Click "📚 Related Case Information" expander
   - See similar historical cases that helped generate the response

4. **Manage Chat:**
   - Click "🗑️ Clear History" to start fresh
   - History is stored in session state

### Email Interface

1. **Send Email Query:**
   - Send email to the configured Gmail address (any sender)
   - Subject and body are processed as one query
   - Response is automatically sent within the configured interval

2. **Email Processing:**
   - Service checks for unread emails every `max_email_check_interval` seconds
   - Processes queries through RAG pipeline
   - Sends formatted HTML response back to sender
   - Marks emails as read after processing

3. **Run Email Service:**
   ```bash
   # Option 1: Run once
   python email_handler.py
   
   # Option 2: Run as continuous service
   python email_service.py
   ```

### Analytics Dashboard

1. Open Streamlit app and navigate to **"📊 Analytics"**
2. View:
   - Total queries count
   - Chat vs Email breakdown
   - Average user rating
   - Query timeline graph
   - Source distribution
   - Recent queries list

### Settings

Navigate to **"🔧 Settings"** to:
- Adjust Top-K similar cases (1-10)
- Set similarity threshold (0.0-1.0)
- Update email credentials
- Modify SMTP settings
- Configure database path

## 🔧 Configuration Details

### RAG Pipeline Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `top_k` | Number of similar cases to retrieve | 3 |
| `similarity_threshold` | Minimum similarity score (0-1) | 0.5 |

### Email Settings

| Setting | Description | Required |
|---------|-------------|----------|
| `gmail_address` | Gmail inbox for receiving queries | Yes |
| `gmail_app_password` | 16-char app password from Gmail | Yes |
| `smtp_server` | SMTP server address | smtp.gmail.com |
| `smtp_port` | SMTP port number | 587 |
| `enable_email_service` | Enable email processing | true |
| `max_email_check_interval` | Seconds between email checks | 60 |

## 📊 Database Schema

### query_logs
```sql
id              - Unique query identifier
timestamp       - Query timestamp
query_type      - 'chat' or 'email'
query_text      - User's question
response        - Generated response
source          - 'streamlit' or 'email'
email_sender    - Sender email (if applicable)
user_rating     - User rating (1-5)
feedback        - User feedback text
case_ids        - JSON array of used case IDs
confidence_score - Response confidence (0-1)
```

### email_tracking
```sql
id              - Unique identifier
timestamp       - Processing timestamp
sender_email    - Email sender
subject         - Email subject
status          - Processing status
response_sent   - Whether response was sent
error_message   - Any error details
```

### user_feedback
```sql
id              - Unique identifier
timestamp       - Feedback timestamp
query_id        - Related query ID
rating          - User rating (1-5)
feedback_text   - Feedback text
```

## 🐛 Troubleshooting

### Issue: "Gmail login failed"
**Solution:** 
- Ensure 2FA is enabled on Gmail account
- Use 16-character app password (not account password)
- Check internet connection

### Issue: "IMAP connection error"
**Solution:**
- Verify Gmail address is correct
- Ensure "Less secure apps" is disabled (use app passwords)
- Check firewall settings allowing port 993

### Issue: "No embeddings found"
**Solution:**
- Ensure `bitext_cases_with_embeddings.pkl` exists
- Run embedding generation if file is missing
- Check CSV file is in the correct directory

### Issue: "Response takes too long"
**Solution:**
- Reduce `top_k` value in settings
- Increase `similarity_threshold` to filter cases
- Check available system memory

## 📈 Performance Optimization

### For Faster Responses:
1. Reduce `top_k` from 3 to 1-2
2. Increase `similarity_threshold` to 0.6-0.7
3. Use GPU (CUDA) if available
4. Consider caching embeddings in memory

### For Better Accuracy:
1. Increase `top_k` to 5
2. Lower `similarity_threshold` to 0.3-0.4
3. Add more training data to CSV
4. Regenerate embeddings with updated data

## 🔐 Security Considerations

1. **Gmail Credentials:**
   - Never commit `chatbot_config.json` to version control
   - Use environment variables for production
   - Rotate app passwords periodically

2. **Database:**
   - Backup `chatbot_logs.db` regularly
   - Restrict file permissions
   - Consider encryption for sensitive data

3. **Email:**
   - Validate sender addresses if needed
   - Implement rate limiting
   - Log all email operations

## 📦 Deployment

### Local Development
```bash
streamlit run chatbot_app.py
```

### Windows Task Scheduler

1. Create batch file `run_email_service.bat`:
```batch
@echo off
cd /path/to/ff2
python email_service.py
```

2. Open Task Scheduler:
   - Create Basic Task
   - Set trigger (e.g., daily at 9 AM)
   - Set action to run the batch file

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "chatbot_app.py"]
```

### Cloud Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Visit https://share.streamlit.io
3. Deploy from repository
4. Set secrets in Streamlit Cloud dashboard

### Production Services

For production, consider:
- Running email service as systemd service on Linux
- Using process manager like PM2 or Supervisor
- Implementing proper logging and monitoring
- Setting up alerts for failures

## 🔄 Workflow Examples

### Example 1: Customer Asks Via Chat
1. User types: "How do I cancel my order?"
2. RAG pipeline retrieves 3 most similar cases
3. Generates response with confidence score
4. Displays related case information
5. Logs query and response to database

### Example 2: Customer Emails Support
1. Customer sends email: "Cancellation help needed"
2. Email service checks inbox every 60 seconds
3. Finds unread email and processes it
4. RAG pipeline generates response
5. Sends HTML formatted email response
6. Marks email as read and logs interaction

### Example 3: Analytics Review
1. Support manager opens Streamlit app
2. Navigates to Analytics dashboard
3. Views query trends over time
4. Checks average customer satisfaction rating
5. Identifies top issues based on query frequency
6. Exports logs to JSON for reporting

## 📝 Logging

### Log Files
- `email_handler.log` - Email processing logs
- `email_service.log` - Background service logs
- `chatbot_logs.db` - Query database

### View Logs
```bash
# Recent email handler logs
tail -f email_handler.log

# Search for errors
grep "ERROR" email_handler.log
```

## 🤝 Contributing

To add new features:

1. **New data sources:** Update `rag_pipeline.py` to handle additional data
2. **New communication channels:** Create new handler similar to `email_handler.py`
3. **Custom analytics:** Add charts to `display_analytics()` in `chatbot_app.py`
4. **Custom responses:** Modify `_construct_response()` in `rag_pipeline.py`

## 📚 API Reference

### RAGPipeline

```python
from rag_pipeline import RAGPipeline

rag = RAGPipeline()

# Retrieve similar cases
cases = rag.retrieve_similar_cases("How to cancel order?", top_k=3)

# Generate full response
response, metadata = rag.generate_response("How to cancel order?")
```

### EmailQueryHandler

```python
from email_handler import EmailQueryHandler

handler = EmailQueryHandler()

# Fetch and process all emails
results = handler.process_all_emails()

# Send custom response
handler.send_email_response(
    recipient="user@example.com",
    subject="Your Question",
    body="Response text",
    original_query="Original question"
)
```

### Database Functions

```python
from utils import log_query, log_user_feedback, get_query_stats

# Log a query
query_id = log_query(
    query_type="chat",
    query_text="User question",
    response="AI response"
)

# Log user feedback
log_user_feedback(query_id, rating=5, feedback_text="Great help!")

# Get statistics
stats = get_query_stats()
```

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in `email_handler.log` and `email_service.log`
3. Check database with: `sqlite3 chatbot_logs.db`

## 📄 License

This project is provided as-is for customer support applications.

## 🎉 Key Achievements

✅ Full-featured Streamlit chatbot interface
✅ Automatic email query processing
✅ Comprehensive logging and analytics
✅ RAG pipeline with semantic search
✅ Multi-source query handling (web + email)
✅ User feedback collection system
✅ Production-ready code structure
✅ Easy configuration management

---

**Last Updated:** January 2026
**Version:** 1.0.0
