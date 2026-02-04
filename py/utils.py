"""
Utility functions for database logging and configuration
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

DB_PATH = "chatbot_logs.db"


def init_database(db_path: str = DB_PATH):
    """
    Initialize SQLite database for logging queries
    
    Args:
        db_path: Path to database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create query logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query_type TEXT NOT NULL,
            query_text TEXT NOT NULL,
            response TEXT,
            source TEXT,
            email_sender TEXT,
            user_rating INTEGER DEFAULT 0,
            feedback TEXT,
            case_ids TEXT,
            confidence_score REAL
        )
    """)
    
    # Create email tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender_email TEXT NOT NULL,
            subject TEXT,
            status TEXT,
            response_sent BOOLEAN DEFAULT 0,
            error_message TEXT
        )
    """)
    
    # Create feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query_id INTEGER,
            rating INTEGER,
            feedback_text TEXT,
            FOREIGN KEY (query_id) REFERENCES query_logs(id)
        )
    """)
    
    conn.commit()
    conn.close()


def log_query(
    query_type: str,
    query_text: str,
    response: str,
    source: str = "streamlit",
    email_sender: Optional[str] = None,
    case_ids: Optional[list] = None,
    confidence_score: Optional[float] = None,
    db_path: str = DB_PATH
) -> int:
    """
    Log a query to database
    
    Args:
        query_type: Type of query ('chat' or 'email')
        query_text: User's query text
        response: Generated response
        source: Source of query ('streamlit' or 'email')
        email_sender: Email sender address (if applicable)
        case_ids: List of case IDs used in response
        confidence_score: Confidence score of response
        db_path: Path to database
        
    Returns:
        ID of inserted log entry
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    case_ids_str = json.dumps(case_ids) if case_ids else None
    
    cursor.execute("""
        INSERT INTO query_logs
        (query_type, query_text, response, source, email_sender, case_ids, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (query_type, query_text, response, source, email_sender, case_ids_str, confidence_score))
    
    conn.commit()
    query_id = cursor.lastrowid
    conn.close()
    
    return query_id


def log_user_feedback(query_id: int, rating: int, feedback_text: str = "", db_path: str = DB_PATH):
    """
    Log user feedback for a query
    
    Args:
        query_id: ID of the query
        rating: User rating (1-5)
        feedback_text: Optional feedback text
        db_path: Path to database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_feedback (query_id, rating, feedback_text)
        VALUES (?, ?, ?)
    """, (query_id, rating, feedback_text))
    
    # Update rating in query_logs
    cursor.execute("""
        UPDATE query_logs SET user_rating = ? WHERE id = ?
    """, (rating, query_id))
    
    conn.commit()
    conn.close()


def log_email_tracking(
    sender_email: str,
    subject: str,
    status: str,
    response_sent: bool = False,
    error_message: str = None,
    db_path: str = DB_PATH
):
    """
    Log email tracking information
    
    Args:
        sender_email: Sender's email address
        subject: Email subject
        status: Processing status
        response_sent: Whether response was sent
        error_message: Any error message
        db_path: Path to database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO email_tracking (sender_email, subject, status, response_sent, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (sender_email, subject, response_sent, error_message))
    
    conn.commit()
    conn.close()


def get_query_stats(db_path: str = DB_PATH) -> Dict:
    """
    Get overall query statistics
    
    Args:
        db_path: Path to database
        
    Returns:
        Dictionary with statistics
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total queries
    cursor.execute("SELECT COUNT(*) FROM query_logs")
    stats['total_queries'] = cursor.fetchone()[0]
    
    # Chat vs Email
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE source='streamlit'")
    stats['chat_queries'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE source='email'")
    stats['email_queries'] = cursor.fetchone()[0]
    
    # Average rating
    cursor.execute("SELECT AVG(user_rating) FROM query_logs WHERE user_rating > 0")
    avg_rating = cursor.fetchone()[0]
    stats['avg_rating'] = round(avg_rating, 2) if avg_rating else 0
    
    # Rated queries
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE user_rating > 0")
    stats['rated_queries'] = cursor.fetchone()[0]
    
    conn.close()
    
    return stats


def export_logs(output_path: str = "query_logs.json", db_path: str = DB_PATH):
    """
    Export query logs to JSON file
    
    Args:
        output_path: Path to output JSON file
        db_path: Path to database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM query_logs ORDER BY timestamp DESC")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    logs = []
    for row in rows:
        log_dict = dict(zip(columns, row))
        log_dict['timestamp'] = str(log_dict['timestamp'])
        logs.append(log_dict)
    
    conn.close()
    
    with open(output_path, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Logs exported to {output_path}")


def create_config_template(config_path: str = "chatbot_config.json"):
    """
    Create a template configuration file
    
    Args:
        config_path: Path to configuration file
    """
    config = {
        "top_k": 3,
        "similarity_threshold": 0.5,
        "gmail_address": "your-email@gmail.com",
        "gmail_app_password": "your-app-password",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "db_path": "chatbot_logs.db",
        "max_email_check_interval": 60,
        "enable_email_service": True
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration template created at {config_path}")
    print("Please update the configuration with your Gmail credentials.")


if __name__ == "__main__":
    # Initialize database and create config template
    init_database()
    create_config_template()
    print("Setup complete!")
