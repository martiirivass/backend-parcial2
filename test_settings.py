import sys; sys.path.insert(0, '.')
from app.core.config import settings
print(f"MP_ACCESS_TOKEN configured: {bool(settings.MP_ACCESS_TOKEN)}")
print(f"Token starts with: {settings.MP_ACCESS_TOKEN[:15] if settings.MP_ACCESS_TOKEN else 'N/A'}...")
