from fastapi import HTTPException, status
from sqlalchemy.future import select
from .models import Subscribers

from email_validator import validate_email, EmailSyntaxError


async def check_existing_email(db, email: str):
    """Check if an email is already registered in the database.
    
    Args:
        db: The database session.
        email (str): The email address to check.

    Raises:
        HTTPException: If the email is already registered, an exception with 
        status code 400 and a message "Email already exists" is raised.
    """
    stmt = select(Subscribers).filter(Subscribers.email == email)
    result = await db.execute(stmt)
    db_email = result.scalar_one_or_none()  # Fetches the result or None if not found

    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    

async def validate_recipient(recipient):

        try:
            # Validate email address
            validate_email(recipient)  # No need for await, this is synchronous
        except EmailSyntaxError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email address: {recipient}"
            )
