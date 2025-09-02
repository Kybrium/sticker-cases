param(
    [Parameter(Mandatory=$false)]
    [string]$cmd = "help"
)

$compose = "docker compose -f docker-compose.dev.yml"

switch ($cmd) {
    "up"          { iex "$compose up --build" }
    "down"        { iex "$compose down" }
    "logs"        { iex "$compose logs -f --tail=100" }
    "ps"          { iex "$compose ps" }
    "restart"     { iex "$compose restart backend" }

    "show-lan" {
        # Try to detect primary IPv4 quickly
        $ip = (Get-NetIPAddress -AddressFamily IPv4 |
            Where-Object { $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1' -and $_.PrefixOrigin -ne 'WellKnown' } |
            Select-Object -First 1 -ExpandProperty IPAddress)
        if (!$ip) { $ip = (hostname -I 2>$null) -split ' ' | Select-Object -First 1 }
        if (!$ip) { Write-Host "Could not detect LAN IP. Set manually with: `$env:LAN_IP = '192.168.x.x'"; break }
        Write-Host "LAN IP: $ip"
        Write-Host "Frontend:  http://$ip:3000"
        Write-Host "Backend:   http://$ip:8000"
    }
    "up-lan" {
        # Detect or let user set $env:LAN_IP beforehand
        if (-not $env:LAN_IP) {
            $ip = (Get-NetIPAddress -AddressFamily IPv4 |
                Where-Object { $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1' -and $_.PrefixOrigin -ne 'WellKnown' } |
                Select-Object -First 1 -ExpandProperty IPAddress)
            if ($ip) { $env:LAN_IP = $ip }
        }
        if (-not $env:LAN_IP) {
            Write-Host "LAN_IP not set and could not auto-detect."
            Write-Host "Set it manually, e.g.: `$env:LAN_IP = '192.168.1.23'  then run: .\dev.ps1 up-lan"
            break
        }
        Write-Host "Using LAN_IP = $env:LAN_IP"
        iex "$compose up --build"
    }

    "migrate"     { iex "$compose exec backend python manage.py migrate" }
    "makemigrations" { iex "$compose exec backend python manage.py makemigrations" }
    "superuser"   { iex "$compose exec backend python manage.py createsuperuser" }
    "shell"       { iex "$compose exec backend python manage.py shell" }
    "bash-backend" { iex "$compose exec backend bash" }

    "bash-frontend" { iex "$compose exec frontend sh" }

    "psql"        { iex "$compose exec db psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB" }

    default {
        Write-Host "Usage: ./dev.ps1 <command>`n"
        Write-Host "Available commands:"
        Write-Host "  up             - start all containers (build if needed)"
        Write-Host "  down           - stop all containers"
        Write-Host "  logs           - show logs"
        Write-Host "  ps             - show container status"
        Write-Host "  restart        - restart backend only"
        Write-Host "  migrate        - apply Django migrations"
        Write-Host "  makemigrations - create new Django migrations"
        Write-Host "  superuser      - create Django superuser"
        Write-Host "  shell          - open Django shell"
        Write-Host "  bash-backend   - open bash in backend container"
        Write-Host "  bash-frontend  - open shell in frontend container"
        Write-Host "  psql           - open Postgres CLI"
    }
}