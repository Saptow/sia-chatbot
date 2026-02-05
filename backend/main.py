from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.chat import router as chat_router
import uvicorn
from dotenv import load_dotenv

app = FastAPI()

# load environment variables from .env file
load_dotenv()

# Add routers here
routers=[
    chat_router,
]
for router in routers:
    app.include_router(router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)