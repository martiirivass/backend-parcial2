"""
WebSocket Router — Endpoints de tiempo real para pedidos.

Endpoints:
  /ws/pedidos        → Admin: recibe eventos de TODOS los pedidos
  /ws/pedidos/{id}   → Cliente: recibe eventos de SU pedido

Autenticación vía cookie `access_token` (compartida con REST).
"""

import logging

import jwt
from fastapi import APIRouter, WebSocket, WebSocketException
from sqlmodel import Session, select

from app.auth.security import ALGORITHM, SECRET_KEY
from app.core.ws_manager import ws_manager
from app.db.database import engine
from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


# ── Helpers de autenticación para WebSocket ────────────────────────────


def _get_user_from_ws(websocket: WebSocket) -> Usuario | None:
    """
    Extrae y valida el token JWT desde cookies o query param ?token=<jwt>.
    Retorna el usuario o None si no es válido.
    """
    token = websocket.cookies.get("access_token") or websocket.query_params.get("token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except Exception:
        return None

    with Session(engine) as session:
        user = session.get(Usuario, int(user_id))
    return user


def _user_has_role(user: Usuario, *roles: str) -> bool:
    """Verifica si el usuario tiene al menos uno de los roles dados."""
    with Session(engine) as session:
        user_role_codes = session.exec(
            select(UsuarioRol.rol_codigo).where(
                UsuarioRol.usuario_id == user.id
            )
        ).all()
    return any(rol in user_role_codes for rol in roles)


def _usuario_tiene_pedido(user_id: int, pedido_id: int) -> bool:
    """Verifica si un pedido pertenece al usuario."""
    from app.models.pedido_model import Pedido

    with Session(engine) as session:
        pedido = session.get(Pedido, pedido_id)
    return pedido is not None and pedido.usuario_id == user_id


# ── Endpoints WebSocket ────────────────────────────────────────────────


@router.websocket("/ws/pedidos")
async def ws_pedidos_admin(websocket: WebSocket) -> None:
    """
    WebSocket para admins.
    Recibe TODOS los eventos de cambio de estado de pedidos.

    Autenticación: requiere cookie `access_token` con rol ADMIN o PEDIDOS.
    """
    try:
        # ── Auth (cookie o query param ?token=) ────────────────────────
        user = _get_user_from_ws(websocket)
        if user is None:
            await websocket.close(code=4001, reason="No autenticado")
            return

        if not _user_has_role(user, "ADMIN", "PEDIDOS"):
            await websocket.close(code=4003, reason="Sin permisos")
            return

        # ── Conexión ───────────────────────────────────────────────────
        await ws_manager.connect_admin(websocket)

        while True:
            data = await websocket.receive_text()
    except Exception:
        pass
    finally:
        await ws_manager.disconnect_admin(websocket)
        if user is not None:
            logger.info("Admin WS desconectado: usuario %d", user.id)


@router.websocket("/ws/pedidos/{pedido_id}")
async def ws_pedidos_cliente(
    websocket: WebSocket,
    pedido_id: int,
) -> None:
    """
    WebSocket para clientes.
    Recibe eventos de UN pedido específico.

    Autenticación: requiere cookie `access_token`.
    El pedido debe pertenecer al usuario autenticado.
    """
    try:
        # ── Auth (cookie o query param ?token=) ────────────────────────
        user = _get_user_from_ws(websocket)
        if user is None:
            await websocket.close(code=4001, reason="No autenticado")
            return

        if not _usuario_tiene_pedido(user.id, pedido_id):
            await websocket.close(code=4003, reason="El pedido no te pertenece")
            return

        # ── Conexión ───────────────────────────────────────────────────
        await ws_manager.connect_client(pedido_id, websocket)

        while True:
            data = await websocket.receive_text()
    except Exception:
        pass
    finally:
        await ws_manager.disconnect_client(pedido_id, websocket)
        if user is not None:
            logger.info(
                "Cliente WS desconectado del pedido %d: usuario %d",
                pedido_id,
                user.id,
            )
