## Why

Los modelos ya están alineados al UML (secciones 1-5), pero los schemas Pydantic y algunos routers/endpoints están desactualizados o no existen. Sin schemas correctos, la API devuelve datos inconsistentes y no se pueden crear/actualizar registros correctamente.

## What Changes

- Crear schemas faltantes: UnidadMedida, FormaPago, EstadoPedido, Pago, RefreshToken
- Actualizar pedido_schema.py para alinear con los modelos reales (forma_pago_codigo, estado_codigo, deleted_at, etc.)
- Crear routers faltantes: UnidadMedida (CRUD), FormaPago (lectura), EstadoPedido (lectura), Pago (registro+consulta)
- Agregar endpoint POST /auth/refresh para refresh tokens
- Crear repositorios faltantes: PagoRepository, RefreshTokenRepository
- Registrar todos los routers en main.py
- Fix pedido_repository.py (usa activo inexistente)
- Fix pedido_service.py (referencias incorrectas)

## Capabilities

### New Capabilities
- `schemas-catalogos`: Schemas Pydantic para catálogos (UnidadMedida, FormaPago, EstadoPedido)
- `schemas-ventas`: Schemas Pydantic para ventas (Pedido, DetallePedido, HistorialEstado, Pago)
- `schemas-auth`: Schemas Pydantic para RefreshToken
- `routers-catalogos`: Endpoints CRUD/lectura para catálogos
- `routers-ventas`: Endpoints para Pago
- `routers-auth`: Endpoint POST /auth/refresh

### Modified Capabilities
- `catalogo-productos`: Schemas de Producto actualizados con campos nuevos
- `ventas-pagos`: Schemas de Pedido/DetallePedido/HistorialEstado actualizados

## Impact

- `app/schemas/`: 6 archivos nuevos, 1 actualizado
- `app/routers/`: 4 archivos nuevos, 1 actualizado (pedido_router)
- `app/repositories/`: 2 archivos nuevos, 1 actualizado (pedido_repository)
- `app/services/`: 1 actualizado (pedido_service)
- `app/auth/router.py`: 1 endpoint nuevo
- `app/main.py`: Registro de routers
