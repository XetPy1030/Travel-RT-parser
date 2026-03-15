from dotenv import load_dotenv
import uvicorn

from app.api import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=9000, reload=False)
