import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import math

from app.core.errors import http_error

from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.historial_estado_model import HistorialEstadoPedido
from app.models.pago_model import Pago

from app.repositories.pedido_repository import PedidoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.estado_pedido_repository import EstadoPedidoRepository
from app.repositories.historial_repository import HistorialRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.direccion_repository import DireccionEntregaRepository

if TYPE_CHECKING:
    from app.core.ws_manager import WSManager

logger = logging.getLogger(__name__)

TRANSICIONES = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["ENTREGADO", "CANCELADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}


class PedidoService:

    def __init__(self, db, ws_manager: "WSManager | None" = None):

        self.db = db
        self.ws_manager = ws_manager
        self._pending_events: list[dict] = []

        self.repo = PedidoRepository(db)

        self.producto_repo = ProductoRepository(db)

        self.estado_repo = EstadoPedidoRepository(db)

        self.historial_repo = HistorialRepository(db)

        self.pago_repo = PagoRepository(db)
        self.direccion_repo = DireccionEntregaRepository(db)

    # ── WebSocket event helpers ────────────────────────────────────────

    def _add_event(
        self,
        pedido_id: int,
        estado_anterior: str | None,
        estado_nuevo: str | None,
        usuario_id: int,
        motivo: str | None = None,
    ) -> None:
        self._pending_events.append({
            "pedido_id": pedido_id,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "usuario_id": usuario_id,
            "motivo": motivo,
        })

    def flush_events(self) -> None:
        if not self.ws_manager:
            self._pending_events.clear()
            return

        events = self._pending_events.copy()
        self._pending_events.clear()

        for ev in events:
            event_payload = {
                "event": "pedido_estado_changed",
                "pedido_id": ev["pedido_id"],
                "estado_anterior": ev["estado_anterior"],
                "estado_nuevo": ev["estado_nuevo"],
                "usuario_id": ev["usuario_id"],
                "motivo": ev.get("motivo"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.ws_manager.broadcast_to_pedido_sync(
                ev["pedido_id"],
                event_payload,
            )

    def _get_estado_by_codigo(self, codigo):

        estado = self.estado_repo.get_by_codigo(codigo)
        if not estado:

            raise http_error(
                500, f"Estado {codigo} no encontrado", "STATE_NOT_FOUND"
            )

        return estado

    def _crear_historial(
        self,
        pedido_id,
        estado_desde,
        estado_hacia,
        usuario_id,
        motivo=None
    ):

        historial = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_desde=estado_desde,
            estado_hacia=estado_hacia,
            usuario_id=usuario_id,
            motivo=motivo,
        )

        self.historial_repo.create(historial)

        return historial

    def crear_pedido(self, usuario_id, datos):

        subtotal = Decimal('0')

        detalles = []

        # Calcular subtotal y validar productos
        for item in datos.items:

            producto = self.producto_repo.get_by_id(
                item.producto_id
            )

            if not producto or producto.deleted_at is not None:

                raise http_error(
                    404, f"Producto ID {item.producto_id} no encontrado", "PRODUCT_NOT_FOUND"
                )

            if producto.stock_cantidad < item.cantidad:
                raise http_error(
                    400, f"Stock insuficiente para {producto.nombre}", "INSUFFICIENT_STOCK"
                )

            item_subtotal = (
                producto.precio_base * item.cantidad
            )

            subtotal += item_subtotal

            detalle = DetallePedido(
                producto_id=producto.id,
                cantidad=item.cantidad,
                nombre_snapshot=producto.nombre,
                precio_snapshot=producto.precio_base,
                subtotal_snap=item_subtotal
            )

            detalles.append(detalle)

        # Validar dirección si se especificó
        if datos.direccion_id is not None:
            direccion = self.direccion_repo.get_by_id(datos.direccion_id)
            if not direccion:
                raise http_error(
                    404, "Dirección de entrega no encontrada", "ADDRESS_NOT_FOUND"
                )

        costo_envio = Decimal('50')

        total = subtotal + costo_envio

        # Crear pedido
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

        # Necesario para obtener ID
        self.db.flush()

        # Guardar detalles
        for detalle in detalles:

            detalle.pedido_id = pedido.id

            self.db.add(detalle)

        # Historial inicial
        self._crear_historial(
            pedido.id,
            None,
            "PENDIENTE",
            usuario_id
        )

        # Crear pago si existe referencia
        if datos.referencia_pago:

            pago = Pago(
                pedido_id=pedido.id,
                transaction_amount=total,
                external_reference=datos.referencia_pago,
                idempotency_key=str(pedido.id),
            )

            self.pago_repo.create(pago)

        # Acumular evento WebSocket
        self._add_event(
            pedido.id,
            None,
            "PENDIENTE",
            usuario_id,
        )

        return pedido

    def avanzar_estado(
        self,
        pedido_id,
        nuevo_estado_codigo,
        usuario_id,
        motivo=None
    ):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise http_error(
                404, "Pedido no encontrado", "ORDER_NOT_FOUND"
            )

        estado_actual = self._get_estado_by_codigo(
            pedido.estado_codigo
        )

        nuevo_estado = self._get_estado_by_codigo(
            nuevo_estado_codigo
        )

        transiciones_validas = TRANSICIONES.get(
            estado_actual.codigo,
            []
        )

        if nuevo_estado.codigo not in transiciones_validas:

            raise http_error(
                400, f"No se puede pasar de {estado_actual.codigo} a {nuevo_estado.codigo}", "INVALID_STATE_TRANSITION"
            )

        # Validate motivo for cancellation
        if nuevo_estado.codigo == "CANCELADO" and (not motivo or not motivo.strip()):
            raise http_error(
                422, "El motivo es obligatorio para cancelar un pedido", "MOTIVO_REQUIRED"
            )

        pedido.estado_codigo = nuevo_estado.codigo

        self.repo.update(pedido)

        self._crear_historial(
            pedido.id,
            estado_actual.codigo,
            nuevo_estado.codigo,
            usuario_id,
            motivo=motivo
        )

        # Acumular evento WebSocket (broadcast post-UoW en el router)
        self._add_event(
            pedido.id,
            estado_actual.codigo,
            nuevo_estado.codigo,
            usuario_id,
            motivo=motivo,
        )

        return pedido

    def cancelar_pedido(
        self,
        pedido_id,
        usuario_id,
        motivo=None
    ):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise http_error(
                404, "Pedido no encontrado", "ORDER_NOT_FOUND"
            )

        if pedido.usuario_id != usuario_id:

            raise http_error(
                403, "No puedes cancelar un pedido que no te pertenece", "FORBIDDEN_CANCEL"
            )

        estado_actual = self._get_estado_by_codigo(
            pedido.estado_codigo
        )

        if estado_actual.codigo not in [
            "PENDIENTE",
            "CONFIRMADO"
        ]:

            raise http_error(
                400, f"No se puede cancelar un pedido en estado {estado_actual.codigo}", "INVALID_CANCEL_STATE"
            )

        # Validate motivo for cancellation
        if not motivo or not motivo.strip():
            raise http_error(
                422, "El motivo es obligatorio para cancelar un pedido", "MOTIVO_REQUIRED"
            )

        pedido.estado_codigo = "CANCELADO"

        self.repo.update(pedido)

        self._crear_historial(
            pedido.id,
            estado_actual.codigo,
            "CANCELADO",
            usuario_id,
            motivo=motivo
        )

        # Acumular evento WebSocket (broadcast post-UoW en el router)
        self._add_event(
            pedido.id,
            estado_actual.codigo,
            "CANCELADO",
            usuario_id,
            motivo=motivo,
        )

        return pedido

    def listar_pedidos(
        self,
        usuario_id,
        es_cliente,
        page: int = 1,
        size: int = 20,
        estado_codigo=None
    ):

        skip = (page - 1) * size

        if es_cliente:

            pedidos = self.repo.get_paginated(
                size, skip,
                usuario_id=usuario_id,
                estado_codigo=estado_codigo
            )

            total = self.repo.count(
                usuario_id=usuario_id,
                estado_codigo=estado_codigo
            )

        else:

            pedidos = self.repo.get_paginated(
                size, skip,
                estado_codigo=estado_codigo
            )

            total = self.repo.count(
                estado_codigo=estado_codigo
            )

        pages = math.ceil(total / size) if size > 0 else 0

        return {
            "items": pedidos,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

    def obtener_pedido(self, pedido_id, usuario_id=None, es_cliente=False):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise http_error(
                404, "Pedido no encontrado", "ORDER_NOT_FOUND"
            )

        if es_cliente and pedido.usuario_id != usuario_id:

            raise http_error(
                403, "No tienes permiso para ver este pedido", "FORBIDDEN_ACCESS"
            )

        return pedido

    def obtener_historial(self, pedido_id):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise http_error(
                404, "Pedido no encontrado", "ORDER_NOT_FOUND"
            )

        historial = self.historial_repo.get_by_pedido_id(
            pedido_id
        )

        return historial
