from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, disease_presets, institutions, users
from app.core.config import settings

app = FastAPI(title="EpiSim API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(institutions.router)
app.include_router(admin.router)
app.include_router(disease_presets.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
