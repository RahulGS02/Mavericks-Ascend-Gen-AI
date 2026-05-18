"""
Email service for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        # In production, use environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "noreply@maverick.com"
        self.sender_password = ""  # Set via env var
        
    async def send_approval_email(self, to_email: str, name: str) -> bool:
        """Send approval notification email"""
        subject = "🎉 Congratulations! Your Maverick Profile is Approved"
        
        body = f"""
        <html>
        <body>
            <h2>Hi {name},</h2>
            <p>Great news! Your profile has been <strong>approved</strong> by our HR team.</p>
            <p>You are now eligible for upcoming training batches and deployment opportunities.</p>
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Keep your profile updated</li>
                <li>Watch out for training batch announcements</li>
                <li>Check your dashboard regularly</li>
            </ul>
            <p>Best regards,<br>Maverick Insights Team</p>
        </body>
        </html>
        """
        
        return await self._send_email(to_email, subject, body)
    
    async def send_rejection_email(self, to_email: str, name: str, reason: str = None) -> bool:
        """Send rejection notification email"""
        subject = "Update on Your Maverick Profile"
        
        reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        body = f"""
        <html>
        <body>
            <h2>Hi {name},</h2>
            <p>Thank you for your interest in joining Maverick Insights.</p>
            <p>After careful review, we regret to inform you that your profile has not been approved at this time.</p>
            {reason_text}
            <p>We encourage you to:</p>
            <ul>
                <li>Gain more experience in relevant technologies</li>
                <li>Enhance your skills</li>
                <li>Reapply in the future</li>
            </ul>
            <p>Best of luck in your career journey!<br>Maverick Insights Team</p>
        </body>
        </html>
        """
        
        return await self._send_email(to_email, subject, body)
    
    async def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Internal method to send email"""
        try:
            # For development/testing, just log the email
            logger.info(f"📧 EMAIL SENT to {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body preview: {body[:100]}...")
            
            # In production, uncomment this to actually send emails:
            # msg = MIMEMultipart('alternative')
            # msg['Subject'] = subject
            # msg['From'] = self.sender_email
            # msg['To'] = to_email
            # 
            # html_part = MIMEText(body, 'html')
            # msg.attach(html_part)
            # 
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.sender_email, self.sender_password)
            #     server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
