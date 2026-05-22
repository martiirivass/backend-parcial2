## 1. Bug Fixes Existentes

- [x] 1.1 Fix CategoriaRepository: cambiar `Categoria.activo == True` por `Categoria.deleted_at == None`
- [x] 1.2 Fix IngredienteRepository: cambiar `Ingrediente.activo == True` por `Ingrediente.deleted_at == None`
- [x] 1.3 Fix auth/router.py: agregar definición faltante `router = APIRouter(prefix="/auth", tags=["Auth"])`
- [x] 1.4 Fix relación Categoria-Producto: remover `productos: List["Producto"]` con `back_populates="categoria"` de Categoria (inconsistente)
- [x] 1.5 Fix test_soft_delete.py: cambiar `.activo` por `.deleted_at` en Categoria e Ingrediente

## 2. Refactor Modelos Existentes — Dominio 1

- [x] 2.1 Refactor Rol: cambiar PK de `id: int` a `codigo: str` como PK semántica (VARCHAR 20)
- [x] 2.2 Refactor Usuario: remover `rol_id` y `rol` (relación 1:N), preparar para N:N vía UsuarioRol
- [x] 2.3 Crear modelo UsuarioRol: tabla link con PK compuesta (usuario_id, rol_codigo) y `asignado_por` (usuario_id opcional)
- [x] 2.4 Actualizar auth/dependencies.py (`get_current_user`) y auth/permissions.py (`require_roles`) para usar la nueva relación N:N

## 3. Nuevos Modelos — Dominio 1

- [x] 3.1 Crear modelo RefreshToken: id, usuario_id (FK), token, expires_at, revoked_at, created_at
- [x] 3.2 Crear modelo DireccionEntrega: id, usuario_id (FK), calle, ciudad, codigo_postal, pais, created_at, updated_at, deleted_at

## 4. Refactor Modelos Existentes — Dominio 2

- [x] 4.1 Crear modelo UnidadMedida: catálogo de unidades de medida
- [x] 4.2 Refactor Producto: agregar `stock_cantidad`, `disponible`, `imagen_url`, timestamps (precio se mantiene)
- [x] 4.3 Refactor Producto: reemplazar `activo: bool` por `deleted_at`, agregar `created_at` y `updated_at`
- [x] 4.4 Refactor ProductoIngrediente: agregar `cantidad`, `unidad_medida_id`, `es_removible`
- [x] 4.5 Refactor Categoria: agregar `created_at`, `updated_at`, eliminar `activo` (usar `deleted_at`)

## 5. Nuevo Dominio 3 — Ventas, Pagos & Trazabilidad (Modelos)

- [x] 5.1 Crear modelo FormaPago: catálogo de formas de pago (integrado de master)
- [x] 5.2 Crear modelo EstadoPedido: catálogo de estados de pedido (integrado de master)
- [x] 5.3 Crear modelo Pedido: tabla principal con FK a Usuario, Direccion, EstadoPedido, FormaPago (integrado de master)
- [x] 5.4 Crear modelo DetallePedido: items con snapshot de nombre y precio (integrado de master)
- [x] 5.5 Crear modelo HistorialEstadoPedido: trazabilidad de cambios de estado (integrado de master)
- [x] 5.6 Crear modelo Pago: pagos asociados a pedidos

## 6. Schemas (Pydantic/SQLModel)

- [ ] 6.1 Actualizar schemas de Producto (ProductoCreate, ProductoRead, ProductoUpdate) para nuevos campos
- [ ] 6.2 Crear schemas de UnidadMedida (UnidadMedidaCreate, UnidadMedidaRead, UnidadMedidaUpdate)
- [ ] 6.3 Crear schemas de DireccionEntrega
- [ ] 6.4 Crear schemas de RefreshToken
- [ ] 6.5 Crear schemas de FormaPago, EstadoPedido
- [ ] 6.6 Crear schemas de Pedido (PedidoCreate, PedidoRead, PedidoReadWithDetails)
- [ ] 6.7 Crear schemas de DetallePedido
- [ ] 6.8 Crear schemas de HistorialEstadoPedido
- [ ] 6.9 Crear schemas de Pago

## 7. Repositories

- [ ] 7.1 Crear repositorio de RefreshToken
- [ ] 7.2 Crear repositorio de DireccionEntrega
- [ ] 7.3 Crear repositorio de UnidadMedida
- [ ] 7.4 Crear repositorio de FormaPago, EstadoPedido
- [ ] 7.5 Crear repositorio de Pedido
- [ ] 7.6 Crear repositorio de DetallePedido
- [ ] 7.7 Crear repositorio de HistorialEstadoPedido
- [ ] 7.8 Crear repositorio de Pago
- [ ] 7.9 Actualizar repositorio de Categoria, Ingrediente, Producto para nuevo soft delete y nuevos campos

## 8. Services

- [ ] 8.1 Crear/actualizar service de autenticación con RefreshToken
- [ ] 8.2 Crear service de DireccionEntrega
- [ ] 8.3 Crear service de UnidadMedida
- [ ] 8.4 Crear service de Pedido (con cálculo de montos, creación de detalle con snapshot, personalización)
- [ ] 8.5 Crear service de HistorialEstadoPedido (validación de transiciones, registro append-only)
- [ ] 8.6 Crear service de Pago
- [ ] 8.7 Actualizar services existentes (Producto, Categoria, Ingrediente) para nuevos campos

## 9. Routers (Endpoints API)

- [ ] 9.1 Agregar endpoint POST /auth/refresh para refresh tokens
- [ ] 9.2 Crear router de DireccionEntrega (/direcciones) con CRUD
- [ ] 9.3 Crear router de UnidadMedida (/unidades-medida) con CRUD
- [ ] 9.4 Crear router de FormaPago (/formas-pago) con lectura
- [ ] 9.5 Crear router de EstadoPedido (/estados-pedido) con lectura
- [ ] 9.6 Crear router de Pedido (/pedidos) con CRUD + cambio de estado + historial
- [ ] 9.7 Crear router de Pago (/pagos) con registro y consulta
- [ ] 9.8 Registrar todos los nuevos routers en main.py

## 10. Seed Data

- [ ] 10.1 Implementar seed de roles (ADMIN, STOCK, PEDIDOS, CLIENT)
- [ ] 10.2 Implementar seed de unidades de medida (kg, g, L, mL, unidad, docena, etc.)
- [ ] 10.3 Implementar seed de formas de pago (EFECTIVO, TARJETA, TRANSFERENCIA, YAPE, PLIN)
- [ ] 10.4 Implementar seed de estados de pedido (PENDIENTE, CONFIRMADO, PREPARANDO, ENVIADO, ENTREGADO, CANCELADO, RECHAZADO)
- [ ] 10.5 Implementar seed de categorías e ingredientes de ejemplo
- [ ] 10.6 Implementar seed de usuario ADMIN por defecto
- [ ] 10.7 Actualizar init_db() para ejecutar seed después de crear tablas

## 11. Tests

- [ ] 11.1 Fix test_soft_delete.py para usar deleted_at en vez de activo
- [ ] 11.2 Crear tests para autenticación con refresh tokens
- [ ] 11.3 Crear tests para CRUD de Pedido
- [ ] 11.4 Crear tests para cambio de estado y validación de transiciones
- [ ] 11.5 Crear tests para snapshot contable en DetallePedido
- [ ] 11.6 Crear tests para permisos por rol
