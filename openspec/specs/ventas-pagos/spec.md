# ventas-pagos Specification

## Purpose
TBD - created by archiving change align-modelos-con-uml. Update Purpose after archive.
## Requirements
### Requirement: FormaPago como catálogo
El sistema SHALL mantener un catálogo de formas de pago con PK semántica (codigo: VARCHAR 20).

#### Scenario: Formas de pago precargadas
- **WHEN** se inicializa la base de datos
- **THEN** existen formas de pago como EFECTIVO, TARJETA, TRANSFERENCIA, YAPE, PLIN

### Requirement: EstadoPedido como catálogo
El sistema SHALL mantener un catálogo de estados de pedido con PK semántica (codigo: VARCHAR 20).

#### Scenario: Estados de pedido precargados
- **WHEN** se inicializa la base de datos
- **THEN** existen estados: PENDIENTE, CONFIRMADO, PREPARANDO, ENVIADO, ENTREGADO, CANCELADO, RECHAZADO

### Requirement: Creación de pedidos
El sistema SHALL crear pedidos con referencia al usuario, dirección de entrega, estado, forma de pago y montos.

#### Scenario: Crear pedido
- **WHEN** un CLIENT crea un pedido con productos, dirección y forma de pago
- **THEN** el sistema crea el pedido con estado PENDIENTE, calcula subtotal desde los precios snapshot, asigna costo_envio=50.00, y total = subtotal - descuento + costo_envio

#### Scenario: Pedido tiene snapshot contable
- **WHEN** se crea un pedido
- **THEN** subtotal, descuento (0.00), costo_envio (50.00) y total son inmutables y no cambian aunque los precios de productos cambien después

### Requirement: DetallePedido con snapshot y personalización
El sistema SHALL crear items de pedido con snapshot de nombre, precio y subtotal, y opcionalmente ingredientes removidos.

#### Scenario: Crear detalle con snapshot
- **WHEN** un CLIENT agrega un producto al pedido
- **THEN** se crea un DetallePedido con nombre_snapshot, precio_snapshot (desde Producto.precio_base), cantidad, subtotal_snap = precio_snapshot * cantidad

#### Scenario: Personalizar removiendo ingredientes
- **WHEN** un CLIENT personaliza un producto removiendo ingredientes con es_removible=true
- **THEN** el detalle guarda un array personalizacion con los IDs de ingredientes removidos

#### Scenario: DetallePedido es inmutable
- **WHEN** un DetallePedido es creado
- **THEN** NO puede ser modificado (no tiene updated_at, solo created_at)
- **THEN** SOLO puede ser eliminado junto con el pedido (CASCADE)

### Requirement: Flujo de cambios de estado con trazabilidad
El sistema SHALL registrar cada cambio de estado de un pedido en HistorialEstadoPedido (append-only).

#### Scenario: Avanzar estado
- **WHEN** un usuario con rol PEDIDOS cambia el estado de CONFIRMADO a PREPARANDO
- **THEN** el sistema actualiza Pedido.estado_codigo Y crea un registro en HistorialEstadoPedido con el estado anterior, el nuevo, el usuario que lo cambió y el timestamp

#### Scenario: Consultar historial
- **WHEN** se consulta el historial de un pedido
- **THEN** se retornan todos los cambios de estado en orden cronológico, desde la creación hasta el estado actual

#### Scenario: Transiciones válidas
- **WHEN** se intenta cambiar de ENTREGADO a CONFIRMADO
- **THEN** el sistema rechaza la transición por ser inválida (no se puede retroceder)

### Requirement: Pagos asociados a pedidos
El sistema SHALL registrar pagos asociados a pedidos con monto, forma de pago y referencia externa.

#### Scenario: Registrar pago
- **WHEN** un pedido es confirmado
- **THEN** se puede registrar un pago con monto, forma_pago_codigo y referencia opcional

#### Scenario: Múltiples pagos por pedido
- **WHEN** un pedido tiene un total mayor a cero
- **THEN** se pueden registrar múltiples pagos hasta cubrir el total

### Requirement: Roles y permisos en pedidos
El sistema SHALL restringir operaciones sobre pedidos según el rol del usuario.

#### Scenario: CLIENT ve solo sus pedidos
- **WHEN** un usuario con rol CLIENT lista pedidos
- **THEN** solo ve sus propios pedidos

#### Scenario: ADMIN ve todos los pedidos
- **WHEN** un usuario con rol ADMIN lista pedidos
- **THEN** ve todos los pedidos del sistema

#### Scenario: PEDIDOS avanza estados
- **WHEN** un usuario con rol PEDIDOS opera sobre un pedido
- **THEN** puede avanzar el estado de CONFIRMADO a ENTREGADO (no puede crear pedidos)

