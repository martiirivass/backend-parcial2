from datetime import (
    date,
    datetime,
    timedelta,
    timezone
)

from sqlmodel import (
    Session,
    select,
    func,
    text
)

from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import (
    DetallePedido
)
from app.models.usuario import Usuario


class StatsRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_resumen_data(self):

        estado_entregado = "ENTREGADO"
        estado_pendiente = "PENDIENTE"

        hoy = date.today()

        hace_30_dias = hoy - timedelta(days=30)

        # Ventas totales
        ventas_totales = self.db.exec(
            select(
                func.coalesce(
                    func.sum(Pedido.total),
                    0.0
                )
            ).where(
                Pedido.estado_codigo
                == estado_entregado,
                Pedido.deleted_at.is_(None),
            )
        ).one()

        # Pedidos hoy
        inicio_hoy = datetime(
            hoy.year,
            hoy.month,
            hoy.day,
            tzinfo=timezone.utc
        )

        fin_hoy = inicio_hoy + timedelta(days=1)

        pedidos_hoy = self.db.exec(
            select(
                func.count(Pedido.id)
            ).where(
                Pedido.created_at >= inicio_hoy,
                Pedido.created_at < fin_hoy,
                Pedido.deleted_at.is_(None),
            )
        ).one()

        # Clientes nuevos
        clientes_nuevos = self.db.exec(
            select(
                func.count(Usuario.id)
            ).where(
                Usuario.deleted_at.is_(None),
                Usuario.created_at >= hace_30_dias,
            )
        ).one()

        # Pedidos pendientes
        pedidos_pendientes = self.db.exec(
            select(
                func.count(Pedido.id)
            ).where(
                Pedido.estado_codigo
                == estado_pendiente,
                Pedido.deleted_at.is_(None),
            )
        ).one()

        return {
            "ventas_totales": ventas_totales,
            "pedidos_hoy": pedidos_hoy,
            "clientes_nuevos": clientes_nuevos,
            "pedidos_pendientes": pedidos_pendientes,
        }

    def get_ventas_semanales(self):

        estado_entregado = "ENTREGADO"

        hoy = date.today()

        hace_7_dias = hoy - timedelta(days=6)

        inicio_semana = datetime(
            hace_7_dias.year,
            hace_7_dias.month,
            hace_7_dias.day,
            tzinfo=timezone.utc
        )

        ventas_db = self.db.exec(
            select(
                func.date(
                    Pedido.created_at
                ).label("fecha"),

                func.coalesce(
                    func.sum(Pedido.total),
                    0.0
                ).label("total"),

                func.count(
                    Pedido.id
                ).label("cantidad"),

            ).where(
                Pedido.estado_codigo
                == estado_entregado,

                Pedido.created_at
                >= inicio_semana,

                Pedido.deleted_at.is_(None),

            ).group_by(
                func.date(Pedido.created_at)

            ).order_by(
                func.date(Pedido.created_at)
            )
        ).all()

        ventas_dict = {
            row.fecha: row
            for row in ventas_db
        }

        data = []

        for i in range(7):

            dia = hace_7_dias + timedelta(days=i)

            if dia in ventas_dict:

                row = ventas_dict[dia]

                data.append({
                    "fecha": dia,
                    "total": row.total,
                    "cantidad": row.cantidad,
                })

            else:

                data.append({
                    "fecha": dia,
                    "total": 0.0,
                    "cantidad": 0,
                })

        return data

    def get_productos_mas_vendidos(
        self,
        limit: int = 10
    ):

        estado_entregado = "ENTREGADO"

        pedidos_entregados = (
            select(Pedido.id)
            .where(
                Pedido.estado_codigo
                == estado_entregado,

                Pedido.deleted_at.is_(None),
            )
            .subquery()
        )

        statement = (
            select(
                DetallePedido.producto_id,

                DetallePedido.nombre_snapshot,

                func.coalesce(
                    func.sum(
                        DetallePedido.cantidad
                    ),
                    0
                ).label("total_vendido"),

                func.coalesce(
                    func.sum(
                        DetallePedido.subtotal_snap
                    ),
                    0.0
                ).label("ingreso_total"),

            ).where(
                DetallePedido.pedido_id.in_(
                    select(
                        pedidos_entregados.c.id
                    )
                ),

            ).group_by(
                DetallePedido.producto_id,
                DetallePedido.nombre_snapshot,

            ).order_by(
                text("total_vendido DESC")

            ).limit(limit)
        )

        return self.db.exec(statement).all()

    def get_pedidos_por_estado(self):
        """Cantidad de pedidos agrupados por estado (GROUP BY)."""

        return self.db.exec(
            select(
                Pedido.estado_codigo,
                func.count(Pedido.id).label("cantidad"),
            ).where(
                Pedido.deleted_at.is_(None),
            ).group_by(
                Pedido.estado_codigo,
            ).order_by(
                Pedido.estado_codigo,
            )
        ).all()

    def get_ingresos_por_forma_pago(self):
        """Ingresos agrupados por forma de pago (solo pagos approved)."""

        from app.models.pago_model import Pago

        # Subquery: pedidos con al menos un pago mp_status='approved'
        pedidos_aprobados = (
            select(Pago.pedido_id)
            .where(Pago.mp_status == "approved")
            .subquery()
        )

        return self.db.exec(
            select(
                Pedido.forma_pago_codigo,
                func.coalesce(
                    func.sum(Pedido.total), 0.0
                ).label("total"),
                func.count(Pedido.id).label("cantidad"),
            ).where(
                Pedido.id.in_(select(pedidos_aprobados.c.pedido_id)),
                Pedido.deleted_at.is_(None),
            ).group_by(
                Pedido.forma_pago_codigo,
            ).order_by(
                text("total DESC"),
            )
        ).all()