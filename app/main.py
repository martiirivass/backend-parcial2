from fastapi import FastAPI
from app.db.init_db import init_db
from app.routers.producto_router import router as producto
from app.routers.categoria_router import router as categoria
from app.routers.ingrediente_router import router as ingrediente
from app.routers.pedido_router import router as pedido
from app.routers.direccion_router import router as direccion
from app.routers.admin_router import router as admin
from app.auth.router import router as auth_router

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(producto, prefix="/api/v1")
app.include_router(categoria, prefix="/api/v1")
app.include_router(ingrediente, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(pedido, prefix="/api/v1")
app.include_router(direccion, prefix="/api/v1")
app.include_router(admin, prefix="/api/v1")
