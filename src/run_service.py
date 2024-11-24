

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    mode = os.getenv("MODE", "prod")

    if mode != "dev":
        uvicorn.run(
            "main:app",  # Import app as a string
            host="0.0.0.0",  # Bind to 0.0.0.0 for external access
            port=int(os.getenv("PORT", 8000)),  # Use the PORT environment variable
            reload=True
        )
    else:
        uvicorn.run(
            "service:app", 
            host="0.0.0.0",  # Use 0.0.0.0 for development as well
            port=8000,  # Fixed port for development
            reload=True
        )


