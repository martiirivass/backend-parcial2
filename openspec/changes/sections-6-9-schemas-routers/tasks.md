## Section 6 — Schemas (Pydantic/SQLModel)

- [x] 6.1 Actualizar `producto_schema.py`: `imagen_url` ya estaba en `ProductoBase` (ok)
- [x] 6.2 Crear `unidad_medida_schema.py`: UnidadMedidaCreate, UnidadMedidaRead, UnidadMedidaUpdate
- [x] 6.3 Crear `forma_pago_schema.py`: FormaPagoRead (solo lectura, PK semántica codigo)
- [x] 6.4 Crear `estado_pedido_schema.py`: EstadoPedidoRead (solo lectura, PK semántica codigo)
- [x] 6.5 Crear `pago_schema.py`: PagoCreate, PagoRead
- [x] 6.6 Crear `refresh_token_schema.py`: RefreshTokenCreate, RefreshTokenRead
- [x] 6.7 Actualizar `pedido_schema.py`: alinear con modelos reales (forma_pago_codigo, estado_codigo, direccion_id, subtotal_snap, nombre_snapshot, precio_snapshot)
- [x] 6.8 Crear `historial_estado_schema.py`: HistorialEstadoRead con estado_codigo
- [x] 6.9 Actualizar `__init__.py` de schemas con nuevos exports + model_rebuild

## Section 9 — Routers & Endpoints

- [x] 9.1 Crear `unidad_medida_router.py`: CRUD completo con permisos ADMIN/STOCK
- [x] 9.2 Crear `forma_pago_router.py`: GET listar/obtener formas de pago (público)
- [x] 9.3 Crear `estado_pedido_router.py`: GET listar/obtener estados de pedido (público)
- [x] 9.4 Crear `pago_router.py`: POST registrar, GET listar/filtrar por pedido
- [x] 9.5 Agregar POST /auth/refresh en `auth/router.py` con rotación de tokens
- [x] 9.6 Crear `refresh_token_repository.py` para validar/revocar tokens
- [x] 9.7 Crear `pago_repository.py` + `pago_service.py` con validación de montos
- [x] 9.8 Actualizar `pedido_repository.py`: fix `activo` → `deleted_at`
- [x] 9.9 Actualizar `pedido_service.py`: fix referencias (estado_codigo, forma_pago_codigo, nombre_snapshot, subtotal_snap)
- [x] 9.10 Actualizar `main.py`: registrar todos los routers

## Bonus — Bugs encontrados y corregidos

- [x] Fix `usuario.py`: `DireccionEntrega` → `Direccion` (import roto)
- [x] Fix `usuario.py`: agregar `tiene_rol()` method + `roles` property
- [x] Fix `historial_estado_model.py`: `estado_pedido_id` → `estado_codigo` (FK inexistente)
- [x] Fix `pago_model.py`: `forma_pago_id` → `forma_pago_codigo` (FK inexistente)
- [x] Fix `seed.py`: `roles=[rol_admin]` → crear `UsuarioRol` explícitamente
- [x] Fix `pedido_router.py`: `PedidoReadWithDetalles` → `PedidoReadWithDetails`
- [x] Fix login: emitir refresh_token cookie junto con access_token
