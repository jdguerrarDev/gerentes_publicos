# API Compromisos y Acciones

API FastAPI para gestión de compromisos, acciones predefinidas y acciones de innovación con validación de pesos porcentuales.

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 12+
- UV (gestor de paquetes para Python)
- psycopg3 (driver PostgreSQL async/await)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd compromiso-api
```

### 2. Instalar UV (si no lo tienes)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Instalar dependencias con UV

```bash
uv sync
```

### 4. Configurar BD

#### Opción A: Crear BD desde cero

```bash
# Conectarse a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE gerentesPublicos;

# Salir
\q

# Ejecutar DDL
psql -U postgres -d gerentesPublicos -f ddl_final_completo.sql

# Ejecutar seeders
psql -U postgres -d gerentesPublicos -f seeders_completo.sql
```

#### Opción B: Usando variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

### 5. Ejecutar la API

```bash
uv run python main.py
```

La API estará disponible en: **http://localhost:8000**

Swagger UI: **http://localhost:8000/docs**

## 📚 Endpoints Disponibles

### Compromisos

- **GET** `/api/v1/usuarios/{usuario_id}/compromisos` - Obtener compromisos del usuario
  
### Acciones

- **GET** `/api/v1/usuarios/{usuario_id}/compromisos/{compromiso_id}/acciones` - Acciones disponibles
- **GET** `/api/v1/usuarios/{usuario_id}/compromisos/{compromiso_id}/acciones-seleccionadas` - Acciones ya seleccionadas
- **POST** `/api/v1/usuarios/{usuario_id}/compromisos/{compromiso_id}/acciones/seleccionar` - Seleccionar acción
  
  Body:
  ```json
  {
    "id_accion": 1,
    "peso_porcentual_usuario": 20.5
  }
  ```

### Innovaciones

- **POST** `/api/v1/usuarios/{usuario_id}/compromisos/{compromiso_id}/innovaciones` - Crear acción de innovación
  
  Body:
  ```json
  {
    "nombre": "Proyecto de automatización",
    "descripcion": "Automatizar procesos de reportes",
    "peso_porcentual_usuario": 30.0,
    "evidencias": "URL o descripción de evidencias"
  }
  ```

- **GET** `/api/v1/usuarios/{usuario_id}/innovaciones` - Obtener todas las innovaciones del usuario

### Validación

- **GET** `/api/v1/usuarios/{usuario_id}/validar-pesos` - Validar que los pesos sumen 100% por compromiso

## 🧪 Ejemplo de Flujo de Uso

```bash
# 1. Obtener compromisos del usuario 1
curl http://localhost:8000/api/v1/usuarios/1/compromisos

# 2. Ver acciones disponibles para compromiso 1
curl http://localhost:8000/api/v1/usuarios/1/compromisos/1/acciones

# 3. Seleccionar una acción
curl -X POST http://localhost:8000/api/v1/usuarios/1/compromisos/1/acciones/seleccionar \
  -H "Content-Type: application/json" \
  -d '{"id_accion": 2, "peso_porcentual_usuario": 25.0}'

# 4. Crear acción de innovación
curl -X POST http://localhost:8000/api/v1/usuarios/1/innovaciones \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Nueva iniciativa",
    "descripcion": "Descripción",
    "peso_porcentual_usuario": 50.0
  }'

# 5. Validar pesos
curl http://localhost:8000/api/v1/usuarios/1/validar-pesos
```

## 📊 Datos de Prueba

El script `seeders_completo.sql` incluye:

- **Usuario:** `usuario.ejemplo@sena.edu.co` (ID: 1)
- **Roles:** Subdirector Centro, Director Regional
- **Región:** Regional Caribe
- **Centro:** Centro Cartagena
- **Compromisos:** 
  - Acciones Misionales (40%)
  - Cumplimiento (35%)
  - Innovación (25%)

**Acciones obligatorias ya pre-seleccionadas:**
- Subdirector Centro: "Compra de Materiales REGULAR" (15%)
- Director Regional: "Seguimiento plan de acción" (15%)

## 🔧 Estructura del Proyecto

```
compromiso-api/
├── main.py                 # API principal
├── config.py               # Configuración BD
├── schemas.py              # Modelos Pydantic
├── pyproject.toml          # Dependencias
├── .env.example            # Variables de entorno
├── ddl_final_completo.sql  # Script DDL
├── seeders_completo.sql    # Datos iniciales
└── README.md               # Este archivo
```

## 💡 Características

✅ Listar compromisos del usuario
✅ Ver acciones disponibles por compromiso
✅ Acciones obligatorias pre-seleccionadas
✅ Seleccionar acciones y asignar pesos variables
✅ Crear acciones de innovación (3-5 por compromiso)
✅ Validar que pesos sumen 100%
✅ Cálculo automático de peso real en total
✅ Swagger UI para pruebas interactivas

## 🐛 Troubleshooting

### Error de conexión BD

```
Error: could not translate host name "localhost" to address
```

Solución: Verifica que PostgreSQL esté corriendo y que `DATABASE_URL` sea correcto.

### Error de módulos no encontrados

```bash
uv sync --upgrade
```

### Puerto 8000 en uso

```bash
uv run python main.py --port 8001
```

## 📝 Notas

- Las acciones obligatorias se pre-seleccionan automáticamente con peso fijo (15%)
- Las demás acciones deben ser seleccionadas por el usuario
- El total de pesos por compromiso debe ser 100%
- Las innovaciones requieren entre 3-5 acciones
- El peso real en el total es: (suma_acciones × peso_compromiso / 100)

## 📞 Soporte

Para preguntas o issues, contacta al equipo de desarrollo.