from .utils import check_existing_email, validate_recipient
from .models import Subscribers

async def collect_email(db, email: str):

    # validate email address
    await validate_recipient(email)

    # Check if email already exists in the database
    await check_existing_email(db, email)
    new_subscriber = Subscribers(email=email)
    db.add(new_subscriber)
    await db.commit()
    await db.refresh(new_subscriber)

    # Access attributes immediately
    email_value = new_subscriber.email

    return {"message": f"Email {email_value} collected successfully"}
from sqlalchemy.future import select









