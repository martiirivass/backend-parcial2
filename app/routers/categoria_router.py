from fastapi import (
    APIRouter,
    Query,
    Depends,
    UploadFile,
    File
)

from typing import (
    Annotated,
    List,
    Optional
)

from sqlmodel import Session

from app.db.database import get_session

from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaRead,
    CategoriaTree
)

from app.services.categoria_service import (
    CategoriaService
)

from app.auth.permissions import (
    require_roles
)

from app.core.unit_of_work import (
    UnitOfWork
)

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)


# Crear categoría
@router.post(
    "/",
    response_model=CategoriaRead,
    status_code=201
)
def crear(
    categoria: CategoriaCreate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    service = CategoriaService(db)

    with UnitOfWork(db):

        nueva_categoria = service.crear_categoria(
            categoria
        )

    db.refresh(
        nueva_categoria
    )

    return nueva_categoria


# Listar categorías con filtro por parent_id (publico)
@router.get("/")
def listar(
    limit: Annotated[int, Query(le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    parent_id: Optional[int] = Query(
        None,
        description="Filtrar por categoria padre"
    ),
    db: Session = Depends(get_session)
):

    service = CategoriaService(db)

    return service.listar_categorias(
        limit,
        offset,
        parent_id=parent_id
    )


# Árbol de categorías
@router.get(
    "/tree",
    response_model=List[CategoriaTree]
)
def get_tree(
    db: Session = Depends(get_session)
):

    service = CategoriaService(db)

    return service.get_tree()


# Obtener categoría
@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead
)
def obtener(
    categoria_id: int,
    db: Session = Depends(get_session)
):

    service = CategoriaService(db)

    return service.obtener_categoria(
        categoria_id
    )


# Actualizar categoría
@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead
)
def actualizar(
    categoria_id: int,
    datos: CategoriaUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    service = CategoriaService(db)

    with UnitOfWork(db):

        categoria = service.actualizar_categoria(
            categoria_id,
            datos
        )

    db.refresh(
        categoria
    )

    return categoria


# Eliminar categoría
@router.delete(
    "/{categoria_id}",
    status_code=204
)
def eliminar(
    categoria_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    service = CategoriaService(db)

    with UnitOfWork(db):

        service.eliminar_categoria(
            categoria_id
        )


# Subir imagen
@router.post(
    "/{categoria_id}/imagen",
    response_model=CategoriaRead
)
def subir_imagen(
    categoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    service = CategoriaService(db)

    with UnitOfWork(db):

        categoria = service.subir_imagen(
            categoria_id,
            archivo
        )

    db.refresh(
        categoria
    )

    return categoria
