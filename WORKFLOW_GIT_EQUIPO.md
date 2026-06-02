# Workflow de Git para el Equipo - Backend Parcial 2

## 📌 Estado Actual (Resuelto ✅)

**Problema identificado:** Múltiples ramas divergentes causando conflictos en merges.

**Solución aplicada:**
- ✅ `master` actualizado con refactor clean architecture
- ✅ Ramas obsoletas eliminadas del remoto (GitHub)
- ✅ Referencias locales sincronizadas

---

## 🎯 Reglas de Oro para Futuros Cambios

### 1️⃣ SIEMPRE partir desde `master`

```bash
# Asegúrate de tener master actualizado
git checkout master
git pull origin master

# Crea tu rama DESDE master
git checkout -b feature/tu-feature

# NUNCA hagas checkout desde ramas viejas
```

### 2️⃣ Arquitectura a seguir

El proyecto usa **Clean Architecture**:

```
app/
├── core/               # Configuración global
│   ├── config.py
│   └── unit_of_work.py
├── models/             # SQLModel (mapeo BD)
├── schemas/            # Pydantic (validación)
├── repositories/       # Acceso a datos
├── services/           # Lógica de negocio
├── routers/            # Endpoints FastAPI
├── auth/               # Autenticación
└── db/                 # Conexión BD
```

**Estructura de un nuevo router:**
```python
# app/routers/nueva_router.py
from fastapi import APIRouter
from app.services.nueva_service import NuevaService
from app.core.unit_of_work import UnitOfWork

router = APIRouter(prefix="/api/nueva", tags=["nueva"])

@router.get("/")
async def obtener_todas(uow: UnitOfWork):
    service = NuevaService(uow)
    return await service.obtener_todas()
```

### 3️⃣ Flujo de Merge

```bash
# 1. Finalizas tu feature
git add .
git commit -m "feat: descripción clara"

# 2. Actualiza desde master para evitar conflictos
git fetch origin
git rebase origin/master

# 3. Push a tu rama
git push origin feature/tu-feature

# 4. CREA UN PR EN GITHUB (no mergees manualmente)
# - Descripción clara
# - Link a issues si existen
# - Review en el equipo

# 5. Después del merge en GitHub
git checkout master
git pull origin master
git branch -d feature/tu-feature
```

---

## ⚠️ Si tienes cambios en una rama vieja

### Caso A: Pocos cambios, quiero llevarlos a master

```bash
# Guarda tus commits
git cherry-pick <commit-hash>

# O si son varios commits
git rebase --onto master rama-vieja
```

### Caso B: Cambios complejos, mejor empezar limpio

```bash
# Crea rama nueva desde master actualizado
git checkout master
git pull origin master
git checkout -b feature/nueva-version

# Copia manualmente los cambios que necesites
# (usa IDE o editor para copiar el código relevant)
```

---

## 📋 Checklist para hacer un buen PR

- [ ] Tu rama está basada en `master` actualizado
- [ ] Los commits tienen mensajes claros
- [ ] El código sigue la estructura Clean Architecture
- [ ] No hay `print()`, usa logging si necesitas debug
- [ ] Probaste localmente que funciona
- [ ] No hay conflictos con `master`
- [ ] Escribiste una descripción en el PR

---

## 🔄 Si ves conflictos en tu PR

**NO HAGAS:** `git push --force`

**HAZLO:**
```bash
git fetch origin
git rebase origin/master

# Resuelve los conflictos en tu editor
# Luego:
git rebase --continue

# Push de la rama rebaseada
git push origin feature/tu-feature
```

---

## 🚨 En Caso de Emergencia

### "Arruiné mi rama"
```bash
git reset --hard origin/master
```

### "Necesito ver qué cambió en master"
```bash
git diff mi-rama..origin/master
```

### "Quiero ver todo el historial bonito"
```bash
git log --oneline --graph --all --decorate
```

---

## 📞 Comandos Útiles Diarios

| Comando | Descripción |
|---------|-------------|
| `git status` | Ver estado actual |
| `git pull origin master` | Actualizar master local |
| `git fetch` | Traer cambios sin mergear |
| `git log --oneline -10` | Ver últimos 10 commits |
| `git diff origin/master` | Ver diferencias con master |
| `git branch -a` | Ver todas las ramas |
| `git branch -d rama` | Eliminar rama local |

---

## 💡 Tips Pro

1. **Haz commits pequeños y frecuentes**
   - Cada commit = un cambio lógico
   - Mensajes claros: `feat:`, `fix:`, `refactor:`

2. **Pushea regularmente**
   - No acumules cambios locales por días
   - Reduce riesgo de conflictos

3. **Revisa los PRs de otros**
   - Aprende del código del equipo
   - Caza bugs juntos

4. **Usa `.gitignore` correctamente**
   - Ya está configurado, no necesitas cambios
   - Archivos `__pycache__`, `.env`, `venv/` están ignorados

---

## 🎓 Próximas Lecturas

- Conventional Commits: https://www.conventionalcommits.org/
- Git Feature Branch Workflow: https://www.atlassian.com/git/tutorials/comparing-workflows
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

