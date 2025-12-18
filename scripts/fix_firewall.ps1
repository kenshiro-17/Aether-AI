# Self-elevate if not running as Administrator
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Output "Requesting Admin privileges..."
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$PWD'; & '$PSCommandPath'`""
    exit
}

$ports = @(8000, 8081, 8082, 5173)
foreach ($port in $ports) {
    Write-Output "Opening Port $port..."
    # Remove old rules to avoid duplicates
    Remove-NetFirewallRule -DisplayName "AETHER ALLOW Port $port" -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "AETHER ALLOW Port $port" -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -Profile Any
}
Write-Output "Firewall rules updated. Please restart the app."
pause
