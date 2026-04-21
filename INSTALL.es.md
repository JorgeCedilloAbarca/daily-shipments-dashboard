> 🌐 [English version](INSTALL.md)

# 🛠️ Guía de configuración — Daily Shipments Dashboard

Sigue estos pasos en orden para adaptar la app a tu base de datos.

---

## Paso 1 — Credenciales de conexión

Copia el archivo `.env.example` y renómbralo como `.env`:

```bash
copy .env.example .env
```

Abre `.env` y rellena tus datos:

```env
DB_SERVER=192.168.x.x        # IP o nombre del servidor SQL Server
DB_NAME=NombreDeTuBD          # Nombre de la base de datos
DB_USER=tu_usuario            # Usuario SQL con permisos de lectura
DB_PWD=tu_contraseña          # Contraseña del usuario
```

> ⚠️ El archivo `.env` está en `.gitignore` y nunca se subirá a GitHub.

---

## Paso 2 — Nombres de tablas

Abre `app.py` y localiza el bloque **"NOMBRES DE TABLAS Y CAMPOS"**.

Sustituye los tres nombres de tabla por los de tu base de datos:

```python
TBL_PEDIDOS    = "tu_esquema.dbo.TuTablaDePedidos"
TBL_TRANSPORT  = "tu_esquema.dbo.TuTablaDeTransportistas"
TBL_CLIENTES   = "tu_esquema.dbo.TuTablaDeClientes"
```

Si tu base de datos no usa esquema propio, pon solo el nombre:

```python
TBL_PEDIDOS    = "Pedidos"
TBL_TRANSPORT  = "Transportistas"
TBL_CLIENTES   = "Clientes"
```

---

## Paso 3 — Campos de la tabla de pedidos

Sustituye cada variable por el nombre exacto del campo en tu tabla:

| Variable | Para qué se usa | Tipo esperado |
|---|---|---|
| `COL_PED_ID` | Clave primaria | int |
| `COL_PED_FECHA` | Fecha y hora del pedido. Filtra el día y genera la línea de tiempo | datetime |
| `COL_PED_TRANSPORT` | Clave foránea hacia la tabla de transportistas | int |
| `COL_PED_CLIENTE` | Clave foránea hacia la tabla de clientes | int o varchar |
| `COL_PED_REF` | Referencia principal del pedido. Se usa para detectar duplicados | varchar |
| `COL_PED_REF2` | Referencia alternativa. Se muestra si `COL_PED_REF` está vacío | varchar |
| `COL_PED_CANCELADO` | Indica si el pedido está cancelado. `0` = activo, `1` = cancelado | bit o int |

Ejemplo:

```python
COL_PED_ID         = "id_pedido"
COL_PED_FECHA      = "fecha_envio"
COL_PED_TRANSPORT  = "id_transportista"
COL_PED_CLIENTE    = "id_cliente"
COL_PED_REF        = "referencia"
COL_PED_REF2       = "num_pedido"
COL_PED_CANCELADO  = "cancelado"
```

---

## Paso 4 — Campos de la tabla de transportistas

| Variable | Para qué se usa | Tipo esperado |
|---|---|---|
| `COL_TRN_ID` | Clave primaria. Debe coincidir con `COL_PED_TRANSPORT` | int |
| `COL_TRN_NOMBRE` | Nombre del transportista que se muestra en el panel | varchar |

Ejemplo:

```python
COL_TRN_ID     = "id"
COL_TRN_NOMBRE = "nombre"
```

---

## Paso 5 — Campos de la tabla de clientes

| Variable | Para qué se usa | Tipo esperado |
|---|---|---|
| `COL_CLI_ID` | Clave primaria. Debe coincidir con `COL_PED_CLIENTE` | int o varchar |
| `COL_CLI_NOMBRE` | Nombre del cliente (aparece en el aviso de direcciones duplicadas) | varchar |
| `COL_CLI_DIRECCION` | Dirección de envío. La app detecta cuando dos pedidos del mismo día van a la misma dirección | varchar |

Ejemplo:

```python
COL_CLI_ID        = "id_cliente"
COL_CLI_NOMBRE    = "nombre"
COL_CLI_DIRECCION = "direccion_envio"
```

---

## Paso 6 — Verificar la conexión

Ejecuta la app para comprobar que todo funciona:

```bash
python app.py
```

Si hay algún error de conexión o de nombre de tabla/campo, aparecerá en la consola con el detalle exacto.

---

## Paso 7 — Generar el .exe (opcional)

Una vez verificado que funciona correctamente:

```bash
pyinstaller --onefile --noconsole ^
  --add-data "templates;templates" ^
  --add-data "icon.ico;." ^
  --icon="icon.ico" ^
  --hidden-import webview ^
  --hidden-import webview.platforms.winforms ^
  app.py
```

El ejecutable quedará en `dist/app.exe`.

> ⚠️ Distribuye el `.exe` solo en entornos de confianza.

---

## Resumen rápido — qué hay que tocar

```
.env                     ← credenciales de conexión
app.py (líneas 30-55)    ← nombres de tablas y campos
```

Solo esas dos cosas. Las queries se construyen automáticamente a partir de las variables que definas.
