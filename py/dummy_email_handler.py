"""
Dummy Email Handler - Simulates email inbox and responses
User sends email -> Bot processes -> Saves to dummy email file
"""

import json
from pathlib import Path
from datetime import datetime
import logging
from rag_pipeline import RAGPipeline
from utils import log_query, init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DummyEmailHandler:
    """Handle dummy email inbox and responses"""
    
    def __init__(self, inbox_file: str = "dummy_inbox.json", sent_file: str = "dummy_sent.json"):
        """
        Initialize dummy email handler
        
        Args:
            inbox_file: Path to inbox JSON file
            sent_file: Path to sent emails JSON file
        """
        self.inbox_file = Path(inbox_file)
        self.sent_file = Path(sent_file)
        self.rag = RAGPipeline()
        
        # Initialize database
        init_database()
        
        # Create empty files if they don't exist
        if not self.inbox_file.exists():
            self._save_json(self.inbox_file, [])
        if not self.sent_file.exists():
            self._save_json(self.sent_file, [])
    
    def _load_json(self, file_path: Path) -> list:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return []
    
    def _save_json(self, file_path: Path, data: list):
        """Save JSON data to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {str(e)}")
    
    def receive_email(self, sender: str, subject: str, body: str) -> dict:
        """
        Simulate receiving an email
        
        Args:
            sender: Sender email address
            subject: Email subject
            body: Email body
            
        Returns:
            Email data dictionary
        """
        email_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "sender": sender,
            "subject": subject,
            "body": body,
            "received_time": datetime.now().isoformat(),
            "status": "unread"
        }
        
        # Load inbox
        inbox = self._load_json(self.inbox_file)
        inbox.append(email_data)
        self._save_json(self.inbox_file, inbox)
        
        logger.info(f"Received email from {sender}: {subject}")
        return email_data
    
    def get_unread_emails(self) -> list:
        """Get all unread emails"""
        inbox = self._load_json(self.inbox_file)
        return [email for email in inbox if email.get("status") == "unread"]
    
    def process_email(self, email_id: str) -> dict:
        """
        Process an email and generate response
        
        Args:
            email_id: Email ID to process
            
        Returns:
            Response data dictionary
        """
        # Load inbox
        inbox = self._load_json(self.inbox_file)
        
        # Find email
        email_data = None
        for email in inbox:
            if email["id"] == email_id:
                email_data = email
                break
        
        if not email_data:
            logger.error(f"Email {email_id} not found")
            return None
        
        # Generate response
        query = f"{email_data['subject']}\n{email_data['body']}"
        response, metadata = self.rag.generate_response(query)
        
        # Log query
        log_query(
            query_type="email",
            query_text=query,
            response=response,
            source="dummy_email",
            email_sender=email_data['sender']
        )
        
        # Create response email
        response_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "to": email_data['sender'],
            "subject": f"Re: {email_data['subject']}",
            "body": response,
            "original_query": email_data['body'],
            "sent_time": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Save to sent folder
        sent = self._load_json(self.sent_file)
        sent.append(response_data)
        self._save_json(self.sent_file, sent)
        
        # Mark as read
        for email in inbox:
            if email["id"] == email_id:
                email["status"] = "read"
                email["processed_time"] = datetime.now().isoformat()
                break
        self._save_json(self.inbox_file, inbox)
        
        logger.info(f"Processed and responded to email from {email_data['sender']}")
        return response_data
    
    def process_all_unread(self) -> dict:
        """
        Process all unread emails
        
        Returns:
            Processing results dictionary
        """
        unread = self.get_unread_emails()
        results = {
            "total": len(unread),
            "successful": 0,
            "failed": 0,
            "responses": []
        }
        
        for email in unread:
            try:
                response = self.process_email(email["id"])
                if response:
                    results["successful"] += 1
                    results["responses"].append(response)
                else:
                    results["failed"] += 1
            except Exception as e:
                results["failed"] += 1
                logger.error(f"Error processing email {email['id']}: {str(e)}")
        
        logger.info(f"Processed {results['successful']}/{results['total']} emails")
        return results
    
    def get_all_inbox(self) -> list:
        """Get all inbox emails"""
        return self._load_json(self.inbox_file)
    
    def get_all_sent(self) -> list:
        """Get all sent emails"""
        return self._load_json(self.sent_file)
    
    def view_email(self, email_id: str, email_type: str = "inbox") -> dict:
        """
        View a specific email
        
        Args:
            email_id: Email ID
            email_type: 'inbox' or 'sent'
            
        Returns:
            Email data or None
        """
        file = self.inbox_file if email_type == "inbox" else self.sent_file
        emails = self._load_json(file)
        
        for email in emails:
            if email["id"] == email_id:
                return email
        
        return None


# CLI interface
def main():
    """Main CLI interface for dummy email handler"""
    handler = DummyEmailHandler()
    
    print("\n" + "="*60)
    print("DUMMY EMAIL SYSTEM - Customer Support Bot")
    print("="*60)
    
    while True:
        print("\n1. Send a new email (as user)")
        print("2. View inbox")
        print("3. View sent emails (bot responses)")
        print("4. Process all unread emails")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n--- Send New Email ---")
            sender = input("Your email address: ").strip()
            subject = input("Subject: ").strip()
            print("Body (press Enter twice to finish):")
            body_lines = []
            while True:
                line = input()
                if line == "":
                    break
                body_lines.append(line)
            body = "\n".join(body_lines)
            
            email_data = handler.receive_email(sender, subject, body)
            print(f"\n✅ Email sent! ID: {email_data['id']}")
            print("Bot will process this automatically...")
            
            # Auto-process
            response = handler.process_email(email_data['id'])
            if response:
                print(f"\n🤖 Bot Response:")
                print(f"To: {response['to']}")
                print(f"Subject: {response['subject']}")
                print(f"\n{response['body']}")
        
        elif choice == "2":
            inbox = handler.get_all_inbox()
            if not inbox:
                print("\n📭 Inbox is empty")
            else:
                print(f"\n📬 Inbox ({len(inbox)} emails):")
                for email in inbox:
                    status = "✉️ " if email['status'] == 'unread' else "📖"
                    print(f"\n{status} ID: {email['id']}")
                    print(f"   From: {email['sender']}")
                    print(f"   Subject: {email['subject']}")
                    print(f"   Time: {email['received_time']}")
                    print(f"   Status: {email['status']}")
        
        elif choice == "3":
            sent = handler.get_all_sent()
            if not sent:
                print("\n📭 No sent emails")
            else:
                print(f"\n📤 Sent Emails ({len(sent)} responses):")
                for email in sent:
                    print(f"\n📧 ID: {email['id']}")
                    print(f"   To: {email['to']}")
                    print(f"   Subject: {email['subject']}")
                    print(f"   Time: {email['sent_time']}")
                    print(f"   Response: {email['body'][:100]}...")
        
        elif choice == "4":
            print("\n🤖 Processing all unread emails...")
            results = handler.process_all_unread()
            print(f"\n✅ Processed: {results['successful']}/{results['total']}")
            if results['failed'] > 0:
                print(f"❌ Failed: {results['failed']}")
        
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
