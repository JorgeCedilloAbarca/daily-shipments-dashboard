from flask import Flask, render_template, request, jsonify
import pymssql
import webview
import threading
from datetime import datetime
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ══════════════════════════════════════════════════════════════
#  CONEXIÓN A LA BASE DE DATOS
#  Los valores se leen del archivo .env — no escribas las
#  credenciales directamente aquí.
#  Consulta el archivo .env.example para ver qué variables
#  debes definir.
# ══════════════════════════════════════════════════════════════
SERVER   = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")
UID      = os.getenv("DB_USER")
PWD      = os.getenv("DB_PWD")

if not all([SERVER, DATABASE, UID, PWD]):
    raise RuntimeError(
        "Faltan credenciales de base de datos. "
        "Copia .env.example como .env y rellena los valores."
    )

# ══════════════════════════════════════════════════════════════
#  NOMBRES DE TABLAS Y CAMPOS  ← CONFIGURA AQUÍ
#
#  Cambia estos valores para que coincidan con tu base de datos.
#  Formato recomendado: "esquema.dbo.NombreTabla"
#  Si no usas esquema, pon solo el nombre: "NombreTabla"
# ══════════════════════════════════════════════════════════════

# ── Tabla de pedidos ──────────────────────────────────────────
TBL_PEDIDOS        = "tu_esquema.dbo.TuTablaDePedidos"
COL_PED_ID         = "Id"               # Clave primaria
COL_PED_FECHA      = "FechaSolEnvio"    # datetime: fecha y hora del pedido (filtra el día y alimenta la línea de tiempo)
COL_PED_TRANSPORT  = "Transportista"    # FK → tabla de transportistas
COL_PED_CLIENTE    = "Cliente"          # FK → tabla de clientes
COL_PED_REF        = "SuPedido"         # Referencia principal del pedido (para detectar duplicados)
COL_PED_REF2       = "NumPedidoCliente" # Referencia alternativa (se usa si COL_PED_REF está vacío)
COL_PED_CANCELADO  = "Cancelado"        # bit/int: 0 = activo, 1 = cancelado

# ── Tabla de transportistas ───────────────────────────────────
TBL_TRANSPORT      = "tu_esquema.dbo.TuTablaDeTransportistas"
COL_TRN_ID         = "Id"              # Clave primaria (relacionada con COL_PED_TRANSPORT)
COL_TRN_NOMBRE     = "Nombre"          # Nombre visible del transportista

# ── Tabla de clientes ─────────────────────────────────────────
TBL_CLIENTES       = "tu_esquema.dbo.TuTablaDeClientes"
COL_CLI_ID         = "NumCliente"      # Clave primaria (relacionada con COL_PED_CLIENTE)
COL_CLI_NOMBRE     = "Nombre"          # Nombre del cliente
COL_CLI_DIRECCION  = "DireccionEnvio"  # Dirección de envío (para detectar duplicados de dirección)


# ══════════════════════════════════════════════════════════════
#  QUERIES  — no es necesario modificarlas si has rellenado
#  correctamente las variables de arriba.
# ══════════════════════════════════════════════════════════════

# Pedidos del día agrupados por transportista
QUERY = f"""
    SELECT
        t.{COL_TRN_NOMBRE},
        COUNT(p.{COL_PED_ID}) AS Total_Pedidos
    FROM {TBL_PEDIDOS} p
    INNER JOIN {TBL_TRANSPORT} t ON t.{COL_TRN_ID} = p.{COL_PED_TRANSPORT}
    WHERE CAST(p.{COL_PED_FECHA} AS DATE) = %s
      AND p.{COL_PED_CANCELADO} = 0
    GROUP BY t.{COL_TRN_NOMBRE}
"""

# Referencias de pedido que aparecen más de una vez el mismo día
QUERY_DUPLICADOS = f"""
    SELECT
        {COL_PED_REF},
        COUNT(*) AS veces
    FROM {TBL_PEDIDOS}
    WHERE CAST({COL_PED_FECHA} AS DATE) = %s
      AND {COL_PED_REF} IS NOT NULL
      AND {COL_PED_REF} != ''
      AND {COL_PED_CANCELADO} = 0
    GROUP BY {COL_PED_REF}
    HAVING COUNT(*) > 1
    ORDER BY veces DESC
"""

# Pedidos con la misma dirección de envío el mismo día
QUERY_DIR_DUPLICADAS = f"""
    SELECT
        c.{COL_CLI_NOMBRE},
        c.{COL_CLI_DIRECCION},
        CASE
            WHEN p.{COL_PED_REF} IS NOT NULL AND p.{COL_PED_REF} != ''
            THEN p.{COL_PED_REF}
            ELSE p.{COL_PED_REF2}
        END AS Referencia
    FROM {TBL_PEDIDOS} p
    INNER JOIN {TBL_CLIENTES} c ON c.{COL_CLI_ID} = p.{COL_PED_CLIENTE}
    WHERE CAST(p.{COL_PED_FECHA} AS DATE) = %s
      AND p.{COL_PED_CANCELADO} = 0
      AND c.{COL_CLI_DIRECCION} IS NOT NULL
      AND c.{COL_CLI_DIRECCION} != ''
      AND (c.{COL_CLI_NOMBRE} + '|' + c.{COL_CLI_DIRECCION}) IN (
          SELECT c2.{COL_CLI_NOMBRE} + '|' + c2.{COL_CLI_DIRECCION}
          FROM {TBL_PEDIDOS} p2
          INNER JOIN {TBL_CLIENTES} c2 ON c2.{COL_CLI_ID} = p2.{COL_PED_CLIENTE}
          WHERE CAST(p2.{COL_PED_FECHA} AS DATE) = %s
            AND p2.{COL_PED_CANCELADO} = 0
            AND c2.{COL_CLI_DIRECCION} IS NOT NULL
            AND c2.{COL_CLI_DIRECCION} != ''
          GROUP BY c2.{COL_CLI_NOMBRE}, c2.{COL_CLI_DIRECCION}
          HAVING COUNT(*) > 1
      )
    ORDER BY c.{COL_CLI_NOMBRE}, p.{COL_PED_REF2}
"""

# TOP 6 transportistas con actividad reciente (para la lista dinámica del panel)
QUERY_TRANSPORTISTAS_RECIENTES = f"""
    SELECT DISTINCT TOP 6
        t.{COL_TRN_NOMBRE}
    FROM {TBL_PEDIDOS} p
    INNER JOIN {TBL_TRANSPORT} t ON t.{COL_TRN_ID} = p.{COL_PED_TRANSPORT}
    WHERE p.{COL_PED_FECHA} IS NOT NULL
      AND p.{COL_PED_CANCELADO} = 0
    ORDER BY t.{COL_TRN_NOMBRE}
"""

# Cada pedido del día con su hora exacta (para la línea de tiempo)
QUERY_TIMELINE = f"""
    SELECT
        CONVERT(VARCHAR(5), p.{COL_PED_FECHA}, 108) AS Hora,
        t.{COL_TRN_NOMBRE} AS Transportista
    FROM {TBL_PEDIDOS} p
    INNER JOIN {TBL_TRANSPORT} t ON t.{COL_TRN_ID} = p.{COL_PED_TRANSPORT}
    WHERE CAST(p.{COL_PED_FECHA} AS DATE) = %s
      AND p.{COL_PED_CANCELADO} = 0
    ORDER BY p.{COL_PED_FECHA} ASC
"""


# ══════════════════════════════════════════════════════════════
#  RUTAS FLASK
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

@app.route("/transportistas")
def transportistas():
    try:
        with pymssql.connect(server=SERVER, user=UID, password=PWD, database=DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute(QUERY_TRANSPORTISTAS_RECIENTES)
                rows = cursor.fetchall()
        nombres = [r[0] for r in rows]
        return jsonify({"transportistas": nombres})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/consultar", methods=["POST"])
def consultar():
    fecha_raw = request.json.get("fecha")
    try:
        fecha = datetime.strptime(fecha_raw, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Fecha inválida"}), 400

    try:
        with pymssql.connect(server=SERVER, user=UID, password=PWD, database=DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute(QUERY, (fecha,))
                rows = cursor.fetchall()

                cursor.execute(QUERY_DUPLICADOS, (fecha,))
                dup_rows = cursor.fetchall()

                cursor.execute(QUERY_DIR_DUPLICADAS, (fecha, fecha))
                dir_rows = cursor.fetchall()

                cursor.execute(QUERY_TIMELINE, (fecha,))
                timeline_rows = cursor.fetchall()

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    datos        = {nombre: total for nombre, total in rows}
    duplicados   = [{"suPedido": sup, "veces": veces} for sup, veces in dup_rows]
    dir_duplicadas = [{"nombre": n, "direccion": d, "referencia": r} for n, d, r in dir_rows]
    timeline     = [{"hora": hora, "transportista": transp} for hora, transp in timeline_rows]

    return jsonify({
        "datos": datos,
        "fecha": fecha_raw,
        "duplicados": duplicados,
        "dirDuplicadas": dir_duplicadas,
        "timeline": timeline
    })


# ══════════════════════════════════════════════════════════════
#  ARRANQUE
# ══════════════════════════════════════════════════════════════

def iniciar_flask():
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    t = threading.Thread(target=iniciar_flask, daemon=True)
    t.start()

    window = webview.create_window(
        "Envíos Diarios",
        "http://localhost:5000",
        width=1280,
        height=800,
        resizable=True,
    )

    def on_shown():
        window.maximize()

    webview.start(on_shown, gui="edgechromium")
