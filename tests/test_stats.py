"""Tests de Statistics: resumen, ventas, productos más vendidos."""
import pytest


class TestResumen:

    RESUMEN_URL = "/api/v1/estadisticas/resumen"

    def test_resumen_ok(self, client, admin_token):
        """GET /admin/stats/resumen con admin retorna 200."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(self.RESUMEN_URL)
        assert response.status_code == 200
        data = response.json()
        assert "ventas_totales" in data
        assert "pedidos_hoy" in data
        assert "clientes_nuevos" in data

    def test_resumen_sin_auth(self, client):
        """401 sin token."""
        client.cookies.clear()
        response = client.get(self.RESUMEN_URL)
        assert response.status_code == 401

    def test_resumen_no_admin(self, client, client_token):
        """403 si no es ADMIN."""
        client.cookies.clear()
        client.cookies.set("access_token", client_token)
        response = client.get(self.RESUMEN_URL)
        assert response.status_code == 403

    def test_resumen_con_fechas(self, client, admin_token):
        """Filtro por fechas funciona."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(
            self.RESUMEN_URL,
            params={"fecha_desde": "2026-01-01", "fecha_hasta": "2026-12-31"},
        )
        assert response.status_code == 200


class TestVentasSemanales:

    URL = "/api/v1/estadisticas/ventas-semanales"

    def test_ventas_semanales_ok(self, client, admin_token):
        """GET /admin/stats/ventas-semanales retorna 200."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(self.URL)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_ventas_semanales_sin_auth(self, client):
        """401 sin token."""
        client.cookies.clear()
        response = client.get(self.URL)
        assert response.status_code == 401


class TestProductosMasVendidos:

    URL = "/api/v1/estadisticas/productos-mas-vendidos"

    def test_productos_mas_vendidos_ok(self, client, admin_token):
        """GET /admin/stats/productos-mas-vendidos retorna 200."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(self.URL)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_productos_mas_vendidos_con_limit(self, client, admin_token):
        """Parámetro limit funciona."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(self.URL, params={"limit": 5})
        assert response.status_code == 200
        assert len(response.json()["data"]) <= 5

    def test_productos_mas_vendidos_sin_auth(self, client):
        """401 sin token."""
        client.cookies.clear()
        response = client.get(self.URL)
        assert response.status_code == 401


class TestPedidosPorEstado:

    URL = "/api/v1/estadisticas/pedidos-por-estado"

    def test_pedidos_por_estado_ok(self, client, admin_token):
        """GET /admin/stats/pedidos-por-estado retorna 200."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(self.URL)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestIngresosPorFormaPago:

    URL = "/api/v1/estadisticas/ingresos-por-forma-pago"

    def test_ingresos_por_forma_pago_ok(self, client, admin_token):
        """GET /admin/stats/ingresos-por-forma-pago retorna 200."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.get(self.URL)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
