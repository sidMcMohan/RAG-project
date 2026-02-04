# 🚀 Deployment Guide

Complete guide for deploying the chatbot to production environments.

## Deployment Options

### Option 1: Streamlit Cloud (Easiest)

**Best for:** Small teams, quick deployment, low traffic

#### Steps:
1. **Prepare GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial chatbot commit"
   git push -u origin main
   ```

2. **Create Streamlit Cloud Account**
   - Visit https://share.streamlit.io
   - Click "Deploy an app"
   - Select your GitHub repository

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to Secrets
   - Add your Gmail credentials:
   ```toml
   [gmail]
   address = "your-email@gmail.com"
   app_password = "your-16-char-app-password"
   ```

4. **Update Configuration**
   - Modify `chatbot_app.py` to read from secrets:
   ```python
   gmail_address = st.secrets.gmail.address
   gmail_app_password = st.secrets.gmail.app_password
   ```

5. **Deploy**
   - Click "Deploy" button
   - App will be live at `https://your-username-chatbot.streamlit.app`

**Cost:** Free tier available, paid tiers from $5/month

---

### Option 2: Docker + Cloud Run (Google Cloud)

**Best for:** Scalable deployment, enterprise features

#### Prerequisites
- Google Cloud account
- Docker installed locally
- gcloud CLI installed

#### Steps:

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   ENV STREAMLIT_SERVER_PORT=8501
   ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ENV STREAMLIT_SERVER_HEADLESS=true
   
   CMD ["streamlit", "run", "chatbot_app.py"]
   ```

2. **Build Docker Image**
   ```bash
   docker build -t chatbot:latest .
   
   # Test locally
   docker run -p 8501:8501 chatbot:latest
   ```

3. **Push to Google Container Registry**
   ```bash
   gcloud auth configure-docker
   docker tag chatbot:latest gcr.io/YOUR-PROJECT/chatbot:latest
   docker push gcr.io/YOUR-PROJECT/chatbot:latest
   ```

4. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy chatbot \
     --image gcr.io/YOUR-PROJECT/chatbot:latest \
     --platform managed \
     --region us-central1 \
     --memory 2Gi \
     --set-env-vars GMAIL_ADDRESS=your-email@gmail.com,GMAIL_APP_PASSWORD=your-password
   ```

5. **Configure Background Email Service**
   - Deploy `email_service.py` as Cloud Scheduler job
   - Or use Cloud Tasks

**Cost:** $0.25/month base + compute charges (usually $5-50/month)

---

### Option 3: Docker + AWS EC2 (Traditional Server)

**Best for:** Full control, complex deployments

#### Steps:

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Inbound rules: 80, 443, 22

2. **SSH into Server**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

4. **Clone Repository**
   ```bash
   git clone your-repo-url
   cd chatbot
   ```

5. **Build and Run**
   ```bash
   docker build -t chatbot .
   docker run -d -p 80:8501 \
     -e GMAIL_ADDRESS=your-email@gmail.com \
     -e GMAIL_APP_PASSWORD=your-password \
     --name chatbot \
     chatbot
   ```

6. **Setup Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Setup Background Service**
   ```bash
   # Create systemd service for email processing
   sudo tee /etc/systemd/system/chatbot-email.service << EOF
   [Unit]
   Description=Chatbot Email Service
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/chatbot
   ExecStart=/usr/bin/python3 /home/ubuntu/chatbot/email_service.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   sudo systemctl enable chatbot-email
   sudo systemctl start chatbot-email
   ```

**Cost:** $5-30/month depending on instance type

---

### Option 4: Heroku (Deprecated alternative)

**Note:** Heroku free tier ended in 2022. Consider alternatives above.

---

### Option 5: Local Server with Ngrok (Testing)

**Best for:** Testing, demonstrations

```bash
# Install ngrok from https://ngrok.com

# Start chatbot
streamlit run chatbot_app.py &

# Create public URL
ngrok http 8501

# Share the generated URL with others
```

---

## Production Checklist

### Security
- [ ] Enable HTTPS/SSL certificate
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets (never commit passwords)
- [ ] Enable CORS if needed
- [ ] Set up firewall rules
- [ ] Regular security updates

### Performance
- [ ] Use caching for embeddings
- [ ] Implement database indexing
- [ ] Set up CDN if using static assets
- [ ] Monitor API response times
- [ ] Set up auto-scaling if needed

### Monitoring
- [ ] Set up application logging
- [ ] Monitor error rates
- [ ] Track response times
- [ ] Monitor email service uptime
- [ ] Set up alerts for failures

### Backup & Recovery
- [ ] Daily database backups
- [ ] Version control all code
- [ ] Document deployment procedures
- [ ] Test disaster recovery

### Email Service
- [ ] Run as separate service/container
- [ ] Implement error retry logic
- [ ] Monitor email queue
- [ ] Set up alerting for failures
- [ ] Test with real Gmail account

---

## Configuration for Production

Edit `chatbot_config.json`:

```json
{
  "top_k": 3,
  "similarity_threshold": 0.5,
  "gmail_address": "support@yourcompany.com",
  "gmail_app_password": "your-app-password",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "db_path": "chatbot_logs.db",
  "max_email_check_interval": 30,
  "enable_email_service": true
}
```

Or use environment variables (recommended for production):

```bash
export CHATBOT_GMAIL_ADDRESS="support@yourcompany.com"
export CHATBOT_GMAIL_PASSWORD="your-app-password"
export CHATBOT_TOP_K="3"
export CHATBOT_SIMILARITY_THRESHOLD="0.5"
```

---

## Monitoring & Logging

### Docker Logs
```bash
docker logs chatbot
docker logs chatbot -f  # Follow logs in real-time
```

### Application Logs
```bash
tail -f email_handler.log
tail -f email_service.log
```

### Database Queries
```bash
# Check query volume
sqlite3 chatbot_logs.db "SELECT COUNT(*) as total_queries FROM query_logs;"

# Check by source
sqlite3 chatbot_logs.db "SELECT source, COUNT(*) FROM query_logs GROUP BY source;"

# Export for analysis
sqlite3 chatbot_logs.db ".headers on" ".mode csv" "SELECT * FROM query_logs;" > queries.csv
```

### Email Service Status
```bash
# Check recent email processing
sqlite3 chatbot_logs.db "SELECT * FROM email_tracking ORDER BY timestamp DESC LIMIT 10;"

# Failed emails
sqlite3 chatbot_logs.db "SELECT * FROM email_tracking WHERE status='failed';"
```

---

## Scaling Considerations

### Horizontal Scaling (Multiple Instances)
1. Use load balancer (nginx, HAProxy)
2. Share database (same `chatbot_logs.db` or cloud database)
3. Share embeddings file or cache in memory
4. Run single instance of email service (or with locks)

### Vertical Scaling (Single Instance)
1. Increase machine resources (RAM, CPU)
2. Use GPU for faster embeddings
3. Cache more data in memory
4. Optimize database queries

### Database Optimization
```sql
-- Add indexes for faster queries
CREATE INDEX idx_source ON query_logs(source);
CREATE INDEX idx_timestamp ON query_logs(timestamp);
CREATE INDEX idx_email_sender ON query_logs(email_sender);
```

---

## Troubleshooting Deployments

### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501
# Kill process
kill -9 <PID>
```

### Out of Memory
```bash
# Check memory usage
free -h
docker stats

# Increase available memory or optimize code
```

### Email Service Not Working
1. Check Gmail credentials
2. Verify IMAP is enabled
3. Check firewall allows port 993/587
4. Review `email_handler.log`

### Database Locked
```bash
# Rebuild database
sqlite3 chatbot_logs.db "VACUUM;"
sqlite3 chatbot_logs.db "PRAGMA optimize;"
```

---

## Cost Comparison

| Platform | Setup | Monthly | Per Query |
|----------|-------|---------|-----------|
| Streamlit Cloud | Free | $5-20 | ~$0 |
| Google Cloud Run | Free | $10-50 | ~$0.001 |
| AWS EC2 | Free | $10-30 | ~$0 |
| Heroku | Free | N/A | N/A |
| Self-hosted | Cost varies | $50+ | ~$0 |

---

## Next Steps

1. Choose deployment platform based on your needs
2. Follow the setup instructions
3. Test thoroughly before going live
4. Set up monitoring and alerts
5. Document your deployment process
6. Plan for scaling as you grow

---

**Ready to deploy?** Choose your platform and follow the detailed steps above!
