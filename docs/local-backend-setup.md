# Guia para correr el backend localmente

Esta guia explica como levantar la API local de `api/`, que es una Azure Functions App con .NET isolated worker.

## Requisitos

- Windows con PowerShell.
- .NET SDK `10.0.302`.
- Node.js `24.10.0`.
- npm `11.6.1`.
- Azure Functions Core Tools v4.

Para comprobar versiones:

```powershell
dotnet --version
node --version
npm.cmd --version
```

En PowerShell, usa `npm.cmd` en lugar de `npm` si el sistema bloquea scripts `.ps1`.

## 1. Instalar Azure Functions Core Tools

Este backend necesita Azure Functions Core Tools para arrancar el host local de Functions.

```powershell
npm.cmd install -g azure-functions-core-tools@4 --unsafe-perm true
```

Verifica la instalacion con:

```powershell
func.cmd --version
```

Usa `func.cmd` y no `func` si PowerShell muestra un error como:

```text
No se puede cargar el archivo ...\func.ps1 porque la ejecucion de scripts esta deshabilitada
```

## 2. Crear la configuracion local

Desde la raiz del repositorio:

```powershell
cd C:\.NET\WEB\chicago-taxi-cloud-analytics
copy api\local.settings.example.json api\local.settings.json
```

El archivo local debe contener el modo de desarrollo:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated",
    "DASHBOARD_SUMMARY_PROVIDER": "Development"
  }
}
```

Con `DASHBOARD_SUMMARY_PROVIDER=Development`, la API no intenta conectarse a Azure SQL. Devuelve respuestas locales de desarrollo.

## 3. Compilar

Desde la raiz del repositorio:

```powershell
dotnet build
```

La compilacion debe terminar con:

```text
Compilacion correcta.
```

## 4. Levantar el backend

Para esta solucion, arranca el backend desde la carpeta `api`:

```powershell
cd C:\.NET\WEB\chicago-taxi-cloud-analytics\api
dotnet run
```

Cuando arranque correctamente, veras rutas similares a estas:

```text
Functions:

        Areas: [GET] http://localhost:7071/api/analytics/areas
        CostDistance: [GET] http://localhost:7071/api/analytics/cost-distance
        DashboardSummary: [GET] http://localhost:7071/api/dashboard/summary
        DataQuality: [GET] http://localhost:7071/api/data-quality
        DemandByHour: [GET] http://localhost:7071/api/analytics/demand/hourly
        Health: [GET] http://localhost:7071/api/health
        MonthlyTrends: [GET] http://localhost:7071/api/analytics/trends/monthly
        PaymentTypes: [GET] http://localhost:7071/api/analytics/payment-types
```

El backend queda disponible en:

```text
http://localhost:7071
```

## 5. Validar que funciona

En otra terminal:

```powershell
Invoke-RestMethod http://localhost:7071/api/health
```

Respuesta esperada:

```text
Status  Service
------  -------
Healthy ChicagoTaxi.Api
```

Tambien puedes probar:

```powershell
Invoke-RestMethod http://localhost:7071/api/dashboard/summary
```

En modo desarrollo, la respuesta esperada incluye:

```text
Status : DEVELOPMENT_NO_DATA
```

## Errores comunes

### `func` no se reconoce

Instala Azure Functions Core Tools:

```powershell
npm.cmd install -g azure-functions-core-tools@4 --unsafe-perm true
```

Luego valida con:

```powershell
func.cmd --version
```

### PowerShell bloquea `func.ps1`

Usa:

```powershell
func.cmd --version
```

o levanta el backend con:

```powershell
cd api
dotnet run
```

### Error `Unable to launch the Azure Functions Core Tools`

Significa que el proyecto compila, pero falta Azure Functions Core Tools o no esta disponible en el `PATH`.

Instala Core Tools y vuelve a correr:

```powershell
npm.cmd install -g azure-functions-core-tools@4 --unsafe-perm true
cd api
dotnet run
```

### Error `El nombre del directorio no es valido`

Puede pasar si se corre:

```powershell
dotnet run --project api\ChicagoTaxi.Api.csproj
```

desde la raiz. Para esta solucion, usa:

```powershell
cd api
dotnet run
```

### Error `NU1301` contra `https://api.nuget.org`

El proyecto necesita restaurar o verificar paquetes de NuGet. Asegurate de tener conexion a internet y ejecuta:

```powershell
dotnet restore
dotnet build
```

Luego:

```powershell
cd api
dotnet run
```

### Health check de storage aparece como `Unhealthy`

Con `AzureWebJobsStorage=UseDevelopmentStorage=true`, el host puede mostrar un aviso de storage si Azurite no esta corriendo. Para estos endpoints HTTP locales, la API puede seguir respondiendo correctamente.

Si necesitas eliminar ese aviso, instala y levanta Azurite.

### El puerto 7071 esta ocupado

Busca el proceso:

```powershell
netstat -ano | Select-String ":7071"
```

Deten el proceso usando el PID que aparece al final:

```powershell
Stop-Process -Id <PID>
```

## Conectar con el frontend local

El frontend de `apps/web` ya tiene un proxy de Vite que envia `/api` a `http://localhost:7071`.

Con el backend corriendo, levanta el frontend en otra terminal:

```powershell
cd C:\.NET\WEB\chicago-taxi-cloud-analytics\apps\web
npm.cmd install
npm.cmd run dev
```

Abre:

```text
http://localhost:5173/dashboard
```
