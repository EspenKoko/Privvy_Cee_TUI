Push-Location $PSScriptRoot
try {
    $pyinstallerCommand = Get-Command pyinstaller -ErrorAction SilentlyContinue
    if ($pyinstallerCommand) {
        $pyinstallerPath = $pyinstallerCommand.Source
    }
    else {
        $localPyInstaller = Join-Path $PSScriptRoot ".venv\Scripts\pyinstaller.exe"
        if (Test-Path $localPyInstaller) {
            $pyinstallerPath = $localPyInstaller
        }
    }

    if (-not $pyinstallerPath) {
        throw "PyInstaller was not found. Activate the project's virtual environment or install PyInstaller first."
    }

    & $pyinstallerPath `
        --onedir `
        --name PrivvyCee `
        --icon "assets\fingerprint.ico" `
        --collect-all textual `
        --add-data "src/css;src/css" `
        main.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
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

    & $isccPath "PrivvyCeeInstaller.iss"
    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup failed with exit code $LASTEXITCODE."
    }

    Write-Host "Installer created in $PSScriptRoot\installer-output"
}
finally {
    Pop-Location
}