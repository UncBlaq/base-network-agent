# import os

# from dotenv import load_dotenv
# from itsdangerous import URLSafeTimedSerializer

# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY environment variable is not set")
# serializer = URLSafeTimedSerializer(
#     SECRET_KEY,
#     salt="email-Configuration"
#     )


# def create_url_safe_token(data : dict):

#     return serializer.dumps(data)
