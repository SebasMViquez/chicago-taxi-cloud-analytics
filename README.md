# Chicago Taxi Cloud Analytics

Plataforma de procesamiento y visualización de datos del dataset público **Chicago Taxi Trips**. El proyecto procesa viajes, genera agregados analíticos y los presenta en un dashboard web construido con datos reales obtenidos desde una API.

## Qué incluye

- Procesamiento de datos CSV hacia resultados analíticos.
- Almacenamiento de archivos de origen y procesados en Azure Data Lake Storage Gen2.
- Agregados preparados para consulta en Azure SQL Database.
- API con Azure Functions para exponer los resultados.
- Dashboard React oscuro y responsive con las secciones Resumen, Zonas, Pagos y Calidad.
- Landing de acceso con animación `LetterGlitch` y transiciones accesibles.

## Arquitectura

```text
Dataset Chicago Taxi Trips (CSV)
          |
          v
Azure Data Lake Storage Gen2 (raw)
          |
          v
Procesador Python / Azure Container Apps Job
          |
          +--> Parquet procesado en ADLS Gen2
          |
          v
Azure SQL Database (agregados analíticos)
          |
          v
Azure Functions API
          |
          v
React + Vite / Azure Static Web Apps
```

El frontend no usa datos simulados: consume los endpoints analíticos de la API y muestra estados de carga, error y ausencia de datos de forma independiente.

## Estructura del repositorio

```text
apps/web/              Frontend React, TypeScript, Vite y Tailwind CSS
api/                   API Azure Functions con .NET isolated worker
api.Tests/             Pruebas de la API .NET
processing/            Procesador Python y sus pruebas
database/              Esquema y migraciones de Azure SQL
infra/bicep/           Infraestructura como código
docs/                  Documentación técnica y de despliegue
.github/workflows/     Automatizaciones de validación
```

## Requisitos locales

- .NET SDK `10.0.302` o compatible con `global.json`.
- Node.js y npm compatibles con Vite 8.
- Python 3.13 para el procesador.
- Azure Functions Core Tools v4 para ejecutar la API localmente.
- Una instancia/configuración de Azure SQL con resultados procesados para ver datos reales en el dashboard.

En Windows, si PowerShell bloquea `npm.ps1`, utilizar `npm.cmd` en lugar de `npm`.

## Inicio rápido del frontend

1. Instalar dependencias:

```powershell
cd apps/web
npm.cmd install
```

2. Configurar el destino de la API únicamente si no se ejecuta en `http://localhost:7071`. Crear `apps/web/.env.local` con este contenido:

```dotenv
API_PROXY_TARGET=http://localhost:7071
```

3. Iniciar el frontend:

```powershell
npm.cmd run dev
```

Abrir <http://localhost:5173>. La landing conduce al dashboard; también puede abrirse directamente en <http://localhost:5173/dashboard/resumen>.

## Rutas del dashboard

| Ruta | Contenido |
|---|---|
| `/` | Landing de acceso. |
| `/dashboard` | Redirige a Resumen. |
| `/dashboard/resumen` | KPIs generales, tendencia mensual, demanda y coste por distancia. |
| `/dashboard/zonas` | Ranking y comparación de zonas de recogida. |
| `/dashboard/pagos` | Distribución, leyenda y participación de métodos de pago. |
| `/dashboard/calidad` | Score y métricas de calidad de los datos procesados. |

## Ejecutar la API

1. Copiar la configuración local de ejemplo:

```powershell
Copy-Item api/local.settings.example.json api/local.settings.json
```

2. Restaurar y compilar desde la raíz:

```powershell
dotnet restore
dotnet build
```

3. Iniciar Azure Functions:

```powershell
cd api
func start
```

La API local se expone normalmente en <http://localhost:7071>. Para configurar SQL y los proveedores de datos, consultar `docs/local-backend-setup.md` y `api/local.settings.example.json`.

## Endpoints consumidos por el dashboard

| Endpoint GET | Uso en la interfaz |
|---|---|
| `/api/dashboard/summary` | KPIs generales: viajes, tarifa, distancia y duración promedio. |
| `/api/analytics/trends/monthly` | Tendencia mensual de viajes. |
| `/api/analytics/demand/hourly` | Demanda por día y hora. |
| `/api/analytics/cost-distance` | Coste promedio según rango de distancia. |
| `/api/analytics/areas` | Ranking y tarifas por zona de recogida. |
| `/api/analytics/payment-types` | Distribución de métodos de pago. |
| `/api/data-quality` | Métricas de validación y calidad del dataset. |
| `/api/health` | Estado básico de la API. |

## Ejecutar el procesador

El procesador incluye una fixture pequeña y ficticia para validaciones técnicas. No se deben subir al repositorio el dataset completo, extractos locales, Parquet generados ni salidas de Data Lake.

```powershell
cd processing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python src/main.py --mode local --input tests/fixtures/chicago_taxi_sample.csv --output .local-output
pytest
```

Consultar `processing/README.md` para la ejecución en Azure Container Apps Job.

## Validación

### Frontend

```powershell
cd apps/web
npm.cmd run lint
npm.cmd run build
```

`build` ejecuta primero la verificación de tipos de TypeScript y después genera la compilación de Vite. Actualmente el frontend no declara un script de pruebas automatizadas.

### API y procesador

```powershell
dotnet test

cd processing
pytest
```

## Tecnologías principales

- React 19, TypeScript, Vite y Tailwind CSS.
- React Router para rutas del dashboard.
- TanStack Query para consultas y caché de datos.
- Recharts para visualizaciones.
- GSAP para transiciones y animaciones puntuales.
- Lucide React para iconografía.
- Azure Functions .NET 10, Azure SQL y Azure Data Lake Storage Gen2.
- Python para el pipeline de procesamiento.

## Documentación adicional

- `docs/architecture.md`: arquitectura y componentes cloud.
- `docs/data-pipeline.md`: flujo de procesamiento de datos.
- `docs/local-backend-setup.md`: preparación y resolución de problemas de la API local.
- `docs/azure-deployment.md`: despliegue en Azure.
- `database/README.md`: propósito de la base de datos analítica.
- `processing/README.md`: ejecución y variables del procesador.

## Dataset

Fuente: <https://www.kaggle.com/datasets/chicago/chicago-taxi-trips-bq>

El dataset original puede ser grande y debe obtenerse desde la fuente indicada. No debe incluirse en commits ni en artefactos del repositorio.
