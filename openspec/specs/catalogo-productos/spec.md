# catalogo-productos Specification

## Purpose
TBD - created by archiving change align-modelos-con-uml. Update Purpose after archive.
## Requirements
### Requirement: Producto con campos completos
El sistema SHALL almacenar productos con los campos: id, nombre (VARCHAR 150), descripción, precio_base (DECIMAL 10,2), unidad_venta_id (FK→UnidadMedida), imágenes_url (TEXT[]), stock_cantidad (INTEGER, DEFAULT 0), disponible (BOOLEAN, DEFAULT true), created_at, updated_at, deleted_at.

#### Scenario: Crear producto completo
- **WHEN** un ADMIN crea un producto con nombre, precio_base, unidad_venta y stock_cantidad
- **THEN** el producto se crea con disponible=true, created_at y updated_at asignados

#### Scenario: stock_cantidad y disponible son independientes
- **WHEN** un producto tiene stock_cantidad=0 y disponible=true
- **THEN** el producto se muestra como "Sin stock" pero puede recibir reposición
- **WHEN** un producto tiene stock_cantidad>0 y disponible=false
- **THEN** el producto está deshabilitado por el operador y no se puede vender

### Requirement: Categorías jerárquicas
El sistema SHALL soportar categorías anidadas mediante parent_id autorreferencial.

#### Scenario: Crear subcategoría
- **WHEN** un ADMIN crea una categoría con parent_id existente
- **THEN** la categoría se crea como subcategoría de la categoría padre

#### Scenario: Categoría raíz
- **WHEN** un ADMIN crea una categoría sin parent_id
- **THEN** la categoría se crea como categoría raíz

### Requirement: Ingredientes con soft delete
El sistema SHALL gestionar ingredientes con nombre, descripción, es_alergeno (BOOLEAN) y deleted_at.

#### Scenario: Crear ingrediente
- **WHEN** un ADMIN crea un ingrediente con nombre y es_alergeno
- **THEN** el ingrediente se crea y puede asociarse a productos

### Requirement: Productos se relacionan N:N con categorías e ingredientes
El sistema SHALL relacionar productos con múltiples categorías e ingredientes mediante tablas link (ProductoCategoria, ProductoIngrediente).

#### Scenario: Asignar categorías a producto
- **WHEN** un ADMIN crea un producto con categoria_ids
- **THEN** el producto queda asociado a todas las categorías indicadas

#### Scenario: Asignar ingredientes con cantidad y unidad
- **WHEN** un ADMIN asocia un ingrediente a un producto
- **THEN** puede especificar cantidad, unidad_medida_id y si es removible por el cliente

### Requirement: UnidadMedida como catálogo
El sistema SHALL mantener un catálogo de unidades de medida (kg, g, L, mL, unidad, docena, etc.).

#### Scenario: Unidades precargadas
- **WHEN** se inicializa la base de datos
- **THEN** las unidades de medida comunes existen en el catálogo

### Requirement: Soft delete con deleted_at
El sistema SHALL usar `deleted_at: TIMESTAMPTZ` para borrado lógico en todas las tablas Table.

#### Scenario: Eliminar producto
- **WHEN** un ADMIN elimina un producto
- **THEN** el producto tiene deleted_at asignado con la fecha actual y NO aparece en consultas normales

#### Scenario: Consultar solo activos
- **WHEN** se listan productos
- **THEN** solo se retornan aquellos con deleted_at IS NULL

