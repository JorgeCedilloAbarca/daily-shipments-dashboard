> 🌐 [Versión en español](README.es.md)

# 📦 Daily Shipments Dashboard

A desktop application to track and monitor daily shipments by carrier, built with **Python, Flask and pywebview**.

---

## ✨ Features

- Date selector with quick access to "Today"
- Shipments table grouped by carrier with daily total
- Automatic detection of duplicate orders
- Automatic detection of duplicate shipping addresses
- Timeline view: cumulative orders per hour and carrier
- Distributed as a `.exe` via PyInstaller

---

## 📸 Preview

| Dashboard | Dashboard with data | Timeline |
|:-:|:-:|:-:|
| ![Empty state](screenshots/empty.png) | ![Dashboard](screenshots/dashboard.png) | ![Timeline](screenshots/timeline.png) |

---

## ⚙️ Requirements

- Python 3.10 or higher
- SQL Server accessible over the network (SQL authentication enabled)
- Windows (pywebview with edgechromium requires Edge to be installed)

---

## 🚀 Quick Start

See the full setup guide: [INSTALL.md](INSTALL.md)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/daily-shipments-dashboard.git
cd daily-shipments-dashboard

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your credentials
copy .env.example .env
# Edit .env with your connection details

# 5. Run the app
python app.py
```

---

## 🗄️ Database Schema

The app expects three tables in your SQL Server database. Table and column names are fully configurable in `app.py`. See [INSTALL.md](INSTALL.md) for the step-by-step configuration guide.

### Orders table
| Variable | Description | Type |
|---|---|---|
| `COL_PED_ID` | Primary key | int |
| `COL_PED_FECHA` | Order datetime — used to filter the day and build the timeline | datetime |
| `COL_PED_TRANSPORT` | Foreign key → carriers table | int |
| `COL_PED_CLIENTE` | Foreign key → clients table | int / varchar |
| `COL_PED_REF` | Main order reference (duplicate detection) | varchar |
| `COL_PED_REF2` | Fallback reference if `COL_PED_REF` is empty | varchar |
| `COL_PED_CANCELADO` | `0` = active · `1` = cancelled | bit |

### Carriers table
| Variable | Description | Type |
|---|---|---|
| `COL_TRN_ID` | Primary key — must match `COL_PED_TRANSPORT` | int |
| `COL_TRN_NOMBRE` | Carrier display name | varchar |

### Clients table
| Variable | Description | Type |
|---|---|---|
| `COL_CLI_ID` | Primary key — must match `COL_PED_CLIENTE` | int / varchar |
| `COL_CLI_NOMBRE` | Client name | varchar |
| `COL_CLI_DIRECCION` | Shipping address (duplicate address detection) | varchar |

---

## 📁 Project Structure

```
daily-shipments-dashboard/
├── app.py                  # Flask server + SQL queries
├── templates/
│   └── index.html          # UI (pywebview)
├── screenshots/
│   ├── empty.png           # Empty state screenshot
│   ├── dashboard.png       # Dashboard with data screenshot
│   └── timeline.png        # Timeline modal screenshot
├── requirements.txt        # Python dependencies
├── .env                    # Credentials (never commit this)
├── .env.example            # Credentials template
├── .gitignore
├── README.md               # This file (English)
├── README.es.md            # Spanish version
├── INSTALL.md              # Setup guide (English)
└── INSTALL.es.md           # Setup guide (Spanish)
```

---

## 📋 Dependencies

```
Flask
pymssql
pywebview
python-dotenv
pyinstaller
```

---

## 📄 License

MIT
