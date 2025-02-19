import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def send_email(subject, body, attachment_paths=None):
    """Sends an email with multiple attachments using SendGrid."""
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=RECIPIENT_EMAIL,
        subject=subject,
        html_content=body,
    )

    if attachment_paths:
        for attachment_path in attachment_paths:
            with open(attachment_path, "rb") as f:
                encoded_file = base64.b64encode(f.read()).decode()
            attachment = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(attachment_path)),
                FileType("application/octet-stream"),
                Disposition("attachment"),
            )
            message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent successfully! Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")
