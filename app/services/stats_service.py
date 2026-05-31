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
)

logger = logging.getLogger(__name__)


class StatsService:

    def __init__(self, db):

        self.repo = StatsRepository(db)

    def get_resumen(self) -> ResumenStats:

        resumen = self.repo.get_resumen_data()

        return ResumenStats(
            ventas_totales=float(
                resumen["ventas_totales"]
            ),
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
                total=float(row["total"]),
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
                ingreso_total=float(
                    row.ingreso_total
                ),
            )
            for row in self.repo.get_productos_mas_vendidos(
                limit
            )
        ]

        return ProductosMasVendidosResponse(
            data=data
        )