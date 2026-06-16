"""Tests de WebSocket: conexión, broadcast, evento resync."""
import json
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from starlette.websockets import WebSocketDisconnect

from tests.conftest import make_pedido


def _assert_ws_rejected(client, url):
    """
    Intenta conectar a un WebSocket que debería ser rechazado.
    Captura WebSocketDisconnect tanto en __enter__ como en
    receive_text(), cubriendo variantes de Starlette/TestClient.
    """
    try:
        with client.websocket_connect(url) as ws:
            try:
                ws.receive_text()
            except WebSocketDisconnect:
                return
    except WebSocketDisconnect:
        return
    pytest.fail(f"WebSocket {url} no fue rechazado")


# ═══════════════════════════════════════════════════════════════
# WS Manager (unit tests)
# ═══════════════════════════════════════════════════════════════

class TestWSManager:

    @pytest.mark.asyncio
    async def test_connect_admin(self):
        """connect_admin agrega al set de admins."""
        from app.core.ws_manager import WSManager
        mgr = WSManager()
        ws = AsyncMock()
        await mgr.connect_admin(ws)
        assert mgr.admin_count == 1

    @pytest.mark.asyncio
    async def test_disconnect_admin(self):
        """disconnect_admin remueve del set."""
        from app.core.ws_manager import WSManager
        mgr = WSManager()
        ws = AsyncMock()
        await mgr.connect_admin(ws)
        await mgr.disconnect_admin(ws)
        assert mgr.admin_count == 0

    @pytest.mark.asyncio
    async def test_connect_client(self):
        """connect_client agrega al dict de clientes."""
        from app.core.ws_manager import WSManager
        mgr = WSManager()
        ws = AsyncMock()
        await mgr.connect_client(1, ws)
        assert 1 in mgr._client_connections

    @pytest.mark.asyncio
    async def test_broadcast_to_admin_only(self):
        """broadcast_to_pedido envía solo a admins si no hay clientes."""
        from app.core.ws_manager import WSManager
        mgr = WSManager()
        admin_ws = AsyncMock()
        await mgr.connect_admin(admin_ws)

        await mgr.broadcast_to_pedido(1, {"type": "test"})
        admin_ws.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_client(self):
        """broadcast_to_pedido envía al cliente del pedido."""
        from app.core.ws_manager import WSManager
        mgr = WSManager()
        client_ws = AsyncMock()
        await mgr.connect_client(42, client_ws)

        await mgr.broadcast_to_pedido(42, {"type": "order_update"})
        client_ws.send_text.assert_called_once()
        call_arg = json.loads(client_ws.send_text.call_args[0][0])
        assert call_arg["type"] == "order_update"


# ═══════════════════════════════════════════════════════════════
# WS Integration tests
# ═══════════════════════════════════════════════════════════════

class TestWSAdminIntegration:

    def test_admin_ws_conexion_ok(self, client, admin_token):
        """Admin se conecta a /ws/pedidos con token válido."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        with client.websocket_connect("/ws/pedidos"):
            pass

    def test_admin_ws_sin_token(self, client):
        """Admin WS sin token se cierra con 4001."""
        client.cookies.clear()
        _assert_ws_rejected(client, "/ws/pedidos")

    def test_admin_ws_role_incorrecto(self, client, client_token):
        """Cliente conectando a /ws/pedidos es rechazado."""
        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        _assert_ws_rejected(client, "/ws/pedidos")

    def test_admin_ws_con_token_query_param(self, client, admin_token):
        """Admin se conecta usando ?token=<jwt>."""
        client.cookies.clear()
        with client.websocket_connect(f"/ws/pedidos?token={admin_token}"):
            pass


class TestWSClienteIntegration:

    def test_cliente_ws_conexion_ok(
        self, client, client_token, db_rollback, cliente_id
    ):
        """Cliente se conecta a su propio pedido."""
        pedido = make_pedido(db_rollback, cliente_id, total=Decimal("100.00"))
        db_rollback.commit()

        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        with client.websocket_connect(f"/ws/pedidos/{pedido.id}"):
            pass

    def test_cliente_ws_sin_token(self, client):
        """Cliente WS sin token se cierra."""
        client.cookies.clear()
        _assert_ws_rejected(client, "/ws/pedidos/1")


# ═══════════════════════════════════════════════════════════════
# Resync event (verificamos que el manager no explota)
# ═══════════════════════════════════════════════════════════════

class TestResyncEvent:

    @pytest.mark.asyncio
    async def test_resync_event_format(self):
        """Broadcast con type=resync no rompe al enviar."""
        from app.core.ws_manager import WSManager
        mgr = WSManager()
        ws = AsyncMock()
        await mgr.connect_admin(ws)

        await mgr.broadcast_to_pedido(1, {"type": "resync"})
        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["type"] == "resync"
