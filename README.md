# Food Store — API Backend

[GitHub](https://github.com/martiirivass/backend-parcial2)

Backend REST de Food Store, una aplicación de gestión de pedidos para delivery. Construido con **FastAPI**, **SQLModel** y **PostgreSQL**, con integración de pagos vía **MercadoPago** y notificaciones en tiempo real via **WebSocket**.

---

## Stack

| Tecnología       | Versión     | Propósito                          |
|------------------|-------------|------------------------------------|
| FastAPI          | 0.136+      | Framework web asincrónico          |
| SQLModel         | 0.0.38+     | ORM basado en SQLAlchemy + Pydantic|
| PostgreSQL       | 15+         | Base de datos relacional           |
| SQLAlchemy       | 2.0+        | Motor de base de datos             |
| PyJWT            | 2.12+       | Autenticación por tokens JWT       |
| Passlib          | 1.7+        | Hashing de contraseñas             |
| MercadoPago SDK  | 2.3+        | Integración con MercadoPago        |
| Uvicorn          | 0.44+       | Servidor ASGI                      |
| Pydantic         | 2.13+       | Validación de datos y settings     |
| python-multipart | 0.0.20+     | Soporte para subida de archivos    |
| Cloudinary SDK   | 1.44+       | Almacenamiento de imágenes en CDN  |

---

## Requisitos

- **Python 3.12+**
- **PostgreSQL 15+**
- pip / venv (o similar)

---

## Instalación

```bash
cd backend/backend-parcial2
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

---

## Environment Variables

Crear un archivo `.env` en la raíz del proyecto (`backend/backend-parcial2/.env`) a partir de `.env.example`:

```bash
copy .env.example .env      # Windows
```

| Variable              | Descripción                                              | Ejemplo                                                    |
|-----------------------|----------------------------------------------------------|------------------------------------------------------------|
| `DATABASE_URL`        | Cadena de conexión a PostgreSQL                          | `postgresql://user:password@localhost:5432/foodstore_db`   |
| `SECRET_KEY`          | Clave secreta para firmar JWT (mínimo 32 caracteres)     | `your-super-secret-key-min-32-chars`                       |
| `CORS_ORIGINS`        | JSON array de orígenes permitidos                        | `["http://localhost:5173","http://localhost:5174"]`        |
| `MP_ACCESS_TOKEN`     | Access Token de MercadoPago (para cobros)                | `TEST-123456789-...`                                       |
| `MP_PUBLIC_KEY`       | Public Key de MercadoPago (para frontend)                | `TEST-...`                                                 |
| `MP_NOTIFICATION_URL` | URL del webhook para recibir notificaciones de MP        | `https://tu-dominio.com/api/v1/pagos/webhook`              |
| `CLOUDINARY_CLOUD_NAME` | Cloud name del account de Cloudinary                  | `mi-cloud`                                                 |
| `CLOUDINARY_API_KEY` | API Key de Cloudinary                                     | `123456789123456`                                          |
| `CLOUDINARY_API_SECRET` | API Secret de Cloudinary                               | `abc123def456`                                             |

---

## Setup

### 1. Base de datos

Crear la base de datos en PostgreSQL:

```sql
CREATE DATABASE foodstore_db;
```

### 2. Configurar `.env`

Editar `DATABASE_URL` en `.env` con los datos de conexión reales.

### 3. Ejecutar seed

El seed carga datos iniciales: roles, estados de pedido, formas de pago, unidades de medida, categorías, ingredientes, productos de ejemplo y un usuario administrador.

```bash
python -m app.db.seed
```

También se ejecuta **automáticamente** en el primer inicio del servdor (via `init_db()` en el evento `startup`).

### 4. Iniciar servidor

```bash
uvicorn app.main:app --reload
```

El servidor se levanta en `http://localhost:8000`.

---

## Seed (`python -m app.db.seed`)

El script de seed (`app/db/seed.py`) carga los siguientes datos:

| Tipo                | Descripción                                          |
|---------------------|------------------------------------------------------|
| **Roles**           | ADMIN, STOCK, PEDIDOS, CLIENT                        |
| **Estados pedido**  | PENDIENTE, CONFIRMADO, EN_PREP, ENTREGADO, CANCELADO |
| **Formas de pago**  | EFECTIVO, TRANSFERENCIA, MERCADOPAGO                 |
| **Unidades medida** | kg, g, L, ml, ud, porciones                          |
| **Admin user**      | `admin@foodstore.com` / `Admin1234!`                 |
| **Categorías**      | Hamburguesas, Pizzas, Bebidas, Postres, etc.         |
| **Ingredientes**    | Carne, pan, quesos, verduras, masa, etc.             |
| **Productos**       | Clasica Burger, Bacon Cheese, Pizzas, Papas, Ensalada|

> El seed es **idempotente**: si el dato ya existe, lo saltea.

---

## Documentación interactiva (Swagger)

- **Swagger UI**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

Ambos muestran todos los endpoints organizados bajo el prefijo `/api/v1/`.

---

## MercadoPago

Integración con MercadoPago a través del SDK oficial (`mercadopago==2.3.0`).

### Endpoints

| Método | Ruta                                    | Descripción                          |
|--------|-----------------------------------------|--------------------------------------|
| POST   | `/api/v1/pagos/crear-preferencia`       | Crea una preferencia de pago en MP   |
| POST   | `/api/v1/pagos/webhook`                 | Recibe notificaciones IPN de MP      |
| GET    | `/api/v1/pagos/{pedido_id}`             | Consulta el estado del pago del pedido|

### Flujo

1. El frontend solicita crear una preferencia → backend devuelve `preference_id` e `init_point`.
2. El frontend redirige al checkout de MercadoPago.
3. MercadoPago envía notificaciones al webhook configurado en `MP_NOTIFICATION_URL`.
4. El backend actualiza el estado del pago y del pedido automáticamente.

---

## Cloudinary

Las imágenes de productos y categorías se almacenan en **Cloudinary** (CDN) cuando está configurado. Si no hay credenciales Cloudinary, el sistema cae automáticamente al almacenamiento local (`uploads/`).

### Configuración

1. Crear una cuenta gratuita en [Cloudinary](https://cloudinary.com)
2. Copiar las credenciales del Dashboard (`Cloud name`, `API Key`, `API Secret`)
3. Agregarlas al `.env`:

```env
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

### Comportamiento

| Condición | Almacenamiento | URL retornada |
|-----------|---------------|---------------|
| Cloudinary configurado | Cloudinary CDN | `https://res.cloudinary.com/...` |
| Cloudinary NO configurado | Local (`uploads/`) | `/api/v1/uploads/...` |

### Estructura en Cloudinary

```
foodstore/
├── productos/    → Imágenes de productos
└── categorias/   → Imágenes de categorías
```

---

## WebSocket

Conexiones en tiempo real para notificaciones de pedidos.

| Ruta                       | Quién conecta     | Propósito                             |
|----------------------------|-------------------|---------------------------------------|
| `/ws/pedidos`              | Panel admin       | Recibe TODOS los cambios de pedidos   |
| `/ws/pedidos/{pedido_id}`  | Cliente (store)   | Recibe cambios de su pedido específico|

Los mensajes se emiten en formato JSON con tipo de evento y datos del pedido.

---

## Estructura del proyecto

Organización por módulos (feature-first):

```
backend-parcial2/
├── app/
│   ├── auth/                # Autenticación (login, register, refresh, permissions)
│   │   ├── router.py
│   │   ├── services.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── permissions.py
│   ├── core/                # Configuración, UoW, WebSocket manager
│   │   ├── config.py
│   │   ├── unit_of_work.py
│   │   └── ws_manager.py
│   ├── db/                  # Base de datos, inicialización y seed
│   │   ├── database.py
│   │   ├── init_db.py
│   │   └── seed.py
│   ├── models/              # Entidades SQLModel
│   │   ├── usuario.py
│   │   ├── producto_model.py
│   │   ├── pedido_model.py
│   │   └── ...
│   ├── pagos/               # Integración MercadoPago
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── schemas.py
│   ├── repositories/        # Capa de acceso a datos
│   │   ├── base.py
│   │   ├── producto_repository.py
│   │   ├── pedido_repository.py
│   │   └── ...
│   ├── routers/             # Endpoints REST
│   │   ├── producto_router.py
│   │   ├── pedido_router.py
│   │   ├── ws_router.py
│   │   └── ...
│   ├── schemas/             # Pydantic request/response
│   │   ├── producto_schema.py
│   │   ├── pedido_schema.py
│   │   └── ...
│   ├── services/            # Lógica de negocio
│   │   ├── producto_service.py
│   │   ├── pedido_service.py
│   │   ├── imagen_service.py
│   │   ├── cloudinary_service.py
│   │   └── ...
│   └── main.py              # Punto de entrada de la aplicación
├── uploads/                 # Archivos subidos (imágenes)
├── .env                     # Variables de entorno (no versionado)
├── .env.example             # Template de variables de entorno
├── requirements.txt         # Dependencias
└── README.md                # Este archivo
```

---

## Arquitectura

```
 ┌──────────┐     ┌──────────┐     ┌─────────┐     ┌────────────┐     ┌─────────┐
 │  Router  │────▶│ Service  │────▶│   UoW   │────▶│ Repository │────▶│  Model  │
 │(FastAPI) │     │(negocio) │     │(tx mgmt)│     │  (datos)   │     │ (SQLM)  │
 └──────────┘     └──────────┘     └─────────┘     └────────────┘     └─────────┘
```

- **Router**: Define endpoints, valida input con Pydantic, delega al Service.
- **Service**: Contiene la lógica de negocio, orquesta operaciones.
- **UoW** (Unit of Work): Maneja transacciones (commit/rollback) automáticamente.
- **Repository**: Acceso a datos (CRUD), abstrae consultas SQLModel.
- **Model**: Entidades SQLAlchemy/SQLModel que mapean a tablas.

---

## Endpoints principales

Todos los endpoints REST están bajo el prefijo `/api/v1/`.

### Auth
| Método | Ruta                       | Descripción                    |
|--------|----------------------------|--------------------------------|
| POST   | `/api/v1/auth/register`    | Registro de usuario            |
| POST   | `/api/v1/auth/login`       | Inicio de sesión               |
| POST   | `/api/v1/auth/refresh`     | Refrescar token JWT            |

### Productos
| Método | Ruta                                       | Descripción                     |
|--------|--------------------------------------------|---------------------------------|
| GET    | `/api/v1/productos`                        | Listar productos                |
| GET    | `/api/v1/productos/{id}`                   | Obtener producto por ID         |
| POST   | `/api/v1/productos`                        | Crear producto (admin)          |
| PUT    | `/api/v1/productos/{id}`                   | Actualizar producto (admin)     |
| DELETE | `/api/v1/productos/{id}`                   | Soft delete (admin)             |
| GET    | `/api/v1/productos/{id}/ingredientes`      | Listar ingredientes del producto |
| POST   | `/api/v1/productos/{id}/ingredientes`      | Agregar ingrediente (admin)     |

### Pedidos
| Método | Ruta                                      | Descripción                     |
|--------|-------------------------------------------|---------------------------------|
| GET    | `/api/v1/pedidos`                         | Listar pedidos (admin)          |
| POST   | `/api/v1/pedidos`                         | Crear pedido (cliente)          |
| GET    | `/api/v1/pedidos/{id}`                    | Obtener pedido por ID           |
| PUT    | `/api/v1/pedidos/{id}/estado`             | Cambiar estado (admin)          |
| DELETE | `/api/v1/pedidos/{id}`                    | Eliminar pedido (cliente propio)|
| PATCH  | `/api/v1/pedidos/{id}/cancelar`           | Cancelar pedido con motivo      |
| PATCH  | `/api/v1/pedidos/{id}/estado`             | Avanzar estado (admin)          |

---

## Integrantes

- **Rivas Martiniano**
- **Fracchia Gonzalo**
- **Scopel Maximo**
- **Dengra Enzo**

---

## Video demostración

[https://drive.google.com/file/d/18-4ZufOsukykmeYCd8krtd8QTFW80Ayd/view?usp=sharing](https://drive.google.com/file/d/18-4ZufOsukykmeYCd8krtd8QTFW80Ayd/view?usp=sharing)
