import uuid
from decimal import Decimal

from app.schemas.admin_schema import AdminUsersListResponse
from app.schemas.producto_schema import (
    ProductoCreate,
    ProductoReadWithRelations,
)
from app.schemas.categoria_schema import CategoriaRead
from app.schemas.ingrediente_schema import (
    IngredienteRead,
    IngredienteCreate,
)
# ── Productos CRUD ──────────────────────────────────────────────────


class TestProductosCRUD:

    def test_listar_retorna_paginacion(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert "total" in data
        assert "data" in data
        assert data["page"] == 1
        assert data["size"] == 10

    def test_obtener_producto_retorna_datos(self, client, producto_id):
        response = client.get(f"/api/v1/productos/{producto_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == producto_id

    def test_crear_producto_requiere_admin(self, client, client_token):
        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/productos/",
            json={
                "nombre": "Producto Test",
                "precio_base": 100.0,
                "categoria_ids": [1],
                "ingrediente_ids": [1],
                "stock_cantidad": 10,
            },
        )
        assert response.status_code == 403

    def test_crear_producto_admin_retorna_201(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        response = client.post(
            "/api/v1/productos/",
            json={
                "nombre": f"Producto CRUD {uuid.uuid4().hex[:6]}",
                "precio_base": 150.0,
                "categoria_ids": [1],
                "ingrediente_ids": [1],
                "stock_cantidad": 5,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"].startswith("Producto CRUD")
        assert data["precio_base"] == 150.0

    def test_actualizar_producto_admin(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.producto_model import Producto

        prod = db.exec(select(Producto).where(Producto.deleted_at.is_(None))).first()
        if not prod:
            return
        client.cookies.set("access_token", admin_token)
        response = client.put(
            f"/api/v1/productos/{prod.id}",
            json={"nombre": f"Updated {uuid.uuid4().hex[:6]}", "precio_base": 200.0},
        )
        assert response.status_code == 200

    def test_actualizar_disponibilidad(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.producto_model import Producto

        prod = db.exec(select(Producto).where(Producto.deleted_at.is_(None))).first()
        if not prod:
            return
        client.cookies.set("access_token", admin_token)
        response = client.patch(
            f"/api/v1/productos/{prod.id}/disponibilidad",
            json={"disponible": False},
        )
        assert response.status_code == 200

    def test_eliminar_producto_admin(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.producto_model import Producto

        prod = db.exec(select(Producto).where(Producto.deleted_at.is_(None))).first()
        if not prod:
            return
        client.cookies.set("access_token", admin_token)
        response = client.delete(f"/api/v1/productos/{prod.id}")
        assert response.status_code == 204


# ── Auth Refresh ───────────────────────────────────────────────────


class TestAuthRefresh:

    def test_refresh_sin_token_devuelve_400(self, client):
        client.cookies.clear()
        response = client.post("/api/v1/auth/refresh")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_refresh_con_token_invalido_devuelve_401(self, client):
        client.cookies.clear()
        client.cookies.set("refresh_token", "invalido")
        response = client.post("/api/v1/auth/refresh")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


# ── Admin CRUD ─────────────────────────────────────────────────────


class TestAdminUsuarios:

    def test_listar_usuarios_retorna_paginacion(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        response = client.get("/api/v1/admin/usuarios")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert "total" in data
        assert "data" in data

    def test_listar_usuarios_sin_admin_devuelve_403(self, client, client_token):
        client.cookies.set("access_token", client_token)
        response = client.get("/api/v1/admin/usuarios")
        assert response.status_code == 403

    def test_obtener_usuario_por_id(self, client, admin_token, db):
        from app.models.usuario import Usuario
        from sqlmodel import select

        user = db.exec(select(Usuario).where(Usuario.email == "test@test.com")).first()
        if not user:
            return
        client.cookies.set("access_token", admin_token)
        response = client.get(f"/api/v1/admin/usuarios/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id

    def test_obtener_usuario_inexistente(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        response = client.get("/api/v1/admin/usuarios/99999")
        assert response.status_code == 404

    def test_actualizar_usuario(self, client, admin_token, db):
        from app.models.usuario import Usuario
        from sqlmodel import select

        user = db.exec(select(Usuario).where(Usuario.email == "test@test.com")).first()
        if not user:
            return
        client.cookies.set("access_token", admin_token)
        response = client.put(
            f"/api/v1/admin/usuarios/{user.id}",
            json={"nombre": "UpdatedName"},
        )
        assert response.status_code == 200

    def test_eliminar_usuario_admin(self, client, admin_token, cliente_id):
        client.cookies.set("access_token", admin_token)
        response = client.delete(f"/api/v1/admin/usuarios/{cliente_id}")
        assert response.status_code == 204

    def test_listar_con_filtro_rol(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        response = client.get("/api/v1/admin/usuarios?rol_codigo=CLIENT")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0


# ── Categorías CRUD ────────────────────────────────────────────────


class TestCategoriasCRUD:

    def test_listar_retorna_paginacion(self, client):
        response = client.get("/api/v1/categorias/")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "pages" in data

    def test_crear_categoria_admin(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        nombre = f"Cat CRUD {uuid.uuid4().hex[:6]}"
        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": nombre, "descripcion": "Test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == nombre

    def test_crear_categoria_sin_admin_devuelve_403(self, client, client_token):
        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "No deberia", "descripcion": "fail"},
        )
        assert response.status_code == 403

    def test_actualizar_categoria(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.categoria_model import Categoria

        cat = db.exec(select(Categoria).where(Categoria.deleted_at.is_(None))).first()
        if not cat:
            return

        client.cookies.set("access_token", admin_token)
        response = client.put(
            f"/api/v1/categorias/{cat.id}",
            json={"nombre": f"Updated {uuid.uuid4().hex[:6]}"},
        )
        assert response.status_code == 200

    def test_eliminar_categoria(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.categoria_model import Categoria

        cat = db.exec(select(Categoria).where(Categoria.deleted_at.is_(None))).first()
        if not cat:
            return

        client.cookies.set("access_token", admin_token)
        response = client.delete(f"/api/v1/categorias/{cat.id}")
        assert response.status_code == 204


# ── Ingredientes CRUD ──────────────────────────────────────────────


class TestIngredientesCRUD:

    def test_listar_retorna_paginacion(self, client):
        response = client.get("/api/v1/ingredientes/")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "pages" in data

    def test_crear_ingrediente_admin(self, client, admin_token):
        client.cookies.set("access_token", admin_token)
        nombre = f"Ing CRUD {uuid.uuid4().hex[:6]}"
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": nombre, "unidad_medida_id": 1, "stock_cantidad": 10},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == nombre

    def test_crear_ingrediente_sin_admin_devuelve_403(self, client, client_token):
        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "No deberia", "unidad_medida_id": 1},
        )
        assert response.status_code == 403

    def test_actualizar_ingrediente(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.ingrediente_model import Ingrediente

        ing = db.exec(select(Ingrediente).where(Ingrediente.deleted_at.is_(None))).first()
        if not ing:
            return

        client.cookies.set("access_token", admin_token)
        response = client.put(
            f"/api/v1/ingredientes/{ing.id}",
            json={"nombre": f"Updated {uuid.uuid4().hex[:6]}"},
        )
        assert response.status_code == 200

    def test_eliminar_ingrediente(self, client, admin_token, db):
        from sqlmodel import select
        from app.models.ingrediente_model import Ingrediente

        ing = db.exec(select(Ingrediente).where(Ingrediente.deleted_at.is_(None))).first()
        if not ing:
            return

        client.cookies.set("access_token", admin_token)
        response = client.delete(f"/api/v1/ingredientes/{ing.id}")
        assert response.status_code == 204


# ── Direcciones CRUD (protegido: CLIENT autenticado) ──────────────


class TestDireccionesCRUD:

    def test_listar_direcciones_requiere_auth(self, client):
        client.cookies.clear()
        response = client.get("/api/v1/direcciones/")
        assert response.status_code == 401

    def test_listar_direcciones_con_auth(self, client, client_token):
        client.cookies.set("access_token", client_token)
        response = client.get("/api/v1/direcciones/")
        assert response.status_code == 200

    def test_crear_direccion(self, client, client_token):
        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/direcciones/",
            json={
                "alias": "Casa",
                "linea1": "Av. Siempre Viva 123",
                "ciudad": "CABA",
                "provincia": "Buenos Aires",
                "codigo_postal": "1000",
            },
        )
        assert response.status_code == 201

    def test_eliminar_direccion(self, client, client_token, db_rollback):
        from tests.conftest import make_pedido

        client.cookies.set("access_token", client_token)
        response = client.post(
            "/api/v1/direcciones/",
            json={
                "alias": "Temp",
                "linea1": "Temp 456",
                "ciudad": "CABA",
            },
        )
        assert response.status_code == 201
        dir_id = response.json()["id"]

        response = client.delete(f"/api/v1/direcciones/{dir_id}")
        assert response.status_code == 204

    def test_eliminar_direccion_ajena_devuelve_403(self, client, client_token, admin_token, db):
        from sqlmodel import select
        from app.models.usuario import Usuario

        admin_user = db.exec(
            select(Usuario).where(Usuario.email == "admin@foodstore.com")
        ).first()
        if not admin_user:
            return

        client.cookies.set("access_token", admin_token)
        response = client.post(
            "/api/v1/direcciones/",
            json={
                "alias": "AdminDir",
                "linea1": "Admin 789",
                "ciudad": "CABA",
            },
        )
        assert response.status_code == 201
        admin_dir_id = response.json()["id"]

        client.cookies.set("access_token", client_token)
        response = client.delete(f"/api/v1/direcciones/{admin_dir_id}")
        assert response.status_code == 403


# ── Unidades de medida ─────────────────────────────────────────────


class TestUnidadesMedida:

    def test_listar(self, client):
        response = client.get("/api/v1/unidades-medida/")
        assert response.status_code == 200

    def test_listar_retorna_lista(self, client):
        response = client.get("/api/v1/unidades-medida/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# ── Estados de pedido ──────────────────────────────────────────────


class TestEstadosPedido:

    def test_listar(self, client):
        response = client.get("/api/v1/estados-pedido/")
        assert response.status_code == 200

    def test_listar_retorna_lista(self, client):
        response = client.get("/api/v1/estados-pedido/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# ── Formas de pago ─────────────────────────────────────────────────


class TestFormasPago:

    def test_listar(self, client):
        response = client.get("/api/v1/formas-pago/")
        assert response.status_code == 200

    def test_listar_retorna_lista(self, client):
        response = client.get("/api/v1/formas-pago/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
