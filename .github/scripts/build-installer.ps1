param(
    [string]$AppName = $env:APP_NAME
)

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $projectRoot
try {
    if ([string]::IsNullOrWhiteSpace($AppName)) {
        $AppName = "PrivvyCee"
    }
    $env:APP_NAME = $AppName

    $executable = Join-Path $projectRoot "dist\$AppName\$AppName.exe"
    if (-not (Test-Path $executable)) {
        throw "The executable was not found at '$executable'. Run build-exe.ps1 first."
    }

    $isccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($isccCommand) {
        $isccPath = $isccCommand.Source
    }
    else {
        $defaultIscc = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
        if (Test-Path $defaultIscc) {
            $isccPath = $defaultIscc
        }
    }

    if (-not $isccPath) {
        throw "Inno Setup 6 was not found. Install Inno Setup, then run this build script again."
    }

    & $isccPath (Join-Path $projectRoot "PrivvyCeeInstaller.iss")
    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup failed with exit code $LASTEXITCODE."
    }

    Write-Host "Installer created in $(Join-Path $projectRoot 'installer-output')"
}
finally {
    Pop-Location
}
