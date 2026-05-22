## Why

El proyecto tiene un UML que define la arquitectura de datos completa con 3 dominios y 16 tablas, pero el código actual solo implementa ~7 modelos de forma parcial. Existen bugs críticos (repositorios que referencian campos inexistentes), faltan modelos enteros de un dominio completo (Ventas, Pagos & Trazabilidad), y el modelo de Identidad & Acceso tiene diferencias estructurales importantes (relación Usuario-Rol, PK semántica). Este cambio alinea el código con el diseño UML para que la base de datos y la API reflejen fielmente la arquitectura definida.

## What Changes

### Bugs Fix
- **CategoriaRepository** e **IngredienteRepository**: usan `Modelo.activo == True` pero los modelos no tienen campo `activo` (tienen `deleted_at`). Cambiar a filtro por `deleted_at == None`.
- **test_soft_delete.py**: intenta leer `.activo` de Categoria e Ingrediente (no existe). Corregir a `deleted_at`.
- **auth/router.py**: falta definición de `router = APIRouter(...)` antes del decorador.
- **Relación Categoria-Producto**: eliminar relación directa inconsistente (Categoria tiene `productos` con `back_populates="categoria"` que no existe en Producto).

### Modelos — Dominio 1: Identidad & Acceso
- **Refactor Rol**: cambiar PK de `id` numérico a `codigo: VARCHAR(20)` (PK semántica). Valores: ADMIN, STOCK, PEDIDOS, CLIENT.
- **Refactor Usuario-Rol**: cambiar de relación 1:N directa (`usuario.rol_id`) a N:N vía tabla link **UsuarioRol**.
- **Crear UsuarioRol**: tabla link con `usuario_id` + `rol_codigo` (PK compuesta).
- **Crear RefreshToken**: tabla session para manejo de refresh tokens JWT.
- **Crear DireccionEntrega**: direcciones de entrega asociadas a usuario.

### Modelos — Dominio 2: Catálogo de Productos
- **Crear UnidadMedida**: catálogo de unidades de medida (Catalog).
- **Campos faltantes en Producto**: agregar `unidad_venta_id` (FK→UnidadMedida), `precio_base` (DECIMAL), `imagenes_url` (TEXT[]), `stock_cantidad` (INTEGER), `disponible` (BOOLEAN), timestamps (`created_at`, `updated_at`, `deleted_at`).
- **Campos faltantes en ProductoIngrediente**: agregar `cantidad` (DECIMAL), `unidad_medida_id` (FK→UnidadMedida), `es_removible` (BOOLEAN).

### Modelos — Dominio 3: Ventas, Pagos & Trazabilidad (NUEVO)
- **Crear FormaPago**: catálogo de formas de pago (Catalog).
- **Crear EstadoPedido**: catálogo de estados de pedido (Catalog).
- **Crear Pedido**: tabla principal con FK a Usuario, DireccionEntrega, EstadoPedido, FormaPago. Snapshot monetario (subtotal, descuento, costo_envio, total).
- **Crear DetallePedido**: items del pedido con PK compuesta (pedido_id + producto_id). Snapshot de nombre, precio, subtotal. Fila INMUTABLE.
- **Crear HistorialEstadoPedido**: trazabilidad append-only de cambios de estado.
- **Crear Pago**: pagos asociados a pedidos.

### Seed Data
- **seed.py**: implementar seed de roles (ADMIN, STOCK, PEDIDOS, CLIENT), categorías, ingredientes, unidades de medida, formas de pago, estados de pedido, y un usuario ADMIN inicial.

## Capabilities

### New Capabilities
- `identidad-acceso`: Gestión de identidad, autenticación JWT con refresh tokens, roles con PK semántica, y direcciones de entrega.
- `catalogo-productos`: Catálogo completo con productos, categorías jerárquicas, ingredientes, unidades de medida, stock y disponibilidad.
- `ventas-pagos`: Flujo completo de pedidos con detalle de items, historial de estados, pagos y snapshots contables.

### Modified Capabilities
- *(ninguna — es la primera versión de specs)*

## Impact

- **Models**: Se modifican Usuario, Rol, Producto, ProductoIngrediente. Se crean 9 modelos nuevos.
- **DB schema**: Cambios en tablas existentes (nuevos campos, nuevas FK). Migración requerida.
- **Auth**: Flujo JWT existente se mantiene, pero se agrega RefreshToken y se cambia relación Usuario-Rol.
- **Repositories**: Fix a CategoriaRepository e IngredienteRepository. Nuevos repos para modelos nuevos.
- **Services/Schemas/Routers**: Nuevos para Dominio 3. Actualizaciones para cambios en Dominio 1 y 2.
- **Tests**: Corrección de tests existentes. Nuevos tests para Dominio 3.
- **Seed**: Implementación completa de seed.py.
