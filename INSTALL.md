> 🌐 [Versión en español](INSTALL.es.md)

# 🛠️ Setup Guide — Daily Shipments Dashboard

Follow these steps in order to adapt the app to your database.

---

## Step 1 — Connection credentials

Copy `.env.example` and rename it to `.env`:

```bash
copy .env.example .env
```

Open `.env` and fill in your details:

```env
DB_SERVER=192.168.x.x        # SQL Server IP or hostname
DB_NAME=YourDatabaseName      # Database name
DB_USER=your_user             # SQL user with read permissions
DB_PWD=your_password          # User password
```

> ⚠️ The `.env` file is listed in `.gitignore` and will never be uploaded to GitHub.

---

## Step 2 — Table names

Open `app.py` and find the **"NOMBRES DE TABLAS Y CAMPOS"** block.

Replace the three table names with your own:

```python
TBL_PEDIDOS    = "your_schema.dbo.YourOrdersTable"
TBL_TRANSPORT  = "your_schema.dbo.YourCarriersTable"
TBL_CLIENTES   = "your_schema.dbo.YourClientsTable"
```

If your database doesn't use a custom schema, just use the table name:

```python
TBL_PEDIDOS    = "Orders"
TBL_TRANSPORT  = "Carriers"
TBL_CLIENTES   = "Clients"
```

---

## Step 3 — Orders table columns

Replace each variable with the exact column name in your table:

| Variable | Purpose | Expected type |
|---|---|---|
| `COL_PED_ID` | Primary key | int |
| `COL_PED_FECHA` | Order datetime. Filters the day and powers the timeline | datetime |
| `COL_PED_TRANSPORT` | Foreign key to the carriers table | int |
| `COL_PED_CLIENTE` | Foreign key to the clients table | int or varchar |
| `COL_PED_REF` | Main order reference. Used for duplicate detection | varchar |
| `COL_PED_REF2` | Fallback reference shown when `COL_PED_REF` is empty | varchar |
| `COL_PED_CANCELADO` | Cancelled flag. `0` = active, `1` = cancelled | bit or int |

Example:

```python
COL_PED_ID         = "order_id"
COL_PED_FECHA      = "shipping_date"
COL_PED_TRANSPORT  = "carrier_id"
COL_PED_CLIENTE    = "client_id"
COL_PED_REF        = "reference"
COL_PED_REF2       = "order_number"
COL_PED_CANCELADO  = "cancelled"
```

---

## Step 4 — Carriers table columns

| Variable | Purpose | Expected type |
|---|---|---|
| `COL_TRN_ID` | Primary key. Must match `COL_PED_TRANSPORT` | int |
| `COL_TRN_NOMBRE` | Carrier name displayed in the dashboard | varchar |

Example:

```python
COL_TRN_ID     = "id"
COL_TRN_NOMBRE = "name"
```

---

## Step 5 — Clients table columns

| Variable | Purpose | Expected type |
|---|---|---|
| `COL_CLI_ID` | Primary key. Must match `COL_PED_CLIENTE` | int or varchar |
| `COL_CLI_NOMBRE` | Client name (shown in the duplicate address alert) | varchar |
| `COL_CLI_DIRECCION` | Shipping address. Used to detect when two orders go to the same address on the same day | varchar |

Example:

```python
COL_CLI_ID        = "client_id"
COL_CLI_NOMBRE    = "name"
COL_CLI_DIRECCION = "shipping_address"
```

---

## Step 6 — Verify the connection

Run the app in development mode to check everything works:

```bash
python app.py
```

If there's a connection error or wrong table/column name, the details will appear in the console.

---

## Step 7 — Build the .exe (optional)

Once the app is running correctly:

```bash
pyinstaller --onefile --noconsole ^
  --add-data "templates;templates" ^
  --add-data "icon.ico;." ^
  --icon="icon.ico" ^
  --hidden-import webview ^
  --hidden-import webview.platforms.winforms ^
  app.py
```

The executable will be generated at `dist/app.exe`.

> ⚠️ Only distribute the `.exe` in trusted environments.

---

## Quick reference — what to edit

```
.env              ← connection credentials
app.py (ln 30-55) ← table and column names
```

Only those two things. The SQL queries are built automatically from the variables you define.
