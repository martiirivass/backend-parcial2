from fastapi import (
    APIRouter,
    Depends
)

from sqlmodel import Session

from app.auth.permissions import (
    require_roles
)

from app.db.database import (
    get_session
)

from app.models.usuario import Usuario

from app.schemas.unidad_medida_schema import (
    UnidadMedidaCreate,
    UnidadMedidaRead,
    UnidadMedidaUpdate
)

from app.services.unidad_medida_service import (
    UnidadMedidaService
)

from app.core.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/unidades-medida",
    tags=["Catálogos"]
)


# Listar
@router.get(
    "/",
    response_model=list[UnidadMedidaRead]
)
def listar(
    db: Session = Depends(get_session)
):

    service = UnidadMedidaService(db)

    return service.listar()


# Obtener
@router.get(
    "/{unidad_id}",
    response_model=UnidadMedidaRead
)
def obtener(
    unidad_id: int,
    db: Session = Depends(get_session)
):

    service = UnidadMedidaService(db)

    return service.obtener(
        unidad_id
    )


# Crear
@router.post(
    "/",
    response_model=UnidadMedidaRead,
    status_code=201
)
def crear(
    datos: UnidadMedidaCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles(
            "ADMIN",
            "STOCK"
        )
    )
):

    with UnitOfWork(db):

        service = UnidadMedidaService(db)

        unidad = service.crear(
            datos
        )

    db.refresh(unidad)

    return unidad


# Actualizar
@router.put(
    "/{unidad_id}",
    response_model=UnidadMedidaRead
)
def actualizar(
    unidad_id: int,
    datos: UnidadMedidaUpdate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles(
            "ADMIN",
            "STOCK"
        )
    )
):

    with UnitOfWork(db):

        service = UnidadMedidaService(db)

        unidad = service.actualizar(
            unidad_id,
            datos
        )

    return unidad


# Eliminar
@router.delete(
    "/{unidad_id}",
    status_code=204
)
def eliminar(
    unidad_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = UnidadMedidaService(db)

        service.eliminar(
            unidad_id
        )
