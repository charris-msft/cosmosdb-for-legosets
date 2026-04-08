#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo "Importing LEGO data into Cosmos DB..."
python scripts/import_data.py
