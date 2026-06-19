"""
WSManager — Singleton que gestiona todas las conexiones WebSocket.

Arquitectura:
- admin_connections: set[WebSocket] — admins escuchando /ws/pedidos (todos los eventos)
- client_connections: dict[int, set[WebSocket]] — clientes escuchando /ws/pedidos/{pedido_id}
- Mutex asyncio.Lock para operaciones concurrentes seguras

Uso:
    from app.core.ws_manager import ws_manager

    # Desde un endpoint WebSocket
    await ws_manager.connect_admin(websocket)
    await ws_manager.disconnect_admin(websocket)
    await ws_manager.connect_client(pedido_id, websocket)
    await ws_manager.disconnect_client(pedido_id, websocket)

    # Para broadcast (SIEMPRE después del commit del UoW)
    await ws_manager.broadcast_to_pedido(pedido_id, event_dict)
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSManager:
    """Manejador singleton de conexiones WebSocket."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._admin_connections: set[WebSocket] = set()
        self._client_connections: dict[int, set[WebSocket]] = {}
        self._main_loop: asyncio.AbstractEventLoop | None = None

    def store_main_loop(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        """
        Almacena el event loop principal para poder hacer broadcast
        desde threads del pool de FastAPI (handlers sync).
        Debe llamarse desde el main loop al iniciar la app.
        """
        self._main_loop = loop or asyncio.get_running_loop()

    def broadcast_to_pedido_sync(
        self, pedido_id: int, event: dict[str, Any]
    ) -> None:
        """
        Versión sync-safe de broadcast_to_pedido.
        Usa run_coroutine_threadsafe para programar el broadcast
        desde cualquier thread (incluyendo thread pool de FastAPI).
        """
        if self._main_loop is None or not self._main_loop.is_running():
            return
        asyncio.run_coroutine_threadsafe(
            self.broadcast_to_pedido(pedido_id, event),
            self._main_loop,
        )

    # ── Admin connections ──────────────────────────────────────────────

    async def connect_admin(self, websocket: WebSocket) -> None:
        """Registra un admin para recibir eventos de TODOS los pedidos."""
        async with self._lock:
            self._admin_connections.add(websocket)
        logger.info(
            "Admin WS conectado. Total admins: %d",
            len(self._admin_connections),
        )

    async def disconnect_admin(self, websocket: WebSocket) -> None:
        """Remueve un admin de la lista de broadcasts."""
        async with self._lock:
            self._admin_connections.discard(websocket)
        logger.info(
            "Admin WS desconectado. Total admins: %d",
            len(self._admin_connections),
        )

    # ── Client connections ─────────────────────────────────────────────

    async def connect_client(
        self, pedido_id: int, websocket: WebSocket
    ) -> None:
        """Registra un cliente para recibir eventos de UN pedido específico."""
        async with self._lock:
            if pedido_id not in self._client_connections:
                self._client_connections[pedido_id] = set()
            self._client_connections[pedido_id].add(websocket)
        client_count = len(self._client_connections[pedido_id])
        logger.info(
            "Cliente WS conectado al pedido %d. Total clientes: %d",
            pedido_id,
            client_count,
        )

    async def disconnect_client(
        self, pedido_id: int, websocket: WebSocket
    ) -> None:
        """Remueve un cliente de un pedido específico."""
        async with self._lock:
            if pedido_id in self._client_connections:
                self._client_connections[pedido_id].discard(websocket)
                if not self._client_connections[pedido_id]:
                    del self._client_connections[pedido_id]
        logger.info(
            "Cliente WS desconectado del pedido %d", pedido_id
        )

    # ── Broadcast ──────────────────────────────────────────────────────

    async def broadcast_to_pedido(
        self, pedido_id: int, event: dict[str, Any]
    ) -> None:
        """
        Envía un evento a:
          - Todos los admins conectados
          - Todos los clientes escuchando ese pedido específico

        El evento se serializa como JSON antes de enviar.
        Conexiones caídas se remueven automáticamente.
        """
        payload = json.dumps(event, default=str)

        async with self._lock:
            # Copia las referencias bajo el lock para evitar race conditions
            admin_targets = list(self._admin_connections)
            client_targets = list(
                self._client_connections.get(pedido_id, set())
            )

        # ── Enviar a admins (todo pedido) ──
        stale_admin: list[WebSocket] = []
        for ws in admin_targets:
            try:
                await ws.send_text(payload)
            except Exception:
                stale_admin.append(ws)

        # ── Enviar a clientes de ese pedido ──
        stale_client: list[WebSocket] = []
        for ws in client_targets:
            try:
                await ws.send_text(payload)
            except Exception:
                stale_client.append(ws)

        # ── Limpiar conexiones muertas ──
        if stale_admin or stale_client:
            async with self._lock:
                for ws in stale_admin:
                    self._admin_connections.discard(ws)
                if pedido_id in self._client_connections:
                    for ws in stale_client:
                        self._client_connections[pedido_id].discard(ws)
                    if not self._client_connections[pedido_id]:
                        del self._client_connections[pedido_id]

        total = len(admin_targets) + len(client_targets)
        logger.debug(
            "Broadcast pedido %d: %d destinos (%d admins, %d clientes)",
            pedido_id,
            total,
            len(admin_targets),
            len(client_targets),
        )

    @property
    def admin_count(self) -> int:
        """Cantidad de admines conectados (para debugging/monitoreo)."""
        return len(self._admin_connections)


# ── Singleton a nivel módulo ────────────────────────────────────────────
ws_manager = WSManager()
