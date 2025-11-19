# email_tool.py
import os
import smtplib
from email.message import EmailMessage
from livekit.agents import function_tool
import logging

# Logger setup
logger = logging.getLogger(__name__)

@function_tool
async def send_email(recipient_email: str, subject: str, body: str) -> str:
    """
    Sends an email to a specified recipient.
    Use this when a user asks to send an email, mail, or message.
    You must ask the user for the recipient's email, the subject, and the body of the message.
    Example: "Send an email to john.doe@example.com with the subject 'Hello' and body 'How are you?'"
    """
    logger.info(f"Attempting to send email to {recipient_email}")

    # Environment variables se email aur password lo
    sender_email = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not app_password:
        logger.error("Email credentials (EMAIL_SENDER, EMAIL_PASSWORD) are not set.")
        return "Sorry, the email sending function is not configured. Please set the environment variables."

    try:
        # Email message ko aache se format karo
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Gmail ke server se connect karke email bhejo
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Connection ko secure karo
            server.login(sender_email, app_password)
            server.send_message(msg)
        
        logger.info(f"Email successfully sent to {recipient_email}")
        return f"Okay, I have successfully sent the email to {recipient_email}."

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return f"Sorry, I encountered an error while sending the email: {e}"