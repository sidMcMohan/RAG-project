"""
Streamlit Chatbot
Main Streamlit application for the chatbot UI
"""

import streamlit as st
import pickle
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime
from pathlib import Path
import sqlite3
from rag_pipeline import RAGPipeline
from utils import init_database, log_query

# Page configuration
st.set_page_config(
    page_title="Customer Support Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI - minimal styling without boxes
st.markdown("""
    <style>
    header { visibility: hidden; }
    .block-container {
        padding-top: 0.5rem;
    }
    .main {
        padding: -1rem 0rem;
    }
    .chat-row {
        display: flex;
        width: 100%;
        margin: 0rem 0;
    }
    .chat-row.user {
        justify-content: flex-start;
    }
    .chat-row.bot {
        justify-content: flex-start;
    }
    .chat-bubble {
        max-width: 75%;
        padding: 0rem;
        border-radius: 0px;
        background: transparent;
        color: inherit;
    }
    .stChatMessage {
        background-color: transparent !important;
        padding: 0rem;
        border-radius: 0px;
        margin: 0rem 0;
    }
    .label-blue {
        color: #1f77b4;
        font-weight: 500;
    }
    p {
        margin-bottom: 0.25rem !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag_pipeline():
    """Load RAG pipeline with cached embeddings and model"""
    return RAGPipeline()

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False

def display_chat_history():
    """Display chat history without boxes"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<span class='label-blue'>👤 **User**</span>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='chat-row user'><div class='chat-bubble'>{message['content']}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"<span class='label-blue'>⊙ **Bot**</span>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='chat-row bot'><div class='chat-bubble'>{message['content']}</div></div>",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Mode selection
    mode = st.sidebar.radio(
        "",
        ["💬 Chat Interface", "📊 Analytics", "🔧 Settings"],
        index=0
    )
    
    st.markdown("# RAG Based Dataset")

    if mode == "💬 Chat Interface":
        display_chat_interface()
    elif mode == "📊 Analytics":
        display_analytics()
    elif mode == "🔧 Settings":
        display_settings()

def display_chat_interface():
    """Display main chat interface"""
    # Load RAG pipeline
    rag = load_rag_pipeline()
    
    # Display chat history
    display_chat_history()
    
    # Chat input (fixed at bottom like typical chat apps)
    if st.session_state.clear_input:
        st.session_state.user_input = ""
        st.session_state.clear_input = False

    user_input = st.chat_input("Type your question or issue...")

    # Process user input
    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response
        with st.spinner("🔍 Searching for solution..."):
            response, metadata = rag.generate_response(user_input)
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "metadata": metadata
        })
        
        # Log query
        st.session_state.query_count += 1
        log_query(
            query_type="chat",
            query_text=user_input,
            response=response,
            source="streamlit"
        )
        st.session_state.clear_input = True
        st.rerun()


def display_analytics():
    """Display analytics dashboard"""
    st.subheader("📊 Query Analytics")
    
    db_path = Path("chatbot_logs.db")
    if not db_path.exists():
        st.info("No query logs available yet.")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        
        # Total queries
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_queries = pd.read_sql("SELECT COUNT(*) as count FROM query_logs", conn)
            st.metric("Total Queries", total_queries['count'].values[0])
        
        with col2:
            chat_queries = pd.read_sql(
                "SELECT COUNT(*) as count FROM query_logs WHERE source='streamlit'",
                conn
            )
            st.metric("Chat Queries", chat_queries['count'].values[0])
        
        with col3:
            email_queries = pd.read_sql(
                "SELECT COUNT(*) as count FROM query_logs WHERE source='email'",
                conn
            )
            st.metric("Email Queries", email_queries['count'].values[0])
        
        with col4:
            avg_rating = pd.read_sql(
                "SELECT AVG(user_rating) as avg FROM query_logs WHERE user_rating > 0",
                conn
            )
            st.metric("Avg Rating", f"{avg_rating['avg'].values[0]:.2f}" if avg_rating['avg'].values[0] else "N/A")
        
        st.markdown("---")
        
        # Query timeline
        st.subheader("Query Timeline")
        timeline_data = pd.read_sql(
            "SELECT DATE(timestamp) as date, COUNT(*) as count FROM query_logs GROUP BY DATE(timestamp) ORDER BY date DESC LIMIT 30",
            conn
        )
        
        if not timeline_data.empty:
            st.area_chart(timeline_data.set_index('date'))
        
        # Query sources
        st.subheader("Query Sources")
        source_data = pd.read_sql(
            "SELECT source, COUNT(*) as count FROM query_logs GROUP BY source",
            conn
        )
        
        if not source_data.empty:
            st.bar_chart(source_data.set_index('source'))
        
        # Recent queries
        st.subheader("Recent Queries")
        recent = pd.read_sql(
            "SELECT timestamp, query_text, source, user_rating FROM query_logs ORDER BY timestamp DESC LIMIT 20",
            conn
        )
        st.dataframe(recent, use_container_width=True)
        
        conn.close()
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def display_settings():
    """Display settings page"""
    st.subheader("⚙️ Chatbot Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### RAG Pipeline Settings")
        top_k = st.slider("Top K Similar Cases", 1, 10, 3)
        
    if st.button("Save Settings", use_container_width=True):
        settings = {
            "top_k": top_k,
            "db_path": "chatbot_logs.db"
        }
        
        with open("chatbot_config.json", "w") as f:
            json.dump(settings, f, indent=2)
        
        st.success("✅ Settings saved successfully!")

if __name__ == "__main__":
    main()
