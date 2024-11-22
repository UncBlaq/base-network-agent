# from fastapi import APIRouter, BackgroundTasks
# from email_utils import SmtpMailService 

# admin_router = APIRouter(
#     prefix="/admin",
#     tags=["Admin"]
# )

# @admin_router.post("/send_email")
# async def send_tvl_email(recipients : str | list, background_task :BackgroundTasks):

#     """
#     Send a TVL notification email to a list of recipients.
#     This function uses the BackgroundTasks object to run the email sending task in the background.

#     Args:
#         recipients (str | list): List of email addresses to send the email to.
#         background_task (BackgroundTasks): FastAPI's BackgroundTasks object for running tasks in the background.

#         Returns:
#             str: Message indicating the email sending status.


#     """
#     smtp_service = SmtpMailService(recipients)
#     background_task.add_task(smtp_service.send_tvl_email)
#     return "Email sent successfully"




 



