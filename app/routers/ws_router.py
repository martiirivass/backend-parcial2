"""
WebSocket Router — Endpoints de tiempo real para pedidos.

Endpoints:
  /ws/pedidos        → Admin: recibe eventos de TODOS los pedidos
  /ws/pedidos/{id}   → Cliente: recibe eventos de SU pedido

Autenticación vía cookie `access_token` (compartida con REST).
"""

import logging

import jwt
from fastapi import APIRouter, WebSocket
from sqlmodel import Session, select

from app.auth.security import ALGORITHM, SECRET_KEY
from app.core.ws_manager import ws_manager
from app.db.database import engine
from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


# ── Helpers de autenticación para WebSocket ────────────────────────────


def _get_user_from_cookies(
    cookies: dict[str, str],
) -> Usuario | None:
    """
    Extrae y valida el token JWT desde las cookies del WebSocket.
    Retorna el usuario o None si no es válido.
    """
    token = cookies.get("access_token")
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
    # ── Auth ───────────────────────────────────────────────────────────
    user = _get_user_from_cookies(websocket.cookies)
    if user is None:
        await websocket.close(code=4001, reason="No autenticado")
        return

    if not _user_has_role(user, "ADMIN", "PEDIDOS"):
        await websocket.close(code=4003, reason="Sin permisos")
        return

    # ── Conexión ───────────────────────────────────────────────────────
    await ws_manager.connect_admin(websocket)
    logger.info("Admin WS conectado: usuario %d", user.id)

    try:
        # Mantiene la conexión abierta; los broadcasts llegan vía WSManager
        while True:
            # Podemos recibir mensajes del cliente (heartbeat, etc.)
            data = await websocket.receive_text()
            # Por ahora solo ignoramos, pero podría usarse para heartbeats
    except Exception:
        pass
    finally:
        await ws_manager.disconnect_admin(websocket)
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
    # ── Auth ───────────────────────────────────────────────────────────
    user = _get_user_from_cookies(websocket.cookies)
    if user is None:
        await websocket.close(code=4001, reason="No autenticado")
        return

    if not _usuario_tiene_pedido(user.id, pedido_id):
        await websocket.close(code=4003, reason="El pedido no te pertenece")
        return

    # ── Conexión ───────────────────────────────────────────────────────
    await ws_manager.connect_client(pedido_id, websocket)
    logger.info(
        "Cliente WS conectado al pedido %d: usuario %d",
        pedido_id,
        user.id,
    )

    try:
        while True:
            data = await websocket.receive_text()
            # Heartbeat / ignorado por ahora
    except Exception:
        pass
    finally:
        await ws_manager.disconnect_client(pedido_id, websocket)
        logger.info(
            "Cliente WS desconectado del pedido %d: usuario %d",
            pedido_id,
            user.id,
        )
