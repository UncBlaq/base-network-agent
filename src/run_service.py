import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    if os.getenv("MODE") != "dev":
        from main import app

        # For testing with streamlit
        # uvicorn.run(app, host="0.0.0.0", port=80)

        # for testing with swagger ui docs
        uvicorn.run(
            "main:app",  # Import app as a string
            host="localhost",
            port=8000,
            reload=True
        )

    else:
        uvicorn.run("service:app", reload=True)

