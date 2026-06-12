from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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
from app.routers.ws_router import router as ws
from app.core.ws_manager import ws_manager
from fastapi.middleware.cors import CORSMiddleware
from app.pagos.router import router as pagos


from sqlmodel import Session
from app.db.database import engine
from sqlalchemy import text

print("[OK] Imports completados")

app = FastAPI()
print("[OK] FastAPI app creada")

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
print("[OK] CORS middleware agregado")

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
print("[OK] Static files montados")


@app.on_event("startup")
def on_startup():
    print("Probando conexión...")

    with Session(engine) as session:
        result = session.exec(text("SELECT 1"))
        print(result.first())

    import asyncio
    ws_manager.store_main_loop(asyncio.get_event_loop())

    print("[OK] Iniciando init_db...")
    init_db()
    print("[OK] init_db completado")


app.include_router(auth)
print("[OK] Auth router incluido")
app.include_router(producto)
print("[OK] Producto router incluido")
app.include_router(categoria)
print("[OK] Categoria router incluido")
app.include_router(ingrediente)
print("[OK] Ingrediente router incluido")
app.include_router(pedido)
print("[OK] Pedido router incluido")
app.include_router(direccion)
print("[OK] Direccion router incluido")
app.include_router(admin)
print("[OK] Admin router incluido")
app.include_router(stats)
print("[OK] Stats router incluido")
app.include_router(unidad_medida)
print("[OK] UnidadMedida router incluido")
app.include_router(forma_pago)
print("[OK] FormaPago router incluido")
app.include_router(estado_pedido)
print("[OK] EstadoPedido router incluido")
app.include_router(pago)
print("[OK] Pago router incluido")
app.include_router(ws)
print("[OK] WebSocket router incluido")
app.include_router(pagos, prefix="/api/v1")
print("[OK] Pagos router incluido")

print("*** APP LISTA ***")
