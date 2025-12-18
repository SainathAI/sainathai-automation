# start-factory.ps1
# This script starts the local AI Social Media Content Factory.

# Check if Docker is running.
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop is not running. Please open the Docker Desktop app and ensure it's running before executing this script."
    exit
}

Write-Host "Starting the AI Social Media Content Factory services..."
docker compose up -d

# Wait for a moment to ensure the services are starting up.
Start-Sleep -Seconds 3

Write-Host "Opening the n8n interface at http://localhost:5678"
Start-Process http://localhost:5678
