from datetime import (
    date,
    datetime,
    timedelta,
    timezone
)
from decimal import Decimal

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
from app.models.pago_model import Pago
from app.models.usuario import Usuario


class StatsRepository:

    def __init__(self, db: Session):
        self.db = db

    def _pedidos_pagados_subquery(self):
        """Subquery de pedidos con estado ENTREGADO y pago approved."""
        return (
            select(Pedido.id)
            .where(
                Pedido.estado_codigo == "ENTREGADO",
                Pedido.deleted_at.is_(None),
                Pedido.id.in_(
                    select(Pago.pedido_id).where(Pago.mp_status == "approved")
                ),
            )
            .subquery()
        )

    def get_resumen_data(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):
        hoy = date.today()
        if fecha_desde is None:
            fecha_desde = hoy - timedelta(days=30)
        if fecha_hasta is None:
            fecha_hasta = hoy

        inicio_periodo = datetime(fecha_desde.year, fecha_desde.month, fecha_desde.day, tzinfo=timezone.utc)
        fin_periodo = datetime(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day, tzinfo=timezone.utc) + timedelta(days=1)

        pedidos_pagados = self._pedidos_pagados_subquery()

        ventas_totales = self.db.exec(
            select(
                func.coalesce(func.sum(Pedido.total), 0)
            ).where(
                Pedido.id.in_(select(pedidos_pagados.c.id)),
                Pedido.created_at.between(inicio_periodo, fin_periodo),
            )
        ).one()

        inicio_hoy = datetime(hoy.year, hoy.month, hoy.day, tzinfo=timezone.utc)
        fin_hoy = inicio_hoy + timedelta(days=1)

        pedidos_hoy = self.db.exec(
            select(func.count(Pedido.id)).where(
                Pedido.created_at >= inicio_hoy,
                Pedido.created_at < fin_hoy,
                Pedido.deleted_at.is_(None),
            )
        ).one()

        clientes_nuevos = self.db.exec(
            select(func.count(Usuario.id)).where(
                Usuario.deleted_at.is_(None),
                Usuario.created_at.between(inicio_periodo, fin_periodo),
            )
        ).one()

        pedidos_pendientes = self.db.exec(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo == "PENDIENTE",
                Pedido.deleted_at.is_(None),
            )
        ).one()

        return {
            "ventas_totales": ventas_totales or Decimal('0.00'),
            "pedidos_hoy": pedidos_hoy,
            "clientes_nuevos": clientes_nuevos,
            "pedidos_pendientes": pedidos_pendientes,
        }

    def get_ventas_semanales(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        trunc: str = "day",
    ):
        hoy = date.today()
        if fecha_desde is None:
            fecha_desde = hoy - timedelta(days=6)
        if fecha_hasta is None:
            fecha_hasta = hoy

        inicio_periodo = datetime(fecha_desde.year, fecha_desde.month, fecha_desde.day, tzinfo=timezone.utc)
        fin_periodo = datetime(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day, tzinfo=timezone.utc) + timedelta(days=1)

        dias_totales = (fecha_hasta - fecha_desde).days + 1

        pedidos_pagados = self._pedidos_pagados_subquery()

        ventas_db = self.db.exec(
            select(
                func.date_trunc(trunc, Pedido.created_at).label("fecha"),
                func.coalesce(func.sum(Pedido.total), 0).label("total"),
                func.count(Pedido.id).label("cantidad"),
            ).where(
                Pedido.id.in_(select(pedidos_pagados.c.id)),
                Pedido.created_at.between(inicio_periodo, fin_periodo),
            ).group_by(
                func.date_trunc(trunc, Pedido.created_at)
            ).order_by(
                func.date_trunc(trunc, Pedido.created_at)
            )
        ).all()

        ventas_dict = {
            row.fecha: row
            for row in ventas_db
        }

        data = []

        for i in range(dias_totales):

            dia = fecha_desde + timedelta(days=i)

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
                    "total": Decimal('0.00'),
                    "cantidad": 0,
                })

        return data

    def get_productos_mas_vendidos(
        self,
        limit: int = 10,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):

        hoy = date.today()
        if fecha_desde is None:
            fecha_desde = hoy - timedelta(days=30)
        if fecha_hasta is None:
            fecha_hasta = hoy

        inicio_periodo = datetime(fecha_desde.year, fecha_desde.month, fecha_desde.day, tzinfo=timezone.utc)
        fin_periodo = datetime(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day, tzinfo=timezone.utc) + timedelta(days=1)

        pedidos_entregados = self._pedidos_pagados_subquery()

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
                    0
                ).label("ingreso_total"),

            ).where(
                DetallePedido.pedido_id.in_(
                    select(
                        pedidos_entregados.c.id
                    )
                ),
                DetallePedido.created_at.between(inicio_periodo, fin_periodo),

            ).group_by(
                DetallePedido.producto_id,
                DetallePedido.nombre_snapshot,

            ).order_by(
                text("total_vendido DESC")

            ).limit(limit)
        )

        return self.db.exec(statement).all()

    def _parse_fechas(
        self,
        fecha_desde: date | None,
        fecha_hasta: date | None,
    ) -> tuple[datetime, datetime]:
        hoy = date.today()
        if fecha_desde is None:
            fecha_desde = hoy - timedelta(days=30)
        if fecha_hasta is None:
            fecha_hasta = hoy
        inicio = datetime(fecha_desde.year, fecha_desde.month, fecha_desde.day, tzinfo=timezone.utc)
        fin = datetime(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day, tzinfo=timezone.utc) + timedelta(days=1)
        return inicio, fin

    def get_pedidos_por_estado(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):
        inicio_periodo, fin_periodo = self._parse_fechas(fecha_desde, fecha_hasta)

        return self.db.exec(
            select(
                Pedido.estado_codigo,
                func.count(Pedido.id).label("cantidad"),
            ).where(
                Pedido.deleted_at.is_(None),
                Pedido.created_at.between(inicio_periodo, fin_periodo),
            ).group_by(
                Pedido.estado_codigo,
            ).order_by(
                Pedido.estado_codigo,
            )
        ).all()

    def get_ingresos_por_forma_pago(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):
        inicio_periodo, fin_periodo = self._parse_fechas(fecha_desde, fecha_hasta)

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
                    func.sum(Pedido.total), 0
                ).label("total"),
                func.count(Pedido.id).label("cantidad"),
            ).where(
                Pedido.id.in_(select(pedidos_aprobados.c.pedido_id)),
                Pedido.deleted_at.is_(None),
                Pedido.created_at.between(inicio_periodo, fin_periodo),
            ).group_by(
                Pedido.forma_pago_codigo,
            ).order_by(
                text("total DESC"),
            )
        ).all()