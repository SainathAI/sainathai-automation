# Check if Docker is running by executing a simple command
docker info > $null 2>&1

# Check the exit code of the last command
if (-Not $?) {
    # Docker command failed, so Docker is not running
    Write-Host "ERROR: Docker Desktop is not running. Please open the Docker Desktop app, wait for the green whale icon, and then run this script again."
    # Pause to allow the user to read the message before the window closes
    Read-Host "Press Enter to exit"
    exit 1
} else {
    # Docker is running, proceed with startup
    Write-Host "Docker Desktop is running. Starting the AI Social Media Content Factory..."

    # Run docker-compose in detached mode
    docker-compose up -d

    Write-Host "Factory services are starting up in the background."
    Write-Host "Waiting a few moments for the n8n container to initialize..."

    # Wait for 10 seconds to give the n8n service time to become available
    Start-Sleep -Seconds 10

    Write-Host "Opening n8n in your default browser at http://localhost:5678"

    # Open the n8n URL in the default browser
    Start-Process "http://localhost:5678"
}
