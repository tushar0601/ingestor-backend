from fastapi import FastAPI
from app.api.routes.api import router as api_router

app = FastAPI()
app.include_router(api_router,prefix="/api/v1")  

@app.get("/health")
def health_check():
    return {"status": "ok"}
