from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.db import Base, engine, ensure_document_notes_column
from src.user.router import user_routes
from src.auth.router import auth_routes
from src.document.router import  document_routes
from src.extraction.router import extraction_routes
from src.notes_ai.router import ai_routes
from starlette.middleware.sessions import SessionMiddleware
from src.utils.settings import settings

Base.metadata.create_all(engine)
ensure_document_notes_column()
app = FastAPI(title="This is my fastAPI project")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-powered-document-to-notes-genera.vercel.app",
        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         settings.FRONTEND_URL,
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)
app.include_router(user_routes)
app.include_router(auth_routes)
app.include_router(document_routes)
app.include_router(extraction_routes)
app.include_router(ai_routes)

