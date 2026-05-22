import logging
from fastapi import HTTPException
from sqlmodel import select

from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.historial_estado_model import HistorialEstadoPedido
from app.models.estado_pedido_model import EstadoPedido
from app.models.producto_model import Producto
from app.repositories.pedido_repository import PedidoRepository
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

# Máquina de estados del pedido
# {estado_actual_codigo: [estados_posibles_codigo]}
TRANSICIONES = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["EN_CAMINO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}


class PedidoService:

    def __init__(self, db):
        self.db = db
        self.repo = PedidoRepository(db)
        self.uow = UnitOfWork(db)

    def _get_estado_by_codigo(self, codigo):
        estado = self.db.exec(
            select(EstadoPedido).where(EstadoPedido.codigo == codigo)
        ).first()
        if not estado:
            raise HTTPException(status_code=500, detail=f"Estado {codigo} no encontrado")
        return estado

    def _crear_historial(self, pedido_id, estado_anterior, estado_nuevo, usuario_id):
        historial = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario_id=usuario_id,
        )
        self.db.add(historial)
        return historial

    def crear_pedido(self, usuario_id, datos):
        try:
            # Calculo subtotal desde los items
            subtotal = 0.0
            detalles = []

            for item in datos.items:
                producto = self.db.get(Producto, item.producto_id)
                if not producto or producto.deleted_at is not None:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto ID {item.producto_id} no encontrado"
                    )

                item_subtotal = producto.precio_base * item.cantidad
                subtotal += item_subtotal

                detalle = DetallePedido(
                    producto_id=producto.id,
                    cantidad=item.cantidad,
                    nombre_snapshot=producto.nombre,
                    precio_snapshot=producto.precio_base,
                    subtotal_snap=item_subtotal
                )
                detalles.append(detalle)

            costo_envio = 50.0
            total = subtotal + costo_envio

            # Creo el pedido
            pedido = Pedido(
                usuario_id=usuario_id,
                forma_pago_codigo=datos.forma_pago_codigo,
                direccion_id=datos.direccion_id,
                estado_codigo="PENDIENTE",
                subtotal=subtotal,
                costo_envio=costo_envio,
                total=total
            )
            self.repo.create(pedido)
            self.db.flush()

            # Asigno los detalles al pedido
            for d in detalles:
                d.pedido_id = pedido.id
                self.db.add(d)

            # Audit trail: estado inicial
            self._crear_historial(
                pedido.id,
                None,
                "PENDIENTE",
                usuario_id
            )

            self.uow.commit()
            self.db.refresh(pedido)

            return pedido

        except HTTPException:
            self.uow.rollback()
            raise
        except Exception as e:
            logger.exception(f"Error creating pedido: {e}")
            self.uow.rollback()
            raise

    def avanzar_estado(self, pedido_id, nuevo_estado_codigo, usuario_id):
        try:
            pedido = self.repo.get_by_id(pedido_id)
            if not pedido:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")

            estado_actual = self._get_estado_by_codigo(pedido.estado_codigo)
            nuevo_estado = self._get_estado_by_codigo(nuevo_estado_codigo)

            # Valido la transicion
            transiciones_validas = TRANSICIONES.get(estado_actual.codigo, [])

            if nuevo_estado.codigo not in transiciones_validas:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede pasar de {estado_actual.codigo} a {nuevo_estado.codigo}"
                )

            # Actualizo el estado
            pedido.estado_codigo = nuevo_estado.codigo

            # Audit trail append-only
            self._crear_historial(
                pedido.id,
                estado_actual.codigo,
                nuevo_estado.codigo,
                usuario_id
            )

            self.uow.commit()
            self.db.refresh(pedido)

            return pedido

        except HTTPException:
            self.uow.rollback()
            raise
        except Exception as e:
            logger.exception(f"Error avanzando estado: {e}")
            self.uow.rollback()
            raise

    def cancelar_pedido(self, pedido_id, usuario_id):
        try:
            pedido = self.repo.get_by_id(pedido_id)
            if not pedido:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")

            # El cliente solo puede cancelar sus propios pedidos
            if pedido.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=403,
                    detail="No puedes cancelar un pedido que no te pertenece"
                )

            estado_actual = self._get_estado_by_codigo(pedido.estado_codigo)

            # Solo se puede cancelar desde PENDIENTE o CONFIRMADO
            if estado_actual.codigo not in ["PENDIENTE", "CONFIRMADO"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede cancelar un pedido en estado {estado_actual.codigo}"
                )

            pedido.estado_codigo = "CANCELADO"

            self._crear_historial(
                pedido.id,
                estado_actual.codigo,
                "CANCELADO",
                usuario_id
            )

            self.uow.commit()
            self.db.refresh(pedido)

            return pedido

        except HTTPException:
            self.uow.rollback()
            raise
        except Exception as e:
            logger.exception(f"Error cancelando pedido: {e}")
            self.uow.rollback()
            raise

    def listar_pedidos(self, usuario_id, es_cliente, limit, offset, estado_codigo=None):
        # Si es CLIENT, ve solo sus pedidos
        if es_cliente:
            pedidos = self.repo.get_by_usuario(usuario_id)
        else:
            # ADMIN o PEDIDOS ven todos
            pedidos = self.repo.get_all()

        # Filtro opcional por estado
        if estado_codigo is not None:
            pedidos = [p for p in pedidos if p.estado_codigo == estado_codigo]

        return {
            "data": pedidos[offset: offset + limit],
            "total": len(pedidos)
        }

    def obtener_pedido(self, pedido_id):
        pedido = self.repo.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return pedido

    def obtener_historial(self, pedido_id):
        # Verifico que el pedido exista
        pedido = self.repo.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        # Audit trail ordenado por fecha
        historial = self.db.exec(
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at)
        ).all()

        return historial
