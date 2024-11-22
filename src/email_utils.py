# import os
# import logging
# from typing import Union

# from fastapi import HTTPException, status
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
# from pathlib import Path
# from dotenv import load_dotenv
# from security.jwt import create_url_safe_token
# from email_validator import validate_email, EmailNotValidError

# # Initialize logging
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# # Get environment variables
# MAIL_USERNAME = os.getenv('MAIL_USERNAME')
# MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
# MAIL_FROM = os.getenv('MAIL_FROM')
# SSL_PREFIX = os.getenv('SSL_PREFIX')
# FRONTEND_URL = os.getenv('FRONTEND_URL')

# # Base directory for templates
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Mail configuration
# config = ConnectionConfig(
#     MAIL_USERNAME=MAIL_USERNAME,
#     MAIL_PASSWORD=MAIL_PASSWORD,
#     MAIL_FROM=MAIL_FROM,
#     MAIL_PORT=465,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True
# )


# def validate_recipients(recipients):
#     for recipient in recipients:
#         try:
#             validate_email(recipient)
#         except EmailNotValidError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid email address: {recipient}"
#             )

# class SmtpMailService:
#     def __init__(self, recipients: Union[str, list[str]], mail: FastMail = FastMail(config)):
#         """
#         Initialize the SMTP Mail Service.

#         :param recipients: Single recipient email or a list of email addresses.
#         :param mail: FastMail instance for sending emails.
#         """
#         self.recipients = [recipients] if isinstance(recipients, str) else recipients
#         self.mail = mail

#     def create_token(self, email: str) -> str:
#         """
#         Create a URL-safe token for email verification.

#         :param email: Email address to encode in the token.
#         :return: Encoded token.
#         """
#         logger.info("Creating token for %s", email)
#         return create_url_safe_token({"email": email})

#     async def send_email(self, subject: str, body: str) -> None:
#         """
#         Send an email to the configured recipients.

#         :param subject: Email subject.
#         :param body: Email body in HTML format.
#         """
#         logger.info("Sending email to %s", self.recipients)
#         message = MessageSchema(
#             subject=subject,
#             recipients=self.recipients,
#             body=body,
#             subtype="html"
#         )
#         try:
#             await self.mail.send_message(message)
#             logger.info("Email sent successfully to %s", self.recipients)
#         except Exception as e:
#             logger.error("Failed to send email: %s", e)
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to send email"
#             )

#     async def send_tvl_email(self) -> None:
#         """
#         Send a TVL verification email to the configured recipients.
#         """
#         logger.info("Sending verification email")
#         body_template = """
#         <!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>TVL Updates</title>
#         </head>
#         <body>
#             <div>
#                 <h3>TVL Update</h3><br>
#                 <p>Here is the current TVL update</p>
#                 <a href="{link}" style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #27B55B; color: white;">Verify your email</a>
#                 <p>Kindly ignore this email if you did not sign up for TVL. Thank you!</p>
#             </div>
#         </body>
#         </html>
#         """

#         for recipient in self.recipients:
#             logger.info("Creating token for recipient: %s", recipient)
#             token = self.create_token(recipient)
#             link = f"{SSL_PREFIX}://{FRONTEND_URL}/{token}"
#             body = body_template.format(link=link)
#             await self.send_email("TVL UPDATES", body)
