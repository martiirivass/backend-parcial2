import requests, os, json
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv(".env", override=True)

token = os.getenv("MP_ACCESS_TOKEN", "")
headers = {"Authorization": f"Bearer {token}"}

resp = requests.get(
    "https://api.mercadopago.com/v1/payments/search",
    headers=headers,
    params={"limit": 50, "sort": "date_created", "criteria": "desc"},
    timeout=15
)
results = resp.json().get("results", [])

from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    for r in results:
        ext_ref = r.get("external_reference")
        if not ext_ref:
            continue

        # Find pago by external_reference
        row = conn.execute(
            text("SELECT id, pedido_id, mp_status FROM pagos WHERE external_reference = :ref"),
            {"ref": ext_ref}
        ).first()

        if row and row.mp_status != "approved":
            print(f"Updating pago {row.id} (pedido={row.pedido_id}): {row.mp_status} -> {r.get('status')}")
            conn.execute(
                text("""
                    UPDATE pagos SET
                        mp_payment_id = :mp_id,
                        mp_status = :status,
                        transaction_amount = :amount,
                        date_approved = :date_approved,
                        actualizado_en = :now
                    WHERE id = :id
                """),
                {
                    "mp_id": r.get("id"),
                    "status": r.get("status"),
                    "amount": r.get("transaction_amount"),
                    "date_approved": r.get("date_approved"),
                    "now": datetime.now(timezone.utc),
                    "id": row.id
                }
            )

            if r.get("status") == "approved":
                # Update pedido to CONFIRMADO
                ped = conn.execute(
                    text("SELECT id, estado_codigo FROM pedidos WHERE id = :id"),
                    {"id": row.pedido_id}
                ).first()
                if ped and ped.estado_codigo == "PENDIENTE":
                    conn.execute(
                        text("UPDATE pedidos SET estado_codigo = 'CONFIRMADO', updated_at = :now WHERE id = :id"),
                        {"now": datetime.now(timezone.utc), "id": ped.id}
                    )
                    print(f"  -> Pedido {ped.id} marcado como CONFIRMADO")

    conn.commit()
    print("Done!")
