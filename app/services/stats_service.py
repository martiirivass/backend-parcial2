import logging
<<<<<<< HEAD
from datetime import date, datetime, timedelta, timezone

from sqlmodel import Session, select, func, text

from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.estado_pedido_model import EstadoPedido
from app.models.usuario import Usuario
=======

from app.repositories.stats_repository import (
    StatsRepository
)

>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
from app.schemas.stats_schema import (
    ResumenStats,
    VentaDiaria,
    VentasSemanalesResponse,
    ProductoMasVendido,
    ProductosMasVendidosResponse,
)

logger = logging.getLogger(__name__)


class StatsService:

<<<<<<< HEAD
    def __init__(self, db: Session):
        self.db = db

    def get_resumen(self) -> ResumenStats:
        """Calcula las métricas de resumen del dashboard."""
        estado_entregado_codigo = "ENTREGADO"
        estado_pendiente_codigo = "PENDIENTE"
        hoy = date.today()
        hace_30_dias = hoy - timedelta(days=30)

        # Ventas totales (suma de totales de pedidos ENTREGADOS)
        ventas_totales = self.db.exec(
            select(func.coalesce(func.sum(Pedido.total), 0.0)).where(
                Pedido.estado_codigo == estado_entregado_codigo,
                Pedido.deleted_at == None,
            )
        ).one()

        # Pedidos de hoy
        inicio_hoy = datetime(hoy.year, hoy.month, hoy.day, tzinfo=timezone.utc)
        fin_hoy = inicio_hoy + timedelta(days=1)
        pedidos_hoy = self.db.exec(
            select(func.count(Pedido.id)).where(
                Pedido.created_at >= inicio_hoy,
                Pedido.created_at < fin_hoy,
                Pedido.deleted_at == None,
            )
        ).one()

        # Clientes nuevos (últimos 30 días)
        clientes_nuevos = self.db.exec(
            select(func.count(Usuario.id)).where(
                Usuario.deleted_at == None,
                Usuario.created_at >= hace_30_dias,
            )
        ).one()

        # Pedidos pendientes
        pedidos_pendientes = self.db.exec(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo == estado_pendiente_codigo,
                Pedido.deleted_at == None,
            )
        ).one()

        return ResumenStats(
            ventas_totales=float(ventas_totales),
            pedidos_hoy=int(pedidos_hoy),
            clientes_nuevos=int(clientes_nuevos),
            pedidos_pendientes=int(pedidos_pendientes),
        )

    def get_ventas_semanales(self) -> VentasSemanalesResponse:
        """Ventas agregadas por día de los últimos 7 días."""
        estado_entregado_codigo = "ENTREGADO"
        hoy = date.today()
        hace_7_dias = hoy - timedelta(days=6)

        inicio_semana = datetime(
            hace_7_dias.year, hace_7_dias.month, hace_7_dias.day,
            tzinfo=timezone.utc
        )

        # Ventas por día desde la DB
        ventas_db = self.db.exec(
            select(
                func.date(Pedido.created_at).label("fecha"),
                func.coalesce(func.sum(Pedido.total), 0.0).label("total"),
                func.count(Pedido.id).label("cantidad"),
            ).where(
                Pedido.estado_codigo == estado_entregado_codigo,
                Pedido.created_at >= inicio_semana,
                Pedido.deleted_at == None,
            ).group_by(
                func.date(Pedido.created_at)
            ).order_by(
                func.date(Pedido.created_at)
            )
        ).all()

        # Convertir a dict para lookup rápido
        ventas_dict = {row.fecha: row for row in ventas_db}

        # Construir array con todos los días (incluir días sin ventas con 0)
        data = []
        for i in range(7):
            dia = hace_7_dias + timedelta(days=i)
            if dia in ventas_dict:
                row = ventas_dict[dia]
                data.append(VentaDiaria(
                    fecha=dia,
                    total=float(row.total),
                    cantidad=int(row.cantidad),
                ))
            else:
                data.append(VentaDiaria(fecha=dia, total=0.0, cantidad=0))

        return VentasSemanalesResponse(data=data)

    def get_productos_mas_vendidos(self, limit: int = 10) -> ProductosMasVendidosResponse:
        """Top productos más vendidos con cantidad e ingreso total."""
        estado_entregado_codigo = "ENTREGADO"

        # Subquery: IDs de pedidos ENTREGADOS
        pedidos_entregados = select(Pedido.id).where(
            Pedido.estado_codigo == estado_entregado_codigo,
            Pedido.deleted_at == None,
        ).subquery()

        # Agrupar detalles de pedido por producto
        resultados = self.db.exec(
            select(
                DetallePedido.producto_id,
                DetallePedido.nombre_snapshot,
                func.coalesce(func.sum(DetallePedido.cantidad), 0).label("total_vendido"),
                func.coalesce(func.sum(DetallePedido.subtotal_snap), 0.0).label("ingreso_total"),
            ).where(
                DetallePedido.pedido_id.in_(select(pedidos_entregados.c.id)),
            ).group_by(
                DetallePedido.producto_id,
                DetallePedido.nombre_snapshot,
            ).order_by(
                text("total_vendido DESC")
            ).limit(limit)
        ).all()
=======
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
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

        data = [
            ProductoMasVendido(
                producto_id=row.producto_id,
                nombre=row.nombre_snapshot,
<<<<<<< HEAD
                total_vendido=int(row.total_vendido),
                ingreso_total=float(row.ingreso_total),
            )
            for row in resultados
        ]

        return ProductosMasVendidosResponse(data=data)
=======
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
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
