import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from fastapi import HTTPException

from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.historial_estado_model import HistorialEstadoPedido
from app.models.pago_model import Pago

from app.repositories.pedido_repository import PedidoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.estado_pedido_repository import EstadoPedidoRepository
from app.repositories.historial_repository import HistorialRepository
from app.repositories.pago_repository import PagoRepository

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

    # ── WebSocket event helpers ────────────────────────────────────────
    # El broadcast DEBE ejecutarse después del commit del UoW.
    # Estas solo acumulan eventos; flush_events() los envía.

    def _add_event(
        self,
        pedido_id: int,
        estado_anterior: str | None,
        estado_nuevo: str | None,
        usuario_id: int,
    ) -> None:
        """Acumula un evento para broadcast posterior (post-UoW)."""
        self._pending_events.append({
            "pedido_id": pedido_id,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "usuario_id": usuario_id,
        })

    def flush_events(self) -> None:
        """
        Envía TODOS los eventos acumulados vía WebSocket.
        Debe llamarse SIEMPRE después del commit del UnitOfWork,
        NUNCA dentro del bloque with UnitOfWork().

        Usa broadcast_to_pedido_sync que es thread-safe:
        funciona desde handlers sync (thread pool) y async (event loop).
        """
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.ws_manager.broadcast_to_pedido_sync(
                ev["pedido_id"],
                event_payload,
            )

    def _get_estado_by_codigo(self, codigo):

        estado = self.estado_repo.get_by_codigo(codigo)

        if not estado:
            raise HTTPException(
                status_code=500,
                detail=f"Estado {codigo} no encontrado"
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

        subtotal = 0.0

        detalles = []

        # Calcular subtotal y validar productos
        for item in datos.items:

            producto = self.producto_repo.get_by_id(
                item.producto_id
            )

            if not producto or producto.deleted_at is not None:

                raise HTTPException(
                    status_code=404,
                    detail=f"Producto ID {item.producto_id} no encontrado"
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

        costo_envio = 50.0

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
                monto=total,
                forma_pago_codigo=datos.forma_pago_codigo,
                referencia=datos.referencia_pago
            )

            self.pago_repo.create(pago)

        # Acumular evento WebSocket (broadcast post-UoW en el router)
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
        usuario_id
    ):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
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

            raise HTTPException(
                status_code=400,
                detail=f"No se puede pasar de {estado_actual.codigo} a {nuevo_estado.codigo}"
            )

        pedido.estado_codigo = nuevo_estado.codigo

        self.repo.update(pedido)

        self._crear_historial(
            pedido.id,
            estado_actual.codigo,
            nuevo_estado.codigo,
            usuario_id
        )

        # Acumular evento WebSocket (broadcast post-UoW en el router)
        self._add_event(
            pedido.id,
            estado_actual.codigo,
            nuevo_estado.codigo,
            usuario_id,
        )

        return pedido

    def cancelar_pedido(
        self,
        pedido_id,
        usuario_id
    ):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        if pedido.usuario_id != usuario_id:

            raise HTTPException(
                status_code=403,
                detail="No puedes cancelar un pedido que no te pertenece"
            )

        estado_actual = self._get_estado_by_codigo(
            pedido.estado_codigo
        )

        if estado_actual.codigo not in [
            "PENDIENTE",
            "CONFIRMADO"
        ]:

            raise HTTPException(
                status_code=400,
                detail=f"No se puede cancelar un pedido en estado {estado_actual.codigo}"
            )

        pedido.estado_codigo = "CANCELADO"

        self.repo.update(pedido)

        self._crear_historial(
            pedido.id,
            estado_actual.codigo,
            "CANCELADO",
            usuario_id
        )

        # Acumular evento WebSocket (broadcast post-UoW en el router)
        self._add_event(
            pedido.id,
            estado_actual.codigo,
            "CANCELADO",
            usuario_id,
        )

        return pedido

    def listar_pedidos(
        self,
        usuario_id,
        es_cliente,
        limit,
        offset,
        estado_codigo=None
    ):

        if es_cliente:

            pedidos = self.repo.get_by_usuario(
                usuario_id
            )

        else:

            pedidos = self.repo.get_all()

        if estado_codigo is not None:

            pedidos = [
                p for p in pedidos
                if p.estado_codigo == estado_codigo
            ]

        return {
            "data": pedidos[offset: offset + limit],
            "total": len(pedidos)
        }

    def obtener_pedido(self, pedido_id):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        return pedido

    def obtener_historial(self, pedido_id):

        pedido = self.repo.get_by_id(pedido_id)

        if not pedido:

            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        historial = self.historial_repo.get_by_pedido_id(
            pedido_id
        )

        return historial