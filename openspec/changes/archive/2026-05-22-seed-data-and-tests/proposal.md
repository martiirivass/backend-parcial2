## Why

La aplicación no tiene datos de demostración (categorías, ingredientes, productos de ejemplo) ni tests automatizados que verifiquen que todo funcione correctamente.

## What Changes

- Agregar seed de categorías, ingredientes y productos de ejemplo
- Crear test integral que cubra auth, pedidos, soft delete y snapshots contables

## Impact

- `app/seed.py`: nueva función seed_demo_data()
- `test_integral.py`: test completo del sistema
