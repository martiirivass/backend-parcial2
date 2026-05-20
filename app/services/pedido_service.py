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

# Maquina de estados del pedido
# {estado_actual: [estados_posibles]}
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

    def _crear_historial(self, pedido_id, estado_id, observacion=None):
        historial = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_pedido_id=estado_id,
            observacion=observacion
        )
        self.db.add(historial)
        return historial

    def crear_pedido(self, usuario_id, datos):
        try:
            # Busco el estado PENDIENTE
            estado_pendiente = self._get_estado_by_codigo("PENDIENTE")

            # Creo el pedido
            pedido = Pedido(
                usuario_id=usuario_id,
                estado_actual_id=estado_pendiente.id,
                forma_pago_id=datos.forma_pago_id,
                direccion_entrega_id=datos.direccion_entrega_id,
                total=0.0
            )
            self.repo.create(pedido)
            self.db.flush()  # Para obtener el ID del pedido

            total = 0.0

            # Por cada item, creo un DetallePedido con SNAPSHOT PATTERN
            for item in datos.items:
                producto = self.db.get(Producto, item.producto_id)
                if not producto or not producto.activo:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto ID {item.producto_id} no encontrado"
                    )

                subtotal = producto.precio * item.cantidad
                total += subtotal

                detalle = DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=producto.id,
                    nombre_producto=producto.nombre,  # Snapshot: guardo el nombre actual
                    precio_unitario=producto.precio,  # Snapshot: guardo el precio actual
                    cantidad=item.cantidad,
                    subtotal=subtotal
                )
                self.db.add(detalle)

            # Actualizo el total del pedido
            pedido.total = total

            # Creo el AUDIT TRAIL (primer estado: PENDIENTE)
            self._crear_historial(
                pedido.id,
                estado_pendiente.id,
                "Pedido creado"
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

    def avanzar_estado(self, pedido_id, nuevo_estado_id):
        try:
            pedido = self.repo.get_by_id(pedido_id)
            if not pedido:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")

            # Busco el estado actual y el nuevo estado
            estado_actual = self.db.get(EstadoPedido, pedido.estado_actual_id)
            nuevo_estado = self.db.get(EstadoPedido, nuevo_estado_id)

            if not estado_actual or not nuevo_estado:
                raise HTTPException(status_code=400, detail="Estado invalido")

            # Valido la transicion (la logica esta en el service, no en el router)
            transiciones_validas = TRANSICIONES.get(estado_actual.codigo, [])

            if nuevo_estado.codigo not in transiciones_validas:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede pasar de {estado_actual.codigo} a {nuevo_estado.codigo}"
                )

            # Actualizo el estado
            pedido.estado_actual_id = nuevo_estado.id

            # Creo el AUDIT TRAIL (append-only)
            self._crear_historial(
                pedido.id,
                nuevo_estado.id,
                f"Cambio de {estado_actual.codigo} a {nuevo_estado.codigo}"
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

            estado_actual = self.db.get(EstadoPedido, pedido.estado_actual_id)

            # Solo se puede cancelar desde PENDIENTE o CONFIRMADO
            if estado_actual.codigo not in ["PENDIENTE", "CONFIRMADO"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede cancelar un pedido en estado {estado_actual.codigo}"
                )

            estado_cancelado = self._get_estado_by_codigo("CANCELADO")
            pedido.estado_actual_id = estado_cancelado.id

            self._crear_historial(
                pedido.id,
                estado_cancelado.id,
                "Cancelado por el cliente"
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

    def listar_pedidos(self, usuario_id, rol_codigo, limit, offset, estado_id=None):
        # Si es CLIENT, ve solo sus pedidos
        if rol_codigo == "CLIENT":
            pedidos = self.repo.get_by_usuario(usuario_id)
        else:
            # ADMIN o PEDIDOS ven todos
            pedidos = self.repo.get_all()

        # Filtro opcional por estado
        if estado_id is not None:
            pedidos = [p for p in pedidos if p.estado_actual_id == estado_id]

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
            .order_by(HistorialEstadoPedido.fecha)
        ).all()

        return historial
