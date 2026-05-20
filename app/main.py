from fastapi import FastAPI
from app.db.init_db import init_db
from app.routers.producto_router import router as producto
from app.routers.categoria_router import router as categoria
from app.routers.ingrediente_router import router as ingrediente

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(producto)
app.include_router(categoria)
app.include_router(ingrediente)
