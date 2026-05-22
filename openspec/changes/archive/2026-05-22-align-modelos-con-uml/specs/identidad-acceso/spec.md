## ADDED Requirements

### Requirement: Registro de usuarios
El sistema SHALL permitir registrar usuarios con nombre, apellido, email y password (hasheada con bcrypt).

#### Scenario: Registro exitoso
- **WHEN** un usuario envía nombre, apellido, email y password válidos
- **THEN** el sistema crea el usuario con password hasheada y retorna los datos del usuario sin la password

#### Scenario: Email duplicado
- **WHEN** un usuario intenta registrarse con un email ya existente
- **THEN** el sistema rechaza el registro con error 409

### Requirement: Inicio de sesión con JWT
El sistema SHALL autenticar usuarios mediante email y password, retornando un JWT access token en cookie HttpOnly.

#### Scenario: Login exitoso
- **WHEN** un usuario envía email y password correctos
- **THEN** el sistema retorna un JWT access token con expiración de 30 minutos en cookie HttpOnly

#### Scenario: Credenciales inválidas
- **WHEN** un usuario envía email o password incorrectos
- **THEN** el sistema retorna error 401

### Requirement: Refresh tokens
El sistema SHALL implementar refresh tokens para renovar access tokens sin requerir login.

#### Scenario: Refresh exitoso
- **WHEN** un usuario envía un refresh token válido
- **THEN** el sistema invalida el refresh token anterior y emite un nuevo par (access + refresh)

#### Scenario: Refresh token inválido
- **WHEN** un usuario envía un refresh token expirado o inválido
- **THEN** el sistema retorna error 401

### Requirement: Roles con PK semántica
El sistema SHALL usar `codigo: VARCHAR(20)` como PK en la tabla Rol. Los roles seed son ADMIN, STOCK, PEDIDOS, CLIENT.

#### Scenario: Roles precargados
- **WHEN** se inicializa la base de datos
- **THEN** los roles ADMIN, STOCK, PEDIDOS, CLIENT existen con sus códigos como PK

#### Scenario: Payload JWT con roles
- **WHEN** un usuario autenticado tiene roles asignados
- **THEN** el payload del JWT SHALL incluir los códigos de rol en formato legible

### Requirement: Usuarios pueden tener múltiples roles (N:N)
El sistema SHALL soportar que un usuario tenga múltiples roles mediante la tabla link UsuarioRol.

#### Scenario: Asignar múltiples roles
- **WHEN** un ADMIN asigna los roles STOCK y PEDIDOS a un usuario
- **THEN** el usuario queda con ambos roles y puede acceder a las funcionalidades de ambos

#### Scenario: Verificar permiso por rol
- **WHEN** un usuario intenta acceder a un endpoint protegido
- **THEN** el sistema verifica si el usuario tiene al menos uno de los roles requeridos

### Requirement: Direcciones de entrega
El sistema SHALL permitir que cada usuario tenga múltiples direcciones de entrega.

#### Scenario: Crear dirección
- **WHEN** un usuario crea una dirección con calle, ciudad, código postal y país
- **THEN** la dirección se asocia al usuario

#### Scenario: Seleccionar dirección en pedido
- **WHEN** un usuario crea un pedido
- **THEN** puede seleccionar una de sus direcciones guardadas como destino
