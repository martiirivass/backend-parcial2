"""Tests específicos de pedidos (FSM, endpoints protegidos, listados)."""


def test_pedido_requires_auth(client):
    """Endpoint protegido: 401 sin autenticar."""
    client.cookies.clear()
    response = client.get("/api/v1/pedidos/")
    assert response.status_code == 401


def test_pedido_list_with_auth(client, admin_token):
    """Endpoint protegido: GET /api/v1/pedidos/ autenticado."""
    client.cookies.clear()
    client.cookies.set("access_token", admin_token)
    response = client.get("/api/v1/pedidos/")
    assert response.status_code == 200


class TestPedidoFSM:

    def test_crear_pedido_requiere_auth(self, client):
        client.cookies.clear()
        response = client.post("/api/v1/pedidos/")
        assert response.status_code == 401

    def test_listar_pedidos_retorna_paginacion(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        response = client.get("/api/v1/pedidos/")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "pages" in data

    def test_crear_pedido_valido(self, client, client_token, admin_token, db_rollback):
        from sqlmodel import select
        from app.models.producto_model import Producto

        db_rollback.commit()
        client.cookies.set("access_token", admin_token)
        prod_resp = client.post(
            "/api/v1/productos/",
            json={
                "nombre": "Test Prod Pedido",
                "precio_base": "100.00",
                "unidad_venta_id": 1,
                "stock_cantidad": 10,
            },
        )
        assert prod_resp.status_code == 201
        prod_id = prod_resp.json()["id"]

        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/pedidos/",
            json={
                "forma_pago_codigo": "EFECTIVO",
                "items": [
                    {"producto_id": prod_id, "cantidad": 2},
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["estado_codigo"] == "PENDIENTE"

    def test_transicion_invalida_devuelve_400(self, client, admin_token, db_rollback, producto_id):
        from tests.conftest import make_pedido, make_detalle
        from app.models.usuario import Usuario
        from sqlmodel import select

        user = db_rollback.exec(
            select(Usuario).where(Usuario.email == "test@test.com")
        ).first()
        if not user:
            return

        pedido = make_pedido(db_rollback, user.id)
        make_detalle(db_rollback, pedido.id, producto_id)
        db_rollback.commit()

        client.cookies.set("access_token", admin_token)
        response = client.patch(
            f"/api/v1/pedidos/{pedido.id}/estado",
            json={"estado_codigo": "ENTREGADO"},
        )
        assert response.status_code == 400
