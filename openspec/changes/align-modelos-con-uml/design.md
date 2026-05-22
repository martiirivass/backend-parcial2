## Context

El proyecto es una API FastAPI + SQLModel para un sistema de pedidos con 3 dominios: Identidad & Acceso, Catálogo de Productos, y Ventas, Pagos & Trazabilidad. Actualmente solo existe implementación parcial del Catálogo de Productos y un esqueleto de autenticación. El UML diseñado define 16 tablas con estereotipos específicos (Table, Catalog, Link, Session, Append) que deben respetarse.

La base de datos es PostgreSQL vía SQLModel con psycopg3. El patrón arquitectónico es capas: Models → Repositories → Services → Routers, con UnitOfWork para manejo transaccional y SQLModel para definición de esquemas y relaciones.

## Goals / Non-Goals

**Goals:**
- Alinear todos los modelos SQLModel con el diseño UML (16 tablas, campos, tipos, relaciones)
- Corregir bugs existentes (repositorios con campos inexistentes, relaciones mal definidas)
- Implementar el Dominio 3 completo (Ventas, Pagos & Trazabilidad)
- Agregar timestamps de auditoría (created_at, updated_at, deleted_at) a todas las tablas
- Implementar seed.py con datos iniciales según especificación del UML
- Preservar la arquitectura existente (capas, UnitOfWork, validaciones)

**Non-Goals:**
- No cambiar el sistema de autenticación JWT existente (solo extender con RefreshToken)
- No implementar lógica de negocio compleja (ej: cálculos de descuento, integración con pasarela de pagos real)
- No crear migraciones automáticas (se usará `SQLModel.metadata.create_all`)
- No implementar UI ni endpoints de frontend

## Decisions

### 1. PK semántica para catálogos (Rol, FormaPago, EstadoPedido)
**Decisión**: Usar `codigo: VARCHAR(20)` como PK en tablas Catalog (Rol, FormaPago, EstadoPedido) en lugar de `id: BIGSERIAL`.
**Rationale**: El UML especifica PK semántica para que el código sea legible en JWTs (`{ roles: ["ADMIN"] }`) y en URLs. Simplifica debugging y evita joins innecesarios.
**Alternativa considerada**: Mantener `id` numérico + `codigo` único. Descartado porque el UML es explícito en usar `{PK, seed}` y la nota sobre payload JWT.

### 2. Usuario-Rol como relación N:N vía UsuarioRol
**Decisión**: Reemplazar `Usuario.rol_id: FK → Rol.id` por tabla link `UsuarioRol(usuario_id, rol_codigo)`.
**Rationale**: Un usuario puede tener múltiples roles (ej: ADMIN + STOCK). El UML modela esto con estereotipo «Link».
**Impacto**: Cambia la estructura de `get_current_user` en auth/dependencies.py y `require_roles` en permissions.py.

### 3. Soft delete unificado
**Decisión**: Usar `deleted_at: Optional[datetime]` para soft delete en TODAS las tablas (reemplazar `activo: bool` en Producto).
**Rationale**: El UML especifica `deleted_at: TIMESTAMPTZ` en las tablas con auditoría. Unificar el mecanismo evita tener dos estrategias de borrado lógico.
**Excepción**: `disponible: BOOLEAN` en Producto se mantiene como flag de negocio independiente (un producto puede tener stock=0 y disponible=true, o viceversa).

### 4. Snapshot contable en Pedido y DetallePedido
**Decisión**: Los campos `precio_base → precio_snapshot`, `nombre → nombre_snapshot` y montos en Pedido son inmutables después de la creación del pedido.
**Rationale**: Integridad contable. Si el precio de un producto cambia después, los pedidos ya creados deben mantener el valor original. El UML marca estos campos con `{snap}`.
**Implementación**: DetallePedido NO tiene `updated_at` (es append-only). Los snapshots se copian del producto al crear el detalle.

### 5. HistorialEstadoPedido como tabla Append-Only
**Decisión**: `HistorialEstadoPedido` solo permite INSERT, nunca UPDATE o DELETE.
**Rationale**: Trazabilidad de cambios de estado. Cada cambio de estado es un evento inmutable. El UML marca con estereotipo «Append».
**Implementación**: El servicio de Pedido crea un registro en HistorialEstadoPedido cada vez que `pedido.estado_codigo` cambia.

### 6. UnidadMedida como catálogo compartido
**Decisión**: `UnidadMedida` es un catálogo (estereotipo «Catalog») referenciado tanto por `Producto.unidad_venta_id` como por `ProductoIngrediente.unidad_medida_id`.
**Rationale**: Una unidad de medida (kg, g, L, mL, unidad) debe ser consistente entre el producto y sus ingredientes. Evita duplicación.

### 7. ProductoIngrediente con atributos propios
**Decisión**: `ProductoIngrediente` no es solo una tabla link, tiene atributos (`cantidad`, `unidad_medida_id`, `es_removible`).
**Rationale**: El UML define estos campos. Un ingrediente puede ser removible por el cliente (ej: cebolla en una hamburguesa) o no. La cantidad permite especificar proporciones.

### 8. Timestamps en todas las tablas Table
**Decisión**: Toda tabla con estereotipo «Table» lleva `created_at`, `updated_at`, `deleted_at` (TIMESTAMPTZ).
**Rationale**: Auditoría y soft delete consistente. Tablas Catalog y Link NO llevan timestamps (son datos de referencia).
**Excepción**: DetallePedido solo lleva `created_at` (es inmutable, no tiene `updated_at`).

## Risks / Trade-offs

- **[Riesgo] Cambio de PK en Rol** → Todas las FK y relaciones existentes que referencien `Rol.id` se rompen. **Mitigación**: Cambiar a `codigo` como PK antes de crear nuevas tablas. Exportar datos existentes si los hay.
- **[Riesgo] Soft break en auth** → `get_current_user` y `require_roles` dependen de `usuario.rol_id` y `usuario.rol.codigo`. **Mitigación**: Actualizar estas dependencias cuando se refactorice a N:N vía UsuarioRol.
- **[Riesgo] Migración de datos** → Si hay datos en BD, cambiar `activo → deleted_at` en Producto y renombrar `precio → precio_base` requiere migración. **Mitigación**: Por ahora se trabaja con `SQLModel.metadata.create_all` (schema desde cero). Documentar para futuro.
- **[Trade-off] Un solo cambio grande** vs múltiples cambios chicos. Se eligió uno solo porque toca múltiples dominios interconectados (cambiar Rol afecta Usuario-Rol, que afecta auth, etc.). Preferible hacer todo junto a tener cambios parciales que dejen la app en estado inconsistente.
