from fastapi import FastAPI
from app.db.init_db import init_db
from app.auth.router import router as auth
from app.routers.producto_router import router as producto
from app.routers.categoria_router import router as categoria
from app.routers.ingrediente_router import router as ingrediente
from app.routers.pedido_router import router as pedido
from app.routers.direccion_router import router as direccion
from app.routers.admin_router import router as admin
from app.routers.stats_router import router as stats
from app.routers.unidad_medida_router import router as unidad_medida
from app.routers.forma_pago_router import router as forma_pago
from app.routers.estado_pedido_router import router as estado_pedido
from app.routers.pago_router import router as pago

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

app.include_router(auth)
app.include_router(producto)
app.include_router(categoria)
app.include_router(ingrediente)
app.include_router(pedido)
app.include_router(direccion)
app.include_router(admin)
app.include_router(stats)
app.include_router(unidad_medida)
app.include_router(forma_pago)
app.include_router(estado_pedido)
app.include_router(pago)
