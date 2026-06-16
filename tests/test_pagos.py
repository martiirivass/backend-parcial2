"""Tests de pagos: crear preferencia, webhook, status."""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_detalle, make_pago, make_pedido


def _mock_mp_preference() -> MagicMock:
    pref = MagicMock()
    pref.create.return_value = {
        "response": {
            "id": "TEST-PREF-001",
            "init_point": "https://www.mercadopago.com.ar/init",
        }
    }
    sdk = MagicMock()
    sdk.preference.return_value = pref
    return sdk


@pytest.fixture
def pedido_pagable(db_rollback, cliente_id, producto_id):
    """Crea un pedido con detalle, commit, y lo retorna."""
    pedido = make_pedido(
        db_rollback, cliente_id,
        subtotal=Decimal("150.00"),
        costo_envio=Decimal("50.00"),
        total=Decimal("200.00"),
    )
    make_detalle(db_rollback, pedido.id, producto_id, precio_snapshot=Decimal("150.00"))
    db_rollback.commit()
    db_rollback.refresh(pedido)
    return pedido


class TestCrearPreferencia:

    @patch("app.pagos.service.mercadopago")
    def test_crear_preferencia_ok(
        self, mock_mp, client, client_token, pedido_pagable,
    ):
        """Crea preferencia y devuelve preference_id."""
        mock_mp.SDK.return_value = _mock_mp_preference()

        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/pagos/crear-preferencia",
            json={"pedido_id": pedido_pagable.id},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["preference_id"] == "TEST-PREF-001"
        assert data["pedido_id"] == pedido_pagable.id

    def test_crear_preferencia_sin_auth(self, client):
        """401 sin token."""
        client.cookies.clear()
        response = client.post(
            "/api/v1/pagos/crear-preferencia",
            json={"pedido_id": 1},
        )
        assert response.status_code == 401

    @patch("app.pagos.service.mercadopago")
    def test_crear_preferencia_pedido_inexistente(
        self, mock_mp, client, client_token,
    ):
        """404 si el pedido no existe."""
        mock_mp.SDK.return_value = _mock_mp_preference()
        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/pagos/crear-preferencia",
            json={"pedido_id": 99999},
        )
        assert response.status_code == 404


class TestWebhook:

    @patch("app.pagos.service.requests")
    def test_webhook_payment_approved(
        self, mock_requests, client, db_rollback, cliente_id
    ):
        """Webhook actualiza pago y marca pedido CONFIRMADO."""
        pedido = make_pedido(db_rollback, cliente_id, total=Decimal("200.00"))
        pago = make_pago(db_rollback, pedido.id, external_reference=str(pedido.id))
        db_rollback.commit()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 50001,
            "status": "approved",
            "status_detail": "accredited",
            "transaction_amount": 200.00,
            "payment_method": {"id": "visa"},
            "date_approved": "2026-06-16T12:00:00.000-03:00",
            "external_reference": str(pedido.id),
        }
        mock_requests.get.return_value = mock_resp

        response = client.post(
            "/api/v1/pagos/webhook",
            params={"data.id": "50001", "topic": "payment"},
        )
        assert response.status_code == 200
        assert response.json()["recibido"] is True

        db_rollback.refresh(pago)
        assert pago.mp_status == "approved"
        assert pago.mp_payment_id == 50001

        db_rollback.refresh(pedido)
        assert pedido.estado_codigo == "CONFIRMADO"

    def test_webhook_sin_data_id(self, client):
        """Webhook sin data.id responde 200 igual."""
        response = client.post(
            "/api/v1/pagos/webhook", params={"topic": "payment"}
        )
        assert response.status_code == 200

    def test_webhook_topic_no_payment(self, client):
        """Webhook con topic no-payment se ignora."""
        response = client.post(
            "/api/v1/pagos/webhook",
            params={"data.id": "50001", "topic": "merchant_order"},
        )
        assert response.status_code == 200

    @patch("app.pagos.service.requests")
    def test_webhook_external_reference_inexistente(
        self, mock_requests, client
    ):
        """Webhook con external_reference desconocida no falla."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 50002,
            "status": "approved",
            "external_reference": "no-existe",
        }
        mock_requests.get.return_value = mock_resp

        response = client.post(
            "/api/v1/pagos/webhook",
            params={"data.id": "50002", "topic": "payment"},
        )
        assert response.status_code == 200


class TestPagoStatus:

    def test_get_pago_status_sin_auth(self, client):
        """GET /pagos/{id} sin auth retorna 401."""
        client.cookies.clear()
        response = client.get("/api/v1/pagos/1")
        assert response.status_code == 401

    @patch("app.pagos.service.requests")
    def test_get_pago_status_pendiente(
        self, mock_requests, client, client_token, db_rollback, cliente_id
    ):
        """Pago pendiente se sincroniza con MP."""
        pedido = make_pedido(db_rollback, cliente_id, total=Decimal("100.00"))
        make_pago(
            db_rollback, pedido.id,
            external_reference=str(pedido.id),
            mp_status="pending",
            mp_payment_id=60001,
        )
        db_rollback.commit()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 60001,
            "status": "approved",
            "transaction_amount": 100.00,
            "date_approved": "2026-06-16T12:00:00.000-03:00",
        }
        mock_requests.get.return_value = mock_resp

        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        response = client.get(f"/api/v1/pagos/{pedido.id}")
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    def test_get_pago_status_sin_pago(
        self, client, client_token, db_rollback, cliente_id
    ):
        """Pedido sin pagos devuelve status None."""
        pedido = make_pedido(db_rollback, cliente_id, total=Decimal("50.00"))
        db_rollback.commit()

        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        response = client.get(f"/api/v1/pagos/{pedido.id}")
        assert response.status_code == 200
        assert response.json()["status"] is None
