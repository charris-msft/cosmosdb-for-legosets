Write-Host "Installing Python dependencies..."
pip install -r requirements.txt --quiet

Write-Host "Importing LEGO data into Cosmos DB..."
python scripts/import_data.py
