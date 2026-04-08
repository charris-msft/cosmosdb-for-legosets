#!/usr/bin/env python3
"""
Post-provision script: imports LEGO CSV data into Cosmos DB.
Requires COSMOS_ENDPOINT, COSMOS_DATABASE, COSMOS_CONTAINER env vars (set by azd).
CSV data is bundled in the data/ directory.
"""

import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from azure.cosmos import CosmosClient
from azure.identity import AzureCliCredential, DefaultAzureCredential

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR.parent / "data" / "lego_sets_and_themes.csv"


def get_cosmos_client() -> CosmosClient:
    """Create Cosmos DB client using Azure CLI or Default credentials."""
    endpoint = os.environ["COSMOS_ENDPOINT"]
    try:
        cred = AzureCliCredential()
        client = CosmosClient(endpoint, credential=cred)
        # Test the connection
        list(client.list_databases())
        return client
    except Exception:
        cred = DefaultAzureCredential()
        return CosmosClient(endpoint, credential=cred)


def import_data(csv_path: str):
    """Read CSV and upsert documents into Cosmos DB."""
    database_name = os.environ["COSMOS_DATABASE"]
    container_name = os.environ["COSMOS_CONTAINER"]

    client = get_cosmos_client()
    container = (
        client.get_database_client(database_name)
        .get_container_client(container_name)
    )

    # Read CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    print(f"Importing {total} LEGO sets into Cosmos DB...", flush=True)

    success = 0
    errors = 0
    start = time.time()

    for i, row in enumerate(rows):
        doc = {
            "id": row["set_number"],
            "set_number": row["set_number"],
            "name": row["name"],
            "year_released": (
                int(float(row["year_released"]))
                if row.get("year_released", "").strip()
                else None
            ),
            "number_of_parts": (
                int(float(row["number_of_parts"]))
                if row.get("number_of_parts", "").strip()
                else None
            ),
            "image_url": row.get("image_url", ""),
            "theme_name": row["theme_name"],
            "type": "legoSet",
            "imported_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            container.upsert_item(body=doc)
            success += 1
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"  Error on {doc['id']}: {e}", flush=True)

        if (i + 1) % 1000 == 0:
            elapsed = time.time() - start
            rate = success / elapsed if elapsed > 0 else 0
            print(
                f"  Progress: {i + 1}/{total} | "
                f"Success: {success} | Rate: {rate:.0f} docs/sec",
                flush=True,
            )

    elapsed = time.time() - start
    print(
        f"Import complete. Success: {success}, Errors: {errors}, "
        f"Time: {elapsed:.0f}s",
        flush=True,
    )


def main():
    for var in ("COSMOS_ENDPOINT", "COSMOS_DATABASE", "COSMOS_CONTAINER"):
        if var not in os.environ:
            print(f"Error: {var} environment variable is not set.", flush=True)
            sys.exit(1)

    if not CSV_PATH.exists():
        print(f"Error: CSV not found at {CSV_PATH}", flush=True)
        sys.exit(1)

    print(f"Using CSV: {CSV_PATH}", flush=True)
    import_data(str(CSV_PATH))


if __name__ == "__main__":
    main()
