import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from endpoints.upload import router as uploadRouter
from endpoints.generateObs import router as generateObsRouter
from endpoints.regenerateObs import router as regenerateObsRouter
from endpoints.applyObs import router as applyObsRouter
from config import UPLOAD_DIR

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(uploadRouter)
app.include_router(generateObsRouter)
app.include_router(regenerateObsRouter)
app.include_router(applyObsRouter)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)