param(
    [ValidateSet("logs", "ssh-backend", "ssh-frontend", "help")]
    [string]$Mode = "logs",

    [string]$BackendService = $env:RAILWAY_BACKEND_SERVICE,
    [string]$FrontendService = $env:RAILWAY_FRONTEND_SERVICE,
    [string]$Environment = $env:RAILWAY_ENVIRONMENT,

    [int]$Lines = 200,
    [switch]$Follow
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host ""
    Write-Host "Railway Debug Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Önkoşullar:" -ForegroundColor Yellow
    Write-Host "  1) Railway CLI kurulu olmalı: npm i -g @railway/cli"
    Write-Host "  2) Login olmalısın: railway login"
    Write-Host "  3) Service isimlerini/ID'lerini parametre veya env ile vermelisin"
    Write-Host ""
    Write-Host "Env değişkenleri (opsiyonel):" -ForegroundColor Yellow
    Write-Host "  RAILWAY_BACKEND_SERVICE=<service-name-or-id>"
    Write-Host "  RAILWAY_FRONTEND_SERVICE=<service-name-or-id>"
    Write-Host "  RAILWAY_ENVIRONMENT=<environment-name-or-id>"
    Write-Host ""
    Write-Host "Örnekler:" -ForegroundColor Yellow
    Write-Host "  .\\scripts\\railway_debug.ps1 -Mode logs -BackendService HotHour-MyRhythmNexus -FrontendService HotHour-FrontEnd -Lines 300 -Follow"
    Write-Host "  .\\scripts\\railway_debug.ps1 -Mode ssh-backend -BackendService HotHour-MyRhythmNexus"
    Write-Host "  .\\scripts\\railway_debug.ps1 -Mode ssh-frontend -FrontendService HotHour-FrontEnd"
    Write-Host ""
}

function Assert-RailwayCli {
    $cmd = Get-Command railway -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Railway CLI bulunamadı. Kur: npm i -g @railway/cli"
    }
}

function Invoke-Railway {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args,
        [switch]$AllowFollowFallback
    )

    Write-Host "`n> railway $($Args -join ' ')" -ForegroundColor DarkGray

    $previousEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & railway @Args 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousEap

    if ($output) {
        $output | ForEach-Object { Write-Host $_ }
    }

    if ($exitCode -ne 0 -and $AllowFollowFallback -and ($Args -contains "--follow")) {
        $text = ($output | Out-String)
        if ($text -match "unexpected argument '--follow'") {
            Write-Host "`nBilgi: Bu Railway CLI sürümünde '--follow' desteklenmiyor. '--follow' olmadan tekrar deneniyor." -ForegroundColor Yellow
            $retryArgs = @($Args | Where-Object { $_ -ne "--follow" })
            Write-Host "`n> railway $($retryArgs -join ' ')" -ForegroundColor DarkGray

            $retryPrevEap = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            $retryOutput = & railway @retryArgs 2>&1
            $retryExitCode = $LASTEXITCODE
            $ErrorActionPreference = $retryPrevEap

            if ($retryOutput) {
                $retryOutput | ForEach-Object { Write-Host $_ }
            }

            if ($retryExitCode -ne 0) {
                throw "Railway komutu başarısız oldu (exit code: $retryExitCode)."
            }
            return
        }
    }

    if ($exitCode -ne 0) {
        throw "Railway komutu başarısız oldu (exit code: $exitCode)."
    }
}

function Build-CommonArgs {
    param(
        [switch]$IncludeFollow
    )

    $args = @()
    if ($Environment) {
        $args += @("--environment", $Environment)
    }
    if ($IncludeFollow -and $Follow) {
        $args += "--follow"
    }
    return $args
}

function Get-RequiredService {
    param(
        [string]$Value,
        [string]$Label
    )
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "$Label belirtilmedi. Parametre ver veya ilgili env değişkenini set et."
    }
    return $Value
}

try {
    Assert-RailwayCli

    if ($Mode -eq "help") {
        Show-Help
        exit 0
    }

    switch ($Mode) {
        "logs" {
            $common = Build-CommonArgs -IncludeFollow

            if ($BackendService) {
                Write-Host "\n=== BACKEND LOGS ===" -ForegroundColor Cyan
                $backendArgs = @("logs", "--service", $BackendService, "--lines", $Lines) + $common
                Invoke-Railway -Args $backendArgs -AllowFollowFallback
            }

            if ($FrontendService) {
                Write-Host "\n=== FRONTEND LOGS ===" -ForegroundColor Magenta
                $frontendArgs = @("logs", "--service", $FrontendService, "--lines", $Lines) + $common
                Invoke-Railway -Args $frontendArgs -AllowFollowFallback
            }

            if (-not $BackendService -and -not $FrontendService) {
                throw "En az bir servis girilmeli: -BackendService veya -FrontendService"
            }
        }

        "ssh-backend" {
            $svc = Get-RequiredService -Value $BackendService -Label "BackendService"
            $common = Build-CommonArgs
            $args = @("ssh", "--service", $svc) + $common
            Invoke-Railway -Args $args
        }

        "ssh-frontend" {
            $svc = Get-RequiredService -Value $FrontendService -Label "FrontendService"
            $common = Build-CommonArgs
            $args = @("ssh", "--service", $svc) + $common
            Invoke-Railway -Args $args
        }
    }
}
catch {
    Write-Host "\nHata: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Yardım için: .\\scripts\\railway_debug.ps1 -Mode help" -ForegroundColor Yellow
    exit 1
}
