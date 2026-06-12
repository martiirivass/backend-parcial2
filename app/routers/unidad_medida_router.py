<<<<<<< HEAD
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.database import get_session
=======
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

>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
from app.schemas.unidad_medida_schema import (
    UnidadMedidaCreate,
    UnidadMedidaRead,
    UnidadMedidaUpdate
)
<<<<<<< HEAD
from app.models.unidad_medida_model import UnidadMedida
from app.auth.permissions import require_roles
from app.models.usuario import Usuario
=======

from app.services.unidad_medida_service import (
    UnidadMedidaService
)

from app.core.unit_of_work import UnitOfWork

>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

router = APIRouter(
    prefix="/unidades-medida",
    tags=["Catálogos"]
)


<<<<<<< HEAD
@router.get("/", response_model=list[UnidadMedidaRead])
def listar(db: Session = Depends(get_session)):
    return db.exec(select(UnidadMedida)).all()


@router.get("/{unidad_id}", response_model=UnidadMedidaRead)
def obtener(unidad_id: int, db: Session = Depends(get_session)):
    unidad = db.get(UnidadMedida, unidad_id)
    if not unidad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return unidad


@router.post("/", response_model=UnidadMedidaRead, status_code=201)
def crear(
    datos: UnidadMedidaCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN", "STOCK"))
):
    unidad = UnidadMedida(**datos.model_dump())
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


@router.put("/{unidad_id}", response_model=UnidadMedidaRead)
=======
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
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
def actualizar(
    unidad_id: int,
    datos: UnidadMedidaUpdate,
    db: Session = Depends(get_session),
<<<<<<< HEAD
    current_user: Usuario = Depends(require_roles("ADMIN", "STOCK"))
):
    unidad = db.get(UnidadMedida, unidad_id)
    if not unidad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    for key, val in datos.model_dump(exclude_unset=True).items():
        setattr(unidad, key, val)
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


@router.delete("/{unidad_id}", status_code=204)
def eliminar(
    unidad_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN"))
):
    unidad = db.get(UnidadMedida, unidad_id)
    if not unidad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    db.delete(unidad)
    db.commit()
=======
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

        db.refresh(unidad)

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
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
