import logging

from app.repositories.stats_repository import (
    StatsRepository
)

from app.schemas.stats_schema import (
    ResumenStats,
    VentaDiaria,
    VentasSemanalesResponse,
    ProductoMasVendido,
    ProductosMasVendidosResponse,
    PedidosPorEstadoItem,
    PedidosPorEstadoResponse,
    IngresoPorFormaPagoItem,
    IngresosPorFormaPagoResponse,
)

logger = logging.getLogger(__name__)


class StatsService:

    def __init__(self, db):

        self.repo = StatsRepository(db)

    def get_resumen(self) -> ResumenStats:

        resumen = self.repo.get_resumen_data()

        return ResumenStats(
            ventas_totales=resumen["ventas_totales"],
            pedidos_hoy=int(
                resumen["pedidos_hoy"]
            ),
            clientes_nuevos=int(
                resumen["clientes_nuevos"]
            ),
            pedidos_pendientes=int(
                resumen["pedidos_pendientes"]
            ),
        )

    def get_ventas_semanales(
        self
    ) -> VentasSemanalesResponse:

        data = [
            VentaDiaria(
                fecha=row["fecha"],
                total=row["total"],
                cantidad=int(row["cantidad"]),
            )
            for row in self.repo.get_ventas_semanales()
        ]

        return VentasSemanalesResponse(
            data=data
        )

    def get_productos_mas_vendidos(
        self,
        limit: int = 10
    ) -> ProductosMasVendidosResponse:

        data = [
            ProductoMasVendido(
                producto_id=row.producto_id,
                nombre=row.nombre_snapshot,
                total_vendido=int(
                    row.total_vendido
                ),
                ingreso_total=row.ingreso_total,
            )
            for row in self.repo.get_productos_mas_vendidos(
                limit
            )
        ]

        return ProductosMasVendidosResponse(
            data=data
        )

    def get_pedidos_por_estado(self) -> PedidosPorEstadoResponse:

        rows = self.repo.get_pedidos_por_estado()

        data = [
            PedidosPorEstadoItem(
                estado_codigo=row.estado_codigo,
                cantidad=int(row.cantidad),
            )
            for row in rows
        ]

        return PedidosPorEstadoResponse(data=data)

    def get_ingresos_por_forma_pago(self) -> IngresosPorFormaPagoResponse:

        rows = self.repo.get_ingresos_por_forma_pago()

        data = [
            IngresoPorFormaPagoItem(
                forma_pago_codigo=row.forma_pago_codigo,
                total=float(row.total),
                cantidad=int(row.cantidad),
            )
            for row in rows
        ]

        return IngresosPorFormaPagoResponse(data=data)
