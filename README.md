# 🧱 cosmosdb-for-legosets

[![azd compatible](https://img.shields.io/badge/azd-compatible-blue?logo=microsoft-azure)](https://learn.microsoft.com/azure/developer/azure-developer-cli/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **One command to a fully loaded Cosmos DB** — an Azure Developer CLI (`azd`) template that provisions an Azure Cosmos DB (serverless, NoSQL API) database and populates it with **21,503 LEGO sets** spanning 1949–2023.

Perfect for demos, workshops, learning Cosmos DB, or bootstrapping a sample dataset for your next app.

## 🏗️ What gets created

```
┌─────────────────────────────────────────┐
│  Resource Group: rg-{env-name}          │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Cosmos DB Account (Serverless)   │  │
│  │  • NoSQL API                      │  │
│  │  • Entra ID auth only (no keys)   │  │
│  │                                   │  │
│  │  └─ LegoDatabase                  │  │
│  │     └─ legoSets container         │  │
│  │        partition key: /theme_name  │  │
│  │        21,503 documents           │  │
│  └───────────────────────────────────┘  │
│                                         │
│  RBAC: Cosmos DB Data Contributor       │
│        → deploying user                 │
└─────────────────────────────────────────┘
```

## ✅ Prerequisites

| Tool | Install |
|---|---|
| Azure Developer CLI (`azd`) | [Install azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) |
| Python 3.9+ | [python.org](https://www.python.org/downloads/) |
| Azure subscription | [Free account](https://azure.microsoft.com/free/) |

## 🚀 Quick start

```bash
# Clone and deploy in one shot
azd init -t charris-msft/cosmosdb-for-legosets
azd auth login
azd up
```

That's it. The `postprovision` hook automatically imports all 21,503 LEGO sets into Cosmos DB.

## 📦 What happens during deployment

1. **`azd provision`** — Creates the resource group, Cosmos DB account (serverless), database, container, and assigns your user the Cosmos DB Data Contributor RBAC role
2. **`postprovision` hook** — Installs Python dependencies and runs `scripts/import_data.py`, which reads the bundled CSV and upserts all 21,503 documents

## 📐 Document schema

Each document in the `legoSets` container:

```json
{
  "id": "75192-1",
  "set_number": "75192-1",
  "name": "Millennium Falcon",
  "year_released": 2017,
  "number_of_parts": 7541,
  "image_url": "https://cdn.rebrickable.com/media/sets/75192-1.jpg",
  "theme_name": "Star Wars",
  "type": "legoSet"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Same as `set_number` (Cosmos DB document ID) |
| `set_number` | string | Official LEGO set number (e.g., `75192-1`) |
| `name` | string | Set name |
| `year_released` | number | Year the set was released (1949–2023) |
| `number_of_parts` | number | Piece count |
| `image_url` | string | Image URL from Rebrickable |
| `theme_name` | string | Theme (partition key) — e.g., `Star Wars`, `Technic` |
| `type` | string | Always `"legoSet"` |

## 🔍 Sample queries

Query the data in the Azure portal's Data Explorer or with the Azure Cosmos DB SDK:

```sql
-- Largest Star Wars sets
SELECT c.name, c.year_released, c.number_of_parts
FROM c
WHERE c.theme_name = "Star Wars"
ORDER BY c.number_of_parts DESC
OFFSET 0 LIMIT 10

-- Sets per theme
SELECT c.theme_name, COUNT(1) AS set_count
FROM c
GROUP BY c.theme_name

-- Sets released per decade
SELECT
  (c.year_released / 10) * 10 AS decade,
  COUNT(1) AS set_count
FROM c
WHERE IS_NUMBER(c.year_released)
GROUP BY (c.year_released / 10) * 10
```

## 🧹 Clean up

```bash
azd down
```

> ⚠️ **Note:** `azd down` deletes the resource group and everything in it. This is the intended behavior for a standalone template. Do **not** point this template at a resource group containing other resources you want to keep. See [azure/azure-dev#4785](https://github.com/azure/azure-dev/issues/4785).

## 🗂️ Project structure

```
cosmosdb-for-legosets/
├── azure.yaml                  # azd project config with postprovision hooks
├── data/
│   └── lego_sets_and_themes.csv  # 21,503 LEGO sets (bundled, CC0 license)
├── infra/
│   ├── main.bicep              # Subscription-scoped entry point
│   ├── main.parameters.json    # Parameter bindings from azd env
│   └── modules/
│       └── cosmos.bicep        # Cosmos DB account, database, container, RBAC
├── scripts/
│   ├── import_data.py          # CSV → Cosmos DB import script
│   ├── postprovision.ps1       # Windows hook
│   └── postprovision.sh        # Linux/macOS hook
├── requirements.txt            # Python dependencies
└── README.md
```

## 📊 Data source

[LEGO Sets & Themes Database (1949-2023)](https://www.kaggle.com/datasets/jkraak/lego-sets-and-themes-database/data) by Jonathan Kraayenbrink — **CC0 Public Domain**. Original data sourced from [Rebrickable](https://rebrickable.com/downloads/).

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details. The LEGO dataset is CC0 (public domain).
